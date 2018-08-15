#!/usr/bin/env python3
import requests
import json
import sqlite3
from datetime import timedelta, date

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_currency_data (URL, SOURCE, API_KEY, TYPE, CURRENCY, *args):
    API_KEY = '?access_key=' + API_KEY
    SOURCE = '&source=' + SOURCE
    if CURRENCY !=  []:
        CURRENCY = '&currencies= ' + ','.join(CURRENCY)
    else:
        CURRENCY = ''
    TYPE = TYPE

    DATE = ''
    if TYPE == 'historical':
        DATE = '&date=' + args[0]
    full_url = URL + TYPE + API_KEY + DATE + SOURCE + CURRENCY + '& format = 1'


    #print(full_url)
    data = requests.get(full_url).text
    return data

def insert_historical_data (SOURCE, CURRENCY, DATE, RATE):
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    try:
        cursor.execute(''' INSERT INTO source_target_table (source, target) values (?,?)''', (SOURCE, CURRENCY))
        connection.commit()
    except:
        pass

    st_id = cursor.execute(''' SELECT st_id from source_target_table where source = ? and target = ? ''', (SOURCE, CURRENCY)).fetchone()[0]
    #print(st_id)

    cursor.execute(''' INSERT INTO price_table(st_id, timestamp, price) values (?, ?, ?) ''', (st_id, DATE, RATE))
    connection.commit()

if __name__ == '__main__':
    USER_ID = 1
    URL = 'http://apilayer.net/api/'
    SOURCE = 'USD'
    CURRENCY = []
    API_KEY = '45d4584351c4a10188d67c228f22b2a9'
    TYPE = 'historical'
    

    start_date = date(2018, 7, 3)
    end_date = date(2018, 7, 4)
    for single_date in daterange(start_date, end_date):
        DATE = single_date.strftime("%Y-%m-%d")
        print(DATE)
        data = get_currency_data (URL, SOURCE, API_KEY, TYPE, CURRENCY, DATE)
        data = json.loads(data)
        for key, value in data['quotes'].items():
            insert_historical_data(key[:3], key[3:], DATE, value)
        #print(key[:3], key[3:], DATE, value)
    #print(data['quotes'])
    #print(json.dumps(json.loads(data), indent=4, sort_keys=True))

