# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\ancalle\Documents\FEQinput\sc\searchwindow.ui'
#
# Created: Tue Jul 21 15:00:02 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(257, 151)
        self.searchbutton = QtGui.QPushButton(Dialog)
        self.searchbutton.setGeometry(QtCore.QRect(90, 120, 75, 23))
        self.searchbutton.setObjectName(_fromUtf8("searchbutton"))
        self.cancel = QtGui.QPushButton(Dialog)
        self.cancel.setGeometry(QtCore.QRect(170, 120, 75, 23))
        self.cancel.setObjectName(_fromUtf8("cancel"))
        self.checkBox = QtGui.QCheckBox(Dialog)
        self.checkBox.setGeometry(QtCore.QRect(10, 60, 131, 17))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.searchText = QtGui.QLineEdit(Dialog)
        self.searchText.setGeometry(QtCore.QRect(40, 20, 201, 20))
        self.searchText.setObjectName(_fromUtf8("searchText"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 20, 46, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.blocks = QtGui.QComboBox(Dialog)
        self.blocks.setGeometry(QtCore.QRect(120, 60, 121, 22))
        self.blocks.setObjectName(_fromUtf8("blocks"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.searchbutton.setText(_translate("Dialog", "Search", None))
        self.cancel.setText(_translate("Dialog", "Cancel", None))
        self.checkBox.setText(_translate("Dialog", "search within block", None))
        self.label.setText(_translate("Dialog", "Text:", None))

