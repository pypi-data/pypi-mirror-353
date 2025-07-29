from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from anytree import AnyNode

from ekfsm.devices import CLASS_MAP
from ekfsm.exceptions import ConfigError

if TYPE_CHECKING:
    from .components import HwModule
    from ekfsm.devices.generic import Device


class BoardDictImporter:

    def __init__(self, nodecls=AnyNode):
        self.nodecls = nodecls

    def import_(self, logger: logging.Logger, data, parent=None, abort: bool = False):
        """Import tree from `data`."""
        return self.__import(logger, data, parent=parent, abort=abort)

    def __import(self, logger: logging.Logger, data, parent=None, abort: bool = False):
        from .components import HwModule

        device_type = data.get("device_type")
        nodecls = CLASS_MAP.get(device_type)
        if nodecls is None:
            raise ConfigError(f"Unknown device type: {device_type}")

        children = data.pop("children", [])
        if parent is not None and isinstance(parent, HwModule):
            # ???
            pass

        node = nodecls(parent=parent, **data)

        if children is not None:
            for child in children:
                try:
                    logger.debug(f"Importing sub device {child}")
                    self.__import(logger, child, parent=node, abort=abort)
                except Exception as e:
                    if abort:
                        logger.error(
                            f"Failed to import sub device {child}: {e}. aborting"
                        )
                        raise e
                    else:
                        logger.error(
                            f"Failed to import sub device {child}: {e}. continue anyway"
                        )
        return node


def deserialize_hardware_tree(
    logger: logging.Logger, data: dict, parent: "HwModule"
) -> tuple[str, str, str, list["Device"]]:
    importer = BoardDictImporter()
    abort = parent.abort

    # better use schema extension for this
    id = data.pop("id", None)
    if id is None:
        raise ConfigError("Board configuration must contain `id`")
    name = data.pop("name", None)
    if name is None:
        raise ConfigError("Board configuration must contain `name`")
    slot_type = data.pop("slot_type")
    if slot_type is None:
        raise ConfigError("Board configuration must contain `board_type`")

    children = data.pop("children", None)
    devices = []
    if children:
        for child in children:
            try:
                logger.debug(f"Importing top level device {child}")
                node = importer.import_(logger, child, parent=parent, abort=abort)
                devices.append(node)
            except Exception as e:
                if abort:
                    logger.error(
                        f"Failed to import top level device {child}: {e}. aborting"
                    )
                    raise e
                else:
                    logger.error(
                        f"Failed to import top level device {child}: {e}. continue anyway"
                    )

    return id, name, slot_type, devices
