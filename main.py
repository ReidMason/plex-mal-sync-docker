import schedule
import time
from sync_handler import do_sync

do_sync()

schedule.every().day.at("19:00").do(do_sync)

while True:
  schedule.run_pending()
  time.sleep(60)  # wait one minute
