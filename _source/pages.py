# -*- coding: utf-8 -*-
"""Page bodies for every page. Shared data lives in content.py."""
import urllib.parse
from content import *


# ----------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------
ARIA_CUR = ' aria-current="page"'
CLS_NO = ' class="no"'


def cls_attr(cls):
    return f' class="{cls}"'


def num_span(n):
    return f'<span class="n">{n}</span>'


def wa(text=None):
    url = 'https://wa.me/' + WHATSAPP
    return url + ('?text=' + urllib.parse.quote(text) if text else '')


def icon(i, cls=''):
    return f'<svg class="ic{(" " + cls) if cls else ""}" aria-hidden="true"><use href="#i-{i}"/></svg>'


def ext(href, inner, cls=''):
    return f'<a{cls_attr(cls) if cls else ""} href="{href}" target="_blank" rel="noopener">{inner}</a>'


def money(c, cur, n):
    cc = CURRENCY[cur]
    return f'{cc[c.lang]}{n}' if cc.get('pre') else f'{n} {cc[c.lang]}'


def page_hero(c, crumbs, h1, lead, actions='', extra=''):
    items = [(c.href('index.html'), c.t(L('Home', 'الرئيسية')))] + crumbs
    cr = ''.join(
        f'<li><a href="{h}">{lbl}</a></li>' if h else f'<li aria-current="page">{lbl}</li>' for h, lbl in items)
    return f'''<section class="page-hero"><div class="wrap">
  <nav aria-label="{c.t(L('Breadcrumb', 'مسار التنقل'))}"><ol class="crumbs">{cr}</ol></nav>
  <h1>{h1}</h1>
  <p class="lead">{lead}</p>
  {('<div class="hero-actions">' + actions + '</div>') if actions else ''}
  {extra}
</div></section>'''


def sec_head(n, kicker, h2, p='', side=''):
    k = f'<span class="kicker">{num_span(n) if n else ""}{kicker}</span>' if kicker else ''
    inner = f'{k}<h2>{h2}</h2>{("<p>" + p + "</p>") if p else ""}'
    if side:
        return f'<div class="sec-head row"><div>{inner}</div>{side}</div>'
    return f'<div class="sec-head">{inner}</div>'


def btn_trial(c, label=None, cls='btn btn-wa'):
    return ext(c.wa('trial'), icon('chat') + (label or c.t(L('Get a free trial', 'اطلب تجربة مجانية'))), cls)


def cta_block(c):
    t = c.t
    return f'''<section class="sec first tight"><div class="wrap">
  <div class="cta">
    <div class="bars" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
    <div>
      <h2>{t(L('Try it free before you pay.', 'جرّب مجاناً قبل أن تدفع.'))}</h2>
      <p>{t(L('12-hour trial for XTV, 24 hours for every other plan. One trial per customer.', 'تجربة 12 ساعة لسيرفر XTV، و24 ساعة لباقي الباقات. تجربة واحدة لكل عميل.'))}</p>
    </div>
    <div class="cta-actions">
      {btn_trial(c, t(L('Request a free trial', 'اطلب تجربة مجانية')))}
      {ext(c.wa('sub'), t(L('Subscribe now', 'اشترك الآن')), 'btn btn-ghost')}
    </div>
  </div>
</div></section>'''


def note(kind, lbl, html):
    return f'<div class="note{" warn" if kind == "warn" else ""}"><span class="lbl">{lbl}</span>{html}</div>'


# ----------------------------------------------------------------------------
# plans
# ----------------------------------------------------------------------------
def aka_text(c, pid):
    p = PLANS[pid]
    if not p.get('aka'):
        return ''
    return ('تُعرف أيضاً باسم ' if c.ar else 'Also known as ') + c.t(p['aka'])


def plan_card(c, region, rp):
    t, p, pid = c.t, PLANS[rp['id']], rp['id']
    nm, rl = t(p['name']), t(region['label'])
    badges = ''
    if rp.get('badge'):
        badges += f'<span class="badge solid">{t(rp["badge"])}</span>'
    if p['egypt_only']:
        badges += f'<span class="badge">{t(L("Egypt only", "مصر فقط"))}</span>'
    p2 = '&nbsp;'
    if rp.get('p2'):
        m = money(c, rp['cur'], rp['p2'])
        p2 = f'أو <b>{m}</b> لمدة سنتين' if c.ar else f'or <b>{m}</b> for 2 years'
    feat = ''.join(
        f'<li{CLS_NO if len(f) > 2 and f[2] else ""}>{icon(f[0])}<span>{t(f[1])}</span></li>' for f in p['feat'])
    stats = ''.join(f'<div class="stat"><b>{v}</b><span>{t(lbl)}</span></div>' for v, lbl in p['stats'])
    aka = aka_text(c, pid)
    logo = (f'<img class="plan-logo" src="{c.root}{p["img"]}" alt="" width="56" height="56" loading="lazy" '
            f'onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'grid\'">'
            f'<span class="plan-mono" style="display:none">{p["mono"]}</span>')
    trial_lbl = f'تجربة مجانية {p["trial"]} ساعة' if c.ar else f'Free {p["trial"]}-hour trial'
    return f'''<article class="plan{" featured" if rp.get("featured") else ""}" style="--c:{p["color"]}">
  <div class="badges">{badges}</div>
  <div class="plan-top">{logo}<div><h3>{nm}</h3>{('<span class="aka">' + aka + '</span>') if aka else ''}</div></div>
  <p class="tag">{t(p["tag"])}</p>
  <div class="price"><span class="amt">{money(c, rp["cur"], rp["p1"])}</span><span class="per">{t(PERIOD[rp["per"]])}</span></div>
  <p class="price-2">{p2}</p>
  <ul class="feat">{feat}</ul>
  <div class="stats">{stats}</div>
  <div class="plan-actions">
    {ext(c.wa('sub', plan=nm, region=rl), icon('chat') + t(L('Subscribe on WhatsApp', 'اشترك عبر واتساب')), 'btn btn-wa')}
    <div class="plan-sub">
      {ext(c.wa('trial', plan=nm, region=rl), icon('clock') + trial_lbl, 'link-arrow')}
      <a class="link-arrow" href="{c.href('setup/index.html')}">{t(L('Setup guide', 'دليل التثبيت'))}{icon('arrow', 'flip')}</a>
    </div>
  </div>
</article>'''


def region_block(c):
    t = c.t
    default = REGIONS[0]['id']
    seg = ''.join(
        f'<button type="button" data-region-btn="{r["id"]}" aria-pressed="{"true" if r["id"] == default else "false"}">{t(r["label"])}</button>'
        for r in REGIONS)
    panels = ''
    for r in REGIONS:
        nt = f'<div class="region-note">{icon("info")}<span>{t(r["note"])}</span></div>' if r['note'] else ''
        cards = ''.join(plan_card(c, r, rp) for rp in r['plans'])
        panels += f'<div data-region-panel="{r["id"]}"{"" if r["id"] == default else " hidden"}>{nt}<div class="plans">{cards}</div></div>'
    return f'''<div class="region">
  <span class="region-label" id="regionLbl">{t(L("I'm watching from", 'أشاهد من'))}</span>
  <div class="seg" role="group" aria-labelledby="regionLbl">{seg}</div>
</div>
{panels}'''


def how_block(c):
    t = c.t
    steps = [
        ('4k', L('Choose a plan', 'اختر باقتك'), L('Pick the plan for your country, or ask for a free trial first.', 'اختر باقة بلدك، أو اطلب تجربة مجانية أولاً.')),
        ('receipt', L('Pay & send receipt', 'ادفع وأرسل الإيصال'), L('Pay, then send a clear screenshot of the receipt on WhatsApp.', 'ادفع، ثم أرسل صورة واضحة للإيصال عبر واتساب.')),
        ('key', L('Get your login', 'استلم بيانات الدخول'), L('Usually within minutes — please allow up to 24 hours.', 'عادةً خلال دقائق — وبحد أقصى 24 ساعة.')),
        ('download', L('Install & watch', 'ثبّت وشاهد'), L('Follow the setup guide for your device.', 'اتبع دليل التثبيت الخاص بجهازك.')),
    ]
    lis = ''.join(
        f'<li><span class="num">0{i + 1}</span>{icon(ic)}<h3>{t(h)}</h3><p>{t(p)}</p></li>' for i, (ic, h, p) in enumerate(steps))
    return f'<ol class="how">{lis}</ol>'


def dev_grid(c):
    t = c.t
    return '<div class="dev-grid">' + ''.join(
        f'<a class="dev-card{" off" if d.get("off") else ""}" href="{c.href("setup/" + d["slug"] + ".html")}">{icon(d["icon"])}<span><b>{t(d["name"])}</b><small>{t(d["short"])}</small></span></a>'
        for d in DEVICES) + '</div>'


def faq_answer(c, a):
    return c.t(a).replace('{channels}', f'<a href="{c.href("channels.html")}">{c.t(L("Channels", "القنوات"))}</a>')


def details(c, iid, q, a, search=False):
    s = ' data-search-item' if search else ''
    return f'<details id="{iid}"{s}><summary>{c.t(q)}{icon("plus")}</summary><div class="ans">{faq_answer(c, a)}</div></details>'


