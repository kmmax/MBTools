# -*- coding: utf-8 -*-
import time

from PyQt5 import QtWidgets, QtCore
import sys
from MBTools.oiserver.constants import TagType, TagTypeSize
from MBTools.drivers.modbus.ModbusDriver import ModbusDriver, Device, DeviceCreator, QualityEnum, DriverCreator


class Tag:
    """
    Class represens single tag:
    - driver
    - name
    - value
    - address
    - type
    - comment
    - time
    - quality
    TODO make quality and time fields
    """
    def __init__(self, device: Device, name: str, type_: TagType, comment: str = "???", address: int = 0, bit_number=None):
        self.__name = name
        self.__address = address
        self.__bit_number = bit_number
        self.__value = 0
        self.__quality = QualityEnum.UNDEF
        self.__type = type_
        self.__comment = comment
        self.__time = None
        self.__device = device
        # print("{0}: Tag constructor".format(self.__name))

    @property
    def device(self) -> Device:
        return self.__device

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def address(self):
        return self.__address

    @property
    def bit_number(self):
        return self.__bit_number

    @property
    def quality(self) -> QualityEnum:
        return self.__quality

    @property
    def time(self):
        return self.__time

    @device.setter
    def device(self, device: Device):
        self.__device = device

    @address.setter
    def address(self, address):
        self.__address = address

    @bit_number.setter
    def bit_number(self, bit_number):
        self.__bit_number = bit_number

    @value.setter
    def value(self, value):
        self.__value = value

    def quality(self, quality: QualityEnum):
        self.__quality = quality

    @time.setter
    def time(self, time):
        self.__time = time

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, type):
        self.__type = type

    @property
    def comment(self):
        return self.__comment

    @comment.setter
    def comment(self, comment):
        self.__comment = comment

    def size(self) -> int:
        if self.__type in TagTypeSize:
            return TagTypeSize[self.__type]
        return None

    def __str__(self):
        size = 0
        if self.__type in TagTypeSize:
            size = TagTypeSize[self.__type]

        if self.__time:
            str_time = "{:02}:{:02}:{:02}".format(self.__time.tm_hour, self.__time.tm_min, self.__time.tm_sec)
        else:
            str_time = None

        return "{0}.{1} ; {2}; {3}[{4}]; [{5}:{6} : {7}]; {8}".format(
            self.__device.name(),
            self.__address,
            self.__name,
            self.__type,
            size,
            self.__value,
            self.__quality,
            str_time,
            self.__comment)


class TagList(list):
    """
    Class represents tag collection (for logical device control, for example Valve1)
    - name - name of tags collection
    - address - first address of tags collection
    - type -  type of logical device (for example "Valve1")
    """
    def __init__(self, name: str, address: int = 0, type=None):
        super().__init__()
        self._address = address
        self._name = name
        self._type = type

    def set_address(self, address):
        """ Set address of device """
        self._address = address

    def address(self):
        """ Returns address of device """
        return self._address

    def set_type(self, type):
        """ Set type of device """
        self._type = type

    def type(self):
        """ Returns type of device """
        return self._type

    def name(self):
        """ Returns name of device """
        return self._name

    def append(self, tag: Tag, offset: int = None) -> None:
        """ Overloaded: appends new tag """
        print("append: {0}, {1}".format(self._address, offset))
        if offset is not None:
            tag.address = self._address + offset
            print(tag.address)
        else:
            if self:
                last_teg = self[-1]
                tag.address = last_teg.address + TagTypeSize[last_teg.type]
            else:
                tag.address = self._address

        super().append(tag)

    def __str__(self):
        out_str = "{0}: {1}: addr={2}:\n".format(self._name, self._type, self._address)
        for tag in self:
            out_str += "\t" + str(tag) + "\n"
        return out_str


def main(argv):
    # devices
    dev1 = DeviceCreator.create(name="dev1", ip="127.0.0.1", port=30502)
    dev2 = DeviceCreator.create(name="dev2", ip="127.0.0.1", port=10502)
    dev1.addRange(99, 20, "rng1")
    dev1.addRange(199, 20, "rng2")

    # tags
    tag1 = Tag(device=dev1, name="TAG1", type_=TagType.INT, address=100, comment="tag1 on dev1")
    tag2 = Tag(device=dev1, name="TAG2", type_=TagType.INT, address=101, comment="tag2 on dev1")
    tag3 = Tag(device=dev2, name="TAG3", type_=TagType.INT, address=100, comment="tag3 on dev2")
    tag1.value = 11; tag1.quality = QualityEnum.UNDEF; tag1.time = time.localtime()
    tag2.value = 12; tag2.quality = QualityEnum.UNDEF; tag2.time = time.localtime()
    tag3.value = 13; tag3.quality = QualityEnum.UNDEF; tag3.time = time.localtime()
    print(tag1)
    print(tag2)
    print(tag3)

    devices = [dev1]
    drv = DriverCreator.create(name="modbus", devices=devices)

    dev1.start()


if "__main__" == __name__:
    sys.exit(main(sys.argv))
