# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QStyledItemDelegate, QTableWidget, QDialog
from PyQt5.QtGui import QColor, QPalette, QImage, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

# from MBTools.utilites.Messages import DummyMessage
from MBTools.oiserver.OIServer import IOServer
from MBTools.oiserver.Tag import Tag, TagType
from MBTools.drivers.modbus.ModbusDriver import QualityEnum
import MBTools.drivers.modbus.tools.ModbusDriverViewer.ModbusDriverViewer as drv

from MBTools.oiserver.tools.OIServerViewer.ui_OIServerViewer import Ui_OIServerViewer
from MBTools.oiserver.Tag import Tag
from MBTools.oiserver.constants import TagTypeFromStr, StrFromTagType

from MBTools.oiserver.tools.OIServerViewer.DlgAddTag import DlgAddTag
from MBTools.oiserver.OIServerConfigure import JsonConfigure
from MBTools.pluton.Fans import Fan
from MBTools.utilites.Messages import DummyMessage

lock = QtCore.QMutex()


class EditDelegate(QtWidgets.QItemDelegate):
    editingStarted = pyqtSignal()
    editingFinished = pyqtSignal()

    def __init__(self, parent=None):
        super(EditDelegate, self).__init__(parent)
        self.__editor = None
        self.__combo = None
        self.__devices_names = []
        self.__types_names = []

    def set_devices_names(self, devices_names: list):
        self.__devices_names = devices_names

    def set_types_names(self, types_names: list):
        self.__types_names = types_names

    def createEditor(self, parent: QtWidgets.QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        column = index.column()
        if 1 == column:         # value
            self.__editor = QtWidgets.QLineEdit(parent)
            self.editingStarted.emit()
            self.closeEditor.connect(self.onClosedEditor)
            return self.__editor
        elif 3 == column:       # devices
            print(self.__devices_names)
            self.__combo = QtWidgets.QComboBox(parent)
            self.__combo.addItems(self.__devices_names)
            return self.__combo
        elif 5 == column:       # type
            self.__combo = QtWidgets.QComboBox(parent)
            self.__combo.addItems(self.__types_names)
            return self.__combo

    @QtCore.pyqtSlot()
    def onClosedEditor(self):
        print("Editing is finished")

    def paint(self, painter, option, index):
        QUALITY_COLUMN = 2 # Quality in 4 column

        model = index.model()
        row = index.row()
        cond_index = model.index(row, QUALITY_COLUMN)   # index of cell "Quality"

        if cond_index.data() == 'GOOD':
            option.palette.setColor(QPalette.Text, QColor("black"))
        else:
            option.palette.setColor(QPalette.Text, QColor("red"))
        QtWidgets.QItemDelegate.paint(self, painter, option, index)


class OIServerViewer(QtWidgets.QMainWindow):
    STYLESHEET_FILE = "config/qss.css"     # path to stylesheet file

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_OIServerViewer()
        self._ui.setupUi(self)
        self._oi: IOServer = None
        self.__edit_delegate = EditDelegate()

        # GUI
        self._ui.tableWidget.setItemDelegate(self.__edit_delegate)

        self._ui.tableWidget.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)
        # self._ui.tableWidget.setColumnHidden(0, True)

        # cur_path = os.path.dirname(__file__)
        # qss = os.path.relpath("../../../config/{}".format(OIServerViewer.STYLESHEET_FILE, cur_path))
        # print("OIServerViewer: {}".format(qss))
        d = os.getcwd()

        print("d= {}".format(d))
        qss = os.path.join(d, OIServerViewer.STYLESHEET_FILE)
        print("OIServer: {}".format(qss))
        try:
            with open(qss, 'r') as css:
                self.setStyleSheet(css.read())
        except IOError:
            print("Style sheet file {0} not found".format(qss))

        self._ui.tableWidget.setStyleSheet("""
            QTableWidget::item {padding-left: 5px; border: 0px}
        """)
        # self._ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self._ui.actionDriver.triggered.connect(self.onDriverViewerShow)
        self._ui.actionAdd_Tag.triggered.connect(self.onDlgAddTagShow)
        self._ui.actionShow_only_GOOD_quality.triggered.connect(self.onFilterQualityTriggered)

        # self._dlg = DlgAddTag(self)
        # self._dlg.show()

        class Flags:
            pass
        self.__flags = Flags()
        self.__flags.quality_filter = False

        self.setGui()

        self._ui.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._ui.tableWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.__menu = QtWidgets.QMenu(self)
        action1 = self.__menu.addAction('Show as widget')
        self.__menu.addSeparator()
        action2 = self.__menu.addAction('Copy')
        action4 = self.__menu.addAction('Edit')
        self.__menu.addSeparator()
        action3 = self.__menu.addAction('Delete')
        action1.triggered.connect(self.show_item)
        action2.triggered.connect(lambda: QtWidgets.QMessageBox.information(self, 'Info', 'Copy Dummy'))
        action3.triggered.connect(lambda: QtWidgets.QMessageBox.information(self, 'Info', 'Delete Dummy'))
        action4.triggered.connect(lambda: QtWidgets.QMessageBox.information(self, 'Info', "Edit Dummy"))

    def show_item(self):
        """Shows value in separate window"""
        # i = self._ui.tableWidget.selectionModel().selectedRows().count()
        i = self._ui.tableWidget.currentRow()
        name = self._ui.tableWidget.item(i, 0).text()
        fan = Fan()
        fan.setTagName(name)
        fan.setOiServer(self._oi)
        fan.resize(200, 50)
        fan.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        fan.show()

    def setGui(self):
        # Выделять только ряд
        self._ui.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        # Сторбцы сортируются щелчком мыши по их заголовку
        # self._ui.tableWidget.setSortingEnabled(True)
        # self._ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        # Menu
        self._ui.actionOpen.triggered.connect(self.open_file)
        self._ui.actionHelp.triggered.connect(lambda:  DummyMessage().exec())
        self._ui.actionAbout.triggered.connect(lambda: DummyMessage().exec())
        self._ui.actionAppereance.triggered.connect(lambda: DummyMessage().exec())
        self._ui.actionNew.triggered.connect(lambda: DummyMessage().exec())
        self._ui.actionSave_As.triggered.connect(lambda: DummyMessage().exec())
        self._ui.actionClose.triggered.connect(lambda: DummyMessage().exec())
        self._ui.actionExit.triggered.connect(lambda: DummyMessage().exec())

        # Table
        header = self._ui.tableWidget.verticalHeader()
        header.setDefaultSectionSize(10)
        self._ui.tableWidget.setVerticalHeader(header)

    # ----- Menu actions -----
    def open_file(self):
        filename, ok = QtWidgets.QFileDialog.getOpenFileName(self, "Choose files", ".", "*.json")
        conf = JsonConfigure()
        conf.read_config(filename)
        self._oi.set_config(conf)
        self.updateGui()

    def show_context_menu(self, point):
        self.__menu.exec(self.mapToGlobal(point))

    def onFilterQualityTriggered(self):
        self.__flags.quality_filter = not self.__flags.quality_filter
        self.updateGui()

    def setOiServer(self, oi: IOServer):
        if oi is None:
            return None
        self._oi = oi
        self._oi.dataChanged.connect(self.onDataChanged)
        self._oi.configChanged.connect(self.onConfigChanged)
        self.onConfigChanged()

    @QtCore.pyqtSlot()
    def onDataChanged(self):
        self.updateGui()

    @QtCore.pyqtSlot()
    def onConfigChanged(self):
        pass

    @QtCore.pyqtSlot()
    def onDriverViewerShow(self):
        """ Starts Modbus Driver Viewer """
        mbdrv = self._oi.driver()
        viewer = drv.ModbusDriverViewer()
        viewer.addDriver(mbdrv)
        viewer.show()

    @QtCore.pyqtSlot()
    def onDlgAddTagShow(self):
        """ Show dialog for adding tag """

        # Devices names for choosing in dialog window
        devices = [dev.name() for dev in self._oi.devices()]

        # name = ""
        dlg = DlgAddTag(devices, self)
        res = dlg.exec()
        if QDialog.Accepted == res:
            status = dlg.status
            # for k, v in status.items():
            #     list_item = "{0}: {1}".format(k, v)
            #     print(list_item)
            name_ = status["name"]
            dev_name  = status["dev"]
            addr_: int = int(status["addr"])
            type_ = TagTypeFromStr[status["type"]]
            comment_ = status["comment"]
            dev = None
            for device in self._oi.devices():
                if device.name() == dev_name:
                    dev = device
                    break

            tags = []
            # devices = self._oi.devices()
            # dev = devices[0]
            new_tag = Tag(dev,
                          name_,
                          type_,
                          address=addr_,
                          comment=comment_)
            tags.append(new_tag)
            self._oi.add_tags(tags)
            self.updateGui()

    def updateGui(self):
        # print("updateGui")
        if self._oi:
            # self._ui.tableWidget.clear()

            # Update table delegate
            types_names = StrFromTagType.values()
            devices_names = [dev.name() for dev in self._oi.devices()]
            self.__edit_delegate.set_devices_names(devices_names)
            self.__edit_delegate.set_types_names(types_names)

            tags = self._oi.tags()
            if self.__flags.quality_filter:
                tags = [tag for tag in tags if QualityEnum.GOOD == tag.quality]

            # print(tags)
            """
            |-------------------------------------------------------------------|
            | Name | Value | Quality | Device | Address | Type | Time | Comment |
            |-------------------------------------------------------------------|
            """
            self._ui.tableWidget.setRowCount(len(tags))
            for i, tag in enumerate(tags):

                # Name
                item = QtWidgets.QTableWidgetItem(tag.name)
                # item.setTextAlignment(QtCore.Qt.AlignCenter)
                self._ui.tableWidget.setItem(i, 0, item)
                # Value
                item = QtWidgets.QTableWidgetItem(str(tag.value))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self._ui.tableWidget.setItem(i, 1, item)
                # Quality
                item = QtWidgets.QTableWidgetItem(str(tag.quality).replace("QualityEnum.", ''))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self._ui.tableWidget.setItem(i, 2, item)
                # Device
                item = QtWidgets.QTableWidgetItem(tag.device.objectName())
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self._ui.tableWidget.setItem(i, 3, item)
                # Address
                addr = str(tag.address)
                if TagType.BOOL == tag.type:
                    addr += ".{0}".format(tag.bit_number)
                # item = QtWidgets.QTableWidgetItem(str(tag.address))
                item = QtWidgets.QTableWidgetItem(addr)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self._ui.tableWidget.setItem(i, 4, item)
                # Type
                item = QtWidgets.QTableWidgetItem(str(tag.type).replace("TagType.", ''))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self._ui.tableWidget.setItem(i, 5, item)
                # Time
                item = QtWidgets.QTableWidgetItem(self.timeFormat(tag.time))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self._ui.tableWidget.setItem(i, 6, QtWidgets.QTableWidgetItem(item))
                # Comment
                self._ui.tableWidget.setItem(i, 7, QtWidgets.QTableWidgetItem(tag.comment))
        # print("end of update GUI")

    def timeFormat(self, time):
        str_time = ''
        if time:
            str_time = "{:02}:{:02}:{:02}".format(time.tm_hour, time.tm_min, time.tm_sec)

        return str_time


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    tag1 = Tag(name="CM", type_=TagType.UINT, comment="Command", address=799)
    tag2 = Tag(name="ST1", type_=TagType.REAL, comment="State", address=800)
    tag3 = Tag(name="RG", type_=TagType.UINT, comment="Mode", address=801)
    tag4 = Tag(name="AM1", type_=TagType.UINT, comment="Alarms 1-st", address=802)
    tag5 = Tag(name="AM2", type_=TagType.UINT, comment="Alarms 2-th", address=803)
    tag6 = Tag(name="WM", type_=TagType.UINT, comment="Warnings", address=804)
    tag7 = Tag(name="CS", type_=TagType.UINT, comment="Accsess", address=805)
    tags = list([tag1, tag2, tag3, tag4, tag5, tag6, tag7])
    io = IOServer()
    io.add_tags(tags)

    oiviewer = OIServerViewer()
    oiviewer.show()
    oiviewer.setOiServer(io)

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))
