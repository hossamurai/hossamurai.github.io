import re, urllib.request
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
     'Accept': 'text/html,*/*;q=0.8', 'Accept-Language': 'ar,en;q=0.8'}
def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=25); return r.read().decode('utf-8', 'ignore')
b = get('https://www.filgoal.com/matches/?date=2026-10-14')
for m in list(re.finditer(r'beIN SPORTS[^<]{0,20}', b))[:3]:
    print('FG ---', b[m.start()-2500:m.end()+300].replace('\n', ' ')[:2900]); print()
b = get('https://www.filgoal.com/matches/?date=2026-10-17')
print('FG 17 channels', sorted(set(re.findall(r'beIN SPORTS[^<]{0,20}|ON Time[^<]{0,20}|SSC[^<]{0,15}|ثمانية[^<]{0,10}', b))))
k = get('https://www.kooora.com/?region=-1')
for m in list(re.finditer(r'beIN Sports Mena \d', k))[:2]:
    print('KO ---', k[m.start()-2500:m.end()+300].replace('\n', ' ')[:2900]); print()
