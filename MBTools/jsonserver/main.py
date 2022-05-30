from JsonServer import JsonServer
from MBTools.oiserver.Tag import Tag, TagType
from MBTools.oiserver.OIServer import IOServer


def main():
    tag1 = Tag(name="CM", type_=TagType.UINT, comment="Command", address=10)
    tag2 = Tag(name="VL", type_=TagType.REAL, comment="Current value", address=111)
    tag3 = Tag(name="ST", type_=TagType.UINT, comment="State", address=112)
    tags = list([tag1, tag2, tag3])
    io = IOServer()
    io.add_tags(tags)

    srv = JsonServer(io)
    # srv.setIoServer(io)
    srv.start()


if __name__ == "__main__":
    main()
