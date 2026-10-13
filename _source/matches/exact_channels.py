"""The exact TV channel of each match ("beIN Sports 2", not just "beIN Sports") — used by fetch_matches.py.

Sources, in order (a match keeps the league's usual channel when none of them lists it):
  1. FilGoal  — filgoal.com/matches/?date=YYYY-MM-DD: every match of that day with its channel, in Arabic.
  2. Kooora   — kooora.com "today's matches": today's games with their channels (backup for today).
  3. The exact channel found on an earlier run (kept if both sites are down).
Matches are paired by the two Arabic team names (spelling differences are ignored) and the day in Cairo time.
"""
import html, re, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    CAIRO = ZoneInfo('Africa/Cairo')
except Exception:                                   # no tz database: Egypt is UTC+2 / +3 in summer
    CAIRO = timezone(timedelta(hours=3))

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
           'Accept': 'text/html,*/*;q=0.8', 'Accept-Language': 'ar,en;q=0.8'}
AR = {'ON Time Sports': 'أون تايم سبورت', 'ON Sport': 'أون سبورت', 'Thmanyah': 'ثمانية', 'SSC': 'SSC', 'Abu Dhabi Sports': 'أبوظبي الرياضية',
      'Dubai Sports': 'دبي الرياضية', 'AD Sports': 'أبوظبي الرياضية', 'Alkass': 'الكاس', 'Shahid': 'شاهد'}


def page(url):
    try:
        req = urllib.request.Request(urllib.parse.quote(url, safe=':/?=&%'), headers=HEADERS)
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read().decode('utf-8', 'ignore')
    except Exception as e:
        print('  channel source failed', url, e, file=sys.stderr)
        return None


def text(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x or ''))).strip()


def key(name):
    """Arabic team name for matching: one alef/yaa/taa form, no diacritics, no 'نادي'/'FC' and the like."""
    x = re.sub(r'[ً-ٰٟـ]', '', str(name or '').lower())
    x = re.sub('[أإآٱ]', 'ا', x).replace('ى', 'ي').replace('ة', 'ه').replace('ؤ', 'و').replace('ئ', 'ي')
    x = re.sub(r'\b(نادي|فريق|fc|sc|cf)\b', ' ', x)
    return re.sub(r'[^a-z0-9؀-ۿ ]+', ' ', x).split()


def same_team(a, b):
    ka, kb = key(a), key(b)
    if not ka or not kb:
        return False
    ja, jb = ''.join(ka), ''.join(kb)
    if ja == jb or (min(len(ja), len(jb)) >= 4 and (ja in jb or jb in ja)):
        return True
    # same consonants ("فايكنج" / "فايكينغ"): long vowels dropped, غ/ق/ج as one sound
    sk = lambda w: re.sub('[غق]', 'ج', re.sub('[اوي]', '', w))
    if len(sk(ja)) >= 3 and sk(ja) == sk(jb):
        return True
    # one shared distinctive word ("مانشستر يونايتد" / "مان يونايتد" -> "يونايتد"); "مانشستر" alone is not enough
    common = {w for w in ka if len(w) >= 4} & {w for w in kb if len(w) >= 4} - {'مانشستر', 'ريال', 'اتلتيكو', 'بوروسيا', 'الاهلي', 'الاتحاد', 'سبورتنغ', 'انتر'}
    return bool(common)


def clean(ch):
    """'beIN SPORTS 7 HD' / 'beIN Sports Mena 4' -> {'en': 'beIN Sports 7', 'ar': 'بي إن سبورت 7'}."""
    ch = re.sub(r'\s+', ' ', ch or '').strip()
    m = re.match(r'(?i)bein\s*sports?\s*(?:mena\s*)?(xtra|max|eng(?:lish)?|premium|hd)?\s*(\d+)?\s*(?:hd)?$', ch)
    if m:
        kind = (m.group(1) or '').lower()
        num = m.group(2) or ''
        kind = {'xtra': 'Xtra ', 'max': 'Max ', 'eng': 'English ', 'english': 'English ', 'premium': 'Premium '}.get(kind, '')
        en = ('beIN Sports ' + kind + num).strip()
        ar = ('بي إن سبورت ' + {'Xtra ': 'إكسترا ', 'Max ': 'ماكس ', 'English ': 'الإنجليزية ', 'Premium ': 'بريميوم '}.get(kind, '') + num).strip()
        return {'en': en, 'ar': ar}
    if not ch:
        return None
    for k, v in AR.items():
        if ch.lower().startswith(k.lower()):
            return {'en': ch, 'ar': v + ch[len(k):]}
    return {'en': ch, 'ar': ch}


