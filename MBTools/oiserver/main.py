# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets

from MBTools.utilites.Messages import DummyMessage
# from .OIServer import IOServer
from MBTools.oiserver.OIServer import IOServer
from MBTools.oiserver.Tag import Tag, TagType
# from MBTools.jsonserver.JsonServer import JsonServer


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    tag1 = Tag(name="CM", type_=TagType.UINT, comment="Command", address=10)
    tag2 = Tag(name="VL", type_=TagType.REAL, comment="Current value", address=111)
    tag3 = Tag(name="ST1", type_=TagType.UINT, comment="State", address=112)
    tags = list([tag1, tag2, tag3])
    io = IOServer()
    io.add_tags(tags)
    # json = JsonServer(io)
    # json.start()

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))
