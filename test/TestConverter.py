import numpy as np

from MBTools.oiserver.OIServer import IOServer
from MBTools.oiserver.constants import TagType, TagTypeSize


data_bytes = np.array([0, 16224], dtype=np.uint16)
data_as_float = data_bytes.view(dtype=np.float32)
print(data_as_float)

# regs = [0x00, 0x3f60]
# regs = [16224, 0x0]
regs = [0, 16224]
ret = IOServer.__regsToValue(regs, TagType.REAL)
print(ret)