def all_faq():
    out = {}
    for _, items in FAQ:
        for iid, q, a in items:
            out[iid] = (q, a)
    return out


def pay_block(c):
    t = c.t
    eg = ''.join(f'<li><b>{t(n)}</b><span>{t(d)}</span></li>' for n, d in PAY_EGYPT)
    ab = ''.join(f'<li><b>{t(n)}</b><span>{t(d)}</span></li>' for n, d in PAY_ABROAD)
    return f'''<div class="pay">
  <div class="pay-card"><h3>{icon('card')}{t(L('Inside Egypt', 'داخل مصر'))}</h3><ul class="pay-list">{eg}</ul></div>
  <div class="pay-card"><h3>{icon('globe')}{t(L('From abroad', 'من خارج مصر'))}</h3><ul class="pay-list">{ab}</ul></div>
</div>
<div class="pay-foot">{icon('receipt')}<span>{t(L("After paying, send a <b>clear screenshot of the receipt</b> on WhatsApp. Subscriptions don't renew automatically — just message us when it's time.", 'بعد الدفع، أرسل <b>صورة واضحة للإيصال</b> عبر واتساب. الاشتراك لا يتجدد تلقائياً — راسلنا عند موعد التجديد.'))}</span></div>'''


# ----------------------------------------------------------------------------
# HOME
# ----------------------------------------------------------------------------
def home(c):
    t = c.t
    hero = f'''<section class="hero"><div class="wrap hero-grid">
  <div>
    <span class="onair"><span class="dot"></span>{t(L('Live now', 'بث مباشر الآن'))}</span>
    <h1>{t(L('Every match, movie and series. <em>On any screen.</em>', 'كل المباريات والأفلام والمسلسلات. <em>على أي شاشة.</em>'))}</h1>
    <p class="lead">{t(L('Live sports, Arabic and international channels, and huge movie libraries in up to 4K. Install on all your devices — activation usually takes minutes.', 'مباريات مباشرة، قنوات عربية وعالمية، ومكتبات أفلام ضخمة بجودة تصل إلى 4K. ثبّت الاشتراك على كل أجهزتك — والتفعيل عادةً خلال دقائق.'))}</p>
    <div class="hero-cta">
      {btn_trial(c)}
      <a class="btn btn-ghost" href="{c.href('plans.html')}">{t(L('See plans & prices', 'الباقات والأسعار'))} {icon('arrow', 'flip')}</a>
    </div>
    <ul class="trust">
      <li>{icon('clock')}{t(L('12–24h free trial', 'تجربة مجانية 12–24 ساعة'))}</li>
      <li>{icon('4k')}{t(L('Up to 4K / UHD', 'جودة حتى 4K'))}</li>
      <li>{icon('devices')}{t(L('TV, phone, PC & more', 'تلفزيون، موبايل، كمبيوتر والمزيد'))}</li>
      <li>{icon('bolt')}{t(L('Activation in minutes', 'تفعيل خلال دقائق'))}</li>
    </ul>
  </div>
  <div aria-hidden="true">
    <div class="tv"><div class="tv-screen">
      <div class="bars"><i></i><i></i><i></i><i></i></div>
      <div class="tv-top"><span class="live-pill"><span class="dot"></span>LIVE</span><span class="tv-q">4K UHD</span></div>
      <div class="tv-rows">
        <div class="tv-row"><span class="sq" style="background:var(--c-xtv)">{icon('ball')}</span><div><b>{t(L('Live football', 'مباريات مباشرة'))}</b><small>{t(L('Every match day', 'في كل جولة'))}</small></div><span class="chip">LIVE</span></div>
        <div class="tv-row"><span class="sq" style="background:var(--c-premium)">{icon('film')}</span><div><b>{t(L('Movies', 'أفلام'))}</b><small>{t(L('Arabic & international', 'عربية وعالمية'))}</small></div><span class="chip">4K</span></div>
        <div class="tv-row"><span class="sq" style="background:var(--c-basic)">{icon('series')}</span><div><b>{t(L('Series', 'مسلسلات'))}</b><small>{t(L('Full seasons', 'مواسم كاملة'))}</small></div><span class="chip">VOD</span></div>
        <div class="tv-row"><span class="sq" style="background:var(--c-marvel)">{icon('kids')}</span><div><b>{t(L('Kids & family', 'أطفال وعائلة'))}</b><small>{t(L('Family-friendly options', 'خيارات مناسبة للعائلة'))}</small></div><span class="chip">HD</span></div>
      </div>
    </div></div>
    <div class="tv-stand"></div>
  </div>
</div></section>'''

    feats = [
        ('clock', L('Try before you pay', 'جرّب قبل أن تدفع'), L('A free 12–24 hour trial on your own devices, before you spend anything.', 'تجربة مجانية 12–24 ساعة على أجهزتك قبل أن تدفع أي شيء.')),
        ('4k', L('Up to 4K quality', 'جودة حتى 4K'), L('Full HD and 4K on supported plans, devices and connections.', 'جودة Full HD و 4K على الباقات والأجهزة والسرعات الداعمة.')),
        ('devices', L('Every screen you own', 'كل شاشاتك'), L('Smart TV, Android box, Firestick, phone, tablet, Mac or PC.', 'شاشة ذكية، أندرويد بوكس، فايرستيك، موبايل، تابلت، ماك أو كمبيوتر.')),
        ('bolt', L('Activated in minutes', 'تفعيل خلال دقائق'), L('Usually minutes after we receive your receipt — never more than 24 hours.', 'عادةً خلال دقائق من استلام الإيصال — وبحد أقصى 24 ساعة.')),
        ('chat', L('Real help on WhatsApp', 'دعم حقيقي عبر واتساب'), L('Setup help and support in Arabic and English, from a real person.', 'مساعدة في التثبيت ودعم بالعربية والإنجليزية من شخص حقيقي.')),
        ('shield', L('No contracts', 'بدون التزامات'), L('Nothing renews automatically. You renew only when you want to.', 'لا يوجد تجديد تلقائي. تجدد فقط عندما تريد.')),
    ]
    fcards = ''.join(f'<div class="fcard">{icon(i)}<h3>{t(h)}</h3><p>{t(p)}</p></div>' for i, h, p in feats)

    reviews = ''
    if REVIEWS:
        rv = ''.join(
            f'<figure class="review"><blockquote>“{t(r["quote"])}”</blockquote><figcaption>{r["name"]} · {t(r["place"])}</figcaption></figure>'
            for r in REVIEWS)
        reviews = f'<section class="sec"><div class="wrap">{sec_head("", t(L("Reviews", "آراء العملاء")), t(L("What our customers say", "ماذا يقول عملاؤنا")))}<div class="reviews">{rv}</div></div></section>'

    fq = all_faq()
    teaser = ''.join(details(c, i, *fq[i]) for i in ['free-trial', 'which-plan', 'multi-device', 'activation', 'speed', 'family'])

    body = hero + f'''
<section class="sec"><div class="wrap">
  {sec_head('01', t(L('Why Hossam TV', 'لماذا Hossam TV')), t(L('Simple, personal and ready in minutes', 'خدمة بسيطة وشخصية وجاهزة خلال دقائق')))}
  <div class="features">{fcards}</div>
</div></section>

<section class="sec" id="plans"><div class="wrap">
  {sec_head('02', t(L('Plans', 'الباقات')), t(L('Pick a plan for where you watch', 'اختر الباقة المناسبة لبلدك')), t(L('Prices and plans depend on your country. Not sure? Start with a free trial.', 'الأسعار والباقات تختلف حسب بلدك. غير متأكد؟ ابدأ بتجربة مجانية.')))}
  {region_block(c)}
  <div class="more-link"><a class="link-arrow" href="{c.href('plans.html#compare')}">{t(L('Compare all plans side by side', 'قارن بين كل الباقات'))}{icon('arrow', 'flip')}</a></div>
</div></section>

<section class="sec"><div class="wrap">
  {sec_head('03', t(L('How it works', 'طريقة الاشتراك')), t(L('From payment to playing in four steps', 'من الدفع إلى المشاهدة في 4 خطوات')))}
  {how_block(c)}
</div></section>

<section class="sec"><div class="wrap">
  {sec_head('04', t(L('Setup', 'التثبيت')), t(L('Works on the devices you already have', 'يعمل على أجهزتك الحالية')), t(L('Step-by-step guides for every device — most take under 10 minutes.', 'أدلة خطوة بخطوة لكل جهاز — معظمها يستغرق أقل من 10 دقائق.')))}
  {dev_grid(c)}
</div></section>
{reviews}
<section class="sec"><div class="wrap">
  {sec_head('05', 'FAQ' if not c.ar else 'الأسئلة', t(L('Questions, answered', 'الأسئلة الشائعة')), side=f'<a class="link-arrow" href="{c.href("help.html")}">{t(L("All questions & troubleshooting", "كل الأسئلة وحل المشكلات"))}{icon("arrow", "flip")}</a>')}
  <div class="faq">{teaser}</div>
</div></section>
''' + cta_block(c)
    return (t(L('Hossam TV — Live Sports, Movies & Series in 4K', 'Hossam TV — مباريات وأفلام ومسلسلات بجودة 4K')),
            t(L('Live sports, movies and series on any screen, up to 4K. Plans for Egypt, the Gulf and worldwide. Free 12–24 hour trial on WhatsApp.',
                'مباريات مباشرة وأفلام ومسلسلات على أي شاشة بجودة حتى 4K. باقات لمصر والخليج وكل الدول. تجربة مجانية 12–24 ساعة عبر واتساب.')),
            body)


