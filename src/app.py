import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem

from layout_colorwidget import Color

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")


        data = {"FACTORY": ["file_a.py", "file_a.txt", "something.xls"],
        "USER": ["file_b.csv", "photo.jpg"]}

        tree = QTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderLabels(["Name"])

        items = []
        for key, values in data.items():
            item = QTreeWidgetItem([key])
            for value in values:
                child = QTreeWidgetItem([value])
                item.addChild(child)
            items.append(item) 

        tree.insertTopLevelItems(0, items)

        self.setCentralWidget(tree)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()