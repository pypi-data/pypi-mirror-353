from typing import TYPE_CHECKING
from munch import Munch
from ekfsm.core.components import SystemComponent
from ekfsm.core.sysfs import SysFSDevice, sysfs_root
from ekfsm.exceptions import ConfigError
from pathlib import Path

if TYPE_CHECKING:
    from ekfsm.core.components import HwModule


class Device(SystemComponent):
    """
    A generic device.
    """

    def __init__(
        self,
        name: str,
        parent: SystemComponent | None = None,
        children: list["Device"] | None = None,
        *args,
        **kwargs
    ):
        super().__init__(name)
        self.parent = parent
        self.device_args = kwargs
        self.logger.debug(f"Device: {name} {kwargs}")

        if children:
            self.children = children

        if not hasattr(self, "sysfs_device"):
            self.sysfs_device: SysFSDevice | None = None

        self._provides_attrs = kwargs.get("provides", {})

        self.provides = self.__post_init__(Munch(self._provides_attrs))

    def __post_init__(self, provides: Munch) -> Munch:
        return self.__init_dynamic_attrs__(provides)

    def __init_dynamic_attrs__(self, provides: Munch) -> Munch:

        for key, fields in provides.items():
            if isinstance(fields, dict):
                provides[key] = self.__init_dynamic_attrs__(Munch(fields))
            elif isinstance(fields, list | str):
                provides[key] = Munch()

                if isinstance(fields, str):
                    fields = [fields]

                while fields:
                    iface = fields.pop()
                    if isinstance(iface, dict):
                        name = list(iface.keys())[0]
                        try:
                            func = list(iface.values())[0]
                        except IndexError:
                            raise ConfigError(
                                f"{self.name}: No function given for interface {name}."
                            )
                        if not hasattr(self, func):
                            raise NotImplementedError(
                                f"{self.name}: Function {func} for interface {name} not implemented."
                            )
                        provides[key].update({name: getattr(self, func)})
                    else:
                        if not hasattr(self, iface):
                            raise NotImplementedError(
                                f"{self.name}: Function {iface} for provider {key} not implemented."
                            )
                        provides[key].update({iface: getattr(self, iface)})

        return provides

    def read_sysfs_attr_bytes(self, attr: str) -> bytes | None:
        if self.sysfs_device and len(attr) != 0:
            return self.sysfs_device.read_attr_bytes(attr)
        return None

    def read_sysfs_attr_utf8(self, attr: str) -> str | None:
        if self.sysfs_device and len(attr) != 0:
            return self.sysfs_device.read_attr_utf8(attr)
        return None

    def write_sysfs_attr(self, attr: str, data: str | bytes) -> None:
        if self.sysfs_device and len(attr) != 0:
            return self.sysfs_device.write_attr(attr, data)
        return None

    @property
    def hw_module(self) -> 'HwModule':
        from ekfsm.core.components import HwModule

        if isinstance(self.root, HwModule):
            return self.root
        else:
            raise RuntimeError("Device is not a child of HwModule")

    def get_i2c_chip_addr(self) -> int:
        assert self.parent is not None

        chip_addr = self.device_args.get("addr")
        if chip_addr is None:
            raise ConfigError(
                f"{self.name}: Chip address not provided in board definition"
            )

        if not hasattr(self.parent, "sysfs_device") or self.parent.sysfs_device is None:
            # our device is the top level device of the slot
            # compute chip address from board yaml and slot attributes
            slot_attributes = self.hw_module.slot.attributes

            if slot_attributes is None:
                raise ConfigError(
                    f"{self.name}: Slot attributes not provided in system configuration"
                )

            if not self.hw_module.is_master:
                # slot coding is only used for non-master devices
                if not hasattr(slot_attributes, "slot_coding"):
                    raise ConfigError(
                        f"{self.name}: Slot coding not provided in slot attributes"
                    )

                slot_coding_mask = 0xFF

                if hasattr(slot_attributes, "slot_coding_mask"):
                    slot_coding_mask = slot_attributes.slot_coding_mask

                chip_addr |= slot_attributes.slot_coding & slot_coding_mask

        return chip_addr

    def get_i2c_sysfs_device(self, addr: int) -> SysFSDevice:
        from ekfsm.core.components import HwModule

        parent = self.parent
        assert parent is not None

        # if parent is a HwModule, we can get the i2c bus from the master device
        if isinstance(parent, HwModule):
            i2c_bus_path = self._master_i2c_bus()
        else:
            # otherwise the parent must be a MuxChannel
            from ekfsm.devices.mux import MuxChannel

            assert isinstance(parent, MuxChannel)
            assert parent.sysfs_device is not None
            i2c_bus_path = parent.sysfs_device.path

        # search for device with addr
        for entry in i2c_bus_path.iterdir():
            if (
                entry.is_dir()
                and not (entry / "new_device").exists()  # skip bus entries
                and (entry / "name").exists()
            ):
                # for PRP devices, address is contained in firmware_node/description
                if (entry / "firmware_node").exists() and (
                    entry / "firmware_node" / "description"
                ).exists():
                    description = (
                        (entry / "firmware_node/description").read_text().strip()
                    )
                    got_addr = int(description.split(" - ")[0], 16)
                    if got_addr == addr:
                        return SysFSDevice(entry)

                # for non-PRP devices, address is contained in the directory name (e.g. 2-0018)
                else:
                    got_addr = int(entry.name.split("-")[1], 16)
                    if got_addr == addr:
                        return SysFSDevice(entry)

        raise FileNotFoundError(
            f"Device with address 0x{addr:x} not found in {i2c_bus_path}"
        )

    @staticmethod
    def _master_i2c_get_config(master: "HwModule") -> dict:
        if (
            master.config.get("bus_masters") is not None
            and master.config["bus_masters"].get("i2c") is not None
        ):
            return master.config["bus_masters"]["i2c"]
        else:
            raise ConfigError("Master definition incomplete")

    def _master_i2c_bus(self) -> Path:
        if self.hw_module.is_master:
            # we are the master
            master = self.hw_module
            master_key = "MASTER_LOCAL_DEFAULT"
            override_master_key = self.device_args.get("i2c_master", None)
            if override_master_key is not None:
                master_key = override_master_key
        else:
            # another board is the master
            if self.hw_module.slot.master is None:
                raise ConfigError(
                    f"{self.name}: Master board not found in slot attributes"
                )

            master = self.hw_module.slot.master
            master_key = self.hw_module.slot.slot_type.name

        i2c_masters = self._master_i2c_get_config(master)

        if i2c_masters.get(master_key) is not None:
            dir = sysfs_root() / Path(i2c_masters[master_key])
            bus_dirs = list(dir.glob("i2c-*"))
            if len(bus_dirs) == 1:
                return bus_dirs[0]
            elif len(bus_dirs) > 1:
                raise ConfigError(f"Multiple master i2c buses found for {master_key}")
            raise ConfigError(f"No master i2c bus found for {master_key}")
        else:
            raise ConfigError(f"Master i2c bus not found for {master_key}")

    def get_i2c_bus_number(self) -> int:
        """
        Get the I2C bus number of the device. Works for devices that do not have a sysfs_device attribute.
        """
        from ekfsm.devices.mux import MuxChannel

        if isinstance(self, MuxChannel):
            raise RuntimeError(f"{self.name}: MuxChannel does not have a bus number")

        if self.sysfs_device is None:
            if self.parent is None:
                raise RuntimeError(f"{self.name}: Must have a parent to get bus number")
            parent_path = self.parent.sysfs_device.path
        else:
            parent_path = self.sysfs_device.path.parent
        if parent_path.is_symlink():
            parent_path = parent_path.readlink()
        bus_number = parent_path.name.split("-")[1]
        return int(bus_number)

    def __repr__(self) -> str:
        sysfs_path = getattr(self.sysfs_device, "path", "")
        return f"{self.name}; sysfs_path: {sysfs_path}"