# ----------------------------------------------------------------------------
# PLANS
# ----------------------------------------------------------------------------
def plans(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('Plans', 'الباقات')))],
                     t(L('Plans & prices', 'الباقات والأسعار')),
                     t(L('Choose your country to see the plans and prices available to you. Every plan comes with a free trial first.',
                         'اختر بلدك لتظهر لك الباقات والأسعار المتاحة. كل باقة تبدأ بتجربة مجانية.')))

    fit = [
        ('xtv', L('Football in Egypt, watching with family', 'كرة القدم في مصر مع العائلة')),
        ('marvel', L('Movies & series in Egypt', 'الأفلام والمسلسلات في مصر')),
        ('basic', L('Arabic channels & football, anywhere', 'القنوات العربية والكرة، في أي دولة')),
        ('premium', L('Everything: all sports, 4K, biggest library', 'كل شيء: كل الرياضات، 4K، أكبر مكتبة')),
    ]
    fit_html = ''.join(
        f'<a href="{c.wa("trial", plan=t(PLANS[pid]["name"]))}" target="_blank" rel="noopener" style="--c:{PLANS[pid]["color"]}"><span class="q">{t(q)}</span><b>{t(PLANS[pid]["name"])} {icon("arrow", "flip")}</b></a>'
        for pid, q in fit)

    head = ''.join(f'<th scope="col" style="--c:{PLANS[p]["color"]}">{t(PLANS[p]["name"])}</th>' for p in PLAN_ORDER)
    rows = ''
    for lbl, cells in COMPARE:
        tds = ''
        for p in PLAN_ORDER:
            yes, txt = cells[p]
            if yes is True:
                tds += f'<td class="y">{icon("check")}<span>{t(txt)}</span></td>'
            elif yes is False:
                tds += f'<td class="n">{icon("x")}<span>{t(txt)}</span></td>'
            else:
                tds += f'<td>{t(txt)}</td>'
        rows += f'<tr><th scope="row">{t(lbl)}</th>{tds}</tr>'
    rows += '<tr><th scope="row">' + t(L('Apps', 'التطبيقات')) + '</th>' + ''.join(
        f'<td><span class="ltr">{t(PLANS[p]["apps"])}</span></td>' for p in PLAN_ORDER) + '</tr>'

    inc = [
        ('devices', L('Install on all your devices', 'التثبيت على كل أجهزتك'), L('Watch on one screen at a time.', 'المشاهدة على شاشة واحدة في نفس الوقت.')),
        ('clock', L('Free trial first', 'تجربة مجانية أولاً'), L('12 hours for XTV, 24 hours for the rest.', '12 ساعة لـ XTV و24 ساعة لباقي الباقات.')),
        ('bolt', L('Activation in minutes', 'تفعيل خلال دقائق'), L('Please allow up to 24 hours.', 'وبحد أقصى 24 ساعة.')),
        ('chat', L('Setup help on WhatsApp', 'مساعدة في التثبيت عبر واتساب'), L('Arabic and English.', 'بالعربية والإنجليزية.')),
        ('refresh', L('No automatic renewal', 'بدون تجديد تلقائي'), L('You renew only when you want to.', 'تجدد فقط عندما تريد.')),
        ('info', L('Maintenance updates', 'أخبار الصيانة'), L('Posted on our WhatsApp Status.', 'تُنشر على حالة الواتساب.')),
    ]
    inc_html = ''.join(f'<li>{icon("check")}<div><b>{t(h)}</b><span>{t(p)}</span></div></li>' for _, h, p in inc)

    body = hero + f'''
<section class="sec first"><div class="wrap">{region_block(c)}</div></section>

<section class="sec"><div class="wrap">
  {sec_head('', t(L('Quick guide', 'دليل سريع')), t(L('Which plan fits you?', 'أي باقة تناسبك؟')), t(L('Tap one to request a free trial of that plan.', 'اضغط على أي منها لطلب تجربة مجانية لهذه الباقة.')))}
  <div class="fit">{fit_html}</div>
</div></section>

<section class="sec" id="compare"><div class="wrap">
  {sec_head('', t(L('Compare', 'مقارنة')), t(L('All plans side by side', 'كل الباقات جنباً إلى جنب')))}
  <div class="table-wrap"><table class="cmp"><thead><tr><th scope="col"><span class="sr-only"></span></th>{head}</tr></thead><tbody>{rows}</tbody></table></div>
</div></section>

<section class="sec"><div class="wrap">
  {sec_head('', t(L('Included', 'مع كل باقة')), t(L('What you get with every plan', 'ما تحصل عليه مع كل باقة')))}
  <ul class="included">{inc_html}</ul>
</div></section>

<section class="sec" id="payment"><div class="wrap">
  {sec_head('', t(L('Payment', 'الدفع')), t(L('Ways to pay', 'طرق الدفع')), t(L("Message us on WhatsApp and we'll send the payment details for your method.", 'راسلنا عبر واتساب وسنرسل لك بيانات الدفع للطريقة المناسبة لك.')))}
  {pay_block(c)}
</div></section>
''' + cta_block(c)
    return (t(L('Plans & Prices', 'الباقات والأسعار')),
            t(L('Hossam TV plans and prices for Egypt, Saudi Arabia & the Gulf, the UAE and worldwide. Compare Basic, Premium, XTV and Marvel.',
                'باقات وأسعار Hossam TV لمصر والسعودية والخليج والإمارات وباقي الدول. قارن بين الأساسية وبريميوم و XTV و Marvel.')),
            body)


# ----------------------------------------------------------------------------
# CHANNELS
# ----------------------------------------------------------------------------
def channels(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('Channels', 'القنوات')))],
                     t(L("What you can watch", 'ماذا يمكنك أن تشاهد')),
                     t(L('Live sports, Arabic and international channels, movies, series and more. Here is what each plan is strongest at.',
                         'رياضة مباشرة، قنوات عربية وعالمية، أفلام، مسلسلات والمزيد. إليك أقوى ما في كل باقة.')))
    cats = ''
    for ic, h, p, best in CATEGORIES:
        chips = ''.join(f'<span class="pchip" style="--c:{PLANS[b]["color"]}">{t(PLANS[b]["name"])}</span>' for b in best)
        cats += f'<div class="cat">{icon(ic)}<h3>{t(h)}</h3><p>{t(p)}</p><div class="dots">{chips}</div></div>'

    per = ''
    for pid in PLAN_ORDER:
        p = PLANS[pid]
        nm = t(p['name'])
        stats = ''.join(f'<div class="stat"><b>{v}</b><span>{t(lbl)}</span></div>' for v, lbl in p['stats'])
        feat = ''.join(f'<li{CLS_NO if len(f) > 2 and f[2] else ""}>{icon(f[0])}<span>{t(f[1])}</span></li>' for f in p['feat'])
        eg = f'<span class="badge">{t(L("Egypt only", "مصر فقط"))}</span>' if p['egypt_only'] else ''
        per += f'''<article class="plan" style="--c:{p["color"]}">
  <div class="badges">{eg}</div>
  <div class="plan-top"><span class="plan-mono">{p["mono"]}</span><div><h3>{nm}</h3>{('<span class="aka">' + aka_text(c, pid) + '</span>') if p.get('aka') else ''}</div></div>
  <p class="tag">{t(p["tag"])}</p>
  <div class="stats">{stats}</div>
  <ul class="feat">{feat}</ul>
  <div class="plan-actions">{ext(c.wa('channels', plan=nm), icon('chat') + t(L('Ask for the full channel list', 'اطلب قائمة القنوات الكاملة')), 'btn btn-ghost')}</div>
</article>'''

    body = hero + f'''
<section class="sec first"><div class="wrap">
  {sec_head('', t(L('Categories', 'الفئات')), t(L('Something for everyone at home', 'شيء لكل فرد في البيت')), t(L('Coloured tags show which plans are strongest in each category.', 'الألوان توضح أقوى الباقات في كل فئة.')))}
  <div class="cats">{cats}</div>
</div></section>

<section class="sec"><div class="wrap">
  {sec_head('', t(L('By plan', 'حسب الباقة')), t(L('What each plan includes', 'ماذا تتضمن كل باقة')), t(L("Line-ups change often. Ask us on WhatsApp for the latest list — or take the free trial and browse everything yourself.", 'قوائم القنوات تتغير باستمرار. اطلب أحدث قائمة عبر واتساب — أو خذ التجربة المجانية وتصفح كل شيء بنفسك.')))}
  <div class="plans">{per}</div>
</div></section>

<section class="sec"><div class="wrap">
  {sec_head('', t(L('Quality', 'الجودة')), t(L('What internet speed do you need?', 'ما سرعة الإنترنت التي تحتاجها؟')), t(L('For each screen that is watching. A network cable or 5 GHz Wi-Fi gives the smoothest picture.', 'لكل شاشة تشاهد. كابل الإنترنت أو واي فاي 5 GHz يعطي أفضل صورة.')))}
  <div class="speed">
    <div><em>SD</em><b>5 Mbps</b><span>{t(L('Phones and small screens', 'الموبايل والشاشات الصغيرة'))}</span></div>
    <div><em>Full HD</em><b>10 Mbps</b><span>{t(L('Most TVs', 'معظم الشاشات'))}</span></div>
    <div><em>4K UHD</em><b>25 Mbps+</b><span>{t(L('4K TV or device needed', 'تحتاج شاشة أو جهازاً يدعم 4K'))}</span></div>
  </div>
</div></section>
''' + cta_block(c)
    return (t(L('Channels, Sports, Movies & Series', 'القنوات والرياضة والأفلام والمسلسلات')),
            t(L('Live football and sports, Arabic and international channels, movies, series, kids and news — see what each Hossam TV plan offers.',
                'مباريات ورياضة مباشرة، قنوات عربية وعالمية، أفلام، مسلسلات، أطفال وأخبار — اعرف ماذا تقدم كل باقة من Hossam TV.')),
            body)


