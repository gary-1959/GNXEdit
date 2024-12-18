# Copyright (C) 2024 gary-1959

from __future__ import annotations

from .cabface import CabFace
#from cabfacetaskmenu import cabFaceTaskMenuFactory

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface


DOM_XML = """
<ui language='c++'>
    <widget class='CabFace' name='cabface'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>280</width>
                <height>280</height>
            </rect>
        </property>
        <property name='cabStyle'>
            <number>0</number>
        </property>
    </widget>
</ui>
"""

class CabFacePlugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()

    def createWidget(self, parent):
        t = CabFace(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'cabface'

    def initialize(self, form_editor):
        pass

    def isContainer(self):
        return False

    def isInitialized(self):
        return True

    def name(self):
        return 'CabFace'

    def toolTip(self):
        return 'CabFace Example'

    def whatsThis(self):
        return self.toolTip()
