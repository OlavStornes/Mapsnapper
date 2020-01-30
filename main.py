import os
import time
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urljoin
import argparse
import sys

ATLAS_URL = "https://vgmaps.com/Atlas/"

TR_IMAGE_POS = 0
TR_NAME_POS = 1
TR_GAMES_START = 2


def sanitize_input(string_input):
    for x in r"/\*?":
        string_input = string_input.replace(x, '_')
    string_input = string_input.replace('"', "'")
    string_input = string_input.replace(':', " -").replace('  ', ' ')
    return string_input


def get_or_create_folder(target_folder):
    target_folder = target_folder.replace('.', '')
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)
        return target_folder
    else:
        return target_folder


def dir_path(string):
    path = os.path.abspath(string)
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


@dataclass
class Game:
    html: object
    game_url: str
    console_folder: str

    @staticmethod
    def get_game_name(table_entry) -> str:
        return table_entry.find_next('td').text.replace(' Maps', '')

    def translate_table(self):
        self.parsed = self.html.findAll('tr')

    def get_game_folder(self):
        path = os.path.join(self.console_folder, self.name)
        self.game_folder = get_or_create_folder(path)

    def translate_map_entry(self, map_entry):
        x = map_entry.findAll('td')
        main_entry = x[0]
        sub_entry = x[1]

        if sub_entry.find('a'):
            href = sub_entry.find('a')['href']
            title = f"{main_entry.text} - {sub_entry.text}"

        elif main_entry.find('a'):
            href = main_entry.find('a')['href']
            title = main_entry.text

        return {
            "title": sanitize_input(title),
            "href": href
        }

    def create_file(self, filepath, response):
        with open(filepath, "wb") as file:
            file.write(response.content)

    def download_maps(self):
        total_maps = len(self.maps)
        i = 0
        for target_map in self.maps:
            i += 1
            target_url = urljoin(self.game_url, target_map['href'])
            postfix = target_url.split('.')[-1]
            filename = f"{sanitize_input(target_map['title'])}.{postfix}"
            map_path = os.path.join(self.game_folder, filename)

            if self.map_already_exists(map_path):
                print(f"Skipping {filename}, as it already exists")
                continue

            try:
                print(f"{i}/{total_maps} - Downloading from {target_url}..", end="")
                r = requests.get(target_url, allow_redirects=True)
                self.create_file(map_path, r)
                print(f"\t Done!")
            except Exception as e:
                print(f"Error! {e}")
                time.sleep(60)
            time.sleep(5)

    def map_already_exists(self, map_path):
        return os.path.isfile(map_path)

    def main(self):
        self.translate_table()
        try:
            self.name = sanitize_input(self.get_game_name(self.parsed[TR_NAME_POS]))
        except IndexError:
            print(f"Something went wrong on a game on {self.game_url}")
            return
        print(f"Starting downloading for {self.name}")
        self.maps = []
        self.get_game_folder()

        for map_entry in self.parsed[TR_GAMES_START:]:
            try:
                self.maps.append(self.translate_map_entry(map_entry))
            except IndexError:
                continue

        self.download_maps()
        print(f"Done downloading for game {self.name}")


class Console():
    def __init__(self, name, url, path):
        self.name = name
        self.url = url
        self.parent_path = path

    def find_all_games(self) -> list:
        self.games = self.soup.findAll('table')

    def get_console_folder(self):
        relative_path = os.path.join(self.parent_path, sanitize_input(self.name))
        self.path = get_or_create_folder(relative_path)

    def main(self):
        print(f"Starting scraping on {self.name}")
        self.get_console_folder()
        response = requests.get(self.url)
        self.soup = BeautifulSoup(response.text, "html5lib")

        self.find_all_games()

        i = 0
        total_games = len(self.games)
        for html_game in self.games:
            i += 1
            print(f"Game {i} of {total_games}")
            x = Game(html_game, self.url, self.path)
            x.main()

        print(f"Finished scraping {self.name}! \n\n")


class MapScraper():

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "-s", "--sources",
            help="Choose which consoles you want to download",
            nargs='+',
            type=str
        )
        self.parser.add_argument(
            "-y", "--yes",
            help="Ignore the confirmation on the start",
            action="store_true"
        )
        self.parser.add_argument('path', type=dir_path)
        self.args = self.parser.parse_args()

    def get_console_list(self):
        self.consoles = {}
        for x in self.soup.findAll("a", class_="r"):
            if x.has_attr('name') and not x.find('img'):
                try:
                    key = x.text
                    self.consoles[key] = urljoin(ATLAS_URL, x['href'])
                except KeyError:
                    pass

    def initialize(self):
        print("\nWelcome to the Mapper snapper!\n")
        skip_confirmation = self.args.yes

        self.target_consoles = {}

        if self.args.sources:
            for c_entry in self.args.sources:
                for console, href in self.consoles.items():
                    if c_entry.lower() in console.lower():
                        self.target_consoles[console] = href
        else:
            self.target_consoles = self.consoles

        print("You are currently attempting the following:")
        for x in self.target_consoles.keys():
            print(x)

        print("Downloading all the consoles above at:")
        print(self.args.path)

        if not skip_confirmation:
            proceed = input("\nDo you wish to proceed? y/n: > ")
            if proceed != 'y':
                sys.exit(1)

    def main(self):
        response = requests.get(ATLAS_URL)
        print(f"Aquiring consoles present on {ATLAS_URL}, please wait..")
        self.soup = BeautifulSoup(response.text, "html5lib")
        self.get_console_list()
        self.initialize()

        i = 0
        total_consoles = len(self.target_consoles)
        for name, url in self.target_consoles.items():
            i += 1
            print(f"Console {i} of {total_consoles}\n")
            console_scraper = Console(name, url, self.args.path)
            console_scraper.main()


if __name__ == "__main__":
    x = MapScraper()
    x.main()
