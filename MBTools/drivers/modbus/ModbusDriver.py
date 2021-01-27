# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from pymodbus.client.sync import ModbusTcpClient
import time
import sys
import enum
import numpy as np
from abc import ABC, abstractmethod

DEFAULT_IP = "127.0.0.1"      # default ip address of modbus server
DEFAULT_PORT = 502            # default port of modbus server
# NUMBER = 50                 # number of registers
REQUEST_DELAY = 0.5           # default delay between requests, sec

lock = QtCore.QMutex()

""" Tag qulity """
@enum.unique
class QualityEnum(enum.Enum):
    UNDEF = 0,          # Undefined
    GOOD = 1,           # Data is relevant
    NO_CONNET = 2,      # No connection with server
    REQUEST_ERROR = 3   # Connection with server exist but request has error
    DRV_NOT_STARTED = 4 # Driver isn't started
    NOT_CONFIGURED = 5  # Driver hasn't represented address


""" Represents Quality as String """
QualityEnumStr = {
    QualityEnum.UNDEF: "UNDEF",                     # corresponds to UNDEF quality
    QualityEnum.GOOD: "GOOD",                       # corresponds to GOOD quality
    QualityEnum.NO_CONNET: "NO CONNECTION",         # corresponds to NO_CONNECT quality
    QualityEnum.REQUEST_ERROR: "REQUEST ERROR",     # correstopns to REQUEST_ERROR quality
    QualityEnum.DRV_NOT_STARTED: "DRIVER NOT WORD", # correstopns to REQUEST_ERROR quality
    QualityEnum.NOT_CONFIGURED: "NOT CONFIGURED"    # correstopns to NOT_CONFIGURED quality
}


# \todo add ABC
# use accessify library fo @protected and @prived methods
class AbstractModbus:
    """
   This class defines interface for all modbus items (modbus ranges, modbus devices and drivers itself)
    """
    def __init__(self):
        self._name = "name"
        self._comment = "comment"

    @abstractmethod
    def ranges(self):
        """ Returns all data of object including child datas """
        pass

    @abstractmethod
    def isAddressExists(self, address: int) -> bool:
        """ returns True if modbus item uses register with pointed address """
        pass

    @abstractmethod
    def _setName(self):
        pass

    @abstractmethod
    def _setComment(self, name: str):
        self._comment

    def name(self):
        return self._name

    def comment(self):
        return self._comment

    def updateInfo(self):
        self._setName()
        self._setComment()


class Range(QObject, AbstractModbus):
    """ Class represents one continuous range of modbus registers """
    id = 0

    def __init__(self, size: int = 0, parent=None):
        QObject.__init__(self, parent)
        AbstractModbus.__init__(self)

        self.__address = 0                   # first registers address
        self.__map = [0] * size              # continuous sequence of modbus registers
        self.__quality = QualityEnum.UNDEF   # quality
        self.__time = time.localtime()       # last time of updating
        self.__id = 0                        # ID

        self.__id = Range.id + 1
        Range.id = self.__id
        self.updateInfo()

    # ---------- Public ----------

    def isAddressExists(self, address: int) -> bool:
        """ returns True if modbus item uses register with pointed address """
        return address in range(self.__address, self.__address + self.number())

    def ranges(self) -> list:
        """ AbstractModbus interface Returns all ranges of item.  In this case, returns itself. """
        return [self]

    def dataId(self) -> int:
        """ Returns ID """
        return self.__id

    def isEmpty(self) -> bool:
        """ Checks the range for registers """
        return self.__map is None

    def setAddress(self, address):
        self.__address = address
        self.updateInfo()

    def address(self) -> int:
        return self.__address

    def number(self) -> int:
        return len(self.__map)

    def setRegisters(self, registers: list, quality=QualityEnum.UNDEF):
        if len(self.__map) < len(registers):
            self.__map = registers[:len(self.__map)]
        else:
            self.__map = list(registers)

        self.__quality = quality
        self.__time = time.localtime()
        self.updateInfo()

    def setQuality(self, quality):
        self.__quality = quality

    def registers(self):
        return self.__map

    def reristersNum(self, addr: int, num: int):
        """ Returns values of num registers from address = addr """
        index = addr - self.__address
        if index + num > len(self.__map):
            return None
        return self.__map[index: index + num]

    def register(self, addr: int):
        """
        returns value by register address
        \todo check the vallidity of the index
        """
        index = addr - self.__address
        if index > len(self.__map):
            return None
        return self.__map[index]

    def quality(self):
        return self.__quality

    def time(self):
        return self.__time

    # ---------- Protected ----------
    def _setName(self):
        self._name = self.objectName()

    def _setComment(self):
        self._comment = "{0}..{1}".format(self.address(), self.number())

    # ---------- Privat -----------
    def __str__(self):
        """ data[id]: [addr:num] time [quality] registers """
        return "data{0}: {1} [{2}:{3}] {4}: {5}".format(
            self.__id,
            "{:02}:{:02}:{:02}".format(self.__time.tm_hour, self.__time.tm_min, self.__time.tm_sec, self.__time),
            self.__address, len(self.__map),
            QualityEnumStr[self.__quality],
            self.__map[:50]) # will be shown only 50 registers

    def __len__(self):
        return len(self.__map)


