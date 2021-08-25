# -----------------------------------------------------------
# This module contains tools for server configuration
#
# (C) 2021 Maxim Kozyakov, Voronezh, Russia
# Released under GNU Public License (MIT)
# email kmmax@yandex.ru
# -----------------------------------------------------------

"""
Модуль Config.py
Назначение:
- Производит чтение конфигурации из файла и производит настройку модели данных
- Производит запись текущей конфигурации модели данных в файл

@todo
- в полной мере не реализовано добавление/удаление тега(гов). Т.е. при добавлении/удалении тега необходима перенастройка драйвера в соответствии с конфигурацией тега:
    + добавление/удаление Device (если нужно) в Driver
    + изменение Ranges в Device (если нужно) при условии, что Tag использует уже сконфигурированный Device
"""

import json
from enum import Enum
from typing import Final

from MBTools.oiserver.Tag import Tag, TagType
from MBTools.drivers.modbus.ModbusDriver import *
from MBTools.oiserver.constants import TagTypeFromStr, StrFromTagType
from MBTools.oiserver.DataModel import DataModel, IDataModel

from PyQt5 import QtWidgets

from abc import ABC, abstractmethod


# ------------ CONSTANTS BEGIN ------------------
# This constants defines names of parameters in json config file

DEVICE_BLOCK_ALIASE: Final = "devices"
TAG_BLOCK_ALIASE: Final = "tags"


class DEVICE_ALIASES:
    """ Constants. Aliases for fields json config file which describes DEVICE """
    NAME = "name"
    PROTOCOL = "protocol"
    IP = "ip"
    PORT = "port"
    COMMENT = "comment"


class TAG_ALIASES:
    """ Constants. Aliases for fields json config file which describes TAG """
    NAME = "name"
    TYPE = "type"
    DEVICE = "device"
    ADDRESS = "address"
    BIT = "bit"
    COMMENT = "comment"

# ------------ CONSTANTS END ------------------


class AbcConf(ABC):
    """
    Class which configures data model
    """
    def __init__(self):
        self._valid = False                     # has valid configuration
        self._model: IDataModel = DataModel()   # current data model

    def set_model(self, model: IDataModel):
        self._model = model

    def model(self) -> DataModel:
        return self._model

    def is_valid(self):
        if self._model is None:
            return False
        return True
        # return self._valid

    def add_tag(self, tag: Tag):
        """ Adds new tag in tag list
        @todo Данная методо только добавляет тег в список тегов модели, но не
        производит переконфигерацию драйвера (возможно нужно добавить новые адреса
        для опроса, перераспределить ranges и т.д.). Это нужно отнести к ответственности
        самого драйвера.

        NOT IMPLEMENTED!!!
        """
        self._model.add(tag)

    def add_tags(self, tags: list):
        """ Adds new tag in tag list

        NOT IMPLEMENTED!!! see: add_tag()
        """
        for tag in tags:
            self.add_tag(tag)

    def del_tag(self, name: str):
        """ Removes tag by name

        NOT IMPLEMENTED!!! see: add_tag()
        """
        pass

    def clear(self):
        """ Clears all configuration """
        self._model.clear()
        self._valid = False

    @abstractmethod
    def read_model_config(self, filename: str):
        """Reads config file and write configuration to model data"""
        pass

    @abstractmethod
    def write_model_config(self, filename: str):
        """ Writes tags configuration to file from data model"""
        pass

    def __str__(self):
        msg = ""
        return msg


