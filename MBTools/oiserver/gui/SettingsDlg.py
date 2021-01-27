# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, uic
from MBTools.oiserver.gui import ui_Settings
from MBTools.oiserver.Tag import TagList, Tag, TagType
from MBTools.oiserver.OIServer import IOServer

import time
import sys


class SettingsDlg(QtWidgets.QDialog):
    """ Settings dialog """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = ui_Settings.Ui_Dialog()
        self.ui.setupUi(self)


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    dlg = SettingsDlg()
    dlg.show()

    return app.exec()


if __name__ == "__main__":
    exit(main(sys.argv))
