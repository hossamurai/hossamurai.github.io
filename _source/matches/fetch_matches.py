"""Fetch this week's big football matches for the website (runs in GitHub Actions every 6 hours).

Fixtures come from ESPN's public scoreboard feed (one request per league per day) — except the Egyptian league,
which ESPN doesn't carry and always comes from TheSportsDB; if ESPN refuses (it sometimes blocks cloud servers),
they come from TheSportsDB (current + next round of each league); if that fails too, from fixturedownload.com (big European leagues).
If all three fail, the last good file is kept (past matches are hidden by the website), so the bar never breaks. The TV channel is NOT in that feed for the Middle East,
so it comes from CHANNELS below (who holds the rights in the Middle East / North Africa). Check it each
season and edit it if rights change.

Output: assets/data/matches.json  →  read by assets/site.js (home page + matches page).
"""
import json, os, sys, time, unicodedata, urllib.request
from datetime import datetime, timedelta, timezone

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'matches.json')
DAYS = 7
MAX_EVENTS = 30

# ESPN league code -> (league name EN, AR, channel EN, channel AR, include every match?)
LEAGUES = {
    'uefa.champions': ('Champions League', 'دوري أبطال أوروبا', 'beIN Sports', 'بي إن سبورت', True),
    'egy.1':          ('Egyptian League', 'الدوري المصري', 'ON Time Sports', 'أون تايم سبورت', False),
    'eng.1':          ('Premier League', 'الدوري الإنجليزي', 'beIN Sports', 'بي إن سبورت', False),
    'esp.1':          ('La Liga', 'الدوري الإسباني', 'beIN Sports', 'بي إن سبورت', False),
    'ita.1':          ('Serie A', 'الدوري الإيطالي', 'beIN Sports', 'بي إن سبورت', False),
    'ger.1':          ('Bundesliga', 'الدوري الألماني', 'beIN Sports', 'بي إن سبورت', False),
    'fra.1':          ('Ligue 1', 'الدوري الفرنسي', 'beIN Sports', 'بي إن سبورت', False),
    'ksa.1':          ('Saudi Pro League', 'دوري روشن السعودي', 'Thmanyah', 'ثمانية', False),
    'uefa.europa':    ('Europa League', 'الدوري الأوروبي', 'beIN Sports', 'بي إن سبورت', False),
    'caf.champions':  ('CAF Champions League', 'دوري أبطال أفريقيا', 'beIN Sports', 'بي إن سبورت', False),
    'caf.nations':    ('Africa Cup of Nations', 'كأس الأمم الأفريقية', 'beIN Sports', 'بي إن سبورت', True),
    'fifa.worldq.caf':('World Cup Qualifiers', 'تصفيات كأس العالم', 'beIN Sports', 'بي إن سبورت', False),
    'fifa.friendly':  ('Friendly', 'مباراة ودية', '', '', False),
}

# Matches with at least one of these teams are shown (plus every match of leagues marked True above).
# key = how ESPN writes it (lowercase, no accents); value = Arabic name
TEAMS = {
    'al ahly': 'الأهلي', 'zamalek': 'الزمالك', 'pyramids': 'بيراميدز', 'egypt': 'مصر',
    'real madrid': 'ريال مدريد', 'barcelona': 'برشلونة', 'atletico madrid': 'أتلتيكو مدريد',
    'manchester city': 'مانشستر سيتي', 'liverpool': 'ليفربول', 'arsenal': 'آرسنال', 'chelsea': 'تشيلسي',
    'manchester united': 'مانشستر يونايتد', 'tottenham hotspur': 'توتنهام',
    'juventus': 'يوفنتوس', 'internazionale': 'إنتر ميلان', 'ac milan': 'ميلان', 'napoli': 'نابولي', 'as roma': 'روما',
    'bayern munich': 'بايرن ميونخ', 'borussia dortmund': 'بوروسيا دورتموند', 'paris saint-germain': 'باريس سان جيرمان',
    'al hilal': 'الهلال', 'al nassr': 'النصر', 'al ittihad': 'الاتحاد', 'al-hilal': 'الهلال', 'al-nassr': 'النصر', 'al-ittihad': 'الاتحاد',
    'man city': 'مانشستر سيتي', 'man utd': 'مانشستر يونايتد', 'spurs': 'توتنهام', 'inter': 'إنتر ميلان', 'milan': 'ميلان',
    'atletico': 'أتلتيكو مدريد', 'atletico de madrid': 'أتلتيكو مدريد', 'bayern munchen': 'بايرن ميونخ', 'bayern': 'بايرن ميونخ',
    'dortmund': 'بوروسيا دورتموند', 'paris': 'باريس سان جيرمان', 'psg': 'باريس سان جيرمان', 'roma': 'روما',
    'morocco': 'المغرب', 'algeria': 'الجزائر', 'tunisia': 'تونس', 'saudi arabia': 'السعودية',
}


