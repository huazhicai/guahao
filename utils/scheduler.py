import os
import time
import schedule
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ext_register import CrawlGuaHao
from combine import Combination
from backup import Backup
from start import run_114yygh, run_114gh

crawl = CrawlGuaHao()
combine = Combination()
backup = Backup()

schedule.every().day.at("14:40").do(crawl.main)
schedule.every().day.at("16:40").do(combine.save_to_mongo)
schedule.every().sunday.at("10:30").do(backup.backup_data)

# 每周更新医院肾内科
schedule.every().monday.at("00:00").do(run_114yygh)
schedule.every().monday.at("00:30").do(run_114gh)

while True:
    schedule.run_pending()
    time.sleep(30)


