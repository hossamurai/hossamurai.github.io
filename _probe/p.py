import re, urllib.parse, urllib.request
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
     'Accept': 'text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8', 'Accept-Language': 'ar,en;q=0.8'}
def get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=25)
        b = r.read().decode('utf-8', 'ignore'); return r.status, r.geturl(), b
    except urllib.error.HTTPError as e: return e.code, u, e.read().decode('utf-8','ignore')[:300]
    except Exception as e: return 'ERR', u, str(e)
q = urllib.parse.quote
for u in ['https://elcinema.com/', 'https://elcinema.com/en/', 'https://www.elcinema.com/', f'https://elcinema.com/search/?s={q("الحشاشين")}',
          f'https://elcinema.com/en/search/?s={q("الحشاشين")}', 'https://elcinema.com/ramadan/', 'https://elcinema.com/en/ramadan/',
          f'https://www.filfan.com/search?q={q("الحشاشين")}', f'https://www.themoviedb.org/search?query={q("الحشاشين")}',
          f'https://v3.sg.media-imdb.com/suggestion/x/{q("The Assassins 2024")}.json']:
    st, fu, b = get(u)
    imgs = re.findall(r'(https?://[^"\' )]+?\.(?:jpg|jpeg|png|webp))', b)
    links = sorted(set(re.findall(r'href="(/(?:en/)?(?:work|ramadan)[^"]*)"', b)))[:15]
    print('==', st, u, '->', fu, len(b)); print('   imgs', imgs[:6]); print('   links', links)
    if 'ramadan' in u and st == 200: print(b[:1500].replace('\n',' '))
