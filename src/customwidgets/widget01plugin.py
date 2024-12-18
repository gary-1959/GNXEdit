# Copyright (C) 2024 gary-1959

from __future__ import annotations

from widget01 import Widget01
#from widget01taskmenu import Widget01TaskMenuFactory

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface


DOM_XML = """
<ui language='c++'>
    <widget class='Widget01' name='widget01'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>100</width>
                <height>120</height>
            </rect>
        </property>
    </widget>
</ui>
"""

class Widget01Plugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()

    def createWidget(self, parent):
        t = Widget01(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'widget01'

    def initialize(self, form_editor):
        pass

    def isContainer(self):
        return False

    def isInitialized(self):
        return True

    def name(self):
        return 'Widget01'

    def toolTip(self):
        return 'Widget01 Example'

    def whatsThis(self):
        return self.toolTip()
