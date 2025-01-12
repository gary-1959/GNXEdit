# statusbar.py
#
# GNXEdit status bar handler
#
# Copyright 2024 gary-1959
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

from PySide6.QtWidgets import QMessageBox

class GNXError(Exception):
    def __init__(self, icon = QMessageBox.NoIcon, title = "GNX Edit Error", text = "An undefine error has occurred", buttons = None, clicked = None):
        super().__init__()

        self.title = title
        self.text = text
        self.buttons = buttons
        self.clicked = clicked
        self.icon = icon

    def alert(self, parent = None):
        match self.icon:
            case QMessageBox.NoIcon:
                f = QMessageBox.information
            case QMessageBox.Information:
                f = QMessageBox.information
            case QMessageBox.Warning:
                f = QMessageBox.warning
            case QMessageBox.Critical:
                f = QMessageBox.critical
            case QMessageBox.Question:
                f = QMessageBox.question
                
        return f(parent, self.title, self.text, self.buttons)
        pass
