import json
import sys

from enum import Enum

from MBTools.oiserver.Tag import Tag, TagType
from MBTools.drivers.modbus.ModbusDriver import *
from MBTools.oiserver.constants import TagTypeFromStr

from PyQt5 import QtWidgets, QtCore


class DeviceConfig:
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


class Configurator:
    def __init__(self):
        self._tags_config = []
        self._devices_config = []
        self._tags = []
        self._devices = []
        self._valid = False        # has valid configuration

    def read_config(self, file_name: str):
        """Returns (devices, lists) awerwise None"""
        pass

    def write_config(self, file: str):
        pass

    def get_devices(self):
        pass

    def get_tags(self):
        pass

    def clear(self):
        self._tags_config.clear()
        self._devices_config.clear()
        self._tags.clear()
        self._devices.clear()
        self._valid = False


class JsonConfigure(Configurator):
    def __init__(self):
        super().__init__()
        self.__data = None

    def is_valid(self):
        return self._valid

    def read_config(self, file_name: str):
        try:
            with open(file_name, 'r') as f:
                self.__data = json.load(f)
                self.clear()
                devs = self.__data["devices"]
                # print(devs)
                for dev in devs:
                    dev_config = DeviceConfig(name=dev["name"],
                                              protocol=dev["protocol"],
                                              ip=dev["ip"],
                                              port=dev["port"])
                    self._devices_config.append(dev_config)

                tags = self.__data["tags"]
                for tag in tags:
                    tag_type = None
                    if tag["type"] in TagTypeFromStr:
                        tag_type = TagTypeFromStr[tag["type"]]
                    else:
                        continue
                    tag_config = TagConfig(name=tag["name"],
                                           type_=tag_type,
                                           device_name=tag["device"],
                                           address=tag["address"],
                                           comment=tag["comment"])
                    if (TagType.BOOL == tag_type):
                        bit_number = tag["bit"]
                        tag_config.set_bit(bit_number)
                    self._tags_config.append(tag_config)
        except IOError as ioe:
            print("Error opening the file: ", ioe)
            return None

        self._valid = True
        return self._devices, self._tags

    def tags_config(self):
        return self._tags_config

    def devices_config(self):
        return self._devices_config


class FormatName(Enum):
    JSON = 1


def create_config(name: FormatName, file: str):
    """
    Configurators factory:
        name:       format name (list of names: FormatName)
        file:       file wich contains configuration
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
    app = QtWidgets.QApplication(sys.argv)

    VALID_FILE_NAME = "conf.json"
    INVALID_FILE_NAME = "conf1.json"

    conf = JsonConfigure()


    print("step2")
    res = conf.read_config(INVALID_FILE_NAME)
    if res is not None:
        devices_config = conf.devices_config()
        tags_config = conf.tags_config()
        print("devices:")
        for device_conf in devices_config:
            print('\t', device_conf)
        print("tags:")
        for tag_conf in tags_config:
            print('\t', tag_conf)
        print("OK")
    else:
        print("File isn't read")

    print("config valid: {}".format(conf.is_valid()))

    print("step1")
    res = conf.read_config(VALID_FILE_NAME)
    print("config valid: {}".format(conf.is_valid()))
    print("finish")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
