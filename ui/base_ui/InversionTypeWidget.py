# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\InversionTypeWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(702, 210)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.stackedWidget = QtWidgets.QStackedWidget(Form)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.stackedWidget.addWidget(self.page_2)
        self.gridLayout_2.addWidget(self.stackedWidget, 0, 1, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.groupBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.type_1D_Btn = QtWidgets.QPushButton(self.groupBox)
        self.type_1D_Btn.setObjectName("type_1D_Btn")
        self.gridLayout.addWidget(self.type_1D_Btn, 0, 0, 1, 1)
        self.type_2D_Btn = QtWidgets.QPushButton(self.groupBox)
        self.type_2D_Btn.setObjectName("type_2D_Btn")
        self.gridLayout.addWidget(self.type_2D_Btn, 1, 0, 1, 1)
        self.type_3D_Btn = QtWidgets.QPushButton(self.groupBox)
        self.type_3D_Btn.setObjectName("type_3D_Btn")
        self.gridLayout.addWidget(self.type_3D_Btn, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Type"))
        self.type_1D_Btn.setText(_translate("Form", "1D"))
        self.type_2D_Btn.setText(_translate("Form", "2D"))
        self.type_3D_Btn.setText(_translate("Form", "3D"))
