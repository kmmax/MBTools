# -*- coding: utf-8 -*-
import sys
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication

from MBTools.utilites.Messages import ValueViewer
from MBTools.pluton.Fans import Fan


from MBTools.oiserver.OIServer import IOServer
import MBTools.oiserver.tools.OIServerViewer.OIServerViewer as oiv
import MBTools.drivers.modbus.tools.ModbusDriverViewer.ModbusDriverViewer as drv


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    cur_path = os.path.dirname(__file__)
    new_path = os.path.relpath("../config/qss.css", cur_path)
    print(new_path)

    io = IOServer()

    oiviewer = oiv.OIServerViewer()
    oiviewer.setOiServer(io)

    # mbdrv = io.driver()
    # viewer = drv.ModbusDriverViewer()
    # viewer.addDriver(mbdrv)

    # value_viewer = ValueViewer()
    # value_viewer.setTagName("M1T1PL02VN00020.Ki")
    # value_viewer.setOiServer(io)
    # value_viewer.show()

    # viewer1 = Fan()
    # viewer1.setTagName("M1T1PL02AL00020.ST1")
    # viewer1.setOiServer(io)
    # viewer1.show()

    # value_viewer = Fan()
    # value_viewer.setTagName("M1T1PL02AL00020.PV")
    # value_viewer.setOiServer(io)
    # value_viewer.show()

    # viewer.move(100, 0)
    # viewer.show()
    oiviewer.show()

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))

# input = 0x3333
# output = [int(x) for x in '{:08b}'.format(input)]
# print(output)