class Device(QObject, AbstractModbus):
    """
    Class pools modbus server
    """
    dataChanged = pyqtSignal(Range)
    rangeNumberChanged = pyqtSignal()
    finished = pyqtSignal()
    runningChanged = pyqtSignal(bool)

    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_PORT,  parent=None):
        super().__init__(parent)
        self.__ranges = []       # ranges of modbus registers (separated requists)
        self.__ip = ip           # ip address of modbus server
        self.__port = port       # port of modbus server

        # For using on writing commangs
        self.__writeAddr = 0
        self.__writeValue = 0
        self._writeFlag = False
        # self.updateInfo()

        # Flags
        self.is_running = False

    def ip(self):
        """ Returns ip address of modbus server """
        return self.__ip

    def port(self):
        """ Returns port number of modbus server """
        return self.__port

    def isAddressExists(self, address: int) -> bool:
        for range in self.__ranges:
            if range.isAddressExists(address):
                return True
        return False

    def _setName(self):
        self._name = self.objectName()

    def _setComment(self):
        self._comment = "{0}:{1}".format(self.__ip, self.__port)

    def addRange(self, addr, num, name: str = '?') -> Range:
        """
        Adds new range of modbus addresses (this will be new request)
        :param addr: Start address
        :param num: Number of registers
        :param name: Name of registers range
        :return: object with represents this modbus range

        \todo This method should itself reallocate the ranges based on the existing ranges
        """
        print("{0}: Device::addRange".format(self.name()))
        data = Range(num)
        data.setAddress(addr)
        data.setObjectName(name)
        self.__ranges.append(data)
        self.rangeNumberChanged.emit()
        return data

    def delRange(self, data: Range) -> bool:
        print("{0}: Device::delRange".format(self.name()))
        self.__ranges.remove(data)
        self.rangeNumberChanged.emit()
        return True

    def delRangeById(self, id: int) -> bool:
        for data in self.__ranges:
            if data.dataId() == id:
                self.__ranges.remove(data)
                self.rangeNumberChanged.emit()
                return True
        return False

    def ranges(self):
        return self.__ranges

    @pyqtSlot()
    def start(self):
        """ Starts loop polling process """
        # print("TagList::start")
        print("{0}: Device::start".format(self.name()))
        # self.is_running = True
        self.is_running = True
        self.loop()

    # @pyqtSlot()
    def stop(self):
        """ Stops loop polling process """
        print("TagList::stop")
        self.is_running = False

    def loop(self):
        # print("TagList::loop")
        print("{0}: Device::loop".format(self.name()))
        n = 0
        client = ModbusTcpClient(self.__ip, self.__port)
        while self.is_running:
            for data in self.__ranges:
                try:
                    if client.is_socket_open():
                        if self._writeFlag:
                            client.write_register(self.__writeAddr, self.__writeValue)
                            print("<- {0}: {1}".format(self.__writeAddr, self.__writeValue))
                            self._writeFlag = False
                        result = client.read_holding_registers(data.address(), data.number())
                        data.setRegisters(result.registers, QualityEnum.GOOD)
                        with QtCore.QMutexLocker(lock):
                            print(data)
                            if data:
                                self.dataChanged.emit(data)
                    else:
                        for d in self.__ranges:
                            d.setQuality(QualityEnum.NO_CONNET)
                            with QtCore.QMutexLocker(lock):
                                self.dataChanged.emit(d)
                        print("connecting to {0}:{1}".format(self.__ip, client.port))
                        client.connect()
                        time.sleep(1)

                except Exception as err:
                    print(err)
                    data.setQuality(QualityEnum.NO_CONNET)
                    with QtCore.QMutexLocker(lock):
                        self.dataChanged.emit(data)
            time.sleep(REQUEST_DELAY)

        client.close()
        for d in self.__ranges:
            d.setQuality(QualityEnum.DRV_NOT_STARTED)
            self.dataChanged.emit(d)

        self.finished.emit()

    @pyqtSlot(int, int)
    def writeRegisters(self, addr, value):
        print("{0}::writeRegisters".format(__class__))
        self.__writeAddr = addr
        self.__writeValue = value
        self._writeFlag = True

    @pyqtSlot(int, int)
    def readRegisters(self, addr, num):
        pass


