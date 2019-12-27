from typing import Optional

from animeList import ListAnime
from plexConnection import PlexAnime


class UpdateData:
    def __init__(self, plex_anime: PlexAnime, list_anime: Optional[ListAnime]):
        self.mal_id = plex_anime.mal_id
        self.tvdb_id = plex_anime.tvdb_id
        self.title = plex_anime.title
        self.season = plex_anime.season_number

        self.plex_watched_episodes = plex_anime.watched_episodes
        self.myanimelist_total_episodes = list_anime.total_episodes if list_anime is not None else None
        self.watched_episodes = plex_anime.watched_episodes
        self.update_watched_episodes()

        self.myanimelist_watched_episodes = list_anime.watched_episodes if list_anime is not None else None
        self.status = None
        self.update_status()

    def set_plex_watched_episodes(self, plex_watched_epsiodes: int):
        self.plex_watched_episodes = plex_watched_epsiodes
        self.update_watched_episodes()

    def set_myanimelist_total_episodes(self, myanimelist_total_episodes: int):
        self.myanimelist_total_episodes = myanimelist_total_episodes
        self.update_status()
        self.update_watched_episodes()

    def equate_watched_episodes(self, watched_episodes: int, total_episodes: int):
        return min(watched_episodes, total_episodes) if total_episodes != -1 else watched_episodes

    def update_watched_episodes(self):
        if self.myanimelist_total_episodes is None:
            self.watched_episodes = self.plex_watched_episodes
            return

        self.watched_episodes = self.equate_watched_episodes(self.plex_watched_episodes,
                                                             self.myanimelist_total_episodes)

    def equate_watch_status(self, myanimelist_total_episodes: int):
        if self.watched_episodes >= myanimelist_total_episodes:
            return 'completed'

        elif self.watched_episodes == 0:
            return 'plan to watch'

        else:
            return 'watching'

    def update_status(self):
        if self.myanimelist_total_episodes is None:
            self.status = None
            return

        self.status = self.equate_watch_status(self.myanimelist_total_episodes)
