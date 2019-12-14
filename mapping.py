import os
import time
import urllib.request
import xml.etree.ElementTree as et
from typing import Optional
from bs4 import BeautifulSoup
from utils import log
import utils


class Mapping:
    def __init__(self, driver):
        self.update_mapping_xml()
        self.xml_tvdb_id_to_anidb_id = et.parse('data/tvdbid_to_anidbid.xml').getroot()
        self.tvdb_id_to_mal_id = self.load_tvdb_id_to_mal_id()
        self.mapping_errors = self.load_mapping_errors()
        self.driver = driver
        self.remove_solved_mapping_errors()

    def load_tvdb_id_to_mal_id(self) -> dict:
        log("Loading tvdb_id to mal_id")
        return utils.load_json('data/tvdbid_to_malid.json')

    def save_tvdb_id_to_mal_id(self) -> None:
        log("Saving tvdb_id to mal_id")
        utils.save_json(self.tvdb_id_to_mal_id, 'data/tvdbid_to_malid.json')

    def load_mapping_errors(self) -> dict:
        log("Loading mapping errors")
        return utils.load_json('data/mapping_errors.json')

    def save_mapping_errors(self) -> None:
        log("Saving mapping errors")
        utils.save_json(self.mapping_errors, 'data/mapping_errors.json')

    def update_mapping_xml(self) -> None:
        if not os.path.exists('data/tvdbid_to_anidbid.xml'):
            self.download_tvdb_anidb_mapping()

        mapping_file_age = time.time() - os.path.getctime('data/tvdbid_to_anidbid.xml')
        # Replace if the old file is 7 days old
        if mapping_file_age >= 603_800:
            self.download_tvdb_anidb_mapping()

    def download_tvdb_anidb_mapping(self) -> None:
        log("Downloading new XML mapping file")
        if os.path.exists('data/tvdbid_to_anidbid.xml'):
            os.remove('data/tvdbid_to_anidbid.xml')

        urllib.request.urlretrieve('https://raw.githubusercontent.com/ScudLee/anime-lists/master/anime-list-full.xml',
                                   'data/tvdbid_to_anidbid.xml')

    def get_mal_id(self, tvdb_id: str, season: str, create: bool = True) -> Optional[str]:
        mal_id = self.tvdb_id_to_mal_id.get(tvdb_id, {}).get(season)
        if mal_id is not None:
            return mal_id

        return self.create_tvdb_id_to_mal_id_mapping(tvdb_id, season) if create else None

    def create_tvdb_id_to_mal_id_mapping(self, tvdb_id: str, season: str):
        log("Creating new anime mapping")
        mal_id = None
        if (anidb_id := self.get_anidb_id_from_tvdb_id(tvdb_id, season)) is not None:
            mal_id = self.get_mal_id_from_anidb_id(anidb_id)

        self.tvdb_id_to_mal_id[tvdb_id] = {**self.tvdb_id_to_mal_id.get(tvdb_id, {}), **{season: mal_id}}
        self.save_tvdb_id_to_mal_id()
        self.remove_solved_mapping_errors()
        return mal_id

    def get_mal_id_from_anidb_id(self, anidb_id: str):
        soup = BeautifulSoup(self.driver.get_html(f'https://anidb.net/anime/{anidb_id}'), 'lxml')
        # Check the two locations for the myanimelist link
        ele = soup.find('a', {'class': 'i_icon i_resource_mal brand'}) or soup.find('a', {'class': 'hide mal'})
        time.sleep(2)
        return ele.get('href').rsplit('/')[-1]

    def get_anidb_id_from_tvdb_id(self, tvdb_id: str, season: str) -> Optional[str]:
        for anime in list(self.xml_tvdb_id_to_anidb_id):
            if anime.get('tvdbid') == tvdb_id and anime.get('defaulttvdbseason') == season:
                return anime.get('anidbid')
        return None

    def add_to_mapping_errors(self, tvdb_id: str, title: str, season: str) -> None:
        self.remove_mapping(tvdb_id, season)

        error = self.mapping_errors.get(tvdb_id, {'title': title, 'seasons': []})
        if season not in error.get('seasons'):
            error['seasons'].append(season)
            self.mapping_errors[tvdb_id] = error
            self.save_mapping_errors()

    def remove_mapping(self, tvdb_id: str, season: str) -> None:
        if season in self.tvdb_id_to_mal_id[tvdb_id].keys():
            self.tvdb_id_to_mal_id[tvdb_id][season] = None
            self.save_tvdb_id_to_mal_id()

    def remove_solved_mapping_errors(self):
        log("Checking mapping errors")
        changed = False
        for tvdb_id, data in self.mapping_errors.items():
            for i, season in enumerate(data.get('seasons')):
                if self.get_mal_id(tvdb_id, season, create = False) is not None:
                    changed = True
                    self.mapping_errors[tvdb_id]['seasons'].pop(i)

        if changed:
            self.mapping_errors = {k: v for k, v in self.mapping_errors.items() if len(v['seasons']) > 0}
            self.save_mapping_errors()
