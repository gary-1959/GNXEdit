# File: main.py
import sys
import os 
import time
import importlib
from MIDIControl import MIDIControl

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QFile, QIODevice

import settings
from exceptions import GNXError
from menu import MenuHandler
from statusbar import StatusControl
from treeview import TreeHandler

from GNX1 import GNX1

def showAlert(e):
    clicked = e.alert()

if __name__ == "__main__":

    os.environ["QT_LOGGING_RULES"]='*.debug=false;qt.pysideplugin=false'     # stop pyside custom plugin errors
    print(os.getcwd())
    app = QApplication(sys.argv)

    try:
        settings.get_settings()

        # main window
        ui_file_name = "src/ui/mainwindow.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)

        loader = QUiLoader()
        window = loader.load(ui_file)

        ui_file.close()
        statusHandler = StatusControl(window)
        midicontrol = MIDIControl(window)
        menuHandler = MenuHandler(window = window, midicontrol = midicontrol, gnx = None)
        treeHandler = TreeHandler(window = window, gnx = None)
        gnx = GNX1(ui = window, midicontrol = midicontrol)
        gnx.gnxAlert.connect(showAlert)


        statusHandler.setGNX(gnx)
        menuHandler.setGNX(gnx)
        treeHandler.setGNX(gnx)
        treeHandler.gnxAlert.connect(showAlert)

        if not window:
            print(loader.errorString())
            sys.exit(-1)

        midicontrol.open_ports()    
        window.showMaximized()

    except GNXError as e:
        e.alert()

    except Exception as e:
        e = GNXError(icon = QMessageBox.Critical, title = "GNX Edit Error", text = f"GNX Edit can not continue {e}", buttons = QMessageBox.Ok)
        e.alert()



    sx = app.exec()
    settings.save_settings()
    sys.exit(sx)


