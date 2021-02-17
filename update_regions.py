from lxutils import config
from lxutils.log import log, timer
import pandas as pd
import aiohttp, asyncio, sys

reg = None
missing = None
new_number = None

def main():
    prepare()
    fetch()
    save()

    log('Complete!')


def prepare():
    global reg, missing, new_number

    with timer('Stage 1 - preparation'):
        log('Reading the stock files')
        stock = pd.read_csv(config['dirs']['data'] + '/trucks - evaluated.csv')['Location']
        stock =  stock.append(pd.read_csv(config['dirs']['data'] + '/trailers - evaluated.csv')['Location'])
        stock = pd.DataFrame(stock)
        loc = stock.rename(columns={'Location': 'location'}).groupby('location')['location'].count()
        loc = loc.sort_values(ascending=False)
        loc = pd.DataFrame(loc)
        loc = loc.rename(columns={'location': 'number'})
        loc = loc.reset_index()
        log(f'{loc.shape[0]} locations found')

        log('Reading the regions file')
        reg = pd.read_excel(config['dirs']['data'] + '/regions.xlsx')
        reg = reg.drop ('number', axis = 1) # будем записывать актуальное

        missing = pd.merge(loc, reg, how="outer", on="location", indicator=True)
        new_number = missing.pop('number')
        missing = missing[missing['_merge'] == 'left_only']
        missing = missing.drop(['_merge'], axis = 1)

        log(f'{missing.shape[0]} new entries found')


def fetch():

    global missing

    with timer('Stage 2 - Fetching geo data from dadata for new entries'):

        if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        results = asyncio.run(fetch_list(missing['location']))

        missing['region'] = [x['data']['region_with_type'] if x else None for x in results]
        log(f'Regions obtained for {missing["region"].dropna().shape[0]} entries')


async def fetch_list(l):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in l:
            tasks.append(asyncio.create_task (fetch_slice(i, session)))
            await asyncio.sleep(0.06)
        results = await asyncio.gather(*tasks)
    return results


async def fetch_slice (sl, session):
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"

    headers = {
    'Authorization': 'Token 20fcc6df8b11d541f012005ff34e75c96a79e96d',
    'Content-Type': 'application/json'
    }

    payload = '{"query": "' + sl + '"}'
    payload = payload.encode('utf-8')

    cities = []

    async with session.request("POST", url, headers=headers, data=payload) as response:
        if response.status == 200:
            log ('Received location data for "{}"'.format (sl))
            json = await response.json(content_type=None)

            cities = list(filter(
                lambda x: (x['data']['city'] == sl) and
                    (x['data']['street_type_full'] == None) and
                    (x['data']['settlement_type_full'] != 'территория'),
                json['suggestions']))

            if len(cities) == 1:
                return cities[0]

            if len(cities) > 1: #пытаемся посмотреть - а вдруг там только одно вхождение с качеством 4?
                cities_qc_4 = list(filter(lambda x: x['data']['qc_geo'] == '4', cities))
                if len(cities_qc_4) == 1:
                    log(f'{len(cities)} entries found for "{sl}", but only one qc4')
                    return cities_qc_4[0]

    log(f'{len(cities)} entries found for "{sl}", returning None')
    return None


def save():
    global reg, missing, new_number

    with timer('Stage 3 - Writing down the regions file'):
        reg = reg.append(missing)
        reg['number'] = new_number
        reg = reg.sort_values('number', ascending=False)
        total_sum = reg['number'].sum()
        covered_sum = total_sum - reg[pd.isna(reg['fo'])]['number'].sum()
        log(f'{int(covered_sum / total_sum * 100)}% ({covered_sum} of {total_sum}) of stocks covered by the federal district indication')
        reg.to_excel(config['dirs']['data'] + '/regions.xlsx', index=False)


if __name__ == "__main__":
    main()