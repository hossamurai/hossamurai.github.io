"""Fetch this week's big football matches for the website (runs in GitHub Actions every 6 hours).

Fixtures come from ESPN's public scoreboard feed (one request per league per day) — except the Egyptian league,
which ESPN doesn't carry and always comes from TheSportsDB; if ESPN refuses (it sometimes blocks cloud servers),
they come from TheSportsDB (current + next round of each league); if that fails too, from fixturedownload.com (big European leagues).
If all three fail, the last good file is kept (past matches are hidden by the website), so the bar never breaks. The TV channel is NOT in that feed for the Middle East,
so it comes from CHANNELS below (who holds the rights in the Middle East / North Africa). Check it each
season and edit it if rights change.

Output: assets/data/matches.json  →  read by assets/site.js (home page + matches page).
"""
import json, os, re, sys, time, unicodedata, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'matches.json')
DAYS = 7
RESULT_DAYS = 7      # finished big matches from the last week -> "Last results" on the matches page
MAX_RESULTS = 12
MAX_EVENTS = 40

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
    'caf.confed':     ('CAF Confederation Cup', 'كأس الكونفدرالية الأفريقية', 'beIN Sports', 'بي إن سبورت', False),
    'caf.nations':    ('Africa Cup of Nations', 'كأس الأمم الأفريقية', 'beIN Sports', 'بي إن سبورت', True),
    'fifa.worldq.caf':('World Cup Qualifiers', 'تصفيات كأس العالم', 'beIN Sports', 'بي إن سبورت', False),
    'fifa.friendly':  ('Friendly', 'مباراة ودية', '', '', False),
    # Lebanon (most customers in Canada are Lebanese): the league from TheSportsDB, the national team and clubs in Asian cups from ESPN
    'lbn.1':          ('Lebanese League', 'الدوري اللبناني', '', '', True),
    'fifa.worldq.afc':('World Cup Qualifiers (Asia)', 'تصفيات كأس العالم (آسيا)', '', '', False),
    'afc.asian.cup':  ('AFC Asian Cup', 'كأس آسيا', '', '', False),
    'afc.cupq':       ('Asian Cup Qualifiers', 'تصفيات كأس آسيا', '', '', False),
    'afc.champions':  ('AFC Champions League Elite', 'دوري أبطال آسيا للنخبة', '', '', False),
    'afc.cup':        ('AFC Champions League Two', 'دوري أبطال آسيا 2', '', '', False),
    'fifa.cwc':       ('FIFA Club World Cup', 'كأس العالم للأندية', '', '', False),
}

# Matches with at least one of these teams are shown (plus every match of leagues marked True above).
# key = how ESPN writes it (lowercase, no accents); value = Arabic name
TEAMS = {
    'al ahly': 'الأهلي', 'zamalek': 'الزمالك', 'pyramids': 'بيراميدز', 'egypt': 'مصر',
    'lebanon': 'لبنان', 'nejmeh': 'النجمة', 'al ahed': 'العهد', 'al-ahed': 'العهد', 'al ansar': 'الأنصار', 'al-ansar': 'الأنصار',
    'real madrid': 'ريال مدريد', 'barcelona': 'برشلونة', 'atletico madrid': 'أتلتيكو مدريد',
    'manchester city': 'مانشستر سيتي', 'liverpool': 'ليفربول', 'arsenal': 'آرسنال', 'chelsea': 'تشيلسي',
    'manchester united': 'مانشستر يونايتد', 'tottenham hotspur': 'توتنهام',
    'juventus': 'يوفنتوس', 'internazionale': 'إنتر ميلان', 'ac milan': 'ميلان', 'napoli': 'نابولي', 'as roma': 'روما',
    'bayern munich': 'بايرن ميونخ', 'borussia dortmund': 'بوروسيا دورتموند', 'paris saint-germain': 'باريس سان جيرمان',
    'al hilal': 'الهلال', 'al nassr': 'النصر', 'al ittihad': 'الاتحاد', 'al ahli': 'الأهلي السعودي', 'al-hilal': 'الهلال', 'al-nassr': 'النصر', 'al-ittihad': 'الاتحاد',
    'man city': 'مانشستر سيتي', 'man utd': 'مانشستر يونايتد', 'spurs': 'توتنهام', 'inter': 'إنتر ميلان', 'milan': 'ميلان',
    'atletico': 'أتلتيكو مدريد', 'atletico de madrid': 'أتلتيكو مدريد', 'bayern munchen': 'بايرن ميونخ', 'bayern': 'بايرن ميونخ',
    'dortmund': 'بوروسيا دورتموند', 'paris': 'باريس سان جيرمان', 'psg': 'باريس سان جيرمان', 'roma': 'روما',
    'morocco': 'المغرب', 'algeria': 'الجزائر', 'tunisia': 'تونس', 'saudi arabia': 'السعودية',
}


