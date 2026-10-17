"""Safety net for the games Egyptian and Lebanese customers care about most — used by fetch_matches.py.

ESPN / TheSportsDB don't carry every competition (the CAF Confederation Cup was missing once, the Egyptian Cup
and the Lebanese league aren't on ESPN at all). This reads the two Arabic sites that list every match of the day
and adds any game of the teams below that the main sources missed:
  1. FilGoal  — filgoal.com/matches/?date=YYYY-MM-DD, day by day (Egyptian, African and Arab competitions).
  2. Kooora   — today's matches worldwide (Lebanese league, Asian cups, friendlies…).
A game already on the list (same team, kick-off within 4 hours) is not added twice.
"""
import hashlib, re
from datetime import datetime, timedelta, timezone

from exact_channels import CAIRO, CRESTS, clean, key, page, text

# Arabic name as FilGoal / Kooora write it -> the English key used in fetch_matches.TEAMS.
# Exact names only: "الأهلي" is Al Ahly; "الأهلي السعودي" / "الأهلي طرابلس" are other clubs.
EGYPT = {'الأهلي': 'al ahly', 'الزمالك': 'zamalek', 'بيراميدز': 'pyramids', 'مصر': 'egypt', 'منتخب مصر': 'egypt'}
LEBANON = {'لبنان': 'lebanon', 'منتخب لبنان': 'lebanon', 'الأنصار': 'al ansar', 'النجمة': 'nejmeh', 'العهد': 'al ahed'}
# Lebanese club names are shared with Saudi clubs (النجمة, الأنصار): they only count in Lebanese / Asian / Arab competitions
LEBANESE_CONTEXT = {'لبنان', 'لبناني', 'اللبناني', 'آسيا', 'اسيا', 'الآسيوي', 'آسيوي', 'العرب', 'العربي', 'العربية', 'ودية', 'ودي', 'الودية'}   # whole words

EN_NAME = {'al ahly': 'Al Ahly', 'zamalek': 'Zamalek', 'pyramids': 'Pyramids FC', 'egypt': 'Egypt',
           'lebanon': 'Lebanon', 'al ansar': 'Al Ansar', 'nejmeh': 'Nejmeh', 'al ahed': 'Al Ahed'}
LEAGUE_EN = {'كأس الكونفدرالية': 'CAF Confederation Cup', 'كأس الكونفدرالية الأفريقية': 'CAF Confederation Cup',
             'دوري أبطال إفريقيا': 'CAF Champions League', 'دوري أبطال أفريقيا': 'CAF Champions League',
             'دوري المحترفين المصري': 'Egyptian League', 'الدوري المصري': 'Egyptian League', 'الدوري المصري الممتاز': 'Egyptian League',
             'كأس مصر': 'Egypt Cup', 'كأس السوبر المصري': 'Egyptian Super Cup', 'كأس الرابطة المصرية': 'Egyptian League Cup',
             'كأس السوبر الإفريقي': 'CAF Super Cup', 'كأس السوبر الأفريقي': 'CAF Super Cup',
             'الدوري اللبناني': 'Lebanese League', 'كأس لبنان': 'Lebanese Cup', 'كأس العالم للأندية': 'FIFA Club World Cup',
             'كأس إنتركونتيننتال': 'FIFA Intercontinental Cup', 'مباريات ودية': 'Friendly', 'مباراة ودية': 'Friendly'}


def _k(name):
    return ''.join(key(name))


_EG = {_k(a): v for a, v in EGYPT.items()}
_LB = {_k(a): v for a, v in LEBANON.items()}


def tracked(ar_name, competition=''):
    n = _k(ar_name)
    if n in _EG:
        return _EG[n]
    if n in _LB and (_LB[n] == 'lebanon' or set(re.findall(r'[\w\u0600-\u06FF]+', competition)) & LEBANESE_CONTEXT):
        return _LB[n]
    return None


def league_en(ar):
    ar = re.sub(r'\s+', ' ', ar).strip()
    for k, v in LEAGUE_EN.items():
        if ar.startswith(k):
            return v
    return ar