# ----------------------------------------------------------------------------
# SETUP — index
# ----------------------------------------------------------------------------
def golden_rule(c):
    t = c.t
    return f'''<div class="rule">{icon('key')}<div>
  <b>{t(L('Golden rule: one screen at a time.', 'القاعدة الذهبية: شاشة واحدة في نفس الوقت.'))}</b>
  <span>{t(L('Install on as many devices as you like, but only one can play at once — watching on two at the same time can lock the account.', 'ثبّت الاشتراك على أي عدد من الأجهزة، لكن التشغيل على جهاز واحد فقط في نفس الوقت — التشغيل على جهازين معاً قد يوقف الحساب.'))}</span>
</div></div>'''


def copy_btn(code):
    return f'<button type="button" class="code" data-copy="{code}">{code}{icon("copy")}</button>'


def open_link(code):
    return f'<a class="code" href="https://{code}" target="_blank" rel="noopener">{code}{icon("arrow")}</a>'


def setup_index(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('Setup', 'التثبيت')))],
                     t(L('Installation guides', 'أدلة التثبيت')),
                     t(L('Pick your device for step-by-step instructions. Most setups take under 10 minutes.',
                         'اختر جهازك لتظهر لك الخطوات بالتفصيل. معظم الأجهزة تستغرق أقل من 10 دقائق.')))
    rows = ''
    for pid in PLAN_ORDER:
        p = PLANS[pid]
        codes = ''
        for a in APPS[pid]:
            w = ''.join(f'<div class="warn-t">{icon("warn")}{t(WARN[x])}</div>' for x in a.get('warn', []))
            codes += f'<div style="margin-bottom:8px"><b>{a["name"]}</b>{(" · " + t(L("Recommended", "موصى به"))) if a.get("rec") else ""}<br>{copy_btn(a["code"])}{w}</div>'
        rows += f'<tr><th scope="row" style="--c:{p["color"]}"><span class="pchip" style="--c:{p["color"]}">{t(p["name"])}</span></th><td>{codes}</td></tr>'
    rows += f'<tr><th scope="row">{t(L("Any plan", "أي باقة"))}</th><td><b>IPTV Smarters Pro</b> — {t(L("alternative app for Android devices", "تطبيق بديل لأجهزة أندرويد"))}<br>{copy_btn(SMARTERS)}</td></tr>'

    need = [
        ('key', L('Your login details', 'بيانات الدخول'), L("We send them on WhatsApp after activation or with your trial.", 'نرسلها عبر واتساب بعد التفعيل أو مع التجربة المجانية.')),
        ('wifi', L('A stable connection', 'اتصال إنترنت مستقر'), L('10 Mbps for Full HD, 25 Mbps for 4K.', '10 ميجابت لجودة Full HD و25 ميجابت لجودة 4K.')),
        ('clock', L('About 10 minutes', 'حوالي 10 دقائق'), L('And your TV remote or phone nearby.', 'مع ريموت التلفزيون أو الموبايل.')),
        ('chat', L('Stuck? Message us', 'واجهتك مشكلة؟ راسلنا'), L('We help with setup on WhatsApp.', 'نساعدك في التثبيت عبر واتساب.')),
    ]
    need_html = ''.join(f'<li>{icon("check")}<div><b>{t(h)}</b><span>{t(p)}</span></div></li>' for _, h, p in need)

    body = hero + f'''
<section class="sec first"><div class="wrap">
  {golden_rule(c)}
  {sec_head('1', t(L('Choose your device', 'اختر جهازك')), t(L('Which device are you installing on?', 'على أي جهاز ستثبّت؟')))}
  {dev_grid(c)}
</div></section>

<section class="sec"><div class="wrap">
  {sec_head('', t(L('Before you start', 'قبل أن تبدأ')), t(L('What you need', 'ما تحتاجه')))}
  <ul class="included">{need_html}</ul>
</div></section>

<section class="sec" id="codes"><div class="wrap">
  {sec_head('', t(L('Quick reference', 'مرجع سريع')), t(L('App codes by plan', 'أكواد التطبيقات حسب الباقة')), t(L('Type these in the Downloader app on TVs, or open them in your browser on a phone. Tap a code to copy it.', 'اكتبها في تطبيق Downloader على التلفزيون، أو افتحها في المتصفح على الموبايل. اضغط على الكود لنسخه.')))}
  <div class="table-wrap"><table class="cmp codes-table" style="min-width:0"><tbody>{rows}</tbody></table></div>
</div></section>
''' + cta_block(c)
    return (t(L('Setup Guides for Every Device', 'أدلة التثبيت لكل الأجهزة')),
            t(L('How to install Hossam TV on Android TV, Firestick, Android, iPhone, Apple TV, Samsung and LG Smart TVs and Windows. Step-by-step guides.',
                'طريقة تثبيت Hossam TV على أندرويد تي في، فايرستيك، أندرويد، آيفون، أبل تي في، شاشات سامسونج و LG، وويندوز. خطوات بالتفصيل.')),
            body)


# ----------------------------------------------------------------------------
# SETUP — device pages
# ----------------------------------------------------------------------------
def apps_block(c, dev):
    """Plan tabs + app list. dev decides copy-vs-link and Firestick filtering."""
    t = c.t
    tabs = ''.join(
        f'<button type="button" data-plan-btn="{pid}" aria-pressed="{"true" if i == 0 else "false"}">{t(PLANS[pid]["name"])}</button>'
        for i, pid in enumerate(PLAN_ORDER))
    panels = ''
    for i, pid in enumerate(PLAN_ORDER):
        lst = [dict(a) for a in APPS[pid]]
        if dev == 'firestick':
            for a in lst:
                if 'firestick' in a.get('warn', []):
                    a['rec'] = False
                    a['blocked'] = True
            lst.sort(key=lambda a: 1 if a.get('blocked') else 0)
            if not any(a.get('rec') for a in lst):
                for a in lst:
                    if not a.get('blocked'):
                        a['rec'] = True
                        break
        items = ''
        for a in lst:
            warns = [w for w in a.get('warn', []) if w != 'firestick' or dev == 'firestick']
            w = ''.join(f'<div class="warn-t">{icon("warn")}{t(WARN[x])}</div>' for x in warns)
            code = open_link(a['code']) if dev == 'android' else copy_btn(a['code'])
            rec = f'<span class="rec-b">{t(L("Recommended", "موصى به"))}</span>' if a.get('rec') else ''
            items += f'<div class="app{" rec" if a.get("rec") else ""}"><div class="app-h">{a["name"]}{rec}</div>{code}{w}</div>'
        panels += f'<div data-panel="{pid}"{"" if i == 0 else " hidden"}><div class="apps">{items}</div></div>'
    return f'''<div class="plan-tabs"><span class="hint" style="display:block;color:var(--muted);font-size:.85rem;margin-bottom:6px">{t(L('Your plan:', 'باقتك:'))}</span>
<div class="seg" role="group" aria-label="{t(L('Plan', 'الباقة'))}">{tabs}</div></div>{panels}'''


def mediafire(c):
    return c.t(L('The code opens a MediaFire page. Tap the <b>big blue Download</b> button — not "Download faster".',
                 'سيفتح الكود صفحة MediaFire. اضغط على زر التحميل <b>الأزرق الكبير</b> — وليس «Download faster».'))


def sign_in(c):
    return c.t(L('Open the app and sign in with the username and password we sent you on WhatsApp.',
                 'افتح التطبيق وسجّل الدخول باسم المستخدم وكلمة المرور التي أرسلناها لك عبر واتساب.'))


def smarters_note(c):
    t = c.t
    return note('tip', t(L('Alternative app', 'تطبيق بديل')), t(L(
        f'Prefer <b>IPTV Smarters Pro</b>? Type {copy_btn(SMARTERS)} in Downloader — it works with every plan. <a href="{SMARTERS_VIDEO}" target="_blank" rel="noopener">Watch the tutorial</a>',
        f'تفضّل <b>IPTV Smarters Pro</b>؟ اكتب {copy_btn(SMARTERS)} في Downloader — يعمل مع كل الباقات. <a href="{SMARTERS_VIDEO}" target="_blank" rel="noopener">شاهد الشرح</a>')))


