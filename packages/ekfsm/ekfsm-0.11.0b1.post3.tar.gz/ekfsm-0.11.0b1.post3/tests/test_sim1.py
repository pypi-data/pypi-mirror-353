import pytest
import pprint
import logging
from pathlib import Path

from ekfsm.system import System, HwModule
from ekfsm.simctrl import enable_simulation
from ekfsm.simctrl import register_gpio_simulations


@pytest.fixture
def simulation():
    enable_simulation(Path(__file__).parent / "sim" / "sys")
    register_gpio_simulations()


def test_system(simulation):
    config = Path(__file__).parent / "sim" / "test_system.yaml"
    system = System(config)
    pprint.pprint(f"System slots {system.slots}")

    psu = system.psu
    assert psu is not None
    assert isinstance(psu, HwModule)
    assert psu.probe()
    assert psu.inventory.vendor() == "Hitron"
    assert psu.inventory.model() == "HDRC300"
    assert psu.main.voltage() == 12.2
    assert psu.sby.current() == 0.5

    cpu = system["CPU"]
    assert cpu is not None
    assert isinstance(cpu, HwModule)
    assert cpu.inventory.vendor() == "EKF Elektronik"
    assert cpu.inventory.model() == "SC9-TOCCATA"
    assert cpu.inventory.serial() == "53082029"

    srf = system.slots["SLOT1"].hwmodule
    assert srf is not None
    assert isinstance(srf, HwModule)

    assert srf.probe()

    assert srf.inventory.vendor() == "EKF Elektronik"
    assert srf.inventory.model() == "SRF-FAN"
    assert srf.inventory.revision() == "0"
    assert srf.inventory.serial() == "54021107"
    assert srf.mux.get_i2c_bus_number() == 1
    assert srf.mux.ch00.gpio.get_i2c_bus_number() == 9

    ccu = system.ccu
    assert ccu is not None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    pytest.main([__file__])