CRESTS = []   # (Arabic team name, badge URL) seen on FilGoal / Kooora — used by fetch_matches.fill_logos for teams with no badge


def crest_for(ar_name):
    return next((url for n, url in CRESTS if same_team(ar_name, n)), '')


def filgoal(day):
    """[(home, away, channel)] for one day (YYYY-MM-DD) from FilGoal."""
    h = page(f'https://www.filgoal.com/matches/?date={day}')
    if not h:
        return None
    out = []
    for blk in h.split('<div class="cin_cntnr"')[1:]:
        teams = [text(t) for t in re.findall(r'<strong>(.*?)</strong>', blk, re.S)][:2]
        for src, name in re.findall(r'data-src="(//semedia\.filgoal\.com/Photos/Team/[^"]+)"\s*>\s*<strong>(.*?)</strong>', blk, re.S):
            CRESTS.append((text(name), 'https:' + src))
        ch = re.search(r'#fb_screen"\s*>\s*</use>\s*</svg>(.*?)</span>', blk, re.S)
        if len(teams) == 2 and ch and text(ch.group(1)):
            out.append((teams[0], teams[1], text(ch.group(1))))
    return out


def kooora():
    """[(home, away, channel)] for today's matches from Kooora (a beIN channel is preferred when several are listed)."""
    h = page('https://www.kooora.com/كرة-القدم/مباريات-اليوم')
    if not h:
        return None
    out = []
    for blk in h.split('class="fco-match-list-item"')[1:]:
        teams = [text(t) for t in re.findall(r'<div class="fco-team-name fco-full-name">(.*?)</div>', blk, re.S)][:2]
        for name, src in re.findall(r'alt="([^"]+?) badge"[^>]*?src="(https://cdn\.sportfeeds\.io/[^"]+)"', blk):
            CRESTS.append((html.unescape(name), html.unescape(src)))
        chans = [text(c) for c in re.findall(r'<div class="fco-tv-channel__name">(.*?)</div>', blk, re.S)]
        ch = next((c for c in chans if 'bein' in c.lower() and 'connect' not in c.lower()), chans[0] if chans else '')
        if len(teams) == 2 and ch:
            out.append((teams[0], teams[1], ch))
    return out


def apply(events, old_events):
    """Sets e['channel'] = {'en', 'ar', 'exact': True} on every match a source lists."""
    days = sorted({datetime.fromisoformat(e['utc'].replace('Z', '+00:00')).astimezone(CAIRO).strftime('%Y-%m-%d') for e in events})
    listed = {d: filgoal(d) or [] for d in days}
    today = datetime.now(CAIRO).strftime('%Y-%m-%d')
    ko = kooora() or []
    before = {e['id']: e.get('channel') for e in old_events or [] if (e.get('channel') or {}).get('exact')}
    found = 0
    for e in events:
        day = datetime.fromisoformat(e['utc'].replace('Z', '+00:00')).astimezone(CAIRO).strftime('%Y-%m-%d')
        cands = listed.get(day, []) + (ko if day == today else [])
        hit = None
        for h, a, ch in cands:
            if (same_team(e['home']['ar'], h) and same_team(e['away']['ar'], a)) or (same_team(e['home']['ar'], a) and same_team(e['away']['ar'], h)):
                hit = clean(ch)
                break
        if hit:
            hit['exact'] = True
            e['channel'] = hit
            found += 1
        elif before.get(e['id']):
            e['channel'] = before[e['id']]
            found += 1
    print(f'  exact channel for {found} of {len(events)} matches')
