from colorama import Fore, init
from selenium.webdriver.common.keys import Keys

import utils
from config import SERVER_TOKEN, SERVER_URL, LIBRARY
from driver import Driver
from mal_list import MalList
from plex_connection import PlexConnection
from utils import log

# Initialise colorama
init()

# Connect to plex server
PLEX_SERVER = PlexConnection(SERVER_URL, SERVER_TOKEN)

driver = Driver()

TVDB_MYANIMELIST_MAPPING = PLEX_SERVER.update_tvdbid_myanimelist_mappings(driver)
MAL_LIST = MalList('SkippyTheSnake')


def get_shows_to_update():
  """
  Cross referenced the myanimelist list and the episodes watched on plex.

  Any discrepancies are added to a list to be updated and returned.
  If no required updates are found an empty dictionary is returned.
  """
  to_update = {}
  log(f"\nChecking for required updates", Fore.CYAN)
  for show in PLEX_SERVER.get_shows(LIBRARY):
    tvdbid = PLEX_SERVER.get_show_tvdbid(show)
    for season in [x for x in show.seasons() if 'Season' in x.title]:
      log(f"\rChecking for updates on {show.title} season {season.seasonNumber}", Fore.CYAN)
      # Get details for the season
      episodes_watched = len([x for x in season if x.isWatched])
      mal_id = TVDB_MYANIMELIST_MAPPING[tvdbid][str(season.seasonNumber)]
      # If there is no mapping print and error
      if mal_id in [None, "None"]:
        log(f"\rNo mapping found for {show.title} season {season.seasonNumber}. Check the error file.", Fore.YELLOW)
        log("\n")
        continue
      on_list, anime_data = MAL_LIST.get_anime(mal_id)

      status = utils.get_watch_status(anime_data.get('anime_num_episodes', 0), episodes_watched)

      # Add shows to be updated
      # Status 2 = Completed
      if not on_list or anime_data.get('status') != 2 and episodes_watched > anime_data.get('num_watched_episodes', 0):
        to_update[mal_id] = {'episodes_watched': episodes_watched,
                             'status': status,
                             'title': show.title}

  # Create list of titles for shows to update
  update_titles = '.'
  if len(to_update) > 1:
    update_titles = ':\n  ' + '\n  '.join([x.get('title') for x in to_update.values()])
  log(f"\rUpdate scan complete. {len(to_update)} updates required{update_titles}", Fore.GREEN)
  return to_update


def update_on_mal(driver, mal_id, data):
  """
  Update myanimelist with the new data for the show.

  :param driver: A chromedriver instance for interacting with myanimelist.
  :param mal_id: The id for the anime that needs to be updated.
  :param data: The update information for the anime.
    This is a dictionary in the structure {'status': 'Watched', 'episodes_watched': 12}
  """
  url = f"https://myanimelist.net/anime/{mal_id}"
  driver.get(url)

  # Click the add to list button
  if driver.element_exists('#showAddtolistAnime'):
    driver.click('#showAddtolistAnime')

  # Set watching status
  status = data.get('status')
  status_maps = {'Completed': 2, 'Watching': 1, 'To watch': 5}
  driver.click(f'#myinfo_status > option:nth-child({status_maps.get(status)})')
  # Enter eps seen
  driver.send_keys('#myinfo_watchedeps', [Keys.CONTROL, 'a'])
  driver.send_keys('#myinfo_watchedeps', data.get('episodes_watched'))

  # Click add or update button
  if driver.element_exists('.js-anime-add-button'):
    driver.click('.js-anime-add-button')
  else:
    driver.click('.js-anime-update-button')


to_update = get_shows_to_update()

# If there are shows to update then login
if len(to_update) > 0:
  driver.myanimelist_login()

  # Update all shows that need updating
  log(f"\nUpdating shows 0/{len(to_update)}", Fore.CYAN)
  i = 0
  for mal_id, data in to_update.items():
    i += 1
    log(f"\rUpdating shows {i}/{len(to_update)}", Fore.CYAN)
    update_on_mal(driver, mal_id, data)

  log(f"\rUpdates complete", Fore.GREEN)
driver.quit()
