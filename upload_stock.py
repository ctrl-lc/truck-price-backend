import gspread, pprint, sys, datetime, codecs, pandas as pd

from oauth2client.service_account import ServiceAccountCredentials

from lxutils import *

# сортируем и кладем в full_stock1.csv

log ('Reading full_stock.csv and sorting by benefit')
df = pd.read_csv(config['dirs']['data'] + '/full_stock.csv', sep = ';')
df.sort_values(by=[u'Выгода'], ascending=False, inplace=True)
df.to_csv (config['dirs']['data'] + '/full_stock1.csv', index=False)
log (f'{df.shape[0]} lines written to full_stock1.csv')

# загружаем в файл стоков на Google Spreadsheets

with timer('Loading stocks to Google Sheets'):
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('robotic-rampart-255014-e2f22bfae60e.json', scope)

    gc = gspread.authorize(credentials)

    content = codecs.open(config['dirs']['data'] + '/full_stock1.csv', 'r', 'utf-8').read()
    gc.import_csv("1Hcc4ay2SZu1gImUljdbTVgw3GEaJrz-7IerNWcZDRzU", content.encode('utf-8')) # новая версия - этой ссылки нет у МЛК