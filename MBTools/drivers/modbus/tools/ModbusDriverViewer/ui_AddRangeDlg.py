# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_AddRangeDlg.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AddRangeDlg(object):
    def setupUi(self, AddRangeDlg):
        AddRangeDlg.setObjectName("AddRangeDlg")
        AddRangeDlg.resize(268, 154)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddRangeDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.leName = QtWidgets.QLineEdit(AddRangeDlg)
        self.leName.setObjectName("leName")
        self.gridLayout.addWidget(self.leName, 0, 1, 1, 1)
        self.lbNameTitle = QtWidgets.QLabel(AddRangeDlg)
        self.lbNameTitle.setWhatsThis("")
        self.lbNameTitle.setObjectName("lbNameTitle")
        self.gridLayout.addWidget(self.lbNameTitle, 0, 0, 1, 1)
        self.lbIpTitle = QtWidgets.QLabel(AddRangeDlg)
        self.lbIpTitle.setWhatsThis("")
        self.lbIpTitle.setObjectName("lbIpTitle")
        self.gridLayout.addWidget(self.lbIpTitle, 1, 0, 1, 1)
        self.lbPortTiltle = QtWidgets.QLabel(AddRangeDlg)
        self.lbPortTiltle.setWhatsThis("")
        self.lbPortTiltle.setObjectName("lbPortTiltle")
        self.gridLayout.addWidget(self.lbPortTiltle, 2, 0, 1, 1)
        self.leFirstAddress = QtWidgets.QLineEdit(AddRangeDlg)
        self.leFirstAddress.setObjectName("leFirstAddress")
        self.gridLayout.addWidget(self.leFirstAddress, 1, 1, 1, 1)
        self.leQualtity = QtWidgets.QLineEdit(AddRangeDlg)
        self.leQualtity.setMaximumSize(QtCore.QSize(100, 16777215))
        self.leQualtity.setObjectName("leQualtity")
        self.gridLayout.addWidget(self.leQualtity, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddRangeDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AddRangeDlg)
        self.buttonBox.accepted.connect(AddRangeDlg.accept)
        self.buttonBox.rejected.connect(AddRangeDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(AddRangeDlg)

    def retranslateUi(self, AddRangeDlg):
        _translate = QtCore.QCoreApplication.translate
        AddRangeDlg.setWindowTitle(_translate("AddRangeDlg", "New Range Dialog"))
        self.lbNameTitle.setText(_translate("AddRangeDlg", "Name:"))
        self.lbIpTitle.setText(_translate("AddRangeDlg", "Address:"))
        self.lbPortTiltle.setText(_translate("AddRangeDlg", "Number:"))
