import json
import os


class Config:
    def __init__(self):
        self.libraries = os.environ.get('libraries').split()
        self.server_token = os.environ.get('server_token')
        self.server_url = os.environ.get('server_url')
        self.mal_username = os.environ.get('mal_username')
        self.mal_password = os.environ.get('mal_password')
        self.sync_time = os.environ.get('sync_time')
