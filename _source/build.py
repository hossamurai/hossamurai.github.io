# -*- coding: utf-8 -*-
"""
Hossam TV static site generator.
Usage (from this _source folder):   python build.py
Writes the finished site into the parent folder (the root of your GitHub repo):
  index.html, 404.html, sitemap.xml, robots.txt, assets/, en/, ar/
Your images (logo.png, basic.png, premium.png, X.png, marvel.png) stay in the repo root.
"""
import os, shutil, posixpath, urllib.parse
from content import *
from pages import PAGE_BUILDERS, DEVICE_PAGES, icon, wa, ARIA_CUR

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
LANGS = ['en', 'ar']


class Ctx:
    def __init__(self, lang, path, key, section):
        self.lang, self.path, self.key, self.section = lang, path, key, section
        self.ar = lang == 'ar'
        depth = path.count('/') + 1          # en/x.html -> 1, en/setup/x.html -> 2
        self.root = '../' * depth            # relative path to repo root

    def t(self, x):
        if x is None:
            return ''
        return x if isinstance(x, str) else x[self.lang]

    def href(self, target):
        """target is a path inside the language folder, e.g. 'plans.html' or 'setup/firestick.html#x'."""
        frag = ''
        if '#' in target:
            target, frag = target.split('#', 1)
            frag = '#' + frag
        full = self.lang + '/' + target
        rel = posixpath.relpath(full, posixpath.dirname(self.lang + '/' + self.path))
        return rel + frag

    def other_lang_href(self):
        other = 'ar' if self.lang == 'en' else 'en'
        return posixpath.relpath(other + '/' + self.path, posixpath.dirname(self.lang + '/' + self.path))

    def wa_msg(self, kind, plan=None, region=None):
        a = self.ar
        if kind == 'trial' and plan:
            return (f'مرحباً، أريد تجربة مجانية لباقة {plan}' + (f' ({region})' if region else '') + '.') if a else \
                   (f"Hi Hossam TV, I'd like a free trial of the {plan} plan" + (f' ({region})' if region else '') + '.')
        if kind == 'sub' and plan:
            return (f'مرحباً، أريد الاشتراك في باقة {plan}' + (f' ({region})' if region else '') + '.') if a else \
                   (f"Hi Hossam TV, I'd like to subscribe to the {plan} plan" + (f' ({region})' if region else '') + '.')
        if kind == 'channels' and plan:
            return f'مرحباً، أريد قائمة القنوات الكاملة لباقة {plan}.' if a else \
                   f"Hi Hossam TV, could you send me the full channel list for the {plan} plan?"
        msgs = {
            'trial': ('مرحباً، أريد تجربة مجانية.', "Hi Hossam TV, I'd like a free trial."),
            'sub': ('مرحباً، أريد الاشتراك في Hossam TV.', "Hi Hossam TV, I'd like to subscribe."),
            'help': ('مرحباً، أحتاج مساعدة في اشتراكي.', 'Hi Hossam TV, I need help with my subscription.'),
            'pay': ('مرحباً، أريد بيانات الدفع.', 'Hi Hossam TV, could you send me the payment details?'),
            'tv': ('مرحباً، هذه بيانات شاشتي (Device ID و Device Key) واسم المستخدم الخاص بي:', "Hi Hossam TV, here are my TV's Device ID and Device Key, and my username:"),
        }
        return msgs[kind][0 if a else 1]

    def wa(self, kind, **kw):
        return wa(self.wa_msg(kind, **kw))


