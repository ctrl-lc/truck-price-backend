from lxutils import config
from lxutils.log import log
from utils import *
from os import remove

def clear_scrapy_result_files():
    files_to_remove = [
        'autoru - trucks.csv',
        'autoru - trailers.csv',
        'comments - auto.ru - results.csv',
        'drom - trucks.csv',
        'comments - drom - results.csv'
    ]
    for f in files_to_remove:
        try:
            remove(config['dirs']['data'] + '\\' + f)
            log(f"File '{f}' deleted'")
        except:
            log(f"File '{f}' not found'")


clear_scrapy_result_files()
[run_scrapy(c) for c in config['scrapy_main'].values()]
run_prep('parse_offers')