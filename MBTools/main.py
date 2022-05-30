# -*- coding: utf-8 -*-
# -----------------------------------------------------------
# Main module
#
# (C) 2021 Maxim Kozyakov
# Released under GNU Public License (MIT)
# email kmmax@yandex.ru
# -----------------------------------------------------------

import os
import sys
sys.path.append(os.path.join(sys.path[0], "../"))

from PyQt5 import QtWidgets

import MBTools.oiserver.tools.OIServerViewer.OIServerViewer as oiv
from MBTools.oiserver.OIServer import IOServer
from MBTools.oiserver.OIServerConfigure import JsonConfigure, create_config, FormatName


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    cur_path = os.path.dirname(__file__)
    new_path = os.path.relpath("../config/qss.css", cur_path)
    print(new_path)
    print("sys path:")
    for path in sys.path:
        print("\t" + path)

    io = IOServer()
    # conf = create_config(FormatName.JSON, "config/conf.json")
    conf = create_config(FormatName.JSON, "config/conf.json")
    io.set_config(conf)

    oiviewer = oiv.OIServerViewer()
    oiviewer.setOiServer(io)

    oiviewer.show()

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))

