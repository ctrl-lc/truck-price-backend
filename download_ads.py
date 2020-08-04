import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import datetime, urllib

from lxutils import *
from tqdm import tqdm
from utils import db

log('Берем проверенные документы')

ads = []

docs = db.collection('ads').where('checked', '==', False).stream()
for doc in tqdm(docs):
    d = doc.to_dict()
    d['url'] = urllib.parse.unquote(doc.id)
    ads.append(d)

log('Берем непроверенные документы')

docs = db.collection('ads').where('checked', '==', True).stream()
for doc in tqdm(docs):
    d = doc.to_dict()
    d['url'] = urllib.parse.unquote(doc.id)
    ads.append(d)

log('Сохраняем все документы')

ads_file = f'{config["dirs"]["data"]}\\{config["files"]["ads"]}'
pd.DataFrame(ads).to_csv(ads_file, index=False)

log('Берем все проверки')

docs = db.collection_group('verifications').stream()
ads = []
for doc in tqdm(docs):
    d = doc.to_dict()
    d['url'] = urllib.parse.unquote(doc.reference.parent.parent.id)
    ads.append(d)

log('Сохраняем все проверки')

verifications_file = f'{config["dirs"]["data"]}\\{config["files"]["verifications"]}'
pd.DataFrame(ads).to_csv(verifications_file, index=False)

log('Успешно закончено')

# на будущее - более быстрое чтение будет при помощи Firebase Admin SDK
# (https://firebase.google.com/docs/firestore/client/libraries#server_client_libraries)
