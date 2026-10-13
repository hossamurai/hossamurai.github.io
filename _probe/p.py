import re, urllib.request
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
     'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8', 'Accept-Language': 'ar,en;q=0.8'}
def get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=25); return r.status, r.read().decode('utf-8','ignore')
    except urllib.error.HTTPError as e: return e.code, ''
for u in ['https://elcinema.com/ramadan/2026/', 'https://elcinema.com/ramadan/2027/', 'https://elcinema.com/en/ramadan/2026/']:
    st, b = get(u)
    works = re.findall(r'/work/(\d+)/', b)
    print('==', u, st, len(b), 'works', len(set(works)))
    i = b.find('/work/'); 
    # print a cleaned excerpt around the first 3 work cards in the main list
    m = [x.start() for x in re.finditer(r'/work/\d+/"', b)]
    for k in m[3:6]: print('   ...', re.sub(r'\s+', ' ', b[k-700:k+500]))
    pages = re.findall(r'href="([^"]*page=\d+[^"]*)"', b)[:5]; print('   pages', pages)
st, b = get('https://elcinema.com/work/2096531/')
print('== work', st, re.findall(r'<meta property="og:(?:title|image)" content="([^"]+)"', b), re.findall(r'<title>([^<]+)', b))
i=b.find('تاريخ'); print(re.sub(r'\s+',' ', b[i-200:i+600]) if i>0 else 'no date')
