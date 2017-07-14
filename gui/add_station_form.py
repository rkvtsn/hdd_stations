#!/usr/bin/env python
# coding=utf-8
import re
'''    
if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", x.lower()):
'''
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import SIGNAL

from gui.design.add_station_dialog import Ui_AddStationDialog


class AddStationForm(QtGui.QDialog, Ui_AddStationDialog):

    def __init__(self, parent=None):
        super(AddStationForm, self).__init__(parent)
        self.setupUi(self)
        self.btn_cancel.clicked.connect(self.close)
        self.btn_ok.clicked.connect(self.add_station)

    def add_station(self):
        self.accept()
        pass