# Arabic names for teams that often sit near the top (only for the Arabic name — they don't make a match 'big')
EXTRA_AR = {
    # Lebanese league
    'sagesse': 'الحكمة', 'riyadi abbasiyah': 'الرياضي العباسية', 'safa': 'الصفاء', 'shabab al sahel': 'شباب الساحل',
    'tadamon sour': 'التضامن صور', 'bourj': 'البرج', 'racing beirut': 'الراسينغ', 'akhaa ahli aley': 'الإخاء الأهلي عاليه',
    'al ahed': 'العهد', 'nejmeh': 'النجمة', 'al ansar': 'الأنصار', 'salam zgharta': 'السلام زغرتا', 'shabab al ghazieh': 'شباب الغازية',
    # Egyptian league
    'asyut petroleum': 'بترول أسيوط', "tala'ea el gaish": 'طلائع الجيش', 'el qanah': 'القناة',
    # more European, Saudi and African clubs, so the Arabic pages never show English names
    'brentford': 'برينتفورد', 'everton': 'إيفرتون', 'ipswich town': 'إبسويتش تاون', 'leeds united': 'ليدز يونايتد', 'brighton': 'برايتون',
    'west ham united': 'وست هام', 'crystal palace': 'كريستال بالاس', 'fulham': 'فولهام', 'wolverhampton wanderers': 'وولفرهامبتون', 'bournemouth': 'بورنموث',
    'afc bournemouth': 'بورنموث', 'burnley': 'بيرنلي', 'sunderland': 'سندرلاند', 'leicester city': 'ليستر سيتي', 'southampton': 'ساوثهامبتون',
    'celta vigo': 'سيلتا فيغو', 'espanyol': 'إسبانيول', 'getafe': 'خيتافي', 'osasuna': 'أوساسونا', 'mallorca': 'مايوركا',
    'rayo vallecano': 'رايو فايكانو', 'alaves': 'ألافيس', 'deportivo alaves': 'ألافيس', 'elche': 'إلتشي', 'levante': 'ليفانتي',
    'real oviedo': 'ريال أوفييدو', 'cagliari': 'كالياري', 'frosinone': 'فروزينوني', 'genoa': 'جنوى', 'parma': 'بارما',
    'sassuolo': 'ساسولو', 'venezia': 'فينيسيا', 'udinese': 'أودينيزي', 'lecce': 'ليتشي', 'verona': 'فيرونا',
    'hellas verona': 'فيرونا', 'cremonese': 'كريمونيزي', 'pisa': 'بيزا', 'werder bremen': 'فيردر بريمن', 'mainz': 'ماينز',
    'fsv mainz 05': 'ماينز', 'tsg hoffenheim': 'هوفنهايم', 'fc augsburg': 'أوغسبورغ', 'hamburg sv': 'هامبورغ', '1. fc koln': 'كولن',
    'fc heidenheim': 'هايدنهايم', 'st. pauli': 'سانت باولي', 'strasbourg': 'ستراسبورغ', 'paris fc': 'باريس إف سي', 'le mans': 'لومان',
    'nantes': 'نانت', 'toulouse': 'تولوز', 'brest': 'بريست', 'auxerre': 'أوكسير', 'angers': 'أنجيه',
    'le havre': 'لوهافر', 'lorient': 'لوريان', 'metz': 'ميتز', 'rb salzburg': 'سالزبورغ', 'lask linz': 'لاسك لينز',
    'lask': 'لاسك لينز', 'fc porto': 'بورتو', 'rangers': 'رينجرز', 'fenerbahce': 'فنربخشة', 'besiktas': 'بشكتاش',
    'olympiacos': 'أولمبياكوس', 'dinamo zagreb': 'دينامو زغرب', 'young boys': 'يونغ بويز', 'slavia prague': 'سلافيا براغ', 'sparta prague': 'سبارتا براغ',
    'copenhagen': 'كوبنهاغن', 'fc copenhagen': 'كوبنهاغن', 'al riyadh': 'الرياض', 'neom sc': 'نيوم', 'neom': 'نيوم',
    'al kholood': 'الخلود', 'al okhdood': 'الأخدود', 'al hazem': 'الحزم', 'al najma': 'النجمة', 'damac': 'ضمك',
    'al wehda': 'الوحدة', 'apr fc': 'إيه بي آر', 'el merriekh bentiu': 'المريخ بانتيو', 'al hilal omdurman': 'الهلال السوداني', 'esperance de tunis': 'الترجي',
    'wydad casablanca': 'الوداد', 'raja casablanca': 'الرجاء', 'mamelodi sundowns': 'ماميلودي صن داونز', 'al merrikh': 'المريخ', 'petro de luanda': 'بترو أتلتيكو',
    'orlando pirates': 'أورلاندو بايرتس', 'simba sc': 'سيمبا', 'young africans': 'يانغ أفريكانز',
    'bodo/glimt': 'بودو جليمت', 'bod/glimt': 'بودو جليمت', 'galatasaray': 'غلطة سراي', 'club brugge': 'كلوب بروج', 'viking fk': 'فايكنج', 'al qadsiah': 'القادسية', 'al ahli': 'الأهلي السعودي', 'al-ahli': 'الأهلي السعودي', 'al ettifaq': 'الاتفاق', 'al shabab': 'الشباب',
    'al taawoun': 'التعاون', 'al fateh': 'الفتح', 'al khaleej': 'الخليج', 'al fayha': 'الفيحاء',
    'ceramica cleopatra': 'سيراميكا كليوباترا', 'al masry': 'المصري', 'ismaily': 'الإسماعيلي', 'future fc': 'فيوتشر',
    'modern sport': 'مودرن سبورت', 'national bank of egypt': 'البنك الأهلي', 'enppi': 'إنبي', 'smouha': 'سموحة',
    'zed fc': 'زد', 'el gouna': 'الجونة', 'pharco': 'فاركو', 'petrojet': 'بتروجت', 'talaea el gaish': 'طلائع الجيش',
    'ghazl el mahalla': 'غزل المحلة', 'al ittihad alexandria': 'الاتحاد السكندري', 'wadi degla': 'وادي دجلة', 'haras el hodoud': 'حرس الحدود',
    'brighton & hove albion': 'برايتون', 'newcastle united': 'نيوكاسل', 'aston villa': 'أستون فيلا', 'nottingham forest': 'نوتنغهام فورست',
    'real betis': 'ريال بيتيس', 'villarreal': 'فياريال', 'athletic club': 'أتلتيك بلباو', 'real sociedad': 'ريال سوسيداد',
    'atalanta': 'أتالانتا', 'lazio': 'لاتسيو', 'fiorentina': 'فيورنتينا', 'bologna': 'بولونيا', 'como': 'كومو', 'torino': 'تورينو',
    'bayer leverkusen': 'باير ليفركوزن', 'rb leipzig': 'لايبزيغ', 'eintracht frankfurt': 'آينتراخت فرانكفورت', 'vfb stuttgart': 'شتوتغارت',
    'sc freiburg': 'فرايبورغ', 'vfl wolfsburg': 'فولفسبورغ', 'borussia monchengladbach': 'مونشنغلادباخ', 'union berlin': 'أونيون برلين', '1. fc union berlin': 'أونيون برلين',
    'marseille': 'مارسيليا', 'olympique de marseille': 'مارسيليا', 'monaco': 'موناكو', 'as monaco': 'موناكو', 'lille': 'ليل', 'losc lille': 'ليل',
    'lyon': 'ليون', 'olympique lyonnais': 'ليون', 'nice': 'نيس', 'ogc nice': 'نيس', 'lens': 'لانس', 'rc lens': 'لانس', 'stade rennais': 'رين', 'rennes': 'رين',
    'benfica': 'بنفيكا', 'porto': 'بورتو', 'sporting cp': 'سبورتنغ لشبونة', 'psv eindhoven': 'آيندهوفن', 'feyenoord': 'فينورد', 'ajax': 'أياكس',
    'galatasaray': 'غلطة سراي', 'club brugge': 'كلوب بروج', 'celtic': 'سلتيك', 'shakhtar donetsk': 'شاختار', 'red bull salzburg': 'سالزبورغ',
    'girona': 'جيرونا', 'sevilla': 'إشبيلية', 'valencia': 'فالنسيا', }



