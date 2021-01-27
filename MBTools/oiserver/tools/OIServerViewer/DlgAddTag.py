# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog, QApplication
import sys

from MBTools.oiserver.tools.OIServerViewer.ui_DlgAddTag import Ui_Dialog
from MBTools.oiserver.constants import TagType, TagTypeFromStr, StrFromTagType

class DlgAddTag(QDialog):
    """ Auxiliary class for displaying data exchange in modbus driver """

    def __init__(self, devices: [], parent=None):
        super().__init__(parent)
        self.__ui = Ui_Dialog()
        self.__ui.setupUi(self)

        self.__status = None
        # self.__types = types
        self.__types = StrFromTagType.values()
        self.__devices = devices

        self.__ui.cbType.addItems(self.__types)
        self.__ui.cbDev.addItems(self.__devices)

        self.__ui.buttonBox.accepted.connect(self.__accepted)
        self.status = {}

    def __accepted(self):
        self.status["name"] = self.__ui.leName.text()
        self.status["type"] = self.__ui.cbType.currentText()
        self.status["dev"] = self.__ui.cbDev.currentText()
        self.status["addr"] = self.__ui.leAddr.text()
        self.status["comment"] = self.__ui.txtComment.toPlainText()
        self.accept()


def main(argv):
    app = QApplication(sys.argv)

    # w = DlgAddTag()
    # w.show()

    return app.exec()


if __name__ == "__main__":
    exit(main(sys.argv))
