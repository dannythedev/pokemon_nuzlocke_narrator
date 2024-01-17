import os
import json
from base64 import b64decode
from functools import partial
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QScrollArea, QGraphicsView, QGraphicsPixmapItem, QGraphicsScene, QFileDialog, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem, QFont, QPainter, QColor
from PyQt5.QtCore import Qt, QSize
from CustomComboBox import CustomComboBox
from Functions import is_json_empty, POKEMON_DIR, ENCOUNTER_DIR


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

    def calculateLayoutIndex(self, region_index, route_index):
        # Assuming each region contributes only one row
        return region_index * 2 + route_index

    def applyDarkTheme(self):
        self.setStyleSheet("""
            QWidget {
    background-color: #101c24; /* Dark gray background */
    color: #D3D3D3; /* Light gray text */
    font-family: "Roboto", sans-serif; /* Modern font */
    font-size: 11pt;
        }
        QLabel#containerTitle {
        font-size: 9pt; /* Adjust the font size */
        font-style: italic;
        color: #D3D3D3; /* Light gray text */
        font-family: 'Palatino Linotype', monospace; /* Modern font */
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
            background-color: #FFA4A4; /* Darker shade on hover */
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
        from datetime import datetime
        # Get the current date
        current_date = datetime.now()
        current_time = current_date.time()
        # Format the time as mm_hh
        # Format the date as dd-mm-yy
        formatted_date = current_date.strftime("%d-%m-%y")
        formatted_time = current_time.strftime("%M_%H")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data File", f"gen{self.GENERATION}_{formatted_date}_{formatted_time}_sav", "JSON Files (*.json);;All Files (*)", options=options)

        if file_name:
            if not file_name.endswith('.json'):
                file_name+='.json'
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

            with open(file_name, 'w') as file:
                if is_json_empty(file_name):
                    json.dump(export_dict, file, indent=4)

            print(f"Data exported successfully to: {file_name}")


    def addPokemonImageContainer(self):
        # Add a new widget to hold the Pokémon images
        self.pokemonImageContainer = QWidget()
        self.pokemonImageContainer.setObjectName("pokemonImageContainer")
        self.pokemonImageContainerLayout = QHBoxLayout(self.pokemonImageContainer)
        self.pokemonImageContainerLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.pokemonImageContainerLayout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins

    def addEncounteredPokemonImageContainer(self):
        # Add a new widget to hold the encountered Pokémon images
        self.encounteredPokemonImageContainer = QWidget()
        self.encounteredPokemonImageContainer.setObjectName("encounteredPokemonImageContainer")
        self.encounteredPokemonImageContainerLayout = QHBoxLayout(self.encounteredPokemonImageContainer)
        self.encounteredPokemonImageContainerLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.encounteredPokemonImageContainerLayout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins


    def loadDataFromFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Data File", "", "JSON Files (*.json);;All Files (*)", options=options)

        if file_name:
            self.loadDataFromFile(file_name)

    def loadDataFromFile(self, file_name):
        if os.path.exists(file_name):
            with open(file_name, 'r') as file:
                data = json.load(file)
            self.loadDataToGUI(data)
            print(f"Data loaded successfully from: {file_name}")
        else:
            print(f"File not found: {file_name}")
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
        # Create a horizontal layout for the load and export buttons
        buttonLayout = QHBoxLayout()

        # Add the export button to the button layout
        exportButton = QPushButton("Export State")
        exportButton.clicked.connect(self.exportData)
        buttonLayout.addWidget(exportButton)

        # Add the load button to the button layout
        loadButton = QPushButton("Load State")
        loadButton.clicked.connect(self.loadDataFromFileDialog)
        buttonLayout.addWidget(loadButton)

        # Add the button layout to the main layout
        mainLayout.addLayout(buttonLayout)

        # Add the generation icon in the top-right corner
        self.addGenerationIcon()

        def set_title(text):
            # Create a QLabel for the title
            label = QLabel(text)
            label.setObjectName("containerTitle")  # Set object name for styling
            mainLayout.addWidget(label)

        # Create a widget to hold the layout for Pokémon images
        self.addPokemonImageContainer()
        containerForImages = QWidget()
        containerForImages.setLayout(self.pokemonImageContainerLayout)
        mainLayout.addWidget(containerForImages)
        self.addEncounteredPokemonImageContainer()
        encounteredContainerForImages = QWidget()
        encounteredContainerForImages.setLayout(self.encounteredPokemonImageContainerLayout)
        mainLayout.addWidget(encounteredContainerForImages)

        self.windowIcon()
        # Adjust window size as needed
        WIDTH, HEIGHT = 655, 855
        self.setFixedHeight(HEIGHT)
        self.setGeometry(300, 300, WIDTH, HEIGHT)

    def updatePokemonImageContainer(self, pokemon_names):
        DIF = 60
        # Clear existing images in the container
        for i in reversed(range(self.pokemonImageContainerLayout.count())):
            item = self.pokemonImageContainerLayout.itemAt(i)
            item.widget().setParent(None)

        # Create a scene for the Pokemon images
        scene = QGraphicsScene(self)

        # Add images for the new Pokémon names
        for i, (pokemon_name, pokemon_nickname) in enumerate(pokemon_names):
            pokemon = next((p for p in self.pokemon_data if p['name'] == pokemon_name), None)
            if pokemon:
                img_data = b64decode(pokemon['chibi_image'].split(",")[-1])
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)

                # Create a QGraphicsPixmapItem for each Pokemon image
                item = QGraphicsPixmapItem(pixmap)
                item.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                item.setPos(i * DIF, 0)
                item.setToolTip(f'{pokemon_nickname}\nThe {pokemon_name}')
                scene.addItem(item)

                img_pokeball = 'sav/img/caught.png'
                pixmap = QPixmap(img_pokeball)
                item2 = QGraphicsPixmapItem(pixmap)
                item2.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio))
                item2 = QGraphicsPixmapItem(pixmap)
                item2.setPos(i * DIF + 60, 60)
                scene.addItem(item2)

        # Create a QGraphicsView and set the scene
        view = QGraphicsView(self)
        view.setScene(scene)

        # Add the QGraphicsView to the layout
        self.pokemonImageContainerLayout.addWidget(view)

    def text_to_pixmap(self, text, font_size=8, width=200, height=50):
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)  # Use transparent background

        painter = QPainter(pixmap)

        # Create a pixelated font
        font = QFont("Courier New", font_size, QFont.Bold)
        painter.setFont(font)

        # Set font color to white
        painter.setPen(QColor(Qt.white))

        # Draw the text on the pixmap
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()

        return pixmap

    def updateEncounteredPokemonImageContainer(self, encountered_pokemon):
        DIF = 25
        # Clear existing images and labels in the container
        for i in reversed(range(self.encounteredPokemonImageContainerLayout.count())):
            item = self.encounteredPokemonImageContainerLayout.itemAt(i)
            item.widget().setParent(None)

        # Create a scene for the encountered Pokemon images
        scene = QGraphicsScene(self)

        # Count the occurrences of each Pokémon in the encountered_pokemon list
        encountered_pokemon_counts = {}
        for pokemon_name in encountered_pokemon:
            encountered_pokemon_counts[pokemon_name] = encountered_pokemon_counts.get(pokemon_name, 0) + 1

        # Sort the encountered Pokémon counts by appearance (highest to lowest)
        sorted_counts = sorted(encountered_pokemon_counts.items(), key=lambda x: x[1], reverse=True)

        # Add images for the encountered Pokémon names with counts
        for i, (pokemon_name, count) in enumerate(sorted_counts):
            pokemon = next((p for p in self.pokemon_data if p['name'] == pokemon_name), None)
            if pokemon:
                img_data = b64decode(pokemon['chibi_image'].split(",")[-1])
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)

                # Create a QGraphicsPixmapItem for each Pokemon image
                item = QGraphicsPixmapItem(pixmap)
                item.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                item.setPos(i * DIF, 0)
                item.setToolTip(f'{pokemon_name}:\nx{str(count)}')
                scene.addItem(item)

                img_pokeball = self.text_to_pixmap(f'x{str(count)}')
                pixmap = QPixmap(img_pokeball)
                item2 = QGraphicsPixmapItem(pixmap)
                item2.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio))
                item2 = QGraphicsPixmapItem(pixmap)
                item2.setPos(i * DIF - 40, 50)
                scene.addItem(item2)

        # Create a QGraphicsView and set the scene
        view = QGraphicsView(self)
        view.setScene(scene)

        # Add the QGraphicsView to the layout
        self.encounteredPokemonImageContainerLayout.addWidget(view)
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
        icon_size = QSize(100, 100)
        comboBox.setModel(model)
        comboBox.setIconSize(icon_size)
        comboBox.currentIndexChanged.connect(lambda: self.onPokemonSelected(comboBox, region, route))

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
        # Disable status buttons initially
        self.disableStatusButtons(region, route)


    def disableStatusButtons(self, region, route):
        if region in self.status_buttons_by_route and route in self.status_buttons_by_route[region]:
            buttons = self.status_buttons_by_route[region][route].get('Status', [])
            for button in buttons:
                button.setEnabled(False)

    def enableStatusButtons(self, region, route):
        if region in self.status_buttons_by_route and route in self.status_buttons_by_route[region]:
            buttons = self.status_buttons_by_route[region][route].get('Status', [])
            for button in buttons:
                button.setEnabled(True)

    def changeButtonColor(self, clickedButton):
        # Extract the region and route information from the clickedButton's parent widget
        region, route = None, None
        for r, routes in self.status_buttons_by_route.items():
            for rt, buttons_info in routes.items():
                if clickedButton in buttons_info.get('Status', []):
                    region, route = r, rt
                    break

        if region is not None and route is not None:
            buttons = self.status_buttons_by_route[region][route].get('Status', [])
            for button in buttons:
                # Reset the color of all buttons in the specific row to grey
                button.setStyleSheet("QPushButton { background-color: grey; }"
                                     "QPushButton:hover { background-color: #FFCDD2; }")  # Light-red on hover

            # Set the color of the clicked button to red
            clickedButton.setStyleSheet("QPushButton { background-color: red; }"
                                        "QPushButton:hover { background-color: #FFA4A4; }")  # Light-red on hover

            # Update the Pokemon image container with the caught Pokemon names
            self.updatePokemonImageContainer(self.getAllCaughtPokemonNames()[0])

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

    def getAllCaughtPokemonNames(self):
        # Get caught pokemon currently in team.
        caught_pokemon_names = []
        encountered_pokemon = []
        for region_name in self.status_buttons_by_route:
            for route_name in self.status_buttons_by_route[region_name]:
                comboBox = self.status_buttons_by_route[region_name][route_name]['comboBox']
                nickname = self.status_buttons_by_route[region_name][route_name]['Nickname']
                encountered_pokemon.append(comboBox.currentText())
                buttons = self.status_buttons_by_route[region_name][route_name]['Status']
                for statusButton in buttons:
                    if 'background-color: red;' in statusButton.styleSheet() and statusButton.toolTip() == 'Caught':
                        caught_pokemon_names.append((comboBox.currentText(), nickname.text()))

        return caught_pokemon_names[:6], encountered_pokemon

    def onPokemonSelected(self, comboBox, region, route):
        selected_pokemon_names = [comboBox.itemText(i) for i in range(comboBox.count())]
        selected_pokemon = comboBox.currentText()  # Get the currently selected Pokémon
        if selected_pokemon != '-':
            self.enableStatusButtons(region, route)
        else:
            self.disableStatusButtons(region, route)
        self.updatePokemonImageContainer(self.getAllCaughtPokemonNames()[0])
        self.updateEncounteredPokemonImageContainer(self.getAllCaughtPokemonNames()[1])

