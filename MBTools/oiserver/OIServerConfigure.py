# -----------------------------------------------------------
# This module contains tools of server configuration
#
# (C) 2021 Maxim Kozyakov, Voronezh, Russia
# Released under GNU Public License (MIT)
# email kmmax@yandex.ru
# -----------------------------------------------------------

import json
from enum import Enum
from typing import Final

from MBTools.oiserver.Tag import Tag, TagType
from MBTools.drivers.modbus.ModbusDriver import *
from MBTools.oiserver.constants import TagTypeFromStr, StrFromTagType

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


class DeviceConfig:
    """ Container which contains device configuration """
    def __init__(self, name: str, protocol: str, ip: str, port: int, comment=''):
        self.name = name
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.comment = comment

    def __str__(self):
        return "{0}: {1}; {2}; {3}; {4}".format(
            self.name, self.protocol, self.ip, self.port, self.comment
        )


class TagConfig:
    """ Container which contains tag configuration """
    def __init__(self, name: str, device_name: str, address: int, type_: TagType, comment='', bit_number=None):
        self.name = name
        self.device_name = device_name
        self.address = address  # register address
        self.bit_number = bit_number          # bit number
        self.type = type_       # type of register
        self.comment = comment

    def set_bit(self, bit_number: int):
        assert (bit_number >= 0 & bit_number < 16)
        self.bit_number = bit_number

    def __str__(self):
        return "{0}: {1}; {2}; {3}; {4}".format(
            self.name, self.device_name, self.address, self.type, self.comment
        )


class Configurator(ABC):
    """
    Class which provides configure of tags and devices list
    """
    def __init__(self):
        self._tags_config = []
        self._devices_config: DeviceConfig = []
        # self._tags = []
        # self._devices = []
        self._valid = False        # has valid configuration

    def is_valid(self):
        return self._valid

    @abstractmethod
    def read_config(self, file_name: str):
        """Returns (devices, lists) awerwise None"""
        pass

    @abstractmethod
    def write_config(self, file_name: str):
        """ Writes tags configuration to file

        :param[str] file_name - name of file for writing

        :return[bool] - True - successful, otherwise - False

        :raise IOError
        """
        pass

    def clear(self):
        """ Clears all configuration """
        self._tags_config.clear()
        self._devices_config.clear()
        # self._tags.clear()
        # self._devices.clear()
        self._valid = False

    def tags_config(self):
        """ Returns current tags configuration """
        return self._tags_config

    def devices_config(self):
        """ Returns current devices configuration """
        return self._devices_config

    def add_tag(self, tag: TagConfig):
        """ Adds new tag in tag list """
        self._tags_config.append(tag)

    def rem_tag(self, name: str):
        """ Removes tag by name """
        pass

    def add_device(self, dev: DeviceConfig):
        """ Adds new device in devices list """
        self._devices_config.append(dev)

    def rem_device(self, name: str):
        """ Removes device by name """
        pass

    def __str__(self):
        devs_str = "\n\t".join([str(dev) for dev in self._devices_config])
        tags_str = "\n\t".join([str(tag) for tag in self._tags_config])
        msg = "Valid: {}".format(self._valid)
        msg += "\nDevices:"
        msg += "\n\t" + devs_str
        msg += "\n" + "Tags:"
        msg += "\n\t" + tags_str

        return msg


class JsonConfigure(Configurator):
    """
    Configurator which works with JSON format
    """
    def __init__(self):
        super().__init__()
        self.__data = None

    def read_config(self, file_name: str):
        try:
            with open(file_name, 'r') as f:
                self.__data = json.load(f)
                self.clear()
                devs = self.__data[DEVICE_BLOCK_ALIASE]
                # print(devs)
                for dev in devs:
                    dev_config = DeviceConfig(name=dev[DEVICE_ALIASES.NAME],
                                              protocol=dev[DEVICE_ALIASES.PROTOCOL],
                                              ip=dev[DEVICE_ALIASES.IP],
                                              port=dev[DEVICE_ALIASES.PORT])
                    self._devices_config.append(dev_config)

                tags = self.__data[TAG_BLOCK_ALIASE]
                for tag in tags:
                    tag_type = None
                    if tag[TAG_ALIASES.TYPE] in TagTypeFromStr:
                        tag_type = TagTypeFromStr[tag[TAG_ALIASES.TYPE]]
                    else:
                        continue
                    tag_config = TagConfig(name=tag[TAG_ALIASES.NAME],
                                           type_=tag_type,
                                           device_name=tag[TAG_ALIASES.DEVICE],
                                           address=tag[TAG_ALIASES.ADDRESS],
                                           comment=tag[TAG_ALIASES.COMMENT])
                    if (TagType.BOOL == tag_type):
                        bit_number = tag[TAG_ALIASES.BIT]
                        tag_config.set_bit(bit_number)
                    self._tags_config.append(tag_config)
        except IOError as ioe:
            print("Error opening the file_name: ", ioe)
            return None

        self._valid = True
        return self._devices_config, self._tags_config

    def write_config(self, file_name: str):
        try:
            with open(file_name, 'w') as f:
                data = {}
                devices = []
                for device_config in self._devices_config:
                    device = {}
                    device[DEVICE_ALIASES.NAME] = device_config.name
                    device[DEVICE_ALIASES.PROTOCOL] = device_config.protocol
                    device[DEVICE_ALIASES.IP] = device_config.ip
                    device[DEVICE_ALIASES.PORT] = device_config.port

                    devices.append(device)

                    data[DEVICE_BLOCK_ALIASE] = devices

                tags = []
                for tag_config in self._tags_config:
                    tag = {}
                    tag[TAG_ALIASES.NAME] = tag_config.name
                    tag[TAG_ALIASES.TYPE] = StrFromTagType[tag_config.type]
                    tag[TAG_ALIASES.DEVICE] = tag_config.device_name
                    tag[TAG_ALIASES.ADDRESS] = tag_config.address
                    if TagType.BOOL == tag_config.type:
                        tag[TAG_ALIASES.BIT] = tag_config.bit_number
                    tag[TAG_ALIASES.COMMENT] = tag_config.comment

                    tags.append(tag)

                    data[TAG_BLOCK_ALIASE] = tags

                json.dump(data, f, indent=4, ensure_ascii=False)

        except IOError as ioe:
            print("Error opening the file_name: ", ioe)
        pass


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
        conf = JsonConfigure()
        conf.read_config(file)
        if conf.is_valid():
            return conf
        else:
            return None


def main(argv):
    READ_VALID_FILE_NAME = "conf.json"           # valid file for reading
    READ_INVALID_FILE_NAME = "conf1.json"        # invalid file for reading
    WRITE_FILE_NAME = "write_conf.json"      # file name for writing

    conf = JsonConfigure()

    # Adding a tag is checked here
    res = conf.read_config(READ_VALID_FILE_NAME)
    new_dev = DeviceConfig("test", "modbus", ip="127.0.0.1", port=1502 )
    new_tag = TagConfig("TAG_TEST", new_dev.name, 100, TagType.INT)
    conf.add_device(new_dev)
    conf.add_tag(new_tag)

    print(conf)

    # Configuration saving is checked here
    conf.write_config("write_conf.json")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