# ----------------------------------------------------------------------------
# icon sprite
# ----------------------------------------------------------------------------
SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="i-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20l1.3-3.9A8 8 0 1 1 8.4 19.3L4 20Z"/><path d="M9 10.5h.01M12 10.5h.01M15 10.5h.01"/></symbol>
<symbol id="i-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
<symbol id="i-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.2 4.2L19 7"/></symbol>
<symbol id="i-x" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></symbol>
<symbol id="i-plus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></symbol>
<symbol id="i-menu" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></symbol>
<symbol id="i-search" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></symbol>
<symbol id="i-copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></symbol>
<symbol id="i-globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3Z"/></symbol>
<symbol id="i-clock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></symbol>
<symbol id="i-4k" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M7 9v3.5h3M9.5 9v6M14 9v6M17.5 9 14.5 12l3 3"/></symbol>
<symbol id="i-devices" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="14" height="10" rx="1.5"/><path d="M6 18h6M9 14v4"/><rect x="17" y="8" width="5" height="12" rx="1.2"/></symbol>
<symbol id="i-bolt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/></symbol>
<symbol id="i-ball" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="m12 7.5 4 2.9-1.5 4.7h-5L8 10.4l4-2.9ZM12 3v4.5M16 10.4l4.5-1.2M14.5 15.1l2.6 4M9.5 15.1l-2.6 4M8 10.4 3.5 9.2"/></symbol>
<symbol id="i-film" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/></symbol>
<symbol id="i-series" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="6" width="18" height="13" rx="2"/><path d="M8 2.5 12 6l4-3.5M10 10.5v5l4-2.5-4-2.5Z"/></symbol>
<symbol id="i-kids" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8.5 14.5c1.8 2 5.2 2 7 0M9 9.5h.01M15 9.5h.01"/></symbol>
<symbol id="i-shield" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 3 4.5 6v6c0 4.5 3.2 7.8 7.5 9 4.3-1.2 7.5-4.5 7.5-9V6L12 3Z"/><path d="m9 12 2 2 4-4"/></symbol>
<symbol id="i-key" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="4"/><path d="M10.3 12.7 20 3M17 6l2.5 2.5M14.5 8.5 17 11"/></symbol>
<symbol id="i-info" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></symbol>
<symbol id="i-warn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4M12 17h.01"/></symbol>
<symbol id="i-card" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M2.5 10h19M6 15h4"/></symbol>
<symbol id="i-receipt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2V3Z"/><path d="M9 8h6M9 12h6"/></symbol>
<symbol id="i-download" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 10l5 5 5-5M4 20h16"/></symbol>
<symbol id="i-refresh" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 1 0-2.3 5.7M20 5v6h-6"/></symbol>
<symbol id="i-wifi" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2.5 9a14 14 0 0 1 19 0M5.5 12.5a9.5 9.5 0 0 1 13 0M8.5 16a5 5 0 0 1 7 0M12 19.5h.01"/></symbol>
<symbol id="i-tv" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="12" rx="2"/><path d="M8 21h8M12 17v4"/></symbol>
<symbol id="i-androidtv" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="12" rx="2"/><path d="M8 21h8M12 17v4M7.5 9.5l2 2M16.5 9.5l-2 2"/></symbol>
<symbol id="i-stick" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="2.5" width="8" height="14" rx="2"/><path d="M10 16.5v3a2 2 0 0 0 4 0v-3M12 6.5h.01"/></symbol>
<symbol id="i-phone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/></symbol>
<symbol id="i-apple" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8c-1.4-1-3-1-4.2-.2C6 8.9 5.6 11.4 6.6 14c.8 2 1.9 3.5 3.2 4 .8.3 1.4-.2 2.2-.2s1.4.5 2.2.2c1.3-.5 2.4-2 3.2-4 1-2.6.6-5.1-1.2-6.2-1.2-.8-2.8-.8-4.2.2Z"/><path d="M12 8c0-1.7 1.2-3 3-3"/></symbol>
<symbol id="i-laptop" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="10" rx="1.5"/><path d="M2 19h20l-1.5-2H3.5L2 19Z"/></symbol>
<symbol id="i-box" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="8" width="18" height="8" rx="2"/><circle cx="17" cy="12" r="1.1" fill="currentColor"/><path d="M6.5 12h5"/></symbol>
</defs></svg>'''

CHATBASE = '''<script>
(function(){if(!window.chatbase||window.chatbase("getState")!=="initialized"){window.chatbase=function(){if(!window.chatbase.q){window.chatbase.q=[]}window.chatbase.q.push(arguments)};window.chatbase=new Proxy(window.chatbase,{get:function(target,prop){if(prop==="q"){return target.q}return function(){var a=Array.prototype.slice.call(arguments);return target.apply(null,[prop].concat(a))}}})}var onLoad=function(){var s=document.createElement("script");s.src="https://www.chatbase.co/embed.min.js";s.id="UR4AT8qVyiMZfTLECiywM";s.domain="www.chatbase.co";document.body.appendChild(s)};if(document.readyState==="complete"){onLoad()}else{window.addEventListener("load",onLoad)}})();
</script>'''

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800'
         '&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=IBM+Plex+Sans+Arabic:wght@400;500;700&display=swap" rel="stylesheet">')

NAV = [
    ('home', 'index.html', L('Home', 'الرئيسية')),
    ('plans', 'plans.html', L('Plans', 'الباقات')),
    ('channels', 'channels.html', L('Channels', 'القنوات')),
    ('setup', 'setup/index.html', L('Setup', 'التثبيت')),
    ('help', 'help.html', L('Help', 'المساعدة')),
    ('about', 'about.html', L('About', 'من نحن')),
]


def canonical(lang, path):
    p = path[:-len('index.html')] if path.endswith('index.html') else path
    return f'{BASE_URL}/{lang}/{p}'


def header(c):
    links = ''.join(
        f'<a href="{c.href(p)}"{ARIA_CUR if c.section == k else ""}>{c.t(lbl)}</a>' for k, p, lbl in NAV)
    other = 'en' if c.ar else 'ar'
    return f'''<header class="nav">
  <div class="bars" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
  <div class="wrap nav-in">
    <a class="brand" href="{c.href('index.html')}" aria-label="{SITE_NAME} — {c.t(L('home', 'الرئيسية'))}">
      <img src="{c.root}logo.png" alt="" width="34" height="34" onerror="this.style.display='none';this.nextElementSibling.style.display='grid'">
      <span class="brand-fallback" aria-hidden="true">H</span><span>{SITE_NAME}</span>
    </a>
    <nav class="nav-links" id="navLinks" aria-label="{c.t(L('Main', 'القائمة الرئيسية'))}">{links}</nav>
    <div class="nav-right">
      <a class="lang" href="{c.other_lang_href()}" hreflang="{other}" lang="{other}" data-setlang="{other}">{icon('globe')}{'English' if c.ar else 'العربية'}</a>
      <a class="btn btn-wa btn-sm" href="{c.wa('trial')}" target="_blank" rel="noopener">{icon('chat')}<span class="lbl">{c.t(L('Free trial', 'تجربة مجانية'))}</span></a>
      <button class="menu-btn" id="menuBtn" type="button" aria-expanded="false" aria-controls="navLinks" aria-label="{c.t(L('Menu', 'القائمة'))}">{icon('menu', 'i-open')}{icon('x', 'i-close')}</button>
    </div>
  </div>
