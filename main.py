#!/usr/local/bin/python3.6
# coding=utf-8
import sys, logging

from PyQt4 import QtGui, QtCore

from gui.main_form import MainForm


def run():
    logging.info(u'"РП" запущено')
    application = QtGui.QApplication(sys.argv)
    translator = QtCore.QTranslator(application)
    locale = QtCore.QLocale.system().name()
    path = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)
    translator.load(u"qt_%s" % locale, path)
    application.installTranslator(translator)

    window = MainForm()
    window.show()

    sys.exit(application.exec_())

if __name__ == "__main__":
    run()
