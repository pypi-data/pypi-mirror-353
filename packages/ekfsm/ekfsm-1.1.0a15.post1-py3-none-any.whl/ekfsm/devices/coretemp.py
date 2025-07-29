from __future__ import annotations
import os
import glob
from pathlib import Path

from ekfsm.core.sysfs import SYSFS_ROOT
from ekfsm.devices.generic import Device

# Path to the root of the HWMON sysfs filesystem
HWMON_ROOT = SYSFS_ROOT / Path("class/hwmon")


def find_core_temp_dir(hwmon_dir) -> Path:
    """
    Find the directory containing the coretemp hwmon device.

    Args:
        hwmon_dir: Path to the hwmon directory

    Returns:
        Path to the directory containing the coretemp hwmon device

    Raises:
        FileNotFoundError: If no coretemp directory is found
    """
    # List all 'name' files in each subdirectory of hwmon_dir
    name_files = glob.glob(os.path.join(hwmon_dir, "*", "name"))

    # Search for the file containing "coretemp"
    for name_file in name_files:
        with open(name_file, "r") as file:
            if file.readline().strip() == "coretemp":
                # Return the directory containing this file
                return Path(os.path.dirname(name_file))

    raise FileNotFoundError("No coretemp directory found")


class CoreTemp(Device):
    """
    This class provides an interface to read the CPU core temperature from the HWMON device.

    Note:
    Currently, only the average temperature over all cores is read from the HWMON device.
    """

    def __init__(
        self,
        name: str,
        parent: Device,
        *args,
        **kwargs,
    ):
        from ekfsm.core.sysfs import SysFSDevice, SYSFS_ROOT

        self.sysfs_device: SysFSDevice = SysFSDevice(
            find_core_temp_dir(SYSFS_ROOT / Path("class/hwmon"))
        )

        super().__init__(name, parent, None, *args, **kwargs)

    def cputemp(self):
        """
        Get the CPU temperature from the HWMON device.

        Returns
        -------
        int
            The CPU temperature in degrees Celsius.
        """
        return int(self.sysfs_device.read_attr_utf8("temp1_input").strip()) / 1000
