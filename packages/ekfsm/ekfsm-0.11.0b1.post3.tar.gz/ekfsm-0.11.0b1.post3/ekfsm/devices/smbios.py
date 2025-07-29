from pathlib import Path
from ekfsm.core.components import HwModule
from ekfsm.core.sysfs import SysFSDevice, SYSFS_ROOT
from .generic import Device


class SMBIOS(Device):
    """
    A class to represent the SMBIOS device.

    A SMBIOS device is a virtual device that is used to read system
    configuration values from the DMI table.

    Note:
    Currently, only the board version / revision is read from the DMI table.
    """

    def __init__(
        self,
        name: str,
        parent: HwModule | None = None,
        *args,
        **kwargs,
    ):
        self.sysfs_device: SysFSDevice = SysFSDevice(SYSFS_ROOT / Path("devices/virtual/dmi/id"))

        super().__init__(name, parent, None, *args, **kwargs)

    def revision(self) -> str:
        """
        Get the board revision from the DMI table.

        Returns
        -------
        str
            The board revision.
        """
        return self.sysfs_device.read_attr_utf8("board_version").strip()
