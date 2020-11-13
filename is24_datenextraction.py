import numpy as np
import pandas as pd
import requests
import sys; sys.path.append('/home/tscho/Desktop/pattern-master')
import pattern
import pattern.web as web
import re

ids = set([])
#Durch die Suchergebnisseiten loopen (Suche: Mietwohnungen in Berlin) und die IDs der Exposes speichern
for page in range(1,184):

    print("collecting page " + str(page))

    url = 'http://www.immobilienscout24.de/Suche/S-4/P-'+str(page)+'/Wohnung-Miete/Berlin/Berlin?pagerReporting=True'
    html = requests.get(url).text
    dom = web.Element(html)
    l = dom('li.result-list__listing')
    for i in l:
        ids.add(i.attrs['data-id'])

ids = list(ids)
ids.sort()
print(ids)

kaltmiete = []
zimmer = []
flaeche = []
lat = []
lon = []
error_ids = []

# aus den Exposes die Kaltmiete, Zimmerzahl, Flaeche und Koordinaten extrahieren
for i in ids:

    print("Scraping ID " + str(i))
    url = 'http://www.immobilienscout24.de/expose/' + str(i)
    html = requests.get(url).text
    dom = web.Element(html)
    try:
        kaltmiete.append(float(dom('div[class="is24qa-kaltmiete"]')[0].content.replace('.','').split()[0].replace(',','.')))
        zimmer.append(float(dom('div[class="is24qa-zi"]')[0].content.replace(',','.')))
        flaeche.append(float(dom('div[class="is24qa-flaeche"]')[0].content.split()[0].replace(',','.')))

        lat.append(re.search("lat: (\d)*\.(\d)*", html).group(0).split()[1])
        lon.append(re.search("lng: (\d)*\.(\d)*", html).group(0).split()[1])
    except:
        print( "ERROR at id " + str(i) + ". retrieved " + str(len(kaltmiete)) + ": ")
        print( "Unexpected error: " + str(sys.exc_info()))
        error_ids.append(i)

print( "done" )

result = {}
result['kaltmiete'] = kaltmiete
result['zimmer'] = zimmer
result['flaeche'] = flaeche
result['lat'] = lat
result['lon'] = lon
result = pd.DataFrame(result)
result['quadratmeter preis'] = result.kaltmiete/result.flaeche

#ungueltige werte filtern
result = result[((result.lat > 0) & (result.lon > 0))& (result.kaltmiete > 100)]
result.to_csv('mietwohnungen4.csv', sep='\t')