# TheSportsDB league ids (Egyptian league always; the rest only if ESPN is down)
SPORTSDB_IDS = {'egy.1': 4829, 'uefa.champions': 4480, 'eng.1': 4328, 'esp.1': 4335, 'ita.1': 4332,
                'ger.1': 4331, 'fra.1': 4334, 'ksa.1': 4668, 'uefa.europa': 4481, 'lbn.1': 5243}


# fixturedownload.com feed names (third source) -> the ESPN code above; season = year it starts
FIXTUREDOWNLOAD = [('champions-league', 'uefa.champions'), ('epl', 'eng.1'), ('la-liga', 'esp.1'),
                   ('serie-a', 'ita.1'), ('bundesliga', 'ger.1'), ('ligue-1', 'fra.1')]


# leagues ESPN doesn't carry (they come from TheSportsDB below)
NO_ESPN = {'egy.1', 'lbn.1'}


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower().strip()
    return s


# short names only count as an exact match ("Inter" yes, "Inter Miami" no; "Paris FC" is not PSG)
EXACT_ONLY = {'inter', 'milan', 'paris', 'psg', 'bayern', 'roma', 'spurs', 'atletico', 'dortmund', 'man city', 'man utd', 'egypt',
              # Saudi clubs share their names with clubs across Africa (Al Ahli Tripoli, Al Hilal Omdurman, Al Ittihad Alexandria…)
              'al hilal', 'al nassr', 'al ittihad', 'al ahli', 'al-hilal', 'al-nassr', 'al-ittihad', 'al-ahli',
              'lebanon', 'al ansar', 'al-ansar'}


