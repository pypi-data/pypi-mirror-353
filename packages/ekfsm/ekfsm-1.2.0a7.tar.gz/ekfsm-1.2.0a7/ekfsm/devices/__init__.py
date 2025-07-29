from ekfsm.devices.generic import Device
from ekfsm.devices.coretemp import CoreTemp
from ekfsm.devices.smbios import SMBIOS
from .eeprom import EEPROM, EKF_EEPROM, EKF_CCU_EEPROM
from .pmbus import PmBus, PsuStatus
from .gpio import GPIO, EKFIdentificationIOExpander, GPIOExpander
from .ekf_sur_led import EKFSurLed
from .ekf_ccu_uc import EKFCcuUc
from .iio_thermal_humidity import IIOThermalHumidity
from .mux import I2CMux, MuxChannel

CLASS_MAP = {
    "GenericDevice": Device,
    "I2CMux": I2CMux,
    "MuxChannel": MuxChannel,
    "GPIO": GPIO,
    "GPIOExpander": GPIOExpander,
    "EKFIdentificationIOExpander": EKFIdentificationIOExpander,
    "EEPROM": EEPROM,
    "EKF_EEPROM": EKF_EEPROM,
    "EKF_CCU_EEPROM": EKF_CCU_EEPROM,
    "EKFCcuUc": EKFCcuUc,
    "PmBus": PmBus,
    "PsuStatus": PsuStatus,
    "SMBIOS": SMBIOS,
    "HWMON": CoreTemp,
    "EKFSurLed": EKFSurLed,
    "IIOThermalHumidity": IIOThermalHumidity,
}
