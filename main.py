import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urljoin
import time
import os

TMP_URL = 'https://vgmaps.com/Atlas/Neo-Geo/'
TMP_NAME = "CONSOLE"

TR_IMAGE_POS = 0
TR_NAME_POS = 1
TR_GAMES_START = 2


def get_or_create_folder(target_folder):
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)
    else:
        return target_folder


@dataclass
class Game:
    html: object
    game_url: str

    @staticmethod
    def get_game_name(table_entry) -> str:
        return table_entry.find_next('td').text.rstrip(' Maps')

    @staticmethod
    def sanitize_input(string_input):
        for x in r":/\*?":
            string_input.replace(x, '_')
        return string_input

    def translate_table(self):
        self.parsed = self.html.findAll('tr')


    def translate_map_entry(self, map_entry):
        x = map_entry.findAll('td')
        main_entry = x[0].find('a')
        sub_entry = x[1].find('a')

        if sub_entry:
            href = sub_entry['href']
            title = f"{main_entry.text}{sub_entry.text}"

        elif main_entry:
            href = main_entry['href']
            title = main_entry.text

        return {
            "title": self.sanitize_input(title),
            "href": href
        }

    def create_file(self, target, response):
        type, prefix = response.headers['Content-Type'].split('/')
        filename = target['href']

        with open(filename, "wb") as file:
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
        self.name = self.sanitize_input(self.get_game_name(self.parsed[TR_NAME_POS]))
        for map_entry in self.parsed[TR_GAMES_START+1:]:
            self.maps.append(self.translate_map_entry(map_entry))

        self.download_maps()


class Console():
    def __init__(self, name, url, path):
        self.name = name
        self.url = url
        self.parent_path = path

    def find_all_games(self) -> list:
        self.games = self.soup.findAll('table')

    def get_console_folder(self):
        os.path.join(self.parent_path, self.name)
        self.path = get_or_create_folder()

    def main(self):
        response = requests.get(self.url)
        self.soup = BeautifulSoup(response.text, "html.parser")

        self.find_all_games()

        for html_game in self.games:
            x = Game(html_game, self.url, self.path)
            x.main()



class MapScraper():
    def main(self):
        tmp_console = Console(TMP_NAME, TMP_URL, ".")
        tmp_console.main()


if __name__ == "__main__":
    x = MapScraper()
    x.main()
