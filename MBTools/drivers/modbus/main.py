# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets

from MBTools.utilites.Messages import DummyMessage


def main(argv):
    app = QtWidgets.QApplication(sys.argv)
    msg = DummyMessage()
    msg.show()
    return app.exec()


if "__main__" == __name__:
    sys.exit(main(sys.argv))