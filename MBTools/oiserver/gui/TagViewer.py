# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, uic
from MBTools.oiserver.gui import ui_TagViewer
from MBTools.oiserver.gui.SettingsDlg import SettingsDlg
from MBTools.oiserver.Tag import TagList, Tag, TagType
from MBTools.oiserver.OIServer import IOServer

import time
import sys


class TagViewer(QtWidgets.QMainWindow):
    """ Auxiliary software for displaying tags in real-time """

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = ui_TagViewer.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tableWidget.setColumnWidth(0, 70)
        for row in range(self.ui.tableWidget.rowCount()):
            self.ui.tableWidget.setRowHeight(row, 5)
        self._srv: IOServer = None
        self._currentDevice = None

        self.ui.listWidget.currentTextChanged.connect(self.selectDevice)
        self.ui.actionCommunication.triggered.connect(self.onSettingsDlg)

    def onSettingsDlg(self):
        dlg = SettingsDlg(self)
        dlg.exec()

    def setUi(self):
        self.ui.tableWidget.setStyleSheet(
            """
                    QTableWidget {
                        background-color: #000;
                        color: yellow;
                        border: 3px solid green;
                        gridline-color: gray;
                    }
            """)
        self.ui.listWidget.setStyleSheet(
            """
                    QListWidget {
                        background-color: #000;
                        color: yellow;
                        border: 3px solid green;
                    }
            """)

    def setServer(self, srv: IOServer):
        """ Sets exchange data block  """
        self._srv = srv
        if self._srv.devices():
            self._currentDevice = self._srv.devices()[0]
        self._srv.dataChanged.connect(self.onDataUpdate)
        self.ui.listWidget.clear()

        for device in self._srv.devices():
            self.ui.listWidget.addItem(device.name())

        self.onDataUpdate()

    @QtCore.pyqtSlot(str)
    def selectDevice(self, name):
        device = self._srv.deviceByName(name)
        if device:
            self._currentDevice = device
            self.ui.tableWidget.clear()
        self.onDataUpdate()


    @QtCore.pyqtSlot()
    def onDataUpdate(self):
        """
        Updates TableWidget by OIServer tags data
        |---------------------------------------------------|
        | Name | Address | Value | Time | Quality | Comment |
        |---------------------------------------------------|
        :return: None
        """
        if self._currentDevice:
            device = self._currentDevice

            # Name
            self.ui.lbName.setText(device.name())

            # Table
            for i in range(len(device)):
                tag = device[i]
                name = tag.name
                addr = tag.address
                value = tag.value
                quality = tag.quality
                timestamp = "???"
                comment = tag.comment

                # Name
                item = QtWidgets.QTableWidgetItem(name)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                self.ui.tableWidget.setItem(i, 0, item)

                # Address
                item = QtWidgets.QTableWidgetItem(str(addr))
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                self.ui.tableWidget.setItem(i, 1, item)

                # Value
                item = QtWidgets.QTableWidgetItem(str(value))
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                # item.setForeground(QtCore.Qt.green)
                self.ui.tableWidget.setItem(i, 2, item)


                # self.ui.tableWidget.setItem(addr, 2, QtWidgets.QTableWidgetItem(time.strftime("%H:%M:%S", timestamp)))

                # Quality
                item = QtWidgets.QTableWidgetItem(str(quality))
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                self.ui.tableWidget.setItem(i, 4, item)

                # Comment
                item = QtWidgets.QTableWidgetItem(comment)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
                self.ui.tableWidget.setItem(i, 5, item)


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    tag1 = Tag("CM", TagType.UINT, "Command")
    tag2 = Tag("VL", TagType.REAL, "Current value")
    tag3 = Tag("ST1", TagType.UINT, "State")
    tag4 = Tag("AM", TagType.WORD, "Errors code")
    tag5 = Tag("PR1", TagType.WORD, "Protection")
    dev1 = TagList("G20K001SD001", 0, "Valve1")
    # dev1.append(tag1, 0)
    # dev1.append(tag2, 1)
    # dev1.append(tag3, 3)
    # dev1.append(tag4, 5)
    # dev1.append(tag5, 8)
    dev1.append(tag1)
    dev1.append(tag2)
    dev1.append(tag3)
    dev1.append(tag4)
    dev1.append(tag5)

    dev2 = TagList("G20K001PT001", 10, "Measurement1")
    tag2_1 = Tag("CM", TagType.UINT, "Command")
    tag2_2 = Tag("VL", TagType.REAL, "Current value")
    dev2.append(tag2_1)
    dev2.append(tag2_2)

    srv = IOServer()
    srv.addTagList(dev1)
    srv.addTagList(dev2)
    print(dev1)

    viewer = TagViewer()
    viewer.show()
    viewer.setServer(srv)
    # viewer.selectDevice("G20K001PT001")
    # viewer.selectDevice("G20K001SD001")

    # drv1.dataUpdated.connect(viewer.onDataUpdate)

    return app.exec()


if __name__ == "__main__":
    exit(main(sys.argv))