def trouble_links(c, ids):
    t = c.t
    names = {i: q for i, q, _ in TROUBLE}
    return '<ul>' + ''.join(f'<li><a href="{c.href("help.html#" + i)}">{t(names[i])}</a></li>' for i in ids) + '</ul>'


def device_data(c, slug):
    t = c.t
    P = lambda en, ar: t(L(en, ar))
    if slug == 'android-tv':
        return dict(
            h1=P('Install Hossam TV on Android TV & TV boxes', 'تثبيت Hossam TV على أندرويد تي في وأجهزة البوكس'),
            lead=P('Works on Android TV and Google TV sets and most Android TV boxes. It takes about 10 minutes.',
                   'يعمل على شاشات Android TV و Google TV ومعظم أجهزة أندرويد بوكس. يستغرق التثبيت حوالي 10 دقائق.'),
            desc=P('Step-by-step: install Hossam TV on Android TV, Google TV and Android TV boxes using the Downloader app.',
                   'خطوة بخطوة: تثبيت Hossam TV على Android TV و Google TV وأجهزة أندرويد بوكس باستخدام تطبيق Downloader.'),
            steps=[
                P('On your TV, open <b>Google Play</b> and install <b>Downloader by AFTVNews</b>.',
                  'على التلفزيون، افتح <b>Google Play</b> وثبّت تطبيق <b>Downloader by AFTVNews</b>.'),
                P('Open Downloader and type the code for your plan:', 'افتح Downloader واكتب الكود الخاص بباقتك:') + apps_block(c, 'androidtv'),
                mediafire(c),
                P('When asked, allow Downloader to install unknown apps, then tap <b>Install</b>.<span class="hint">Nothing happens? Look under <span class="path">Settings → Apps → Security &amp; restrictions → Unknown sources</span> and turn on Downloader. The path differs slightly by brand.</span>',
                  'عند السؤال، اسمح لتطبيق Downloader بتثبيت التطبيقات، ثم اضغط <b>Install</b>.<span class="hint">لا يحدث شيء؟ ادخل إلى <span class="path">الإعدادات ← التطبيقات ← الأمان والقيود ← مصادر غير معروفة</span> وفعّل Downloader. المسار يختلف قليلاً حسب الشركة.</span>'),
                sign_in(c),
            ],
            notes=[smarters_note(c)],
            trouble=['install', 'login', 'buffering'],
        )
    if slug == 'firestick':
        vega = note('warn', P('Check your Firestick first', 'تأكد من نوع الفايرستيك أولاً'), P(
            "Newer Firesticks running <b>Vega OS</b> — such as the <b>Fire TV Stick 4K Select</b> and the 2026 <b>Fire TV Stick HD</b> — can't run IPTV apps. To check: <span class=\"path\">Settings → My Fire TV → About</span>. If the software version says <b>Fire OS</b>, you're good. If it just says <b>OS</b> with a version starting with 1, it's Vega OS — use an Android TV box or another device instead.",
            'أجهزة فايرستيك الأحدث التي تعمل بنظام <b>Vega OS</b> — مثل <b>Fire TV Stick 4K Select</b> و<b>Fire TV Stick HD</b> إصدار 2026 — لا تدعم تطبيقات IPTV. للتأكد: <span class="path"><bdi dir="ltr">Settings → My Fire TV → About</bdi></span>. إذا كان إصدار النظام مكتوباً <b>Fire OS</b> فجهازك مناسب. إذا كان مكتوباً <b>OS</b> فقط ويبدأ الرقم بـ 1، فهو Vega OS — استخدم أندرويد بوكس أو جهازاً آخر.'))
        return dict(
            h1=P('Install Hossam TV on Amazon Firestick', 'تثبيت Hossam TV على أمازون فايرستيك'),
            lead=P('Works on Fire TV Sticks and Fire TV devices running Fire OS. It takes about 10 minutes.',
                   'يعمل على أجهزة Fire TV Stick و Fire TV التي تعمل بنظام Fire OS. يستغرق التثبيت حوالي 10 دقائق.'),
            desc=P('Step-by-step: install Hossam TV on Amazon Firestick with Downloader, and check if your Firestick runs Vega OS.',
                   'خطوة بخطوة: تثبيت Hossam TV على أمازون فايرستيك باستخدام Downloader، وطريقة التأكد إن كان جهازك يعمل بنظام Vega OS.'),
            pre=[vega],
            steps=[
                P('From the Home screen, open <b>Find → Search</b>, search for <b>Downloader</b> and install <b>Downloader by AFTVNews</b>.',
                  'من الشاشة الرئيسية، افتح <b>Find ← Search</b>، ابحث عن <b>Downloader</b> وثبّت <b>Downloader by AFTVNews</b>.'),
                P('Allow Downloader to install apps: <span class="path">Settings → My Fire TV → Developer options → Install unknown apps → Downloader → ON</span>.<span class="hint">No Developer options? Go to <span class="path">Settings → My Fire TV → About</span> and click your device name 7 times until it says you are a developer.</span>',
                  'اسمح لـ Downloader بتثبيت التطبيقات: <span class="path"><bdi dir="ltr">Settings → My Fire TV → Developer options → Install unknown apps → Downloader → ON</bdi></span>.<span class="hint">لا تجد Developer options؟ ادخل إلى <span class="path"><bdi dir="ltr">Settings → My Fire TV → About</bdi></span> واضغط على اسم جهازك 7 مرات حتى تظهر رسالة أنك أصبحت مطوراً.</span>'),
                P('Open Downloader and type the code for your plan:', 'افتح Downloader واكتب الكود الخاص بباقتك:') + apps_block(c, 'firestick'),
                mediafire(c) + P(' Then tap <b>Install</b>.', ' ثم اضغط <b>Install</b>.'),
                sign_in(c) + P('<span class="hint">Tip: hold the Home button → <b>Apps</b> to find the app later and move it to the front.</span>',
                               '<span class="hint">نصيحة: اضغط مطولاً على زر Home ← <b>Apps</b> لتجد التطبيق لاحقاً وتنقله إلى المقدمة.</span>'),
            ],
            notes=[smarters_note(c)],
            trouble=['install', 'login', 'buffering'],
        )
    if slug == 'android':
        return dict(
            h1=P('Install Hossam TV on Android phones & tablets', 'تثبيت Hossam TV على موبايل وتابلت أندرويد'),
            lead=P('Download the app straight from your phone’s browser. It takes about 5 minutes.',
                   'حمّل التطبيق مباشرة من متصفح الموبايل. يستغرق التثبيت حوالي 5 دقائق.'),
            desc=P('Step-by-step: install Hossam TV on an Android phone or tablet.',
                   'خطوة بخطوة: تثبيت Hossam TV على موبايل أو تابلت أندرويد.'),
            steps=[
                P("Open your phone's browser and go to the link for your plan:", 'افتح المتصفح على موبايلك وادخل على رابط باقتك:') + apps_block(c, 'android'),
                mediafire(c),
                P('When the <b>APK</b> file finishes downloading, open it and tap <b>Install</b>.<span class="hint">If your phone asks, allow your browser to install apps. If Google Play Protect warns you, tap <b>More details → Install anyway</b>.</span>',
                  'بعد تحميل ملف <b>APK</b>، افتحه واضغط <b>تثبيت</b>.<span class="hint">إذا سألك الهاتف، اسمح للمتصفح بتثبيت التطبيقات. وإذا ظهر تحذير Google Play Protect، اضغط <b>مزيد من التفاصيل ← التثبيت على أي حال</b>.</span>'),
                sign_in(c),
            ],
            notes=[note('tip', P('Alternative app', 'تطبيق بديل'), P(f'You can also get <b>IPTV Smarters Pro</b> from {open_link(SMARTERS)}', f'يمكنك أيضاً تحميل <b>IPTV Smarters Pro</b> من {open_link(SMARTERS)}'))],
            trouble=['install', 'login', 'buffering'],
        )
    if slug == 'apple':
        return dict(
            h1=P('Install Hossam TV on iPhone, iPad, Mac & Apple TV', 'تثبيت Hossam TV على آيفون وآيباد وماك وأبل تي في'),
            lead=P('Apple devices use the free Smarters Player Lite app from the App Store. It takes about 5 minutes and works the same for every plan.',
                   'أجهزة أبل تستخدم تطبيق Smarters Player Lite المجاني من App Store. يستغرق حوالي 5 دقائق ونفس الخطوات لكل الباقات.'),
            desc=P('Step-by-step: watch Hossam TV on iPhone, iPad, Mac and Apple TV with Smarters Player Lite.',
                   'خطوة بخطوة: شاهد Hossam TV على آيفون وآيباد وماك وأبل تي في باستخدام Smarters Player Lite.'),
            steps=[
                P('Open the <b>App Store</b> and install <b>Smarters Player Lite</b>.', 'افتح <b>App Store</b> وثبّت تطبيق <b>Smarters Player Lite</b>.'),
                P('Open the app, accept the terms and choose <b>Login with Xtream Codes API</b>.', 'افتح التطبيق، وافق على الشروط، ثم اختر <b>Login with Xtream Codes API</b>.'),
                P('Enter any name you like, then the <b>username</b>, <b>password</b> and <b>server URL</b> we sent you on WhatsApp, and tap <b>Add user</b>.',
                  'اكتب أي اسم تريده، ثم <b>اسم المستخدم</b> و<b>كلمة المرور</b> و<b>رابط السيرفر</b> التي أرسلناها لك عبر واتساب، واضغط <b>Add user</b>.'),
                P('Wait for the channels and movies to load, then start watching.', 'انتظر حتى يتم تحميل القنوات والأفلام، ثم ابدأ المشاهدة.'),
            ],
            notes=[note('tip', P('Apple TV', 'أبل تي في'), P('The same app and the same steps work on Apple TV — search for it in the Apple TV App Store.', 'نفس التطبيق ونفس الخطوات تعمل على أبل تي في — ابحث عنه في App Store الخاص بأبل تي في.'))],
            trouble=['login', 'buffering'],
        )
    if slug == 'smart-tv':
        return dict(
            h1=P('Install Hossam TV on Samsung & LG Smart TVs', 'تثبيت Hossam TV على شاشات سامسونج و LG'),
            lead=P("Smart TVs use IBO Player (or Bob Player). You install the app, send us your TV's code, and we load your playlist for you.",
                   'الشاشات الذكية تستخدم تطبيق IBO Player (أو Bob Player). تثبّت التطبيق، ترسل لنا كود الشاشة، ونحن نجهّز لك القائمة.'),
            desc=P('Step-by-step: watch Hossam TV on Samsung and LG Smart TVs with IBO Player or Bob Player, including app fees.',
                   'خطوة بخطوة: شاهد Hossam TV على شاشات سامسونج و LG باستخدام IBO Player أو Bob Player، مع توضيح رسوم التطبيق.'),
            steps=[
                P("Open your TV's app store (<b>Apps</b> on Samsung, <b>LG Content Store</b> on LG) and search for <b>IBO Player</b>.<span class=\"hint\">Can't find it? Install <b>Bob Player</b> instead — same company, same steps.</span>",
                  'افتح متجر التطبيقات في الشاشة (<b>Apps</b> في سامسونج، و<b>LG Content Store</b> في LG) وابحث عن <b>IBO Player</b>.<span class="hint">لا تجده؟ ثبّت <b>Bob Player</b> بدلاً منه — من نفس الشركة وبنفس الخطوات.</span>'),
                P('Install and open it. The screen shows a <b>Device ID</b> (MAC) and a <b>Device Key</b>.', 'ثبّت التطبيق وافتحه. ستظهر على الشاشة بيانات <b>Device ID</b> (MAC) و <b>Device Key</b>.'),
                P(f'Send a clear photo of them on WhatsApp together with your subscription <b>username</b>. {ext(c.wa("tv"), "Send on WhatsApp")}',
                  f'أرسل صورة واضحة لهما عبر واتساب مع <b>اسم المستخدم</b> الخاص باشتراكك. {ext(c.wa("tv"), "أرسل عبر واتساب")}'),
                P("We load your playlist. Restart the app and your channels will appear.", 'سنجهّز قائمتك. أعد تشغيل التطبيق وستظهر القنوات.'),
            ],
            notes=[
                note('tip', P('App fee — Basic & Premium', 'رسوم التطبيق — الأساسية وبريميوم'),
                     P('IBO / Bob Player activation is <b>free for your first TV</b> with your plan. Each extra TV is <b>$4</b> for lifetime.',
                       'تفعيل IBO / Bob Player <b>مجاني لأول شاشة</b> مع باقتك. كل شاشة إضافية <b>4 دولارات</b> مدى الحياة.')),
                note('warn', P('App fee — XTV & Marvel', 'رسوم التطبيق — XTV و Marvel'),
                     P('IBO / Bob Player activation is separate from your subscription: <b>100 EGP</b> for 1 year or <b>200 EGP</b> for lifetime, per TV. The app gives you a 7-day free trial first.',
                       'تفعيل IBO / Bob Player منفصل عن الاشتراك: <b>100 جنيه</b> لسنة أو <b>200 جنيه</b> مدى الحياة لكل شاشة. التطبيق يتيح تجربة مجانية 7 أيام أولاً.')),
            ],
            trouble=['buffering', 'locked'],
        )
    if slug == 'windows':
        return dict(
            h1=P('Install Hossam TV on Windows PC & laptop', 'تثبيت Hossam TV على كمبيوتر ويندوز'),
            lead=P('Windows uses the free SFVIP Player. It takes about 5 minutes and works the same for every plan.',
                   'ويندوز يستخدم برنامج SFVIP Player المجاني. يستغرق حوالي 5 دقائق ونفس الخطوات لكل الباقات.'),
            desc=P('Step-by-step: watch Hossam TV on a Windows PC or laptop with SFVIP Player.',
                   'خطوة بخطوة: شاهد Hossam TV على كمبيوتر أو لابتوب ويندوز باستخدام SFVIP Player.'),
            steps=[
                P(f'Download <b>SFVIP Player</b> (ZIP file) from <a href="{SFVIP_ZIP}" target="_blank" rel="noopener">MediaFire</a>.<span class="hint">Click the big blue Download button — not "Download faster".</span>',
                  f'حمّل <b>SFVIP Player</b> (ملف ZIP) من <a href="{SFVIP_ZIP}" target="_blank" rel="noopener">MediaFire</a>.<span class="hint">اضغط زر التحميل الأزرق الكبير — وليس «Download faster».</span>'),
                P('Right-click the ZIP file, choose <b>Extract All</b>, then open the app inside.<span class="hint">If Windows shows "Windows protected your PC", click <b>More info → Run anyway</b>.</span>',
                  'اضغط بزر الماوس الأيمن على ملف ZIP واختر <b>Extract All</b>، ثم افتح البرنامج الموجود بداخله.<span class="hint">إذا ظهرت رسالة "Windows protected your PC"، اضغط <b>More info ← Run anyway</b>.</span>'),
                sign_in(c),
            ],
            notes=[note('tip', P('Video', 'فيديو'), P(f'Prefer video? <a href="{SFVIP_VIDEO}" target="_blank" rel="noopener">Watch the tutorial</a>', f'تفضّل الفيديو؟ <a href="{SFVIP_VIDEO}" target="_blank" rel="noopener">شاهد الشرح</a>'))],
            trouble=['login', 'buffering'],
        )
    if slug == 'roku':
        return dict(
            h1=P('Hossam TV on Roku', 'Hossam TV على روكو'),
            lead=P("Sorry — Roku isn't supported, because it doesn't allow the player apps we use.",
                   'للأسف روكو غير مدعوم، لأنه لا يسمح بتثبيت التطبيقات التي نستخدمها.'),
            desc=P('Roku is not supported by Hossam TV. Here are the easiest alternatives.', 'روكو غير مدعوم في Hossam TV. إليك أسهل البدائل.'),
            roku=True,
        )


