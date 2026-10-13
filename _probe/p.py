import json, urllib.parse, urllib.request
def get(u, raw=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (hossamservices.com probe)'}), timeout=25)
    b = r.read()
    return b.decode('utf-8', 'ignore') if raw else json.loads(b)
W = 'https://ar.wikipedia.org/w/api.php?'
def api(**k):
    k['format'] = 'json'
    return get(W + urllib.parse.urlencode(k))
for q in ['مسلسلات رمضان 2026', 'قائمة مسلسلات رمضان 2025', 'دراما رمضان 2026', 'مسلسلات رمضان 2027']:
    try:
        r = api(action='query', list='search', srsearch=q, srlimit=8)
        print('SEARCH', q, [x['title'] for x in r['query']['search']])
    except Exception as e: print('ERR', q, e)
for pre in ['مسلسلات رمضان', 'مسلسلات تلفزيونية مصرية عرضت في', 'مسلسلات عرضت في رمضان', 'مسلسلات مصرية']:
    try:
        r = api(action='query', list='allcategories', acprefix=pre, aclimit=30, acprop='size')
        print('CAT', pre, [(x['*'], x.get('size')) for x in r['query']['allcategories']])
    except Exception as e: print('ERR', pre, e)
for u in ['https://elcinema.com/ar/', 'https://www.elcinema.com/ar/series/', 'https://www.filfan.com/', 'https://www.themoviedb.org/']:
    try:
        h = get(u, raw=True); print('OK', u, len(h))
    except Exception as e: print('FAIL', u, e)
