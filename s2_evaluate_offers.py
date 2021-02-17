from lxutils.log import log
from utils import *

for e in [e for e in config.sections() if e.find('evaluate_') != -1]:
    run_bigmler(e, delimiter=';')

log('Preparing tasks for comment parsing...')
run_prep('evaluate_offers')