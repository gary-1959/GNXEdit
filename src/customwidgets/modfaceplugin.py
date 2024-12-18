# Copyright (C) 2024 gary-1959

from __future__ import annotations

from .modface import ModFace
#from ampfacetaskmenu import ampFaceTaskMenuFactory

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface

DOM_XML = """
<ui language='c++'>
    <widget class='ModFace' name='modface'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>1000</width>
                <height>240</height>
            </rect>
        </property>
        <property name='modType'>
            <number>0</number>
        </property>
    </widget>
</ui>
"""

class ModFacePlugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()

    def createWidget(self, parent):
        t = ModFace(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'modface'

    def initialize(self, form_editor):
        pass

    def isContainer(self):
        return False

    def isInitialized(self):
        return True

    def name(self):
        return 'ModFace'

    def toolTip(self):
        return 'ModFace Example'

    def whatsThis(self):
        return self.toolTip()
