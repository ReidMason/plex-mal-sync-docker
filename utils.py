import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as et

import requests
from bs4 import BeautifulSoup
from colorama import Style, Fore

from config import MAPPING_AGE


def log(text, *style):
  """ Logs text with a specified style using colorama styles """
  # print(text)
  sys.stdout.write((''.join(style) + text).ljust(100) + Style.RESET_ALL)
  sys.stdout.flush()


def load_json(filepath):
  """ Opens json files and returns the parsed data.

  :param filepath: File path to the json file.
  :return: Parsed json data file.
  """
  # Create file if it doesn't exist and return a blank dictionary
  if not os.path.exists(filepath):
    with open(filepath, 'w') as f:
      f.write('{}')
      return {}

  # Load from existing file
  with open(filepath, 'r') as f:
    return json.load(f)


def save_json(data, filepath):
  """ Saved data to a json file at the specified file path

  :param data: The data to write to the json file.
  :param filepath: The path where the json file will be saved.
  """
  with open(filepath, 'w') as f:
    json.dump(data, f)


def get_watch_status(total_episodes, episodes_watched):
  """ Decide what watch status an anime should have.

  :param total_episodes: Number of total episodes in the anime.
  :param episodes_watched: Number of episodes watched.
  :return: String representing the watch status of the anime
  """
  status = 'To watch'

  if episodes_watched != 0:
    status = 'Watching'

  if total_episodes > 0 and total_episodes <= episodes_watched:
    status = 'Completed'

  return status


def add_to_error_log(title, tvdbid, season):
  """ Adds an entry to the error log to inform on any manual mappings that need to be done.

  :param title: The title of the anime causing the error.
  :param tvdbid: The tvdb id for the anime causing the error.
  :param season: The season number for the anime causing the error.
  """
  errors = load_json('data/errors.json')
  if not tvdbid in errors:
    errors[tvdbid] = {'title': title}
  errors[tvdbid]['season'] = season
  save_json(errors, 'data/errors.json')


def get_tvdb_anidb_mapping():
  """ Load the tvdb id to anidb id mapping xml file.

  If the xml file with the mapping is older than the specified date then it will be re-downloaded.

  :return: xml object containing the mapping data for the tvdb and anidb ids.
  """
  mapping_path = 'data/anime-list-full.xml'

  if not os.path.exists(mapping_path):
    download_tvdb_anidb_mapping()

  creation_time = os.path.getctime(mapping_path)
  age = time.time() - creation_time
  if age >= MAPPING_AGE * 86400:
    os.remove('data/anime-list-full.xml')
    download_tvdb_anidb_mapping()

  return et.parse(mapping_path).getroot()


def download_tvdb_anidb_mapping():
  """ Downloads the latest tvdb id to anidb id mapping file from the github repo. """
  log('\nDownloading new tvdb myanimelist mapping file', Fore.CYAN)
  urllib.request.urlretrieve('https://raw.githubusercontent.com/ScudLee/anime-lists/master/anime-list-full.xml',
                             'data/anime-list-full.xml')
  log('\rDownloaded new tvdb myanimelist mapping file', Fore.GREEN)


def get_myanimelist_id(anidb_id, driver):
  """ Gets the myanimelist id from the anidb page for the anime.

  :param anidb_id: The anidb id for the anime.
  :param driver: A chromedriver for loading the anime page.
  :return: Returns the myanimelist id as a string.
  """
  # When the anidb_id couldn't be found
  if anidb_id == None:
    return None

  url = 'https://anidb.net/perl-bin/animedb.pl?show=anime&aid=' + anidb_id
  soup = BeautifulSoup(driver.get_html(url), 'lxml')

  # Check the two locations for the myanimelist link
  ele = soup.find('a', {'class': 'i_icon i_resource_mal brand'})
  if ele is None:
    ele = soup.find('a', {'class': 'hide mal'})

  return ele.get('href').lstrip('https://myanimelist.net/anime/')


def find_anidb_id(tvdb_anidb_mapping, tvdbid, season):
  """ Gets the anifb id from the tvdb id to anidb id mapping.

  :param tvdb_anidb_mapping: The mapping data for tvdb id to anidb id.
  :param tvdbid: The tvdb id for the anime.
  :param season: The season number for the anime being requested.
  :return: The anidb id as a string or if it isn't found then None.
  """
  for type in tvdb_anidb_mapping.findall('anime'):
    if type.get('tvdbid') == str(tvdbid) and type.get('defaulttvdbseason') == str(season):
      return type.get('anidbid')

  return None


def get_mal_data_from_id(mal_id):
  """ Gets anime data from myanimelist api

  :param mal_id: The id of the anime to get data for.
  :return: A dictionary containing information about the anime.
  """
  return requests.get(f'https://api.jikan.moe/v3/anime/{mal_id}/').json()
