
import pytest

from MBTools.drivers.modbus.ModbusDriver import ModbusCalculator


# ------------ ModbusCalculator --------------


@pytest.mark.parametrize("numbers, expect, max_len", [
    ([199, 33, 104, 25, 1, 10, 46, 150, 122],      [[1, 46],  [104, 199]],              100),
    ([78, 79, 33, 120, 120, 100, 55, 154, 107],    [[33, 120], [154, 154]],             100),
    ([55, 66, 101, 105],                           [[55,  105]],                         100),
    ([199, 50, 104, 25, 0, 10, 46, 150, 122],      [[0, 46], [50, 50], [104, 150], [199, 199]],   50),
    ([1885, 1887, 1887, 100, 150, 199],            [[100, 199], [1885, 1887]],          100),
    ([1885, 1887, 1887],                           [[1885, 1887]],                      100),
    ([1, 100, 101, 102],                           [[1, 100], [101, 102]],                100),
])
def test_split_numbers(numbers, expect, max_len):
    assert ModbusCalculator.split_numbers(numbers, max_len) == expect
