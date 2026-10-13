import re, urllib.request, urllib.parse
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
     'Accept': 'text/html,*/*;q=0.8', 'Accept-Language': 'ar,en;q=0.8'}
def get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=25); return r.status, r.read().decode('utf-8', 'ignore')
    except urllib.error.HTTPError as e: return e.code, ''
st, b = get('https://www.filgoal.com/matches/?date=2026-10-14')
blocks = re.split(r'<div class="mc-block"', b)
print('FG blocks', len(blocks))
for blk in blocks[1:3]: print('BLK', re.sub(r'\s+', ' ', blk)[:2500]); print()
st, k = get('https://www.kooora.com/?region=-1')
links = sorted(set(urllib.parse.unquote(x) for x in re.findall(r'href="(/[^"]*)"', k) if 'مباريات' in urllib.parse.unquote(x) or 'date' in x))[:30]
print('KO links', links)
for u in ['https://www.kooora.com/كرة-القدم/مباريات-اليوم', 'https://www.kooora.com/كرة-القدم/مباريات?date=2026-10-17', 'https://www.kooora.com/%D9%83%D8%B1%D8%A9-%D8%A7%D9%84%D9%82%D8%AF%D9%85/%D9%85%D8%A8%D8%A7%D8%B1%D9%8A%D8%A7%D8%AA-%D8%A7%D9%84%D9%8A%D9%88%D9%85?date=2026-10-17']:
    st, h = get(urllib.parse.quote(u, safe=':/?=&%'))
    print('KO', st, len(h), u, len(re.findall('fco-match-list-item', h)), sorted(set(re.findall(r'fco-tv-channel__name">([^<]+)', h)))[:10])
