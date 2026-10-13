"""Ramadan series for the website's Ramadan page — fully automatic (runs in GitHub Actions every 6 hours).

Sources (each one fills what the one before it missed; if all fail, the last good file is kept):
  1. elCinema (elcinema.com/ramadan/<year>/) — every series of that Ramadan with its poster, English name and cast;
     the start date comes from each series' page ("تاريخ العرض"), fetched once and remembered.
  2. Arabic Wikipedia: the category "مسلسلات رمضان <Hijri year> هـ" + a search for announced series — adds what
     elCinema misses, and its posters / dates / English names (Wikidata) fill gaps.
  3. The last good assets/data/ramadan.json.
Posters: elCinema, else Wikipedia (real poster uploads only); the page shows a designed title card when there is none
or when an image fails to load. No date = the first day of Ramadan.

Output: assets/data/ramadan.json  →  _source/pages.py (build) and assets/ramadan.js (live, no-store).
"""
import json, os, re, sys, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'ramadan.json')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pages import RAMADAN, ramadan_season   # noqa: E402  (expected Ramadan dates + Hijri years live in one place)

MONTHS = {'يناير': 1, 'فبراير': 2, 'مارس': 3, 'أبريل': 4, 'ابريل': 4, 'مايو': 5, 'يونيو': 6, 'يوليو': 7, 'أغسطس': 8, 'اغسطس': 8,
          'سبتمبر': 9, 'أكتوبر': 10, 'اكتوبر': 10, 'نوفمبر': 11, 'ديسمبر': 12,
          'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8,
          'september': 9, 'october': 10, 'november': 11, 'december': 12}
AR_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')


