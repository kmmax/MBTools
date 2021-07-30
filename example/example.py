# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtWidgets

from MBTools.oiserver.OIServer import IOServer
from MBTools.oiserver.OIServerConfigure import create_config, FormatName
import MBTools.oiserver.tools.OIServerViewer.OIServerViewer as oiv


def main(argv):
    app = QtWidgets.QApplication(sys.argv)

    # Server
    io = IOServer()

    # Server configuration
    conf = create_config(FormatName.JSON, "../MBTools/config/conf.json")
    io.set_config(conf)

    # Server tag viewer
    oiviewer = oiv.OIServerViewer()
    oiviewer.setOiServer(io)
    oiviewer.show()

    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))