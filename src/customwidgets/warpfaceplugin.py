# Copyright (C) 2024 gary-1959

from __future__ import annotations

from .warpface import WarpFace
#from ampfacetaskmenu import ampFaceTaskMenuFactory

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface


DOM_XML = """
<ui language='c++'>
    <widget class='WarpFace' name='warpface'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>280</width>
                <height>280</height>
            </rect>
        </property>
    </widget>
</ui>
"""

class WarpFacePlugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()

    def createWidget(self, parent):
        t = WarpFace(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'warpface'

    def initialize(self, form_editor):
        pass

    def isContainer(self):
        return False

    def isInitialized(self):
        return True

    def name(self):
        return 'WarpFace'

    def toolTip(self):
        return 'WarpFace Example'

    def whatsThis(self):
        return self.toolTip()
