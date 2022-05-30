# -*- coding: utf-8 -*-
from MBTools.drivers.modbus.tools.ModbusDriverViewer.ModbusDriverViewer import *
import sys


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    devices = []

    # device1
    device1 = DeviceCreator.create("10.18.32.78", 10502, "dev1")
    device1.addRange(0, 3, "data1")
    device1.addRange(20, 7, "data2")
    device1.addRange(30, 5, "data3")
    devices.append(device1)

    # device2
    device2 = DeviceCreator.create("10.18.32.78", 20502, "dev2")
    device2.addRange(0, 10, "data1")
    devices.append(device2)

    drv1 = DriverCreator.create("modbus", devices)

    viewer = ModbusDriverViewer()
    viewer.add_driver(drv1)
    viewer.show()

    return app.exec()


if __name__ == "__main__":
    exit(main(sys.argv))