def filgoal_day(day):
    """[(competition, context, home, away, kick UTC, channel, home crest, away crest)] for one day from FilGoal."""
    h = page(f'https://www.filgoal.com/matches/?date={day}')
    if not h or 'match-list-viewer' not in h:
        return None
    h = h.split('id="match-list-viewer"', 1)[1]
    out = []
    for sec in h.split('<div class="mc-block"')[1:]:
        m = re.search(r'<h6[^>]*>\s*<span>(.*?)</span>', sec, re.S)
        comp = text(m.group(1)) if m else ''
        for blk in sec.split('<div class="cin_cntnr"')[1:]:
            teams = [text(t) for t in re.findall(r'<strong>(.*?)</strong>', blk, re.S)][:2]
            crests = ['https:' + s for s in re.findall(r'data-src="(//semedia\.filgoal\.com/Photos/Team/[^"]+)"', blk)][:2]
            when = re.search(r'(\d{1,2})-(\d{1,2})-(\d{4})\s*-\s*(\d{1,2}):(\d{2})', text(blk))
            ch = re.search(r'#fb_screen"\s*>\s*</use>\s*</svg>(.*?)</span>', blk, re.S)
            status = re.search(r'class="status[^"]*"\s*>(.*?)<', blk, re.S)
            if len(teams) != 2 or not when or (status and text(status.group(1)) == 'تأجيل'):
                continue
            d, mo, y, hh, mm = map(int, when.groups())
            kick = datetime(y, mo, d, hh, mm, tzinfo=CAIRO).astimezone(timezone.utc)
            out.append((comp, comp, teams[0], teams[1], kick, text(ch.group(1)) if ch else '', *(crests + ['', ''])[:2]))
    return out


def kooora_today():
    """Same tuples for today's matches from Kooora (every competition, with the country in the section header)."""
    h = page('https://www.kooora.com/كرة-القدم/مباريات-اليوم')
    if not h:
        return None
    out = []
    for sec in h.split('fco-competition-section__header-name">')[1:]:
        comp = text(sec.split('<', 1)[0])
        area = re.search(r'header-area">([^<]*)', sec)
        comp_full = comp + ' ' + (text(area.group(1)) if area else '')
        for blk in sec.split('class="fco-match-list-item"')[1:]:
            teams = [text(t) for t in re.findall(r'<div class="fco-team-name fco-full-name">(.*?)</div>', blk, re.S)][:2]
            crests = [c.replace('&amp;', '&') for c in re.findall(r'src="(https://cdn\.sportfeeds\.io/sdl/images/team/crest/[^"]+)"', blk)][:2]
            t = re.search(r'dateTime="([0-9T:.\-]+Z)"', blk)
            chans = [text(c) for c in re.findall(r'<div class="fco-tv-channel__name">(.*?)</div>', blk, re.S)]
            ch = next((c for c in chans if 'bein' in c.lower() and 'connect' not in c.lower()), chans[0] if chans else '')
            if len(teams) != 2 or not t:
                continue
            kick = datetime.fromisoformat(t.group(1).replace('Z', '+00:00')[:19] + '+00:00')
            out.append((comp, comp_full, teams[0], teams[1], kick, ch, *(crests + ['', ''])[:2]))
    return out


def add_missing(events, team_key, now, end):
    """Adds the tracked teams' games that are not in `events` yet. Returns how many were added."""
    have = []
    for e in events:
        try:
            k = datetime.fromisoformat(e['utc'].replace('Z', '+00:00'))
        except Exception:
            continue
        have.append((k, {team_key(e['home']['en']), team_key(e['away']['en'])} - {None}))
    rows = []
    day = now.astimezone(CAIRO).date()
    for i in range((end - now).days + 1):
        got = filgoal_day((day + timedelta(days=i)).strftime('%Y-%m-%d'))
        rows += got or []
    rows += kooora_today() or []
    added = 0
    for comp, ctx, home, away, kick, ch, hc, ac in rows:
        if kick < now - timedelta(hours=2) or kick > end:
            continue
        keys = [tracked(home, ctx), tracked(away, ctx)]
        if not any(keys):
            continue
        if any(abs((kick - k).total_seconds()) < 4 * 3600 and ((set(keys) - {None}) & ks) for k, ks in have):
            continue
        comp_ar = re.sub(r'\s+', ' ', comp).strip()
        for name, crest in ((home, hc), (away, ac)):
            if crest:
                CRESTS.append((name, crest))
        ev_id = 'x' + hashlib.md5(f'{home}|{away}|{kick:%Y-%m-%d}'.encode()).hexdigest()[:10]
        c = clean(ch) if ch else None
        if c:
            c['exact'] = True
        events.append({
            'id': ev_id, 'utc': kick.strftime('%Y-%m-%dT%H:%M:%SZ'), 'live': False, 'code': 'xtra', 'espn': None,
            'league': {'en': league_en(comp_ar), 'ar': comp_ar},
            'home': {'en': EN_NAME.get(keys[0], home), 'ar': home, 'logo': hc},
            'away': {'en': EN_NAME.get(keys[1], away), 'ar': away, 'logo': ac},
            'channel': c,
            'big': sum(1 for k in keys if k),
            'top': all(keys) or 'egypt' in keys or 'lebanon' in keys,
        })
        have.append((kick, set(keys) - {None}))
        added += 1
    print(f'  {added} more match(es) of Egyptian / Lebanese teams from FilGoal / Kooora ({len(rows)} listed)')
    return added
