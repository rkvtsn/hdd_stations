#!/usr/bin/env python
# coding=utf-8
import logging

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import SIGNAL

from gui.design.main_window import Ui_MainWindow
from gui.add_station_form import AddStationForm

class MainForm(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.setupUi(self)

        self.btn_create.clicked.connect(self.show_add_station_dialog)

        self.icon_delete = QtGui.QIcon("gui/design/images/red_cross.png")
        self.refresh()

    def show_add_station_dialog(self):
        form = AddStationForm()
        if form.exec_():
            print(1)
        else:
            print(2)

        return

    def refresh(self):
        self.stations = self.get_stations()
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        for s_name, s_status in self.stations.items():
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            cell = QtGui.QTableWidgetItem(s_name)
            params = (0, 0, 0) if s_status else (150,150,150)
            cell.setForeground(QtGui.QColor.fromRgb(*params))
            self.tableWidget.setItem(rowPosition, 0, cell)
            btn = QtGui.QPushButton(self.tableWidget)
            btn.setIcon(self.icon_delete)
            btn.id = s_name
            btn.setMaximumWidth(30)
            btn.clicked.connect(self.delete)
            self.tableWidget.setCellWidget(rowPosition, 1, btn)

    def delete(self):
        btn = self.sender()
        # TODO логика удаления станции
        # Удаление станции из таблицы
        self.stations.pop(btn.id, None)
        # Обновление GUI
        self.refresh()


    def get_stations(self):
        stations = {}
        with open('tgtadm_list.txt', 'r') as fp:
            cmd_result = fp.read()
        targets = list(filter(bool, cmd_result.split('#')))

        return stations




    def on_close(self):
        logging.info(u"Application closed")

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self,
                                           u'Уведомление',
                                           u"Уверены, что желаете выйти?",
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Yes:
            self.on_close()
            event.accept()
        else:
            event.ignore()
