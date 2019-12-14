import os
from datetime import datetime
import json


def log(text: str) -> None:
    """ Logs text with a specified style using colorama styles """
    # config.socketio.emit('new_log', {'log': text}, namespace = '/socket')
    # config.latest_log = text
    timestamp = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    print(f"{timestamp} {text}")


def load_mapping():
    return load_json('data/tvdbid_to_malid.json')


def load_json(filepath: str):
    if not os.path.exists(filepath):
        save_json({}, filepath)

    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data, filepath: str):
    with open(filepath, 'w') as f:
        json.dump(data, f)
