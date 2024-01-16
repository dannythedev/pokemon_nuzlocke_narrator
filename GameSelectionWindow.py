from functools import partial

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

from LoadingBar import DataRetrievalThread, MarqueeProgressBar
from NuzlockeTracker import NuzlockeTracker


class GameSelectionWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nuzlocke Narrator")
        layout = QVBoxLayout(self)

        label = QLabel("Select a game to Nuzlocke:")
        layout.addWidget(label)

        generation_buttons = []
        for generation in range(1, 6):
            button = QPushButton(f"Generation {generation}")
            icon_path = f"sav/img/gen/{generation}.png"
            icon = QIcon(icon_path)
            button.setIcon(icon)
            button.setIconSize(QSize(100, 100))
            button.clicked.connect(partial(self.selectGeneration, generation))
            layout.addWidget(button)
            generation_buttons.append(button)

        self.generation_buttons = generation_buttons
        # Toggle button for data retrieval
        self.retrieveButton = QPushButton("Retrieve Encounter and\nPokemon Data from the Web: OFF")
        self.retrieveButtonStatus = 0
        self.retrieveButton.clicked.connect(self.toggleRetrieveData)
        layout.addWidget(self.retrieveButton)
        self.windowIcon()
        self.applyDarkTheme()
        WIDTH, HEIGHT = 280, 540
        self.setFixedHeight(HEIGHT)
        self.setFixedWidth(WIDTH)
        self.setGeometry(300, 300, WIDTH, HEIGHT)

    def windowIcon(self):
        NuzlockeTracker.windowIcon(self)


    def selectGeneration(self, generation):
        self.selectedGame = generation

        if self.retrieveButtonStatus:
            # Create and configure the progress dialog
            progress_dialog = QProgressDialog("Retrieving Generation {} Pokemon\nEncounters from the web...".format(generation), "Cancel", 0, 0, self)
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setWindowTitle("Please Wait")
            progress_dialog.setCancelButton(None)  # Disable cancel button

            # Apply the dark theme
            self.applyDarkTheme()

            # Create a custom indeterminate progress bar
            progress_bar = MarqueeProgressBar(progress_dialog)
            progress_dialog.setBar(progress_bar)

            # Create a thread for data retrieval
            data_thread = DataRetrievalThread(generation)
            data_thread.data_retrieved.connect(self.dataRetrieved)
            data_thread.finished.connect(progress_dialog.accept)

            # Start the thread and show the progress dialog
            data_thread.start()
            progress_dialog.exec_()

        self.accept()

    def dataRetrieved(self, data):
        # Handle the retrieved data here
        print("Data retrieved:", data)
        # You can use the 'data' variable as needed in your application
        self.accept()

    def toggleRetrieveData(self):
        # Implement the logic for toggling data retrieval
        if self.retrieveButtonStatus == 0:
            self.retrieveButton.setText("Retrieve Encounter and\nPokemon Data from the Web: ON")
            self.retrieveButtonStatus = 1
            # Add logic to start data retrieval here
        else:
            self.retrieveButton.setText("Retrieve Encounter and\nPokemon Data from the Web: OFF")
            self.retrieveButtonStatus = 0
            # Add logic to stop data retrieval here



    def applyDarkTheme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #101c24; /* Dark gray background */
                color: #D3D3D3; /* Light gray text */
                font-family: "Segoe UI", Arial, sans-serif; /* Modern font */
                font-size: 10pt;
            }

            QLabel {
                font-weight: bold; /* Bold font for labels */
                color: #D3D3D3; /* Light gray text */
            }

            QPushButton {
                background-color: #808080; /* Green background */
                color: #FFFFFF; /* White text */
                border: 0px solid #808080; /* Slightly darker border */
                padding: 6px;
                border-radius: 4px; /* Rounded corners */
                min-height: 30px; /* Minimum height */
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #388E3C; /* Darker shade on hover */
            }

            QPushButton:pressed {
                background-color: #2E7D32; /* Even darker when pressed */
            }
        """)

    def selectGame(self):
        selected_game = self.gameComboBox.currentText()
        # You can now pass this selected game to your main application
        # For example, you can store it in an instance variable
        self.selectedGame = selected_game
        self.accept()
