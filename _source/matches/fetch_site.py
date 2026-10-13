"""Public bits of the bot's knowledge, baked into the pages for search engines (runs in GitHub Actions every 6 hours).

The website also reads them live from n8n (site-data) on every visit, so a change from the admin bot shows at once;
this copy only makes sure Google sees the same series times and match channels in the HTML.

Only `series` (Ramadan series: name, channel, time) and `channels` (match channel per league) are kept —
nothing about customers. If n8n can't be reached, the last good file is kept.

Posters: a series the admin gave a poster link to uses that; the others get the main picture of the series'
Wikipedia article (Arabic first, then English), saved in `posters` by name. Anything without a poster gets a designed
title card on the page, so a card is never empty.

Output: assets/data/bot.json  →  read by _source/pages.py at build time.
"""
import json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

URL = 'https://n8n.hossamservices.com/webhook/site-data'
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'bot.json')


def norm(x):
    """Name for matching: no diacritics/tatweel, one alef/yaa/taa form, no numbers, season words or brackets."""
    x = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', str(x or '').lower())
    x = re.sub('[أإآ]', 'ا', x).replace('ى', 'ي').replace('ة', 'ه')
    x = re.sub(r'\(.*?\)|\b(season|part)\b|الجزء|الموسم|[0-9٠-٩]+', ' ', x)
    return re.sub(r'[^a-z\u0600-\u06ff]+', '', x)


def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'hossamservices.com build (ramadan posters)', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def wiki_poster(ar, en):
    """Lead image of the series' Wikipedia article, only when the article title really is that series."""
    for lang, name, word in (('ar', ar, 'مسلسل'), ('en', en, 'TV series')):
        if not name or len(norm(name)) < 3:
            continue
        try:
            q = urllib.parse.urlencode({'action': 'query', 'generator': 'search', 'gsrsearch': f'{name} {word}', 'gsrlimit': 5,
                                        'prop': 'pageimages', 'piprop': 'thumbnail', 'pithumbsize': 500, 'format': 'json'})
            pages = sorted((get_json(f'https://{lang}.wikipedia.org/w/api.php?{q}').get('query') or {}).get('pages', {}).values(),
                           key=lambda p: p.get('index', 99))
        except Exception as e:
            print('  wikipedia', lang, name, e, file=sys.stderr)
            continue
        for pg in pages:
            src = (pg.get('thumbnail') or {}).get('source', '')
            if src and norm(pg.get('title')).startswith(norm(name)) and not src.lower().endswith('.svg.png'):
                return src
    return ''


def main():
    old = {}
    try:
        with open(OUT, encoding='utf-8') as f:
            old = json.load(f)
    except Exception:
        pass
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (hossamservices.com build)', 'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
    except Exception as e:
        print('site-data failed, keeping the old file:', e, file=sys.stderr)
        return
    out = {
        'series': d['series'] if isinstance(d.get('series'), list) else old.get('series', []),
        'channels': d['channels'] if isinstance(d.get('channels'), dict) else old.get('channels', {}),
    }
    # posters found on Wikipedia, by series name (kept between runs; missing ones are tried again)
    posters = {}
    for x in out['series']:
        if not isinstance(x, dict) or x.get('poster'):
            continue
        key = x.get('ar') or x.get('en')
        posters[key] = (old.get('posters') or {}).get(key) or wiki_poster(x.get('ar'), x.get('en'))
    out['posters'] = {k: v for k, v in posters.items() if v}
    if out == {k: old.get(k) for k in out}:
        print('no change')
        return
    out['updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('wrote', len(out['series']), 'series,', len(out['channels']), 'channels')


if __name__ == '__main__':
    main()
