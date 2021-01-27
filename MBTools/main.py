# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(sys.path[0], "../"))

from PyQt5 import QtWidgets


import MBTools.oiserver.tools.OIServerViewer.OIServerViewer as oiv
from MBTools.oiserver.OIServer import IOServer


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    cur_path = os.path.dirname(__file__)
    new_path = os.path.relpath("../config/qss.css", cur_path)
    print(new_path)
    print("sys path:")
    for path in sys.path:
        print("\t" + path)


    io = IOServer()

    oiviewer = oiv.OIServerViewer()
    oiviewer.setOiServer(io)

    oiviewer.show()

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))

# input = 0x3333
# output = [int(x) for x in '{:08b}'.format(input)]
# print(output)
