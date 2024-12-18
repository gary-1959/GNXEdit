# Copyright (C) 2024 gary-1959

from __future__ import annotations

from .styledial import StyleDial
#from styledialtaskmenu import StyleDialTaskMenuFactory

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface


DOM_XML = """
<ui language='c++'>
    <widget class='StyleDial' name='styledial'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>100</width>
                <height>100</height>
            </rect>
        </property>
        <property name='dialStyle'>
            <string>blkfac</string>
        </property>
        <property name='startStop'>
            <number>0</number>
        </property>
        <property name='endStop'>
            <number>345</number>
        </property>
        <property name='overallRotation'>
            <number>0</number>
        </property>
    </widget>
</ui>
"""

class StyleDialPlugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()

    def createWidget(self, parent):
        t = StyleDial(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'styledial'

    def initialize(self, form_editor):
        pass

    def isContainer(self):
        return False

    def isInitialized(self):
        return True

    def name(self):
        return 'StyleDial'

    def toolTip(self):
        return 'StyleDial Example'

    def whatsThis(self):
        return self.toolTip()
