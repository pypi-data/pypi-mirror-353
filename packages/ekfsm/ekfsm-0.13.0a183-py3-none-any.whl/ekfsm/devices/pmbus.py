from enum import IntFlag
from pathlib import Path

from ekfsm.core.components import SysTree

from ..core.sysfs import SysFSDevice, sysfs_root

from .generic import Device
from ..core.probe import ProbeableDevice

from time import sleep
from functools import wraps
from ekfsm.log import ekfsm_logger
from threading import Lock
import re

__all__ = ["PsuStatus", "PmBus", "retry"]

logger = ekfsm_logger(__name__)


def retry(max_attempts=5, delay=0.5):
    """
    Retry decorator.

    Decorator that retries a function a number of times before giving up.

    This is useful for functions that may fail due to transient errors.

    Note
    ----
    This is needed for certain PMBus commands that may fail due to transient errors
    because page switching timing is not effectively handled by older kernel versions.

    Important
    ---------
    This decorator is thread-safe, meaning a read attempt is atomic and cannot
    be interupted by scheduler.

    Parameters
    ----------
    max_attempts
        The maximum number of attempts before giving up.
    delay
        The delay in seconds between attempts.
    """

    lock = Lock()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                with lock:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempts += 1
                        if attempts == max_attempts:
                            logger.exception(
                                f"Failed to execute {func.__name__} after {max_attempts} attempts: {e}"
                            )
                            raise e
                        logger.info(
                            f"Retrying execution of {func.__name__} in {delay}s..."
                        )
                sleep(delay)

        return wrapper

    return decorator


class PsuStatus(IntFlag):
    """
    Represents the status of a PSU according to STATUS_BYTE register.

    See Also
    --------
    `PMBus Power System Management Protocol Specification - Part II - Revision 1.4, Fig. 60 <https://pmbus.org/>`_
    """

    OUTPUT_OVERVOLTAGE = 0x20
    OUTPUT_OVERCURRENT = 0x10
    INPUT_UNDERVOLTAGE = 0x08
    TEMP_ANORMALY = 0x04
    COMMUNICATION_ERROR = 0x02
    ERROR = 0x01
    OK = 0x00


class PmBus(Device, ProbeableDevice):

    def __init__(
        self,
        name: str,
        parent: SysTree | None = None,
        children: list[Device] | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(name, parent, children, **kwargs)
        self.addr = self.get_i2c_chip_addr()
        self.sysfs_device = self.get_i2c_sysfs_device(self.addr)

        files = list(Path(self.sysfs_device.path).rglob("hwmon/*/in1_input"))
        if len(files) == 0:
            raise FileNotFoundError("No HWMON entries found in sysfs")
        self.hwmon_sysfs = SysFSDevice(files[0].parent)

        self.debugfs_root = sysfs_root() / "kernel/debug/pmbus"
        files = list(self.debugfs_root.rglob("hwmon*/status*_input"))
        if len(files) == 0:
            raise FileNotFoundError("No HWMON entries found in debugfs")
        self.hwmon_debugfs = SysFSDevice(files[0].parent)

    def probe(self, *args, **kwargs) -> bool:
        from ekfsm.core import HwModule

        assert isinstance(self.hw_module, HwModule)
        # compare the regexp from the board yaml file with the model
        return re.match(self.hw_module.id, self.model()) is not None

    # Voltage and Current Interfaces
    def _conversion(self, in_file: str) -> float:
        return float(self.hwmon_sysfs.read_attr_utf8(in_file)) / 1000.0

    @retry()
    def in1_input(self) -> float:
        """
        Get input voltage of PSU page 1.

        Returns
        -------
            Input voltage in volts
        """
        return self._conversion("in1_input")

    @retry()
    def in2_input(self) -> float:
        """
        Get input voltage of PSU page 2.

        Returns
        -------
            Input voltage in volts
        """
        return self._conversion("in2_input")

    @retry()
    def curr1_input(self) -> float:
        """
        Get input current of PSU page 1.

        Returns
        -------
            Input current in amperes
        """
        return self._conversion("curr1_input")

    @retry()
    def curr2_input(self) -> float:
        """
        Get input current of PSU page 2.

        Returns
        -------
            Input current in amperes
        """
        return self._conversion("curr2_input")

    # Status Interface
    @retry()
    def status0_input(self) -> PsuStatus:
        """
        Get the status of PSU page 1.

        Returns
        -------
            PSU status as defined in PsuStatus
        """
        status = int(self.hwmon_debugfs.read_attr_utf8("status0_input").strip(), 16)
        return PsuStatus(status)

    @retry()
    def status1_input(self) -> PsuStatus:
        """
        Get the status of PSU page 2.

        Returns
        -------
            PSU status as defined in PsuStatus
        """
        status = int(self.hwmon_debugfs.read_attr_utf8("status1_input").strip(), 16)
        return PsuStatus(status)

    # Temperature Interface
    @retry()
    def temp1_input(self) -> float:
        """
        Get the PSU temperature.

        Returns
        -------
            PSU temperature in degrees celsius
        """
        return self._conversion("temp1_input")

    # Inventory Interface
    def vendor(self) -> str:
        """
        Get the vendor of the PSU.

        Returns
        -------
            PSU vendor
        """
        return self.hwmon_sysfs.read_attr_utf8("vendor").strip()

    def model(self) -> str:
        """
        Get the model of the PSU.

        Returns
        -------
            PSU model
        """
        return self.hwmon_sysfs.read_attr_utf8("model").strip()

    def serial(self) -> str:
        """
        Get the serial number of the PSU.

        Returns
        -------
            PSU serial number
        """
        return self.hwmon_sysfs.read_attr_utf8("serial").strip()

    def revision(self) -> str:
        """
        Get the revision of the PSU.

        Returns
        -------
            PSU revision
        """
        return self.hwmon_sysfs.read_attr_utf8("revision").strip()
