# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_station_dialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_AddStationDialog(object):
    def setupUi(self, AddStationDialog):
        AddStationDialog.setObjectName(_fromUtf8("AddStationDialog"))
        AddStationDialog.resize(402, 408)
        self.frame = QtGui.QFrame(AddStationDialog)
        self.frame.setGeometry(QtCore.QRect(10, 10, 381, 391))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout = QtGui.QGridLayout(self.frame)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edit_gate = QtGui.QLineEdit(self.frame)
        self.edit_gate.setObjectName(_fromUtf8("edit_gate"))
        self.gridLayout.addWidget(self.edit_gate, 11, 0, 1, 3)
        self.edit_mask = QtGui.QLineEdit(self.frame)
        self.edit_mask.setObjectName(_fromUtf8("edit_mask"))
        self.gridLayout.addWidget(self.edit_mask, 5, 0, 1, 3)
        self.btn_ok = QtGui.QPushButton(self.frame)
        self.btn_ok.setObjectName(_fromUtf8("btn_ok"))
        self.gridLayout.addWidget(self.btn_ok, 14, 0, 1, 1)
        self.edit_ip = QtGui.QLineEdit(self.frame)
        self.edit_ip.setObjectName(_fromUtf8("edit_ip"))
        self.gridLayout.addWidget(self.edit_ip, 7, 0, 1, 3)
        self.edit_subnet = QtGui.QLineEdit(self.frame)
        self.edit_subnet.setObjectName(_fromUtf8("edit_subnet"))
        self.gridLayout.addWidget(self.edit_subnet, 9, 0, 1, 3)
        self.btn_cancel = QtGui.QPushButton(self.frame)
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.gridLayout.addWidget(self.btn_cancel, 14, 2, 1, 1)
        self.edit_mac = QtGui.QLineEdit(self.frame)
        self.edit_mac.setObjectName(_fromUtf8("edit_mac"))
        self.gridLayout.addWidget(self.edit_mac, 3, 0, 1, 3)
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.frame)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 10, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.frame)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 8, 0, 1, 1)
        self.edit_station_name = QtGui.QLineEdit(self.frame)
        self.edit_station_name.setMaxLength(255)
        self.edit_station_name.setPlaceholderText(_fromUtf8(""))
        self.edit_station_name.setObjectName(_fromUtf8("edit_station_name"))
        self.gridLayout.addWidget(self.edit_station_name, 1, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 14, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem1, 13, 0, 1, 3)

        self.retranslateUi(AddStationDialog)
        QtCore.QMetaObject.connectSlotsByName(AddStationDialog)
        AddStationDialog.setTabOrder(self.edit_station_name, self.edit_mac)
        AddStationDialog.setTabOrder(self.edit_mac, self.edit_mask)
        AddStationDialog.setTabOrder(self.edit_mask, self.edit_ip)
        AddStationDialog.setTabOrder(self.edit_ip, self.edit_subnet)
        AddStationDialog.setTabOrder(self.edit_subnet, self.edit_gate)
        AddStationDialog.setTabOrder(self.edit_gate, self.btn_ok)
        AddStationDialog.setTabOrder(self.btn_ok, self.btn_cancel)

    def retranslateUi(self, AddStationDialog):
        AddStationDialog.setWindowTitle(_translate("AddStationDialog", "Добавление бездисковой станции", None))
        self.edit_gate.setInputMask(_translate("AddStationDialog", "999.999.999.999; ", None))
        self.edit_gate.setPlaceholderText(_translate("AddStationDialog", "XXX.XXX.XXX.XXX", None))
        self.edit_mask.setInputMask(_translate("AddStationDialog", "999.999.999.999; ", None))
        self.edit_mask.setPlaceholderText(_translate("AddStationDialog", "XXX.XXX.XXX.XXX", None))
        self.btn_ok.setText(_translate("AddStationDialog", "Начать настройку", None))
        self.edit_ip.setInputMask(_translate("AddStationDialog", "999.999.999.999; ", None))
        self.edit_ip.setPlaceholderText(_translate("AddStationDialog", "XXX.XXX.XXX.XXX", None))
        self.edit_subnet.setInputMask(_translate("AddStationDialog", "999.999.999.999; ", None))
        self.edit_subnet.setPlaceholderText(_translate("AddStationDialog", "XXX.XXX.XXX.XXX", None))
        self.btn_cancel.setText(_translate("AddStationDialog", "Отмена", None))
        self.edit_mac.setInputMask(_translate("AddStationDialog", "XX-XX-XX-XX-XX-XX; ", None))
        self.edit_mac.setPlaceholderText(_translate("AddStationDialog", "FF:FF.FF:FF.FF:FF", None))
        self.label_4.setText(_translate("AddStationDialog", "IP-адрес клиентской станции", None))
        self.label_2.setText(_translate("AddStationDialog", "MAC-адрес", None))
        self.label.setText(_translate("AddStationDialog", "Наименование логической станции", None))
        self.label_3.setText(_translate("AddStationDialog", "Маска подсети", None))
        self.label_6.setText(_translate("AddStationDialog", "Широковещательный адрес", None))
        self.label_7.setText(_translate("AddStationDialog", "Адрес подсети", None))

