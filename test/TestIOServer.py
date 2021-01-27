import sys
import unittest
from MDViewer.oiserver.OIServer import IOServer
from MDViewer.oiserver.constants import TagTypeSize, TagType


class TestCalculator(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_calculateRanges(self):
        max_len = 50
        addresses = [0, 5, 22, 8, 33, 105, 122, 111, 1050, 222, 555]
        res = [[0, 33], [105, 122], [222, 222], [555, 555], [1050, 1050]]
        ret = IOServer.__calculateRanges(max_len, addresses)
        self.assertListEqual(res, ret, "Range=50")

        addresses = [22]
        res = [[22, 22]]
        ret = IOServer.__calculateRanges(max_len, addresses)
        self.assertListEqual(res, ret)

        max_len = 100
        addresses = [0, 5, 22, 8, 33, 105, 122, 111, 1050, 222, 555, 1052]
        res = [[0, 33], [105, 122], [222, 222], [555, 555], [1050, 1052]]
        ret = IOServer.__calculateRanges(max_len, addresses)
        self.assertListEqual(res, ret)

    def test_regsToValue(self):
        regs = None
        type_ = TagType.INT
        ret = IOServer.__regsToValue(regs, type_)
        self.assertEqual(ret, None)

        regs = [10, 20, 30]
        type_ = None
        ret = IOServer.__regsToValue(regs, type_)
        self.assertEqual(ret, None)

        regs = []
        type_ = TagType.INT
        ret = IOServer.__regsToValue(regs, type_)
        self.assertEqual(ret, None)

        regs = [10, 20]
        types = [TagType.INT, TagType.WORD, TagType.UINT, TagType.DWORD]
        rets = [10, 10, 10, 1020]
        for tp, rt in zip(types, rets):
            self.assertEqual(IOServer.__regsToValue(regs, tp), rt)

        regs = [0, 16224]
        types = [TagType.REAL]
        rets = [0.875]
        for tp, rt in zip(types, rets):
            self.assertEqual(IOServer.__regsToValue(regs, tp), rt)


if __name__ == "__main__":
    unittest.main()