def team_key(name):
    n = norm(name)
    for k in TEAMS:
        if n == k or (k not in EXACT_ONLY and (n.startswith(k + ' ') or n.endswith(' ' + k))):
            return k
    return None


def small_logo(url):
    """Team badges at thumbnail size (ESPN's image resizer / TheSportsDB's /tiny), so pages stay light."""
    url = (url or '').replace('\\/', '/')
    if 'a.espncdn.com/i/teamlogos/' in url:
        return 'https://a.espncdn.com/combiner/i?img=' + url.split('a.espncdn.com', 1)[1] + '&w=80&h=80'
    if 'thesportsdb.com' in url and not url.endswith(('/tiny', '/small')):
        return url + '/tiny'
    return url


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



LOGOS = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'data', 'logos.json')


def wiki_logo(name):
    """The club's logo from its Wikipedia article ("Pyramids FC" -> the badge in the infobox), only when the article is that club."""
    core = re.sub(r'\b(FC|SC|CF|AFC|Club)\b', '', name).strip().lower()
    try:
        q = urllib.parse.urlencode({'action': 'query', 'generator': 'search', 'gsrsearch': f'{name} football club', 'gsrlimit': 5,
                                    'prop': 'pageimages', 'piprop': 'thumbnail', 'pithumbsize': 120, 'pilicense': 'any', 'format': 'json', 'formatversion': 2})
        req = urllib.request.Request('https://en.wikipedia.org/w/api.php?' + q, headers={'User-Agent': 'hossamservices.com matches (https://hossamservices.com)'})
        with urllib.request.urlopen(req, timeout=15) as r:
            pages = sorted((json.load(r).get('query') or {}).get('pages', []), key=lambda p: p.get('index', 99))
    except Exception as e:
        print('  wikipedia logo failed', name, e, file=sys.stderr)
        return ''
    for p in pages:
        src = (p.get('thumbnail') or {}).get('source', '')
        title = unicodedata.normalize('NFKD', p.get('title', '')).encode('ascii', 'ignore').decode().lower()
        file = src.rsplit('/', 1)[-1].lower()
        # the club's own article, and a badge (a local upload, or a Commons file named logo / crest / badge)
        if src and core and core in title and ('/wikipedia/en/' in src or re.search(r'logo|crest|badge|emblem', file)):
            return src.split('?')[0]
    return ''


