import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urljoin
import time
import os


ATLAS_URL = "https://vgmaps.com/Atlas/"

TR_IMAGE_POS = 0
TR_NAME_POS = 1
TR_GAMES_START = 2


def sanitize_input(string_input):
    for x in r":/\*?":
        string_input = string_input.replace(x, '_')
    return string_input


def get_or_create_folder(target_folder):
    target_folder = target_folder
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)
        return target_folder
    else:
        return target_folder


@dataclass
class Game:
    html: object
    game_url: str
    console_folder: str

    @staticmethod
    def get_game_name(table_entry) -> str:
        return table_entry.find_next('td').text.rstrip(' Maps')

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

    def create_file(self, target, response):
        type, prefix = response.headers['Content-Type'].split('/')
        filename = sanitize_input(target['title'])
        map_path = os.path.join(self.game_folder, f"{filename}.{prefix}")

        with open(map_path, "wb") as file:
            file.write(response.content)

    def download_maps(self):
        for target_map in self.maps:
            target_url = urljoin(self.game_url, target_map['href'])
            print(f"Downloading from {target_url}..", end="")
            r = requests.get(target_url, allow_redirects=True)

            self.create_file(target_map, r)
            print(f"\t Done!")
            time.sleep(1)

    def main(self):
        self.maps = []
        self.translate_table()
        self.name = sanitize_input(self.get_game_name(self.parsed[TR_NAME_POS]))
        print(f"Starting downloading for {self.name}")
        self.get_game_folder()

        for map_entry in self.parsed[TR_GAMES_START:]:
            self.maps.append(self.translate_map_entry(map_entry))

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
        self.get_console_folder()
        response = requests.get(self.url)
        self.soup = BeautifulSoup(response.text, "html.parser")

        self.find_all_games()

        for html_game in self.games[2:]:
            x = Game(html_game, self.url, self.path)
            x.main()


class MapScraper():

    def get_console_list(self):
        self.consoles = {}
        for x in self.soup.findAll("a", class_="r"):
            if x.has_attr('name') and not x.find('img'):
                key = x.text
                self.consoles[key] = urljoin(ATLAS_URL, x.href)

    def main(self):
        response = requests.get(ATLAS_URL)
        self.soup = BeautifulSoup(response.text, "html.parser")
        self.get_console_list()

        for name, url in self.consoles.items():
            console_scraper = Console(name, url, ".")
            console_scraper.main()

if __name__ == "__main__":
    x = MapScraper()
    x.main()