</header>'''


def footer(c):
    t = c.t
    explore = ''.join(f'<li><a href="{c.href(p)}">{t(lbl)}</a></li>' for k, p, lbl in NAV)
    devs = ''.join(f'<li><a href="{c.href("setup/" + d["slug"] + ".html")}">{t(d["name"])}</a></li>' for d in DEVICES if not d.get('off'))
    pol = [('policies.html#terms', L('Terms of service', 'شروط الخدمة')),
           ('policies.html#refund', L('Refund policy', 'سياسة الاسترجاع')),
           ('policies.html#privacy', L('Privacy policy', 'سياسة الخصوصية'))]
    pols = ''.join(f'<li><a href="{c.href(p)}">{t(lbl)}</a></li>' for p, lbl in pol)
    return f'''<footer class="site">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <span class="foot-brand">{SITE_NAME}</span>
        <p>{t(L('Live sports, movies and series on any screen — with personal support on WhatsApp.', 'مباريات وأفلام ومسلسلات على أي شاشة — مع دعم شخصي عبر واتساب.'))}</p>
        <p>{t(L('WhatsApp (chat only, no calls):', 'واتساب (رسائل فقط، بدون مكالمات):'))}<br><a class="foot-wa" href="{wa()}" target="_blank" rel="noopener">{WHATSAPP_DISPLAY}</a></p>
      </div>
      <div><h3>{t(L('Explore', 'تصفح'))}</h3><ul>{explore}</ul></div>
      <div><h3>{t(L('Setup guides', 'أدلة التثبيت'))}</h3><ul>{devs}</ul></div>
      <div><h3>{t(L('Policies', 'السياسات'))}</h3><ul>{pols}</ul>
        <p style="margin-top:16px">{t(L('Save our number — updates and maintenance notices are posted on our WhatsApp Status.', 'احفظ رقمنا — التحديثات وأخبار الصيانة تُنشر على حالة الواتساب.'))}</p></div>
    </div>
    <div class="foot-bottom">
      <span>&copy; <span id="yr">2026</span> {SITE_NAME}</span>
      <a href="{c.other_lang_href()}" data-setlang="{'en' if c.ar else 'ar'}" lang="{'en' if c.ar else 'ar'}">{'English' if c.ar else 'العربية'}</a>
    </div>
  </div>
</footer>'''


def layout(c, title, desc, body):
    full_title = title if SITE_NAME in title else f'{title} — {SITE_NAME}'
    alt = ''.join(f'<link rel="alternate" hreflang="{l}" href="{canonical(l, c.path)}">' for l in LANGS)
    alt += f'<link rel="alternate" hreflang="x-default" href="{BASE_URL}/">'
    return f'''<!DOCTYPE html>
