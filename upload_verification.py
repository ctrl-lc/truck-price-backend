import pandas as pd
import datetime, urllib
from tqdm import tqdm

from lxutils import *
from utils import db

# удаление всех прошлых автоматических верификаций

log('Deleting old automatic verifications...')
i = 0
docs = db.collection_group('verifications').where('confidence', '<', 1).stream()
for d in tqdm(docs):
    d.reference.delete()
    i += 1

# Добавляем в базу результаты автоматической верификации
log('Adding new automatic verification results...')

r = pd.read_csv(config['dirs']['data'] + '/comments evaluated.csv')
i = 0
for val in tqdm(enumerate(r.iterrows()), total=r.shape[0]): 
    v = val[1][1]
    try: 
        ad_data = {
            'comment': v['Comment'],
            'vehicleType': v['VehicleType'],
            'make': v['Make'],
            'year': v['Year'],
            'supplierPrice': v['Price'],
            'mileage': v['Mileage'],
            'supplier': v['Supplier'],
            'valuation': v['Price 1'],
            'benefit': v['Benefit']
        }

        verification_data = {
            u'date': datetime.datetime.now(),
            u'user': u'auto',
            u'result': v["Result"],
            u'confidence': v['confidence']
        }

        doc_name = urllib.parse.quote(v['URL'], safe='')
        doc_ref = db.collection(u'ads').document(doc_name)

        try:
            doc = doc_ref.get()
            if not "checked" in doc.to_dict():
                ad_data['checked'] = False
        except:
            ad_data['checked'] = False

        doc_ref.set (ad_data, merge = True)
        doc_ref.collection(u'verifications').add(verification_data)
        i += 1
    except:
        log('Exception caught (probably no URL)')

# удаление всех объявлений, у которых нет верификаций - было нужно после сбоев в загрузке

log ('Deleting documents without verifications...')
i = 0
docs = db.collection('ads').stream()
for d in tqdm(docs):
    verifications = d.reference.collection('verifications').stream()
    try:
        _ = next(verifications)
    except:
        d.reference.delete()
        i += 1
log ('{} deleted.'.format(i))

# на будущее - более быстрая запись будет при помощи Firebase Admin SDK
# (https://firebase.google.com/docs/firestore/client/libraries#server_client_libraries)
