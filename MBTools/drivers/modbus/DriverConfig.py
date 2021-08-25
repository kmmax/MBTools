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
        self._driver: ModbusDriver  = None

    def set_driver(self, driver: ModbusDriver):
        self._driver = driver

    def driver(self):
        return self._driver

    def is_valid(self):
        return self._driver is None

    def add_addresses(self, dev: Device, addresses: list):
        assert self._driver is not None

        # print("\tadd_addresses: {0}; {1}".format(dev.name(), addresses))
        devs = self._driver.devices()
        old_addresses = dev.all_addresses()
        new_addresses = [addr for addr in addresses if addr not in old_addresses]
        result_addresses = []
        # print("\told_addresses: {0}; {1}".format(dev.name(), old_addresses))
        # print("\tnew_addresses: {0}; {1}".format(dev.name(), new_addresses))
        if dev in devs:
            # print("\tAdd: dev {0} is exists".format(dev.name()))
            if not new_addresses:
                print("\tNothing to add")
                return None
            else:
                # print("\tNew ranges will be crerated to {}".format(dev.name()))
                dev.delAllRanges()
                result_addresses = old_addresses + new_addresses
                ranges = ModbusCalculator.split_numbers(result_addresses, 100)
                for i, rng in enumerate(ranges):
                    dev.addRange(rng[0], rng[1] - rng[0], "range{}".format(i))
                print("\tNew ranges has been created for {}".format(dev.name()))
                return None
        else:
            # print("\tAdd: dev {0} isn't exists".format(dev.name()))
            result_addresses = old_addresses + new_addresses
            ranges = ModbusCalculator.split_numbers(result_addresses, 100)
            # print("\tresult_addresses: {}".format(result_addresses))
            # print("\tranges: {}".format(ranges))
            for i, rng in enumerate(ranges):
                dev.addRange(rng[0], rng[1] - rng[0], "range{}".format(i))
            print("\tDevice's been  added: {}".format(dev.name()))
            self._driver.addDevice(dev)
            return None

        print("End of method")

    def del_addresses(self, dev: Device, adresses: list):
        assert dev is not None

        devs = self._driver.devices()
        if dev in devs:
            print("Del: dev {} is exists".format(dev.name()))
        else:
            print("Del: dev {} will be created".format(dev.name()))

    def del_channel(self, dev: Device, range: Range ):
        assert self._driver is not None
        pass

    def clear(self):
        """ Clears all configuration """
        pass

    def __str__(self):
        msg = ""
        return msg


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    # dev1
    dev1 = DeviceCreator.create("10.18.32.78", 10502, "dev1")
    dev1.addRange(0, 5, "data1")
    # dev1.addRange(121, 7, "data2")

    # dev2
    dev2 = DeviceCreator.create("10.18.32.78", 10502, "dev2")
    # dev2.addRange(0, 10, "data3")

    # dev3
    dev3 = DeviceCreator.create("127.0.0.1", 10502, "dev3")
    # dev3.addRange(20, 5, "data4")

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
