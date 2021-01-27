from PyQt5 import QtCore
from PyQt5 import QtWidgets as qtw


class ContextMenuWidget(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ContextMenuWidget')

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.menu = qtw.QMenu(self)
        action1 = self.menu.addAction('Say: "Hello!"')
        action2 = self.menu.addAction('Say: "Hello!"')
        action3 = self.menu.addAction('Say: "Hello!"')
        action1.triggered.connect(lambda: qtw.QMessageBox.information(self, 'Info', 'Hello!'))
        action2.triggered.connect(lambda: qtw.QMessageBox.information(self, 'Info', 'Hello!'))
        action3.triggered.connect(lambda: qtw.QMessageBox.information(self, 'Info', 'Hello!'))

    def show_context_menu(self, point):
        self.menu.exec(self.mapToGlobal(point))


if __name__ == "__main__":
    app = qtw.QApplication([])

    root = ContextMenuWidget()
    root.resize(400, 400)
    root.show()

    app.exec_()