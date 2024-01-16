import os
import json
from base64 import b64decode
from functools import partial
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QScrollArea
from PyQt5.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSize
from CustomComboBox import CustomComboBox
from Functions import is_json_empty, POKEMON_DIR, ENCOUNTER_DIR, EXPORT_DIR


class NuzlockeTracker(QWidget):
    def __init__(self, GENERATION):
        super().__init__()
        self.GENERATION = GENERATION
        if not is_json_empty(POKEMON_DIR):
            self.pokemon_data = self.load_json(POKEMON_DIR)
        else:
            self.pokemon_data = []
        if not is_json_empty(ENCOUNTER_DIR.format(GENERATION)):
            self.encounter_data = self.load_json(ENCOUNTER_DIR.format(GENERATION))
        else:
            self.encounter_data = {}
        self.status_buttons_by_route = dict()
        self.initUI()

    def load_json(self, filename):
        with open(filename, 'r') as file:
            return json.load(file)

    def loadData(self):
        filename = EXPORT_DIR.format(self.GENERATION)
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                data = json.load(file)
            self.loadDataToGUI(data)
        else:
            print("Exported data file not found.")

    def loadDataToGUI(self, data):
        for i, (region, region_data) in enumerate(data.items()):
            for j, (route, route_data) in enumerate(region_data.items(), start=1):
                comboBox = self.status_buttons_by_route[region][route]['comboBox']
                nicknameEdit = self.status_buttons_by_route[region][route]['Nickname']
                nicknameEdit.setText(route_data['nickname'])
                comboBox.setCurrentText(route_data['pokemon'])
                buttons = self.status_buttons_by_route[region][route]['Status']
                for statusButton in buttons:
                    if statusButton.toolTip() == route_data['status']:
                        self.changeButtonColor(statusButton)

        for x in range(self.layout.count()):
            try:
                s = self.layout.itemAt(x).layout().itemAt(2).layout().itemAt(0).widget().currentText()
                if s != '-':
                    print(s)
            except:
                pass

    def calculateLayoutIndex(self, region_index, route_index):
        # Assuming each region contributes only one row
        return region_index*2 + route_index

    def applyDarkTheme(self):
        self.setStyleSheet("""
            QWidget {
    background-color: #101c24; /* Dark gray background */
    color: #D3D3D3; /* Light gray text */
    font-family: "Roboto", sans-serif; /* Modern font */
    font-size: 11pt;
        }
        QLabel#regionLabel {
            font-size: 9pt;
            font-style: italic;
            font-family: 'Courier New', monospace; /* Modern font */
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


        QLineEdit, QComboBox {
            background-color: #15232e; /* White background */
            color: #D3D3D3; /* Dark text */
            border: 1px solid #BDBDBD; /* Light gray border */
            border-radius: 4px; /* Rounded corners */
            padding: 5px;
            min-height: 70px; /* Minimum height */
        }

        QLabel {
            font-weight: bold; /* Bold font for labels */
        }

        QComboBox QAbstractItemView {
            background: #212121; /* White background for dropdown */
            selection-background-color: #4CAF50; /* Green selection background */
        }

        QScrollArea {
            border: none; /* No border for scroll area */
        }

        /* Scrollbar styles */
        QScrollBar:vertical {
            background: #424242;
            width: 10px; /* Width of the vertical scrollbar */
            margin: 10px 0 10px 0;
        }

        QScrollBar::handle:vertical {
            background: #616161; /* Color of the scrollbar handle */
            min-height: 20px; /* Minimum height of the handle */
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            background: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }

        """)

    def exportData(self):
        export_dict = dict()

        for i in range(self.layout.count()):
            vBox = self.layout.itemAt(i).layout()
            if vBox:
                regionLabel = vBox.itemAt(1).widget()
                region_name = regionLabel.text()
                routeLabel = vBox.itemAt(0).widget()
                route_name = routeLabel.text()

                # Add an empty dictionary for each route in the corresponding region
                export_dict.setdefault(region_name, {})[route_name] = {}

                for j in range(1, vBox.count()):
                    hBox = vBox.itemAt(j).layout()
                    if hBox:
                        # Initialize status as None
                        status = None
                        comboBox = hBox.itemAt(0).widget()
                        pokemon_name = comboBox.currentText()

                        nicknameEdit = hBox.itemAt(1).widget()
                        nickname = nicknameEdit.text()
                        export_dict[region_name][route_name] = {
                            'pokemon': pokemon_name,
                            'nickname': nickname,
                            'status': status
                        }


        # Iterate through status buttons to find the selected one
        for region_name in self.status_buttons_by_route:
            for route_name in self.status_buttons_by_route[region_name]:
                buttons = self.status_buttons_by_route[region_name][route_name]['Status']
                for statusButton in buttons:
                    if 'background-color: red;' in statusButton.styleSheet():
                        status = statusButton.toolTip()
                        # Add the data to the route data dictionary
                        export_dict[region_name][route_name]['status'] = status

        with open(EXPORT_DIR.format(self.GENERATION), 'w') as file:
            if is_json_empty(EXPORT_DIR.format(self.GENERATION)):
                json.dump(export_dict, file, indent=4)

        print("Data exported successfully.")

    def initUI(self):
        self.setWindowTitle("Nuzlocke Narrator")
        # Create the main layout
        self.layout = QVBoxLayout()

        self.applyDarkTheme()

        for region, routes in self.encounter_data.items():
            self.status_buttons_by_route[region] = dict()
            for route, pokemon_names in routes.items():
                self.addRouteWidgets(region, route, pokemon_names)

        # Create a widget to hold the layout
        container = QWidget()
        container.setLayout(self.layout)

        # Create a scroll area and set its widget
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)  # Make the scroll area resizable
        scrollArea.setWidget(container)

        # Set the scroll area as the central widget if using QMainWindow
        # self.setCentralWidget(scrollArea)

        # For QWidget, set the layout to contain the scroll area
        mainLayout = QVBoxLayout(self)  # The main layout for the window
        mainLayout.addWidget(scrollArea)

        # Add the export button at the bottom
        exportButton = QPushButton("Export Data")
        exportButton.clicked.connect(self.exportData)
        mainLayout.addWidget(exportButton)

        # Add the generation icon in the top-right corner
        self.addGenerationIcon()
        self.windowIcon()
        self.loadData()
        # Adjust window size as needed
        self.setGeometry(300, 300, 655, 700)

    def windowIcon(self):
        icon_path = f'sav/img/pokeball.png'  # Replace with the actual path to your icon file
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.setWindowIcon(icon)

    def addGenerationIcon(self):
        gen_icon_path = f'sav/img/gen/{self.GENERATION}.png'  # Replace with the actual path
        if os.path.exists(gen_icon_path):
            gen_icon_label = QLabel()
            pixmap = QPixmap(gen_icon_path)
            gen_icon_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio))
            gen_icon_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
            self.layout.insertWidget(0, gen_icon_label)

    def addRouteWidgets(self, region, route, pokemon_names):
        vBox = QVBoxLayout()

        # Create a label for the route name and add it to the vertical layout
        routeLabel = QLabel(route)
        vBox.addWidget(routeLabel)

        def add_region_label():
            # Create a label for the region and add it to the vertical layout
            setattr(self, f"{region}Label", QLabel(region))  # Create the label if not exists
            region_widget = getattr(self, f"{region}Label")
            region_widget.setObjectName("regionLabel")  # Set the object name for the QLabel
            font = region_widget.font()
            font.setPointSize(10)  # Adjust the size as needed
            font.setItalic(True)
            region_widget.setFont(font)
            vBox.addWidget(region_widget)  # Add the label to the vertical layout
        add_region_label()
        hBox1 = QHBoxLayout()
        comboBox = CustomComboBox()  # Use the custom combo box
        model = QStandardItemModel()
        # Create an empty item as the first item
        empty_item = QStandardItem('-')
        model.appendRow(empty_item)

        for name in pokemon_names:
            pokemon = next((p for p in self.pokemon_data if p['name'] == name), None)
            if pokemon:
                img_data = b64decode(pokemon['chibi_image'].split(",")[-1])
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                icon_size = QSize(100, 100)
                item = QStandardItem(QIcon(pixmap.scaled(icon_size, Qt.KeepAspectRatio)), name)
                model.appendRow(item)

        comboBox.setModel(model)
        comboBox.setIconSize(icon_size)
        comboBox.currentIndexChanged.connect(lambda: self.onPokemonSelected(comboBox))

        comboBox.setFixedSize(250, 200)
        hBox1.addWidget(comboBox)

        nickname = QLineEdit()
        nickname.setPlaceholderText("Enter Nickname")
        nickname.setFixedSize(200, 100)

        if route not in self.status_buttons_by_route[region]:
            self.status_buttons_by_route[region][route] = {'Nickname': nickname,
                                                           'comboBox': comboBox}
        hBox1.addWidget(nickname)

        image_label = QLabel()
        hBox1.addWidget(image_label)

        hBox1Buttons = QHBoxLayout()
        hBox2Buttons = QHBoxLayout()

        # Create a vertical layout for the buttons container
        buttonsContainer = QVBoxLayout()
        status_buttons_info1 = {
            'Caught': 'sav/img/pokeball.png',
            'Left': 'sav/img/fainted.png'
        }
        buttonsContainer.addLayout(hBox1Buttons)
        status_buttons_info2 = {
            'Stored': 'sav/img/billspc.png',
            'Died': 'sav/img/pokegrave.png'
        }

        for button_text, icon_path in status_buttons_info1.items():
            aButton = QPushButton()
            icon = QIcon(icon_path)
            aButton.setIcon(icon)
            aButton.setIconSize(icon_size)
            aButton.setToolTip(button_text)
            aButton.setFixedSize(50, 40)
            aButton.clicked.connect(partial(self.updateStatus, comboBox, '-', aButton))
            aButton.clicked.connect(partial(self.changeButtonColor, aButton))

            if 'Status' not in self.status_buttons_by_route[region][route]:
                self.status_buttons_by_route[region][route].update({'Status': []})
            self.status_buttons_by_route[region][route]['Status'].append(aButton)  # Add the button to the list
            hBox1Buttons.addWidget(aButton)

        for button_text, icon_path in status_buttons_info2.items():
            aButton = QPushButton()
            icon = QIcon(icon_path)
            aButton.setIcon(icon)
            aButton.setIconSize(icon_size)
            aButton.setToolTip(button_text)
            aButton.setFixedSize(50, 40)
            aButton.clicked.connect(partial(self.updateStatus, comboBox, '-', aButton))
            aButton.clicked.connect(partial(self.changeButtonColor, aButton))
            if 'Status' not in self.status_buttons_by_route[region][route]:
                self.status_buttons_by_route[region][route].update({'Status': []})
            self.status_buttons_by_route[region][route]['Status'].append(aButton)  # Add the button to the list
            hBox2Buttons.addWidget(aButton)

        # Add the second row buttons to the buttons container
        buttonsContainer.addLayout(hBox2Buttons)
        # Add the buttons container to the main horizontal layout
        hBox1.addLayout(buttonsContainer)
        vBox.addLayout(hBox1)

        # Status display label
        statusLabel = QLabel('-')
        vBox.addWidget(statusLabel)

        self.layout.addLayout(vBox)

    def changeButtonColor(self, button):
        current_style = button.styleSheet()
        # Check if the current color is red and toggle
        if 'background-color: red;' in current_style:
            button.setStyleSheet("QPushButton { background-color: grey; }")
        else:
            button.setStyleSheet("QPushButton { background-color: red; }")

    def updateStatus(self, comboBox, status, clickedButton):
        pokemon_name = comboBox.currentText()
        for i in range(self.layout.count()):
            # Get the vertical layout that might contain the horizontal layouts
            vBox = self.layout.itemAt(i).layout()
            if vBox:
                for j in range(vBox.count()):
                    # Get the horizontal layout
                    hBox = vBox.itemAt(j).layout()
                    if hBox:
                        # Check if this horizontal layout contains the comboBox
                        if hBox.indexOf(comboBox) != -1:
                            # Find the status label (assuming it's the last widget in the hBox)
                            statusLabel = hBox.itemAt(hBox.count() - 1).widget()
                            if isinstance(statusLabel, QLabel):
                                statusLabel.setText(status)
                                return  # Break out of both loops

    def onPokemonSelected(self, comboBox):
        pokemon_name = comboBox.currentText()
        for pokemon in self.pokemon_data:
            if pokemon['name'] == pokemon_name:
                img_data = b64decode(pokemon['chibi_image'].split(",")[-1])
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                for i in range(self.layout.count()):
                    hbox = self.layout.itemAt(i).layout()
                    if hbox:
                        if hbox.itemAt(1).widget() == comboBox:
                            hbox.itemAt(3).widget().setPixmap(pixmap.scaled(75, 75, Qt.KeepAspectRatio))
                            break