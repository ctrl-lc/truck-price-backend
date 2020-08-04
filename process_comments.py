from utils import *
from lxutils import log

for c in config['datacol_comments']:
    run_datacol(c)

log('Preparing Data for valuation...')
run_prep('comments')
run_bigmler('comments', delimiter=';')
