"""League tables for the matches page (runs in GitHub Actions with fetch_matches.py, every 6 hours).

Premier League, La Liga and the Saudi Pro League come from ESPN's public standings feed; the Egyptian league
(not on ESPN) from TheSportsDB. A league that fails keeps its last good table, so the page never goes empty.

Output: assets/data/standings.json  →  read by assets/standings.js (matches page).
"""
import json, os, sys
from datetime import datetime, timezone

from fetch_matches import TEAMS, EXTRA_AR, norm, small_logo, team_key, get

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'standings.json')
TOP = 6

# order on the page: (id, name EN, name AR, source, source id)
LEAGUES = [
    ('egy', 'Egyptian League', 'الدوري المصري', 'sportsdb', 4829),
    ('eng', 'Premier League', 'الدوري الإنجليزي', 'espn', 'eng.1'),
    ('esp', 'La Liga', 'الدوري الإسباني', 'espn', 'esp.1'),
    ('ksa', 'Saudi Pro League', 'دوري روشن السعودي', 'espn', 'ksa.1'),
    ('ucl', 'Champions League', 'دوري أبطال أوروبا', 'espn', 'uefa.champions'),
    ('ita', 'Serie A', 'الدوري الإيطالي', 'espn', 'ita.1'),
    ('ger', 'Bundesliga', 'الدوري الألماني', 'espn', 'ger.1'),
    ('fra', 'Ligue 1', 'الدوري الفرنسي', 'espn', 'fra.1'),
]

def ar_name(en):
    k = team_key(en)
    if k:
        return TEAMS[k]
    return EXTRA_AR.get(norm(en), en)


def season_now():
    n = datetime.now(timezone.utc)
    y = n.year if n.month >= 7 else n.year - 1
    return f'{y}-{y + 1}'


def espn(code):
    d = get(f'https://site.api.espn.com/apis/v2/sports/soccer/{code}/standings')
    try:
        s = (d.get('children') or [d])[0]['standings']
        rows = []
        for x in s['entries']:
            t, st = x['team'], {i['name']: i.get('displayValue') for i in x['stats']}
            logo = (t.get('logos') or [{}])[0].get('href', '')
            rows.append({'rank': int(st.get('rank') or len(rows) + 1), 'en': t.get('shortDisplayName') or t['displayName'],
                         'full': t['displayName'], 'p': int(st.get('gamesPlayed') or 0),
                         'gd': st.get('pointDifferential') or '0', 'pts': int(st.get('points') or 0), 'logo': small_logo(logo)})
        return rows
    except Exception as e:
        print('  espn', code, e, file=sys.stderr)
        return None


def sportsdb(lid):
    d = get(f'https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l={lid}&s={season_now()}')
    try:
        rows = []
        for x in d['table']:
            gd = int(x.get('intGoalDifference') or 0)
            logo = (x.get('strBadge') or '').replace('\\/', '/')
            rows.append({'rank': int(x['intRank']), 'en': x['strTeam'], 'full': x['strTeam'], 'p': int(x.get('intPlayed') or 0),
                         'gd': f'+{gd}' if gd > 0 else str(gd), 'pts': int(x.get('intPoints') or 0), 'logo': small_logo(logo)})
        return rows
    except Exception as e:
        print('  sportsdb', lid, e, file=sys.stderr)
        return None


def main():
    old = {}
    try:
        with open(OUT, encoding='utf-8') as f:
            old = {l['id']: l for l in json.load(f).get('leagues', [])}
    except Exception:
        pass
    out, fresh = [], 0
    for lid, en, ar, src, sid in LEAGUES:
        rows = espn(sid) if src == 'espn' else sportsdb(sid)
        if rows and any(r['p'] for r in rows):
            rows = sorted(rows, key=lambda r: r['rank'])[:TOP]
            for r in rows:
                r['ar'] = ar_name(r['full'])
                del r['full']
            out.append({'id': lid, 'name': {'en': en, 'ar': ar}, 'rows': rows})
            fresh += 1
            print(lid, 'ok', len(rows))
        elif lid in old:
            out.append(old[lid])
            print(lid, 'kept old table')
        else:
            print(lid, 'no data')
    if not out:
        print('nothing fetched — keeping the old file')
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'leagues': out}, f, ensure_ascii=False, indent=1)
    print('wrote', fresh, 'fresh tables')


if __name__ == '__main__':
    main()
