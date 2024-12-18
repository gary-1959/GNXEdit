
from PySide6.QtWidgets import QDial, QSpinBox, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QSize, QRect

from styledial import StyleDial

class Widget01(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.dial = StyleDial()
        self.setObjectName(u"dial")
        self.setMinimumSize(80, 80)
        self.verticalLayout.addWidget(self.dial)

        self.spinBox = QSpinBox()
        self.spinBox.setObjectName(u"spinBox")
        #self.spinBox.setMinimumWidth(40)
        self.spinBox.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.verticalLayout.addWidget(self.spinBox)

        self.verticalLayout.setGeometry(QRect(0, 0, 40, 80))
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.dial.valueChanged.connect(self.spinBox.setValue)
        self.spinBox.valueChanged.connect(self.dial.setValue)

        self.heightForWidth(True)
        self.setLayout(self.verticalLayout)

    def setMaximum(self,value):
        self.dial.setMaximum(value)
        self.spinBox.setMaximum(value)

    def setMinimum(self, value):
        self.setMinimum(value)
        self.spinBox.setMinimum(value)

    def setSuffix(self, suffix):
        self.spinBox.suffix = suffix

    def setValue(self, value):
        self.value = value
        self.spinBox.value = value
    
    
    