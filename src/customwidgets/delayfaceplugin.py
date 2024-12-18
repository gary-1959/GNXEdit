# Copyright (C) 2024 gary-1959

from __future__ import annotations

from .delayface import DelayFace

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface

DOM_XML = """
<ui language='c++'>
    <widget class='DelayFace' name='delayface'>
        <property name='geometry'>
            <rect>
                <x>0</x>
                <y>0</y>
                <width>1000</width>
                <height>240</height>
            </rect>
        </property>
    </widget>
</ui>
"""

class DelayFacePlugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()

    def createWidget(self, parent):
        t = DelayFace(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'delayface'

    def initialize(self, form_editor):
        pass

    def isContainer(self):
        return False

    def isInitialized(self):
        return True

    def name(self):
        return 'DelayFace'

    def toolTip(self):
        return 'DelayFace Example'

    def whatsThis(self):
        return self.toolTip()
