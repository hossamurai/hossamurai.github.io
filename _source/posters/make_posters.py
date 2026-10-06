"""Makes the made-up movie/series posters used in the faint poster wall (assets/img/posters/).
All titles and artwork are invented for Hossam TV — no real films, studios or actors.
Run:  python make_posters.py   (from this folder)"""
import os, random
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'img', 'posters')
FONT = "Impact, 'Arial Black', 'Helvetica Neue', Arial, sans-serif"
SANS = "'Helvetica Neue', Arial, sans-serif"

def credits(y, col):
    r = random.Random(y)
    bars = ''.join(f'<rect x="{40 + i * 33}" y="{y}" width="{r.randint(16, 28)}" height="3" rx="1.5" fill="{col}" opacity=".55"/>' for i in range(10))
    bars += ''.join(f'<rect x="{60 + i * 30}" y="{y + 9}" width="{r.randint(12, 24)}" height="3" rx="1.5" fill="{col}" opacity=".4"/>' for i in range(10))
    return bars

def badge(text, fill, ink):
    return (f'<rect x="24" y="24" rx="6" width="{len(text) * 11 + 22}" height="26" fill="{fill}"/>'
            f'<text x="35" y="42" font-family="{SANS}" font-size="13" font-weight="700" letter-spacing="1.5" fill="{ink}">{text}</text>')

def poster(name, bg1, bg2, scene, title, tag, kicker, title_col='#fff', size=58, ty=470, badge_txt=None, badge_fill='#e3101b', badge_ink='#fff'):
    lines = title.split('|')
    t = ''.join(f'<text x="200" y="{ty + i * (size * .92)}" text-anchor="middle" font-family="{FONT}" font-size="{size}" letter-spacing="2" fill="{title_col}">{ln}</text>' for i, ln in enumerate(lines))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" width="400" height="600">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset=".45" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>
