# -*- coding: utf-8 -*-
import sys
import time

from PyQt5 import QtWidgets

from MBTools.drivers.modbus.ModbusDriver import DeviceCreator, DriverCreator
from MBTools.drivers.modbus.DriverConfig import AbcDriverConf, ModbusDriverConf
from MBTools.drivers.modbus.tools.ModbusDriverViewer.ModbusDriverViewer import ModbusDriverViewer


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    drv1 = DriverCreator.create("modbus")
    cfg: AbcDriverConf = ModbusDriverConf()
    cfg.set_driver(drv1)

    dev1 = DeviceCreator.create("127.0.0.1", 10502, "dev1")
    dev2 = DeviceCreator.create("127.0.0.1", 20502, "dev2")
    dev3 = DeviceCreator.create("127.0.0.1", 30502, "dev3")

    # ModbusDriverViewer не отображает новые Ranges, если cfg.add_address после viewer.addDriver(drv1)
    cfg.add_addresses(dev1, [3, 8, 110, 112, 121, 199, 200, 201, 325, 144, 235])
    cfg.add_addresses(dev2, [4, 3])
    cfg.add_addresses(dev3, [21, 22, 100, 101, 5, 8, 151, 188, 189])

    time.sleep(3)
    cfg.del_addresses(dev1, [4, 3])

    viewer = ModbusDriverViewer()
    viewer.add_driver(drv1)
    viewer.show()

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))