# TheSportsDB league ids (Egyptian league always; the rest only if ESPN is down)
SPORTSDB_IDS = {'egy.1': 4829, 'uefa.champions': 4480, 'eng.1': 4328, 'esp.1': 4335, 'ita.1': 4332,
                'ger.1': 4331, 'fra.1': 4334, 'ksa.1': 4668, 'uefa.europa': 4481}


# fixturedownload.com feed names (third source) -> the ESPN code above; season = year it starts
FIXTUREDOWNLOAD = [('champions-league', 'uefa.champions'), ('epl', 'eng.1'), ('la-liga', 'esp.1'),
                   ('serie-a', 'ita.1'), ('bundesliga', 'ger.1'), ('ligue-1', 'fra.1')]


# leagues ESPN doesn't carry (they come from TheSportsDB below)
NO_ESPN = {'egy.1'}


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower().strip()
    return s


# short names only count as an exact match ("Inter" yes, "Inter Miami" no; "Paris FC" is not PSG)
EXACT_ONLY = {'inter', 'milan', 'paris', 'psg', 'bayern', 'roma', 'spurs', 'atletico', 'dortmund', 'man city', 'man utd', 'egypt'}


def team_key(name):
    n = norm(name)
    for k in TEAMS:
        if n == k or (k not in EXACT_ONLY and (n.startswith(k + ' ') or n.endswith(' ' + k))):
            return k
    return None


def get(url, tries=2):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
                'Accept': 'application/json,text/plain,*/*', 'Accept-Language': 'en-US,en;q=0.9'})
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.load(r)
        except Exception as e:
            print('  retry', i + 1, url, e, file=sys.stderr)
            if '403' in str(e) or '404' in str(e):
                break
            time.sleep(3 * (i + 1))
    return None


