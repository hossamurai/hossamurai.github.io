import json, re, urllib.parse, urllib.request
def get(u, raw=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (hossamservices.com probe)'}), timeout=25)
    b = r.read()
    return b.decode('utf-8', 'ignore') if raw else json.loads(b)
def api(host='ar', **k):
    k['format'] = 'json'
    return get(f'https://{host}.wikipedia.org/w/api.php?' + urllib.parse.urlencode(k))
for y in range(1441, 1449):
    r = api(action='query', prop='categoryinfo', titles=f'تصنيف:مسلسلات رمضان {y} هـ')
    print(y, [p.get('categoryinfo') for p in r['query']['pages'].values()])
r = api(action='query', generator='categorymembers', gcmtitle='تصنيف:مسلسلات رمضان 1447 هـ', gcmlimit=200, gcmtype='page', prop='pageimages|pageprops', piprop='thumbnail', pithumbsize=400, pilicense='any')
pages = list(r['query']['pages'].values())
print('1447 members', len(pages), 'with image', sum(1 for p in pages if p.get('thumbnail')), 'local', sum(1 for p in pages if '/wikipedia/ar/' in (p.get('thumbnail') or {}).get('source','')))
for p in pages[:12]: print(' ', p['title'], (p.get('thumbnail') or {}).get('source','')[:90], (p.get('pageprops') or {}).get('wikibase_item'))
# text search for 2027 mentions
r = api(action='query', list='search', srsearch='"رمضان 2027" مسلسل', srlimit=20)
print('2027 text', [x['title'] for x in r['query']['search']])
h = get('https://www.filfan.com/', raw=True)
print('filfan ramadan links', sorted(set(re.findall(r'href="([^"]*(?:ramadan|رمضان)[^"]*)"', h)))[:20])
