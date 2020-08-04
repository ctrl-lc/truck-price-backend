def evaluate_trucks (df): 
    import subprocess, pandas as pd

    df.to_csv ("..\\temp\\in_trucks.csv") 

    subprocess.run("bigmler --ensemble ensemble/5e7e6b3bfb7bdd1123005026 \
                --test ..\\temp\\in_trucks.csv \
                --output ..\\temp\\out_trucks.csv \
                --remote \
                --username leshchenko \
                --api_key 724c06d2530db8744a01ea24cdce30911cdba42d \
                --locale \"en_US.UTF-8\" \
                --prediction-header \
                --prediction-info full")

    return pd.read_csv("..\\temp\\out_trucks.csv")

def evaluate_trailers (df):
    import subprocess
    import pandas

    df.to_csv ("..\\temp\\in_trailers.csv")

    subprocess.run("bigmler --ensemble ensemble/5e7de328fb7bdd111a000aff \
                --test ..\\temp\\in_trailers.csv \
                --output ..\\temp\\out_trailers.csv \
                --remote \
                --username leshchenko \
                --api_key 724c06d2530db8744a01ea24cdce30911cdba42d \
                --locale \"en_US.UTF-8\" \
                --prediction-header \
                --prediction-info full")

    return pandas.read_csv("..\\temp\\out_trailers.csv")


def upload_to_google_sheets (df):
    import gspread, pprint, sys, datetime

    from oauth2client.service_account import ServiceAccountCredentials

    projectdir = 'C:\\Users\\a.leshchenko\\Documents\\Stocks'

    f = open(projectdir + '\\data\\full_stock1.csv', 'r')
    content = f.read()

    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(projectdir + '\\scripts\\robotic-rampart-255014-e2f22bfae60e.json', scope)

    gc = gspread.authorize(credentials)

    gc.import_csv("1Hcc4ay2SZu1gImUljdbTVgw3GEaJrz-7IerNWcZDRzU", content)
    
    return
