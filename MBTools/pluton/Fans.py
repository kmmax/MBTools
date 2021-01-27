# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
import sys

from MBTools.oiserver.OIServer import IOServer


class DummyMessage(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(300, 100)
        self.setText("This is dummy")
        self.setStyleSheet("QLabel {"
                           "background: black; "
                           "color: yellow; font-size: 16px; qproperty-alignment: AlignCenter"
                           "}")


class Fan(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__tag_name = None
        self.__oi = None
        self.resize(300, 100)
        self.setText("No data")
        self.setStyleSheet("QLabel {"
                           "background: black; "
                           "color: yellow; font-size: 20px; qproperty-alignment: AlignCenter"
                           "}")
        # Context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.__menu = QtWidgets.QMenu(self)

        action1 = self.__menu.addAction("On Top")
        action2 = self.__menu.addAction('Say: "Hello!"')
        action3 = self.__menu.addAction('Say: "Hello!"')
        action1.triggered.connect(lambda : QtWidgets.QMessageBox.information(self, "Info", "Hello"))
        action2.triggered.connect(lambda : QtWidgets.QMessageBox.information(self, "Info", "Hello"))
        action3.triggered.connect(lambda : QtWidgets.QMessageBox.information(self, "Info", "Hello"))

    def show_context_menu(self, point):
        self.__menu.exec(self.mapToGlobal(point))


    @QtCore.pyqtSlot(int)
    def onIndexChanged(self, num: int):
        self.setTagName(self.__combo.currentText())

    def setTagName(self, tag_name: str):
        self.__tag_name = tag_name
        self.setWindowTitle(self.__tag_name)

    def setOiServer(self, oi: IOServer):
        self.__oi = oi
        self.__oi.dataChanged.connect(self.onDataChanged)
        # self.__combo.clear()
        # if self.__oi:
        #     tags = self.__oi.tags()
        #     tag_names = [tag.name for tag in tags]
        #     for item in tag_names:
        #         self.__combo.addItem(item)

    @QtCore.pyqtSlot()
    def onDataChanged(self):
        if self.__oi:
            self.setText(self.__tag_name)
            tags = self.__oi.tags()
            for tag in tags:
                if tag.name == self.__tag_name:
                    self.setText(str(tag.value))


def main(argv):
    app = QtWidgets.QApplication(sys.argv)
    lb = DummyMessage()
    lb.show()

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))
