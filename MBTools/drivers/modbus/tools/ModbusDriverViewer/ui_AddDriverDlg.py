# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_AddDriverDlg.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AddDriverDlg(object):
    def setupUi(self, AddDriverDlg):
        AddDriverDlg.setObjectName("AddDriverDlg")
        AddDriverDlg.resize(268, 154)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddDriverDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.leName = QtWidgets.QLineEdit(AddDriverDlg)
        self.leName.setObjectName("leName")
        self.gridLayout.addWidget(self.leName, 0, 1, 1, 1)
        self.lbNameTitle = QtWidgets.QLabel(AddDriverDlg)
        self.lbNameTitle.setObjectName("lbNameTitle")
        self.gridLayout.addWidget(self.lbNameTitle, 0, 0, 1, 1)
        self.lbIpTitle = QtWidgets.QLabel(AddDriverDlg)
        self.lbIpTitle.setObjectName("lbIpTitle")
        self.gridLayout.addWidget(self.lbIpTitle, 1, 0, 1, 1)
        self.lbPortTiltle = QtWidgets.QLabel(AddDriverDlg)
        self.lbPortTiltle.setObjectName("lbPortTiltle")
        self.gridLayout.addWidget(self.lbPortTiltle, 2, 0, 1, 1)
        self.leIp = QtWidgets.QLineEdit(AddDriverDlg)
        self.leIp.setObjectName("leIp")
        self.gridLayout.addWidget(self.leIp, 1, 1, 1, 1)
        self.lePort = QtWidgets.QLineEdit(AddDriverDlg)
        self.lePort.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lePort.setObjectName("lePort")
        self.gridLayout.addWidget(self.lePort, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddDriverDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AddDriverDlg)
        self.buttonBox.accepted.connect(AddDriverDlg.accept)
        self.buttonBox.rejected.connect(AddDriverDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(AddDriverDlg)

    def retranslateUi(self, AddDriverDlg):
        _translate = QtCore.QCoreApplication.translate
        AddDriverDlg.setWindowTitle(_translate("AddDriverDlg", "Dialog"))
        self.lbNameTitle.setText(_translate("AddDriverDlg", "Name"))
        self.lbIpTitle.setText(_translate("AddDriverDlg", "IP"))
        self.lbPortTiltle.setText(_translate("AddDriverDlg", "Port"))
