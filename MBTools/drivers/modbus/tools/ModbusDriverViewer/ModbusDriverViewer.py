# -*- coding: utf-8 -*-
from MBTools.drivers.modbus import ModbusDriver
from MBTools.drivers.modbus.tools.ModbusDriverViewer import ui_ModbusDriverViewer
from MBTools.drivers.modbus.tools.ModbusDriverViewer.ModbusModel import *
from MBTools.drivers.modbus.ModbusDriver import *
from MBTools.drivers.modbus.tools.ModbusDriverViewer.AddDriverDlg import AddDriverDlg
from MBTools.drivers.modbus.tools.ModbusDriverViewer.AddRangeDlg import AddRangeDlg
import time
import sys
import json


class ModbusDriverViewer(QtWidgets.QMainWindow):
    """ Auxiliary class for displaying data exchange in modbus driver """
    cmdSent = pyqtSignal(int, int)

    STYLESHEET_FILE = "MBTools/config/qss.css"     # path to stylesheet file

    def __init__(self, parent=None):
        super().__init__(parent)

        qss = ModbusDriverViewer.STYLESHEET_FILE
        try:
            with open(qss, 'r') as css:
                self.setStyleSheet(css.read())
        except IOError:
            print("Style sheet file {0} not found".format(qss))

        self.ui = ui_ModbusDriverViewer.Ui_MainWindow()
        self.ui.setupUi(self)
        self._commands = {}
        self.setGui()
        self.__datas = []
        self.__current_row_editing = None

        self._driver: ModbusDriver = None
        self._model = DriverModel()
        self.ui.treeView.setModel(self._model)
        self.ui.treeView.clicked.connect(self._onClicked)
        selectionModel = self.ui.treeView.selectionModel()
        selectionModel.setCurrentIndex(self.ui.treeView.rootIndex(), QItemSelectionModel.Select)
        self._currentDevice = None

        # self.ui.tableWidget.itemSelectionChanged.connect(self.on_selection)
        # self.ui.tableWidget.itemChanged.connect(self.on_selection)
        # self.ui.tableWidget.itemDoubleClicked.connect(self.on_selection)
        self.ui.tableWidget.cellDoubleClicked.connect(self.on_selection)
        self.ui.tableWidget.cellChanged.connect(self.on_deselection)

        # self.ui.tableView.setModel(self._model)

        # TreeViewer
        self.ui.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.menu = self.create_menu()
        self.ui.treeView.customContextMenuRequested.connect(self.open_menu)
        self.ui.treeView.expanded.connect(lambda: self.ui.treeView.resizeColumnToContents(0))

        # Menu
        self.ui.actionSave_As.triggered.connect(self.saveAsDialog)
        self.ui.actionOpen.triggered.connect(self.openDialog)
        # self.ui.actionExit.triggered.connect()

    def on_selection(self, row, column):
        print("Sell editing: {0}, {1}".format(row, column))
        if column == 1:
            self.__current_row_editing = row

    def on_deselection(self, row, column):
        if column == 1 and row == self.__current_row_editing:
            print("Sell deselection: {0}, {1}".format(row, column))
            self.__current_row_editing = None
            model = self.ui.tableWidget.model()
            # addr = 11
            value = int(model.data(self.ui.tableWidget.currentIndex()))
            addr = int(model.index(row, 0).data())
            print("----- addr: {0}; value: {1}".format(addr, value))
            self.cmdSent.emit(addr, value)

    # --- Actions ---
    def saveAsDialog(self):
         fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Configuration", "", "json (*.json)")
         out_str = self._createDriverConfig(self._driver)
         # if fileName:
         #     try:
         #         with open(fileName, 'w') as file:
         #             pass
         #             # file.write(out_str)
         #     except PermissionError:
         #        print("Error of opening file")

    def openDialog(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open file", "", "*.json (*.json)")
        self.__loadDriverConfig(fileName)

    def open_menu(self, position) -> QMenu:
        print("Open menu")
        action = self.menu.exec(self.ui.treeView.viewport().mapToGlobal(position))

    def create_menu(self) -> QMenu:
        menu = QMenu()
        menu.addAction("Add..", self.__onAdd)
        menu.addAction("Delete", self.__onRemove)
        menu.addAction("Property", self.__onProperty)
        # menu.addAction("Start", self._onStart)
        # menu.addAction("Stop", self._onStop)
        return menu

    def setGui(self):
        # self._commands = {
        #     "btOpen": [2, 1],
        #     "btClose": [2, 2],
        #     "btStop": [2, 4],
        # }
        # self.ui.btOpen.clicked.connect(self.onCmdReady)
        # self.ui.btClose.clicked.connect(self.onCmdReady)
        # self.ui.btStop.clicked.connect(self.onCmdReady)
        #
        # self.ui.lb1_1.setStyleSheet(
        #     """
        #     QLabel {
        #         background-color: #000;
        #         color: yellow;
        #         border: 3px solid green;
        #     }
        # """)

        self.ui.tableWidget.setColumnWidth(0, 70)
        for row in range(self.ui.tableWidget.rowCount()):
            self.ui.tableWidget.setRowHeight(row, 5)

    @QtCore.pyqtSlot()
    def onCmdReady(self):
        print("ModbusViewer: onCmdReade")
        addr = 22
        value = 777
        self.cmdSent.emit(addr, value)
        # sender = self.sender()
        # name = sender.objectName()
        # addr = 0
        # value = 0
        # if name in self._commands:
        #     addr = self._commands[name][0]
        #     value = self._commands[name][1]
        # else:
        #     print("No keys found")
        # print("clicked: {0}, {1}, {2}".format(name, addr, value))
        # self.cmdSent.emit(addr, value)

    @QtCore.pyqtSlot(str, Range)
    def onDataUpdate(self, drvName: str, data: Range):
        self._tableDataUpdate()
        # index = QModelIndex()
        # self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole])

    def addDriver(self, drv: ModbusDriver):
        self._driver = drv
        drv.dataChanged.connect(self.onDataUpdate)
        self.cmdSent.connect(drv.onCmdReady)
        self._model.addDriver(drv)
        # self._model.setupModelData()

    def setDriver(self, drv: ModbusDriver):
        self._driver = drv
        drv.dataChanged.connect(self.onDataUpdate)
        self.cmdSent.connect(drv.onCmdReady)
        self._model.removeAllDrivers()
        self._model.setDriver(drv)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def _onClicked(self, index: QtCore.QModelIndex):
        model: DriverModel = None
        model = self.ui.treeView.model()
        node = model.getNodeFromIndex(index)
        mb: AbsModbus = node.ref()
        if mb is None:
            print("Node is None")
            return None

        # Sets the required number of cells
        self.__datas = mb.ranges()
        num = 0
        for data in self.__datas:
            num += len(data)

        self._tableFormatUpdate(num)
        self._tableDataUpdate()

    def _tableFormatUpdate(self, num):
        self.ui.tableWidget.setRowCount(num)
        for row in range(num):
            self.ui.tableWidget.setRowHeight(row, 12)

    def _tableDataUpdate(self):
        row = 0
        for i, data in enumerate(self.__datas):
            startAddr = data.address()
            quality = data.quality()
            timestamp = data.time()
            registers = data.registers()
            # print("-> {0}: ".format(data))
            for j, value in enumerate(registers):
                if row != self.__current_row_editing:
                    addr = startAddr+j

                    item = QtWidgets.QTableWidgetItem(str(addr))
                    # item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    item.setTextAlignment(QtCore.Qt.AlignHCenter)
                    self.ui.tableWidget.setItem(row, 0, item)

                    item = QtWidgets.QTableWidgetItem(str(value))
                    # item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    item.setTextAlignment(QtCore.Qt.AlignHCenter)
                    self.ui.tableWidget.setItem(row, 1, item)

                    item = QtWidgets.QTableWidgetItem(time.strftime("%H:%M:%S", timestamp))
                    # item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    item.setTextAlignment(QtCore.Qt.AlignHCenter)
                    self.ui.tableWidget.setItem(row, 2, item)

                    item = QtWidgets.QTableWidgetItem(QualityEnumStr[quality])
                    item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    self.ui.tableWidget.setItem(row, 3, item)

                row = row + 1

    def _createDriverConfig(self, drv: ModbusDriver) -> str:
        data = {
            "driver": "modbus1",
            "prpperty": None,
            "devices": {

                "device1": {
                    "property": {
                        "ip": "10.18.32.78",
                        "port": 10502,
                    },
                    "ranges": {
                        "range1": {
                            "property": {
                                "adddress": 0,
                                "quantity": 10,
                                "comment": None,
                            },
                        },
                        "range2": {
                            "property": {
                                "adddress": 0,
                                "quantity": 10,
                                "comment": None,
                            },
                        },
                    },
                },

                "device2": {
                    "property": {
                        "ip": "10.18.32.78",
                        "port": 10502,
                    },
                    "ranges": {
                        "range1": {
                            "property": {
                                "adddress": 0,
                                "quantity": 10,
                                "comment": None,
                            },
                        },
                        "range2": {
                            "property": {
                                "adddress": 0,
                                "quantity": 10,
                                "comment": None,
                            },
                        },
                    },
                },

            },
        }

        with open("project.json", 'w') as file:
            json.dump(data, file, indent=4)
        out_str = ""

        return out_str

    def __loadDriverConfig(self, fileName: str):
        data = {}
        with open(fileName, 'r') as file:
            data = json.load(file)

        devices = []
        driverName = data["driver"]
        devicesConf = data["devices"]
        print(driverName)
        for deviceName, deviceElement in devicesConf.items():
            try:
                ip = deviceElement["property"]["ip"]
                port = deviceElement["property"]["port"]
                ranges = deviceElement["ranges"]
            except KeyError:
                print("Key error")
                pass
            print("{0}, {1}:{2}".format(deviceName, ip, port))

            # device1
            device1 = DeviceCreator.create(ip, port, deviceName)

            for rangeName, rangeIlement in ranges.items():
                try:
                    address = rangeIlement["property"]["adddress"]
                    quantity = rangeIlement["property"]["quantity"]
                    print("{0}, {1} ({2})".format(rangeName, address, quantity))
                    device1.addRange(address, quantity, rangeName)
                except KeyError:
                    print("Key Error")

            devices.append(device1)

        drv1 = DriverCreator.create(driverName, devices)
        self.setDriver(drv1)

    # --- Events of this class ---
    @QtCore.pyqtSlot()
    def __onAdd(self):
        print(self.__onAdd.__name__)
        index = self.ui.treeView.selectedIndexes()[0]
        node = self._model.getNodeFromIndex(index)
        modbusItem = node.ref()
        print("modbusItem = {0}".format(type(modbusItem)))

        # Adds Range in TagList
        if Device == type(modbusItem):
            dlg = AddRangeDlg(self)
            if dlg.exec_():
                name, addr, quantity = dlg.getParameters()
                data = modbusItem.addRange(int(addr), int(quantity), name)
                # data = modbusItem.addRange(50, 10, "range4")

                child = ModbusItem("node", node, data)
                self._model.beginInsertRows(index, 0, 0)
                self._model.endInsertRows()
                self.ui.treeView.resizeColumnToContents(0)

                # self._model.dataChanged.emit(QModelIndex(), QModelIndex(), [QtCore.Qt.DisplayRole, QtCore.Qt.TextColorRole])
                print("ModbusDriverViewer: {0}, type={1}".format(node.name(), type(node)))

        elif ModbusDriver == type(modbusItem):

            # Dialog for getting parameters of new driver
            dlg = AddDriverDlg(self)
            if dlg.exec_():
                name, ip, port = dlg.getParameters()
                device = DeviceCreator.create(ip, int(port), name)
                self._driver.addDevice(device)

                childNode = ModbusItem("device", node, device)
                self._model.beginInsertRows(index, 0, 0)
                self._model.endInsertRows()
                self.ui.treeView.resizeColumnToContents(0)

    @QtCore.pyqtSlot()
    def __onRemove(self):
        print(self.__onRemove.__name__)
        index = self.ui.treeView.selectedIndexes()[0]

        node = self._model.getNodeFromIndex(index)
        modbusItem = node.ref()
        print("Type of modbus = {0}".format(type(modbusItem)))
        if Range == type(modbusItem):

            id = modbusItem.dataId()
            device: Device = node.getParent().ref()
            res = device.delRangeById(id)

            if res:
                parent = node.getParent()
                parent.remChild(node)
                self._model.beginResetModel()
                self._model.endResetModel()
                # self._model.beginRemoveRows(index, 0, 0)
                # self._model.endRemoveRows()
                self.ui.treeView.resizeColumnToContents(0)

        elif Device == type(modbusItem):
            print("this is TagList: {0}".format(modbusItem.name()))
            parent = node.getParent()
            parent.remChild(node)

            driver: ModbusDriver = parent.ref()
            print("this is Driver: {0}".format(driver.name()))
            device: Device = modbusItem
            if driver.delDevice(device):
                print("ModbusDriverViewer::_onRemove::driver deleted")
            else:
                print("ModbusDriverViewer::_onRemove::driver not deleted")
            self._model.beginResetModel()
            self._model.endResetModel()

        self.ui.treeView.resizeColumnToContents(0)

    @QtCore.pyqtSlot()
    def __onStart(self):
        pass

    @QtCore.pyqtSlot()
    def __onStop(self):
        print(self.__onStop.__name__)
        index = self.ui.treeView.selectedIndexes()[0]

        node = self._model.getNodeFromIndex(index)
        device: Device = node.ref()
        print("node = {}".format(device.name()))
        device.stop()

    @QtCore.pyqtSlot()
    def __onProperty(self):
        print(self.__onProperty.__name__)
        index = self.ui.treeView.selectedIndexes()[0]

        node = self._model.getNodeFromIndex(index)
        device = node.ref()


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    # drv1 = ModbusDriver()
    # drv1.setObjectName("Modbus")

    devices = []

    # device1
    device1 = DeviceCreator.create("10.18.32.78", 10502, "dev1")
    device1.addRange(0, 3, "data1")
    device1.addRange(20, 7, "data2")
    device1.addRange(30, 5, "data3")
    devices.append(device1)

    # device2
    device2 = DeviceCreator.create("10.18.32.78", 20502, "dev2")
    device2.addRange(0, 10)
    devices.append(device2)

    drv1 = DriverCreator.create("modbus", devices)

    viewer = ModbusDriverViewer()
    viewer.addDriver(drv1)
    viewer.show()

    return app.exec()


if __name__ == "__main__":
    exit(main(sys.argv))
