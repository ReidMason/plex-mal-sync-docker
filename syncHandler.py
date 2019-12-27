from plexConnection import PlexConnection, PlexAnime
from updateData import UpdateData
from utils import log
from config import Config
from animeList import AnimeList
from driver import Driver
from mapping import Mapping


def update_required(plex_anime, list_anime):
    plex_we = plex_anime.watched_episodes
    list_we = list_anime.watched_episodes
    list_te = list_anime.total_episodes

    # Conditions for needing to be updated
    anime_not_listed = list_anime is None
    anime_list_behind = (list_we < plex_we) and (plex_we <= list_te or list_te == -1)
    anime_completed = plex_we >= list_te != -1 and list_anime.status != 'completed'

    return anime_not_listed or anime_completed or anime_list_behind


def enter_watch_status(update: UpdateData, driver: Driver):
    if update.status is None:
        update.set_myanimelist_total_episodes(driver.get_total_episodes())

    driver.select_watch_status(update.status)


def apply_update(update: UpdateData, config: Config, mapping: Mapping, driver: Driver):
    log(f"Updating series {update.title}")
    if not driver.login_myanimelist(config.mal_username, config.mal_password):
        log("Failed to log into MyAnimeList")
        return

    if update.mal_id is None:
        log(f"No id for {update.title}")
        return

    # Load the anime page
    if not driver.load_anime_page(update.mal_id):
        log("Error can't load page with that mal id")
        mapping.add_to_mapping_errors(update.tvdb_id, update.title, update.season)
        return

    log("Filling in information")
    driver.add_to_list()
    enter_watch_status(update, driver)
    driver.enter_episodes_seen(update.watched_episodes)
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
            if list_anime is None or update_required(show, list_anime):
                apply_update(UpdateData(show, list_anime), config, mapping, driver)

    driver.quit()
    log("Sync complete")
