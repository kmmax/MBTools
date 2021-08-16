import sys
import unittest

from MBTools.drivers.modbus.ModbusDriver import DriverCreator, DeviceCreator
from MBTools.oiserver.DataModel import DataModel
from MBTools.oiserver.Tag import Tag, TagType


class TestCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.model = DataModel()

        self.dev1 = DeviceCreator.create("127.0.0.1", 502, "dev1")
        self.dev2 = DeviceCreator.create("127.0.0.1", 10502, "dev2")
        # self.drv1 = DriverCreator.create("modbus", [self.dev1, self.dev2])
        self.tag1 = Tag(device=self.dev1, name="TAG1", type_=TagType.INT, address=100, comment="tag1 on dev1")
        self.tag2 = Tag(device=self.dev1, name="TAG2", type_=TagType.INT, address=101, comment="tag2 on dev1")
        self.tag3 = Tag(device=self.dev2, name="TAG3", type_=TagType.INT, address=100, comment="tag3 on dev2")
        self.tag4 = Tag(device=self.dev2, name="TAG4", type_=TagType.INT, address=100, comment="tag3 on dev2")

    def tearDown(self) -> None:
        self.model.clear()

    # @unittest.skip
    def test_devices(self):
        self.model.add(self.tag1)    # add dev1
        self.model.add(self.tag2)    # add dev2
        self.model.add(self.tag3)    # add dev3
        # print(model)

        devices = self.model.devices()

        # checking number of devices
        self.assertEqual(2, len(devices))

        # checking devices itself
        dev_list = [self.dev1, self.dev2]
        for dev in dev_list:
            self.assertIn(dev, devices)

    def test_tags(self):
        self.model.add(self.tag1)
        self.model.add(self.tag2)
        self.model.add(self.tag3)

        tags = self.model.tags()
        self.assertIn(self.tag1, tags)
        self.assertIn(self.tag2, tags)
        self.assertIn(self.tag3, tags)
        self.assertNotIn(self.tag4, tags)

    # @unittest.skip
    def test_find_by_name(self):
        name = self.dev1.name()
        self.model.add(self.tag1)

        # device exitsts
        dev_list = [self.dev1, self.dev2]
        dev = DataModel.find_by_name("dev1", dev_list)
        self.assertEqual(name, dev.name())

        # device not exitsts
        dev = DataModel.find_by_name("dev4", dev_list)
        self.assertIsNone(dev)

    # @unittest.skip
    def test_add(self):
        self.model.add(self.tag1)
        self.model.add(self.tag2)
        self.model.add(self.tag3)
        # print(model)
        self.assertIn(self.tag1, self.model)
        self.assertIn(self.tag2, self.model)
        self.assertIn(self.tag3, self.model)

        devices = self.model.devices()
        self.assertIn(self.dev1, devices)
        self.assertIn(self.dev2, devices)

    # @unittest.skip("dummy")
    def test_discard(self):
        self.model.add(self.tag1)        # add dev1
        self.model.add(self.tag2)        # add dev1
        self.model.add(self.tag3)        # add dev2
        self.model.discard(self.tag3)    # remove dev1
        # При удалении тега удаляется и связанный с ним device (если он больше никем не используется)

        self.assertIn(self.tag1, self.model)         # есть tag2
        self.assertIn(self.tag2, self.model)         # есть tag3
        self.assertNotIn(self.tag3, self.model)      # нет tag1
        self.assertEqual(2, len(self.model.tags()))  # осталось 2 элемента

        devices = self.model.devices()
        self.assertIn(self.dev1, devices)
        self.assertNotIn(self.dev2, devices)

    # @unittest.skip
    def test_tags_by_device(self):
        self.model.add(self.tag1)        # add dev1
        self.model.add(self.tag2)        # add dev1
        self.model.add(self.tag3)        # add dev2

        # в списке tag1, tag2 (привязанные к dev1), отсуствует tag3 (привязан к dev2)
        tags = self.model.tags_by_device(self.dev1)
        self.assertIn(self.tag1, tags)
        self.assertIn(self.tag2, tags)
        self.assertNotIn(self.tag3, tags)

    def test_find_tag_by_name(self):
        pass


if __name__ == "__main__":
    unittest.main()
