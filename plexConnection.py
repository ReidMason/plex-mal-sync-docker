from plexapi.server import PlexServer

from animeList import AnimeList
from utils import log, load_mapping
from typing import Optional
from mapping import Mapping


class PlexConnection(PlexServer):
    def __init__(self, server_url: str, server_token: str, mapping: Mapping) -> None:
        """ Connects to plex server with the given url and token.
        :param server_url: The url to the target plex server.
        :param server_token: The token for the target server.
        """
        log("Connecting to plex server")
        super().__init__(server_url, server_token)
        self.mapping = mapping
        log("Plex connection established")

    def get_shows(self, library: str) -> Optional[list]:
        """ Gets all the shows in a given library.
        :param library: The name of the target library.
        :return: A list of Show objects from the target library.
        """
        log(f"Getting shows for library {library}")
        shows = []
        if library in [x.title for x in self.library.sections()]:
            for media in self.library.section(library).all():
                shows.extend(self.create_anime_season_objects(media))

        return shows

    def create_anime_season_objects(self, anime_show):
        tvdbid = anime_show.guid.rsplit('/')[-1].split('?')[0]
        return [PlexAnime(anime_show.title, tvdbid, x, self.mapping) for x in anime_show.seasons() if
                x.title.lower() != 'specials']


class PlexAnime:
    def __init__(self, title: str, tvdbid: str, show_data, mapping: Mapping) -> None:
        self.mapping = mapping
        self.title = f"{title} {show_data.title}"
        self.watched_episodes = len([x for x in show_data.episodes() if x.isWatched])
        self.tvdb_id = tvdbid
        self.season_number = str(show_data.seasonNumber)
        log(f"Loading anime {self.title}")
        self.mal_id = self.mapping.get_mal_id(self.tvdb_id, self.season_number)

        # If mal_id isn't found add the anime to the mapping errors
        if self.mal_id is None:
            mapping.add_to_mapping_errors(self.tvdb_id, self.title, self.season_number)

    def __repr__(self):
        return f"Title: {self.title}\n  tvdb_id: {self.tvdb_id}\n  mal_id: {self.mal_id}\n  Watched episodes: {self.watched_episodes}"
