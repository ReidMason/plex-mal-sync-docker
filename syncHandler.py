from plexConnection import PlexConnection, PlexAnime
from utils import log
from config import Config
from animeList import AnimeList, ListAnime
from driver import Driver
from mapping import Mapping


def get_watch_status(plex_anime: PlexAnime, list_anime: ListAnime):
    watched_episodes = get_watched_episodes(plex_anime.watched_episodes, list_anime.total_episodes)
    if watched_episodes == list_anime.total_episodes:
        return 'completed'

    elif watched_episodes == 0:
        return 'plan to watch'

    else:
        return 'watching'


def get_watched_episodes(watched_episodes: int, total_episodes: int):
    return min(watched_episodes, total_episodes) if total_episodes != -1 else watched_episodes


def update_required(plex_anime, list_anime):
    plex_we = plex_anime.watched_episodes
    list_we = list_anime.watched_episodes
    list_te = list_anime.total_episodes

    # Conditions for needing to be updated
    anime_not_listed = list_anime is None
    anime_list_behind = (list_we < plex_we) and (plex_we <= list_te or list_te == -1)
    anime_completed = plex_we >= list_te != -1 and list_anime.status != 'completed'

    return anime_not_listed or anime_completed or anime_list_behind


def get_update_data(plex_anime: PlexAnime, list_anime: ListAnime):
    return {'mal_id'          : plex_anime.mal_id,
            'tvdb_id'         : plex_anime.tvdb_id,
            'title'           : plex_anime.title,
            'season'          : plex_anime.season_number,
            'watched_episodes': get_watched_episodes(plex_anime.watched_episodes, list_anime.total_episodes),
            'status'          : get_watch_status(plex_anime, list_anime)}


def apply_update(update: dict, config: Config, mapping: Mapping, driver: Driver):
    log(f"Updating series {update.get('title')}")
    if not driver.login_myanimelist(config.mal_username, config.mal_password):
        log("Failed to log into MyAnimeList")
        return

    # Load the anime page
    if not driver.load_anime_page(update.get('mal_id')):
        log("Error can't load page with that mal id")
        mapping.add_to_mapping_errors(update.get('tvdb_id'), update.get('title'), update.get('season'))
        return

    log("Filling in information")
    driver.add_to_list()
    driver.select_watch_status(update.get('status'))
    driver.enter_episodes_seen(update.get('watched_episodes'))
    driver.confirm_update()


def start_sync(config: Config):
    driver = Driver()
    mapping = Mapping(driver)
    plex_connection = PlexConnection(config.server_url, config.server_token, mapping)
    anime_list = AnimeList(config.mal_username)

    # Sync selected libraries
    for plex_library in config.libraries:
        for show in plex_connection.get_shows(plex_library):
            list_anime = anime_list.get_anime(show.mal_id)
            if list_anime is not None and update_required(show, list_anime):
                apply_update(get_update_data(show, list_anime), config, mapping, driver)

    driver.quit()
    log("Sync complete")