def main():
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=DAYS)
    events, ok_leagues = [], 0

    added = set()

    def add(code, ev_id, kick, live, home, away):
        # same match from two lists / sources -> keep one
        k = (code, kick.strftime('%Y-%m-%dT%H'), norm(home)[:6], norm(away)[:6])
        if ev_id in added or k in added:
            return
        added.update((ev_id, k))
        len_, lar, chen, char, all_matches = LEAGUES[code]
        keys = [team_key(home), team_key(away)]
        if not all_matches and not any(keys):
            return
        events.append({
            'id': ev_id, 'utc': kick.strftime('%Y-%m-%dT%H:%M:%SZ'), 'live': live,
            'league': {'en': len_, 'ar': lar},
            'home': {'en': home, 'ar': TEAMS.get(keys[0]) or home},
            'away': {'en': away, 'ar': TEAMS.get(keys[1]) or away},
            'channel': {'en': chen, 'ar': char} if chen else None,
            'big': sum(1 for k in keys if k),
        })

    def espn_event(code, ev):
        try:
            comp = ev['competitions'][0]
            state = ev.get('status', {}).get('type', {}).get('state', 'pre')
            kick = datetime.fromisoformat(ev['date'].replace('Z', '+00:00'))
        except Exception:
            return
        if state == 'post' or kick < now - timedelta(hours=2) or kick > end:
            return
        teams = sorted(comp.get('competitors', []), key=lambda c: 0 if c.get('homeAway') == 'home' else 1)
        if len(teams) != 2:
            return
        names = [t.get('team', {}).get('displayName', '') for t in teams]
        add(code, 'e' + str(ev.get('id')), kick, state == 'in', names[0], names[1])

    # ESPN answers one day at a time (date ranges get "400 Bad Request")
    days = [(now + timedelta(days=i)).strftime('%Y%m%d') for i in range(DAYS + 1)]
    seen, espn_raw = set(), 0
    for code in LEAGUES:
        if code in NO_ESPN:
            continue
        for day in days:
            d = get(f'https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard?dates={day}')
            if not d:
                break   # league not on ESPN (or ESPN down) -> skip its other days
            ok_leagues += 1
            espn_raw += len(d.get('events', []))
            for ev in d.get('events', []):
                if ev.get('id') in seen:
                    continue
                seen.add(ev.get('id'))
                espn_event(code, ev)

    def sportsdb_league(code, lid):
        """Current + next round of one league from TheSportsDB (free key: rounds are complete, day lists are not)."""
        nxt = get(f'https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id={lid}')
        evs = (nxt or {}).get('events') or []
        if not evs:
            return 0
        season, rnd = evs[0].get('strSeason'), int(evs[0].get('intRound') or 0)
        got = 0
        for r in ([rnd, rnd + 1] if rnd else [None]):
            d = get(f'https://www.thesportsdb.com/api/v1/json/3/eventsround.php?id={lid}&r={r}&s={season}') if r else nxt
            for ev in (d or {}).get('events') or []:
                got += 1
                ts = ev.get('strTimestamp') or ((ev.get('dateEvent') or '') + 'T' + (ev.get('strTime') or '00:00:00'))
                try:
                    kick = datetime.fromisoformat(ts.replace('Z', '')[:19]).replace(tzinfo=timezone.utc)
                except Exception:
                    continue
                status = norm(ev.get('strStatus'))
                if status in ('match finished', 'ft', 'aet', 'pen', 'postponed', 'cancelled') or kick < now - timedelta(hours=2) or kick > end:
                    continue
                add(code, 's' + str(ev.get('idEvent')), kick, status in ('1h', '2h', 'ht', 'live'), ev.get('strHomeTeam') or '', ev.get('strAwayTeam') or '')
            time.sleep(1)
        return got

    # Egyptian league is not on ESPN: always from TheSportsDB
    for code in NO_ESPN:
        if sportsdb_league(code, SPORTSDB_IDS[code]):
            ok_leagues += 1

    # second source: TheSportsDB for every league, if ESPN gave nothing
    if espn_raw == 0:
        print('ESPN unavailable — using TheSportsDB', file=sys.stderr)
        for code, lid in SPORTSDB_IDS.items():
            if code not in NO_ESPN and sportsdb_league(code, lid):
                ok_leagues += 1

    # third source: fixturedownload.com season feeds (if neither gave anything)
    if not events and espn_raw == 0:
        print('TheSportsDB unavailable — using fixturedownload.com', file=sys.stderr)
        season = now.year if now.month >= 7 else now.year - 1
        for slug, code in FIXTUREDOWNLOAD:
            d = get(f'https://fixturedownload.com/feed/json/{slug}-{season}')
            if not isinstance(d, list):
                continue
            ok_leagues += 1
            for ev in d:
                try:
                    kick = datetime.strptime(str(ev.get('DateUtc', '')).replace('Z', '').strip(), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                except Exception:
                    continue
                if ev.get('HomeTeamScore') is not None or kick < now - timedelta(hours=2) or kick > end:
                    continue
                add(code, 'f' + slug + str(ev.get('MatchNumber')), kick, False, ev.get('HomeTeam') or '', ev.get('AwayTeam') or '')

    # last line: nothing reachable -> keep the previous file untouched (the site hides matches that are over)
    if ok_leagues == 0:
        print('::warning::No match source reachable — keeping the previous matches.json')
        return 0
    # keep the biggest games if there are too many: matches with 2 popular teams first, then by time
    events.sort(key=lambda e: e['utc'])
    if len(events) > MAX_EVENTS:
        keep = sorted(events, key=lambda e: (-e['big'], e['utc']))[:MAX_EVENTS]
        ids = {e['id'] for e in keep}
        events = [e for e in events if e['id'] in ids]
    for e in events:
        e.pop('big', None)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = {'updated': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'events': events}
    old = None
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT))
        except Exception:
            pass
    if old and old.get('events') == events:
        print('No change')
        return 0
    json.dump(data, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f'Wrote {len(events)} matches from {ok_leagues} leagues')
    return 0


if __name__ == '__main__':
    sys.exit(main())