def device_page(slug):
    def fn(c):
        t = c.t
        d = next(x for x in DEVICES if x['slug'] == slug)
        data = device_data(c, slug)
        hero = page_hero(c, [(c.href('setup/index.html'), t(L('Setup', 'التثبيت'))), (None, t(d['name']))], data['h1'], data['lead'])
        side_links = ''.join(
            f'<li><a href="{c.href("setup/" + x["slug"] + ".html")}"{ARIA_CUR if x["slug"] == slug else ""}>{icon(x["icon"])}{t(x["name"])}</a></li>'
            for x in DEVICES)
        side = f'''<aside class="side">
  <div class="side-card"><h3>{t(L('Other devices', 'أجهزة أخرى'))}</h3><ul>{side_links}</ul></div>
  <div class="side-card"><h3>{t(L('Need a hand?', 'تحتاج مساعدة؟'))}</h3><p>{t(L("Send us a photo of your screen on WhatsApp and we'll guide you.", 'أرسل لنا صورة للشاشة عبر واتساب وسنرشدك.'))}</p>{ext(c.wa('help'), icon('chat') + t(L('Get setup help', 'اطلب المساعدة')), 'btn btn-wa btn-sm')}</div>
</aside>'''
        if data.get('roku'):
            alts = [x for x in DEVICES if x['slug'] in ('android-tv', 'firestick')]
            alt_html = ''.join(
                f'<a class="dev-card" href="{c.href("setup/" + x["slug"] + ".html")}">{icon(x["icon"])}<span><b>{t(x["name"])}</b><small>{t(x["short"])}</small></span></a>' for x in alts)
            main = f'''<div class="guide">
  <h2>{t(L('Easiest alternatives', 'أسهل البدائل'))}</h2>
  <p>{t(L('An <b>Android TV box</b> or a <b>Firestick</b> running Fire OS (not Vega OS) plugs into the same TV and takes about 10 minutes to set up.', '<b>أندرويد بوكس</b> أو <b>فايرستيك</b> بنظام Fire OS (وليس Vega OS) يتصل بنفس الشاشة ويستغرق تثبيته حوالي 10 دقائق.'))}</p>
  <div class="dev-grid" style="margin-top:16px">{alt_html}</div>
</div>'''
        else:
            pre = f'<div class="notes pre">{"".join(data["pre"])}</div>' if data.get('pre') else ''
            steps = ''.join(f'<li class="st"><span class="st-n">{i + 1}</span><div class="st-b">{s}</div></li>' for i, s in enumerate(data['steps']))
            notes = f'<div class="notes">{"".join(data["notes"])}</div>' if data.get('notes') else ''
            trouble = f'<div class="trouble prose"><h2>{t(L("Having trouble?", "تواجه مشكلة؟"))}</h2>{trouble_links(c, data["trouble"])}</div>'
            main = f'<div class="guide">{pre}<h2>{t(L("Steps", "الخطوات"))}</h2><ol class="steps">{steps}</ol>{notes}{trouble}</div>'
        body = hero + f'''<section class="sec first"><div class="wrap">
  {golden_rule(c) if not data.get('roku') else ''}
  <div class="setup-layout"><div>{main}</div>{side}</div>
</div></section>'''
        return data['h1'], data['desc'], body
    return fn


