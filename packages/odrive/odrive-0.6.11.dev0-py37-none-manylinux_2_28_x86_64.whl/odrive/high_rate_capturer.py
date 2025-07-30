
import asyncio
import enum
import logging
import struct
import time
from typing import Any, Callable, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from odrive._internal_utils import run_on_loop, transform_odrive_objects
from odrive.codecs import decode_all
from odrive.runtime_device import RuntimeDevice

_CONTROL_LOOP_FREQ = 8000

logger = logging.getLogger("odrive")

DEFAULT_TRIGGER_POINT = 0.5

class TimestampFmt(enum.Enum):
    """
    Timestamp format to use in :func:`HighRateCapturer.download()`.
    """

    CONTROL_CYCLE = enum.auto()
    """
    Timestamps are integers that increment by 1 for each control cycle.
    Currently the ODrive's control loop frequency is fixed at 8kHz.
    """

    NANOSECONDS = enum.auto()
    """Timestamps are nanoseconds relative to the trigger point."""

    NANOSECONDS_PYTHON = enum.auto()
    """
    Timestamps are with respect to the Python monotonic clock :func:`time.monotonic_ns()`.

    The correlation is based on a best effort of correlating the ODrive's clock
    with. On a Raspberry Pi 4, the accuracy was observed to be in the range of
    1ms - 5ms, but can be worse in some cases (e.g. high CPU load or garbage
    collect event).
    The correlation happens at the time of :func:`~HighRateCapturer.download()`,
    so if the data is downloaded significantly later than the trigger, the
    correlation may be less accurate due to clock drift.
    """

def _ensure_debug_info(odrv: RuntimeDevice):
    try:
        import odrive_private.debug_utils
    except ImportError:
        raise NotImplementedError()
    odrive_private.debug_utils.ensure_debug_info(odrv)

async def _resolve_expression(odrv: RuntimeDevice, expression: Union[str, int]) -> Tuple[int, Callable[[bytes], Any]]:
    """
    Resolves an expression to a tuple of (address, byte_size, bytes_to_val).
    """
    if isinstance(expression, int):
        return expression, 4, (lambda b: int.from_bytes(b, 'little'))
    elif isinstance(expression, str) and expression.startswith("raw:"):
        expr = expression[4:]
        _ensure_debug_info(odrv)
        address, type_info = await odrv._dbg_info.resolve_symbol(expr)
        return address, type_info.byte_size, type_info.bytes_to_val
    elif isinstance(expression, str):
        prop_info = odrv.try_get_prop_info(expression)
        def bytes_to_val(val, codec=prop_info.codec):
            return decode_all([codec], val, odrv)[0]
        address = (0xffff << 16) | prop_info.endpoint_id
        return address, prop_info.codec.size, bytes_to_val
    else:
        raise TypeError("expressions must be int or str type")

async def _odrive_time_to_python_time_ns(odrv: RuntimeDevice, odrive_time: int):
    # TODO: report confidence interval of the time correlation
    python_now = time.monotonic_ns()
    firmware_now = await odrv.read('n_evt_control_loop')
    python_now = (time.monotonic_ns() + python_now) // 2
    firmware_offset = (firmware_now - odrive_time + 2**32) % 2**32
    assert isinstance(firmware_offset, int)
    return python_now - firmware_offset * int(1e9) // _CONTROL_LOOP_FREQ

def _max_inputs(odrv: RuntimeDevice):
    return len(odrv.functions['oscilloscope.config'].inputs)

T = TypeVar('T')

