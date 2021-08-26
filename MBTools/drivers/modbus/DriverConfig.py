# -----------------------------------------------------------
# This module contains tools for server configuration
#
# (C) 2021 Maxim Kozyakov, Voronezh, Russia
# Released under GNU Public License (MIT)
# email kmmax@yandex.ru
# -----------------------------------------------------------

"""
Модуль Config.py
Назначение:
Производит настройку драйвера

@todo
    - method clear isn't work
"""

import sys
import time
from abc import ABC, abstractmethod

from PyQt5 import QtWidgets

from MBTools.drivers.modbus.ModbusDriver import ModbusDriver, Device, Range, DeviceCreator, DriverCreator, ModbusCalculator


class AbcDriverConf(ABC):
    """
    Class which configures driver
    """
    def __init__(self):
        self.__MAX_NUMBERS_IN_RANGE = 100   # Maximum address range from minimum to maximum

        self._driver: ModbusDriver = None   # Reference to ModbusDriver

    @abstractmethod
    def add_addresses(self, dev: Device, addresses: list):
        pass

    @abstractmethod
    def del_addresses(self, dev: Device, addresses: list):
        pass

    def set_driver(self, driver: ModbusDriver):
        self._driver = driver

    def driver(self):
        return self._driver

    def is_valid(self):
        """Checking that the driver is installed"""
        return self._driver is None

    def __str__(self):
        msg = ""
        return msg

    def _update_ranges(self, dev: Device, addresses: list):
        """Перераспределяем адреса по новым диапазоном устройства
        @param[in-out] dev - устройство для которого будет перераспределены диапазоны
        @param[in] addresses - полный перечень адресов устройства
        """
        ranges = ModbusCalculator.split_numbers(addresses, self.__MAX_NUMBERS_IN_RANGE)
        dev.delAllRanges()
        for i, rng in enumerate(ranges):
            dev.addRange(rng[0], rng[1] - rng[0] + 1, "range{}".format(i))


class ModbusDriverConf(AbcDriverConf):
    def __init__(self): 
        super().__init__()
    
    def add_addresses(self, dev: Device, addresses: list):
        """
        Adding new addresses to device for polling

        Work algorithm:
        1. Making a list of added addresses
        2. If all "new addresses" are already present, do nothing
        3. If there are no "new addresses" in the existing device, we redistribute the range for this device
        4. If the device is not presented for the "new addresses", add the device to the driver
        """
        assert self._driver is not None

        # print("\tadd_addresses: {0}; {1}".format(dev.name(), addresses))
        devs = self._driver.devices()
        old_addresses = dev.all_addresses()
        add_addresses = [addr for addr in addresses if addr not in old_addresses]
        # print("\told_addresses: {0}; {1}".format(dev.name(), old_addresses))
        # print("\tnew_addresses: {0}; {1}".format(dev.name(), new_addresses))
        if dev in devs:
            # print("\tAdd: dev {0} is exists".format(dev.name()))
            if not add_addresses:
                print("\tNothing to add")
                return None
            else:
                # print("\tNew ranges will be crerated to {}".format(dev.name()))
                new_addresses = old_addresses + add_addresses
                self._update_ranges(dev, new_addresses)
                print("\tNew ranges has been created for {}".format(dev.name()))
                return None
        else:
            # print("\tAdd: dev {0} isn't exists".format(dev.name()))
            new_addresses = old_addresses + add_addresses
            self._update_ranges(dev, new_addresses)
            self._driver.addDevice(dev)
            print("\tDevice's been  added: {}".format(dev.name()))
            return None

        print("End of method")

    def del_addresses(self, dev: Device, addresses: list):
        assert dev is not None

        devs = self._driver.devices()
        # if the device does not exist, do nothing
        if dev not in devs:
            print("Del: dev {} isn't exists".format(dev.name()))
            return None

        # 1. Calculate a new up-to-date list of addresses
        # 2. Relocate addresses to new ranges
        old_addresses = dev.all_addresses()
        del_addresses = [addr for addr in addresses if addr in old_addresses]
        new_addresses = [addr for addr in old_addresses if addr not in del_addresses]
        # print("\taddresses: {0}; {1}".format(dev.name(), addresses))
        # print("\told_addresses: {0}; {1}".format(dev.name(), old_addresses))
        # print("\tdel_addresses: {0}; {1}".format(dev.name(), del_addresses))
        # print("\tresult_addresses: {0}; {1}".format(dev.name(), result_addresses))
        self._update_ranges(dev, new_addresses)
        return None

    def clear(self):
        """ Clears all configuration
        @todo Not implemented !!!
        """
        self._driver.clear()


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    # dev1
    dev1 = DeviceCreator.create("10.18.32.78", 10502, "dev1")
    dev1.addRange(0, 5, "data1")

    # dev2
    dev2 = DeviceCreator.create("10.18.32.78", 10502, "dev2")

    # dev3
    dev3 = DeviceCreator.create("127.0.0.1", 10502, "dev3")

    devs = [dev1]
    drv1 = DriverCreator.create("modbus", devs)

    cfg = AbcDriverConf()
    cfg.set_driver(drv1)

    time.sleep(3)
    print("----------------")
    cfg.add_addresses(dev1, [123, 128])
    cfg.add_addresses(dev3, [21, 22, 100, 101])
    cfg.add_addresses(dev2, [23, 28])
    cfg.add_addresses(dev3, [21, 22, 55, 58, 92, 100, 101, 124, 204, 1288, 1293])

    return app.exec()


if __name__ == "__main__":
    exit(main(sys.argv))