<rect width="400" height="600" fill="url(#bg)"/>{scene}<rect width="400" height="600" fill="url(#fade)"/>
<text x="200" y="{ty - size - 8}" text-anchor="middle" font-family="{SANS}" font-size="12" letter-spacing="4" fill="#fff" opacity=".85">{kicker}</text>{t}
<text x="200" y="{ty + (len(lines) - 1) * size * .92 + 30}" text-anchor="middle" font-family="{SANS}" font-size="13" letter-spacing="1" fill="#fff" opacity=".8">{tag}</text>
{credits(566, '#fff')}{badge(badge_txt, badge_fill, badge_ink) if badge_txt else ''}</svg>'''
    open(os.path.join(OUT, name + '.svg'), 'w').write(svg)

def skyline(col, base=420, seed=1):
    r = random.Random(seed); x = 0; out = ''
    while x < 400:
        w = r.randint(22, 48); h = r.randint(60, 210)
        out += f'<rect x="{x}" y="{base - h}" width="{w}" height="{h + 200}" fill="{col}"/>'
        for wy in range(base - h + 10, base - 10, 16):
            for wx in range(x + 5, x + w - 6, 10):
                if r.random() < .35: out += f'<rect x="{wx}" y="{wy}" width="4" height="6" fill="#ffd27a" opacity=".7"/>'
        x += w + r.randint(2, 6)
    return out

def figure(x, y, s, col):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="{col}"><circle cx="0" cy="-118" r="16"/>'
            f'<path d="M-24-98h48l10 70-14 4-6-40-4 104h-14l-2-58-2 58h-14l-4-104-6 40-14-4z"/></g>')

os.makedirs(OUT, exist_ok=True)
poster('p01', '#06121f', '#0e4d64', skyline('#03101b', 430, 3) + '<circle cx="300" cy="120" r="46" fill="url(#glow)" opacity=".5"/>' + figure(200, 470, 1.25, '#020a12'),
       'NEON|TIDE', 'THE CITY NEVER SLEEPS. NEITHER DOES SHE.', 'A THRILLER', size=74, ty=420, badge_txt='NEW')
poster('p02', '#05030f', '#2a0b45', '<circle cx="200" cy="230" r="120" fill="#7a3cff" opacity=".35"/><circle cx="200" cy="230" r="86" fill="#b04cff" opacity=".55"/>'
       '<ellipse cx="200" cy="230" rx="170" ry="26" fill="none" stroke="#e2c4ff" stroke-width="3" opacity=".6"/>'
       + ''.join(f'<circle cx="{random.Random(i).randint(0,400)}" cy="{random.Random(i+50).randint(0,600)}" r="{random.Random(i+9).choice([1,1,1.5,2])}" fill="#fff" opacity=".8"/>' for i in range(70)),
       'ORBIT|NINE', 'NINE CREW. ONE WAY HOME.', 'A SCI-FI EPIC', size=70, ty=440, badge_txt='4K')
poster('p03', '#f0a04b', '#5a1e0a', '<circle cx="270" cy="170" r="70" fill="#ffe1a3" opacity=".9"/>'
       '<path d="M0 360 Q120 300 220 350 T400 330 V600 H0z" fill="#b5541c"/><path d="M0 420 Q140 360 260 410 T400 400 V600 H0z" fill="#7a2c0c"/>'
       + figure(130, 420, .6, '#3a1205') + figure(160, 424, .55, '#3a1205'),
       'THE RED|DUNE', 'THE DESERT KEEPS ITS SECRETS.', 'AN ADVENTURE', size=66, ty=470)
poster('p04', '#06210f', '#0b3b1c', '<path d="M0 380 H400 V600 H0z" fill="#145a2a"/>' + ''.join(f'<path d="M{x} 0 L{x-60} 380 L{x+60} 380z" fill="#fff" opacity=".07"/>' for x in (60, 340))
       + '<circle cx="60" cy="40" r="22" fill="#fff" opacity=".9"/><circle cx="340" cy="40" r="22" fill="#fff" opacity=".9"/>'
       '<circle cx="200" cy="330" r="34" fill="#fff"/><path d="M200 300l12 9-5 14h-14l-5-14z M178 332l10-6 5 13-8 9z M222 332l-10-6-5 13 8 9z" fill="#111"/>',
       'KICKOFF|NIGHTS', 'EVERY MATCH. EVERY HEARTBEAT.', 'A FOOTBALL SERIES', size=62, ty=470, badge_txt='NEW SEASON', badge_fill='#fff', badge_ink='#111')
poster('p05', '#1b0f2e', '#7a3b12', '<circle cx="200" cy="150" r="54" fill="#ffd27a" opacity=".85"/>'
       '<path d="M40 420 V250 Q40 190 100 190 Q160 190 160 250 V420z M240 420 V230 Q240 160 300 160 Q360 160 360 230 V420z" fill="#2a1408"/>'
       + ''.join(f'<path d="M{x} 240 l10 18h-20z" fill="#ffb347"/><circle cx="{x}" cy="262" r="7" fill="#ffcf6b" opacity=".9"/>' for x in (100, 300, 200)),
       'MIDNIGHT|SUQ', 'EVERY STALL HAS A STORY.', 'A DRAMA SERIES', size=66, ty=470, badge_txt='NEW SERIES')
poster('p06', '#8fd3ff', '#e8f6ff', '<circle cx="320" cy="90" r="40" fill="#fff6c2"/>'
       '<path d="M0 470 Q100 420 200 460 T400 450 V600 H0z" fill="#7bc96f"/>'
       + ''.join(f'<g transform="translate({x},{y}) rotate({a})"><path d="M0 -40 L28 0 L0 40 L-28 0z" fill="{c}"/><path d="M0 40 q10 40 -10 80" stroke="#555" fill="none" stroke-width="1.5"/></g>' for x, y, a, c in ((110, 180, -12, '#ff6b6b'), (250, 140, 10, '#ffd93d'), (190, 260, -4, '#6bcBff'))),
       'PAPER|KITES', 'A BIG ADVENTURE FOR LITTLE DREAMERS.', 'AN ANIMATED FILM', title_col='#1d3557', size=68, ty=430)
poster('p07', '#0b1020', '#3a4a5c', '<path d="M0 330 L80 250 L150 300 L240 200 L320 280 L400 230 V600 H0z" fill="#1c2633"/><path d="M0 380 L120 320 L220 360 L320 300 L400 340 V600 H0z" fill="#0e151f"/>'
       + ''.join(f'<line x1="{random.Random(i).randint(0,400)}" y1="{random.Random(i+7).randint(0,600)}" x2="{random.Random(i).randint(0,400)-6}" y2="{random.Random(i+7).randint(0,600)+18}" stroke="#cfe3ff" stroke-width="1.2" opacity=".5"/>' for i in range(90))
       + figure(200, 470, 1.1, '#05080e'),
       'COLD|FRONT', 'HE HAS ONE NIGHT TO GET OUT.', 'AN ACTION FILM', size=76, ty=440, badge_txt='4K')
poster('p08', '#2b0d0d', '#c75b2a', '<rect x="0" y="300" width="400" height="300" fill="#3a1208"/>'
       + ''.join(f'<g transform="translate({x},{y})"><line x1="0" y1="-60" x2="0" y2="0" stroke="#000" stroke-width="1"/><rect x="-14" y="0" width="28" height="38" rx="10" fill="#ffb347"/><rect x="-14" y="0" width="28" height="38" rx="10" fill="url(#glow)" opacity=".5"/></g>' for x, y in ((70, 120), (150, 90), (240, 130), (330, 100), (110, 200), (290, 210)))
       + '<path d="M60 600 V330 L200 250 L340 330 V600z" fill="#1f0904"/><rect x="180" y="420" width="40" height="70" rx="20" fill="#ffcf6b" opacity=".85"/>',
       'HOUSE OF|LANTERNS', 'ONE FAMILY. THREE GENERATIONS.', 'A DRAMA SERIES', size=52, ty=500, badge_txt='NEW EPISODES')
poster('p09', '#1a1440', '#ff7aa2', '<circle cx="200" cy="250" r="130" fill="#ffd1dc" opacity=".25"/>'
       + ''.join(f'<path d="M{x} {y} l3 9 9 0 -7 6 3 9 -8 -5 -8 5 3 -9 -7 -6 9 0z" fill="#fff" opacity=".8"/>' for x, y in ((60, 80), (330, 60), (300, 180), (90, 210), (200, 40)))
       + figure(170, 420, .95, '#2a1030') + figure(230, 420, .9, '#2a1030'),
       'STARFALL', 'SOME LOVE STORIES ARE WRITTEN IN THE SKY.', 'A ROMANCE', size=70, ty=480)
poster('p10', '#000000', '#122018', '<circle cx="200" cy="200" r="150" fill="#1f3b2c" opacity=".6"/>'
       '<rect x="120" y="120" width="160" height="110" rx="8" fill="#0a120d" stroke="#3fa36b" stroke-width="3"/>'
       + ''.join(f'<rect x="130" y="{130 + i * 8}" width="140" height="3" fill="#3fa36b" opacity="{.15 + (i % 3) * .2}"/>' for i in range(12))
       + '<path d="M150 300 Q200 260 250 300" stroke="#3fa36b" stroke-width="2" fill="none" opacity=".6"/>',
       'GHOST|SIGNAL', 'THE STATIC IS CALLING.', 'A MYSTERY', title_col='#d8ffe6', size=70, ty=440)
poster('p11', '#0d0d0d', '#e3101b', '<path d="M0 360 H400 V600 H0z" fill="#1a1a1a"/>'
       + ''.join(f'<rect x="{x}" y="420" width="40" height="6" fill="#fff" opacity=".7"/>' for x in range(-20, 400, 80))
       + '<path d="M90 380 Q120 330 200 330 Q280 330 310 380 L320 400 H80z" fill="#111"/><circle cx="130" cy="400" r="18" fill="#000"/><circle cx="270" cy="400" r="18" fill="#000"/>'
       '<path d="M40 380 L0 370 M40 395 L0 400" stroke="#ff8a00" stroke-width="3" opacity=".8"/>',
       'DRIFT|KINGS', 'THE STREETS HAVE RULES.', 'AN ACTION FILM', size=76, ty=480, badge_txt='TOP 10', badge_fill='#fff', badge_ink='#e3101b')
poster('p12', '#0f2a4a', '#5aa3e6', '<path d="M0 420 H400 V600 H0z" fill="#1d6b3a"/><path d="M200 420 V600" stroke="#fff" stroke-width="2" opacity=".5"/>'
       '<circle cx="200" cy="470" r="40" stroke="#fff" stroke-width="2" fill="none" opacity=".5"/>' + figure(200, 420, 1.2, '#0a1a2c')
       + '<rect x="40" y="70" width="70" height="40" rx="4" fill="#0a1a2c"/><text x="75" y="98" text-anchor="middle" font-family="' + SANS + '" font-size="20" font-weight="700" fill="#ffcf3a">2 - 1</text>',
       'SECOND|HALF', 'IT’S NOT OVER UNTIL IT’S OVER.', 'A SPORTS DRAMA', size=72, ty=300, badge_txt='NEW')
print('made', len([f for f in os.listdir(OUT) if f.endswith('.svg')]), 'posters in', os.path.abspath(OUT))