# ----------------------------------------------------------------------------
# HELP
# ----------------------------------------------------------------------------
def help_page(c):
    t = c.t
    search = f'''<div class="search">{icon('search')}<input id="helpSearch" type="search" placeholder="{t(L('Search: buffering, Firestick, refund…', 'ابحث: تقطيع، فايرستيك، استرجاع…'))}" aria-label="{t(L('Search help', 'ابحث في المساعدة'))}"></div>'''
    hero = page_hero(c, [(None, t(L('Help', 'المساعدة')))],
                     t(L('Help center', 'مركز المساعدة')),
                     t(L('Quick fixes for common problems and answers to the questions we get most.', 'حلول سريعة للمشكلات الشائعة وإجابات لأكثر الأسئلة تكراراً.')),
                     extra=search)
    tr = ''.join(details(c, i, q, a, search=True) for i, q, a in TROUBLE)
    groups = f'''<div class="faq-group" data-search-group>
  <h2 class="h2">{icon('refresh')} {t(L('Troubleshooting', 'حل المشكلات'))}</h2>
  <div class="faq">{tr}</div>
</div>'''
    for g, items in FAQ:
        its = ''.join(details(c, i, q, a, search=True) for i, q, a in items)
        groups += f'<div class="faq-group" data-search-group><h2 class="h2">{t(g)}</h2><div class="faq">{its}</div></div>'
    body = hero + f'''
<section class="sec first"><div class="wrap">
  {groups}
  <p class="empty" id="helpEmpty">{t(L('No results. Try another word, or ask us on WhatsApp.', 'لا توجد نتائج. جرّب كلمة أخرى، أو اسألنا عبر واتساب.'))}</p>
</div></section>

<section class="sec first tight"><div class="wrap">
  <div class="cta">
    <div class="bars" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
    <div>
      <h2>{t(L('Still stuck?', 'ما زالت المشكلة قائمة؟'))}</h2>
      <p>{t(L('Check our WhatsApp Status for maintenance news, then send us a message with a photo of your screen.', 'تابع حالة الواتساب لأخبار الصيانة، ثم أرسل لنا رسالة مع صورة للشاشة.'))}</p>
    </div>
    <div class="cta-actions">{ext(c.wa('help'), icon('chat') + t(L('Message support', 'راسل الدعم')), 'btn btn-wa')}
      <a class="btn btn-ghost" href="{c.href('setup/index.html')}">{t(L('Setup guides', 'أدلة التثبيت'))}</a></div>
  </div>
</div></section>'''
    return (t(L('Help Center & FAQ', 'مركز المساعدة والأسئلة الشائعة')),
            t(L('Fix buffering, login and installation problems, and find answers about plans, payment, renewal and devices.',
                'حل مشكلات التقطيع وتسجيل الدخول والتثبيت، وإجابات عن الباقات والدفع والتجديد والأجهزة.')),
            body)


# ----------------------------------------------------------------------------
# ABOUT
# ----------------------------------------------------------------------------
def about(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('About', 'من نحن')))],
                     t(L('About Hossam TV', 'عن Hossam TV')),
                     t(L('A small, personal IPTV service — you talk to a real person from your first trial to every renewal.',
                         'خدمة IPTV صغيرة وشخصية — تتعامل مع شخص حقيقي من أول تجربة وحتى كل تجديد.')))
    lic = ''
    if t(LICENSE_TEXT):
        lic = f'<h2>{t(L("Licensing", "التراخيص"))}</h2><p>{t(LICENSE_TEXT)}</p>'
    regions = [L('Egypt', 'مصر'), L('Saudi Arabia', 'السعودية'), L('Kuwait', 'الكويت'), L('Qatar', 'قطر'),
               L('Bahrain', 'البحرين'), L('Oman', 'عُمان'), L('UAE', 'الإمارات'), L('Worldwide', 'باقي دول العالم')]
    body = hero + f'''
<section class="sec first"><div class="wrap split">
  <div class="prose">
    <h2>{t(L('Who we are', 'من نحن'))}</h2>
    <p>{t(L('Hossam TV is based in Egypt. We help viewers in Egypt, the Gulf and around the world watch live sports, Arabic and international channels, movies and series on the devices they already own.',
            'يقع مقر Hossam TV في مصر. نساعد المشاهدين في مصر والخليج وحول العالم على مشاهدة المباريات المباشرة والقنوات العربية والعالمية والأفلام والمسلسلات على الأجهزة التي يملكونها بالفعل.'))}</p>
    <h2>{t(L('How we work', 'كيف نعمل'))}</h2>
    <p>{t(L('Everything happens personally on WhatsApp: your free trial, payment, activation, setup help and renewals. We recommend the plan that actually fits how you watch — even when it is the cheaper one.',
            'كل شيء يتم بشكل شخصي عبر واتساب: التجربة المجانية، والدفع، والتفعيل، والمساعدة في التثبيت، والتجديد. ونرشح لك الباقة المناسبة فعلاً لطريقة مشاهدتك — حتى لو كانت الأرخص.'))}</p>
    <h2>{t(L('Our promises', 'وعودنا لك'))}</h2>
    <ul>
      <li>{t(L('<b>Try before you pay</b> — a free trial on every plan.', '<b>جرّب قبل أن تدفع</b> — تجربة مجانية لكل باقة.'))}</li>
      <li>{t(L('<b>Fast activation</b> — usually minutes, never more than 24 hours.', '<b>تفعيل سريع</b> — عادةً خلال دقائق، وبحد أقصى 24 ساعة.'))}</li>
      <li>{t(L('<b>No surprises</b> — no automatic renewals, and any app fees are listed upfront.', '<b>بدون مفاجآت</b> — لا يوجد تجديد تلقائي، وأي رسوم للتطبيقات موضحة مسبقاً.'))}</li>
      <li>{t(L('<b>Honest updates</b> — maintenance news is posted on our WhatsApp Status.', '<b>تحديثات واضحة</b> — أخبار الصيانة تُنشر على حالة الواتساب.'))}</li>
    </ul>
    {lic}
    <h2>{t(L('Where we serve', 'أين نقدم خدماتنا'))}</h2>
    <ul class="regions">{''.join('<li>' + t(r) + '</li>' for r in regions)}</ul>
  </div>
  <aside class="contact-card">
    <div class="bars" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
    <h3>{t(L('Talk to us', 'تواصل معنا'))}</h3>
    <p>{t(L('WhatsApp chat only — no calls, please. Save our number to see updates on our Status.', 'واتساب رسائل فقط — بدون مكالمات من فضلك. احفظ رقمنا لتتابع التحديثات على الحالة.'))}</p>
    <span class="num">{WHATSAPP_DISPLAY}</span>
    {ext(c.wa('sub'), icon('chat') + t(L('Message us on WhatsApp', 'راسلنا عبر واتساب')), 'btn btn-wa')}
  </aside>
</div></section>
''' + cta_block(c)
    return (t(L('About Us', 'من نحن')),
            t(L('Hossam TV is a personal IPTV service based in Egypt, serving Egypt, the Gulf and worldwide with support on WhatsApp.',
                'Hossam TV خدمة IPTV شخصية مقرها في مصر، تخدم مصر والخليج وباقي دول العالم مع دعم عبر واتساب.')),
            body)


