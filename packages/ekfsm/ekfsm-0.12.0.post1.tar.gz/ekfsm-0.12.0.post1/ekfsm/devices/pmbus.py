from pathlib import Path

from ekfsm.core.components import SystemComponent

from ..core.sysfs import SysFSDevice

from .generic import Device
from ..core.probe import ProbeableDevice


class PmBus(Device, ProbeableDevice):
    def __init__(
        self,
        name: str,
        parent: SystemComponent | None = None,
        children: list[Device] | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(name, parent, children, **kwargs)
        self.addr = self.get_i2c_chip_addr()
        self.sysfs_device = self.get_i2c_sysfs_device(self.addr)

        files = list(Path(self.sysfs_device.path).rglob("hwmon/*/in1_input"))
        if len(files) == 0:
            raise FileNotFoundError("No HWMON entries found")
        self.hwmon_sysfs = SysFSDevice(files[0].parent)

    def probe(self, *args, **kwargs) -> bool:
        from ekfsm.core import HwModule

        assert isinstance(self.root, HwModule)
        return self.root.id == self.model()

    # Voltage and Current Interfaces
    def _in_conversion(self, in_file: str) -> float:
        return float(self.hwmon_sysfs.read_attr_utf8(in_file)) / 1000.0

    def _current_conversion(self, in_file: str) -> float:
        return float(self.hwmon_sysfs.read_attr_utf8(in_file)) / 1000.0

    def in1_input(self) -> float:
        return self._in_conversion("in1_input")

    def in2_input(self) -> float:
        return self._in_conversion("in2_input")

    def curr1_input(self) -> float:
        return self._current_conversion("curr1_input")

    def curr2_input(self) -> float:
        return self._current_conversion("curr2_input")

    # Inventory Interface
    def vendor(self) -> str:
        return self.hwmon_sysfs.read_attr_utf8("vendor").strip()

    def model(self) -> str:
        return self.hwmon_sysfs.read_attr_utf8("model").strip()

    def serial(self) -> str:
        return self.hwmon_sysfs.read_attr_utf8("serial").strip()

    def revision(self) -> str:
        return self.hwmon_sysfs.read_attr_utf8("revision").strip()
