# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
import sys
import numpy as np
from MBTools.oiserver.Tag import Tag, TagType, TagTypeSize
from MBTools.drivers.modbus.ModbusDriver import Range, \
    DeviceCreator, DriverCreator, QualityEnum
from MBTools.oiserver.OIServerConfigure import JsonConfigure, create_config, FormatName

lock = QtCore.QMutex()


class IOServer(QtCore.QObject):
    dataChanged = QtCore.pyqtSignal()
    configChanged = QtCore.pyqtSignal()

    def __init__(self, data=None, conf=None, parent=None):
        super().__init__(parent)

        self.__conf = conf

        # Data
        self.__data = data
        self.__drv = None
        self.__devices = []
        self.__tags = []


        # conf = create_config(FormatName.JSON, "config/conf.json")
        # conf = JsonConfigure()
        # conf.read_config("config/conf1.json")
        # if conf:
        #     self.set_config(conf)

    def clear_config(self):

        # Удаляем устройства
        devices = self.__devices
        for dev in devices:
            self.__drv.delDevice(dev)

        # Удаляем все теги
        self.__tags.clear()

        self.__drv = None
        self.configChanged.emit()

    def set_config(self, conf: JsonConfigure):
        """Sets new tags set by using tag configuration"""
        if not conf:
            return None
        if not conf.is_valid():
            return None

        """1. Old configuration clearing"""
        self.clear_config()

        self.__conf = conf
        devs_cfg = self.__conf.devices_config()
        tags_cfg = self.__conf.tags_config()

        """2. Devices configuration"""
        if self.__drv:
            for dev in self.__drv.devices():
                dev.stop()
            # for dev in self.__drv.devices():
            #     self.__drv.delDevice(dev)
        else:
            self.__drv = DriverCreator.create("modbus")
            self.__drv.dataChanged.connect(self.__onDataUpdated)
            self.__drv.rangeNumberChanged.connect(self.__onRangeNumberChanged)

        self.__devices.clear()
        for dev_cfg in devs_cfg:
            print(dev_cfg)
            dev = DeviceCreator.create(dev_cfg.ip, dev_cfg.port, dev_cfg.name)
            self.__devices.append(dev)

        for dev in self.__devices:
            self.__drv.addDevice(dev)

        print("OIServer: registered devices:")
        for dev in self.__devices:
            print("\tOIServer: {} ({}:{})".
                  format(dev.name(), dev.ip(), dev.port()))

        """3. Tags configuration"""
        tags = []
        self.__tags = []
        self.__tags.clear()
        for tag_cfg in tags_cfg:
            print(tag_cfg)
            for dev in self.__devices:
                if dev.name() == tag_cfg.device_name:
                    tag = Tag(device=dev,
                              name=tag_cfg.name,
                              type_=tag_cfg.type,
                              comment=tag_cfg.comment,
                              address=tag_cfg.address)
                    if (TagType.BOOL == tag.type):
                        tag.bit_number = tag_cfg.bit_number
                    tags.append(tag)
        self.add_tags(tags)

        self.configChanged.emit()

    def config(self):
        return self.__conf

    def devices(self):
        return self.__devices

    def addTag(self, tag: Tag):
        """ Adds single tag to current tag list """
        pass

    def add_tags(self, tags: list):
        """Adds set of tags to current tags list

        The method adds a list of tags to the existing list, performs configuring
        the modbus driver.

        Args:
            tags: list of tags wich will be added in self.__tags

        \bugs Если для адреса нового тега уже существует диапазон, то все равно создается
        новый диапазон (запрос) для нового тега. Разобраться.
        \todo Для последнего тега, если он больше 1 регистра, добавляется в конец еще адрес.
        Сделать это сразу после формирования свписка, а не в блоке <if device_tags:> - подумать
        """
        self.__tags.extend(tags)
        addresses = []
        ranges = []
        """We split new tags addresses by devices.
        Not consider tags which addresses is existed already.y"""
        for i, dev in enumerate(self.__devices):
            dev_name = dev.name()
            device_tags = [tag for tag in tags if tag.device.name() == dev_name]
            device_addrs = [tag.address for tag in device_tags
                            if not dev.isAddressExists(tag.address)]
            """If the last tag is multy-register tag (larger than 1 register), 
            we add tail (the required number of addresses to the end)."""
            if device_tags:
                last_tag = device_tags[-1]
                if last_tag.size() > 1:
                    device_addrs.append(last_tag.address + last_tag.size() - 1)
                    """To ensure that a multi-register tag is not split between 
                    ranges, we expand the new range from the beginning."""
                    # if dev.isAddressExists(last_tag.address):
                    #     device_addrs.append(last_tag.address - 1)
                    device_addrs.append(last_tag.address)
            device_addrs = list(set(device_addrs))  # Removing duplicates of addresses from the list

            addresses.append(device_addrs)
            print("addresses: {0}".format(addresses))

        """We find addresses ranges for each device"""
        for device_addrs in addresses:
            range_ = IOServer.__calculateRanges(100, device_addrs)
            ranges.append(range_)

        """Configuring devices by setting addresses ranges"""
        for dev, dev_ranges in zip(self.__devices, ranges):
            if dev_ranges:
                for i, range_ in enumerate(dev_ranges):
                    dev.addRange(range_[0],
                                 range_[1] - range_[0] + 1,
                                 "range{}".format(i))

    def tag(self, name: str) -> Tag:
        """ Returns tag by name """
        res_tag = None
        for tag in self.__tags:
            # print(tag)
            if tag.name == name:
                res_tag = tag
                break

        return res_tag

    def tags(self):
        """ Returns all tags """
        return self.__tags

    def driver(self):
        return self.__drv

    # --- private ---
    @staticmethod
    def __calculateRanges(max_len: int, addresses: list) -> dict:
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

    @staticmethod
    def __regsToValue(regs: [], type_: TagType, bit_number=None):
        if regs is None or type_ is None:
            return None

        if len(regs) < TagTypeSize[type_]:
            return None

        if TagType.INT == type_:
            return regs[0]
        elif TagType.WORD == type_:
            return regs[0]
        elif TagType.UINT == type_:
            return regs[0]
        elif TagType.REAL == type_:
            data_bytes = np.array([regs[0], regs[1]], dtype=np.uint16)
            data_as_float = data_bytes.view(dtype=np.float32)
            return data_as_float[0]
        elif TagType.DWORD == type_:
            data_as_dword = (regs[1] << 16) + regs[0]
            return data_as_dword
        elif TagType.BOOL == type_:
            assert (bit_number is not None)
            output = [int(x) for x in '{:08b}'.format(regs[0])]
            output.reverse()
            # Заполняем старшие биты нулями (пока просто добавляем 16 нулей, потом сделать лучуше)
            output.extend([0 for i in range(16)])
            return bool(output[bit_number])

    @QtCore.pyqtSlot(str, Range)
    def __onDataUpdated(self, dev_name, range_):
        pass
        # print(
        #     "OIServer: onDataUpdated : "
        #     "dev_name={0}, range={1}".format(dev_name, range_))
        for tag in self.__tags:
            address = tag.address
            if range_.isAddressExists(address):
                sz = TagTypeSize[tag.type]
                regs = range_.reristersNum(address, sz)
                if dev_name == tag.device.name():
                    if TagType.BOOL == tag.type:
                        tag.value = IOServer.__regsToValue(regs, tag.type, tag.bit_number)
                    else:
                        tag.value = IOServer.__regsToValue(regs, tag.type, tag.bit_number)
                    tag.quality = range_.quality()
                    tag.time = range_.time()
            # print(tag)

        self.dataChanged.emit()

    @QtCore.pyqtSlot()
    def __onRangeNumberChanged(self):
        for i in range(len(self.__tags)):
            if not self.__drv.isAddressExists(self.__tags[i].address):
                self.__tags[i].quality = QualityEnum.NOT_CONFIGURED


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    conf = create_config(FormatName.JSON, "conf.json")
    if conf is None:
        print("No config")

    io = IOServer(conf=conf)

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))
