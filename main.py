import time
import schedule
from config import Config
from syncHandler import start_sync

if __name__ == '__main__':
    config = Config()
    schedule.every().day.at(config.sync_time).do(lambda: start_sync(config))
    start_sync(config)

    while True:
        schedule.run_pending()
        time.sleep(1)  # wait one minute
