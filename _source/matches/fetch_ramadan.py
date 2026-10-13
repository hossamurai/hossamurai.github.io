"""Ramadan series for the website's Ramadan page — fully automatic (runs in GitHub Actions every 6 hours).

Sources (each one fills what the one before it missed; if all fail, the last good file is kept):
  1. Arabic Wikipedia category "مسلسلات رمضان <Hijri year> هـ" — editors add every series of that Ramadan.
  2. Arabic Wikipedia search for "رمضان <year>" in series articles — catches series announced before they are categorised.
  3. The last good assets/data/ramadan.json.
For each series: Arabic + English name, start date (from the article's infobox, else the first day of Ramadan),
lead actors and the poster (Arabic article, else the English one; only real poster uploads, never random photos —
the page shows a designed title card when there is none).

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


def season_series(hijri, year, start, end):
    """Every series of one Ramadan from Wikipedia; None if Wikipedia didn't answer at all."""
    titles, ok = [], False
    try:   # 1. the category
        cont = {}
        while True:
            r = api('ar', action='query', list='categorymembers', cmtitle=f'تصنيف:مسلسلات رمضان {hijri} هـ', cmtype='page', cmlimit=500, **cont)
            ok = True
            titles += [p['title'] for p in r['query']['categorymembers']]
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
            r = api('ar', action='query', titles='|'.join(batch), prop='pageimages|revisions|langlinks|categories',
                    piprop='thumbnail', pithumbsize=500, pilicense='any', rvprop='content', rvslots='main',
                    lllang='en', lllimit=500, cllimit=500, redirects=1)
        except Exception as e:
            print('  pages failed', e, file=sys.stderr)
            continue
        en_titles = {}
        for p in r['query'].get('pages', []):
            if p.get('missing'):
                continue
            text = ((p.get('revisions') or [{}])[0].get('slots', {}).get('main', {}) or {}).get('content', '')
            cats = ' '.join(c['title'] for c in p.get('categories', []))
            in_cat = f'مسلسلات رمضان {hijri}' in cats
            # a search hit must really be a series of this Ramadan
            if not in_cat and not re.search(rf'رمضان\s*{year}|رمضان\s*{hijri}', text):
                continue
            if not re.search(r'مسلسل|series', cats + text[:3000], re.I):
                continue
            en = (p.get('langlinks') or [{}])[0].get('title', '')
            item = {'ar': clean_title(p['title']), 'en': clean_title(en), 'date': infobox_date(text, start, end),
                    'stars': stars_of(text), 'poster': poster_of(p), 'wiki': p['title']}
            if not item['poster'] and en:
                en_titles[en] = item
            out.append(item)
        if en_titles:   # poster from the English article when the Arabic one has none
            try:
                r = api('en', action='query', titles='|'.join(en_titles), prop='pageimages', piprop='thumbnail', pithumbsize=500, pilicense='any', redirects=1)
                norm = {n['to']: n['from'] for n in r['query'].get('redirects', []) + r['query'].get('normalized', [])}
                for p in r['query'].get('pages', []):
                    it = en_titles.get(p['title']) or en_titles.get(norm.get(p['title'], ''))
                    if it:
                        it['poster'] = poster_of(p)
            except Exception as e:
                print('  en posters failed', e, file=sys.stderr)
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
    now = season_series(hijri, year, a, b)
    seasons = {'season': {'year': year, 'hijri': hijri, 'series': now if now is not None else (old.get('season') or {}).get('series', [])}}
    # last Ramadan too — shown as "watch again" until this year's list fills up
    pa, pb, py, ph = None, None, year - 1, hijri - 1
    prev = [x for x in RAMADAN if int(x[0][:4]) == py]
    if prev:
        pa, pb = date.fromisoformat(prev[0][0]), date.fromisoformat(prev[0][1])
    else:
        pa, pb = a - timedelta(days=355), b - timedelta(days=355)
    last = season_series(ph, py, pa, pb)
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