def api(host, **k):
    k.update(format='json', formatversion=2)
    req = urllib.request.Request(f'https://{host}.wikipedia.org/w/api.php?' + urllib.parse.urlencode(k),
                                 headers={'User-Agent': 'hossamservices.com Ramadan page (https://hossamservices.com)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def clean_title(t):
    t = re.sub(r'\s*\((مسلسل[^)]*|[^)]*series[^)]*)\)\s*$', '', t or '', flags=re.I)
    return re.sub(r'^مسلسل\s+', '', t).strip()


def poster_of(page):
    src = (page.get('thumbnail') or {}).get('source', '')
    # posters are local (non-free) uploads: …/wikipedia/ar/… or …/wikipedia/en/…; Commons pictures are not posters
    if src and '/wikipedia/commons/' not in src and not src.lower().endswith('.svg.png'):
        return src.split('?')[0]
    return ''


def infobox_date(text, start, end):
    """First date in the article's broadcast fields that falls in this Ramadan (± a few days)."""
    for m in re.finditer(r'\|\s*(?:[^|=\n]*(?:بث|عرض|first_aired|released|air_date)[^|=\n]*)=([^\n]*)', text or '', re.I):
        v = re.sub(r'[\[\]،,]', ' ', m.group(1).translate(AR_DIGITS))
        cands = []
        for d, mo, y in re.findall(r'(\d{1,2})\s+([^\s\d|]+)\s+(\d{4})', v):
            if mo.lower() in MONTHS:
                cands.append((int(y), MONTHS[mo.lower()], int(d)))
        for y, mo, d in re.findall(r'(\d{4})[-|/](\d{1,2})[-|/](\d{1,2})', v):
            cands.append((int(y), int(mo), int(d)))
        for y, mo, d in cands:
            try:
                x = date(y, mo, d)
            except ValueError:
                continue
            if start - timedelta(days=3) <= x <= end:
                return x.isoformat()
    return ''


def stars_of(text):
    m = re.search(r'\|\s*(?:بطولة|starring)\s*=([^\n]*(?:\n\s*[*{\[][^\n]*)*)', text or '', re.I)
    if not m:
        return ''
    names = [n.split('|')[-1].strip() for n in re.findall(r'\[\[([^\]]+)\]\]', m.group(1))]
    names = [n for n in names if n and ':' not in n and not re.search(r'\d', n)][:2]
    return '، '.join(names)


def wiki_series(hijri, year, start, end):
    """Every series of one Ramadan from Wikipedia; None if Wikipedia didn't answer at all."""
    titles, cat_titles, ok = [], set(), False
    try:   # 1. the category
        cont = {}
        while True:
            r = api('ar', action='query', list='categorymembers', cmtitle=f'تصنيف:مسلسلات رمضان {hijri} هـ', cmtype='page', cmlimit=500, **cont)
            ok = True
            titles += [p['title'] for p in r['query']['categorymembers']]
            cat_titles.update(titles)
            if 'continue' not in r:
                break
            cont = {'cmcontinue': r['continue']['cmcontinue']}
    except Exception as e:
        print('  category failed', hijri, e, file=sys.stderr)
    try:   # 2. announced series not categorised yet
        for q in (f'"رمضان {year}" مسلسل', f'"موسم رمضان {year}"', f'"دراما رمضان {year}"'):
            r = api('ar', action='query', list='search', srsearch=q, srlimit=50, srnamespace=0)
            ok = True
            titles += [p['title'] for p in r['query']['search'] if re.search(r'\(مسلسل', p['title'])]
    except Exception as e:
        print('  search failed', year, e, file=sys.stderr)
    if not ok:
        return None
    titles = list(dict.fromkeys(titles))
    out = []
    for i in range(0, len(titles), 20):
        batch = titles[i:i + 20]
        try:
            r = api('ar', action='query', titles='|'.join(batch), prop='pageimages|revisions|pageprops',
                    piprop='thumbnail', pithumbsize=500, pilicense='any', rvprop='content', rvslots='main',
                    ppprop='wikibase_item', redirects=1)
        except Exception as e:
            print('  pages failed', e, file=sys.stderr)
            continue
        for p in r['query'].get('pages', []):
            if p.get('missing'):
                continue
            text = ((p.get('revisions') or [{}])[0].get('slots', {}).get('main', {}) or {}).get('content', '')
            # a search hit (not in the category) must really be a series of this Ramadan
            if p['title'] not in cat_titles and not re.search(rf'رمضان\s*{year}|رمضان\s*{hijri}', text):
                continue
            if not re.search(r'مسلسل|series', text[:4000], re.I):
                continue
            out.append({'ar': clean_title(p['title']), 'en': '', 'date': infobox_date(text, start, end),
                        'stars': stars_of(text), 'poster': poster_of(p), 'wiki': p['title'],
                        'qid': (p.get('pageprops') or {}).get('wikibase_item', '')})
    # English name: the English Wikipedia article's title, else the English label on Wikidata
    by_q = {x['qid']: x for x in out if x.get('qid')}
    ids = list(by_q)
    en_titles = {}
    for i in range(0, len(ids), 50):
        try:
            req = urllib.request.Request('https://www.wikidata.org/w/api.php?' + urllib.parse.urlencode(
                {'action': 'wbgetentities', 'ids': '|'.join(ids[i:i + 50]), 'props': 'labels|sitelinks', 'languages': 'en',
                 'sitefilter': 'enwiki', 'format': 'json'}), headers={'User-Agent': 'hossamservices.com Ramadan page (https://hossamservices.com)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                ents = json.load(r).get('entities', {})
        except Exception as e:
            print('  wikidata failed', e, file=sys.stderr)
            continue
        for q, e in ents.items():
            it = by_q.get(q)
            if not it:
                continue
            enwiki = ((e.get('sitelinks') or {}).get('enwiki') or {}).get('title', '')
            label = ((e.get('labels') or {}).get('en') or {}).get('value', '')
            it['en'] = clean_title(enwiki or label)
            if enwiki and not it['poster']:
                en_titles[enwiki] = it
    # poster from the English article when the Arabic one has none
    names = list(en_titles)
    for i in range(0, len(names), 50):
        try:
            r = api('en', action='query', titles='|'.join(names[i:i + 50]), prop='pageimages', piprop='thumbnail', pithumbsize=500, pilicense='any', redirects=1)
            back = {n['to']: n['from'] for n in r['query'].get('redirects', []) + r['query'].get('normalized', [])}
            for p in r['query'].get('pages', []):
                it = en_titles.get(p['title']) or en_titles.get(back.get(p['title'], ''))
                if it:
                    it['poster'] = poster_of(p)
        except Exception as e:
            print('  en posters failed', e, file=sys.stderr)
    for x in out:
        x.pop('qid', None)
        if x['en'] and re.search(r'[\u0600-\u06ff]', x['en']):
            x['en'] = ''
    return out


# ---------------------------------------------------------------- elCinema
EC = 'https://elcinema.com'
EC_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
              'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8', 'Accept-Language': 'ar,en;q=0.8'}


def ec_get(path):
    req = urllib.request.Request(EC + path, headers=EC_HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')


def ec_unescape(x):
    import html
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', x or ''))).strip()


def ec_cards(path):
    """{id: {name, poster, cast}} from every page of an elCinema Ramadan list (stops when a page adds nothing new)."""
    out = {}
    for page in range(1, 15):
        h = ec_get(f'{path}?page={page}')
        new = 0
        for wid, block in re.findall(r'<div class="row" id="w(\d+)">(.*?)(?=<div class="row" id="w\d+">|<hr />\s*</div>|$)', h, re.S):
            if wid in out:
                continue
            title = re.search(r'<h3><a href="[^"]*/work/\d+/">(.*?)</a></h3>', block, re.S)
            if not title:
                continue
            img = re.search(r'data-src="(https://[^"]+\.(?:jpg|jpeg|png|webp))"', block)
            block = re.sub(r'<ul class="list-separator list-title">.*?</ul>', '', block, flags=re.S)
            cast = [ec_unescape(n) for n in re.findall(r'<a href="[^"]*/person/\d+/">(.*?)</a>', block, re.S)][:2]
            poster = img.group(1) if img and 'blank' not in img.group(1) else ''
            out[wid] = {'name': ec_unescape(title.group(1)), 'poster': poster, 'cast': cast}
            new += 1
        if not new:
            break
    return out


def ec_date(wid, start, end):
    """Start date from the series' page: "تاريخ العرض: 19 فبراير 2026"."""
    try:
        h = ec_get(f'/work/{wid}/')
    except Exception:
        return ''
    m = re.search(r'تاريخ العرض:(.{0,400})', h, re.S)
    return infobox_date('| بث = ' + ec_unescape(m.group(1)) + '\n', start, end) if m else ''


def ec_series(year, start, end, known_dates):
    """Every series of one Ramadan from elCinema; None if elCinema didn't answer."""
    try:
        ar = ec_cards(f'/ramadan/{year}/')
    except Exception as e:
        print('  elcinema failed', year, e, file=sys.stderr)
        return None
    try:
        en = ec_cards(f'/en/ramadan/{year}/')
    except Exception as e:
        print('  elcinema en failed', year, e, file=sys.stderr)
        en = {}
    out, fetched = [], 0
    for wid, x in ar.items():
        d = known_dates.get(wid)
        if d is None and fetched < 120:          # each series' page once; remembered in ramadan.json
            d = ec_date(wid, start, end)
            fetched += 1
        e = en.get(wid) or {}
        out.append({'ar': x['name'], 'en': e.get('name', '') if e.get('name') != x['name'] else '', 'date': d or '',
                    'stars': '، '.join(x['cast']), 'poster': x['poster'] or e.get('poster', ''), 'ec': wid})
    print('  elcinema', year, len(out), 'series,', fetched, 'pages read')
    return out


def match_key(name):
    """Same series across sites: no diacritics/tatweel, one alef/yaa/taa form, no part/season numbers or brackets."""
    x = re.sub(r'[ً-ٰٟـ]', '', str(name or '').lower())
    x = re.sub('[أإآ]', 'ا', x).replace('ى', 'ي').replace('ة', 'ه')
    x = re.sub(r'\(.*?\)|\bج\s*\d+|الجزء\s*\S+|الموسم\s*\S+|[0-9٠-٩]+', ' ', x)
    return re.sub(r'[^a-z؀-ۿ]+', '', x)


def season_series(hijri, year, start, end, old_items):
    """elCinema + Wikipedia merged; None if both failed (the caller keeps the old list)."""
    known = {x['ec']: x.get('date') or '' for x in old_items or [] if x.get('ec')}
    ec = ec_series(year, start, end, known)
    wk = wiki_series(hijri, year, start, end)
    if ec is None and wk is None:
        return None
    out = list(ec or [])
    index = {match_key(x['ar']): x for x in out}
    for w in wk or []:
        x = index.get(match_key(w['ar']))
        if x is None:
            out.append(w)
            index[match_key(w['ar'])] = w
            continue
        for k in ('date', 'poster', 'en', 'stars'):
            if not x.get(k) and w.get(k):
                x[k] = w[k]
    return out


def main():
    old = {}
    try:
        with open(OUT, encoding='utf-8') as f:
            old = json.load(f)
    except Exception:
        pass
    a, b, year = ramadan_season()
    i = next(k for k, x in enumerate(RAMADAN) if x[0] == a.isoformat())
    hijri = RAMADAN[i][2]
    now = season_series(hijri, year, a, b, (old.get('season') or {}).get('series'))
    seasons = {'season': {'year': year, 'hijri': hijri, 'series': now if now is not None else (old.get('season') or {}).get('series', [])}}
    # last Ramadan too — shown as "watch again" until this year's list fills up
    pa, pb, py, ph = None, None, year - 1, hijri - 1
    prev = [x for x in RAMADAN if int(x[0][:4]) == py]
    if prev:
        pa, pb = date.fromisoformat(prev[0][0]), date.fromisoformat(prev[0][1])
    else:
        pa, pb = a - timedelta(days=355), b - timedelta(days=355)
    last = season_series(ph, py, pa, pb, (old.get('last') or {}).get('series'))
    seasons['last'] = {'year': py, 'hijri': ph, 'start': pa.isoformat(),
                       'series': last if last is not None else (old.get('last') or {}).get('series', [])}
    # by start date (none = the first day of Ramadan), series with a poster first, then by name
    for k, first in (('season', a.isoformat()), ('last', pa.isoformat())):
        seasons[k]['series'].sort(key=lambda x: (x.get('date') or first, not x.get('poster'), x['ar']))
    if {k: old.get(k) for k in seasons} == seasons:
        print('no change')
        return
    seasons['updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(seasons, f, ensure_ascii=False, indent=1)
    print('wrote', year, len(seasons['season']['series']), 'series;', py, len(seasons['last']['series']))


if __name__ == '__main__':
    main()
