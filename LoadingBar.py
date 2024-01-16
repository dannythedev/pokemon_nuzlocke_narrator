from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QProgressBar

from PokemonDB import get_data


class DataRetrievalThread(QThread):
    data_retrieved = pyqtSignal(dict)

    def __init__(self, generation):
        super().__init__()
        self.generation = generation

    def run(self):
        data = get_data(GENERATION=self.generation)
        self.data_retrieved.emit(data)


class MarqueeProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advanceOffset)
        self.offset = 0
        self.timer.start(15)  # Adjust the timer interval for animation speed

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the animated progress bar
        color = QColor(56, 142, 60)  # Color of the progress bar
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)

        width = self.width()
        height = self.height()
        barWidth = 30  # Width of each segment

        x = (self.offset - barWidth) % (width + barWidth)

        painter.drawRect(x - 15, 0, barWidth, height)

    def advanceOffset(self):
        self.offset += 2
        self.update()
