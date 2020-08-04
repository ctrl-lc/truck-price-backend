from lxutils import *
from utils import *

[run_datacol(c) for c in config['datacol_main'].values()]
run_prep('parse_offers')