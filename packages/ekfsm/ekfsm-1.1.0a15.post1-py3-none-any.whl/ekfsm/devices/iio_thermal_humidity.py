from pathlib import Path

from ekfsm.core.components import SysTree
from ekfsm.log import ekfsm_logger

from ..core.sysfs import SysFSDevice

from .generic import Device
from .iio import iio_get_in_value


class IIOThermalHumidity(Device):
    """
    Device for IIO thermal and/or humidity sensors.

    Parameters
    ----------
    name
        The name of the device.
    parent
        The parent device of the IIOThermalHumidity device. If None, no parent is created.
    children
        The children of the IIOThermalHumidity device. If None, no children are created.
    """

    def __init__(
        self,
        name: str,
        parent: SysTree | None = None,
        children: list[Device] | None = None,
        *args,
        **kwargs,
    ):
        self.logger = ekfsm_logger("IIOThermalHumidity:" + name)
        super().__init__(name, parent, children, *args, **kwargs)
        self.addr = self.get_i2c_chip_addr()
        self.sysfs_device = self.get_i2c_sysfs_device(self.addr)

        dir = list(Path(self.sysfs_device.path).glob("iio:device*"))
        if len(dir) == 0:
            raise FileNotFoundError("iio entry not found")
        self.iio_sysfs = SysFSDevice(dir[0])
        self.logger.debug(f"iio: {self.iio_sysfs.path}")

    def temperature(self) -> float:
        return iio_get_in_value(self.iio_sysfs, "in_temp") / 1000.0

    def humidity(self) -> float:
        return iio_get_in_value(self.iio_sysfs, "in_humidityrelative") / 1000.0
