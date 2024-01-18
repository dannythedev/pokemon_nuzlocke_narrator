import json
from collections import OrderedDict

import requests

from Functions import convert_image_url_to_base64, is_json_empty, POKEMON_DIR, ENCOUNTER_DIR, calculate_level_averages, \
    sort_routes_for_each_region, average_level
from Parser import Parser
from Request import Request



class PokemonDB(Request):
    def __init__(self, GENERATION):
        self.GENERATION = GENERATION
        self.rating = []
        self.html = Parser()
        self.home_url = 'https://pokemondb.net'
        self.region_url = '{home_url}/location/'
        self.location_url = '{home_url}/location/{location}#gen{gen_id}'
        self.pokemon_url = '{home_url}/pokedex/{pokemon_name_or_id}'
        self.image_url = 'https://img.pokemondb.net/sprites/crystal/normal/{pokemon_name}.png'
        self.stats_pokemon = '{home_url}/pokedex/stats/gen{gen_id}'
        self.headers = {}
        self.params = {}
        self.request_counter = 0
        self.xpaths = {"pokemon_single_page":
                           {"name": "//main[@id='main']/h1/text()",
                            "id": "//tr[th[contains(text(), 'National')]]/td/strong/text()",
                            "type": "//tr[th[contains(text(), 'Type')]]/td/a/text()"},
                       "pokemon_stats_page":
                           {"column": "//td[@class='cell-num cell-fixed']/..",
                            "name": ".//td[@class='cell-name']//text()",
                            "type": ".//td[@class='cell-icon']/a/text()",
                            "chibi_image": ".//img[@class='img-fixed icon-pkmn']/@src",
                            "id": ".//span[@class='infocard-cell-data']//text()"},
                       "pokemon_locations_page":
                           {"location_url": "//a[contains(@href,'location/{region}')]/@href",
                            "regions": "//nav[@class='sv-tabs-tab-list']/a/text()"
                            },
                       "pokemon_route_page":
                           {
                               "generation_encounter": "//h2[contains(text(), 'Generation {gen_id}')]/following-sibling::div/table",
                               "encounter_method": ".//h2[contains(text(), 'Generation {gen_id}')]/following-sibling::h3/text()",
                               "encounter_name": ".//a[@class='ent-name']/text()",
                               "encounter_rarity": ".//td[6]/img[@class='icon-loc'][@title]/@title",
                               "encounter_levels":".//td[@class='cell-num']/text()",
                               "route_name": "//h1/text()"}
                       }

    def get_all_pokemon(self):
        pokemon_list = []
        if is_json_empty(POKEMON_DIR):
            for gen in range(1, 6):
                response = self.get(url=self.stats_pokemon.format(home_url=self.home_url, gen_id=gen))
                pokemon_data = self.html.get_xpath_elements([self.xpaths["pokemon_stats_page"]["column"]])
                for mon in pokemon_data:
                    pokemon_list.append({
                        "id": int(mon.xpath(self.xpaths["pokemon_stats_page"]["id"])[0]),
                        "name": str(mon.xpath(self.xpaths["pokemon_stats_page"]["name"])[0]),
                        "type": mon.xpath(self.xpaths["pokemon_stats_page"]["type"]),
                        "chibi_image": convert_image_url_to_base64(
                            str(mon.xpath(self.xpaths["pokemon_stats_page"]["chibi_image"])[0]))})
            export_to_json(POKEMON_DIR, pokemon_list)
        else:
            print("Pokemon.json is already here.")
        return pokemon_list

    def get_all_locations_url(self):
        # Add Starters
        starters = {
            "Kanto": ["Bulbasaur", "Charmander", "Squirtle"],
            "Johto": ["Chikorita", "Cyndaquil", "Totodile"],
            "Hoenn": ["Treecko", "Torchic", "Mudkip"],
            "Sinnoh": ["Turtwig", "Chimchar", "Piplup"],
            "Unova": ["Snivy", "Tepig", "Oshawott"],
            "Kalos": ["Chespin", "Fennekin", "Froakie"],
            "Alola": ["Rowlet", "Litten", "Popplio"],
            "Galar": ["Grookey", "Scorbunny", "Sobble"]
            # Add more regions and starters as needed
        }

        route_name = ''
        region_name = ''
        # Locations
        location_encounters = dict()
        if is_json_empty(ENCOUNTER_DIR.format(self.GENERATION)):
            response = self.get(url=self.region_url.format(home_url=self.home_url))
            regions_list = {'1': ['Kanto'],
                            '2': ['Johto'],
                            '3': ['Hoenn'],
                            '4': ['Sinnoh'],
                            '5': ['Unova'],
                            '6': ['Kalos'],
                            '7': ['Alola'],
                            '8': ['Galar', 'Hisui'],
                            '9': ['Paldea']}
            locations_list = []
            regions_list = [value for sublist in list(regions_list.values())[:self.GENERATION] for value in sublist]
            for region in regions_list:
                locations_list.extend(self.html.get_xpath_elements(
                    [self.xpaths["pokemon_locations_page"]["location_url"].format(region=region.lower())]))
                if region not in location_encounters:
                    location_encounters[region] = dict()
                    location_encounters[region]['Starters'] = {pokemon: {'Level':0, 'Time':'', 'Method':'Gift'} for pokemon in starters[region]}
            # Encounter
            for location in locations_list:
                response = self.get(url=self.home_url + location)
                encounter_method = self.html.get_xpath_elements(
                    [self.xpaths["pokemon_route_page"]["encounter_method"].format(gen_id=self.GENERATION)])
                pokemon_encountered = self.html.get_xpath_elements(
                    [self.xpaths["pokemon_route_page"]["generation_encounter"].format(gen_id=self.GENERATION)])
                encounter_pair = dict()
                if pokemon_encountered:
                    method_pair = list(zip(pokemon_encountered, encounter_method))
                    for pokemon_encounter_method, pokemon_method in method_pair:
                        encounter_names = pokemon_encounter_method.xpath(self.xpaths["pokemon_route_page"]["encounter_name"])
                        encounter_levels = pokemon_encounter_method.xpath(self.xpaths["pokemon_route_page"]["encounter_levels"])
                        route_average_level = calculate_level_averages(encounter_levels)
                        encounter_pair.update({pokemon: {'Level':route_average_level, 'Time':'', 'Method':pokemon_method} for pokemon in encounter_names})
                        route_name, region = self.html.get_xpath_elements([self.xpaths["pokemon_route_page"]["route_name"]])[0].split(', ')
                    location_encounters[region][route_name] = encounter_pair
            location_encounters = OrderedDict(reversed(location_encounters.items()))

            # Sort routes for each region in the Pokemon dictionary
            location_encounters = sort_routes_for_each_region(location_encounters)

            export_to_json(ENCOUNTER_DIR.format(self.GENERATION), location_encounters)
        else:
            print("Encounter.json is already here.")
        return location_encounters

def export_to_json(filename, data):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully exported to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_data(GENERATION):
    site = PokemonDB(GENERATION)
    site.get_all_pokemon()
    site.get_all_locations_url()
