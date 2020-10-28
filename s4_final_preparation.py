from utils import *
from lxutils import *
import pandas as pd
import shutil
import datetime


def sanity_check():
    df = pd.read_csv(config['files']['final_offers'])
    
    duplicates = df.shape[0] - df.drop_duplicates.shape[0]
    
    if duplicates:
        raise ValueError(f'{duplicates} duplicates in the final file, aborting')


with timer('Downloading ads'):
    import download_ads
with timer('Updating regions file'):
    import update_regions
run_prep('final', what_to_gauge=config['files']['final_offers'])

sanity_check()

log('Backing up the archive') 
shutil.copy(f"{config['dirs']['data']}\\{config['files']['archive_file']}", f"{config['dirs']['archive']}\\{datetime.date.today()}.csv")
gauge(config['files']['archive_file'])