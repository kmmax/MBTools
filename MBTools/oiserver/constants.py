from enum import Enum


# Supported tag types
class TagType(Enum):
    UINT = 1,
    INT = 2,
    REAL = 3,
    WORD = 4,
    DWORD = 5,
    BOOL = 6


# Str:Type association
TagTypeFromStr = {
    "UINT": TagType.UINT,
    "INT": TagType.INT,
    "REAL": TagType.REAL,
    "WORD": TagType.WORD,
    "DWORD": TagType.DWORD,
    "BOOL": TagType.BOOL
}

# Type:Str association
StrFromTagType = {v: k for k, v in TagTypeFromStr.items()}


# Tag size types in 16 bit registers
TagTypeSize = {
    TagType.UINT: 1,
    TagType.INT: 1,
    TagType.REAL: 2,
    TagType.WORD: 1,
    TagType.DWORD: 2,
    TagType.BOOL: 1
}


print(TagType["INT"], type(TagType["INT"]))
my_enum = eval('TagType.UINT')
print(my_enum, type(my_enum))