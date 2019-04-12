import datetime
import json
from pytz import timezone
import requests
import time

API_URL_BASE = "https://min-api.cryptocompare.com/"
HISTORY_HOUR_PATH = API_URL_BASE + "data/histohour"

#"01.01.2018 16:12:31"

def getAverageCoinPrice(api_key, crypto_currency, fiat_currency, time, location = 'Europe/Berlin', timeout = 5):
    ts = None
    if isinstance(time, str):
        tz = timezone(location)
        dt = tz.localize((datetime.datetime.strptime("01.05.2018  12:31:59", "%d.%m.%Y %H:%M:%S")))
        ts = dt.timestamp()
    elif isinstance(time, str):
        ts = time

    req_param = "fsym=" + str(crypto_currency) + "&tsym=" + str(fiat_currency) + "&limit=1&toTs=" + str(ts)
    try:
        response = requests.get(HISTORY_HOUR_PATH, params=req_param, timeout=timeout)
    except requests.exceptions.Timeout:
        print("Request " + API_URL_BASE + " TIMEOUT!")
        return None

    if response.status_code != 200:
        return None

    js = json.loads(response.content.decode('utf-8'))

    open_price = js['Data'][1]['open']
    close_price = js['Data'][1]['close']

    diff = close_price - open_price
    add = (diff / 3600) * (ts % 3600)

    print(open_price + add)
    

    
    