from .generic import Device
from smbus2 import SMBus
from enum import Enum
from typing import Tuple
from ekfsm.core.components import SystemComponent
from ..exceptions import AcquisitionError
import struct


class CcuCommands(Enum):
    NOP = 0x01
    IMU_SAMPLES = 0x10
    FAN_STATUS = 0x11
    VIN_VOLTAGE = 0x12
    CCU_TEMPERATURE = 0x13
    CCU_HUMIDITY = 0x14
    PUSH_TEMPERATURE = 0x15
    SW_SHUTDOWN = 0x16
    WD_TRIGGER = 0x17
    IDENTIFY_FIRMWARE_TITLE = 0x80
    IDENTIFY_FIRMWARE_VERSION = 0x81
    LOAD_FIRMWARE_CHUNK = 0x82
    LOAD_PARAMETERSET = 0x83
    GET_PARAMETERSET_BEGIN = 0x84
    GET_PARAMETERSET_FOLLOW = 0x85
    RESTART = 0x8F


class EKFCcuUc(Device):
    """
    A class to communicate with I2C microcontroller on the EKF CCU.
    """

    def __init__(
        self,
        name: str,
        parent: SystemComponent | None,
        *args,
        **kwargs,
    ):
        super().__init__(name, parent, None, *args, **kwargs)
        self._i2c_addr = self.get_i2c_chip_addr()
        self._i2c_bus = self.get_i2c_bus_number()
        self._smbus = SMBus(self._i2c_bus)

    def __str__(self) -> str:
        return (
            f"EKFCCU - I2C Bus/Address: {self._i2c_bus}/{hex(self._i2c_addr)}; "
            f"sysfs_path: {self.sysfs_device.path if self.sysfs_device else ''}"
        )

    def temperature(self) -> float:
        """
        Get the temperature from the CCU thermal/humidity sensor.
        The temperature is read once per second.

        Returns
        -------
        float
            The temperature in degrees Celsius.

        Raises
        ------
        AcquisitionError
            If the temperature cannot be read, for example, because the sensor is not working.
        """
        return (
            self._get_signed_word_data(CcuCommands.CCU_TEMPERATURE.value, "temperature")
            / 10.0
        )

    def humidity(self) -> float:
        """
        Get the relative humidity from the CCU thermal/humidity sensor.
        The humidity is read once per second.

        Returns
        -------
        float
            The relative humidity in percent.

        Raises
        ------
        AcquisitionError
            If the humidity cannot be read, for example, because the sensor is not working.
        """
        return (
            self._get_signed_word_data(CcuCommands.CCU_HUMIDITY.value, "humidity")
            / 10.0
        )

    def vin_voltage(self) -> float:
        """
        Get the system input voltage from the CCU (the pimary voltage of the PSU).
        The voltage is read every 100ms.

        Returns
        -------
        float
            The system input voltage in volts.

        Raises
        ------
        AcquisitionError
            If the voltage cannot be read, for example, because the ADC is not working.
        """
        return (
            self._get_signed_word_data(CcuCommands.VIN_VOLTAGE.value, "VIN voltage")
            / 10.0
        )

    def _get_signed_word_data(self, cmd: int, what: str) -> int:
        v = self._smbus.read_word_data(self._i2c_addr, cmd)
        if v == 0x8000:
            raise AcquisitionError(f"cannot read {what}")
        return struct.unpack("<h", struct.pack("<H", v))[0]

    def fan_status(self, fan: int) -> Tuple[float, float, int]:
        """
        Get the status of a fan.

        Parameters
        ----------
        fan
            The fan number (0-2).

        Returns
        -------
        Tuple[float, float, int]
            The desired speed, the actual speed, and the diagnostic value.
            The diagnostic value is a bitfield with the following meaning:

            - bit 0: 0 = fan status is invalid, 1 = fan status is valid
            - bit 1: 0 = no error detected, 1 = fan is stuck
        """
        data = self._smbus.read_block_data(self._i2c_addr, CcuCommands.FAN_STATUS.value)
        _data = bytes(data)
        desired, actual, diag = struct.unpack("<HHB", _data[fan * 5 : fan * 5 + 5])
        return desired, actual, diag

    def push_temperature(self, fan: int, temp: float) -> None:
        """
        Tell FAN controller the external temperature, usually the CPU temperature.

        Parameters
        ----------
        fan
            The fan number (0-2), or -1 to set the external temperature of all fans.

        temp
            The external temperature in degrees Celsius.

        Important
        ---------
        If push_temperature is no more called for a certain time (configurable with `fan-push-tout` parameter),
        the fan controller will fallback to it's default fan speed (configurable with the `fan-defrpm` parameter).

        """
        if fan == -1:
            fan = 0xFF
        data = struct.pack("<Bh", fan, int(temp * 10))
        self._smbus.write_block_data(
            self._i2c_addr, CcuCommands.PUSH_TEMPERATURE.value, list(data)
        )

    def sw_shutdown(self) -> None:
        """
        Tell CCU that the system is going to shutdown.
        This cause the CCU's system state controller to enter shutdown state and power off the system after a certain time
        (parameter `shutdn-delay`).

        """
        self._smbus.write_byte(self._i2c_addr, CcuCommands.SW_SHUTDOWN.value)

    def wd_trigger(self) -> None:
        """
        Trigger the CCU's application watchdog.
        This will reset the watchdog timer.

        The CCU watchdog is only enabled when the parameter `wd-tout` is set to a value greater than 0. Triggering
        the watchdog when the timeout is 0 will have no effect.

        If the watchdog is not reset within the timeout, the CCU will power cycle the system.
        """
        self._smbus.write_byte(self._i2c_addr, CcuCommands.WD_TRIGGER.value)

    #
    # Management commands
    #
    def identify_firmware(self) -> Tuple[str, str]:
        """
        Get the firmware title and version of the CCU.

        Returns
        -------
        Tuple[str, str]
            The firmware title and version.
        """
        title = bytes(
            self._smbus.read_block_data(
                self._i2c_addr, CcuCommands.IDENTIFY_FIRMWARE_TITLE.value
            )
        ).decode("utf-8")
        version = bytes(
            self._smbus.read_block_data(
                self._i2c_addr, CcuCommands.IDENTIFY_FIRMWARE_VERSION.value
            )
        ).decode("utf-8")
        return title, version

    def load_firmware(self, firmware: bytes, progress_callback=None) -> None:
        """
        Load firmware into the CCU.

        The firmware must be the binary firmware file containing the application partition,
        typically named `fw-ccu-mm-default.bin`,
        where `mm` is the major version of the CCU hardware.

        The download can take several minutes, that is why a progress callback can be provided.

        When the download is complete and successful, the CCU will restart. To check if the firmware was loaded successfully,
        call :meth:`identify_firmware()` after the restart.

        Parameters
        ----------
        firmware
            The firmware binary data.

        progress_callback
            A callback function that is called with the current progress in bytes.

        Warning
        ---------
        Do not call this method at the same time from multiple threads or processes.

        """
        offset = 0
        max_chunk_len = 28
        while len(firmware) > 0:
            chunk, firmware = firmware[:max_chunk_len], firmware[max_chunk_len:]
            self._load_firmware_chunk(offset, len(firmware) == 0, chunk)
            offset += len(chunk)
            if len(firmware) != 0:
                self._nop()
            if progress_callback is not None:
                progress_callback(offset)

    def _load_firmware_chunk(self, offset: int, is_last: bool, data: bytes) -> None:
        if is_last:
            offset |= 0x80000000
        hdr = struct.pack("<I", offset)
        data = hdr + data
        self._smbus.write_block_data(
            self._i2c_addr, CcuCommands.LOAD_FIRMWARE_CHUNK.value, list(data)
        )

    def get_parameterset(self) -> str:
        """
        Get the CCU parameterset in JSON format.

        A typical parameterset looks like this:

        .. code-block:: json

            {
                "version":      "factory",
                "parameters":   {
                        "num-fans":     "2",
                        "fan-temp2rpm": "25:2800;50:5000;100:6700",
                        "fan-rpm2duty": "2800:55;5000:88;6700:100",
                        "fan-defrpm":   "5500",
                        "fan-ppr":      "2",
                        "fan-push-tout":        "4000",
                        "pon-min-temp": "-25",
                        "pon-max-temp": "70",
                        "shutdn-delay": "120",
                        "wd-tout":      "0",
                        "pwrcycle-time":        "10"
                },
                "unsupported_parameters":       [],
                "missing_parameters":   ["num-fans", "fan-temp2rpm", "fan-rpm2duty", "fan-defrpm", "fan-ppr", \
                    "fan-push-tout", "pon-min-temp", "pon-max-temp", "shutdn-delay", "wd-tout", "pwrcycle-time"],
                "invalid_parameters":   [],
                "reboot_required":      false
            }

        `version` is the version of the parameterset. If no parameterset has been loaded by the user, the version is `factory`,
        otherwise it is the version of the loaded parameterset.

        `parameters` contains the current values of all parameters of the parameterset.

        `unsupported_parameters` contains the names of parameters that might have been downloaded, but
        are not supported by the CCU firmware.

        `missing_parameters` contains the names of parameters that have not been downloaded yet. Those parameters will
        have their default values.

        `invalid_parameters` contains the names of parameters that have been downloaded, but have invalid values.
        Those parameters will have their default values.

        `reboot_required` is a flag that indicates if a reboot is required to apply the parameterset.


        Returns
        -------
        str
            The parameterset in JSON format.

        Warning
        ---------
        Do not call this method at the same time from multiple threads or processes.
        """
        json = b""
        begin = True
        while True:
            chunk = self._get_parameterset_chunk(begin)
            if len(chunk) < 32:
                break
            json += chunk
            begin = False
        return json.decode("utf-8")

    def _get_parameterset_chunk(self, begin: bool) -> bytes:
        data = self._smbus.read_block_data(
            self._i2c_addr,
            (
                CcuCommands.GET_PARAMETERSET_BEGIN.value
                if begin
                else CcuCommands.GET_PARAMETERSET_FOLLOW.value
            ),
        )
        return bytes(data)

    def load_parameterset(self, _cfg: str) -> None:
        """
        Load a parameterset into the CCU.

        The parameterset must be a JSON string containing the parameterset, for example:

        .. code-block:: json

            {
                "version": "1.0.0",
                "parameters":   {
                    "fan-defrpm": "6000"
                }
            }


        This would load a parameterset with just one parameter, the default fan speed. All other parameters will
        be set to their default values.

        In order to apply the parameterset, the CCU must be restarted.

        Parameters
        ----------
        _cfg
            The parameterset in JSON format.

        Warning
        ---------
        Do not call this method at the same time from multiple threads or processes.

        """
        cfg = _cfg.encode("utf-8")
        offset = 0
        max_chunk_len = 28
        while len(cfg) > 0:
            chunk, cfg = cfg[:max_chunk_len], cfg[max_chunk_len:]
            self._load_parameterset_chunk(offset, len(cfg) == 0, chunk)
            offset += len(chunk)
            self._nop()

    def _load_parameterset_chunk(self, offset: int, is_last: bool, data: bytes) -> None:
        if is_last:
            offset |= 0x80000000
        hdr = struct.pack("<I", offset)
        data = hdr + data
        self._smbus.write_block_data(
            self._i2c_addr, CcuCommands.LOAD_PARAMETERSET.value, list(data)
        )

    def restart(self) -> None:
        """
        Restart the CCU.
        """
        self._smbus.write_byte(self._i2c_addr, CcuCommands.RESTART.value)

    def _nop(self) -> None:
        self._smbus.read_word_data(self._i2c_addr, CcuCommands.NOP.value)
