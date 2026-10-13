import json, subprocess, urllib.request
subprocess.run(['python3', 'fetch_ramadan.py'], cwd='_source/matches', check=True)
d = json.load(open('assets/data/ramadan.json'))
for k in ('season', 'last'):
    s = d[k]; L = s['series']
    print(k, s['year'], len(L), 'posters', sum(1 for x in L if x['poster']), 'dates', sum(1 for x in L if x['date']), 'en', sum(1 for x in L if x['en']), 'ec', sum(1 for x in L if x.get('ec')))
    for x in L[:40]: print('  ', x['date'] or '-', '|', x['ar'], '|', x['en'], '|', x['stars'], '|', x['poster'][-40:])
img = next(x['poster'] for x in d['season']['series'] if 'elcinema' in x['poster'])
r = urllib.request.urlopen(urllib.request.Request(img, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20)
print('image no-referer', r.status, r.headers.get('content-type'), len(r.read()))
