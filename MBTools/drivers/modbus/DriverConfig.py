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
from abc import abstractmethod

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject

from MBTools.drivers.modbus.ModbusDriver import ModbusDriver, Device, Range, DeviceCreator, DriverCreator, ModbusCalculator, AbsConfControl


def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider


class AbcDriverConf(object):
    """
    Class which configures driver
    """
    def __init__(self):
        self.__MAX_NUMBERS_IN_RANGE = 100   # Maximum address range from minimum to maximum

        self._driver: AbsConfControl = None   # Reference to ModbusDriver

    @abstractmethod
    def add_addresses(self, dev: Device, addresses: list):
        """ Adding new addresses to device for polling """
        pass

    @abstractmethod
    def del_addresses(self, dev: Device, addresses: list):
        """ Deletes addresses from device """
        pass

    @abstractmethod
    def clear(self):
        self._driver: ModbusDriver = None   # Reference to ModbusDriver

    def set_driver(self, driver: ModbusDriver):
        """Sets current modbus driver"""
        self._driver = driver

    def driver(self):
        """Returns current modbus driver"""
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


class ModbusDriverConf(QObject, AbcDriverConf):
    def __init__(self): 
        super().__init__()

    @overrides(AbcDriverConf)
    def add_addresses(self, dev: Device, addresses: list):
        """
        Adding new addresses to device for polling

        Work algorithm:
        1. Making a list of added addresses
        2. If all "new addresses" are already present, do nothing
        3. If there are no "new addresses" in the existing device, we redistribute the ranges for this device
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

        assert False, "End of ModbusDriverConf::add_addreses"

    @overrides(AbcDriverConf)
    def del_addresses(self, dev: Device, addresses: list):
        """ Deletes addresses from device

        Work algorithm:
        1. If device not present, do nothing
        2. Create a new list of all addresses
        3. Updating ranges of addresses
        """
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

    @overrides(AbcDriverConf)
    def clear(self):
        """ Clears all configuration
        @todo Not implemented !!!
        """
        self._driver.clear()


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    dev1 = DeviceCreator.create("127.0.0.1", 10502, "dev1")
    dev2 = DeviceCreator.create("127.0.0.1", 20502, "dev2")
    dev3 = DeviceCreator.create("127.0.0.1", 30502, "dev3")

    drv1 = DriverCreator.create("modbus")

    cfg: AbcDriverConf = ModbusDriverConf()
    cfg.set_driver(drv1)

    time.sleep(3)
    print("----------------")
    cfg.add_addresses(dev1, [21, 22, 123, 128])
    time.sleep(3)
    cfg.add_addresses(dev3, [21, 22, 100, 101])
    time.sleep(3)
    cfg.add_addresses(dev2, [23, 28])
    time.sleep(3)
    cfg.add_addresses(dev3, [21, 22, 55, 58, 92, 100, 101, 124, 204, 1288, 1293])

    return app.exec()


if __name__ == "__main__":
    exit(main(sys.argv))
