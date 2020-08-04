# Специальная версия загрузчика для пакетной загрузки результатов ручной верификации
# Использовалась для первоначальной загрузки результатов, которые были также использованы для обучения модели
# верификации

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import datetime, urllib

# Закачать файл с результатами автоматической верификации
projectdir = u'C:\\Users\\a.leshchenko\\OneDrive\\Документы\\Контрол\\Stocks'
r = pd.read_csv(projectdir + u'\\temp\\comments - training 2.csv', sep=';')

# Use the application default credentials
firebase_admin.initialize_app()
db = firestore.client()

# Добавляем в базу результаты автоматической верификации
for val in enumerate(r.iterrows()): 
    v = val[1][1]
    ad_data = {
        'comment': v['Comment'],
        'vehicleType': v['VehicleType'],
        'make': v['Make'],
        'year': v['Year'],
        'supplierPrice': v['Price'],
        'mileage': v['Mileage'],
        'supplier': v['Supplier'],
        'valuation': v['Price 1'],
        'benefit': v['Benefit'],
        'checked': True
    }

    verification_data = {
        u'date': datetime.datetime.now(),
        u'user': u'leshchenko',
        u'result': val[1][1]["Result"],
        u'confidence': 1
    }

    doc_name = urllib.parse.quote(v['URL'], safe='')
    doc_ref = db.collection(u'ads').document(doc_name)
    doc_ref.set (ad_data, merge = True)
    doc_ref.collection(u'verifications').add(verification_data)

# на будущее - более быстрая запись будет при помощи Firebase Admin SDK
# (https://firebase.google.com/docs/firestore/client/libraries#server_client_libraries)
