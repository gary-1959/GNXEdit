# Copyright (C) 2024 gary-1959

from __future__ import annotations

from .whammyface import WhammyFace
#from ampfacetaskmenu import ampFaceTaskMenuFactory

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface

DOM_XML = """
<ui language='c++'>
    <widget class='WhammyFace' name='whammyface'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>1000</width>
                <height>140</height>
            </rect>
        </property>
        <property name='whammyType'>
            <number>0</number>
        </property>
    </widget>
</ui>
"""

class WhammyFacePlugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()

    def createWidget(self, parent):
        t = WhammyFace(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'whammyface'

    def initialize(self, form_editor):
        pass

    def isContainer(self):
        return False

    def isInitialized(self):
        return True

    def name(self):
        return 'WhammyFace'

    def toolTip(self):
        return 'WhammyFace Example'

    def whatsThis(self):
        return self.toolTip()