class ModbusDriver(QObject, AbstractModbus):
    dataChanged = pyqtSignal(str, Range)
    cmdSent = pyqtSignal(int, int)
    rangeNumberChanged = pyqtSignal()
    deviceNumberChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__name = ""
        self.__comment = ""
        self.__devices = {}

    def addDevice(self, device: Device):
        thread = QThread()
        device.dataChanged.connect(self.onDataChanged)
        device.rangeNumberChanged.connect(self.rangeNumberChanged)
        self.cmdSent.connect(device.writeRegisters)
        self.__devices[device] = thread
        device.moveToThread(thread)
        thread.started.connect(device.start)
        device.finished.connect(thread.terminate)
        thread.start()
        self.deviceNumberChanged.emit()

    def delDevice(self, device: Device) -> bool:
        for dev in self.__devices.keys():
            print(id(dev))

        if device in self.__devices:
            print("TagList has found {0}".format(device))
        else:
            print("TagList hasn't found ")
            return False

        device.stop()
        thread: QThread = self.__devices[device]
        thread.quit()
        thread.wait()
        print("device deleted : {0}".format(thread.isRunning()))
        del self.__devices[device]
        self.deviceNumberChanged.emit()

    @QtCore.pyqtSlot(Range)
    def onDataChanged(self, data: Range):
        sender = self.sender()
        self.dataChanged.emit(sender.objectName(), data)

    @QtCore.pyqtSlot(int, int)
    def onCmdReady(self, addr: int, value: int, device: Device = None):
        """
        Sends value for writing to register using address for all devices which has this address
        :param addr: address of register for writing
        :param value: value for writing
        :return:
        """
        for device in self.__devices.keys():
            if device.isAddressExists(addr):
                device.writeRegisters(addr, value)
        # TODO make this method by using signal, now it'not work
        # self.cmdSent.emit(addr, value)

    def devices(self):
        devices = self.__devices.keys()
        return devices

    # Overrided methods from AbstractDriver
    def ranges(self):
        datas = []
        for client in self.devices():
            datas.extend(client.ranges())
        return datas

    def _setName(self):
        self.__name = self.objectName()

    def _setComment(self):
        self.__comment = "Modbus driver"

    def isAddressExists(self, address: int) -> bool:
        pass

    def clear(self):
        dev = self.__devices.keys()[0]
        self.delDevice(dev)


class DeviceCreator:
    @staticmethod
    def create(ip: str, port: int, name: str):
        device = Device(ip, port)
        device.setObjectName(name)
        device.updateInfo()
        return device


class DriverCreator:
    @staticmethod
    def create(name: str, devices=None):
        drv = ModbusDriver()
        drv.setObjectName("modbus")
        if devices is not None:
            for dev in devices:
                drv.addDevice(dev)
        return drv


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    drv1 = DriverCreator.create("modbus")
    drv1.deviceNumberChanged.connect(lambda: print("TagList number Changed"))

    # device1
    device1 = DeviceCreator.create("10.18.32.78", 10502, "dev1")
    device1.addRange(0, 3, "data1")
    device1.addRange(20, 7, "data2")
    drv1.addDevice(device1)

    # slepping and adding device after
    QThread.sleep(5)
    device2 = DeviceCreator.create("10.18.32.78", 20502, "dev2")
    device2.addRange(0, 10)
    drv1.addDevice(device2)

    # slepping and deleting device after
    QThread.sleep(5)
    drv1.delDevice(device2)

    return app.exec()


if __name__ == "__main__":
    exit(main(sys.argv))