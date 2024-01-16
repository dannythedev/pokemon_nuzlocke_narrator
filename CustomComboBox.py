from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QComboBox, QStyleFactory


class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CustomComboBox, self).__init__(parent)
        self.iconSize = QSize(100, 100)  # Set the icon size

    def sizeHint(self):
        size = super(CustomComboBox, self).sizeHint()
        size.setHeight(self.iconSize.height() + 10)  # Adjust item height
        return size

    def resizeEvent(self, event):
        super(CustomComboBox, self).resizeEvent(event)
        self.setStyle(QStyleFactory.create(self.style().objectName()))  # Refresh style
