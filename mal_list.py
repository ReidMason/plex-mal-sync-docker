import json

import requests
from bs4 import BeautifulSoup

import utils


class MalList:
    def __init__(self, username):
        """ Loads the list from myanimelist """
        url = f'https://myanimelist.net/animelist/{username}?status=7'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')

        self.list_data = json.loads(soup.find('table', {'class', 'list-table'}).get('data-items'))

    def get_anime(self, mal_id):
        """ Search for anime with matching id from the list.

        :param mal_id: The id of the anime being looked for.
        :return: Dictionary containing the data for the anime.
        """
        for anime in self.list_data:
            if anime['anime_id'] == int(mal_id):
                # True return because anime was in list
                return True, anime

        # If matching anime wasn't on list then request the data
        # False return because anime isn't in list
        return False, utils.get_mal_data_from_id(mal_id)
