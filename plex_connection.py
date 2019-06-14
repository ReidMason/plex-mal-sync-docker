from colorama import Fore
from plexapi.server import PlexServer

import utils
from config import LIBRARY
from utils import log


class PlexConnection:
  def __init__(self, server_url, server_token):
    """ Connects to plex server with the given url and token.

    :param server_url: The url to the target plex server.
    :param server_token: The token for the target server.
    """
    log('\nConnecting to plex server', Fore.CYAN)
    self.server = PlexServer(server_url, server_token)
    log('\rConnected to plex server', Fore.GREEN)
    self.tvdb_myanimelist_mapping = utils.load_json('data/tvdb_myanimelist_mapping.json')
    self.tvdb_anidb_mapping = utils.get_tvdb_anidb_mapping()

  def get_shows(self, library):
    """ Gets all the shows in a given library.

    :param library: The name of the target library.
    :return: A list of Show objects from the target library.
    """
    return self.server.library.section(library).all()

  def get_watched_episodes(self, library):
    """ Get a dictionary of all shows in a library with the episodes watched in each season of the show

    :param library: The name of the target library.
    :return: A dictionary with the episodes watched for each season in a show.
    """
    data = {}
    for show in self.get_shows(library):
      # Get all seasons excluding specials
      seasons = list(filter(lambda x: 'Specials' not in x.title, show.seasons()))
      data[show.title] = {s.seasonNumber: len([x for x in s if x.isWatched]) for s in seasons}

    return data

  def get_show_tvdbid(self, show):
    """ Gets the tvdb id of the passed show.

    :param show: A Show object to get the tvdbid from.
    :return: The tvdb id for the target Show.
    """
    return show.guid.split('//', 1)[1].rstrip('?lang=en')

  def create_mapping(self, show, season, driver):
    """ Creates a mapping from tvdb id to the mal id.

    Using the tvdb to anidb mapping the corresponding anidb id is found.
    If there is no tvdb to anidb mapping it is added to the error log for manual entry.
    The anidb page is loaded and then the myanimelist id is scraped from there.

    :param show: Show object for the show to map.
    :param season: The season number to create the mapping for.
    :param driver: A chromedriver to get the myanimelist link from anidb.
    """
    tvdbid = self.get_show_tvdbid(show)
    anidb_id = utils.find_anidb_id(self.tvdb_anidb_mapping, tvdbid, season)
    myanimelist_id = utils.get_myanimelist_id(anidb_id, driver)

    # If the myanimelist id could not be found then it needs to logged so I can add the mapping manually
    if myanimelist_id is None:
      log(f"Error: No mapping for anime '{show.title}' tvdbid: {tvdbid} season: {season}", Fore.RED)
      utils.add_to_error_log(show.title, tvdbid, season)

    self.tvdb_myanimelist_mapping[tvdbid][season] = str(myanimelist_id)

  def update_tvdbid_myanimelist_mappings(self, driver):
    """ Checks the tvdb id to myanimelist id mapping and create mappings for any unmapped ones.

    :param driver: A chromedriver to pass into the create_mapping function.
    :return: New list of updated mappings.
    """
    for show in self.get_shows(LIBRARY):
      # Extract the tvdbid
      tvdbid = self.get_show_tvdbid(show)
      season_numbers = [str(x.seasonNumber) for x in show.seasons() if 'Season' in x.title]

      # If mapping isn't defined add a blank value
      if not tvdbid in self.tvdb_myanimelist_mapping:
        self.tvdb_myanimelist_mapping[tvdbid] = {}

      # Check if each season has a mapping
      for season in season_numbers:
        if self.tvdb_myanimelist_mapping[tvdbid].get(season) in [None, 'None']:
          self.create_mapping(show, season, driver)

      # Save new mapping info
      utils.save_json(self.tvdb_myanimelist_mapping, 'data/tvdb_myanimelist_mapping.json')
    return self.tvdb_myanimelist_mapping
