# MyAnimeList login info
import os

MAL_USERNAME = os.environ['MAL_USERNAME']
MAL_PASSWORD = os.environ['MAL_PASSWORD']

# Plex server info
SERVER_TOKEN = os.environ['SERVER_TOKEN']
SERVER_URL = os.environ['SERVER_URL']

# Plex library name to scan
LIBRARY = 'Anime'

# Max age of tvdb to anidb mapping file in days
MAPPING_AGE = 7

# Default location for chromedriver and ublock
dir_path = os.path.dirname(os.path.realpath(__file__))
# UBLOCK_PATH = os.path.join(dir_path, 'tools/ublock')
CHROMEDRIVER_PATH = os.path.join(dir_path, 'tools/chromedriver.exe')
