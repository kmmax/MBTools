# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_Settings.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(253, 156)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lb1 = QtWidgets.QLabel(Dialog)
        self.lb1.setObjectName("lb1")
        self.horizontalLayout.addWidget(self.lb1)
        self.leIpAddr = QtWidgets.QLineEdit(Dialog)
        self.leIpAddr.setObjectName("leIpAddr")
        self.horizontalLayout.addWidget(self.leIpAddr)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lb1_2 = QtWidgets.QLabel(Dialog)
        self.lb1_2.setObjectName("lb1_2")
        self.horizontalLayout_2.addWidget(self.lb1_2)
        self.leIpAddr_2 = QtWidgets.QLineEdit(Dialog)
        self.leIpAddr_2.setObjectName("leIpAddr_2")
        self.horizontalLayout_2.addWidget(self.leIpAddr_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Settings"))
        self.lb1.setText(_translate("Dialog", "IP Address:"))
        self.leIpAddr.setText(_translate("Dialog", "127.0.0.1"))
        self.lb1_2.setText(_translate("Dialog", "Port:"))
        self.leIpAddr_2.setText(_translate("Dialog", "502"))
