from utils import *
from lxutils import *
import pandas as pd
import shutil
import os
import datetime

with timer('Downloading ads'):
    import download_ads
with timer('Updating regions file'):
    import update_regions
run_prep('final', what_to_gauge=config['files']['final_offers'])

log('Backing up the archive') 
shutil.copy(f"{config['dirs']['data']}\\{config['files']['archive_file']}", f"{config['dirs']['archive']}\\{datetime.date.today()}.csv")
gauge(config['files']['archive_file'])

with timer('Uploading ads to Google Sheets'):
    import upload_stock
with timer('Uploading verification data to Google Firestore'):
    import upload_verification