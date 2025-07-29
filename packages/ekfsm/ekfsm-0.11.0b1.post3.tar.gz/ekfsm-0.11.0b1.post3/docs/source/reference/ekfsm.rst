ekfsm package
=============

.. This generates documentation for all members in the __all__ list of the ekfsm package.
.. automodule:: ekfsm

.. automodule:: ekfsm.exceptions

ekfsm.devices package
=====================

.. We don't want the __all__ list in this package, so we must mention each module explicitly.


I2C Devices using SysFs
-----------------------

EEPROM
~~~~~~
.. automodule:: ekfsm.devices.eeprom

.. for some unknown reason, EKF_CCU_EEPROM will not be included with automodule
.. autoclass:: ekfsm.devices.eeprom.EKF_CCU_EEPROM

GPIO
~~~~
.. automodule:: ekfsm.devices.gpio

EKF SUR LED
~~~~~~~~~~~
.. automodule:: ekfsm.devices.ekf_sur_led

PMBUS
~~~~~
.. automodule:: ekfsm.devices.pmbus

IIO Thermal and Humidity Sensor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: ekfsm.devices.iio_thermal_humidity

I2C MUX
~~~~~~~
.. automodule:: ekfsm.devices.mux

I2C Devices using SMBus directly
--------------------------------

EKF CCU Microcontroller
~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: ekfsm.devices.ekf_ccu_uc


Devices using SysFs
-------------------

HWMON
~~~~~
.. automodule:: ekfsm.devices.hwmon

SMBIOS
~~~~~~
.. automodule:: ekfsm.devices.smbios

Base Classes and Utilities
--------------------------

.. automodule:: ekfsm.devices.generic
.. automodule:: ekfsm.devices.utils
.. automodule:: ekfsm.devices.iio

ekfsm.core package
=====================

.. We don't want the __all__ list in this package, so we must mention each module explicitly.
.. automodule:: ekfsm.core.components
.. automodule:: ekfsm.core.probe
.. automodule:: ekfsm.core.sysfs
.. automodule:: ekfsm.core.utils
