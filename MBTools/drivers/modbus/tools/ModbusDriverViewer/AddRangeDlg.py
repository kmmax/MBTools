
# -*- coding: utf-8 -*-
from MBTools.drivers.modbus.tools.ModbusDriverViewer import ui_AddRangeDlg
from MBTools.drivers.modbus.ModbusDriver import *
import sys


class AddRangeDlg(QtWidgets.QDialog):
    """ Auxiliary class for displaying data exchange in modbus driver """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = ui_AddRangeDlg.Ui_AddRangeDlg()
        self.ui.setupUi(self)

    def getParameters(self):
        return self.ui.leName.text(), self.ui.leFirstAddress.text(), self.ui.leQualtity.text()


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    dlg = AddRangeDlg()
    if dlg.exec_():
        print ("OK")
        print("IP: {}".format(dlg.getParameters()))
    else:
        print ("Cancel")

    return app.exec()


if __name__ == "__main__":
    exit(main(sys.argv))
