# -----------------------------------------------------------
# This module contains Model of Data
# - drivers
# - devices
# - tags
#
# (C) 2021 Maxim Kozyakov, Voronezh, Russia
# Released under GNU Public License (MIT)
# email kmmax@yandex.ru
# -----------------------------------------------------------
import time

from MBTools.oiserver.Tag import Tag, TagType
from MBTools.drivers.modbus.ModbusDriver import *
from MBTools.oiserver.constants import TagTypeFromStr, StrFromTagType
from MBTools.oiserver.OIServerConfigure import JsonConfigure, DeviceConfig, TagConfig
from MBTools.drivers.modbus.ModbusDriver import DriverCreator, DeviceCreator


class DataModel(list):
    """
    Container for data. Contains: drivers, devices, tags
    """
    def __init__(self, drivers=[], devises=[], tags=[]):
        self.__drivers = drivers
        self.__devices = devises
        self.__tags = tags

    def drivers(self):
        pass

    def devices(self):
        return self.__devices

    def tags(self):
        pass

    def append(self, tag: Tag) -> None:
        """ Overloaded: appends new tag """
        assert Tag is not None, " None instead of Tag"
        device: Device = tag.device
        device_name = device.name()
        # driver_name: ModbusDriver = tag.device.driver().name()
        if DataModel.find_by_name(device_name, self.__devices) is None:
            self.__devices.append(device)
        # if DataModel.find_by_name(tag.name, self.__devices) is None:
        #     self.__devices.append(device)

        super().append(tag)

    @staticmethod
    def find_by_name(name: str, collection):
        """Returns the first object from the iterable collection with the given name

        object must have 'name()->str' method
        param[str] name - name of object
        param[iter] collection - iterable collection of objects (list, dict itc.)

        return object, otherwise None
        """
        ret_item = None
        for item in collection:
            if item.name() == name:
                ret_item = item
                break

        return ret_item


def main(argv):
    print(argv)

    dev1 = DeviceCreator.create("127.0.0.1", 502, "dev1")
    dev2 = DeviceCreator.create("127.0.0.1", 10502, "dev2")
    drv1 = DriverCreator.create("modbus", [dev1, dev2])
    tag1 = Tag(device=dev1, name="TAG1", type_=TagType.INT, address=100, comment="tag1 on dev1")
    tag2 = Tag(device=dev1, name="TAG2", type_=TagType.INT, address=101, comment="tag2 on dev1")
    tag3 = Tag(device=dev2, name="TAG3", type_=TagType.INT, address=100, comment="tag3 on dev2")
    # print(tag1)
    # print(tag2)
    # print(tag3)
    tags = []
    tags.append(tag1)
    tags.append(tag2)
    tags.append(tag3)

    devices = [dev1, dev2]

    # dev = DataModel.find_by_name(name="dev3", collection=devices)
    # if dev is not None:
    #     print(dev.name())
    # else:
    #     print("No devices")

    # time.sleep(2)
    print("----------------")

    model = DataModel()
    model.append(tag3)
    model.append(tag1)
    model.append(tag2)

    for item in model:
        print(item, ": ", id(item.device))

    for dev in model.devices():
        print(dev.name(), ": ", id(dev))

    return 0


if __name__ == "__main__":
    res = main(sys.argv)
    sys.exit(res)
