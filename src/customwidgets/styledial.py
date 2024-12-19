# styledial.py
#
# GNX Edit Pot widget for Digitech GNX1
#
# Copyright 2024 gary-1959
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PySide6.QtWidgets import QDial, QWidget, QLabel, QToolTip
from PySide6.QtCore import Qt, QRect, QPointF, Property, Slot
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics, QImage, QCursor
import math
import os

from .cache import cache_image

class StyleDial(QDial):

          
    def __init__(self, parent = None, style = None):
        super().__init__(parent)

        self.parent = parent
        self.setObjectName(u"styledial")
        self.setSingleStep(1)
        self.setPageStep(1)
        self.setCursor(Qt.PointingHandCursor)
        
        self.label = QLabel(self)
        self.dial = self

        self.setStartStop(0)        # angle of start stop (degrees)
        self.setEndStop(300)        # angle of end stop (degrees)
        self.setMaximumUnit(99)     # max value in units
        self.setMinimumUnit(0)      # min value in units
        self.setUnitPrefix("")
        self.setUnitSuffix("")
        self.setUnitsScale(None)    # tooltip scale 
        self.setToolTipFormat("0.0f")   # number format in tooltip
        self.setDialMinimum(1)      # minimum number on dial
        self.setDialMaximum(10)     # maximum number on dial
        self.setDialStep(1)         # step number on dial

        self.setOverallRotation(0) # rotation of knob and scale (degrees)
        self.setImagePath(os.path.join(os.path.dirname(__file__), "images/dial"))

        self.setDrawStyle(1)
        self.setMarkerColor(Qt.lightGray)
        self.setTicks(False)
        self.setMarks(None)

        self.setDialStyle(style)

        self.valueChanged.connect(self.toolValue)

    # call the appropriate drawing routine
    def paintEvent(self, event):
        # paint background image
        match self.drawStyle:
            case 1:
                fn = self.drawStyle1
            case 1:
                fn = self.drawStyle2
            case _:
                fn = self.drawStyle2
        
        fn(event = event)

    def dialNumbers(self, painter, r, fontname = "Arial", fwd = True, aligned = False):

        if self._dialStep == 0:
            return
        
        painter.save()
        if self.marks:
            steps = len(self.marks) - 1
        else:
            if self._dialStep != 0 and (self._dialMaximum != self._dialMinimum):
                steps = (self._dialMaximum - self._dialMinimum)
            else:
                steps = 10

        if self.ticks:
            anginc = ((self._endStop - self._startStop) / steps) * self._dialStep    
        else:
            anginc = ((self._endStop - self._startStop) / steps)  

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(self.markerColor)
        painter.setPen(pen)
        font = QFont(fontname)

        if self.marks:
            n = 0
        else:
            n = self._dialMinimum

        if aligned or self.ticks:
            angle = self._overallRotation + self._startStop
            painter.rotate(angle)

            text_height = r / 2.8
            numy = r - (text_height * 0.18)
            font.setPixelSize(text_height)
            painter.setFont(font)
            font_metrics = QFontMetrics(font)

            while n <= (self._dialMaximum if self.marks == None else steps):      # fwd = 1 - 10
                text_width = font_metrics.horizontalAdvance(str(n))

                # aligned numbers (radial) or ticks
                # sequence is :translate to 12 o'clock, add number, translate back, rotate, continue
                # get ratio between current value and maximum to calculate angle
                painter.translate(0, - numy)

                if self.ticks:
                        pen.setWidth(1)
                        pen.setColor(self.markerColor)
                        painter.setPen(pen)
                        painter.drawLine(0, 0, 0, text_height - 4)
                else:
                    m = str(abs(n)) if self.marks == None else str(self.marks[n])
                    painter.drawText(QRect(-text_width, 0, 2 * text_width, text_height), Qt.AlignCenter | Qt.AlignBottom, m)
                
                painter.translate(0, numy)
                painter.rotate(anginc if fwd else -anginc)

                n += (self._dialStep if self.marks == None else 1)
        else:
            angle =  self._overallRotation + self._startStop
            text_height = r / 2.8
            numy = r - (text_height * 0.5)
            font.setPixelSize(text_height)
            painter.setFont(font)
            font_metrics = QFontMetrics(font)

            while n <= (self._dialMaximum if self.marks == None else steps):      # fwd = 1 - 10
                text_width = font_metrics.horizontalAdvance(str(n))

                # non-aligned numbers (vertical)
                # sequence is: translate to 12 o'clock, rotate, add number, translate back, continue
                # get ratio between current value and maximum to calculate angle
                rads = math.radians(angle)
                dx = numy * math.sin(rads)
                dy = numy * math.cos(rads)

                painter.translate( dx, - dy)
                m = str(abs(n)) if self.marks == None else str(self.marks[n])
                painter.drawText(QRect(-text_width, -text_height, 2 * text_width, 2 * text_height), Qt.AlignCenter | Qt.AlignCenter, m)
                painter.translate(-dx, dy)
                angle += anginc if fwd else -anginc
                n += (self._dialStep if self.marks == None else 1)

        painter.restore()
        #painter.rotate(anginc * n)              # unwind number-adding rotation

    # marks move with dial
    def drawStyle1(self, event = None):

        painter = QPainter(self)

        # So that we can use the background color
        painter.setBackgroundMode(Qt.BGMode.TransparentMode)

        # Smooth out the circle
        painter.setRenderHint(QPainter.Antialiasing)
        img_base = cache_image(f"{self._dialStyle}-knob.png", os.path.join(os.path.dirname(__file__), self.imagePath, f"{self._dialStyle}-knob.png"))

        w = self.width()
        h = self.height()
        painter.drawImage(QRect(0, 0, w, h), img_base)
        
        # No border
        painter.setPen(QPen(Qt.NoPen))

        # Radius of knob  circle
        r = self.height() / 2.0

        # translate to middle of knob
        painter.translate(r, r)
        painter.rotate(self._overallRotation + self._startStop)

        kcr = r * 0.4         # knob center radius
        
        # centre knob outline

        pwidth = r / 20
        prad = kcr + pwidth / 2

        painter.setBrush(Qt.NoBrush)
        
        pen = QPen(Qt.black)
        pen.setWidth(pwidth)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawEllipse(QPointF(0, 0), prad, prad)

        # everything below here gets rotated with dial
        minval = self.minimum()
        maxval = self.maximum()
        val = self.value()
        ratio = (val - minval) / (maxval - minval)
        angle = ratio * (self._endStop - self._startStop)
        painter.rotate(angle)
        self.dialNumbers(painter, r, fwd = False, aligned = True)

        # flutes & knurls

        pwidth = pwidth * 2
        prad = kcr + pwidth / 2

        pen.setWidth(pwidth)
        c = 2 * math.pi * prad          # length of circumference
        flutes = 10                     # number of flutes
        fratio = 0.5                    # ratio of flutes to knurls(?)
        flen = fratio * c / flutes
        klen = (1 - fratio) * c / flutes
        pen.setDashPattern([(klen / pwidth), (flen / pwidth)])
        painter.setPen(pen)
        painter.drawEllipse(QPointF(0, 0), prad, prad)

        painter.rotate(-angle)                  # unwind value rotation
        painter.rotate(-self._overallRotation)   # unwind overall rotation

    # marks fixed around dial
    def drawStyle2(self, event = None):
        
        img_base = cache_image(f"{self._dialStyle}-knob.png", os.path.join(os.path.dirname(__file__), self.imagePath, f"{self._dialStyle}-knob.png"))
        img_top = cache_image(f"{self._dialStyle}-knob-top.png", os.path.join(os.path.dirname(__file__), self.imagePath, f"{self._dialStyle}-knob-top.png"))
        
        painter = QPainter(self)
        w = self.width()
        h = self.height()
        painter.drawImage(QRect(0, 0, w, h), img_base)

        # So that we can use the background color
        #painter.setBackgroundMode(Qt.BGMode.TransparentMode)

        # Smooth out the circle
        painter.setRenderHint(QPainter.Antialiasing)

        # No border
        painter.setPen(QPen(Qt.NoPen))

        # Radius of knob  circle
        r = self.height() / 2.0
        
        # translate to middle of knob
        painter.translate(r, r)
        self.dialNumbers(painter, r, fwd = True, aligned = False)

        painter.rotate(self._overallRotation + self._startStop)

        # everything below here gets rotated with dial
        minval = self.minimum()
        maxval = self.maximum()
        val = self.value()
        ratio = (val - minval) / (maxval - minval)
        angle = ratio * (self._endStop - self._startStop)
        painter.rotate(angle)
        #painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Darken)
        painter.drawImage(QRect(-r, -r, w, h), img_top)         
        painter.rotate(-angle)                  # unwind value rotation

    def toolValue(self):
        value = self.value()
        if self.unitsScale == None:
            unitval = self.minimumUnit + (value * (self.maximumUnit - self.minimumUnit) / (self.maximum() - self.minimum()))
        else:
            unitval = self.unitsScale[value]
            
        fstr = "{0} {1:" + self.toolTipFormat + "} {2}"
        QToolTip.showText(QCursor.pos(), fstr.format(self.unitPrefix, unitval, self.unitSuffix))

    def setValue(self, value):
        if value == self.value():
            return
        self.blockSignals(True)
        super().setValue(value)
        self.blockSignals(False)

    def setDrawStyle(self, value):
        self.drawStyle = value

    def setMarkerColor(self, value):
        self.markerColor = value

    def setTicks(self, value):
        self.ticks = value
        
    def setMarks(self, value):
        self.marks = value

    def setImagePath(self, value):
        self.imagePath = value

    def setToolTipFormat(self, value):
        self.toolTipFormat = value

    def setMaximumUnit(self, value):
        self.maximumUnit = value

    def setMinimumUnit(self, value):
        self.minimumUnit = value

    def setUnitPrefix(self, str):
        self.unitPrefix = str

    def setUnitSuffix(self, str):
        self.unitSuffix = str

    def setDialMinimum(self, value):
        self._dialMinimum = value

    def setDialMaximum(self, value):
        self._dialMaximum = value

    def setDialStep(self, value):
        self._dialStep = value

    def setUnitsScale(self, value):
        self.unitsScale = value

    # set knob start angle in degrees
    def setStartStop(self, value):
        self._startStop = value

    def startStop(self):
        return self._startStop

    # set knob end angle in degrees
    def setEndStop(self, value):
        self._endStop = value

    def endStop(self):
        return self._endStop

    # set device overall rotation in degrees
    def setOverallRotation(self, value):
        self._overallRotation = value

    def overallRotation(self):
        return self._overallRotation

    # set the dial style by name
    def setDialStyle(self, style):
        if style != None:
            self._dialStyle = style.lower()
        else:
            self._dialStyle = ""

        self.update()

    def dialStyle(self):
        return self._dialStyle  
    
    def resizeEvent(self, event):
        super().resizeEvent(event)

        #self.label.setGeometry(0, 0, self.width(), self.width())
        #self.setGeometry(0, 0, self.width(), self.width())
        #self.label.setPixmap(self.pixmap.scaled(self.width(), self.height(),Qt.KeepAspectRatio))

    # stop window scrolling when limit stops reached
    def wheelEvent(self, event):
        super().wheelEvent(event)
        event.accept()
        return True
    
    # properties for QT Creator plugin

    dialStyle = Property(str, dialStyle, setDialStyle)
    startStop = Property(int, startStop, setStartStop)
    endStop = Property(int, endStop, setEndStop)
    overallRotation = Property(int, overallRotation, setOverallRotation)
    



    
    
    