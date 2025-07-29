from ekfsm.core.components import SysTree

from ..core.sysfs import SysFSDevice
from .generic import Device


class MuxChannel(Device):
    """
    A MuxChannel is a device that represents a channel on an I2C multiplexer.
    It is a child of the I2CMux device.
    The MuxChannel device is used to access the I2C bus on the channel.

    Parameters
    ----------
    name
        The name of the device.
    channel_id
        The channel ID of the device.
    parent
        The parent device of the MuxChannel.
    children
        The children of the MuxChannel device. If None, no children are created.
    """

    def __init__(
        self,
        name: str,
        channel_id: int,
        parent: "I2CMux",
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
    """
    This class represents an I2C multiplexer device.

    Parameters
    ----------
    name
        The name of the device.
    parent
        The parent device of the I2CMux device. If None, no parent is created.
    children
        The children of the I2CMux device. If None, no children are created.
    """

    def __init__(
        self,
        name: str,
        parent: SysTree | None = None,
        children: list[MuxChannel] | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(name, parent, children, **kwargs)

        self.addr = self.get_i2c_chip_addr()
        self.sysfs_device = self.get_i2c_sysfs_device(self.addr)
