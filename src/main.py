# File: main.py
import sys
import os 
import time
import importlib
from MIDIControl import MIDIControl

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QTabWidget, QWidget, QMenuBar
from PySide6.QtCore import QFile, QIODevice

import settings
from menu import MenuHandler
from GNX1 import GNX1

def closed():
    pass
    settings.save_settings()

if __name__ == "__main__":

    os.environ["QT_LOGGING_RULES"]='*.debug=false;qt.pysideplugin=false'     # stop pyside custom plugin errors
    print(os.getcwd())
    app = QApplication(sys.argv)

    settings.get_settings()

    # main window
    ui_file_name = "src/ui/mainwindow.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)

    loader = QUiLoader()
    window = loader.load(ui_file)
    window.closeEvent.connect(closed)##############

    ui_file.close()
    midicontrol = MIDIControl(window)
    menuHandler = MenuHandler(window, midicontrol)
    GNX1(ui = window, midicontrol = midicontrol)

    if not window:
        print(loader.errorString())
        sys.exit(-1)

    midicontrol.open_ports()    
    window.showMaximized()

    settings.save_settings()
    sys.exit(app.exec())

