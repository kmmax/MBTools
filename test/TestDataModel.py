import sys
import unittest

from MBTools.drivers.modbus.ModbusDriver import DriverCreator, DeviceCreator
from MBTools.oiserver.DataModel import DataModel
from MBTools.oiserver.Tag import Tag, TagType


class TestCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.dev1 = DeviceCreator.create("127.0.0.1", 502, "dev1")
        self.dev2 = DeviceCreator.create("127.0.0.1", 10502, "dev2")
        # self.drv1 = DriverCreator.create("modbus", [self.dev1, self.dev2])
        self.tag1 = Tag(device=self.dev1, name="TAG1", type_=TagType.INT, address=100, comment="tag1 on dev1")
        self.tag2 = Tag(device=self.dev1, name="TAG2", type_=TagType.INT, address=101, comment="tag2 on dev1")
        self.tag3 = Tag(device=self.dev2, name="TAG3", type_=TagType.INT, address=100, comment="tag3 on dev2")
        self.tag_list = [self.tag1, self.tag2, self.tag3]
        self.dev_list = [self.dev1, self.dev2]

    def test_find_by_name(self):
        name = self.dev1.name()
        model = DataModel()
        model.append(self.tag1)

        # device exitsts
        dev = DataModel.find_by_name("dev1", self.dev_list)
        self.assertEqual(name, dev.name())

        # device not exitsts
        dev = DataModel.find_by_name("dev4", self.dev_list)
        self.assertIsNone(dev)

    def test_append(self):
        model = DataModel()
        model.append(self.tag1)
        model.append(self.tag2)
        model.append(self.tag3)
        self.assertIn(self.tag1, model)
        self.assertIn(self.tag2, model)
        self.assertIn(self.tag3, model)

        devices = model.devices()
        self.assertListEqual(devices, self.dev_list)

        tst1 = [id(dev) for dev in devices]
        tst2 = [id(self.dev1), id(self.dev2)]
        self.assertListEqual(tst1, tst2)

    def test_calculateRanges(self):
        pass
        # max_len = 50
        # addresses = [0, 5, 22, 8, 33, 105, 122, 111, 1050, 222, 555]
        # res = [[0, 33], [105, 122], [222, 222], [555, 555], [1050, 1050]]
        # ret = IOServer.__calculateRanges(max_len, addresses)
        # self.assertListEqual(res, ret, "Range=50")
        #
        # addresses = [22]
        # res = [[22, 22]]
        # ret = IOServer.__calculateRanges(max_len, addresses)
        # self.assertListEqual(res, ret)
        #
        # max_len = 100
        # addresses = [0, 5, 22, 8, 33, 105, 122, 111, 1050, 222, 555, 1052]
        # res = [[0, 33], [105, 122], [222, 222], [555, 555], [1050, 1052]]
        # ret = IOServer.__calculateRanges(max_len, addresses)
        # self.assertListEqual(res, ret)


if __name__ == "__main__":
    unittest.main()
