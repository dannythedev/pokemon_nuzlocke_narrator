# Nuzlocke Narrator

## Overview

Nuzlocke Narrator is a Pokemon Nuzlocke Tracker designed to help you keep track of your Nuzlocke challenge progress. With this tool, you can select the generation of Pokemon games you wish to play, retrieve data about Pokemon and encounters from pokemondb.net, and track your encounters throughout the game.
To start the program, execute the  ```main.py``` with Python.

## Features

- **Select Generation:**
  - Choose the generation of Pokemon games you want to play.
  - ![image](https://github.com/dannythedev/pokemon_nuzlocke_narrator/assets/99733108/0c2f0d53-a94c-4d5b-99b1-be7ed25b8ccc)

- **Retrieve Data:**
  - In case the information about Pokemon and encounters is not already present on your local machine, utilize the "Retrieve Data" button to fetch data from pokemondb.net, ensuring compliance with their robots.txt guidelines.
  - This action will generate a ```pokemon.json``` file containing all the Pokemon of the selected generation and an ```encounters.json``` file specific to the chosen generation. These files will serve as a local database for the program.
  - ![image](https://github.com/dannythedev/pokemon_nuzlocke_narrator/assets/99733108/7d047cc0-7c79-483c-8911-458c1a68ce74)

- **View Locations and Encounters:**
  - After retrieving the data, all the locations and their encounters will be shown accordingly.
  - ![image](https://github.com/dannythedev/pokemon_nuzlocke_narrator/assets/99733108/e5799a32-d994-49a4-ab7b-2a25387fa47f)

- **Track Pokemon Encounters:**
  - Track the Pokemon you encounter during your Nuzlocke challenge.

- **Update Encounter Status:**
  - Select if you've caught a Pokemon, stored it in Bill's PC, or if it unfortunately died during battle. Click Export Data (will export a ```save.json```) to save your run in the specific generation.

## Usage

1. **Select Generation:**
   - Launch the Nuzlocke Narrator application and choose the generation of Pokemon games you want to play.

2. **Retrieve Data:**
   - If the data is not locally available, click the "Retrieve Data" button to fetch information from pokemondb.net.

3. **Track Encounters:**
   - View the locations and encounters for the selected generation.
   - Track the Pokemon you encounter, update their status, and manage your Nuzlocke journey.

## Development

- The application is developed in Python using PyQt5 for the graphical user interface.

## Requirements

- Python 3.x
- PyQt5
- beautifulsoup4
- lxml
- requests

## How to Run

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/Nuzlocke-Narrator.git
