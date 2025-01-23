# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
import os

#from .tictactoe.tictactoeplugin import TicTacToePlugin
#from .widget01plugin import Widget01Plugin
#from customwidgets.searchresultsplugin import SearchResultsPlugin
from customwidgets.styledialplugin import StyleDialPlugin
from customwidgets.ampfaceplugin import AmpFacePlugin
from customwidgets.cabfaceplugin import CabFacePlugin
from customwidgets.warpfaceplugin import WarpFacePlugin
from customwidgets.pickupfaceplugin import PickupFacePlugin
from customwidgets.wahfaceplugin import WahFacePlugin
from customwidgets.compressorfaceplugin import CompressorFacePlugin
from customwidgets.whammyfaceplugin import WhammyFacePlugin
from customwidgets.gatefaceplugin import GateFacePlugin
from customwidgets.modfaceplugin import ModFacePlugin
from customwidgets.delayfaceplugin import DelayFacePlugin
from customwidgets.reverbfaceplugin import ReverbFacePlugin
from customwidgets.expfaceplugin import ExpFacePlugin
from customwidgets.lfofaceplugin import LFOFacePlugin

from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection

# Set PYSIDE_DESIGNER_PLUGINS to point to this directory and load the plugin

if __name__ == '__main__' or True:

    #QPyDesignerCustomWidgetCollection.addCustomWidget(TicTacToePlugin())
    #QPyDesignerCustomWidgetCollection.addCustomWidget(Widget01Plugin())
    #QPyDesignerCustomWidgetCollection.addCustomWidget(SearchResultsPlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(StyleDialPlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(AmpFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(CabFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(WarpFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(PickupFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(WahFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(CompressorFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(WhammyFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(GateFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(ModFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(DelayFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(ReverbFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(ExpFacePlugin())
    QPyDesignerCustomWidgetCollection.addCustomWidget(LFOFacePlugin())
