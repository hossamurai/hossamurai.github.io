"""Basketball for the basketball page (en/ar basketball.html) — most Lebanese customers follow basketball more than football.

Sources:
  - ESPN: NBA (the next 7 days) and FIBA (national teams, the next 3 weeks — Lebanon's games and every World Cup game)
  - TheSportsDB: EuroLeague (the next round and the last results)
  - The Lebanese league comes from the admin bot (no free feed carries it): fetch_site.py saves those games in bot.json
Output: assets/data/basketball.json — {updated, events: [...], results: [...]} in the same shape as matches.json.
A source that is down keeps its games from the previous file.
"""
import json, os, sys, time
from datetime import datetime, timedelta, timezone

from fetch_matches import get, small_logo   # same polite fetcher and badge resizer as the football matches

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'basketball.json')
NBA_DAYS, FIBA_DAYS = 7, 21
LEAGUES = {'nba': ('NBA', 'الدوري الأمريكي NBA'), 'fiba': ('FIBA', 'فيبا — المنتخبات'), 'euroleague': ('EuroLeague', 'اليوروليغ')}
AR_TEAMS = {'lebanon': 'لبنان', 'egypt': 'مصر', 'jordan': 'الأردن', 'saudi arabia': 'السعودية', 'qatar': 'قطر', 'iran': 'إيران',
            'united states': 'أمريكا', 'spain': 'إسبانيا', 'france': 'فرنسا', 'germany': 'ألمانيا', 'serbia': 'صربيا', 'greece': 'اليونان',
            'real madrid': 'ريال مدريد', 'barcelona': 'برشلونة', 'fc barcelona': 'برشلونة', 'olympiacos': 'أولمبياكوس', 'panathinaikos': 'باناثينايكوس',
            'fenerbahce': 'فنربخشة', 'anadolu efes': 'أنادولو إفيس'}


def team(name, logo=''):
    n = (name or '').strip()
    return {'en': n, 'ar': AR_TEAMS.get(n.lower(), n), 'logo': small_logo(logo)}


def main():
    now = datetime.now(timezone.utc)
    events, results, ok = [], [], set()
    try:
        old = json.load(open(OUT))
    except Exception:
        old = {}

    def espn(code, days_ahead, keep):
        for i in range(-2, days_ahead + 1):
            day = (now + timedelta(days=i)).strftime('%Y%m%d')
            d = get(f'https://site.api.espn.com/apis/site/v2/sports/basketball/{code}/scoreboard?dates={day}')
            if d is None:
                return
            ok.add(code)
            for ev in d.get('events', []):
                try:
                    comp = ev['competitions'][0]
                    kick = datetime.fromisoformat(ev['date'].replace('Z', '+00:00'))
                    state = ev.get('status', {}).get('type', {}).get('state', 'pre')
                except Exception:
                    continue
                ts = sorted(comp.get('competitors', []), key=lambda c: 0 if c.get('homeAway') == 'home' else 1)
                if len(ts) != 2:
                    continue
                h, a = (team(t.get('team', {}).get('displayName', ''), t.get('team', {}).get('logo', '')) for t in ts)
                if not keep(h['en'], a['en']):
                    continue
                base = {'id': 'b' + str(ev.get('id')), 'utc': kick.strftime('%Y-%m-%dT%H:%M:%SZ'), 'code': code,
                        'league': {'en': LEAGUES[code][0], 'ar': LEAGUES[code][1]}, 'home': h, 'away': a}
                if state == 'post' and kick > now - timedelta(days=2):
                    try:
                        results.append({**base, 'hs': int(ts[0].get('score')), 'as': int(ts[1].get('score'))})
                    except (TypeError, ValueError):
                        pass
                elif state != 'post' and now - timedelta(hours=3) < kick < now + timedelta(days=days_ahead):
                    events.append({**base, 'live': state == 'in'})

    espn('nba', NBA_DAYS, lambda h, a: True)
    # national teams: every World Cup / qualifier game of Lebanon and the Arab teams, and the big games
    espn('fiba', FIBA_DAYS, lambda h, a: True)

    def sportsdb(lid, code):
        time.sleep(3)   # the free key allows a few calls a second; the football fetcher has just used it
        nxt = get(f'https://www.thesportsdb.com/api/v1/json/123/eventsnextleague.php?id={lid}')
        past = get(f'https://www.thesportsdb.com/api/v1/json/123/eventspastleague.php?id={lid}')
        if nxt is None and past is None:
            return
        ok.add(code)
        # the free "next" list holds one game: read that game's whole round (and the one after)
        first = ((nxt or {}).get('events') or [{}])[0]
        if first.get('intRound') and first.get('strSeason'):
            evs = []
            for r in (int(first['intRound']), int(first['intRound']) + 1):
                time.sleep(2)
                d = get(f'https://www.thesportsdb.com/api/v1/json/123/eventsround.php?id={lid}&r={r}&s={first["strSeason"]}')
                evs += (d or {}).get('events') or []
            if evs:
                nxt = {'events': evs}
            else:
                ok.discard(code)   # the round didn't come through: keep the last full list below
        for src, done in ((nxt, False), (past, True)):
            for ev in (src or {}).get('events') or []:
                ts = ev.get('strTimestamp') or ((ev.get('dateEvent') or '') + 'T' + (ev.get('strTime') or '00:00:00'))
                try:
                    kick = datetime.fromisoformat(ts.replace('Z', '')[:19]).replace(tzinfo=timezone.utc)
                except Exception:
                    continue
                base = {'id': 's' + str(ev.get('idEvent')), 'utc': kick.strftime('%Y-%m-%dT%H:%M:%SZ'), 'code': code,
                        'league': {'en': LEAGUES[code][0], 'ar': LEAGUES[code][1]},
                        'home': team(ev.get('strHomeTeam'), ev.get('strHomeTeamBadge')), 'away': team(ev.get('strAwayTeam'), ev.get('strAwayTeamBadge'))}
                if done:
                    if kick > now - timedelta(days=4) and ev.get('intHomeScore') not in (None, '') and ev.get('intAwayScore') not in (None, ''):
                        results.append({**base, 'hs': int(ev['intHomeScore']), 'as': int(ev['intAwayScore'])})
                elif now - timedelta(hours=3) < kick < now + timedelta(days=10):
                    events.append({**base, 'live': False})

    sportsdb(4546, 'euroleague')

    # a source that didn't answer keeps its games from the last good run
    for code in LEAGUES:
        if code not in ok:
            events += [e for e in old.get('events', []) if e.get('code') == code and e['utc'] > (now - timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M:%SZ')]
            results += [r for r in old.get('results', []) if r.get('code') == code]
    seen = set()
    events = [e for e in events if not (e['id'] in seen or seen.add(e['id']))]
    results = [r for r in results if not (r['id'] in seen or seen.add(r['id']))]
    events.sort(key=lambda e: e['utc'])
    results.sort(key=lambda r: r['utc'], reverse=True)
    data = {'events': events, 'results': results[:12]}
    if {k: old.get(k) for k in data} == data:
        print('basketball: no change')
        return 0
    data['updated'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f'basketball: {len(events)} games, {len(data["results"])} results from {sorted(ok)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