def fill_logos(items):
    """Teams a feed gave no badge (often African clubs) — looked up once and remembered in assets/data/logos.json
    (a miss is tried again after 7 days). Sources in order: TheSportsDB, Wikipedia (the club article's logo),
    then the crest FilGoal / Kooora show next to the team. The website draws the team's first letter if none is found."""
    try:
        cache = json.load(open(LOGOS))
    except Exception:
        cache = {}
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    retry = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')
    asked = 0
    for it in items:
        for side in ('home', 'away'):
            t = it[side]
            if t.get('logo'):
                continue
            name = t['en']
            hit = cache.get(name)
            if hit is None or (not hit.get('logo') and hit.get('checked', '') < retry and asked < 20):
                logo = ''
                for q in dict.fromkeys([name, re.sub(r'\b(FC|SC|CF|AFC)\b', '', name).strip()]):
                    d = get('https://www.thesportsdb.com/api/v1/json/123/searchteams.php?t=' + urllib.parse.quote(q))
                    asked += 1
                    teams = [x for x in ((d or {}).get('teams') or []) if x.get('strSport') == 'Soccer' and x.get('strBadge')]
                    if teams:
                        logo = small_logo(teams[0]['strBadge'])
                        break
                if not logo:
                    logo = wiki_logo(name)
                if not logo:
                    try:
                        import exact_channels
                        logo = exact_channels.crest_for(t.get('ar') or name)
                    except Exception:
                        pass
                hit = cache[name] = {'logo': logo, 'checked': today}
            if hit.get('logo'):
                t['logo'] = hit['logo']
    try:
        with open(LOGOS, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
    except Exception as e:
        print('  logos cache not saved', e, file=sys.stderr)

HEALTH = os.path.join(os.path.dirname(OUT), 'sources.json')


def report_health(ok):
    """Remembers how many runs in a row each source failed (assets/data/sources.json) and pings Hossam's ntfy
    (secret NTFY_TOPIC) when one fails twice in a row, and again when it is back — so a source can't stop silently."""
    try:
        fails = json.load(open(HEALTH))
    except Exception:
        fails = {}
    msgs = []
    for name, good in ok.items():
        before = int(fails.get(name, 0))
        now_ = 0 if good else before + 1
        fails[name] = now_
        if now_ == 2:
            msgs.append(f'⚠️ Match source down: {name} failed 2 runs in a row (12 h). The site keeps the last data it had.')
        elif before >= 2 and good:
            msgs.append(f'✅ Match source back: {name}')
    with open(HEALTH, 'w') as f:
        json.dump(fails, f, indent=1, sort_keys=True)
    topic = os.environ.get('NTFY_TOPIC', '').strip()
    for m in msgs:
        print('  ' + m)
        if topic:
            try:
                urllib.request.urlopen(urllib.request.Request('https://ntfy.sh/' + topic, data=m.encode(), headers={'Title': 'Hossam TV website', 'Tags': 'soccer'}), timeout=15)
            except Exception as e:
                print('  ntfy failed', e, file=sys.stderr)


def main():
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=DAYS)
    events, results, ok_leagues = [], [], 0
    since = now - timedelta(days=RESULT_DAYS)

    added = set()

    def add(code, ev_id, kick, live, home, away, hlogo='', alogo=''):
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
            # for the live-score bar: the browser asks ESPN for this league's scoreboard during the match
            'code': code, 'espn': ev_id[1:] if ev_id.startswith('e') else None,
            'league': {'en': len_, 'ar': lar},
            'home': {'en': home, 'ar': TEAMS.get(keys[0]) or EXTRA_AR.get(norm(home)) or home, 'logo': small_logo(hlogo)},
            'away': {'en': away, 'ar': TEAMS.get(keys[1]) or EXTRA_AR.get(norm(away)) or away, 'logo': small_logo(alogo)},
            'channel': {'en': chen, 'ar': char} if chen else None,
            'big': sum(1 for k in keys if k),
            # high-profile = two popular teams (Ahly–Zamalek, Real–Barça, City–PSG…) or Egypt's national team → home-page countdown
            'top': all(keys) or 'egypt' in keys or 'lebanon' in keys,
        })

    done = set()

    def add_result(code, rid, kick, home, away, hs, as_, hlogo='', alogo=''):
        """A finished match with at least one popular team (or a league we show in full)."""
        k = (code, kick.strftime('%Y-%m-%d'), norm(home)[:6], norm(away)[:6])
        if rid in done or k in done or kick < since or hs is None or as_ is None:
            return
        done.update((rid, k))
        len_, lar, _, _, all_matches = LEAGUES[code]
        keys = [team_key(home), team_key(away)]
        if not all_matches and not any(keys):
            return
        try:
            hs, as_ = int(hs), int(as_)
        except (TypeError, ValueError):
            return
        results.append({
            'id': rid, 'utc': kick.strftime('%Y-%m-%dT%H:%M:%SZ'), 'league': {'en': len_, 'ar': lar},
            'home': {'en': home, 'ar': TEAMS.get(keys[0]) or EXTRA_AR.get(norm(home)) or home, 'logo': small_logo(hlogo)},
            'away': {'en': away, 'ar': TEAMS.get(keys[1]) or EXTRA_AR.get(norm(away)) or away, 'logo': small_logo(alogo)},
            'hs': hs, 'as': as_, 'big': sum(1 for x in keys if x), 'top': all(keys) or 'egypt' in keys or 'lebanon' in keys,
        })

    def espn_event(code, ev):
        try:
            comp = ev['competitions'][0]
            state = ev.get('status', {}).get('type', {}).get('state', 'pre')
            kick = datetime.fromisoformat(ev['date'].replace('Z', '+00:00'))
        except Exception:
            return
        teams = sorted(comp.get('competitors', []), key=lambda c: 0 if c.get('homeAway') == 'home' else 1)
        if len(teams) != 2:
            return
        names = [t.get('team', {}).get('displayName', '') for t in teams]
        logos = [t.get('team', {}).get('logo', '') for t in teams]
        if state == 'post':
            add_result(code, 'e' + str(ev.get('id')), kick, names[0], names[1], teams[0].get('score'), teams[1].get('score'), *logos)
            return
        if kick < now - timedelta(hours=2) or kick > end:
            return
        add(code, 'e' + str(ev.get('id')), kick, state == 'in', names[0], names[1], *logos)

    # ESPN answers one day at a time (date ranges get "400 Bad Request")
    days = [(now + timedelta(days=i)).strftime('%Y%m%d') for i in range(-RESULT_DAYS, DAYS + 1)]
    seen, espn_raw = set(), 0
    for code in LEAGUES:
        if code in NO_ESPN:
            continue
        for day in days:
            d = get(f'https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard?dates={day}')
            if not d:
                break   # league not on ESPN (or ESPN down) -> skip its other days
            if day < now.strftime('%Y%m%d'):
                for ev in d.get('events', []):   # past days: results only
                    if ev.get('id') not in seen:
                        seen.add(ev.get('id'))
                        espn_event(code, ev)
                continue
            ok_leagues += 1
            espn_raw += len(d.get('events', []))
            for ev in d.get('events', []):
                if ev.get('id') in seen:
                    continue
                seen.add(ev.get('id'))
                espn_event(code, ev)

    sdb_ok = {}

    def sportsdb_league(code, lid):
        """Current + next round of one league from TheSportsDB (free key: rounds are complete, day lists are not)."""
        nxt = get(f'https://www.thesportsdb.com/api/v1/json/123/eventsnextleague.php?id={lid}')
        sdb_ok[code] = nxt is not None          # answered (an empty list off-season still counts as working)
        evs = (nxt or {}).get('events') or []
        if not evs:
            return 0
        season, rnd = evs[0].get('strSeason'), int(evs[0].get('intRound') or 0)
        got = 0
        for r in ([rnd, rnd + 1] if rnd else [None]):
            d = get(f'https://www.thesportsdb.com/api/v1/json/123/eventsround.php?id={lid}&r={r}&s={season}') if r else nxt
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
                add(code, 's' + str(ev.get('idEvent')), kick, status in ('1h', '2h', 'ht', 'live'), ev.get('strHomeTeam') or '', ev.get('strAwayTeam') or '',
                    ev.get('strHomeTeamBadge') or '', ev.get('strAwayTeamBadge') or '')
            time.sleep(1)
        return got

    def sportsdb_results(code, lid):
        """Last finished matches of one league (TheSportsDB) -> results."""
        d = get(f'https://www.thesportsdb.com/api/v1/json/123/eventspastleague.php?id={lid}')
        for ev in (d or {}).get('events') or []:
            ts = ev.get('strTimestamp') or ((ev.get('dateEvent') or '') + 'T' + (ev.get('strTime') or '00:00:00'))
            try:
                kick = datetime.fromisoformat(ts.replace('Z', '')[:19]).replace(tzinfo=timezone.utc)
            except Exception:
                continue
            add_result(code, 's' + str(ev.get('idEvent')), kick, ev.get('strHomeTeam') or '', ev.get('strAwayTeam') or '',
                       ev.get('intHomeScore'), ev.get('intAwayScore'), ev.get('strHomeTeamBadge') or '', ev.get('strAwayTeamBadge') or '')

    # Egyptian and Lebanese leagues are not on ESPN: always from TheSportsDB
    for code in NO_ESPN:
        if sportsdb_league(code, SPORTSDB_IDS[code]):
            ok_leagues += 1
        sportsdb_results(code, SPORTSDB_IDS[code])

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
    health = {'ESPN': espn_raw > 0, 'TheSportsDB (Egyptian league)': sdb_ok.get('egy.1', False), 'TheSportsDB (Lebanese league)': sdb_ok.get('lbn.1', False)}
    if ok_leagues == 0:
        print('::warning::No match source reachable — keeping the previous matches.json')
        report_health(health)
        return 0
    # safety net: Egyptian / Lebanese teams' games the sources above missed (another competition, a source down) from FilGoal / Kooora
    try:
        import extra_sources
        from exact_channels import same_team
        known = {}   # Arabic -> English for every club the site knows, so English pages don't show Arabic names
        for k, v in list(EXTRA_AR.items()) + list(TEAMS.items()):
            known.setdefault(v, ' '.join(w if w.isupper() else w.capitalize() for w in k.replace('-', ' ').split()))
        ar_to_en = lambda ar: next((en for a, en in known.items() if same_team(ar, a)), None)
        if extra_sources.add_missing(events, team_key, now, end, ar_to_en):
            ok_leagues += 1
    except Exception as ex:
        print('  FilGoal / Kooora safety net skipped:', ex, file=sys.stderr)
    try:
        health.update(extra_sources.STATUS)
    except Exception:
        pass
    report_health(health)
    # keep the biggest games if there are too many: matches with 2 popular teams first, then by time
    events.sort(key=lambda e: e['utc'])
    if len(events) > MAX_EVENTS:
        keep = sorted(events, key=lambda e: (-e['big'], e['utc']))[:MAX_EVENTS]
        ids = {e['id'] for e in keep}
        events = [e for e in events if e['id'] in ids]
    for e in events:
        e.pop('big', None)
    # last results: newest first, the biggest games if there are too many
    results.sort(key=lambda r: r['utc'], reverse=True)
    if len(results) > MAX_RESULTS:
        keep = {r['id'] for r in sorted(results, key=lambda r: -r['big'])[:MAX_RESULTS]}   # stable sort: newest first within each group
        results = [r for r in results if r['id'] in keep]
    for r in results:
        r.pop('big', None)
    # the exact channel of each match ("beIN Sports 2") from FilGoal / Kooora; the league's usual channel otherwise
    try:
        import exact_channels
        prev = json.load(open(OUT)).get('events', []) if os.path.exists(OUT) else []
        exact_channels.apply(events, prev)
    except Exception as ex:
        print('  exact channels skipped:', ex, file=sys.stderr)
    fill_logos(events + results)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = {'updated': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'events': events, 'results': results}
    old = None
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT))
        except Exception:
            pass
    if not results and old and old.get('results'):
        data['results'] = old['results']   # results source down -> keep last week's
    if old and old.get('events') == events and old.get('results') == data['results']:
        print('No change')
        return 0
    json.dump(data, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f'Wrote {len(events)} matches from {ok_leagues} leagues')
    return 0


if __name__ == '__main__':
    sys.exit(main())
