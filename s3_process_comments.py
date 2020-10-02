from utils import *
from lxutils import log

for c in config['scrapy_comments'].values():
    run_scrapy(c)

log('Preparing Data for valuation...')
run_prep('comments')
run_bigmler('comments', delimiter=';')
