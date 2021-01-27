# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
import sys
from MBTools.oiserver.constants import TagType, TagTypeSize
from MBTools.drivers.modbus.ModbusDriver import ModbusDriver, Device


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
        self.__quality = "???"
        self.__type = type_
        self.__comment = comment
        self.__time = None
        self.__device = device
        print("{0}: Tag constructor".format(self.__name))

    @property
    def device(self):
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
    def quality(self):
        return self.__quality

    @property
    def time(self):
        return self.__time

    @device.setter
    def device(self, device):
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

    @quality.setter
    def quality(self, quality):
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

        return "{0} : {1}, {2}[{3}], [{4}:{5} : {6}], {7}".format(
            self.__address,
            self.__name,
            self.__type,
            size,
            self.__value,
            self.__quality,
            str_time,
            self.__comment)


class TagList(list):
    """ Class represents tag collection """
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
    # app = QtWidgets.QApplication(sys.argv)

    tag1 = Tag("CM", TagType.UINT, "Command")
    tag2 = Tag("VL", TagType.REAL, "Current value")
    tag3 = Tag("ST1", TagType.UINT, "State")
    tag4 = Tag("AM", TagType.WORD, "Errors code")
    tag5 = Tag("PR1", TagType.WORD, "Protection")
    tags = TagList("G20K001SD001", 200, "Valve1")
    tags.append(tag1)
    tags.append(tag2)
    tags.append(tag3)
    tags.append(tag4)
    tags.append(tag5)
    tag1.value = 1024
    print(tags)

    # return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))
