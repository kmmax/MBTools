# -*- coding: utf-8 -*-
# -----------------------------------------------------------
# This module contains Model of Data
# - tags
# - devices
# - drivers
#
# (C) 2021 Maxim Kozyakov, Voronezh, Russia
# Released under GNU Public License (MIT)
# email kmmax@yandex.ru
# -----------------------------------------------------------
import time
import cProfile

from MBTools.oiserver.Tag import Tag, TagType
from MBTools.drivers.modbus.ModbusDriver import *
# from MBTools.drivers.modbus.ModbusDriver import DriverCreator, DeviceCreator
from abc import ABC, abstractmethod


def profile(func):
    """Decorator for run function profile"""
    def wrapper(*args, **kwargs):
        profile_filename = func.__name__ + '.prof'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(profile_filename)
        return result
    return wrapper


class IDataModel2(ABC):
    """
    Interface for data model
    """
    def __init__(self):
        pass

    @abstractmethod
    def add_device(self, name: str, **kwargs):
        """Adds new device"""
        pass

    @abstractmethod
    def add_tag(self, tagname: str, **kwargs):
        """Adds new tag"""
        pass

    @abstractmethod
    def driver(self) -> ModbusDriver:
        """Returns all used drivers"""
        pass

    @abstractmethod
    def devices(self) -> list:
        """Returns all used devices"""
        pass

    @abstractmethod
    def tags(self) -> list:
        """Returns all tags"""
        pass

    @abstractmethod
    def tags_in_device(self, device: Device) -> list:
        """Returns the tags associated with this device """
        pass

    @abstractmethod
    def find_tag_by_name(self, tagname: str) -> Tag:
        """Finds and Returns tag by name. Returns a tag (if exists) by its name, otherwise None """
        pass


