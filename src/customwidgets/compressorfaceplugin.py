# Copyright (C) 2024 gary-1959

from __future__ import annotations

from .compressorface import CompressorFace
#from ampfacetaskmenu import ampFaceTaskMenuFactory

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface

DOM_XML = """
<ui language='c++'>
    <widget class='CompressorFace' name='compressorface'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>1000</width>
                <height>140</height>
            </rect>
        </property>
    </widget>
</ui>
"""

class CompressorFacePlugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()

    def createWidget(self, parent):
        t = CompressorFace(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'compressorface'

    def initialize(self, form_editor):
        pass

    def isContainer(self):
        return False

    def isInitialized(self):
        return True

    def name(self):
        return 'CompressorFace'

    def toolTip(self):
        return 'CompressorFace Example'

    def whatsThis(self):
        return self.toolTip()
