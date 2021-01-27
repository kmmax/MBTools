import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from MBTools.drivers.modbus.ModbusDriver import *


# class ModbusItem(object):
class ModbusItem:

    def __init__(self, name,  parentNode: 'ModbusItem'=None, ref: AbstractModbus=None):
        self._ref: AbstractModbus = ref
        self._name = "*"
        self._comment = ""
        if ref is not None:
            self._name = ref.objectName()
            self._comment = ref.comment()

        self._children = []
        self._parentNode = parentNode
        if parentNode is not None:
            parentNode.addChild(self)

    def typeName(self):
        return self._name

    def typeComment(self):
        return self._comment

    def typeQuality(self) -> QualityEnum:
        datas = self._ref.ranges()
        quality = QualityEnum.GOOD
        # The device has communication if at least one request is successful
        for data in datas:
            if QualityEnum.GOOD == data.quality():
                return QualityEnum.GOOD

        return QualityEnum.NO_CONNET

    def addChild(self, child):
        self._children.append(child)

    def remChild(self, child):
        self._children.remove(child)

    def remAllChildren(self):
        self._children.clear()

    def name(self):
        return self._name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def getParent(self):
        return self._parentNode

    def row(self):
        if self._parentNode is not None:
            return self._parentNode._children.index(self)

    def ref(self):
        return self._ref

    def getObjectType(self):
        return type(self._ref)


class DriverModel(QtCore.QAbstractItemModel):
    def __init__(self):
        QtCore.QAbstractItemModel.__init__(self)
        self._root: ModbusItem = ModbusItem("Root")
        self._drivers = []
        self.setupModelData()
        self.setHeaderData(1, QtCore.Qt.Horizontal, "value")

    @QtCore.pyqtSlot(str, Range)
    def onDataUpdate(self, drvName: str = "", data: Range = Range()):
        # print("DriverModel::onDataChanged")
        # self.dataChanged(QModelIndex(), QModelIndex(), [QtCore.Qt.DisplayRole, QtCore.Qt.TextColorRole])
        # QAbstractItemModel.dataChanged.emit(QModelIndex(), QModelIndex())
        # self.dataChanged(QModelIndex(), QModelIndex())
        self.dataChanged.emit(QModelIndex(), QModelIndex(), [QtCore.Qt.DisplayRole, QtCore.Qt.TextColorRole])

    def addDriver(self, drv: ModbusDriver):
        drv.dataChanged.connect(self.onDataUpdate)
        self._drivers.clear()
        self._drivers.append(drv)
        self.setupModelData()
        self.beginResetModel()
        self.endResetModel()

    def setDriver(self, drv: ModbusDriver):
        """
        Remove all drivers and sets single driver
        :param drv:
        :return:
        """
        print("ModbusModel::setDriver")
        self._drivers.clear()
        drv.dataChanged.connect(self.onDataUpdate)
        self._drivers.append(drv)
        self.setupModelData()
        self.beginResetModel()
        self.endResetModel()

    def removeAllDrivers(self):
        self._drivers.clear()
        self._root.remAllChildren()
        self.setupModelData()
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, index=QtCore.QModelIndex()):
        return 2

    def getNodeFromIndex(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._root

    def parent(self, index):
        node = self.getNodeFromIndex(index)
        parentNode = node.getParent()
        if parentNode == self._root:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parentIndex):
        parentNode = self.getNodeFromIndex(parentIndex)
        childItem = parentNode.child(row)
        if childItem:
            newIndex = self.createIndex(row, column, childItem)
            return newIndex
        else:
            return QtCore.QModelIndex()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            parentNode = self._root
        else:
            parentNode = parent.internalPointer()
        return parentNode.childCount()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        row = index.row()
        column = index.column()
        node: ModbusItem = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            if column == 0 and not self.columnCount():
                return QtCore.QModelIndex()
            elif 0 == column:
                return QtCore.QVariant(node.typeName())
            elif 1 == column:
                return QtCore.QVariant(node.typeComment())
            else:
                return QtCore.QModelIndex()
        elif QtCore.Qt.TextColorRole == role:
            if 0 == column or 1 == column:
                # print(node.typeQuality())
                if QualityEnum.GOOD == node.typeQuality():
                    return QtCore.QVariant(QColor("green"))
                else:
                    return QtCore.QVariant(QColor("red"))

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if QtCore.Qt.Vertical == orientation:
            return QtCore.QVariant()

        if QtCore.Qt.DisplayRole == role:
            if 0 == section:
                return "Name"
            elif 1 == section:
                return "Description"

        if QtCore.Qt.TextAlignmentRole == role:
            return QtCore.Qt.AlignHCenter

        return QtCore.QVariant()

    def setupModelData(self):
        print("ModbusModel::setupModelData")
        if not self._drivers:
            print("No drivers")
            return

        for driver in self._drivers:
            drv1 = ModbusItem(name="modbus", parentNode=self._root, ref=driver)

            for device in driver.devices():
                name = device.objectName()
                print(name)
                dev = ModbusItem(name, drv1, device)
                for data in device.ranges():
                    range = ModbusItem("data", dev, data)


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(mainLayout)
        self.dataModel = DriverModel()

        self.viewA1 = QtWidgets.QTableView()
        self.viewA = QtWidgets.QTreeView()
        # self.viewA = QtWidgets.QListView()
        self.viewA.setModel(self.dataModel)
        self.viewA.clicked.connect(self.onClick)
        self.viewA1.setModel(self.dataModel)

        mainLayout.addWidget(self.viewA)
        mainLayout.addWidget(self.viewA1)

        self.viewA1.setSelectionModel(self.viewA.selectionModel())


        self.show()

    def onClick(self, index):
        node = index.internalPointer()
        print("{0}, {1}".format(node.name(), node.getParent().name()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
