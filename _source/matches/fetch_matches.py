"""Fetch this week's big football matches for the website (runs in GitHub Actions every 6 hours).

Fixtures come from ESPN's public scoreboard feed. The TV channel is NOT in that feed for the Middle East,
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
    'morocco': 'المغرب', 'algeria': 'الجزائر', 'tunisia': 'تونس', 'saudi arabia': 'السعودية',
}


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower().strip()
    return s


def team_key(name):
    n = norm(name)
    for k in TEAMS:
        if n == k or n.startswith(k + ' ') or n.endswith(' ' + k):
            return k
    return None


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'hossamservices.com matches (+https://hossamservices.com)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print('  retry', i + 1, url, e, file=sys.stderr)
            time.sleep(3 * (i + 1))
    return None


def main():
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=DAYS)
    rng = f"{now:%Y%m%d}-{end:%Y%m%d}"
    events, ok_leagues = [], 0
    for code, (len_, lar, chen, char, all_matches) in LEAGUES.items():
        d = get(f'https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard?dates={rng}&limit=300')
        if not d:
            continue
        ok_leagues += 1
        for ev in d.get('events', []):
            try:
                comp = ev['competitions'][0]
                state = ev.get('status', {}).get('type', {}).get('state', 'pre')
                kick = datetime.fromisoformat(ev['date'].replace('Z', '+00:00'))
            except Exception:
                continue
            if state == 'post' or kick < now - timedelta(hours=2) or kick > end:
                continue
            teams = sorted(comp.get('competitors', []), key=lambda c: 0 if c.get('homeAway') == 'home' else 1)
            if len(teams) != 2:
                continue
            names = [t.get('team', {}).get('displayName', '') for t in teams]
            keys = [team_key(n) for n in names]
            if not all_matches and not any(keys):
                continue
            events.append({
                'id': ev.get('id'),
                'utc': kick.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'live': state == 'in',
                'league': {'en': len_, 'ar': lar},
                'home': {'en': names[0], 'ar': TEAMS.get(keys[0]) or names[0]},
                'away': {'en': names[1], 'ar': TEAMS.get(keys[1]) or names[1]},
                'channel': {'en': chen, 'ar': char} if chen else None,
                'big': sum(1 for k in keys if k),
            })
    if ok_leagues == 0:
        print('No data from ESPN — keeping the old file', file=sys.stderr)
        return 1
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
