# Mapsnapper

# Intro
Mapsnapper is a video game map downloader. After a few suggestions from the well recieved [ScrapingManAss](https://github.com/OlavStornes/Scraping-Manual-Assistant), i decided to give it a try to get as many VG-maps as well.

# Design
Mapsnapper shamelessly downloads all maps from [The Video Game Atlas](https://vgmaps.com/Atlas/). The maps are then sorted in folders respective of their console and game (example further down)


# Usage

* `--help -h` : Shows the help menu
* `--source -s` : Match which consoles you would like to download from
* `--yes -y` : Start without a confirmation


## Arguments
The option `-s` accepts an arbitrary amount of inputs. This is an inclusive search, so you will retrieve all consoles that has whatever variable you decide to put in  

### Example:

* `python ./main.py -s windows` 
* `python ./main.py -s nes ios`

## Folder layout:

`/{CONSOLE}/{GAME}/{MAIN_SECTION} - {SUB_SECTION}.{POSTFIX}`


# Requirements
## Python packages
* Beautifulsoup4
* Requests
* html5lib

# Potential improvements

As this project has satisfied my needs, i dont see an immediate need to further improve on it. However, there are a few things that could be better

* An improved console filter
* Filter by game
