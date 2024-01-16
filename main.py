import sys
from PyQt5.QtWidgets import QApplication
from GameSelectionWindow import GameSelectionWindow
from NuzlockeTracker import NuzlockeTracker


def main():
    app = QApplication(sys.argv)

    # Show the game selection window
    gameSelectionWindow = GameSelectionWindow()
    if gameSelectionWindow.exec_():
        # Pass the selected game to the main window
        GENERATION = gameSelectionWindow.selectedGame
        ex = NuzlockeTracker(GENERATION=GENERATION)
        ex.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
