import pandas as pd
import datetime, urllib
from tqdm import tqdm

from lxutils.log import log
from lxutils import config
from utils import db
from firestore_batch import Batch


ads = {}


def main():
    delete_old_verifications()
    load_ads()
    add_automatic_verifications()
    delete_ads_without_verifications()


def delete_old_verifications():
    # удаление всех прошлых автоматических верификаций

    log('Deleting old automatic verifications...')

    docs = db.collection_group('verifications').where('confidence', '<', 1).stream()

    with Batch(db) as batch:
        for doc in tqdm(docs):
            batch.delete(doc.reference)


def load_ads():
    global ads
    log ('Loading ads...')
    for ad in tqdm(db.collection('ads').stream()):
        ads[ad.id] = ad


def add_automatic_verifications():
    global ads

    # Добавляем в базу результаты автоматической верификации
    log('Adding new automatic verification results...')

    log('Preparing data...')

    all_ad_data = {}
    all_verification_data = {}
    comments = pd.read_csv(config['dirs']['data'] + '/comments evaluated.csv')

    for val in tqdm(comments.itertuples(), total = comments.shape[0]):
        if type(val.URL) == float:
            continue

        ad_data = {
            'comment': val.Comment,
            'vehicleType': val.VehicleType,
            'make': val.Make,
            'year': val.Year,
            'supplierPrice': val.Price,
            'mileage': val.Mileage,
            'supplier': val.Supplier,
            'valuation': val._9, # в оригинале "Price 1", но пробелы превратили это в "_9"
            'benefit': val.Benefit
        }

        verification_data = {
            'date': datetime.datetime.now(),
            'user': 'auto',
            'result': val.Result,
            'confidence': val.confidence
        }

        doc_name = urllib.parse.quote(val.URL, safe="")

        if doc_name not in ads or "checked" not in ads[doc_name].to_dict():
            ad_data['checked'] = False

        doc_ref = db.collection('ads').document(doc_name)

        all_ad_data[doc_ref] = ad_data
        all_verification_data[doc_ref] = verification_data

    log('Uploading data...')
    with Batch(db) as batch:
        for ad_doc_ref, ad_data in all_ad_data.items():
            batch.set(ad_doc_ref, ad_data, merge = True)

        for ad_doc_ref, verification_data in all_verification_data.items():
            ver_doc_ref = ad_doc_ref.collection('verifications')\
                                    .document(str(verification_data['date']))
            batch.set(ver_doc_ref, verification_data)


def delete_ads_without_verifications():
    # удаление всех объявлений, у которых нет верификаций - было нужно после сбоев в загрузке

    global ads

    log ('Deleting ads without verifications...')
    ads_to_delete = set()

    with tqdm(total=len(ads)) as pbar:
        for __, ad_doc in ads.items():
            verifications = ad_doc.reference.collection('verifications').stream()
            try:
                _ = next(verifications)
            except:
                ads_to_delete.add(ad_doc.reference)
                pbar.set_postfix({'found': len(ads_to_delete)})
            pbar.update()

    with Batch(db) as batch:
        for doc_ref in ads_to_delete:
            batch.delete(doc_ref)

    log (f'{len(ads_to_delete)} deleted.')

# на будущее - более быстрая запись будет при помощи Firebase Admin SDK
# (https://firebase.google.com/docs/firestore/client/libraries#server_client_libraries)


if __name__ == "__main__":
    main()