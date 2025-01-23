# Copyright (C) 2024 gary-1959

from __future__ import annotations

from .searchresults import SearchResults

from PySide6.QtGui import QIcon
from PySide6.QtDesigner import QDesignerCustomWidgetInterface

DOM_XML = """
<ui language='c++'>
    <widget class='SearchResults' name='searchresults'>
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

class SearchResultsPlugin(QDesignerCustomWidgetInterface):
    def __init__(self):
        super().__init__()

    def createWidget(self, parent):
        t = SearchResults(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return ''

    def icon(self):
        return QIcon()

    def includeFile(self):
        return 'searchresults'

    def initialize(self, form_editor):
        pass

    def isContainer(self):
        return False

    def isInitialized(self):
        return True

    def name(self):
        return 'SearchResults'

    def toolTip(self):
        return 'SearchResults Example'

    def whatsThis(self):
        return self.toolTip()
