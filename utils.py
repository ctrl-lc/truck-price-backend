from subprocess import run
from lxutils.read_config import config
from lxutils.log import timer, log
from time import monotonic


def run_scrapy(file, what_to_gauge = ''):
    with timer(f'Running scrapy file {file}'):
        run([config["execs"]["scrapy"], 'runspider', file], encoding='utf-8', check=True)
    if what_to_gauge:
        gauge(what_to_gauge)


def run_prep(label, what_to_gauge = ''):
    file = config['prep'][label]
    with timer(f'Running Tableau Prep file {file}'):
        run([config['execs']['prep'], '-t', file], encoding='utf-8', check=True)
    if what_to_gauge:
        gauge(what_to_gauge)


def run_bigmler(section_label, delimiter=','):
    input_file =    config[section_label]['input_file']
    command =       config[section_label]['command']
    output_file =   config[section_label]['output_file']

    args = [config['execs']['bigmler'],
            *command.split(' '),
            '--test', f'{config["dirs"]["data"]}\\{input_file}',
            '--output', f'{config["dirs"]["data"]}\\{output_file}',
            '--prediction-info', 'full',
            '--prediction-header',
            '--remote',
            '--locale', 'en_US.UTF-8',
            '--test-separator', f'{delimiter}'
            ]
    with timer(f'Running bigmler: {input_file} -> {output_file}'):
        run(args, check=True)
    gauge(output_file)


def gauge(file):
    with open(f'{config["dirs"]["data"]}\\{file}', encoding='utf-8') as f:
        for i, __ in enumerate(f):
            pass
    log(f'{file}: {i} rows')

# Use the application default credentials
import firebase_admin
from firebase_admin import credentials, firestore
firebase_admin.initialize_app()
db = firestore.client()