# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout

#from widget01 import Widget01
#from customwidgets.styledial import StyleDial
#from customwidgets.ampface import AmpFace
#from customwidgets.cabface import CabFace
#fromcustomwidgets. warpface import WarpFace
#from customwidgets.wahface import WahFace
#from customwidgets.compressorface import CompressorFace
#from customwidgets.whammyface import WhammyFace
#from customwidgets.gateface import GateFace
#from customwidgets.modface import ModFace
#from customwidgets.delayface import DelayFace
#from customwidgets.reverbface import ReverbFace
#from customwidgets.expface import ExpFace
#from customwidgets.lfoface import LFOFace
from customwidgets.searchresults import SearchResults

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #window = TicTacToe()
    #widget = Widget01()
    widget = QWidget()
    widget.setGeometry(0, 0, 1600, 440)
    layout = QVBoxLayout()
    widget.setLayout(layout)

    d1 = SearchResults()
    layout.addWidget(d1)   
    d1.setGeometry(0, 0, 1000, 180)
    d1.setMaximumWidth(1000)
    d1.setMaximumHeight(240)

    widget.show()
    sys.exit(app.exec())