<html lang="{c.lang}" dir="{'rtl' if c.ar else 'ltr'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#fbf8f3">
<title>{full_title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical(c.lang, c.path)}">
{alt}
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{BASE_URL}/logo.png">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical(c.lang, c.path)}">
<meta property="og:locale" content="{'ar_EG' if c.ar else 'en_US'}">
<link rel="icon" type="image/png" href="{c.root}logo.png">
<link rel="apple-touch-icon" href="{c.root}logo.png">
{FONTS}
<link rel="stylesheet" href="{c.root}assets/style.css">
</head>
<body>
{SPRITE}
<a class="skip" href="#main">{c.t(L('Skip to content', 'انتقل إلى المحتوى'))}</a>
{header(c)}
<main id="main">
{body}
</main>
{footer(c)}
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script src="{c.root}assets/site.js" defer></script>
{CHATBASE}
</body>
</html>
'''


# ----------------------------------------------------------------------------
# root chooser, 404, sitemap, robots
# ----------------------------------------------------------------------------
def root_index():
    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{SITE_NAME} — Live Sports, Movies &amp; Series | مباريات وأفلام ومسلسلات</title>
<meta name="description" content="Live sports, movies and series on any screen, up to 4K. Free trial on WhatsApp. | مباريات وأفلام ومسلسلات على أي شاشة بجودة حتى 4K. تجربة مجانية عبر واتساب.">
<link rel="alternate" hreflang="en" href="{BASE_URL}/en/">
<link rel="alternate" hreflang="ar" href="{BASE_URL}/ar/">
<link rel="alternate" hreflang="x-default" href="{BASE_URL}/">
<meta property="og:image" content="{BASE_URL}/logo.png">
<link rel="icon" type="image/png" href="logo.png">
<script>
(function(){{
  var l = null;
  try {{ l = localStorage.getItem('htv-lang'); }} catch(e) {{}}
  if (l !== 'ar' && l !== 'en') {{
    var langs = navigator.languages || [navigator.language || ''];
    l = 'en';
    for (var i = 0; i < langs.length; i++) {{ if ((langs[i] || '').toLowerCase().indexOf('ar') === 0) {{ l = 'ar'; break; }} }}
  }}
  location.replace(l + '/index.html' + location.hash);
}})();
</script>
{FONTS}
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="center-page"><div>
  <img src="logo.png" alt="" width="64" height="64" style="margin:0 auto 12px;border-radius:16px">
  <h1>{SITE_NAME}</h1>
  <div class="row">
    <a class="btn btn-ink" href="ar/index.html" lang="ar">العربية</a>
    <a class="btn btn-ghost" href="en/index.html" lang="en" dir="ltr">English</a>
  </div>
</div></div>
</body>
</html>
'''


def page_404():
    # served by GitHub Pages at any missing URL, so it uses root-absolute paths
    return f'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Page not found — {SITE_NAME}</title>
<link rel="icon" type="image/png" href="/logo.png">
{FONTS}
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="bars" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
<div class="center-page"><div>
  <span class="kicker"><span class="n">404</span></span>
  <h1>Page not found</h1>
  <p>The page you're looking for doesn't exist or has moved.</p>
  <h1 lang="ar" dir="rtl" style="font-family:var(--f-ar);font-size:1.8rem">الصفحة غير موجودة</h1>
  <p lang="ar" dir="rtl" style="font-family:var(--f-ar)">الصفحة التي تبحث عنها غير موجودة أو تم نقلها.</p>
  <div class="row">
    <a class="btn btn-ink" href="/en/index.html">Go to homepage</a>
    <a class="btn btn-ghost" href="/ar/index.html" lang="ar" style="font-family:var(--f-ar)">الصفحة الرئيسية</a>
    <a class="btn btn-wa" href="{wa()}" target="_blank" rel="noopener">WhatsApp</a>
  </div>
</div></div>
</body>
</html>
'''


def sitemap(paths):
    rows = []
    for p in paths:
        for l in LANGS:
            alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{canonical(a, p)}"/>' for a in LANGS)
            rows.append(f'  <url><loc>{canonical(l, p)}</loc>{alts}</url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


# ----------------------------------------------------------------------------
def write(rel, text):
    full = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)


def main():
    for d in ['en', 'ar', 'assets']:
        shutil.rmtree(os.path.join(OUT, d), ignore_errors=True)
    shutil.copytree(os.path.join(HERE, 'assets'), os.path.join(OUT, 'assets'))

    pages = list(PAGE_BUILDERS) + list(DEVICE_PAGES)
    count = 0
    for key, path, section, fn in pages:
        for lang in LANGS:
            c = Ctx(lang, path, key, section)
            title, desc, body = fn(c)
            write(f'{lang}/{path}', layout(c, title, desc, body))
            count += 1
    write('index.html', root_index())
    write('404.html', page_404())
    write('sitemap.xml', sitemap([p for _, p, _, _ in pages]))
    write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n')
    print(f'Built {count} pages into {OUT}')


if __name__ == '__main__':
    main()
