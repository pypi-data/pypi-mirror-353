import yamale  # type: ignore
import yaml
import munch

from typing import Any, List, Tuple

schema_str = """
system_config:
  name: str()
  aggregates: map(required=False)
  slots: list(include('slot'))
---
slot:
  name: str()
  slot_type: regex('^CPCI_S0_(PER|SYS|PSU|UTILITY)$')
  desired_hwmodule_type: str()
  desired_hwmodule_name: str()
  attributes: map(required=False)
"""


def _validate_config(config_file: str) -> None:
    schema = yamale.make_schema(content=schema_str)
    data = yamale.make_data(config_file)
    yamale.validate(schema, data)


def _parse_config(config_file: str) -> Any | munch.Munch | List | Tuple:
    with open(config_file) as file:
        config = yaml.safe_load(file)
        munchified_config = munch.munchify(config)
    return munchified_config


def load_config(config_file: str) -> Any:
    _validate_config(config_file)
    config = _parse_config(config_file)
    return config
