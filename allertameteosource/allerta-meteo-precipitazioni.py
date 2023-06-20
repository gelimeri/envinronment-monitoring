# import http.client
import requests
import pandas
import json
import numpy as np
from datetime import datetime
from datetime import timedelta
import calendar

url = 'https://allertameteo.regione.emilia-romagna.it/' \
      'o/api/allerta/get-time-series/'
'https://allertameteo.regione.emilia-romagna.it/o/api/allerta/get-time-series/?stazione=-/1171292,4434535/simnbo&variabile=1,0,900/1,-,-,-/B13011'

params = '?stazione={stazione}&variabile={variabile}'
stazione = '-/1171292,4434535/simnbo'
variabile = '1,0,900/1,-,-,-/B13011'

time = calendar.timegm(datetime.now().timetuple()) * 1000

complete_url = url + params.format(variabile=variabile, time=time)

with requests.Session() as session:
    r = session.get(complete_url, headers={'Accept': 'application/json'})
    print(r.status_code)
    content = r.content
jsonobjs = r.json()

for item in jsonobjs['_items']:
    # item['levelsamples'] = []
    # item['levelsamples'].appen#d({'datetime': datetime.now(), 'value': ''})
    for (day, times) in item['dati'].items():
        for (time, values) in times.items():
            if values['livello_idro']:
                dt = datetime.strptime(day + time, '%Y%m%d%H%M')
                val = values['livello_idro']
                if 'levelsamples' not in item:
                    item['levelsamples'] = []
                item['levelsamples'].append({'datetime': dt, 'value': val})
    item['crescita'] = False
    item['sogliamassima_superata'] = False
    item['sogliamassima_delta'] = None
    item['last_sample'] = item['levelsamples'][-1]['value']
    item['soglia_3'] = None
    item['soglia_2'] = None
    item['soglia_1'] = None
    if len(item['levelsamples']) >= 4:
        x1 = (item['levelsamples'][-3]['value'] + item['levelsamples'][-4]['value']) / 2
        x2 = (item['levelsamples'][-2]['value'] + item['levelsamples'][-1]['value']) / 2
        item['crescita'] = x2 - x1 > 0.5
        try:
            ths = item['anagrafica']['sensori']['livello_idro']['soglie']
            ths.sort()
            thmax = ths[2]
            item['soglia_3'] = ths[2]
            item['soglia_2'] = ths[1]
            item['soglia_1'] = ths[0]
        except Exception:
            thmax = None
        if thmax:
            item['sogliamassima_superata'] = item['levelsamples'][-1]['value'] >= thmax
            item['sogliamassima_delta'] = item['levelsamples'][-1]['value'] - thmax

downloaded_data = pandas.DataFrame.from_dict(jsonobjs['_items'])
print(downloaded_data['sogliamassima_superata'])
filtered = downloaded_data[downloaded_data['sogliamassima_superata'] | downloaded_data['crescita']]
filtered.plot()
print(filtered)

# prova = pandas.json_normalize(jsonobjs['_items'], record_path=['livello_idro'],
#                              meta=['_id', ['anagrafica', 'nome'],
#                                    ['anagrafica', 'sensori', 'livello_idro', 'soglie', '0'],
#                                    ['anagrafica', 'sensori', 'livello_idro', 'soglie', '1'],
#                                    ['anagrafica', 'sensori', 'livello_idro', 'soglie', '2'],
#                                    ['anagrafica', 'sensori', 'comune'],
#                                    ['anagrafica', 'sensori', 'provincia'],
#                                    ['anagrafica', 'sensori', 'livello_idro', 'soglie', 'bacino']],
#                              errors='ignore')
# downloaded_data['levels_df'] = pandas.DataFrame.from_dict(downloaded_data['levelsamples'])
# print(downloaded_data)

# downloaded_data['last_sample'] = downloaded_data['levels_df'].iloc[-1]
# prova = pandas.json_normalize(jsonobjs['_items'], record_path=['levelsamples'], meta=['_id', 'anagrafica'])
# print(prova)
# df = pandas.json_normalize(downloaded_data.dati)  # , record_prefix="Prefix.")
# downloaded_data = downloaded_data + df
# dg = pandas.DataFrame.from_dict(dati.dati, orient='index') # json_normalize(dati.dati) #, record_prefix="Prefix.")
# downloaded_data['livello'] = pandas.json_normalize(downloaded_data['dati'])
# downloaded_data.assign(levels=lambda x: pandas.DataFrame(pandas.json_normalize(x["dati"]))).head()
