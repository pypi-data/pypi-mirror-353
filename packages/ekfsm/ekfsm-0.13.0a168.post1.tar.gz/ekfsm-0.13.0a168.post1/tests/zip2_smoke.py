from pathlib import Path
from ekfsm.system import System
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

config = Path(__file__).parent / "zip2-smoke.yaml"
system = System(config)


cpu = system[0]
print(f"probing CPU: {cpu.probe()}")
print(
    f"inventory: {cpu.inventory.vendor()} {cpu.inventory.model()} {cpu.inventory.serial()}"
)

sq1 = system[1]
print(f"probing SQ1: {sq1.probe()}")
print(
    f"inventory: {sq1.inventory.vendor()} {sq1.inventory.model()} {sq1.inventory.serial()}"
)

sur = system.sur
print(f"probing SUR: {sur.probe()}")
print(
    f"inventory: {sur.inventory.vendor()} {sur.inventory.model()} {sur.inventory.serial()}"
)

spv = system.spv
print(f"probing SPV: {spv.probe()}")
print(
    f"inventory: {spv.inventory.vendor()} {spv.inventory.model()} {spv.inventory.serial()}"
)

print(system)

# SUR LED Test
system.sur.led_a.set(0, "red")
system.sur.led_a.set(1, "yellow")
system.sur.led_c.set(0, "white")
system.sur.led_d.set(1, "blue")

print(f"SUR TEMP: {system.sur.th.temperature()}")
print(f"SUR HUMIDITY: {system.sur.th.humidity()}")


# CCU Test
ccu = system.ccu
print(f"CCU firmware: {ccu.management.identify_firmware()}")

# SPV Test
print(f"modem1 control lines {spv.gpio0.num_lines()}")
print(f"modem1 control lines {spv.gpio1.num_lines()}")
print(f"modem1 control lines {spv.gpio2.num_lines()}")