class JsonConf(AbcConf):
    """
    Configurator which works with JSON format
    """
    def __init__(self):
        super().__init__()
        self.__drv = None

    def read_model_config(self, filename: str):
        """Read config file into data model
        @param[in] - name of config file
        """
        try:
            devices = {}
            with open(filename, 'r') as f:
                self.__data = json.load(f)
                self.clear()
                self._model.clear()

                # devices
                devs = self.__data[DEVICE_BLOCK_ALIASE]
                for dev in devs:

                    name=dev[DEVICE_ALIASES.NAME]
                    protocol=dev[DEVICE_ALIASES.PROTOCOL]
                    ip=dev[DEVICE_ALIASES.IP]
                    port=dev[DEVICE_ALIASES.PORT]
                    dev = DeviceCreator.create(ip, port, name)
                    key = hash(dev.name())
                    devices[key] = dev

                # tags
                tags = self.__data[TAG_BLOCK_ALIASE]
                for tag in tags:
                    tag_type = None
                    if tag[TAG_ALIASES.TYPE] in TagTypeFromStr:
                        tag_type = TagTypeFromStr[tag[TAG_ALIASES.TYPE]]
                    else:
                        continue

                    name = tag[TAG_ALIASES.NAME]
                    type_ = tag_type
                    device_name = tag[TAG_ALIASES.DEVICE]
                    address = tag[TAG_ALIASES.ADDRESS]
                    comment = tag[TAG_ALIASES.COMMENT]

                    # Находим устройство, соответстующее тегу
                    key = hash(device_name)
                    dev = devices.get(key)
                    if dev is None:
                        print("{0}, {1}: Bag tag's device in configuration, Break".format(key, device_name))
                        continue

                    tagr = Tag(device=dev, name=name, type_=type_, comment=comment, address=address)
                    if (TagType.BOOL == tagr.type):
                        bit_number = tag[TAG_ALIASES.BIT]
                        tagr.bit_number = bit_number

                    self._model.add(tagr)

        except IOError as ioe:
            print("Error opening the file_name: ", ioe)
            return None

        self._valid = True
        if self._model is None:
            return None

        self.__drv = DriverCreator.create("modbus")
        for dev in self._model.devices():
            addresses = ConfigCalculater.addresses_from_tags(self._model.tags(), dev)
            ranges = ModbusCalculator.split_numbers(addresses, 100)
            for i, rng in enumerate(ranges):
                dev.addRange(rng[0], rng[1] - rng[0] + 2, "range{}".format(i))
                # dev.start()
            # print(dev)
            self.__drv.addDevice(dev)

        return True

    def write_model_config(self, filename: str):
        """Write save data model in config file
        @param[filename] - name of config file
        """
        assert self._model is not None

        devs = self._model.devices()
        itags = self._model.tags()

        try:
            with open(filename, 'w') as f:
                data = {}
                devices = []
                for dev in devs:
                    device = {}
                    device[DEVICE_ALIASES.NAME] = dev.name()
                    device[DEVICE_ALIASES.PROTOCOL] = "modbus" #dev.protocol()
                    device[DEVICE_ALIASES.IP] = dev.ip()
                    device[DEVICE_ALIASES.PORT] = dev.port()

                    devices.append(device)

                    data[DEVICE_BLOCK_ALIASE] = devices

                tags = []
                for itag in itags:
                    tag = {}

                    tag[TAG_ALIASES.NAME] = itag.name
                    tag[TAG_ALIASES.TYPE] = StrFromTagType[itag.type]
                    tag[TAG_ALIASES.DEVICE] = itag.device.name()
                    tag[TAG_ALIASES.ADDRESS] = itag.address
                    if TagType.BOOL == itag.type:
                        tag[TAG_ALIASES.BIT] = itag.bit_number
                    tag[TAG_ALIASES.COMMENT] = itag.comment

                    tags.append(tag)

                    data[TAG_BLOCK_ALIASE] = tags

                json.dump(data, f, indent=4, ensure_ascii=False)

        except IOError as ioe:
            print("Error opening the file_name: ", ioe)


class ConfigCalculater(object):
    """This is an additional class for various calculations of the configurator. """
    def __init__(self):
        pass

    @staticmethod
    def addresses_from_tags(tags: list, dev: Device) -> list:
        """Returns a list of all addresses that the device polls"""
        addresses = [tag.address for tag in tags if dev.name() == tag.device.name()]
        addr_set = set(addresses)
        addresses = list(addr_set)
        print(dev.name(), addresses)
        return addresses


class FormatName(Enum):
    JSON = 1


def create_config(name: FormatName, file: str):
    """
    Configurators factory:
        name:       format name (list of names: FormatName)
        file_name:       file_name wich contains configuration
        returns:    config object, otherwise - None
    """
    # JSON
    if FormatName.JSON == name:
        conf = JsonConf()
        conf.read_config(file)
        if conf.is_valid():
            return conf
        else:
            return None


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    READ_VALID_FILE_NAME = "conf.json"           # valid file for reading
    READ_INVALID_FILE_NAME = "conf1.json"        # invalid file for reading
    WRITE_FILE_NAME = "write_conf.json"      # file name for writing

    conf = JsonConf()
    # model = conf.model()
    # tag_1 = model.find_tag_by_name("TAG1")
    # print(tag_1.device.driver())
    # print(tag_1.device)
    # print(tag_1)

    # Adding a tag is checked here
    model: IDataModel = DataModel()
    conf.set_model(model)
    conf.read_model_config(READ_VALID_FILE_NAME)

    dev1 = DeviceCreator.create(ip="127.0.0.1", port=30502, name="dev8")
    tag1 = Tag(dev1, "TAG1", TagType.INT, "This is tag1", address=100)
    tag2 = Tag(dev1, "TAG2", TagType.INT, "This is tag2", address=101)
    tag3 = Tag(dev1, "TAG3", TagType.INT, "This is tag3", address=102)
    conf.add_tag(tag1)
    conf.add_tag(tag2)
    conf.add_tag(tag3)
    print(model)

    # conf.read_model_config(READ_VALID_FILE_NAME)
    # model: IDataModel = DataModel()
    # print(model)

    app.exec()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