class HighRateCapturer:
    """
    Facility to capture variables from the ODrive at its native control loop rate.

    The variables are recorded into a circular buffer on the ODrive, and a capture
    event can be triggered by the user, similar to an oscilloscope. The buffer is
    then downloaded in a separate step.

    The duration of the recording is determined by the fixed in-firmware buffer
    size and depends on how many variables are being captured. For firmware
    version 0.6.11 on ODrive Pro, S1 and Micro:

    * 1 variable: 2048ms
    * 2 variables: 1024ms
    * 9 variables: 228ms

    Firmware version 0.6.11 or later is required for this feature.

    Usage example from a Python script:

    .. code:: ipython

        from odrive.utils import HighRateCapturer
        capturer = await HighRateCapturer.from_properties(odrv, ['axis0.controller.pos_setpoint', 'axis0.pos_estimate'])
        await capturer.start()
        await capturer.trigger()
        await capturer.wait()
        data = await capturer.download()

    For a shortcut, see :func:`high_rate_capture()`.
    """
    def __init__(self, odrv: RuntimeDevice, type_info: List[Tuple[Any, int, Callable[[bytes], Any]]], unsafe: bool):
        if not odrv.has_property('oscilloscope.trigger_pos'):
            raise NotImplementedError("HighRateCapturer is not compatible with this firmware version")

        self.odrv = odrv
        self.type_info = type_info
        assert all(byte_size <= 4 for _, _, byte_size, _ in self.type_info), "Expressions with byte size > 4 not supported"
        if not unsafe:
            assert all((address & 0xffff0000) == 0xffff0000 for _, address, _, _ in self.type_info), "Only property names are allowed as expressions"

    @staticmethod
    async def from_properties(odrv: RuntimeDevice, properties: Iterable[Union[str, int]], unsafe: bool = False) -> 'HighRateCapturer':
        """
        Creates a :class:`HighRateCapturer` object from a list of property names.

        :param odrv: The ODrive to capture data from.
        :param properties: The paths of the properties to capture, e.g. ``['axis0.controller.pos_setpoint', 'axis0.pos_estimate']``.
        :param unsafe: Should be left as False unless instructed otherwise by ODrive
            support. If set to True, ODrive firmware can reset unexpectedly, potentially
            causing damage to the hardware.
        """
        max_variables = _max_inputs(odrv)
        assert len(properties) > 0, "At least one expression is required"
        assert len(properties) <= max_variables, f"Too many expressions ({len(properties)}). Max allowed: {max_variables}"

        type_info = [(expr, *(await _resolve_expression(odrv, expr))) for expr in properties]
        return HighRateCapturer(odrv, type_info, unsafe)

    async def _download_raw_buffer(self):
        """
        Downloads the raw buffer from the oscilloscope and rotates/prunes it
        according to the current write index and rollover status.
        """
        # If no rollover happened, could just read buffer until pos for better
        # efficiency.
        buf = b''
        buffer_size = await self.odrv.read('oscilloscope.size')
        assert buffer_size % 32 == 0, f"Expected buffer size to be a multiple of 32, but got {buffer_size}"
        for i in range(0, buffer_size, 32):
            raw_ints = await self.odrv.call_function('oscilloscope.get_raw', i)
            buf += struct.pack('<QQQQ', *raw_ints)

        row_size = 4 * len(self.type_info)

        # Prune buf to multiple of sample_size
        # This is needed because wraparound always happens at sample_size granularity.
        buf = buf[:len(buf) - (len(buf) % row_size)]

        pos = await self.odrv.read('oscilloscope.pos')
        trigger_pos = await self.odrv.read('oscilloscope.trigger_pos')
        assert pos % row_size == 0, f"Expected pos to be a multiple of {row_size}, but got {pos}"
        assert trigger_pos % row_size == 0, f"Expected trigger_pos to be a multiple of {row_size}, but got {trigger_pos}"
        buf_part0 = buf[:pos]
        buf_part1 = buf[pos:]
        if await self.odrv.read('oscilloscope.rollover'):
            # If a trigger_point of 1.0 was set, the firmware currently reports
            # the trigger_pos as one sample too early, so the expression below
            # evaluates to len(buf)-1 instead of 0.
            # This makes it distinguishable from the case trigger_point = 0.0.
            trigger_pos = (trigger_pos + len(buf_part1)) % len(buf)
            return (buf_part1 + buf_part0), trigger_pos
        else:
            assert trigger_pos <= len(buf_part0)
            return buf_part0, trigger_pos

    def _decode(self, buf: bytes, trigger_pos: int):
        """
        Decodes the raw buffer into a list of tuples, each tuple containing
        the decoded values for each expression.
        """
        outputs = []
        row_size = 4 * len(self.type_info)
        assert len(buf) % row_size == 0, "Buffer size must be a multiple of sample_size"
        for row_offset in range(0, len(buf), row_size):
            elem = ()
            for i, (_, _, byte_size, bytes_to_val) in enumerate(self.type_info):
                elem_offset = row_offset + i * 4
                elem += (bytes_to_val(buf[elem_offset:elem_offset + byte_size]),)
            outputs.append(elem)
        return outputs, trigger_pos // row_size

    async def start(self):
        """
        Starts recording into a circular buffer on the ODrive. Once the buffer is
        full, the oldest samples are overwritten.

        Only one :class:`HighRateCapturer` instance can be active for each ODrive
        at a time. Starting multiple recordings at the same time causes corrupt
        data once :func:`download()` is called.
        """
        addresses = [address for _, address, _, _ in self.type_info]
        logger.debug(f"Recording from " + ", ".join(['0x{:08x}'.format(addr) for addr in addresses]) + "...")
        
        await self.odrv.call_function('oscilloscope.config', *addresses, *([0] * (_max_inputs(self.odrv) - len(addresses))))

    async def trigger(self, trigger_point: float = DEFAULT_TRIGGER_POINT):
        """
        Triggers the capture.

        After the triggering, use :func:`wait()` to wait for the recording to
        complete.
        
        Has no effect if the capture was already triggered (by a previous call
        to this function or by the ODrive entering
        :attr:`AxisState.IDLE <ODrive.Axis.AxisState.IDLE>`).

        :param trigger_point: Number in the range ``[0.0, 1.0]`` that defines the
            timing of the trigger relative to the capture window.

            * 0.0 means the resulting capture starts at :func:`trigger()`
            * 1.0 means the resulting capture stops at :func:`trigger()`

            Defaults to 0.5.
        """
        assert trigger_point >= 0 and trigger_point <= 1
        await self.odrv.call_function('oscilloscope.trigger', trigger_point)

    async def wait(self, timeout: Optional[float] = None):
        """
        Waits for the recording to complete.

        Recording completes shortly after the trigger. The trigger can is set
        off either manually by calling :func:`trigger()` or automatically when
        the ODrive enters :attr:`AxisState.IDLE <ODrive.Axis.AxisState.IDLE>`
        (e.g. because of an error).

        :param timeout: Optional maximum time [s] to wait for the recording to
            complete. If it is expected that the trigger already fired or will
            fire in a specific time, it is recommended to provide this parameter.
            Otherwise, can be omitted to wait indefinitely.
        """
        i = 0
        tsleep = 0.1
        while await self.odrv.read('oscilloscope.recording'):
            if (not timeout is None) and (i * tsleep >= timeout):
                raise TimeoutError()
            await asyncio.sleep(tsleep)
            i += 1

    async def download(self, return_as: Type[T] = list, t_fmt: Optional[TimestampFmt] = None) -> T:
        """
        Downloads and decodes the recorded data. Recording must have completed
        before calling this function (see :func:`wait()`).

        :param return_as: The requested return type. Can be one of:

            * :class:`list`: the result is returned as a list of lists where each inner list is the timeseries for one expression.
            * :class:`dict`: the result is returned as a dict of the form:

              .. parsed-literal::
                  {
                      'timestamps': [...], # according t_fmt
                      'expr1': [...],
                      'expr2': [...],
                      ...
                  }
            
            * :class:`numpy.ndarray`: the result is returned as a 2D numpy array
              of shape (n_expressions, n_samples), similar to the list format.
            * :class:`numpy.recarray`: the result is returned as a structured
              numpy array with the fields 'timestamps', 'expr1', 'expr2', etc,
              similar to the dict format.
                  
        :param t_fmt: The timestamp format. If None (default), no timestamps are
            included. If not None, timestamps are included as the first series
            in the result.

        :returns: The captured data, in the format specified by `return_as` and `t_fmt`.
        """
        is_recording = await self.odrv.read('oscilloscope.recording')
        assert not is_recording, "Recording is still active. Call wait() before download()."

        logger.debug(f"Fetching buffer...")

        buf, trigger_pos = await self._download_raw_buffer()
        outputs, trigger_sample_idx = self._decode(buf, trigger_pos)

        n_samples = len(outputs)
        sampling_freq = 8000
        logger.debug(f"Collected {n_samples} samples, which corresponds to {n_samples/sampling_freq*1000:.2f} ms of data (assuming a sampling frequency of {sampling_freq})")

        # transpose output
        return_val = [[outputs[i][j] for i in range(n_samples)] for j in range(len(outputs[0]))]

        # Include timestamps if requested
        if t_fmt is not None:
            timestamps = list(range(-trigger_sample_idx, n_samples - trigger_sample_idx))

            # Transform timestamps
            if t_fmt == TimestampFmt.CONTROL_CYCLE:
                pass
            elif t_fmt == TimestampFmt.NANOSECONDS:
                timestamps = [(t * 1e9) // sampling_freq for t in timestamps]
            elif t_fmt == TimestampFmt.NANOSECONDS_PYTHON:
                trigger_timestamp = await self.odrv.read('oscilloscope.triggered_at')
                shift = await _odrive_time_to_python_time_ns(self.odrv, trigger_timestamp)
                timestamps = [((t * 1e9) // sampling_freq) + shift for t in timestamps]
            else:
                raise ValueError(f"Unsupported timestamp format: {t_fmt}")

            return_val = [timestamps] + return_val
            keys = ['timestamps'] + [key for key, _, _, _ in self.type_info]
        else:
            keys = [key for key, _, _, _ in self.type_info]

        # Convert to requested return type
        if return_as == list:
            return return_val
        elif f"{return_as.__module__}.{return_as.__qualname__}" == 'numpy.ndarray':
            # TODO: use structured array instead
            import numpy as np
            return np.array(return_val)
        # Name of the the recarray class differs between numpy versions
        elif f"{return_as.__module__}.{return_as.__qualname__}" in {'numpy.rec.recarray', 'numpy.recarray'}:
            import numpy as np
            return np.rec.fromarrays(return_val, names=keys)
        elif return_as == dict:
            return {
                key: timeseries for key, timeseries in zip(keys, return_val)
            }
        else:
            raise Exception(f"return type {return_as} not supported")

    async def trigger_and_download_async(
            self,
            trigger_point: Optional[float] = DEFAULT_TRIGGER_POINT,
            trigger_timeout: Optional[float] = None,
            return_as: Type[T] = list, t_fmt: Optional[TimestampFmt] = None) -> T:
        """
        Combines :func:`trigger()`, :func:`wait()` and :func:`download()` into a
        single function call.
        
        This function is asynchronous and intended for use in async scripts. For
        use in odrivetool or synchronous scripts, use :func:`trigger_and_download_sync()`.

        :param trigger_point: See :func:`trigger()`.
        :param trigger_timeout: See :func:`wait()`.
        :param return_as: See :func:`download()`.
        :param t_fmt: See :func:`download()`.
        :returns: The captured data, in the format specified by `return_as`.
        """
        if trigger_point is not None:
            await self.trigger(trigger_point)
        else:
            logger.info("waiting for in-firmware trigger...")
        await self.wait(trigger_timeout)
        return await self.download(return_as, t_fmt)

    def trigger_and_download_sync(
            self,
            trigger_point: Optional[float] = DEFAULT_TRIGGER_POINT,
            trigger_timeout: Optional[float] = None,
            return_as: Type[T] = list, t_fmt: Optional[TimestampFmt] = None) -> T:
        """
        Combines :func:`trigger()`, :func:`wait()` and :func:`download()` into a
        single function call.

        This function is synchronous and intended for use in odrivetool or
        synchronous scripts. For asynchronous usage, use
        :func:`trigger_and_download_async()`.

        :param trigger_point: See :func:`trigger()`.
        :param trigger_timeout: See :func:`wait()`.
        :param return_as: See :func:`download()`.
        :param t_fmt: See :func:`download()`.
        :returns: The captured data, in the format specified by `return_as`.
        """
        coro = self.trigger_and_download_async(trigger_point, trigger_timeout, return_as, t_fmt)
        loop = self.odrv.sync_wrapper._loop
        return run_on_loop(coro, loop)

@transform_odrive_objects
async def high_rate_capture(odrv: RuntimeDevice,
                            properties: Iterable[Union[str, int]], unsafe: bool = False, 
                            trigger_point: Optional[float] = DEFAULT_TRIGGER_POINT,
                            trigger_timeout: Optional[float] = None,
                            return_as: Type[T] = list, t_fmt: Optional[TimestampFmt] = None) -> T:
    """
    Captures a short window of data from the ODrive at its native control loop rate.

    The length of the window depends on how many variables are being captured.

    For more information, see :class:`HighRateCapturer`.

    Example:

    .. code:: ipython
        
        from odrive.utils import high_rate_capture
        data = await high_rate_capture(odrv, ['axis0.controller.pos_setpoint', 'axis0.pos_estimate'])

    :param properties: See :func:`HighRateCapturer.from_properties()`.
    :param unsafe: See :func:`HighRateCapturer.from_properties()`.
    :param trigger_point: See :func:`HighRateCapturer.trigger()`.
    :param trigger_timeout: See :func:`HighRateCapturer.wait()`.
    :param return_as: See :func:`HighRateCapturer.download()`.
    :param t_fmt: See :func:`HighRateCapturer.download()`.
    :returns: The captured data, in the format specified by `return_as`.
    """
    capturer = await high_rate_capture_start(odrv, properties, unsafe)
    return await capturer.trigger_and_download_async(trigger_point, trigger_timeout, return_as, t_fmt)

@transform_odrive_objects
async def high_rate_capture_start(odrv: RuntimeDevice,
                                  properties: Iterable[Union[str, int]], unsafe: bool = False):
    """
    Starts recording data on the ODrive at its native control loop rate and
    returns a :class:`HighRateCapturer` that can be used to trigger and download
    the data.

    :param properties: See :func:`HighRateCapturer.from_properties()`.
    :param unsafe: See :func:`HighRateCapturer.from_properties()`.
    :returns: A :class:`HighRateCapturer` object that can be used to trigger and
        download the data.
    """
    capturer = await HighRateCapturer.from_properties(odrv, properties, unsafe)
    await capturer.start()
    return capturer
