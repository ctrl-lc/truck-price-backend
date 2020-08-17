from lxutils import *
from utils import *

[run_scrapy(c) for c in config['scrapy_main'].values()]
run_prep('parse_offers')