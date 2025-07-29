import logging
import time
from pathlib import Path
from ekfsm.system import System

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

config = Path(__file__).parent / "zip2-ccu-only.yaml"
system = System(config)

cpu = system[0]
print(f"probing CPU: {cpu.probe()}")
print(
    f"inventory: {cpu.inventory.vendor()} {cpu.inventory.model()} {cpu.inventory.serial()}"
)

ccu = system.ccu
print(f"probing CCU: {ccu.probe()}")

e = ccu.mux.ch00.eeprom

e.write_cserial(12345678)


def progress_callback(offset):
    print(f"Loading firmware: {offset}")


# with open("/home/klaus/fw-ccu-00-default-0.2.0.bin", "rb") as f:
#     firmware = f.read()
#     ccu.management.load_firmware(firmware, progress_callback)
# time.sleep(5)

print(f"CCU firmware: {ccu.management.identify_firmware()}")

while True:
    cputemp = cpu.th.cputemp()
    print(f"CPU temperature: {cputemp}")
    ccu.fan.push_temperature(-1, cputemp)
    time.sleep(1)
    fan_status = ccu.fan.fan_status(0)
    print(f"Fan status0: {fan_status}")
    fan_status = ccu.fan.fan_status(1)
    print(f"Fan status1: {fan_status}")
