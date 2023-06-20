# import http.client
import requests
import pandas
import json
import numpy as np
from datetime import datetime, timezone
from datetime import timedelta
import calendar


def get_data(utctimestamp=None):
    url = 'https://allertameteo.regione.emilia-romagna.it' \
          '/o/api/allerta/get-sensor-values-no-time/'
    params = '?variabile={variabile}&time={time}'
    variabile = '1,0,3600/1,-,-,-/B13011'
    # n = datetime.utcnow()

    if isinstance(utctimestamp, str):
        try:
            timestamp = datetime.strptime(utctimestamp)
        except Exception:
            print("Parameter error")

    if utctimestamp is not None and not isinstance(utctimestamp, datetime.datetime):
        raise Exception("Parameter error")

    if utctimestamp is None:
        utctimestamp = datetime.now(timezone.utc)

        delta = utctimestamp.time().minute % 15
        tm = utctimestamp - timedelta(minutes=(delta + 30), seconds=utctimestamp.second,
                                      microseconds=utctimestamp.microsecond)
        timereq = calendar.timegm(tm.timetuple()) * 1000
    else:
        tm = utctimestamp
        timereq = calendar.timegm(utctimestamp.timetuple()) * 1000

    # print(timereq)
    complete_url = url + params.format(variabile=variabile, time=timereq)

    with requests.Session() as session:
        r = session.get(complete_url, headers={'Accept': 'application/json'})
        # print(r.status_code)
        content = r.content
    jsonobjs = r.json()

    downloaded_data = pandas.DataFrame.from_dict(jsonobjs[1:])
    downloaded_data['timestamp_utc'] = tm
    return downloaded_data


df = get_data()
# downloaded_data = pandas.json_normalize(jsonobjs)
# downloaded_data['value'].isna().count()
print(df['value'].isna().sum())

with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
    print(df)
