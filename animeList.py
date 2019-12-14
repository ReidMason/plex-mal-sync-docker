import json
from typing import Optional

import requests
from bs4 import BeautifulSoup
from pprint import pprint


class ListAnime:
    def __init__(self, watchlist_data: dict) -> None:
        self.title = watchlist_data.get('anime_title')
        self.id = str(watchlist_data.get('anime_id'))
        self.total_episodes = self.set_total_episodes(watchlist_data.get('anime_num_episodes'))
        self.watched_episodes = watchlist_data.get('num_watched_episodes')
        self.status = self.convert_status(watchlist_data.get('status'))

        self.data = watchlist_data

    def convert_status(self, status_number: int) -> str:
        status_conversion = {1: 'watching',
                             2: 'completed',
                             3: 'on hold',
                             4: 'dropped',
                             6: 'plan to watch'}
        return status_conversion.get(status_number)

    def set_total_episodes(self, total_episodes: int) -> int:
        return total_episodes if total_episodes != 0 else -1

    def get_watchlist_data(self):
        return self.data

    def __repr__(self) -> str:
        return f"Title: {self.title}\n  " \
               f"id: {self.id}\n  " \
               f"watched episodes: {self.watched_episodes}\n  " \
               f"total episodes: {self.total_episodes}"


class AnimeList:
    def __init__(self, username: str) -> None:
        self.username = username
        self.anime_list = self.scrape_anime_list()

    def scrape_anime_list(self) -> list:
        r = requests.get(f"https://myanimelist.net/animelist/{self.username}?status=7")
        soup = BeautifulSoup(r.content, 'lxml')
        watchlist_data = json.loads(soup.find('table', {'class': 'list-table'}).get('data-items'))

        anime_list = []
        for data in watchlist_data:
            anime_list.append(ListAnime(data))

        return anime_list

    def get_anime(self, mal_id: str) -> Optional[ListAnime]:
        for anime in self.anime_list:
            if anime.id == mal_id:
                return anime
        return None