# ----------------------------------------------------------------------------
# POLICIES
# ----------------------------------------------------------------------------
def policies(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('Policies', 'السياسات')))],
                     t(L('Terms, refunds & privacy', 'الشروط والاسترجاع والخصوصية')),
                     t(L('Written in plain language so you know exactly how things work.', 'مكتوبة بلغة بسيطة لتعرف بالضبط كيف تسير الأمور.')),
                     extra=f'<p class="updated">{t(L("Last updated:", "آخر تحديث:"))} {t(LAST_UPDATED)}</p>')
    nav = ''.join(f'<a class="btn btn-ghost btn-sm" href="#{a}">{t(lbl)}</a>' for a, lbl in [
        ('terms', L('Terms of service', 'شروط الخدمة')), ('refund', L('Refund policy', 'سياسة الاسترجاع')), ('privacy', L('Privacy policy', 'سياسة الخصوصية'))])

    if c.ar:
        prose = f'''
<h2 id="terms">شروط الخدمة</h2>
<h3>الخدمة</h3>
<p>توفر Hossam TV اشتراكات IPTV (قنوات مباشرة وأفلام ومسلسلات) تُشاهَد عبر الإنترنت، ويتم تفعيلها بشكل شخصي عبر واتساب.</p>
<h3>حسابك</h3>
<ul>
<li>يمكنك تثبيت الاشتراك على أي عدد من الأجهزة ومشاركته مع أفراد أسرتك، لكن التشغيل يكون على <b>شاشة واحدة فقط في نفس الوقت</b>.</li>
<li>التشغيل على شاشتين أو أكثر في نفس الوقت قد يؤدي إلى إيقاف الحساب.</li>
<li>لا يجوز إعادة بيع الاشتراك أو توزيعه.</li>
</ul>
<h3>التجربة المجانية</h3>
<p>تجربة مجانية واحدة لكل عميل: 12 ساعة لسيرفر XTV و24 ساعة لباقي الباقات.</p>
<h3>الدفع والتفعيل</h3>
<ul>
<li>الدفع يتم بإحدى الطرق الموضحة في <a href="{c.href('plans.html#payment')}">صفحة الباقات</a>، ثم ترسل صورة واضحة للإيصال عبر واتساب.</li>
<li>التفعيل عادةً خلال دقائق، وبحد أقصى 24 ساعة.</li>
<li>الأسعار تختلف حسب البلد وقد تتغير، والسعر الذي دفعته يسري على اشتراكك الحالي بالكامل.</li>
</ul>
<h3>التجديد</h3>
<p>الاشتراك لا يتجدد تلقائياً ولا يمكن إيقافه مؤقتاً. يمكنك تغيير الباقة عند التجديد.</p>
<h3>توفر المحتوى</h3>
<ul>
<li>القنوات والمحتوى قد تتغير، أو تتوقف مؤقتاً، أو تُحذف دون إشعار مسبق. ننشر أخبار الصيانة على حالة الواتساب كلما أمكن.</li>
<li>بعض شركات الإنترنت (مثل الإمارات) قد تحجب خدمات IPTV، وهذا خارج عن إرادتنا.</li>
</ul>
<h3>التطبيقات</h3>
<p>تطبيقات المشاهدة (مثل IBO Player و Bob Player و Smarters و SFVIP) تابعة لمطوريها، وبعضها له رسوم تفعيل خاصة موضحة في أدلة التثبيت.</p>
<h3>التعديلات</h3>
<p>قد نحدّث هذه الشروط من وقت لآخر، وأحدث نسخة موجودة دائماً في هذه الصفحة.</p>

<h2 id="refund">سياسة الاسترجاع</h2>
<ul>
<li>كل باقة تبدأ بتجربة مجانية حتى تتأكد أن الخدمة تعمل جيداً على أجهزتك وسرعة الإنترنت لديك.</li>
<li><b>لا يوجد استرجاع للمبلغ بعد تفعيل الاشتراك.</b></li>
<li>إذا دفعت ولم يتم تفعيل اشتراكك، راسلنا عبر واتساب مع صورة الإيصال وسنحل المشكلة.</li>
</ul>

<h2 id="privacy">سياسة الخصوصية</h2>
<h3>ما نجمعه</h3>
<p>عند تواصلك معنا عبر واتساب: اسمك ورقمك ورسائلك، وصور إيصالات الدفع، وبيانات الشاشة (Device ID و Device Key) إذا كنت تستخدم شاشة ذكية. ونحتفظ ببيانات الدخول التي ننشئها لك.</p>
<h3>كيف نستخدمها</h3>
<p>فقط لتفعيل اشتراكك، ومساعدتك في التثبيت والدعم، والتواصل معك بخصوص التجديد والصيانة. لا نبيع بياناتك، ولا نشاركها إلا بالقدر اللازم لتفعيل اشتراكك (مثل تسجيل بيانات شاشتك في تطبيق المشاهدة).</p>
<h3>هذا الموقع</h3>
<ul>
<li>لا يوجد تسجيل حسابات أو نماذج في الموقع.</li>
<li>يحفظ الموقع اختيارك للغة والبلد والباقة في متصفحك (localStorage) حتى يتذكرها في زيارتك القادمة.</li>
<li>مساعد المحادثة في الموقع مقدَّم من Chatbase، والرسائل التي تكتبها فيه تتم معالجتها لدى Chatbase.</li>
<li>الخطوط يتم تحميلها من Google Fonts.</li>
</ul>
<h3>اختياراتك</h3>
<p>يمكنك أن تطلب منا عبر واتساب حذف بياناتك بعد انتهاء اشتراكك.</p>
'''
    else:
        prose = f'''
<h2 id="terms">Terms of service</h2>
<h3>The service</h3>
<p>Hossam TV provides IPTV subscriptions (live channels, movies and series) watched over the internet, activated personally through WhatsApp.</p>
<h3>Your account</h3>
<ul>
<li>You can install your subscription on as many devices as you like and share it with your household, but only <b>one screen can play at a time</b>.</li>
<li>Playing on two or more screens at the same time can get the account locked.</li>
<li>You may not resell or redistribute your subscription.</li>
</ul>
<h3>Free trial</h3>
<p>One free trial per customer: 12 hours for XTV and 24 hours for every other plan.</p>
<h3>Payment & activation</h3>
<ul>
<li>Pay with one of the methods listed on the <a href="{c.href('plans.html#payment')}">Plans page</a>, then send a clear screenshot of your receipt on WhatsApp.</li>
<li>Activation usually takes a few minutes. Please allow up to 24 hours.</li>
<li>Prices depend on your country and may change. The price you paid applies to your whole current subscription.</li>
</ul>
<h3>Renewal</h3>
<p>Subscriptions don't renew automatically and can't be paused. You can switch plans when you renew.</p>
<h3>Content availability</h3>
<ul>
<li>Channels and content can change, be temporarily unavailable or be removed without notice. We post maintenance news on our WhatsApp Status whenever we can.</li>
<li>Some internet providers (for example in the UAE) may block IPTV services. This is outside our control.</li>
</ul>
<h3>Apps</h3>
<p>Player apps (such as IBO Player, Bob Player, Smarters and SFVIP) belong to their developers. Some have their own activation fees, which are listed in our setup guides.</p>
<h3>Changes</h3>
<p>We may update these terms from time to time. The latest version is always on this page.</p>

<h2 id="refund">Refund policy</h2>
<ul>
<li>Every plan starts with a free trial, so you can make sure it works well on your devices and internet connection.</li>
<li><b>There are no refunds after your subscription is activated.</b></li>
<li>If you paid and your subscription wasn't activated, message us on WhatsApp with your receipt and we'll sort it out.</li>
</ul>

<h2 id="privacy">Privacy policy</h2>
<h3>What we collect</h3>
<p>When you contact us on WhatsApp: your name, number and messages, payment receipt screenshots, and your TV's Device ID and Device Key if you use a Smart TV. We also keep the login details we create for you.</p>
<h3>How we use it</h3>
<p>Only to activate your subscription, help with setup and support, and contact you about renewals and maintenance. We don't sell your data, and we only share it as far as needed to activate your subscription (for example, registering your TV's Device ID in the player app).</p>
<h3>This website</h3>
<ul>
<li>There are no accounts or forms on this site.</li>
<li>The site saves your language, country and plan choice in your browser (localStorage) so it remembers them next time.</li>
<li>The chat assistant on this site is provided by Chatbase. Messages you type there are processed by Chatbase.</li>
<li>Fonts are loaded from Google Fonts.</li>
</ul>
<h3>Your choices</h3>
<p>You can ask us on WhatsApp to delete your data after your subscription ends.</p>
'''
    body = hero + f'''
<section class="sec first"><div class="wrap" style="max-width:820px">
  <div class="policy-nav">{nav}</div>
  <div class="prose">{prose}
    <h2>{t(L('Contact', 'التواصل'))}</h2>
    <p>{t(L('Questions about these policies? Message us on WhatsApp:', 'لديك أسئلة عن هذه السياسات؟ راسلنا عبر واتساب:'))} <a class="ltr" href="{wa()}" target="_blank" rel="noopener">{WHATSAPP_DISPLAY}</a></p>
  </div>
</div></section>'''
    return (t(L('Terms, Refund & Privacy Policy', 'الشروط وسياسة الاسترجاع والخصوصية')),
            t(L('Hossam TV terms of service, refund policy and privacy policy in plain language.', 'شروط خدمة Hossam TV وسياسة الاسترجاع والخصوصية بلغة بسيطة.')),
            body)


# ----------------------------------------------------------------------------
# registry: (key, path inside language folder, nav section, builder)
# ----------------------------------------------------------------------------
PAGE_BUILDERS = [
    ('home', 'index.html', 'home', home),
    ('plans', 'plans.html', 'plans', plans),
    ('channels', 'channels.html', 'channels', channels),
    ('setup', 'setup/index.html', 'setup', setup_index),
    ('help', 'help.html', 'help', help_page),
    ('about', 'about.html', 'about', about),
    ('policies', 'policies.html', None, policies),
]
DEVICE_PAGES = [('setup-' + d['slug'], 'setup/' + d['slug'] + '.html', 'setup', device_page(d['slug'])) for d in DEVICES]