class DataModel2(IDataModel2, set):
    """
    Container for data. Contains: drivers, devices, tags
    list overloaded methods:
    - add(a)
    - clear()
    - discard(a)

    @todo reload the remaining methods that change the content
    """
    def __init__(self, tags=[]):
        super().__init__()
        self.__driver = DriverCreator.create("modbus")
        self.__devices = []
        self.__tags = []

    # ---------- IDataModel overloaded ---------

    def driver(self) -> ModbusDriver:
        return self.__driver

    def devices(self):
        """Returns all devices"""
        return self.__devices

    def tags(self):
        """Returns all tags"""
        return self.__tags

    def add_device(self, name: str, **kwargs):
        if name in [dev.name for dev in self.__devices]:
            return None

        if 'ip' not in kwargs.keys():
            kwargs["ip"] = "127.0.0.1"

        if 'port' not in kwargs.keys():
            kwargs["port"] = 502;

        ip = kwargs.get('ip')
        port = kwargs.get('port')
        dev = DeviceCreator.create(ip=ip, port=port, name=name)
        self.__devices.append(dev)
        self.__driver.addDevice(dev)

    def add_tag(self, tagname: str, **kwargs):
        if tagname in [tag.name for tag in self.__tags]:
            return None

        if "type_" not in kwargs.keys():
            print("return: bad type_")
            return None
        if "address" not in kwargs.keys():
            print("return: bad address")
            return None
        if "devname" not in kwargs.keys():
            print("return: bad devname")
            return None
        if "comment" not in kwargs.keys():
            kwargs["comment"] = ""

        dev = self.find_device_by_name(kwargs.get("devname"))
        if dev is None:
            print("return: dev is null")
            return None
        # dev.addRange(0, 20, "range0")

        type_ = kwargs.get("type_")
        address = kwargs.get("address")
        comment = kwargs.get("comment")

        tag = Tag(device=dev, name=tagname, type_=type_, address=address, comment=comment)
        self.__tags.append(tag)

    def del_tag(self, tagname: str) -> None:
        """Overloaded: set.discard
            - Удаляется тег с указанным именем
            - обновляются списки devices и drivers

            Возвращает количество удаленных тегов
        """

        tag_out = None
        len_in = len(self.__tags)
        for tag in self.__tags:
            if tag.name == tagname:
                tag_out = tag
        self.__tags.remove(tag_out)

        return len_in - len(self.__tags)

    def del_device(self, devname: str) -> None:
        """Удаляет device если он не связан не с одним тегом """
        pass

    def clear_devices(self) -> None:
        # super().clear()
        # for dev in self.__devices:
        #     if not self.tags_in_device():
        #         self.__devices.remove(dev)
        pass

    def tags_in_device(self, devname: str) -> list:
        """Returns tags corresponds with the device """
        tags = [tag for tag in self.__tags if tag.device.name() == devname]
        return tags

    def find_tag_by_name(self, tagname: str) -> Tag:
        """Finds tag by name and return it, if tag not exists return None """
        pass

    def find_device_by_name(self, devname: str) -> Device:
        """Finds device by name and return it, if device not exists return None """
        for dev in self.__devices:
            if dev.name() == devname:
                return dev
        return None

    @staticmethod
    def find_by_name(name: str, collection):
        """Returns the first object from the iterable collection with the given name (devices, drivers)

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

    @staticmethod
    def __get_hash_from_tags(tags: list) -> dict:
        """Creates hash table of tags from tags list"""
        hash_tags = dict()
        for tag in tags:
            hash_tags[hash(tag.name)] = tag
        return hash_tags

    @staticmethod
    def __get_tags_from_hash(hash_tags: dict) -> list:
        """Creates tags list from tags hash table"""
        return hash_tags.values()

    def __get_devices_from_tags(self) -> list:
        """Returns devices which is used by all tags"""
        devices = set()
        for tag in self.__hash_tags.values():
            devices.add(tag.device)

        return list(devices)

    def __str__(self):
        msg = "model:\n"
        msg += "\tdevices:\n"
        for dev in self.__devices:
            msg += "\t\t" + str(dev)
        msg += "\ttags:\n"
        for tag in self.__tags:
            msg += "\t\t" + str(tag) + "\n"

        return msg

    # --- private ---
    @staticmethod
    def __calculate_ranges(max_len: int, addresses: list) -> dict:
        """ Method calculates ranges for modbus driver """
        if len(addresses) < 1:
            return None
        ranges = []
        addresses.sort()
        min_value = min(addresses)
        max_value = max(addresses)
        first = min_value

        x_old = min_value
        print(addresses)
        for x in addresses:
            if (x - first) > max_len:
                # last = x_old
                pair = [first, x_old]
                ranges.append(pair)
                first = x
            if x == max_value:
                pair = [first, x]
                ranges.append(pair)
            x_old = x

        return ranges


@profile
def find_tag_test(name: str):
    print("testing start...")
    dev1 = DeviceCreator.create("127.0.0.1", 502, "dev1")
    model = DataModel2()
    tags = []
    for i in range(1000):
        tag = Tag(device=dev1, name="TAG{}".format(str(i)), type_=TagType.INT, address=100, comment="tag1 on dev1")
        start_time = time.time()
        model.add(tag)
        end_time = time.time()
        print(tag)

    start_time = time.time()
    for i in range(10):
        my_tag = model.find_tag_by_name("TAG9999")
    end_time = time.time()
    print("my_tag: {}".format(my_tag))
    duration = end_time - start_time
    print("duration: {}".format(duration))


def test1():
    # app = QtWidgets.QApplication(sys.argv)

    model = DataModel2()
    model.add_device("dev1", ip="127.0.0.1", port=10502)
    model.add_device("dev2", ip="127.0.0.1", port=20502)
    model.add_device("dev3", ip="127.0.0.1", port=30502)

    model.add_tag(tagname="TAG01", devname="dev1", type_=TagType.INT, address=100, comment="tag1 on dev1")
    model.add_tag(tagname="TAG02", devname="dev1", type_=TagType.INT, address=101, comment="tag2 on dev1")
    model.add_tag(tagname="TAG03", devname="dev1", type_=TagType.INT, address=102, comment="tag3 on dev1")
    model.add_tag(tagname="TAG04", devname="dev2", type_=TagType.INT, address=100, comment="tag1 on dev1")
    model.add_tag(tagname="TAG05", devname="dev2", type_=TagType.INT, address=101, comment="tag2 on dev1")
    model.add_tag(tagname="TAG06", devname="dev2", type_=TagType.INT, address=102, comment="tag3 on dev1")

    print(model)
    print("----------------")
    print(model.del_tag("TAG04"))
    print(model.del_tag("TAG05"))
    print(model.del_tag("TAG06"))
    print("----------------")
    model.clear_devices()
    print("----------------")
    print(model)
    print("---")

    # dev = model.find_device_by_name("dev1")
    # if dev:
    #     dev.addRange(0, 10, "range0")
    #     dev.addRange(10, 10, "range1")
    #
    # dev = model.find_device_by_name("dev2")
    # if dev:
    #     dev.addRange(0, 10, "range2")
    #     dev.addRange(10, 10, "range4")
    #
    # return app.exec()


def main(argv):
    print(argv)
    print("----- model ------")
    test1()
    return 0


if __name__ == "__main__":
    res = main(sys.argv)
    sys.exit(res)
