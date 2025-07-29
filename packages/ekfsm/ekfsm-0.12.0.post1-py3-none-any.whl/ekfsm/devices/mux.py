from ekfsm.core.components import SystemComponent

from ..core.sysfs import SysFSDevice
from .generic import Device


class MuxChannel(Device):
    def __init__(
        self,
        name: str,
        channel_id: int,
        parent: 'I2CMux',
        children: list[Device] | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(name=name, parent=parent, children=children)
        self.channel_id = channel_id

        assert parent.sysfs_device is not None
        assert isinstance(self.parent, I2CMux)

        path = parent.sysfs_device.path / f"channel-{self.channel_id}"
        self.sysfs_device = SysFSDevice(path)


class I2CMux(Device):
    def __init__(
        self,
        name: str,
        parent: SystemComponent | None = None,
        children: list[MuxChannel] | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(name, parent, children, **kwargs)

        self.addr = self.get_i2c_chip_addr()
        self.sysfs_device = self.get_i2c_sysfs_device(self.addr)
