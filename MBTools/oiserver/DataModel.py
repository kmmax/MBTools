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
from MBTools.drivers.modbus.ModbusDriver import DriverCreator, DeviceCreator
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


class IDataModel(ABC):
    """
    Interface for data model
    """
    def __init__(self):
        pass

    @abstractmethod
    def drivers(self) -> list:
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
    def tags_by_device(self, device: Device) -> list:
        """Returns the tags associated with this device """
        pass

    @abstractmethod
    def find_tag_by_name(self, tagname: str) -> Tag:
        """Finds and Returns tag by name. Returns a tag (if exists) by its name, otherwise None """
        pass


class DataModel(IDataModel, set):
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
        self.__hash_tags = DataModel.__get_hash_from_tags(tags)
        self.__drivers = self.__get_drivers_from_tags()
        self.__devices = self.__get_devices_from_tags()

    # ---------- IDataModel overloaded ---------
    def drivers(self):
        return self.__drivers

    def devices(self):
        return self.__devices

    def tags(self):
        return self.__hash_tags.values()

    def tags_by_device(self, device: Device) -> list:
        """Returns tags corresponds with the device """
        return [tag for tag in self.__hash_tags.values() if device.name() == tag.device.name()]

    def find_tag_by_name(self, tagname: str) -> Tag:
        """Returns tag by his name"""
        assert tagname
        key = hash(tagname)
        tag = self.__hash_tags.get(key)
        return tag

    # ---------- set overloaded ---------
    def add(self, tag: Tag) -> None:
        """Overloaded: set.add

        1. Если тэг с таким именем уже существует, то действие игнорируется
        2. Если отстутствует то тэг добавляется в существующий список тегов
        """
        assert Tag is not None, " None instead of Tag"

        key = hash(tag.name)
        if key in self.__hash_tags:
            print("Tag {0} has had dublicate (it ins't added)".format(tag.name))
            return None

        self.__hash_tags[hash(tag.name)] = tag
        super().add(tag)
        self.__devices = self.__get_devices_from_tags()
        self.__drivers = self.__get_drivers_from_tags()
        return None

    def discard(self, tag: Tag) -> None:
        """Overloaded: set.discard
            - Удаляется тег с указанным именем
            - обновляются списки devices и drivers
        """
        assert Tag is not None, " None instead of Tag"

        key = hash(tag.name)
        if key in self.__hash_tags:
            super().discard(tag)
            del self.__hash_tags[key]
            self.__devices = self.__get_devices_from_tags()
            self.__drivers = self.__get_drivers_from_tags()

        return None

    def clear(self) -> None:
        super().clear()
        self.__hash_tags.clear()
        self.__devices.clear()
        self.__drivers.clear()

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

    def __get_drivers_from_tags(self) -> list:
        """Returns drivers which is used by all tags"""
        drivers = list()
        return drivers

        return list(drivers)

    def __str__(self):
        msg = "model:\n"
        msg += "\tdevices:\n"
        for dev in self.__devices:
            msg += "\t\t" + str(dev)
        msg += "\ttags:\n"
        for tag in self.__hash_tags.values():
            msg += "\t\t" + str(tag) + "\n"

        return msg


@profile
def find_tag_test(name: str):
    print("testing start...")
    dev1 = DeviceCreator.create("127.0.0.1", 502, "dev1")
    model = DataModel()
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


def main(argv):
    print(argv)

    # dev1 = DeviceCreator.create("127.0.0.1", 502, "dev1")
    # dev2 = DeviceCreator.create("127.0.0.1", 10502, "dev2")
    # drv1 = DriverCreator.create("modbus", [dev1, dev2])
    #
    # tag1 = Tag(device=dev1, name="TAG1", type_=TagType.INT, address=100, comment="tag1 on dev1")
    # tag2 = Tag(device=dev1, name="TAG2", type_=TagType.INT, address=101, comment="tag2 on dev1")
    # tag3 = Tag(device=dev2, name="TAG3", type_=TagType.INT, address=100, comment="tag3 on dev2")
    # tag4 = Tag(device=dev2, name="TAG3", type_=TagType.INT, address=101, comment="tag3 on dev2")
    #
    # tags = []
    # tags.append(tag1)
    # tags.append(tag2)
    # tags.append(tag3)
    #
    # # devices = [dev1, dev2]
    #
    # # dev = DataModel.find_by_name(name="dev3", collection=devices)
    # # if dev is not None:
    # #     print(dev.name())
    # # else:
    # #     print("No devices")
    #
    # time.sleep(1)
    print("----- model ------")

    # model = DataModel()
    # model.add(tag3)
    # model.add(tag1)
    # model.add(tag2)
    # model.add(tag4)
    # print(model)

    # for item in model:
    #     print(item, ": device id={}".format(id(item.device)))
    # print("----- tags:")
    # model_tags = model.tags()
    # for t in model_tags:
    #     print(t, ": ", id(t.device))
    #
    # print("----- devices:")
    # for device in model.devices():
    #     print(device.name(), ": ", id(device))
    #
    # print("=====")
    # model.discard(tag3)
    # for item in model:
    #     print(item, ": device id={}".format(id(item.device)))
    # print("-----")
    # for device in model.devices():
    #     print(device.name(), ": ", id(device))

    find_tag_test("TAG1")

    return 0


if __name__ == "__main__":
    res = main(sys.argv)
    sys.exit(res)
