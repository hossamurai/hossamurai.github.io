# -*- coding: utf-8 -*-
"""Page bodies for every page. Shared data lives in content.py."""
import os
import urllib.parse
from themecss import theme_css
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


def html_attr_json(o):
    import json, html
    return html.escape(json.dumps(o, ensure_ascii=False), quote=True)


def _apply_bot_prices():
    """Prices are set in ONE place: the admin bot's price entries (n8n site-data → assets/data/bot.json, every 6 hours).
    They replace the numbers in content.py REGIONS (the fallback) for the plan cards, the order form and every page."""
    import json, os
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'assets', 'data', 'bot.json'), encoding='utf-8') as f:
            prices = json.load(f).get('prices') or {}
    except Exception:
        return
    for r in REGIONS:
        for rp in r['plans']:
            v = prices.get(rp['id']) or {}
            # XTV / Marvel are in EGP, Basic / Premium in USD everywhere — the bot's numbers use the same currencies
            if v.get('y1'):
                rp['p1'] = v['y1']
            if v.get('y2') and rp.get('p2'):
                rp['p2'] = v['y2']


_apply_bot_prices()


def ld_json(o):
    """schema.org data for Google (rich results); '</' escaped so it can't close the script tag."""
    import json, re
    return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def _plain(x):
    import re, html
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x))).strip()


def money(c, cur, n):
    cc = CURRENCY[cur]
    return f'{cc[c.lang]}{n}' if cc.get('pre') else f'{n} {cc[c.lang]}'


def poster_wall(n=40):
    """Faint wall of made-up 'poster' tiles behind page tops (pure CSS art — no real, copyrighted posters)."""
    return '<div class="poster-wall" aria-hidden="true">' + '<i></i>' * n + '</div>'


def page_hero(c, crumbs, h1, lead, actions='', extra=''):
    items = [(c.href('index.html'), c.t(L('Home', 'الرئيسية')))] + crumbs
    cr = ''.join(
        f'<li><a href="{h}">{lbl}</a></li>' if h else f'<li aria-current="page">{lbl}</li>' for h, lbl in items)
    return f'''<section class="page-hero">{poster_wall(30)}<div class="wrap">
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
    return trial_link(c, icon('chat') + (label or c.t(L('Get a free trial', 'اطلب تجربة مجانية'))), cls)


def trial_link(c, inner, cls='', plan=''):
    """Opens the free-trial form (trial_dialog). Without JavaScript it falls back to WhatsApp."""
    return (f'<a{cls_attr(cls) if cls else ""} href="{c.wa("trial")}" target="_blank" rel="noopener" data-trial'
            f'{f" data-plan={chr(34)}{plan}{chr(34)}" if plan else ""}>{inner}</a>')


# the chosen country's currency, for the order form's approximate total ("≈ 48 CAD")
DIAL_CUR = {'ca': 'CAD', '20': 'EGP', '966': 'SAR', '965': 'KWD', '974': 'QAR', '973': 'BHD', '968': 'OMR', '962': 'JOD', '964': 'IQD',
            '218': 'LYD', '216': 'TND', '213': 'DZD', '212': 'MAD', '90': 'TRY', '44': 'GBP', '49': 'EUR', '33': 'EUR', '31': 'EUR', '32': 'EUR',
            '41': 'CHF', '43': 'EUR', '46': 'SEK', '47': 'NOK', '45': 'DKK', '39': 'EUR', '34': 'EUR', '353': 'EUR', '61': 'AUD'}
# devices for the trial form -> keys the n8n site-order webhook accepts
TRIAL_DEVICES = [('android-tv', 'androidtv'), ('firestick', 'firestick'), ('smart-tv', 'smarttv'),
                 ('android', 'android'), ('apple', 'apple'), ('windows', 'windows')]


def order_link(c, kind, inner, cls='', plan='', user=''):
    """Opens the order form in subscribe or renew mode (order_dialog). Without JavaScript it falls back to WhatsApp."""
    extra = (f' data-plan="{plan}"' if plan else '') + (f' data-user="{user}"' if user else '')
    return f'<a{cls_attr(cls) if cls else ""} href="{c.wa("sub")}" target="_blank" rel="noopener" data-order="{kind}"{extra}>{inner}</a>'


def trial_dialog(c):
    """One form for free trial, subscribe and renew. Trial asks for the device; subscribe/renew ask how they'll pay
    (renew also asks the username); trial/subscribe ask for the device; renew asks for the server and how long (with the price). Sends the choices to n8n (site-order) and opens WhatsApp with them filled in."""
    t = c.t
    countries = [('ca', L('Canada', 'كندا')), ('us', L('USA', 'أمريكا'))] + [x for x in REMIND_CC if x[0] != '1']
    def region(cc):
        return 'eg' if cc == '20' else 'intl'
    copts = ''.join(f'<option value="{cc}" data-region="{region(cc)}" data-cur="{DIAL_CUR.get(cc, "")}" data-alt="{nm["en"] if c.ar else nm["ar"]}">{t(nm)}</option>' for cc, nm in countries)
    copts += f'<option value="other" data-region="intl">{t(L("Other country", "دولة أخرى"))}</option>'
    popts = ''.join(f'<option value="{pid}"{" data-eg" if PLANS[pid]["egypt_only"] else ""}>{t(PLANS[pid]["name"])}</option>' for pid in PLAN_ORDER)
    devs = {d['slug']: d for d in DEVICES}
    # the form groups every TV that uses the paid TV app (IBO / Bob Player): Samsung, LG, Vidaa and Apple TV
    form_name = {'smart-tv': L('Samsung, LG, Vidaa or Apple TV', 'سامسونج أو LG أو Vidaa أو Apple TV'), 'apple': L('iPhone, iPad or Mac', 'آيفون أو آيباد أو ماك')}
    dopts = ''.join(f'<option value="{key}" data-guide="{c.href("setup/" + slug + ".html")}">{t(form_name.get(slug, devs[slug]["name"]))}</option>' for slug, key in TRIAL_DEVICES)
    dopts += f'<option value="other" data-guide="{c.href("setup/index.html")}">{t(L("Other / not sure", "جهاز آخر / لست متأكداً"))}</option>'
    payopts = ''.join(f'<option value="{k}" data-note="{t(note)}"{" data-eg" if eg else ""}{" data-intl" if intl else ""}>{t(nm)}</option>'
                      for k, nm, note, eg, intl in PAY_FORM)
    pick = t(L('Choose…', 'اختر…'))
    # renewal periods + prices per region and plan, from REGIONS (same numbers as the plan cards)
    per_lbl = {'y1': L('1 year', 'سنة'), 'y2': L('2 years', 'سنتين'), 'm12': L('12 months', '12 شهراً'), 'm3': L('3 months', '3 أشهر')}
    prices = {}
    for r in REGIONS:
        for rp in r['plans']:
            opts = [[rp['per'], t(per_lbl[rp['per']]), money(c, rp['cur'], rp['p1']), rp['p1'], rp['cur']]]
            if rp.get('p2'):
                opts.append(['y2', t(per_lbl['y2']), money(c, rp['cur'], rp['p2']), rp['p2'], rp['cur']])
            prices.setdefault(r['id'], {})[rp['id']] = opts
    prices_attr = html_attr_json(prices)
    fees_attr = html_attr_json(dict({pid: [cur, y1, life] for pid, (cur, y1, life) in APP_FEE.items()}, eg=list(APP_FEE_EGYPT)))
    # price per plan and region for the total: 1 screen-year = p1; 2 or more = each at half the 2-year price (Basic 60, 90, 120…)
    units_attr = html_attr_json({r['id']: {rp['id']: [rp['cur'], rp['p1'], rp.get('p2') or rp['p1'] * 2] for rp in r['plans']} for r in REGIONS})
    cur_attr = html_attr_json({k: [v['en'] if not c.ar else v['ar'], bool(v.get('pre'))] for k, v in CURRENCY.items()})
    return f'''<dialog class="trial-dlg" id="trialDlg" aria-labelledby="trialTitle">
  <form class="remind trial-form" method="dialog" data-trial-form data-mode="trial" data-api="{N8N_WEBHOOK}site-order" data-wa="{WHATSAPP}" novalidate>
    <button type="button" class="trial-x" data-trial-close aria-label="{t(L('Close', 'إغلاق'))}">{icon('x')}</button>
    <h3 id="trialTitle">
      <span data-for="trial">{icon('clock')}{t(L('Free trial', 'تجربة مجانية'))}</span>
      <span data-for="subscribe">{icon('card')}{t(L('Subscribe', 'اشترك'))}</span>
      <span data-for="renew">{icon('refresh')}{t(L('Renew', 'جدّد اشتراكك'))}</span>
    </h3>
    <p data-for="subscribe renew">{t(L("We'll reply with the payment details.", 'سنرد عليك بتفاصيل الدفع.'))}</p>
    <div class="rf-grid">
      <div class="rf rf-full" data-for="renew"><label for="trUser">{t(L('Username', 'اسم المستخدم'))}</label><input id="trUser" name="username" type="text" maxlength="64" autocomplete="username" autocapitalize="none" spellcheck="false" dir="ltr"></div>
      <div class="rf rf-full"><label for="trName">{t(L('Name', 'الاسم'))}</label><input id="trName" name="name" type="text" maxlength="40" autocomplete="name" required></div>
      <div class="rf"><label for="trCountry">{t(L('Country', 'الدولة'))}</label><div class="cbox" data-cbox><input id="trCountry" type="text" autocomplete="off" autocapitalize="none" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="trCountryList" aria-autocomplete="list" placeholder="{t(L('Type your country', 'اكتب اسم بلدك'))}"><ul class="cbox-list" id="trCountryList" role="listbox" hidden></ul><select name="country" tabindex="-1" aria-hidden="true" hidden required><option value="">{pick}</option>{copts}</select></div></div>
      <div class="rf"><label for="trPlan"><span data-for="trial subscribe">{t(L('Plan', 'الباقة'))}</span><span data-for="renew">{t(L('Server', 'السيرفر'))}</span></label><select id="trPlan" name="plan" required><option value="">{pick}</option>{popts}</select></div>
      <div class="rf rf-full" data-for="trial subscribe"><label for="trPhone">{t(L('WhatsApp number', 'رقم الواتساب'))}</label><div class="tr-phone" dir="ltr"><span class="tr-cc" data-tr-cc>+</span><input id="trPhone" name="phone" type="tel" inputmode="tel" autocomplete="tel-national" maxlength="20" placeholder="{t(L('Number', 'الرقم'))}"></div></div>
      <div class="rf rf-full" data-for="subscribe renew"><label for="trPeriod"><span data-for="renew">{t(L('Renew for', 'مدة التجديد'))}</span><span data-for="subscribe">{t(L('Subscribe for', 'مدة الاشتراك'))}</span></label><select id="trPeriod" name="period" data-prices="{prices_attr}"><option value="">{pick}</option></select></div>
      <div class="rf rf-full"><label for="trScreens">{t(L('How many accounts?', 'كم حساب؟'))}</label><input id="trScreens" name="screens" type="number" inputmode="numeric" min="1" max="5" value="1"><small class="rf-hint">{t(L('Each account plays on one screen at a time.', 'كل حساب يعمل على شاشة واحدة في نفس الوقت.'))}</small></div>
      <div class="rf rf-full" data-for="trial subscribe"><label for="trDevs">{t(L('How many devices?', 'كم جهاز؟'))}</label><input id="trDevs" name="devs" type="number" inputmode="numeric" min="1" max="6" value="1"></div>
      <div class="rf rf-full tr-devs" data-for="trial subscribe" data-devs data-l-dev="{t(L('Device {n}', 'الجهاز {n}'))}" data-l-one="{t(L('Device', 'الجهاز'))}" data-l-many="{t(L('Your devices', 'أجهزتك'))}"><label for="trDevice" data-dev-lbl>{t(L('Device', 'الجهاز'))}</label><select id="trDevice" name="device"><option value="">{pick}</option>{dopts}</select></div>
      <div class="rf rf-full" data-for="trial subscribe" data-golden hidden><p class="tr-golden">{icon('info')}<span data-golden-txt><b>{t(L('Golden rule: one screen at a time.', 'القاعدة الذهبية: شاشة واحدة في نفس الوقت.'))}</b> {t(L('Install on as many devices as you like, but only one can play at once — watching on two at the same time can lock the account.', 'ثبّت الاشتراك على أي عدد من الأجهزة، لكن التشغيل على جهاز واحد فقط في نفس الوقت — التشغيل على جهازين معاً قد يوقف الحساب.'))}</span></p></div>
      <div class="rf rf-full" data-for="subscribe renew"><label for="trPay">{t(L('How will you pay?', 'طريقة الدفع'))}</label><select id="trPay" name="pay"><option value="">{pick}</option>{payopts}</select><small class="pay-note" data-pay-note hidden></small></div>
    </div>
    <div class="tr-total" data-total data-fees="{fees_attr}" data-units="{units_attr}" data-cur="{cur_attr}"
      data-l-total="{t(L('Approximate total', 'الإجمالي التقريبي'))}" data-l-after="{t(L('If you subscribe after the trial', 'لو اشتركت بعد التجربة'))}"
      data-l-acc="{t(L('{n} account', 'حساب واحد'))}" data-l-accs="{t(L('{n} accounts', '{n} حسابات'))}" data-l-yr="{t(L('1 year', 'سنة'))}" data-l-yrs="{t(L('{n} years', '{n} سنوات'))}"
      data-l-tv="{t(L('TV app', 'تطبيق الشاشة'))}" data-l-tv1="{t(L('1 year', 'سنة'))}" data-l-tvl="{t(L('lifetime', 'مدى الحياة'))}"
      data-l-sum="{t(L('Total', 'الإجمالي'))}" data-l-note="{t(L('The TV app is charged per TV. Hossam confirms the final amount on WhatsApp.', 'تطبيق الشاشة يُحسب لكل شاشة. حسام يؤكد المبلغ النهائي على واتساب.'))}" hidden></div>
    <p class="trial-note" data-for="trial subscribe">{icon('info')}<span>{t(L('Install the app first so everything is ready:', 'ثبّت التطبيق أولاً ليكون كل شيء جاهزاً:'))} <a data-trial-guide href="{c.href('setup/index.html')}">{t(L('Setup guide', 'دليل التثبيت'))}</a></span></p>
    <input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
    <p class="remind-msg" role="status" hidden data-msg-empty="{t(L('Please fill in all the fields.', 'من فضلك املأ كل الحقول.'))}" data-msg-phone="{t(L('Check the WhatsApp number.', 'راجع رقم الواتساب.'))}"></p>
    <button type="submit" class="btn btn-wa">{icon('chat')}<span>{t(L('Send on WhatsApp', 'أرسل عبر واتساب'))}</span></button>
  </form>
</dialog>'''


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
    </div>
  </div>
</div></section>'''


def note(kind, lbl, html, img=''):
    body = f'<span class="lbl">{lbl}</span>{html}'
    if img:
        body = f'{img}<div>{body}</div>'
    return f'<div class="note{" warn" if kind == "warn" else ""}{" has-app" if img else ""}">{body}</div>'


def app_img(c, key, size=40):
    src, name = APP_ICONS[key]
    return f'<img class="app-ic" src="{c.root}{src}" alt="{name}" width="{size}" height="{size}" loading="lazy">'


def need_list(c, keys):
    or_ = c.t(L('or', 'أو'))
    items = f'<li class="or">{or_}</li>'.join(f'<li>{app_img(c, k, 30)}{APP_ICONS[k][1]}</li>' for k in keys)
    return f'<div class="need-wrap"><span class="need-lbl">{c.t(L("App you need", "التطبيق المطلوب"))}</span><ul class="need">{items}</ul></div>'


# ----------------------------------------------------------------------------
# plans
# ----------------------------------------------------------------------------
def aka_text(c, pid):
    p = PLANS[pid]
    if not p.get('aka'):
        return ''
    return ('تُعرف أيضاً باسم ' if c.ar else 'Also known as ') + c.t(p['aka'])


def plan_card(c, region, rp):
    """Airbnb-style card: a soft picture area with the logo and badges, then a title, two grey lines and the price."""
    t, p, pid = c.t, PLANS[rp['id']], rp['id']
    nm, rl = t(p['name']), t(region['label'])
    badges = ''
    if rp.get('badge'):
        badges += f'<span class="pill">{t(rp["badge"])}</span>'
    if p['egypt_only']:
        badges += f'<span class="pill pill-soft">{t(L("Egypt only", "مصر فقط"))}</span>'
    p2 = ''
    if rp.get('p2'):
        m = money(c, rp['cur'], rp['p2'])
        if rp['cur'] == 'usd':
            m += f'<span class="cad" data-cad="{rp["p2"]}" data-cad-short hidden></span>'
        p2 = f'<span class="p2">{m} لسنتين</span>' if c.ar else f'<span class="p2">{m} for 2 years</span>'   # its own line under the yearly price
    aka = c.t(p['aka']) if p.get('aka') else ''
    first = t(p['feat'][0][1])
    stats = ' · '.join(f'{v} {t(lbl)}' for v, lbl in p['stats'])
    logo = (f'<img class="plan-logo" src="{c.root}{p["img"]}" alt="" width="64" height="64" loading="lazy" '
            f'onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'grid\'">'
            f'<span class="plan-mono" style="display:none">{p["mono"]}</span>')
    trial = f'تجربة مجانية {p["trial"]} ساعة' if c.ar else f'{p["trial"]}h free trial'
    cad1 = f'<span class="cad" data-cad="{rp["p1"]}" hidden></span>' if rp['cur'] == 'usd' else ''  # filled for visitors in Canada
    return f'''<article class="pcard{" featured" if rp.get("featured") else ""}" style="--c:{p["color"]}">
  <div class="plan-body">
    <div class="badges">{badges}</div>
    <div class="plan-head">{logo}<div><h3>{nm}</h3>{('<span class="aka">' + aka + '</span>') if aka else ''}</div>{trial_link(c, icon('clock') + trial, 'plan-trial', pid)}</div>
    <p class="plan-line">{first}</p>
    <p class="plan-line ltr-nums">{stats}</p>
    <p class="plan-price"><b>{money(c, rp["cur"], rp["p1"])}</b>{cad1} {t(PERIOD[rp["per"]])} {p2}</p>
    <div class="plan-actions">
      {order_link(c, 'subscribe', icon('chat') + t(L('Subscribe', 'اشترك')), 'btn btn-wa', pid)}
    </div>
    <a class="plan-setup" data-setup-link href="{c.href('setup/index.html')}">{t(L('Setup guide', 'دليل التثبيت'))}{icon('arrow', 'flip')}</a>
  </div>
</article>'''


def region_block(c):
    t = c.t
    default = 'intl'   # most customers are in Canada -> start on 'Canada & worldwide' (the script still picks Egypt by location)
    seg = ''.join(
        f'<button type="button" data-region-btn="{r["id"]}" aria-pressed="{"true" if r["id"] == default else "false"}">{t(r["label"])}</button>'
        for r in REGIONS)
    panels = ''
    for r in REGIONS:
        nt = f'<div class="region-note">{icon("info")}<span>{t(r["note"])}</span></div>' if r['note'] else ''
        cards = ''.join(plan_card(c, r, rp) for rp in r['plans'])
        panels += f'<div data-region-panel="{r["id"]}"{"" if r["id"] == default else " hidden"}>{nt}<div class="plans pgrid">{cards}</div></div>'
    ae = f'<div class="region-note" data-ae-note hidden>{icon("info")}<span>{t(L("We no longer serve the UAE.", "لم نعد نقدم الخدمة في الإمارات."))}</span></div>'
    return f'''{ae}<div class="region">
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
    return (c.t(a).replace('{channels}', f'<a href="{c.href("channels.html")}">{c.t(L("Channels", "القنوات"))}</a>')
            .replace('{reminders}', f'<a href="{c.href("help.html#reminders")}">{c.t(L("Renewal reminders", "تنبيهات التجديد"))}</a>')
            .replace('{speedtest}', f'<a href="{c.href("speed-test.html")}">{c.t(L("our speed test", "اختبار السرعة"))}</a>'))


def reminder_card(c, compact=False):
    """Renewal reminders: the customer enters username + password + WhatsApp number (always all three,
    because usernames repeat). The form posts to the n8n 'site-link' webhook, which checks the Customers
    table and saves the number there. Nothing is stored on the website."""
    t = c.t
    head = '' if compact else f'''<h3>{icon('clock')}{t(L('Renewal reminders', 'تنبيهات التجديد'))}</h3>
  <p>{t(L("Link an account to a WhatsApp number and we'll message that number before the subscription ends. You can add a friend's account on their number too.",
          'اربط الحساب برقم واتساب وسنراسل هذا الرقم قبل انتهاء الاشتراك. يمكنك أيضاً إضافة حساب صديق على رقمه.'))}</p>'''
    week = (L('New subscription or renewal? It can take up to a week before you can link it.', 'اشتراك جديد أو تجديد؟ قد يستغرق حتى أسبوع قبل أن تتمكن من ربطه.') if compact else
            L("Just subscribed or renewed? It can take up to a week before you can link it — we add new accounts and renewals to our list once a week.",
              "اشتركت أو جدّدت حديثاً؟ قد يستغرق الأمر حتى أسبوع قبل أن تتمكن من ربط الحساب — نضيف الحسابات الجديدة والتجديدات لقائمتنا مرة كل أسبوع."))
    fine = (L('The password is needed because some usernames are shared. Nothing is stored on this website.', 'نحتاج كلمة المرور لأن بعض أسماء المستخدمين تتكرر. لا يُحفظ أي شيء على هذا الموقع.') if compact else
            L(f'We need the password because some usernames are shared by more than one account. Your details are checked by our system and are not stored on this website. Prefer WhatsApp? Message our bot: <a href="https://wa.me/{BOT_WHATSAPP}" target="_blank" rel="noopener">{BOT_WHATSAPP_DISPLAY}</a>.',
              f'نحتاج كلمة المرور لأن بعض أسماء المستخدمين تتكرر لأكثر من حساب. يتم التحقق من بياناتك عبر نظامنا ولا تُحفظ على هذا الموقع. تفضّل الواتساب؟ راسل البوت: <a href="https://wa.me/{BOT_WHATSAPP}" target="_blank" rel="noopener"><bdi dir="ltr">{BOT_WHATSAPP_DISPLAY}</bdi></a>.'))
    return f'''<form class="remind{' remind-compact' if compact else ''}" id="reminders" data-remind data-api="{N8N_WEBHOOK}site-link" data-bot="{BOT_WHATSAPP}" novalidate>
  {head}
  <div class="rf-grid">
  <div class="rf">
  <label for="remindUser">{t(L('Username', 'اسم المستخدم'))}</label>
  <input id="remindUser" name="username" type="text" dir="ltr" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" maxlength="64" placeholder="{t(L('e.g. ahmed123', 'مثال: ahmed123'))}">
  </div>
  <div class="rf">
  <label for="remindPass">{t(L('Password', 'كلمة المرور'))}</label>
  <div class="remind-pass" dir="ltr">
    <input id="remindPass" name="password" type="password" dir="ltr" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" maxlength="64">
    <button type="button" class="remind-show" aria-pressed="false" data-show="{t(L('Show', 'إظهار'))}" data-hide="{t(L('Hide', 'إخفاء'))}">{t(L('Show', 'إظهار'))}</button>
  </div>
  </div>
  <div class="rf rf-phone">
  <label for="remindPhone">{t(L('WhatsApp number for reminders', 'رقم الواتساب للتنبيهات'))}</label>
  <div class="phone-row" dir="ltr">
    <label class="cc-wrap"><span class="cc-show" aria-hidden="true">+20</span><select name="cc" aria-label="{t(L('Country code', 'كود الدولة'))}">{''.join(f'<option value="{cc}"{" selected" if cc == "20" else ""}>+{cc} {t(nm)}</option>' for cc, nm in REMIND_CC)}</select></label>
    <input id="remindPhone" name="phone" type="tel" dir="ltr" inputmode="tel" autocomplete="tel-national" maxlength="20" placeholder="{t(L('Number', 'الرقم'))}">
  </div>
  </div>
  <button type="submit" class="btn btn-wa">{icon('check')}<span>{t(L('Link account', 'اربط الحساب'))}</span></button>
  </div>
  <input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
  <p class="remind-msg" role="status" hidden data-msg-empty="{t(L('Fill in the username, password and WhatsApp number.', 'اكتب اسم المستخدم وكلمة المرور ورقم الواتساب.'))}" data-msg-phone="{t(L('Check the WhatsApp number — include the country code, e.g. +971 50 123 4567.', 'راجع رقم الواتساب — اكتب كود الدولة، مثال: 971501234567+.'))}" data-msg-not_found="{t(L("The username and password don't match an account. Check the picture we sent after payment and type both exactly. If you subscribed or renewed in the last week, try again in a few days.", 'اسم المستخدم وكلمة المرور لا يطابقان أي حساب. راجع الصورة التي أرسلناها بعد الدفع واكتبهما بالضبط. لو اشتركت أو جدّدت خلال الأسبوع الماضي، حاول مرة أخرى بعد أيام.'))}" data-msg-limited="{t(L('Too many tries today. Please try again tomorrow, or message our bot on WhatsApp.', 'محاولات كثيرة اليوم. حاول غداً، أو راسل البوت على واتساب.'))}" data-msg-error="{t(L("Couldn't connect right now. Try again in a minute, or message our bot on WhatsApp.", 'تعذّر الاتصال الآن. حاول بعد دقيقة، أو راسل البوت على واتساب.'))}" data-msg-linked="{t(L("Linked ✅ We'll send a WhatsApp reminder to that number before it expires. A confirmation message is on its way.", 'تم الربط ✅ سنرسل تذكيراً على هذا الرقم قبل انتهاء الاشتراك. ستصلك رسالة تأكيد على الواتساب.'))}"></p>
  <p class="remind-week">{icon('clock')}<span>{t(week)}</span></p>
  <small>{t(fine)}</small>
</form>'''


def details(c, iid, q, a, search=False):
    s = ' data-search-item' if search else ''
    if search and isinstance(q, dict):
        # the other language's words too, so "firestick" also finds the Arabic answer (and the other way round)
        import re, html as _h
        o = 'en' if c.ar else 'ar'
        k = re.sub(r'<[^>]+>|\{[a-z]+\}', ' ', (q.get(o) or '') + ' ' + ((a.get(o) or '') if isinstance(a, dict) else ''))
        s += f' data-k="{_h.escape(" ".join(k.split()), quote=True)}"'
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
<div class="pay-renew">{order_link(c, 'renew', icon('refresh') + t(L('Renew my subscription', 'جدّد اشتراكي')), 'btn btn-wa')}</div>
<div class="pay-foot">{icon('receipt')}<span>{t(L("After paying, send a <b>clear screenshot of the receipt</b> on WhatsApp. Subscriptions don't renew automatically — just message us when it's time.", 'بعد الدفع، أرسل <b>صورة واضحة للإيصال</b> عبر واتساب. الاشتراك لا يتجدد تلقائياً — راسلنا عند موعد التجديد.'))}</span></div>'''


# ----------------------------------------------------------------------------
# HOME
# ----------------------------------------------------------------------------
def home(c):
    t = c.t
    hero = f'''<section class="hero hero-apple">{poster_wall(40)}<div class="wrap">
    <h1>{t(L('Sports. Movies. Series. <span class="grad">Anywhere.</span>', 'رياضة. أفلام. مسلسلات. <span class="grad">في أي مكان.</span>'))}</h1>
    <p class="lead">{t(L('Live sports, Arabic and international channels and movies — up to 4K.', 'مباريات مباشرة وقنوات عربية وعالمية وأفلام — بجودة حتى 4K.'))}</p>
    <div class="hero-cta">
      {btn_trial(c)}
    </div>
    {status_line(c)}
  </div>
</section>'''

    # Reviews: real reviews from customers. The form sends them to n8n (site-review) as pending;
    # only reviews Hossam approves come back through site-data and are shown here.
    rv = ''.join(
        f'<figure class="review"><div class="rev-stars" aria-label="5/5">★★★★★</div><blockquote>“{t(r["quote"])}”</blockquote><figcaption>{r["name"]} · {t(r["place"])}</figcaption></figure>'
        for r in REVIEWS)
    star_btns = ''.join(f'<button type="button" class="star" data-star="{i}" aria-label="{i}/5">★</button>' for i in range(1, 6))
    reviews = f'''<section class="sec" id="reviews"><div class="wrap">
  {sec_head('', t(L('Reviews', 'آراء العملاء')), t(L('What customers say', 'ماذا يقول عملاؤنا')))}
  <p class="rev-rating" data-rating hidden></p>
  <div class="reviews" data-reviews>{rv}</div>
  <p class="rev-empty" data-rev-empty{' hidden' if REVIEWS else ''}>{t(L('No reviews yet — be the first to share yours.', 'لا توجد آراء بعد — كن أول من يشاركنا رأيه.'))}</p>
  <button type="button" class="btn btn-ghost rev-open" data-rev-open aria-expanded="false" aria-controls="reviewForm">{icon('chat')}{t(L('Write a review', 'اكتب رأيك'))}</button>
  <form class="remind rev-form" id="reviewForm" data-review data-api="{N8N_WEBHOOK}site-review" novalidate hidden>
    <label>{t(L('Your rating', 'تقييمك'))}</label>
    <div class="stars" role="radiogroup" aria-label="{t(L('Your rating', 'تقييمك'))}" dir="ltr">{star_btns}</div>
    <input type="hidden" name="stars" value="5">
    <label for="revName">{t(L('Name', 'الاسم'))}</label>
    <input id="revName" name="name" type="text" maxlength="30" autocomplete="given-name" style="font-family:inherit">
    <label for="revPlace">{t(L('City or country (optional)', 'المدينة أو الدولة (اختياري)'))}</label>
    <input id="revPlace" name="place" type="text" maxlength="30" style="font-family:inherit">
    <label for="revText">{t(L('Your review', 'رأيك'))}</label>
    <textarea id="revText" name="text" rows="4" maxlength="400"></textarea>
    <input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
    <p class="remind-msg" role="status" hidden data-msg-empty="{t(L('Please add your name and a few words (at least 10 letters).', 'من فضلك اكتب اسمك وبضع كلمات (10 حروف على الأقل).'))}" data-msg-received="{t(L("Thank you! Your review will appear after a quick check.", 'شكراً لك! سيظهر رأيك بعد مراجعة سريعة.'))}" data-msg-limited="{t(L('Thanks — we already got your review today.', 'شكراً — وصلنا رأيك اليوم بالفعل.'))}" data-msg-error="{t(L("Couldn't send right now. Please try again in a minute.", 'تعذّر الإرسال الآن. حاول بعد دقيقة.'))}"></p>
    <button type="submit" class="btn btn-wa">{icon('check')}<span>{t(L('Send review', 'أرسل رأيك'))}</span></button>
    <small>{t(L('Reviews are checked before they appear. Only your name and city are shown.', 'تتم مراجعة الآراء قبل نشرها. يظهر اسمك ومدينتك فقط.'))}</small>
  </form>
</div></section>'''

    fq = all_faq()
    teaser = ''.join(details(c, i, *fq[i]) for i in ['free-trial', 'which-plan', 'multi-device', 'activation'])

    body = hero + f'''
{ramadan_teaser(c)}
<section class="sec" id="plans"><div class="wrap">
  {sec_head('', t(L('Plans', 'الباقات')), t(L('Pick your plan', 'اختر باقتك')))}
  {region_block(c)}
  <div class="more-link"><a class="link-arrow" href="{c.href('plans.html#compare')}">{t(L('Compare all plans', 'قارن بين الباقات'))}{icon('arrow', 'flip')}</a></div>
</div></section>


<section class="sec" id="reminders-sec"><div class="wrap">
  {sec_head('', t(L('Your subscription', 'اشتراكك')), t(L('Reminders & expiry check', 'التنبيهات وتاريخ الانتهاء')))}
  <div class="duo-box">
    <div class="duo-col"><div class="remind acct-form duo-title"><h3>{icon('clock')}{t(L('Renewal reminders', 'تنبيهات التجديد'))}</h3></div>{reminder_card(c, compact=True)}</div>
    <div class="duo-col">{account_card(c, compact=True)}</div>
  </div>
</div></section>
{reviews}


'''
    body += ld_json({'@context': 'https://schema.org', '@graph': [
        {'@type': 'Organization', '@id': BASE_URL + '/#org', 'name': SITE_NAME, 'url': BASE_URL + '/', 'logo': BASE_URL + '/assets/img/logo-180.png',
         'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer support', 'telephone': '+' + WHATSAPP, 'availableLanguage': ['English', 'Arabic']},
         'areaServed': ['CA', 'US', 'GB', 'EG', 'SA', 'AE']},
        {'@type': 'WebSite', '@id': BASE_URL + '/#site', 'name': SITE_NAME, 'url': BASE_URL + '/', 'inLanguage': c.lang, 'publisher': {'@id': BASE_URL + '/#org'}}]})
    return (t(L('Hossam TV — Arabic TV, Live Football & Movies in Canada, the USA & Worldwide', 'Hossam TV — قنوات عربية ومباريات وأفلام في كندا وأمريكا وحول العالم')),
            t(L('Arabic channels, live football, movies and series on any screen, up to 4K — for viewers in Canada, the USA, Egypt, the Gulf and worldwide. Free trial on WhatsApp.',
                'قنوات عربية ومباريات مباشرة وأفلام ومسلسلات على أي شاشة بجودة حتى 4K — للمشاهدين في كندا وأمريكا ومصر والخليج وحول العالم. تجربة مجانية عبر واتساب.')),
            body)


# ----------------------------------------------------------------------------
# PLANS
# ----------------------------------------------------------------------------
def savings_block(c):
    """Savings calculator: cable/satellite bill per month vs Hossam TV Basic per year (filled by site.js; CAD for visitors in Canada)."""
    t = c.t
    basic = next(rp['p1'] for rg in REGIONS if rg['id'] == 'intl' for rp in rg['plans'] if rp['id'] == 'basic')
    return f'''<div class="calc" data-savings data-basic="{basic}">
  <h2>{t(L('How much could you save?', 'كم ممكن توفّر؟'))}</h2>
  <label for="billRange">{t(L('Your cable or satellite bill per month', 'فاتورة الكابل أو الدش شهرياً'))} <b dir="ltr" data-bill>$70</b></label>
  <input id="billRange" type="range" min="20" max="500" step="10" value="90" data-bill-range>
  <div class="calc-out"><b dir="ltr" data-save>$805</b><span>{t(L('saved every year', 'توفير كل سنة'))}</span></div>
  <p class="calc-note" data-calc-note data-l="{t(L('You pay {y} a year now. Hossam TV Basic: {b} a year.', 'بتدفع حالياً {y} في السنة. باقة Hossam TV الأساسية: {b} في السنة.'))}"></p>
  {btn_trial(c)}
</div>'''


def plans(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('Plans', 'الباقات')))],
                     t(L('Plans & prices', 'الباقات والأسعار')),
                     t(L('Prices depend on your country. Every plan starts with a free trial.', 'الأسعار تختلف حسب بلدك. كل باقة تبدأ بتجربة مجانية.')))

    fit = [
        ('xtv', L('Football in Egypt, watching with family', 'كرة القدم في مصر مع العائلة')),
        ('marvel', L('Movies & series in Egypt', 'الأفلام والمسلسلات في مصر')),
        ('basic', L('Arabic channels & football, anywhere', 'القنوات العربية والكرة، في أي دولة')),
        ('premium', L('Everything: all sports, 4K, biggest library', 'كل شيء: كل الرياضات، 4K، أكبر مكتبة')),
    ]
    fit_html = ''.join(
        f'<a href="{c.wa("trial", plan=t(PLANS[pid]["name"]))}" target="_blank" rel="noopener" data-trial data-plan="{pid}" style="--c:{PLANS[pid]["color"]}"><span class="q">{t(q)}</span><b>{t(PLANS[pid]["name"])} {icon("arrow", "flip")}</b></a>'
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


    body = hero + f'''
<section class="sec first"><div class="wrap">{region_block(c)}</div></section>

<section class="sec"><div class="wrap">{savings_block(c)}</div></section>

<section class="sec"><div class="wrap">
  {sec_head('', t(L('Quick guide', 'دليل سريع')), t(L('Which plan fits you?', 'أي باقة تناسبك؟')), t(L('Tap one to request a free trial of that plan.', 'اضغط على أي منها لطلب تجربة مجانية لهذه الباقة.')))}
  <div class="fit">{fit_html}</div>
</div></section>

<section class="sec" id="compare"><div class="wrap">
  {sec_head('', t(L('Compare', 'مقارنة')), t(L('All plans side by side', 'كل الباقات جنباً إلى جنب')))}
  <p class="swipe-hint">{t(L('Swipe to see all plans', 'اسحب لرؤية كل الباقات'))} {icon('arrow', 'flip')}</p>
  <div class="table-wrap"><table class="cmp"><thead><tr><th scope="col"><span class="sr-only"></span></th>{head}</tr></thead><tbody>{rows}</tbody></table></div>
</div></section>

<section class="sec"><div class="wrap">
  {sec_head('', t(L('How it works', 'طريقة الاشتراك')), t(L('From payment to playing in four steps', 'من الدفع إلى المشاهدة في 4 خطوات')))}
  {how_block(c)}
</div></section>

<section class="sec" id="payment"><div class="wrap">
  {sec_head('', t(L('Payment', 'الدفع')), t(L('Ways to pay', 'طرق الدفع')), t(L("Message us and we'll send the payment details.", 'راسلنا وسنرسل لك تفاصيل الدفع.')))}
  {pay_block(c)}
</div></section>
''' + cta_block(c)
    return (t(L('Plans & Prices', 'الباقات والأسعار')),
            t(L('Hossam TV plans and prices for Canada, the USA and worldwide, plus Egypt and the Gulf. Arabic channels, live football and 4K — every plan starts with a free trial.',
                'باقات وأسعار Hossam TV لكندا وأمريكا وباقي الدول، ومصر والخليج. قنوات عربية ومباريات مباشرة و4K — وكل باقة تبدأ بتجربة مجانية.')),
            body)


# ----------------------------------------------------------------------------
# CHANNELS
# ----------------------------------------------------------------------------
def channels(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('Channels', 'القنوات')))],
                     t(L("What you can watch", 'ماذا يمكنك أن تشاهد')),
                     t(L('What each plan is strongest at.', 'ما تتميز به كل باقة.')))
    cats = ''
    for ic, h, p, best in CATEGORIES:
        # two rows: Egypt-only plans and plans sold worldwide
        rows = ''
        for lbl, group in [(L('Egypt', 'مصر'), [x for x in best if PLANS[x]['egypt_only']]),
                           (L('Worldwide', 'كل الدول'), [x for x in best if not PLANS[x]['egypt_only']])]:
            if group:
                chips = ''.join(f'<span class="pchip" style="--c:{PLANS[x]["color"]}">{t(PLANS[x]["name"])}</span>' for x in group)
                rows += f'<div class="dots"><span class="dots-lbl">{t(lbl)}</span>{chips}</div>'
        cats += f'<div class="cat">{icon(ic)}<h3>{t(h)}</h3><p>{t(p)}</p><div class="dot-rows">{rows}</div></div>'

    per = ''
    for pid in PLAN_ORDER:
        p = PLANS[pid]
        nm = t(p['name'])
        stats = ''.join(f'<div class="stat"><b>{v}</b><span>{t(lbl)}</span></div>' for v, lbl in p['stats'])
        feat = ''.join(f'<li{CLS_NO if len(f) > 2 and f[2] else ""}>{icon(f[0])}<span>{t(f[1])}</span></li>' for f in p['feat'])
        eg = f'<span class="badge">{t(L("Egypt only", "مصر فقط"))}</span>' if p['egypt_only'] else ''
        per += f'''<article class="plan" style="--c:{p["color"]}">
  <div class="badges">{eg}</div>
  <div class="plan-top"><img class="plan-logo" src="{c.root}{p["img"]}" alt="" width="56" height="56" loading="lazy"><div><h3>{nm}</h3>{('<span class="aka">' + aka_text(c, pid) + '</span>') if p.get('aka') else ''}</div></div>
  <p class="tag">{t(p["tag"])}</p>
  <div class="stats">{stats}</div>
  <ul class="feat">{feat}</ul>
</article>'''

    body = hero + f'''
<section class="sec first"><div class="wrap">
  {sec_head('', t(L('Categories', 'الفئات')), t(L('Something for everyone at home', 'شيء لكل فرد في البيت')), t(L('The strongest plans in Egypt and worldwide.', 'أقوى الباقات في مصر وفي كل الدول.')))}
  <div class="cats">{cats}</div>
</div></section>

<section class="sec"><div class="wrap">
  {sec_head('', t(L('By plan', 'حسب الباقة')), t(L('What each plan includes', 'ماذا تتضمن كل باقة')), t(L('Each plan at a glance.', 'كل باقة بنظرة سريعة.')))}
  <div class="plans">{per}</div>
</div></section>

<section class="sec"><div class="wrap">
  <a class="st-more" href="{c.href('speed-test.html')}">{icon('bolt')}<span>{t(L('What internet speed do you need? Test yours — 5 Mbps for SD, 10 for HD, 25 for 4K.', 'ما السرعة التي تحتاجها؟ اختبر سرعتك — 5 ميجا لـ SD و10 لـ HD و25 لـ 4K.'))}</span>{icon('arrow', 'flip')}</a>
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
                     t(L('Pick your device. Most setups take under 10 minutes.', 'اختر جهازك. معظم الأجهزة تستغرق أقل من 10 دقائق.')))
    rows = ''
    for pid in PLAN_ORDER:
        p = PLANS[pid]
        codes = ''
        for a in APPS[pid]:
            w = ''.join(f'<div class="warn-t">{icon("warn")}{t(WARN[x])}</div>' for x in a.get('warn', []))
            codes += f'<div style="margin-bottom:8px"><b>{a["name"]}</b>{(" · " + t(L("Recommended", "موصى به"))) if a.get("rec") else ""}<br>{copy_btn(a["code"])}{w}</div>'
        rows += f'<tr><th scope="row" style="--c:{p["color"]}"><span class="pchip" style="--c:{p["color"]}">{t(p["name"])}</span></th><td>{codes}</td></tr>'
    host_rows = ''
    for pid in PLAN_ORDER:
        p = PLANS[pid]
        hosts = ''.join(f'<div style="margin-bottom:8px"><b>{t(L("Main", "الأساسي")) if j == 0 else t(L(f"Backup {j}", f"احتياطي {j}"))}</b><br>{copy_btn(h)}</div>' for j, h in enumerate(HOSTS[pid]))
        host_rows += f'<tr><th scope="row" style="--c:{p["color"]}"><span class="pchip" style="--c:{p["color"]}">{t(p["name"])}</span></th><td>{hosts}</td></tr>'
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
  {sec_head('', t(L('Quick reference', 'مرجع سريع')), t(L('App codes by plan', 'أكواد التطبيقات حسب الباقة')), t(L('Type in Downloader on a TV, or open on a phone. Tap to copy.', 'اكتبها في Downloader على التلفزيون أو افتحها على الموبايل. اضغط للنسخ.')))}
  <div class="table-wrap"><table class="cmp codes-table" style="min-width:0"><tbody>{rows}</tbody></table></div>
</div></section>

<section class="sec" id="hosts"><div class="wrap">
  {sec_head('', t(L('Other players', 'مشغلات أخرى')), t(L('Server hosts by plan', 'الهوست حسب الباقة')), t(L('For apps where you type your own details (IPTV Smarters, SFVIP, TiviMate…). If the main host doesn’t work, try a backup.', 'للتطبيقات التي تكتب فيها بياناتك (IPTV Smarters و SFVIP و TiviMate…). لو الهوست الأساسي لا يعمل جرّب الاحتياطي.')))}
  <div class="table-wrap"><table class="cmp codes-table" style="min-width:0"><tbody>{host_rows}</tbody></table></div>
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


def hosts_block(c):
    """Plan tabs + server hosts (server URL) for manual players."""
    t = c.t
    tabs = ''.join(
        f'<button type="button" data-plan-btn="{pid}" aria-pressed="{"true" if i == 0 else "false"}">{t(PLANS[pid]["name"])}</button>'
        for i, pid in enumerate(PLAN_ORDER))
    panels = ''
    for i, pid in enumerate(PLAN_ORDER):
        items = ''.join(
            f'<div class="app{" rec" if j == 0 else ""}"><div class="app-h">{t(L("Main host", "الهوست الأساسي")) if j == 0 else t(L(f"Backup host {j}", f"هوست احتياطي {j}"))}</div>{copy_btn(h)}</div>'
            for j, h in enumerate(HOSTS[pid]))
        panels += f'<div data-panel="{pid}"{"" if i == 0 else " hidden"}><div class="apps">{items}</div></div>'
    return f'''<div class="plan-tabs"><span class="hint" style="display:block;color:var(--muted);font-size:.85rem;margin-bottom:6px">{t(L('Server URL (host) for your plan — tap to copy:', 'رابط السيرفر (الهوست) لباقتك — اضغط للنسخ:'))}</span>
<div class="seg" role="group" aria-label="{t(L('Plan', 'الباقة'))}">{tabs}</div></div>{panels}<span class="hint">{t(L("If the main host doesn't work, try a backup — the same username and password work on all of them.", 'لو الهوست الأساسي لا يعمل، جرّب الاحتياطي — نفس اسم المستخدم وكلمة المرور تعمل عليها كلها.'))}</span>'''


def manual_sign_in(c):
    return c.t(L('Sign in with the <b>username</b> and <b>password</b> we sent you on WhatsApp, and the <b>server URL</b> for your plan:',
                 'سجّل الدخول باسم <b>المستخدم</b> و<b>كلمة المرور</b> التي أرسلناها لك عبر واتساب، و<b>رابط السيرفر</b> الخاص بباقتك:')) + hosts_block(c)


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
        f'تفضّل <b>IPTV Smarters Pro</b>؟ اكتب {copy_btn(SMARTERS)} في Downloader — يعمل مع كل الباقات. <a href="{SMARTERS_VIDEO}" target="_blank" rel="noopener">شاهد الشرح</a>')) + hosts_block(c), app_img(c, 'smarters-pro'))


def trouble_links(c, ids):
    t = c.t
    names = {i: q for i, q, _ in TROUBLE}
    return '<ul>' + ''.join(f'<li><a href="{c.href("help.html#" + i)}">{t(names[i])}</a></li>' for i in ids) + '</ul>'


def device_data(c, slug):
    t = c.t
    P = lambda en, ar: t(L(en, ar))
    if slug == 'android-tv':
        return dict(
            apps=['downloader'],
            h1=P('Install Hossam TV on Android TV & TV boxes', 'تثبيت Hossam TV على أندرويد تي في وأجهزة البوكس'),
            lead=P('Android TV, Google TV and most TV boxes. About 10 minutes.', 'أندرويد تي في وجوجل تي في ومعظم البوكسات. حوالي 10 دقائق.'),
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
            "Newer Firesticks running <b>Vega OS</b> — such as the <b>Fire TV Stick 4K Select</b> and the 2026 <b>Fire TV Stick HD</b> — can't run our streaming apps. To check: <span class=\"path\">Settings → My Fire TV → About</span>. If the software version says <b>Fire OS</b>, you're good. If it just says <b>OS</b> with a version starting with 1, it's Vega OS — use an Android TV box or another device instead.",
            'أجهزة فايرستيك الأحدث التي تعمل بنظام <b>Vega OS</b> — مثل <b>Fire TV Stick 4K Select</b> و<b>Fire TV Stick HD</b> إصدار 2026 — لا تدعم تطبيقات البث الخاصة بنا. للتأكد: <span class="path"><bdi dir="ltr">Settings → My Fire TV → About</bdi></span>. إذا كان إصدار النظام مكتوباً <b>Fire OS</b> فجهازك مناسب. إذا كان مكتوباً <b>OS</b> فقط ويبدأ الرقم بـ 1، فهو Vega OS — استخدم أندرويد بوكس أو جهازاً آخر.'))
        return dict(
            apps=['downloader'],
            h1=P('Install Hossam TV on Amazon Firestick', 'تثبيت Hossam TV على أمازون فايرستيك'),
            lead=P('Fire TV devices running Fire OS. About 10 minutes.', 'أجهزة Fire TV بنظام Fire OS. حوالي 10 دقائق.'),
            desc=P('Step-by-step: install Hossam TV on Amazon Firestick with Downloader, and check if your Firestick runs Vega OS.',
                   'خطوة بخطوة: تثبيت Hossam TV على أمازون فايرستيك باستخدام Downloader، وطريقة التأكد إن كان جهازك يعمل بنظام Vega OS.'),
            pre=[vega],
            steps=[
                P('From the Home screen, open <b>Find</b> (the magnifying glass), search for <b>Downloader</b> and install <b>Downloader by AFTVNews</b>.',
                  'من الشاشة الرئيسية، افتح <b>Find</b> (علامة العدسة)، ابحث عن <b>Downloader</b> وثبّت <b>Downloader by AFTVNews</b>.'),
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
            lead=P('Download from your phone’s browser. About 5 minutes.', 'حمّل التطبيق من متصفح الموبايل. حوالي 5 دقائق.'),
            desc=P('Step-by-step: install Hossam TV on an Android phone or tablet.',
                   'خطوة بخطوة: تثبيت Hossam TV على موبايل أو تابلت أندرويد.'),
            steps=[
                P("Open your phone's browser and go to the link for your plan:", 'افتح المتصفح على موبايلك وادخل على رابط باقتك:') + apps_block(c, 'android'),
                mediafire(c),
                P('When the <b>APK</b> file finishes downloading, open it and tap <b>Install</b>.<span class="hint">If your phone asks, allow your browser to install apps. If Google Play Protect warns you, tap <b>More details → Install anyway</b>.</span>',
                  'بعد تحميل ملف <b>APK</b>، افتحه واضغط <b>تثبيت</b>.<span class="hint">إذا سألك الهاتف، اسمح للمتصفح بتثبيت التطبيقات. وإذا ظهر تحذير Google Play Protect، اضغط <b>مزيد من التفاصيل ← التثبيت على أي حال</b>.</span>'),
                sign_in(c),
            ],
            notes=[note('tip', P('Alternative app', 'تطبيق بديل'), P(f'You can also get <b>IPTV Smarters Pro</b> from {open_link(SMARTERS)}', f'يمكنك أيضاً تحميل <b>IPTV Smarters Pro</b> من {open_link(SMARTERS)}') + hosts_block(c), app_img(c, 'smarters-pro'))],
            trouble=['install', 'login', 'buffering'],
        )
    if slug == 'apple':
        return dict(
            apps=['smarters-lite'],
            h1=P('Install Hossam TV on iPhone, iPad, Mac & Apple TV', 'تثبيت Hossam TV على آيفون وآيباد وماك وأبل تي في'),
            lead=P('Free Smarters Player Lite app. About 5 minutes, any plan.', 'تطبيق Smarters Player Lite المجاني. حوالي 5 دقائق، لكل الباقات.'),
            desc=P('Step-by-step: watch Hossam TV on iPhone, iPad, Mac and Apple TV with Smarters Player Lite.',
                   'خطوة بخطوة: شاهد Hossam TV على آيفون وآيباد وماك وأبل تي في باستخدام Smarters Player Lite.'),
            steps=[
                P('Open the <b>App Store</b> and install <b>Smarters Player Lite</b>.', 'افتح <b>App Store</b> وثبّت تطبيق <b>Smarters Player Lite</b>.'),
                P('Open the app, accept the terms and choose <b>Login with Xtream Codes API</b>.', 'افتح التطبيق، وافق على الشروط، ثم اختر <b>Login with Xtream Codes API</b>.'),
                P('Enter any name you like, then the <b>username</b> and <b>password</b> we sent you on WhatsApp and the <b>server URL</b> for your plan, and tap <b>Add user</b>.',
                  'اكتب أي اسم تريده، ثم <b>اسم المستخدم</b> و<b>كلمة المرور</b> التي أرسلناها لك عبر واتساب و<b>رابط السيرفر</b> الخاص بباقتك، واضغط <b>Add user</b>.') + hosts_block(c),
                P('Wait for the channels and movies to load, then start watching.', 'انتظر حتى يتم تحميل القنوات والأفلام، ثم ابدأ المشاهدة.'),
            ],
            notes=[note('tip', P('Apple TV', 'أبل تي في'), P('The same app and the same steps work on Apple TV — search for it in the Apple TV App Store.', 'نفس التطبيق ونفس الخطوات تعمل على أبل تي في — ابحث عنه في App Store الخاص بأبل تي في.'))],
            trouble=['login', 'buffering'],
        )
    if slug == 'smart-tv':
        return dict(
            apps=['bob', 'ibo'],
            h1=P('Install Hossam TV on Samsung & LG Smart TVs', 'تثبيت Hossam TV على شاشات سامسونج و LG'),
            lead=P("Bob Player on Samsung, IBO Player on LG. Send us your TV's code and we load your channels.", 'Bob Player على سامسونج و IBO Player على LG. أرسل لنا كود الشاشة ونحن نجهّز القنوات.'),
            desc=P('Step-by-step: watch Hossam TV on Samsung (Bob Player) and LG (IBO Player) Smart TVs, including app fees.',
                   'خطوة بخطوة: شاهد Hossam TV على شاشات سامسونج (Bob Player) و LG (IBO Player)، مع توضيح رسوم التطبيق.'),
            steps=[
                P("Open your TV's app store and install the app: <b>Samsung</b> (<b>Apps</b>) → <b>Bob Player</b>. <b>LG</b> (<b>LG Content Store</b>) → <b>IBO Player</b>.<span class=\"hint\">IBO Player isn't in the Samsung store right now, so Samsung uses Bob Player — same company, same steps.</span>",
                  'افتح متجر التطبيقات في الشاشة وثبّت التطبيق: <b>سامسونج</b> (<b>Apps</b>) ← <b>Bob Player</b>. <b>LG</b> (<b>LG Content Store</b>) ← <b>IBO Player</b>.<span class="hint">IBO Player غير موجود حالياً في متجر سامسونج، لذلك نستخدم Bob Player على سامسونج — من نفس الشركة وبنفس الخطوات.</span>'),
                P('Install and open it. The screen shows a <b>Device ID</b> (MAC) and a <b>Device Key</b>.', 'ثبّت التطبيق وافتحه. ستظهر على الشاشة بيانات <b>Device ID</b> (MAC) و <b>Device Key</b>.'),
                P(f'Send a clear photo of them on WhatsApp together with your subscription <b>username</b>. {ext(c.wa("tv"), "Send on WhatsApp")}',
                  f'أرسل صورة واضحة لهما عبر واتساب مع <b>اسم المستخدم</b> الخاص باشتراكك. {ext(c.wa("tv"), "أرسل عبر واتساب")}'),
                P("We load your playlist. Restart the app and your channels will appear.", 'سنجهّز قائمتك. أعد تشغيل التطبيق وستظهر القنوات.'),
            ],
            notes=[
                note('tip', P('App fee — outside Egypt', 'رسوم التطبيق — خارج مصر'),
                     P('Bob / IBO Player activation per TV: <b>$2</b> for 1 year or <b>$4</b> for lifetime.',
                       'تفعيل Bob / IBO Player لكل شاشة: <b>2 دولار</b> لسنة أو <b>4 دولارات</b> مدى الحياة.')),
                note('warn', P('App fee — Egypt', 'رسوم التطبيق — مصر'),
                     P('In Egypt, Bob / IBO Player activation is <b>200 EGP lifetime</b> per TV, with any plan. The app gives you a 7-day free trial first.',
                       'في مصر، تفعيل Bob / IBO Player بـ <b>200 جنيه مدى الحياة</b> لكل شاشة مع أي باقة. التطبيق يتيح تجربة مجانية 7 أيام أولاً.')),
            ],
            trouble=['buffering', 'locked'],
        )
    if slug == 'windows':
        return dict(
            h1=P('Install Hossam TV on Windows PC & laptop', 'تثبيت Hossam TV على كمبيوتر ويندوز'),
            lead=P('Free SFVIP Player. About 5 minutes, any plan.', 'برنامج SFVIP Player المجاني. حوالي 5 دقائق، لكل الباقات.'),
            desc=P('Step-by-step: watch Hossam TV on a Windows PC or laptop with SFVIP Player.',
                   'خطوة بخطوة: شاهد Hossam TV على كمبيوتر أو لابتوب ويندوز باستخدام SFVIP Player.'),
            steps=[
                P(f'Download <b>SFVIP Player</b> (ZIP file) from <a href="{SFVIP_ZIP}" target="_blank" rel="noopener">MediaFire</a>.<span class="hint">Click the big blue Download button — not "Download faster".</span>',
                  f'حمّل <b>SFVIP Player</b> (ملف ZIP) من <a href="{SFVIP_ZIP}" target="_blank" rel="noopener">MediaFire</a>.<span class="hint">اضغط زر التحميل الأزرق الكبير — وليس «Download faster».</span>'),
                P('Right-click the ZIP file, choose <b>Extract All</b>, then open the app inside.<span class="hint">If Windows shows "Windows protected your PC", click <b>More info → Run anyway</b>.</span>',
                  'اضغط بزر الماوس الأيمن على ملف ZIP واختر <b>Extract All</b>، ثم افتح البرنامج الموجود بداخله.<span class="hint">إذا ظهرت رسالة "Windows protected your PC"، اضغط <b>More info ← Run anyway</b>.</span>'),
                manual_sign_in(c),
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



# ----------------------------------------------------------------------------
# STEP PICTURES — a small drawn screen under each setup step (pure HTML/CSS, no real screenshots), with a red ring
# on what to press. Third-party apps are only named, never copied.
# ----------------------------------------------------------------------------
STEP_PICS = {   # labels follow the real screens (Downloader v2, Fire OS, MediaFire, Smarters Player Lite, IBO/Bob Player, SFVIP)
    'android-tv': [('tv', 'store', 'Google Play', 'Downloader', 'Install'), ('tv', 'code'), ('tv', 'mediafire'), ('tv', 'install'), ('tv', 'login')],
    'firestick': [('tv', 'store', 'Find', 'Downloader', 'Get'),
                  ('tv', 'path', ['Settings', 'My Fire TV', 'Developer Options', 'Install Unknown Apps', 'Downloader']),
                  ('tv', 'code'), ('tv', 'mediafire'), ('tv', 'login')],
    'android': [('phone', 'browser'), ('phone', 'mediafire'), ('phone', 'install'), ('phone', 'login')],
    'apple': [('phone', 'store', 'App Store', 'Smarters Player Lite', 'Get'), ('phone', 'xtream'), ('phone', 'smarters'), ('phone', 'watch')],
    'smart-tv': [('tv', 'store', 'Apps', 'Bob Player · IBO Player', 'Install'), ('tv', 'devid'), ('phone', 'whatsapp'), ('tv', 'watch')],
    'windows': [('pc', 'mediafire'), ('pc', 'zip'), ('pc', 'sfvip')],
}


def step_pic(c, frame, kind, *a):
    t = c.t
    hot = lambda x, cls='': f'<span class="mk-hot{(" " + cls) if cls else ""}">{x}</span>'
    field = lambda lbl, val: f'<div class="mk-in"><small>{lbl}</small><b class="mk-ltr">{val}</b></div>'
    if kind == 'store':
        where, app, btn = a
        inner = (f'<div class="mk-bar">{icon("search")}<span>{app.split(" · ")[0]}</span></div>'
                 f'<div class="mk-app"><i class="mk-ic"></i><div><b>{app}</b><small>{where}</small></div>{hot(btn, "mk-btn")}</div>')
    elif kind == 'code':   # Downloader v2: sidebar + one address bar on top, browser below
        inner = (f'<div class="mk-dl mk-ltr"><ul class="mk-side"><li class="on">Home</li><li>Files</li><li>Favorites</li><li>Settings</li></ul>'
                 f'<div class="mk-dl-main">{hot(t(L("your plan’s code", "كود باقتك")) + "<span class=mk-caret></span>", "mk-field")}'
                 f'<div class="mk-lines"><i></i><i></i><i></i></div></div></div>')
    elif kind == 'browser':
        inner = (f'<div class="mk-url mk-ltr">{icon("globe")}<span>{t(L("your plan’s link", "رابط باقتك"))}</span></div>'
                 f'<div class="mk-lines"><i></i><i></i><i></i></div>')
    elif kind == 'mediafire':
        inner = (f'<small class="mk-lbl">MediaFire</small><div class="mk-file"><i class="mk-ic mk-ic-file"></i><b class="mk-ltr">HossamTV.apk</b></div>'
                 f'{hot("Download (25 MB)", "mk-btn mk-blue mk-ltr")}')
    elif kind == 'install':
        inner = (f'<div class="mk-dlg mk-ltr"><div class="mk-file"><i class="mk-ic"></i><b>Hossam TV</b></div><p>Do you want to install this application?</p>'
                 f'<div class="mk-row"><span class="mk-ghost">Cancel</span>{hot("Install", "mk-btn")}</div></div>')
    elif kind == 'path':
        items = a[0]
        rows = ''.join(f'<li>{x}<span>›</span></li>' for x in items[:-1])
        inner = f'<ul class="mk-list mk-ltr">{rows}<li>{items[-1]}{hot("<i class=mk-tog></i>", "mk-on")}</li></ul>'
    elif kind == 'login':
        inner = (field(t(L('Username', 'اسم المستخدم')), 'ahmed123') + field(t(L('Password', 'كلمة المرور')), '••••••••')
                 + hot(t(L('Sign in', 'تسجيل الدخول')), 'mk-btn mk-wide'))
    elif kind == 'xtream':   # Smarters Player Lite: login type
        inner = (f'{hot("Login with Xtream Codes API", "mk-opt")}<div class="mk-opt">Load Your Playlist or File/URL</div>')
    elif kind == 'smarters':
        inner = ('<div class="mk-ltr mk-col">' + ''.join(f'<div class="mk-in"><b>{v}</b></div>' for v in ('Any Name', 'Username', 'Password', 'http://url_here.com:port'))
                 + hot('ADD USER', 'mk-btn mk-wide mk-violet') + '</div>')
    elif kind == 'sfvip':
        inner = ('<small class="mk-lbl">SFVIP Player · User/Pass</small><div class="mk-ltr mk-col">' + field('Address', 'http://…') + field('User', 'ahmed123')
                 + field('Password', '••••••••') + hot('OK', 'mk-btn') + '</div>')
    elif kind == 'devid':
        inner = (f'<div class="mk-hot mk-ids mk-ltr"><div><small>Mac Address</small><b>1A:2B:3C:4D:5E:6F</b></div><div><small>Device Key</small><b>123456</b></div></div>'
                 f'<span class="mk-cam">{icon("info")}{t(L("Take a photo of this (may say Device ID)", "صوّر هذه البيانات (قد تظهر باسم Device ID)"))}</span>')
    elif kind == 'whatsapp':
        inner = (f'<div class="mk-chat"><span class="mk-photo"></span><span class="mk-msg">{t(L("Username: ahmed123", "اسم المستخدم: ahmed123"))}</span></div>'
                 f'{hot(icon("chat"), "mk-send")}')
    elif kind == 'zip':
        inner = (f'<div class="mk-file"><i class="mk-ic mk-ic-zip"></i><b class="mk-ltr">SFVIP.zip</b></div>'
                 f'<ul class="mk-menu mk-ltr"><li>Open</li><li class="mk-hot">Extract All...</li><li>Copy</li></ul>')
    elif kind == 'watch':
        inner = '<div class="mk-tiles">' + '<i></i>' * 8 + f'</div>{hot(t(L("▶ Watching", "▶ تشغيل")), "mk-btn")}'
    else:
        return ''
    return f'<figure class="mk mk-{frame}" aria-hidden="true"><div class="mk-scr mk-k-{kind}">{inner}</div></figure>'

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
            pics = STEP_PICS.get(slug, [])
            steps = ''.join(f'<li class="st"><span class="st-n">{i + 1}</span><div class="st-b">{s}{step_pic(c, *pics[i]) if i < len(pics) else ""}</div></li>'
                            for i, s in enumerate(data['steps']))
            notes = f'<div class="notes">{"".join(data["notes"])}</div>' if data.get('notes') else ''
            trouble = f'<div class="trouble prose"><h2>{t(L("Having trouble?", "تواجه مشكلة؟"))}</h2>{trouble_links(c, data["trouble"])}</div>'
            need = need_list(c, data['apps']) if data.get('apps') else ''
            main = f'<div class="guide">{pre}<h2>{t(L("Steps", "الخطوات"))}</h2>{need}<ol class="steps">{steps}</ol>{notes}{trouble}</div>'
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
                     t(L('Quick fixes and common questions.', 'حلول سريعة وأسئلة شائعة.')),
                     extra=search + status_line(c))
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
  <div class="help-remind">{reminder_card(c)}{account_card(c)}</div>
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
    body += ld_json({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': _plain(t(q)), 'acceptedAnswer': {'@type': 'Answer', 'text': _plain(faq_answer(c, a))}}
        for _, items in FAQ for _, q, a in items]})
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
                     t(L('A small, personal streaming service — a real person helps you on WhatsApp.', 'خدمة بث صغيرة وشخصية — شخص حقيقي يساعدك على واتساب.')))
    lic = ''
    if t(LICENSE_TEXT):
        lic = f'<h2>{t(L("Licensing", "التراخيص"))}</h2><p>{t(LICENSE_TEXT)}</p>'
    regions = [L('Canada', 'كندا'), L('Egypt', 'مصر'), L('USA', 'أمريكا'), L('Europe', 'أوروبا'), L('Gulf', 'الخليج'), L('Worldwide', 'باقي دول العالم')]
    body = hero + f'''
<section class="sec first"><div class="wrap split">
  <div class="prose">
    <h2>{t(L('Who we are', 'من نحن'))}</h2>
    <p>{t(L('Based in Egypt, serving viewers in Canada, Egypt, the Gulf and worldwide.', 'مقرنا في مصر، ونخدم المشاهدين في كندا ومصر والخليج وحول العالم.'))}</p>
    <h2>{t(L('How we work', 'كيف نعمل'))}</h2>
    <p>{t(L('Trial, payment, activation, setup and renewals — all personally on WhatsApp. We recommend the plan that fits you, even if it’s the cheaper one.', 'التجربة والدفع والتفعيل والتثبيت والتجديد — كلها بشكل شخصي على واتساب. ونرشح لك الباقة المناسبة حتى لو كانت الأرخص.'))}</p>
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
  <div class="about-side">
  <aside class="contact-card">
    <div class="bars" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
    <h3>{t(L('Talk to us', 'تواصل معنا'))}</h3>
    <p>{t(L('WhatsApp chat only — no calls, please. Save our number to see updates on our Status.', 'واتساب رسائل فقط — بدون مكالمات من فضلك. احفظ رقمنا لتتابع التحديثات على الحالة.'))}</p>
    <span class="num">{WHATSAPP_DISPLAY}</span>
    {ext(c.wa('sub'), icon('chat') + t(L('Message us on WhatsApp', 'راسلنا عبر واتساب')), 'btn btn-wa')}
  </aside>
  </div>
</div></section>
''' + cta_block(c)
    return (t(L('About Us', 'من نحن')),
            t(L('Hossam TV is a personal streaming service for Arabic viewers in Canada, the USA, Egypt, the Gulf and worldwide, with fast support on WhatsApp.',
                'Hossam TV خدمة بث شخصية للمشاهدين العرب في كندا وأمريكا ومصر والخليج وحول العالم، مع دعم سريع عبر واتساب.')),
            body)


# ----------------------------------------------------------------------------
# POLICIES
# ----------------------------------------------------------------------------
def policies(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('Policies', 'السياسات')))],
                     t(L('Terms, refunds & privacy', 'الشروط والاسترجاع والخصوصية')),
                     t(L('In plain language.', 'بلغة بسيطة.')),
                     extra=f'<p class="updated">{t(L("Last updated:", "آخر تحديث:"))} {t(LAST_UPDATED)}</p>')
    nav = ''.join(f'<a class="btn btn-ghost btn-sm" href="#{a}">{t(lbl)}</a>' for a, lbl in [
        ('terms', L('Terms of service', 'شروط الخدمة')), ('refund', L('Refund policy', 'سياسة الاسترجاع')), ('privacy', L('Privacy policy', 'سياسة الخصوصية'))])

    if c.ar:
        prose = f'''
<h2 id="terms">شروط الخدمة</h2>
<h3>الخدمة</h3>
<p>توفر Hossam TV اشتراكات بث (قنوات مباشرة وأفلام ومسلسلات) تُشاهَد عبر الإنترنت، ويتم تفعيلها بشكل شخصي عبر واتساب.</p>
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
<li>بعض شركات الإنترنت قد تحجب خدمات البث، وهذا خارج عن إرادتنا. لم نعد نقدم الخدمة في الإمارات.</li>
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
<li>لا يوجد تسجيل حسابات في الموقع. عند الضغط على «تجربة مجانية» يظهر نموذج قصير، ويتم إرسال اسمك واختياراتك (البلد والباقة والجهاز) إلى خادمنا حتى نجهّز طلبك، ثم يُفتح واتساب.</li>
<li>يحفظ الموقع اختيارك للغة والبلد والباقة في متصفحك (localStorage) حتى يتذكرها في زيارتك القادمة، ويحفظ محادثتك مع المساعد الآلي لمدة 24 ساعة.</li>
<li>مساعد المحادثة في الموقع <b>بوت آلي يعمل بالذكاء الاصطناعي</b>، وليس شخصاً وليس رقم الواتساب الرئيسي. الرسائل التي تكتبها فيه تُرسل إلى خادمنا ويتم معالجتها بالذكاء الاصطناعي لكتابة الردود. لا تكتب فيه كلمات مرور أو بيانات دفع.</li>
<li>الخطوط يتم تحميلها من Google Fonts.</li>
</ul>
<h3>اختياراتك</h3>
<p>يمكنك أن تطلب منا عبر واتساب حذف بياناتك بعد انتهاء اشتراكك.</p>
'''
    else:
        prose = f'''
<h2 id="terms">Terms of service</h2>
<h3>The service</h3>
<p>Hossam TV provides streaming subscriptions (live channels, movies and series) watched over the internet, activated personally through WhatsApp.</p>
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
<li>Some internet providers may block streaming services. This is outside our control. We no longer serve the UAE.</li>
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
<li>There are no accounts on this site. When you tap Free trial, a short form opens. Your name and choices (country, plan, device) are sent to our server so we can prepare your order, then WhatsApp opens.</li>
<li>The site saves your language, country and plan choice in your browser (localStorage) so it remembers them next time. It also keeps your chat with the assistant there for 24 hours.</li>
<li>The chat assistant on this site is an <b>automated AI bot</b>, not a person and not our main WhatsApp. Messages you type there are sent to our server and processed by AI to write the replies. Don't type passwords or payment details in it.</li>
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
# ----------------------------------------------------------------------------
# MY ACCOUNT — username + password -> plan, expiry, reminders (n8n site-account). Nothing is stored on the website.
# ----------------------------------------------------------------------------
def status_line(c):
    """Filled in by bot.js from site-data: 'All servers working' or which plan has a problem. Hidden until the data arrives."""
    return f'<p class="svc-status" data-status hidden data-ok="{c.t(L("All servers working", "كل السيرفرات تعمل"))}" data-bad="{c.t(L("Problem with {x} — we’re on it", "مشكلة في {x} — نعمل عليها"))}"></p>'


def account_card(c, compact=False):
    """Check my subscription: username + password -> plan, expiry, days left, reminders on/off (n8n site-account).
    Sits under the renewal-reminders form. Nothing is stored on the website."""
    t = c.t
    return f'''<form class="remind acct-form{' remind-compact' if compact else ''}" id="account" data-account data-api="{N8N_WEBHOOK}site-account" novalidate>
    <h3>{icon('key')}{t(L('Check expiry date', 'تاريخ انتهاء الاشتراك'))}</h3>
    <div class="rf-grid">
      <div class="rf"><label for="acctUser">{t(L('Username', 'اسم المستخدم'))}</label>
        <input id="acctUser" name="username" type="text" dir="ltr" autocomplete="username" autocapitalize="none" autocorrect="off" spellcheck="false" maxlength="64"></div>
      <div class="rf"><label for="acctPass">{t(L('Password', 'كلمة المرور'))}</label>
        <div class="remind-pass" dir="ltr"><input id="acctPass" name="password" type="password" dir="ltr" autocomplete="current-password" autocapitalize="none" autocorrect="off" spellcheck="false" maxlength="64">
        <button type="button" class="remind-show" data-acct-show aria-pressed="false" data-show="{t(L('Show', 'إظهار'))}" data-hide="{t(L('Hide', 'إخفاء'))}">{t(L('Show', 'إظهار'))}</button></div></div>
      <button type="submit" class="btn btn-wa">{icon('search')}<span>{t(L('Check', 'استعلم'))}</span></button>
    </div>
    <input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
    <p class="remind-msg" role="status" hidden
      data-msg-empty="{t(L('Type your username and password.', 'اكتب اسم المستخدم وكلمة المرور.'))}"
      data-msg-not_found="{t(L("No account matches that username and password. Type both exactly as in the picture we sent. Renewed in the last week? Try again in a few days.", 'لا يوجد حساب بهذا الاسم وكلمة المرور. اكتبهما بالضبط كما في الصورة التي أرسلناها. جدّدت خلال الأسبوع الماضي؟ حاول بعد أيام.'))}"
      data-msg-limited="{t(L('Too many checks today. Please try again tomorrow.', 'محاولات كثيرة اليوم. حاول غداً.'))}"
      data-msg-error="{t(L("Couldn't connect right now. Try again in a minute.", 'تعذّر الاتصال الآن. حاول بعد دقيقة.'))}"></p>
    <div class="acct-out" data-acct-out hidden
      data-l-expires="{t(L('Ends on', 'ينتهي في'))}" data-l-left="{t(L('{n} days left', 'باقي {n} يوم'))}" data-l-today="{t(L('Ends today', 'ينتهي اليوم'))}"
      data-l-expired="{t(L('Expired', 'منتهي'))}" data-l-rem-on="{t(L('Renewal reminders are on', 'تنبيهات التجديد مفعّلة'))}"
      data-l-rem-off="{t(L('Turn on renewal reminders', 'فعّل تنبيهات التجديد'))}" data-l-renew="{t(L('Renew', 'جدّد'))}"
      data-reminders="#reminders" data-locale="{'ar-EG' if c.ar else 'en-CA'}"></div>
  </form>'''


def matches_block(c, limit=0):
    """Big matches (assets/data/matches.json, refreshed by a GitHub Action). Rendered by site.js; hidden until data loads."""
    t = c.t
    return (f'<div class="matches" data-matches data-src="{c.root}assets/data/matches.json" data-limit="{limit}" '
            f'data-l-mine="{t(L("Your time", "بتوقيتك"))}" '
            f'data-l-live="{t(L("Live now", "مباشر الآن"))}" data-l-cal="{t(L("Add to calendar", "أضف للتقويم"))}" data-l-empty="{t(L("No big matches in the next few days.", "لا توجد مباريات كبيرة في الأيام القادمة."))}" '
            f'data-locale="{"ar-EG" if c.ar else "en-US"}" hidden></div>')


def next_match(c, more=True):
    """Countdown to the next high-profile match (filled by assets/matches.js from matches.json; hidden when there's none).
    "Add to calendar" downloads a small .ics file with a 30-minute reminder."""
    t = c.t
    units = ''.join(f'<div class="nm-unit"><b data-next-v="{u}">00</b><small data-next-l="{u}"></small></div>' for u in 'dhms')
    team = lambda side: (f'<b><img class="nm-logo" data-next-{side}-logo alt="" width="40" height="40" hidden>'
                         f'<span data-next-{side}></span></b>')
    link = (f'<a class="nm-btn nm-more" href="{c.href("matches.html")}">{t(L("All matches", "كل المباريات"))}{icon("arrow", "flip")}</a>'
            if more else '')
    return (f'<div class="nextm" data-next data-src="{c.root}assets/data/matches.json" '
            f'data-l-cal="{t(L("Watch live on Hossam TV — hossamservices.com", "شاهدها مباشرة على Hossam TV — hossamservices.com"))}" hidden>'
            f'<span class="nm-league">{icon("ball")}<span data-next-league></span></span>'
            f'<span class="nm-teams">{team("home")}<i>{t(L("vs", "ضد"))}</i>{team("away")}</span>'
            f'<span class="nm-count">{units}</span>'
            f'<span class="nm-livebox" data-next-livebox hidden></span>'
            f'<span class="nm-when" data-next-when></span>'
            f'<span class="nm-actions"><button type="button" class="nm-btn nm-cal" data-next-cal>{icon("clock")}{t(L("Add to calendar", "أضف للتقويم"))}</button>{link}</span>'
            f'</div>')


def results_block(c):
    """Last week's results of the big matches (matches.json "results"), filled by assets/matches.js."""
    t = c.t
    return (f'<section class="results" data-results hidden><h2 class="st-h">{t(L("Last results", "آخر النتائج"))}</h2>'
            f'<div class="rs-list" data-results-list></div></section>')


def matches_ticker(c):
    """Swipeable row of small match cards under the header — live matches first (score + minute), then this week's big
    matches with kick-off in the visitor's time zone and the channel. Each card opens the matches page on that match's
    countdown (with "Add to calendar"), the last one all matches. Filled by assets/matches.js from assets/data/matches.json (hidden until there's something to show)."""
    return (f'<nav class="mstrip" data-strip data-src="{c.root}assets/data/matches.json" data-root="{c.root}" '
            f'aria-label="{c.t(L("Big matches this week", "أهم مباريات الأسبوع"))}" hidden><div class="ms-track" data-strip-track></div></nav>')


def standings_block(c):
    """League tables (top 6) — filled by assets/standings.js; hidden until the data loads."""
    t = c.t
    return f'''<section class="tables" data-standings data-src="{c.root}assets/data/standings.json" hidden>
  <h2 class="st-h">{t(L('League tables', 'ترتيب الدوريات'))}</h2>
  <div class="tb-tabs" role="tablist" data-st-tabs></div>
  <div class="tb-wrap"><table class="tb">
    <thead><tr><th>#</th><th class="tb-team">{t(L('Team', 'الفريق'))}</th><th>{t(L('P', 'لعب'))}</th><th>{t(L('GD', 'الفارق'))}</th><th>{t(L('Pts', 'نقاط'))}</th></tr></thead>
    <tbody data-st-body></tbody>
  </table></div>
</section>
<script src="{c.root}assets/standings.js" defer></script>'''


def match_links(c):
    """Links to the big-match pages (also helps Google find them)."""
    t, vs = c.t, c.t(L('vs', 'ضد'))
    items = ''.join(f'<li><a href="{c.href("match/" + sl + ".html")}">{t(L(e["home"]["en"], e["home"]["ar"]))} {vs} {t(L(e["away"]["en"], e["away"]["ar"]))}</a></li>'
                    for sl, e, r in match_list() if not r)
    return f'<div class="mp-links"><h2 class="st-h">{t(L("Big match pages", "صفحات القمم"))}</h2><ul class="mp-more">{items}</ul></div>' if items else ''


def matches_page(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('Matches', 'المباريات')))],
                     t(L('Football — matches, results & tables', 'الكورة — المباريات والنتائج والترتيب')),
                     t(L('This week’s big matches in your time zone with the channel, last results and league tables.', 'مباريات الأسبوع بتوقيتك والقناة الناقلة، وآخر النتائج وترتيب الدوريات.')))
    body = hero + f'''
<section class="sec first"><div class="wrap">
  {next_match(c, more=False)}
  {match_links(c)}
  {matches_block(c)}
  {results_block(c)}
  {standings_block(c)}
  <div class="tb-tabs lg-others">{''.join(f'<a class="tb-tab" href="{c.href("league/" + sl + ".html")}">{c.t(L(e, a))} →</a>' for _, _, sl, e, a, _, _ in LEAGUE_PAGES)}</div>
  <p class="matches-note">{t(L('Updated automatically every few hours. Times can change — check closer to kick-off.', 'يتم التحديث تلقائياً كل بضع ساعات. المواعيد قد تتغير — راجعها قبل المباراة.'))}</p>
</div></section>
''' + cta_block(c)
    return (t(L('Football — Matches, Results & League Tables', 'الكورة — المباريات والنتائج وترتيب الدوريات')),
            t(L('This week’s big football matches in your time zone (Canada, the USA or anywhere) with the TV channel, plus last results and league tables.',
                'أهم مباريات الأسبوع بتوقيتك المحلي (كندا أو أمريكا أو أي مكان) والقناة الناقلة، مع آخر النتائج وترتيب الدوريات.')),
            body)


# ----------------------------------------------------------------------------
# COUNTRY PAGES — for Google searches like "Arabic TV in Canada". Same plans and prices as the Plans page
# ("Canada & worldwide"), written for viewers in one country.
# ----------------------------------------------------------------------------
COUNTRY_PAGES = [   # Canada first (most customers), then the USA
    ('canada', L('Canada', 'كندا'), L('in Canada', 'في كندا'), 'America/Toronto',
     L('Toronto · Mississauga · Montreal · Ottawa · Calgary · Edmonton · Vancouver · Windsor · London · Halifax',
       'تورونتو · ميسيساجا · مونتريال · أوتاوا · كالجاري · إدمونتون · فانكوفر · وندسور · لندن أونتاريو · هاليفاكس')),
    ('usa', L('the USA', 'أمريكا'), L('in the USA', 'في أمريكا'), 'America/New_York',
     L('New York · New Jersey · Dearborn & Detroit · Chicago · Houston · Dallas · Los Angeles · San Francisco · Washington DC',
       'نيويورك · نيوجيرسي · ديربورن وديترويت · شيكاغو · هيوستن · دالاس · لوس أنجلوس · سان فرانسيسكو · واشنطن')),
    ('uk', L('the UK', 'بريطانيا'), L('in the UK', 'في بريطانيا'), 'Europe/London', None),
    ('europe', L('Europe', 'أوروبا'), L('in Europe', 'في أوروبا'), 'Europe/Berlin', None),
]


def _cat(*parts):
    """Join L() texts: _cat(L('Pay from ', 'ادفع من '), name) -> one L()."""
    return {k: ''.join(p[k] for p in parts) for k in parts[0]}


def country_page(slug, name, where, tz=None, cities=None):
    def build(c):
        t = c.t
        W, N = t(where), t(name)
        hero = page_hero(c, [(None, t(L('Arabic TV', 'القنوات العربية')) + ' ' + W)],
                         t(L('Arabic TV ', 'القنوات العربية ')) + W,
                         t(L('Live football, Arabic channels, movies and series — on your TV, phone or laptop. Try it free first.',
                             'مباريات مباشرة وقنوات عربية وأفلام ومسلسلات — على شاشتك أو موبايلك أو اللابتوب. جرّب مجاناً أولاً.')),
                         actions=btn_trial(c), extra=status_line(c))
        intl = next(r for r in REGIONS if r['id'] == 'intl')
        cards = ''.join(plan_card(c, intl, rp) for rp in intl['plans'])
        why = [
            ('clock', L('Free trial first', 'تجربة مجانية أولاً'), L('Watch for 24 hours before you pay.', 'شاهد 24 ساعة قبل أن تدفع.')),
            ('devices', L('Works on your devices', 'يعمل على أجهزتك'), L('Firestick, Android TV, Samsung & LG, iPhone, Android and PC.', 'فايرستيك وأندرويد تي في وسامسونج و LG وآيفون وأندرويد والكمبيوتر.')),
            ('chat', L('A real person on WhatsApp', 'شخص حقيقي على واتساب'), L('Setup help in Arabic and English.', 'مساعدة في التثبيت بالعربية والإنجليزية.')),
            ('card', _cat(L('Easy to pay from ', 'دفع سهل من '), name), L('PayPal, TapTap Send, Sendwave or Whish Money.', 'PayPal أو TapTap Send أو Sendwave أو Whish Money.')),
        ]
        why_html = ''.join(f'<li>{icon(ic)}<div><b>{t(h)}</b><span>{t(d)}</span></div></li>' for ic, h, d in why)
        faq = [
            (f'{slug}-works', _cat(L('Does it work ', 'هل يعمل '), where, L('?', '؟')),
             L('Yes. All you need is an internet connection — 10 Mbps for HD, 25 Mbps for 4K.', 'نعم. كل ما تحتاجه هو اتصال إنترنت — 10 ميجا لجودة HD و25 ميجا لجودة 4K.')),
            (f'{slug}-plan', L('Which plan should I pick?', 'أي باقة أختار؟'),
             L('Basic if you mostly watch Arabic channels and football. Premium for the biggest library, all sports and channels from every country.', 'الأساسية لو أغلب مشاهدتك قنوات عربية وكرة قدم. بريميوم لأكبر مكتبة وكل الرياضات وقنوات من كل الدول.')),
            (f'{slug}-pay', _cat(L('How do I pay from ', 'كيف أدفع من '), name, L('?', '؟')),
             L("With PayPal, TapTap Send, Sendwave or Whish Money. Message us and we'll send the details.", 'عن طريق PayPal أو TapTap Send أو Sendwave أو Whish Money. راسلنا وسنرسل لك التفاصيل.')),
            (f'{slug}-egypt', _cat(L('Can I watch Egyptian and Arab football ', 'هل أقدر أشاهد الدوري المصري والكورة العربية '), where, L('?', '؟')),
             L('Yes — the Egyptian league, Saudi league, Champions League and the big European leagues, live. See this week’s matches in your local time on our matches page.',
               'نعم — الدوري المصري والسعودي ودوري الأبطال والدوريات الأوروبية الكبرى مباشرة. شاهد مباريات الأسبوع بتوقيتك المحلي في صفحة المباريات.')),
        ]
        import json as _json, html as _html, re as _re
        _plain = lambda x: _re.sub(r'<[^>]+>', '', x)
        ld = '<script type="application/ld+json">' + _json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': _plain(t(q)), 'acceptedAnswer': {'@type': 'Answer', 'text': _plain(t(a))}} for _, q, a in faq]},
            ensure_ascii=False).replace('</', '<\\/') + '</script>'
        cities_html = (f'<section class="sec"><div class="wrap"><p class="country-cities"><b>{t(_cat(L("Viewers across ", "مشاهدون في كل "), name))}</b> {t(cities)}</p></div></section>'
                       if cities else '')
        faq_html = ''.join(f'<details id="{i}"><summary>{t(q)}{icon("plus")}</summary><div class="ans"><p>{t(a)}</p></div></details>' for i, q, a in faq)
        body = hero + f'''
<section class="sec first"><div class="wrap">
  {sec_head('', t(L('Why Hossam TV', 'لماذا Hossam TV')), t(L('Made for Arabic viewers abroad', 'مصممة للمشاهد العربي في الخارج')))}
  <ul class="country-why">{why_html}</ul>
</div></section>
<section class="sec"><div class="wrap">
  {sec_head('', t(L('Plans', 'الباقات')), t(L('Plans & prices', 'الباقات والأسعار')), t(L('Prices in US dollars.', 'الأسعار بالدولار الأمريكي.')))}
  <div class="plans pgrid">{cards}</div>
  <div class="more-link"><a class="link-arrow" href="{c.href('plans.html#compare')}">{t(L('Compare all plans', 'قارن بين الباقات'))}{icon('arrow', 'flip')}</a></div>
</div></section>
<section class="sec"><div class="wrap">
  {sec_head('', t(L('Setup', 'التثبيت')), t(L('Set up in minutes', 'التثبيت في دقائق')))}
  {dev_grid(c)}
</div></section>
<section class="sec"><div class="wrap">
  {sec_head('', t(L('Matches', 'المباريات')), t(L('Big matches this week', 'أهم مباريات الأسبوع')))}
  {matches_block(c, 4)}
  <div class="more-link"><a class="link-arrow" href="{c.href('matches.html')}">{t(L('All matches', 'كل المباريات'))}{icon('arrow', 'flip')}</a></div>
</div></section>
<section class="sec"><div class="wrap">
  {sec_head('', t(L('Questions', 'أسئلة')), t(L('Good to know', 'معلومات مفيدة')))}
  <div class="faq">{faq_html}</div>
</div></section>
{cities_html}
{ld}
''' + cta_block(c)
        return (t(L('Arabic TV ', 'القنوات العربية ')) + W + t(L(' — Live Football, Arabic Channels & Movies', ' — مباريات وقنوات عربية وأفلام')),
                t(L('Watch Arabic channels, live football, movies and series ', 'شاهد القنوات العربية والمباريات المباشرة والأفلام والمسلسلات ')) + W
                + t(L(' on any screen. Free trial, setup help on WhatsApp, easy payment.', ' على أي شاشة. تجربة مجانية، ومساعدة في التثبيت على واتساب، ودفع سهل.')),
                body)
    return build


# ----------------------------------------------------------------------------
# SPEED TEST — its own page; "Fix a problem", the buffering fix and the FAQ link here.
# ----------------------------------------------------------------------------
def speed_page(c):
    t = c.t
    hero = page_hero(c, [(None, t(L('Speed test', 'اختبار السرعة')))],
                     t(L('Internet speed test', 'اختبار سرعة الإنترنت')),
                     t(L('Is your internet fast enough for HD and 4K?', 'هل الإنترنت عندك سريع كفاية لجودة HD و4K؟')))
    lb = {
        'again': L('Test again', 'اختبر مرة أخرى'), 'testing': L('Testing your download speed…', 'جاري قياس سرعة التحميل…'),
        'idle': L('Tap the play button to start', 'اضغط زر التشغيل للبدء'),
        'error': L("Couldn't run the test. Try fast.com instead.", 'تعذّر الاختبار. جرّب fast.com.'),
        'r4k': L('Great — fast enough for 4K.', 'ممتاز — كافي لجودة 4K.'),
        'rhd': L('Good for HD. For 4K, use a cable or move closer to the router.', 'كويس لجودة HD. لـ 4K استخدم كابل أو قرّب من الراوتر.'),
        'rsd': L('Enough for SD only — try the tips below.', 'يكفي لجودة SD فقط — جرّب النصائح بالأسفل.'),
        'rslow': L('Too slow — this is likely why it freezes. Try the tips below.', 'بطيء جداً — غالباً ده سبب التقطيع. جرّب النصائح بالأسفل.'),
        'ping': L('Checking the delay…', 'جاري قياس زمن الاستجابة…'),
        'magic': L('If it ever freezes, do the magic trick: unplug the router and the TV for 10 seconds, then plug them back in.',
                   'لو حصل تقطيع، اعمل الحل السحري: افصل الراوتر والشاشة من الكهرباء 10 ثواني ثم وصّلهم تاني.'),
        'stable': L('Stable', 'ثابت'), 'shaky': L('Some dips', 'فيه تذبذب'),
        'onmobile': L("You're on mobile data — to check the TV's speed, run the test on the same Wi-Fi as the TV.", 'إنت على بيانات الموبايل — عشان تعرف سرعة الشاشة، اعمل الاختبار على نفس الواي فاي اللي عليه الشاشة.'),
        'neednet': L('Choose Wi-Fi or mobile data first, then tap play.', 'اختار واي فاي أو بيانات الموبايل الأول، وبعدين اضغط زر التشغيل.'),
        'needname': L('Type your name first, then tap play.', 'اكتب اسمك الأول، وبعدين اضغط زر التشغيل.'),
    }
    attrs = ' '.join(f'data-l-{k}="{t(v)}"' for k, v in lb.items())
    # gauge: a 270° ring centred at (160,160), radius 120 (from bottom-left, clockwise to bottom-right);
    # the scale is stretched at the low end (0 5 10 25 50 100+). Logo colours: silver → red.
    marks = [0, 5, 10, 25, 50, 100]
    import math
    ticks = ''
    for i, m in enumerate(marks):
        f = i / (len(marks) - 1)
        a = math.radians(135 + 270 * f)
        x, y = 160 + 92 * math.cos(a), 160 + 92 * math.sin(a)
        ticks += f'<text x="{x:.1f}" y="{y + 4:.1f}">{m}{"+" if m == 100 else ""}</text>'
    ring = 'M75.1 244.9 A120 120 0 1 1 244.9 244.9'
    scale = ''   # fine tick marks inside the ring, longer at each number
    for i in range(51):
        a = math.radians(135 + 270 * i / 50)
        mj = i % 10 == 0
        r1, r2 = (100, 109) if mj else (104, 109)
        scale += f'<line{" class=" + chr(34) + "mj" + chr(34) if mj else ""} x1="{160 + r1 * math.cos(a):.1f}" y1="{160 + r1 * math.sin(a):.1f}" x2="{160 + r2 * math.cos(a):.1f}" y2="{160 + r2 * math.sin(a):.1f}" stroke-width="{2 if mj else 1}"/>'
    gauge = f'''<svg class="st-gauge" viewBox="0 0 320 262" aria-hidden="true">
      <defs><linearGradient id="stGrad" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset=".55" stop-color="#2563eb"/><stop offset=".8" stop-color="#7c3aed"/><stop offset="1" stop-color="#ef4444"/></linearGradient></defs>
      <circle class="st-face" cx="160" cy="160" r="112"/>
      <path class="st-arc-bg" d="{ring}"/>
      <g class="st-scale">{scale}</g>
      <path class="st-arc" data-st-arc d="{ring}"/>
      <g class="st-ticks">{ticks}</g>
      <g class="st-needle" data-st-needle><path d="M156 162 L160 58 L164 162 Z"/><circle class="st-tip" cx="160" cy="60" r="3.5"/></g>
      <circle class="st-hub" cx="160" cy="160" r="11"/><circle class="st-hub-in" cx="160" cy="160" r="4.5"/>
    </svg>'''
    # light streaks behind the dial (blue from the left, red to the right — like the speed card picture)
    streaks = '''<svg class="st-streaks" viewBox="0 0 400 200" preserveAspectRatio="none" aria-hidden="true">
      <defs><linearGradient id="stsB" x1="0" x2="1"><stop offset="0" stop-color="#1d4ed8" stop-opacity="0"/><stop offset=".6" stop-color="#3b82f6"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></linearGradient>
      <linearGradient id="stsR" x1="0" x2="1"><stop offset="0" stop-color="#7c3aed" stop-opacity="0"/><stop offset=".4" stop-color="#ef4444"/><stop offset="1" stop-color="#ef4444" stop-opacity="0"/></linearGradient></defs>
      <path d="M0 120 C80 80 120 150 200 110" stroke="url(#stsB)" stroke-width="3" fill="none"/><path d="M0 140 C90 100 130 165 200 125" stroke="url(#stsB)" stroke-width="1.5" fill="none" opacity=".7"/>
      <path d="M0 100 C70 70 130 130 200 95" stroke="url(#stsB)" stroke-width="1" fill="none" opacity=".5"/>
      <path d="M200 110 C280 70 320 140 400 95" stroke="url(#stsR)" stroke-width="3" fill="none"/><path d="M200 125 C290 95 330 155 400 115" stroke="url(#stsR)" stroke-width="1.5" fill="none" opacity=".7"/>
    </svg>'''
    # the start button is the logo tile itself (assets/img/go.webp)
    needs = [(5, 'SD', L('Basic quality', 'جودة عادية'), 'tv'), (10, 'HD', L('Full HD', 'Full HD'), 'tv'), (25, '4K', L('Ultra HD', 'Ultra HD'), '4k')]
    tiles = ''.join(f'<div class="st-need" data-need="{n}">{icon(ic)}<b>{q}</b><span dir="ltr">{n}+ Mbps</span><small>{t(d)}</small></div>' for n, q, d, ic in needs)
    tips = [('refresh', L('Do the magic trick', 'اعمل الحل السحري'), L('Unplug the router and the TV for 10 seconds, then plug them back in.', 'افصل الراوتر والشاشة من الكهرباء 10 ثواني ثم وصّلهم تاني.')),
            ('bolt', L('Use a cable or 5 GHz', 'استخدم كابل أو 5 جيجا'), L('A network cable to the TV is the most stable.', 'كابل النت للشاشة هو الأكثر ثباتاً.')),
            ('devices', L('Move closer', 'قرّب من الراوتر'), L('Or add a Wi-Fi extender near the TV.', 'أو ضع مقوّي واي فاي قرب الشاشة.')),
            ('info', L('Free up the line', 'خفّف الضغط على الخط'), L('Pause big downloads and other streams.', 'أوقف التحميلات والبث على الأجهزة الأخرى.'))]
    tips_html = ''.join(f'<li>{icon(ic)}<div><b>{t(h)}</b><span>{t(d)}</span></div></li>' for ic, h, d in tips)
    body = hero + f'''
<section class="sec first"><div class="wrap st-wrap">
  <div class="st-wifi" role="note">{icon('wifi')}<div><b>{t(L('Test on the same Wi-Fi as your TV', 'اعمل الاختبار على نفس الواي فاي اللي عليه الشاشة'))}</b>
    <span>{t(L('Connect your phone to the same network the TV uses — on mobile data the result means nothing for the TV.', 'وصّل موبايلك بنفس الشبكة اللي عليها الشاشة — نتيجة بيانات الموبايل لا تعبّر عن سرعة الشاشة.'))}</span></div></div>
  <div class="st-card" data-speedtest data-api="{N8N_WEBHOOK}site-speed" {attrs}>
    <label class="st-name"><span>{t(L('Your name', 'اسمك'))}</span>
      <input type="text" data-st-name maxlength="30" autocomplete="given-name" placeholder="{t(L('So Hossam can see your result', 'عشان حسام يشوف نتيجتك'))}"></label>
    <div class="st-net" data-st-net role="radiogroup" aria-label="{t(L('Connected through', 'متصل عن طريق'))}" hidden>
      <span>{t(L('Connected through', 'متصل عن طريق'))}</span>
      <button type="button" role="radio" aria-checked="false" data-net="wifi">📶 Wi-Fi</button>
      <button type="button" role="radio" aria-checked="false" data-net="cellular">📱 {t(L('Mobile data', 'بيانات الموبايل'))}</button>
    </div>
    <div class="st-dial">
      {streaks}
      {gauge}
      <button type="button" class="st-go" data-st-start aria-label="{t(L('Start the speed test', 'ابدأ اختبار السرعة'))}"><img src="{c.root}assets/img/go.webp" alt="" width="118" height="118"></button>
      <div class="st-readout" data-st-readout hidden dir="ltr"><b data-st-num>0</b><span>Mbps</span></div>
    </div>
    <div class="st-stats" data-st-stats hidden>
      <div><small>{t(L('Ping', 'البينج'))}</small><b dir="ltr" data-st-ping>—</b></div>
      <div><small>{t(L('Jitter', 'التذبذب'))}</small><b dir="ltr" data-st-jitter>—</b></div>
      <div><small>{t(L('Stability', 'الثبات'))}</small><b data-st-stab>—</b></div>
    </div>
    <p class="st-msg" data-st-msg aria-live="polite">{t(lb['idle'])}</p>
    <p class="st-hint" data-st-hint hidden>{icon('refresh')}<span>{t(lb['magic'])}</span></p>
    <button type="button" class="st-again" data-st-again hidden>{icon('refresh')}{t(lb['again'])}</button>
    <small class="st-note">{t(L('Delay + download test · up to 25 MB of data · about 10 seconds', 'اختبار الاستجابة والتحميل · حتى 25 ميجابايت · حوالي 10 ثواني'))}</small>
  </div>

  <section class="st-log" data-st-log hidden>
    <h2 class="st-h">{t(L('Latest tests', 'آخر الاختبارات'))}</h2>
    <div class="st-log-list" data-st-log-list></div>
  </section>

  <h2 class="st-h">{t(L('What you need', 'السرعة المطلوبة'))}</h2>
  <div class="st-needs">{tiles}</div>

  <div class="st-tips" data-st-tips>
    <h2 class="st-h">{t(L('Too slow? Try this', 'السرعة ضعيفة؟ جرّب هذا'))}</h2>
    <ul>{tips_html}</ul>
  </div>
  <a class="st-more" href="{c.href('fix.html')}">{icon('info')}<span>{t(L('Still freezing with good speed? Fix a problem', 'لسه في تقطيع والسرعة كويسة؟ حل مشكلة'))}</span>{icon('arrow', 'flip')}</a>
</div></section>
<script src="{c.root}assets/speedtest.js" defer></script>
'''
    return (t(L('Internet Speed Test — Is It Fast Enough for HD & 4K?', 'اختبار سرعة الإنترنت — هل تكفي لجودة HD و4K؟')),
            t(L('Free internet speed test: see if your connection is fast enough for SD, HD and 4K streaming, with quick tips to fix buffering.',
                'اختبار سرعة إنترنت مجاني: اعرف هل الاتصال يكفي للبث بجودة SD وHD و4K، مع نصائح سريعة لحل التقطيع.')),
            body)


# ----------------------------------------------------------------------------
# MATCH PAGES — one page per high-profile match ("Al Ahly vs Zamalek: kick-off time & channel"), made from
# assets/data/matches.json on every build. The "Update matches" GitHub Action rebuilds the site every 6 hours,
# so pages appear a week before kick-off and disappear 2 days after the final whistle.
# ----------------------------------------------------------------------------
def _match_data():
    import json, os
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'assets', 'data', 'matches.json'), encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _slug(x):
    import re, unicodedata
    x = unicodedata.normalize('NFKD', x or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', x).strip('-')


def _bot_data():
    """assets/data/bot.json: Ramadan series + match channels set from the admin bot (fetch_site.py, every 6 hours)."""
    import json, os
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'assets', 'data', 'bot.json'), encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _channel_for(league, default):
    """The admin's channel for this league ("channel: Premier League = beIN Sports 1"), else the built-in one.
    Same matching as assets/matches.js; "English / عربي" gives a name per language."""
    import re
    key = lambda x: re.sub(r'[^a-z\u0600-\u06ff]+', '', str(x or '').lower())
    names = [n for n in (key(league.get('en')), key(league.get('ar'))) if n]
    hit = None
    for k, v in (_bot_data().get('channels') or {}).items():
        kk = key(k)
        if kk and any(n == kk or kk in n or n in kk for n in names):
            hit = str(v)
    if hit:
        parts = [x.strip() for x in re.split(r'\s+/\s+', hit)]
        return {'en': parts[0], 'ar': parts[1] if len(parts) > 1 else parts[0]}
    return default or {}


def match_list():
    """[(slug, event, result-or-None)] for upcoming top matches and top results of the last 2 days."""
    from datetime import datetime, timedelta, timezone
    d = _match_data()
    now = datetime.now(timezone.utc)
    out, seen = [], set()
    for e in d.get('events', []):
        if e.get('top'):
            out.append((e, None))
    for r in d.get('results', []):
        try:
            when = datetime.fromisoformat(r['utc'].replace('Z', '+00:00'))
        except Exception:
            continue
        if r.get('top') and now - when < timedelta(days=2):
            out.append((r, r))
    pages = []
    for e, res in sorted(out, key=lambda x: x[0]['utc']):
        slug = f"{_slug(e['home']['en'])}-vs-{_slug(e['away']['en'])}-{e['utc'][:10]}"
        if slug in seen:
            continue
        seen.add(slug)
        pages.append((slug, e, res))
    return pages


def _fixed_times(utc):
    """Kick-off written out for Google (the page also shows the visitor's own time): Toronto, New York, Cairo."""
    from datetime import datetime
    try:
        from zoneinfo import ZoneInfo
        k = datetime.fromisoformat(utc.replace('Z', '+00:00'))
        f = lambda tz: k.astimezone(ZoneInfo(tz))
        tor, ny, cai = f('America/Toronto'), f('America/New_York'), f('Africa/Cairo')
        hm = lambda d: d.strftime('%I:%M %p').lstrip('0')
        return tor.strftime('%a %d %b %Y'), hm(tor), hm(ny), hm(cai), cai.strftime('%Y-%m-%d')
    except Exception:
        return utc[:10], '', '', '', utc[:10]


def match_ics(lang, e):
    """Calendar file for one match (served as <lang>/match/<slug>.ics; iPhone shows "Add to Calendar", computers open it in their calendar)."""
    from datetime import datetime, timedelta
    k = datetime.fromisoformat(e['utc'].replace('Z', '+00:00'))
    f = lambda d: d.strftime('%Y%m%dT%H%M%SZ')
    nm = lambda x: x['ar'] if lang == 'ar' else x['en']
    esc = lambda x: str(x or '').replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;')
    chd = _channel_for(e.get('league') or {}, e.get('channel'))
    ch = nm(chd) if chd else ''
    title = f"{nm(e['home'])} – {nm(e['away'])} ({nm(e['league'])})"
    note = ('شاهدها مباشرة على Hossam TV — hossamservices.com' if lang == 'ar' else 'Watch live on Hossam TV — hossamservices.com')
    return '\r\n'.join([
        'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Hossam TV//Matches//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'BEGIN:VEVENT',
        f"UID:{e['id']}@hossamservices.com", f'DTSTAMP:{f(k)}', f'DTSTART:{f(k)}', f'DTEND:{f(k + timedelta(hours=2))}',
        f'SUMMARY:{esc(title)}', f"DESCRIPTION:{esc((ch + ' · ' if ch else '') + note)}", 'URL:https://hossamservices.com/',
        'BEGIN:VALARM', 'TRIGGER:-PT30M', 'ACTION:DISPLAY', f'DESCRIPTION:{esc(title)}', 'END:VALARM',
        'END:VEVENT', 'END:VCALENDAR', ''])


def match_page(slug, e, res):
    def build(c):
        t = c.t
        H, A, LG = e['home'], e['away'], e['league']
        hn, an, lg = t(L(H['en'], H['ar'])), t(L(A['en'], A['ar'])), t(L(LG['en'], LG['ar']))
        ch = _channel_for(LG, e.get('channel'))
        chn = t(L(ch.get('en', ''), ch.get('ar', ''))) if ch else ''
        day, tor, ny, cai, _ = _fixed_times(e['utc'])
        vs = t(L('vs', 'ضد'))
        logo = lambda x: (f'<img class="nm-logo" src="{x["logo"]}" alt="" width="40" height="40" loading="lazy" onerror="this.hidden=true">'
                          if x.get('logo') else '')
        team = lambda x, n: f'<b>{logo(x)}<span>{n}</span></b>'
        if res:
            middle = (f'<span class="mp-final"><small>{t(L("Full time", "انتهت"))}</small>'
                      f'<b dir="ltr">{res["hs"] if not c.ar else res["as"]} – {res["as"] if not c.ar else res["hs"]}</b></span>')
        else:
            units = ''.join(f'<div class="nm-unit"><b data-mp-v="{u}">00</b><small>{t(L(*lbl))}</small></div>'
                            for u, lbl in (('d', ('days', 'يوم')), ('h', ('hrs', 'ساعة')), ('m', ('min', 'دقيقة')), ('s', ('sec', 'ثانية'))))
            middle = f'<span class="nm-count" data-mp-count>{units}</span>'
        fixed = (f'{day} · {tor} Toronto · {ny} New York · {cai} Cairo' if not c.ar
                 else f'{tor} تورونتو · {cai} القاهرة')
        card = f'''<div class="nextm mp-card" data-mp data-utc="{e['utc']}" data-l-live="{t(L('Live now', 'مباشر الآن'))}" data-l-mine="{t(L('Your time', 'بتوقيتك'))}">
  <span class="nm-league">{icon('ball')}<span>{lg}</span></span>
  <span class="nm-teams">{team(H, hn)}<i>{vs}</i>{team(A, an)}</span>
  {middle}
  <span class="nm-when"><time datetime="{e['utc']}" data-mp-when>{fixed}</time>{(' · ' + chn) if chn else ''}</span>
  {'' if res else '<span class="nm-actions" data-mp-cal>' + cal_link(c, e, 'nm-btn nm-cal') + '</span>'}
</div>'''
        others = ''.join(f'<li><a href="{c.href("match/" + s2 + ".html")}">{t(L(e2["home"]["en"], e2["home"]["ar"]))} {vs} {t(L(e2["away"]["en"], e2["away"]["ar"]))}</a></li>'
                         for s2, e2, r2 in match_list() if s2 != slug and not r2)
        if res:
            lead = t(L(f'{lg} · final score and where to watch the next big matches.', f'{lg} · النتيجة النهائية وأين تشاهد المباريات الكبيرة القادمة.'))
        else:
            lead = t(L(f'{lg} · kick-off in your own time zone and the TV channel.', f'{lg} · موعد المباراة بتوقيتك والقناة الناقلة.'))
        hero = page_hero(c, [(c.href('matches.html'), t(L('Matches', 'المباريات'))), (None, f'{hn} {vs} {an}')],
                         f'{hn} {vs} {an}', lead)
        # "Where to watch" — what people search for ("where to watch Al Ahly vs Zamalek in Canada"); answered on the page and for Google
        if res:
            where = f'''<div class="mp-cta">
    <p>{t(L('Watch the next big match live on your TV, phone or laptop — up to 4K.', 'شاهد المباراة الكبيرة القادمة مباشرة على الشاشة أو الموبايل أو اللابتوب — بجودة حتى 4K.'))}</p>
    {btn_trial(c)}
  </div>'''
            ld = ''
        else:
            q_where = t(L(f'Where to watch {H["en"]} vs {A["en"]} in Canada and the USA?', f'أين أشاهد مباراة {H["ar"]} و{A["ar"]} في كندا وأمريكا؟'))
            a_where = t(L(f'{H["en"]} vs {A["en"]} is live {("on " + ch.get("en", "") + " ") if ch.get("en") else ""}— watch it in Canada, the USA or anywhere with Hossam TV on your TV, phone or laptop, up to 4K, Arabic or English commentary.',
                          f'مباراة {H["ar"]} و{A["ar"]} مذاعة {("على " + ch.get("ar", "") + " ") if ch.get("ar") else ""}— شاهدها في كندا أو أمريكا أو أي مكان مع Hossam TV على الشاشة أو الموبايل أو اللابتوب بجودة حتى 4K، بتعليق عربي أو إنجليزي.'))
            q_time = t(L(f'What time is {H["en"]} vs {A["en"]}?', f'متى موعد مباراة {H["ar"]} و{A["ar"]}؟'))
            a_time = t(L(f'{day}: {tor} in Toronto, {ny} in New York and {cai} in Cairo.', f'الساعة {cai} بتوقيت القاهرة و{tor} بتوقيت تورونتو و{ny} بتوقيت نيويورك.'))
            where = f'''<div class="mp-where">
    <div class="lg-ch">{icon('tv')}<div><small>{t(L('Where to watch', 'أين تشاهدها'))}</small><b>{chn or 'Hossam TV'}</b></div>{btn_trial(c)}</div>
    <p>{a_where}</p>
  </div>'''
            ld = ld_json({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
                {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in ((q_where, a_where), (q_time, a_time))]})
        body = hero + f'''
<section class="sec first"><div class="wrap mp-wrap">
  {card}
  {where}
  {('<h2 class="st-h">' + t(L('More big matches', 'مباريات كبيرة أخرى')) + '</h2><ul class="mp-more">' + others + '</ul>') if others else ''}
  <a class="st-more" href="{c.href('matches.html')}">{icon('ball')}<span>{t(L('All matches, results & tables', 'كل المباريات والنتائج والترتيب'))}</span>{icon('arrow', 'flip')}</a>
</div></section>
<script>/* kick-off in the visitor's own time zone + countdown (Toronto / New York / Cairo are written out for search engines) */
(function(){{var b=document.querySelector('[data-mp]');if(!b)return;var k=Date.parse(b.getAttribute('data-utc')),ar=document.documentElement.lang==='ar',w=b.querySelector('[data-mp-when]'),z='';
try{{z=Intl.DateTimeFormat().resolvedOptions().timeZone||'';}}catch(e){{}}
try{{w.textContent=new Date(k).toLocaleString(ar?'ar-EG':'en-US',{{weekday:'short',day:'numeric',month:'short',hour:'numeric',minute:'2-digit',hour12:true}})+' · '+(ar||!/\\//.test(z)?b.getAttribute('data-l-mine'):z.split('/').pop().replace(/_/g,' '));}}catch(e){{}}
var c=b.querySelector('[data-mp-count]');if(!c)return;function p(n){{return(n<10?'0':'')+n;}}
function tick(){{var l=k-Date.now();if(l<=0){{var q=b.querySelector('[data-mp-cal]');if(q)q.hidden=true;c.innerHTML='';var s=document.createElement('b');s.className='mp-live';s.textContent=b.getAttribute('data-l-live');c.appendChild(s);return;}}
var v={{d:Math.floor(l/864e5),h:Math.floor(l/36e5)%24,m:Math.floor(l/6e4)%60,s:Math.floor(l/1e3)%60}};['d','h','m','s'].forEach(function(u){{c.querySelector('[data-mp-v="'+u+'"]').textContent=u==='d'?v[u]:p(v[u]);}});setTimeout(tick,1000);}}tick();}})();</script>
'''
        if res:
            title = t(L(f'{H["en"]} {res["hs"]}–{res["as"]} {A["en"]} — {LG["en"]} result',
                        f'{H["ar"]} {res["hs"]}–{res["as"]} {A["ar"]} — نتيجة {LG["ar"]}'))
            desc = t(L(f'{H["en"]} vs {A["en"]} ({LG["en"]}) ended {res["hs"]}–{res["as"]}. See the next big matches with kick-off times in your time zone and the TV channel.',
                       f'انتهت مباراة {H["ar"]} و{A["ar"]} ({LG["ar"]}) بنتيجة {res["hs"]}–{res["as"]}. شاهد مواعيد المباريات الكبيرة القادمة بتوقيتك والقناة الناقلة.'))
        else:
            title = t(L(f'Where to Watch {H["en"]} vs {A["en"]} — Time & TV Channel ({LG["en"]})',
                        f'أين تشاهد {H["ar"]} ضد {A["ar"]} — الموعد والقناة الناقلة ({LG["ar"]})'))
            desc = t(L(f'When is {H["en"]} vs {A["en"]}? {day}: {tor} Toronto, {ny} New York, {cai} Cairo{(" on " + ch.get("en", "")) if ch.get("en") else ""}. Watch it live with Hossam TV — free trial.',
                       f'موعد مباراة {H["ar"]} و{A["ar"]}: {cai} بتوقيت القاهرة و{tor} بتوقيت تورونتو{(" على " + ch.get("ar", "")) if ch.get("ar") else ""}. شاهدها مباشرة مع Hossam TV — تجربة مجانية.'))
        return title, desc, body + ld
    return build


# ----------------------------------------------------------------------------
# LEAGUE PAGES — evergreen pages for Google ("Egyptian League on TV in Canada"): table, upcoming big matches,
# last results and the channel. Rendered from assets/data/standings.json + matches.json on every build
# (the "Update matches" Action rebuilds every 6 hours), so they stay current all season.
# ----------------------------------------------------------------------------
LEAGUE_PAGES = [  # (standings id or None, matches code, slug, name EN, name AR, channel EN, channel AR)
    ('egy', 'egy.1', 'egyptian-league', 'Egyptian League', 'الدوري المصري', 'ON Time Sports', 'أون تايم سبورت'),
    ('eng', 'eng.1', 'premier-league', 'Premier League', 'الدوري الإنجليزي', 'beIN Sports', 'بي إن سبورت'),
    ('esp', 'esp.1', 'la-liga', 'La Liga', 'الدوري الإسباني', 'beIN Sports', 'بي إن سبورت'),
    ('ksa', 'ksa.1', 'saudi-pro-league', 'Saudi Pro League', 'دوري روشن السعودي', 'Thmanyah', 'ثمانية'),
    ('ucl', 'uefa.champions', 'champions-league', 'Champions League', 'دوري أبطال أوروبا', 'beIN Sports', 'بي إن سبورت'),
    ('ita', 'ita.1', 'serie-a', 'Serie A', 'الدوري الإيطالي', 'beIN Sports', 'بي إن سبورت'),
    ('ger', 'ger.1', 'bundesliga', 'Bundesliga', 'الدوري الألماني', 'beIN Sports', 'بي إن سبورت'),
    ('fra', 'fra.1', 'ligue-1', 'Ligue 1', 'الدوري الفرنسي', 'beIN Sports', 'بي إن سبورت'),
    (None, 'caf.champions', 'caf-champions-league', 'CAF Champions League', 'دوري أبطال أفريقيا', 'beIN Sports', 'بي إن سبورت'),
]


def _standings():
    import json, os
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'assets', 'data', 'standings.json'), encoding='utf-8') as f:
            return {l['id']: l for l in json.load(f).get('leagues', [])}
    except Exception:
        return {}


def _when_html(c, utc):
    """A <time> the page script turns into the visitor's own time; Toronto + Cairo are written for search engines."""
    day, tor, ny, cai, _ = _fixed_times(utc)
    txt = f'{day} · {tor} Toronto · {cai} Cairo' if not c.ar else f'{tor} تورونتو · {cai} القاهرة'
    return f'<time datetime="{utc}" data-local>{txt}</time>'


LOCAL_TIME_JS = """<script>/* every <time data-local> -> the visitor's own time zone */
(function(){var ar=document.documentElement.lang==='ar',z='';try{z=Intl.DateTimeFormat().resolvedOptions().timeZone||'';}catch(e){}
var lbl=ar||!/\\//.test(z)?(ar?'بتوقيتك':'your time'):z.split('/').pop().replace(/_/g,' ');
Array.prototype.forEach.call(document.querySelectorAll('time[data-local]'),function(t){try{t.textContent=new Date(t.getAttribute('datetime')).toLocaleString(ar?'ar-EG':'en-US',{weekday:'short',day:'numeric',month:'short',hour:'numeric',minute:'2-digit',hour12:true})+' · '+lbl;}catch(e){}});})();</script>"""



CLOCK_SVG = '<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
CAL_SVG = '<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3.5 10h17M8 3v4M16 3v4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'


def cal_link(c, e, cls='mt-cal', label=None):
    """"Add to calendar": the match's .ics file (<lang>/cal/<id>.ics, built for every match); Android opens Google Calendar (assets/matches.js)."""
    import html
    nm = lambda x: c.t(L(x['en'], x.get('ar') or x['en']))
    title = f"{nm(e['home'])} – {nm(e['away'])} ({nm(e['league'])})"
    return (f'<a class="{cls}" href="{c.href("cal/" + str(e["id"]) + ".ics")}" data-cal="{e["utc"]}" data-cal-t="{html.escape(title)}">'
            f'{CAL_SVG}{label or c.t(L("Add to calendar", "أضف للتقويم"))}</a>')


def mt_act(c, e):
    """Countdown + "Add to calendar" under one match row (ticked by assets/matches.js; hidden once it kicks off)."""
    return f'<span class="mt-act"><span class="mt-cd" data-cd="{e["utc"]}">{CLOCK_SVG}</span>{cal_link(c, e)}</span>'


def _mt_row(c, e, res=None):
    """One aligned match row (same look as the matches list): home | score or "vs" | away, with logos."""
    import html, re
    def team(x, side):
        n = c.t(L(x['en'], x.get('ar') or x['en']))
        first = (re.sub(r'^(?:al|el|ال)[\s-]?', '', n, flags=re.I)[:1] or '?').upper()
        ini = f'<span class="mt-logo mt-ini" aria-hidden="true">{html.escape(first)}</span>'   # no badge: the first letter
        img = (f'<img class="mt-logo" src="{html.escape(x["logo"])}" alt="" width="24" height="24" loading="lazy" '
               f'onerror="this.outerHTML=\'{ini.replace(chr(34), "&quot;")}\'">' if x.get('logo') else ini)
        return f'<span class="mt-team mt-{side}">{img}<span class="mt-name{" mt-long" if any(len(w) > 10 for w in n.split()) else ""}">{html.escape(n)}</span></span>'
    if res:
        mid = f'<b class="match-score">{res["as"] if c.ar else res["hs"]} – {res["hs"] if c.ar else res["as"]}</b>'
    else:
        mid = f'<span class="mt-vs">{c.t(L("vs", "ضد"))}</span>'
    return f'<span class="mt-row">{team(e["home"], "home")}<span class="mt-mid">{mid}</span>{team(e["away"], "away")}</span>'

def league_page(sid, code, slug, n_en, n_ar, ch_en, ch_ar):
    def build(c):
        t = c.t
        st = (_standings().get(sid) or {}) if sid else {}
        md = _match_data()
        nm = {'en': n_en, 'ar': n_ar}
        chd = _channel_for(nm, {'en': ch_en, 'ar': ch_ar})
        c_en, c_ar = chd['en'], chd['ar']
        ln = t(L(nm['en'], nm['ar']))
        vs = t(L('vs', 'ضد'))
        name = lambda x: t(L(x['en'], x['ar']))
        # table (rendered in the page so search engines read it)
        rows = ''.join(
            f'<tr><td class="tb-rank">{r["rank"]}</td><td class="tb-team"><div class="tb-tm">'
            + (f'<img src="{r["logo"]}" alt="" width="22" height="22" loading="lazy" onerror="this.style.visibility=\'hidden\'">' if r.get('logo') else '')
            + f'<span>{t(L(r["en"], r.get("ar") or r["en"]))}</span></div></td><td class="tb-num">{r["p"]}</td><td class="tb-num" dir="ltr">{r["gd"]}</td><td class="tb-pts">{r["pts"]}</td></tr>'
            for r in st.get('rows', []))
        table = (f'<h2 class="st-h">{t(L("Table", "الترتيب"))}</h2><div class="tb-wrap"><table class="tb"><thead><tr><th>#</th><th class="tb-team">{t(L("Team", "الفريق"))}</th>'
                 f'<th>{t(L("P", "لعب"))}</th><th>{t(L("GD", "الفارق"))}</th><th>{t(L("Pts", "نقاط"))}</th></tr></thead><tbody>{rows}</tbody></table></div>') if rows else ''
        # upcoming big matches of this league
        mp = {e['id']: sl for sl, e, r in match_list() if not r}
        ups = [e for e in md.get('events', []) if e.get('code') == code]
        items = []
        for e in ups:
            inner = _mt_row(c, e) + f'<small>{_when_html(c, e["utc"])}</small>'
            items.append((f'<li><a href="{c.href("match/" + mp[e["id"]] + ".html")}">{inner}</a>' if e['id'] in mp else f'<li><div>{inner}</div>') + mt_act(c, e) + '</li>')
        upcoming = (f'<h2 class="st-h">{t(L("Upcoming big matches", "المباريات الكبيرة القادمة"))}</h2><ul class="lg-list">{"".join(items)}</ul>') if items else ''
        res = [r for r in md.get('results', []) if r.get('league', {}).get('en') == nm['en']]
        res_html = ''.join(f'<li><div>{_mt_row(c, r, r)}</div></li>' for r in res[:5])
        results = (f'<h2 class="st-h">{t(L("Last results", "آخر النتائج"))}</h2><ul class="lg-list">{res_html}</ul>') if res_html else ''
        chn = t(L(c_en, c_ar))
        others = ''.join(f'<a class="tb-tab" href="{c.href("league/" + s2 + ".html")}">{t(L(e2, a2))}</a>'
                         for _, _, s2, e2, a2, _, _ in LEAGUE_PAGES if s2 != slug)
        hero = page_hero(c, [(c.href('matches.html'), t(L('Matches', 'المباريات'))), (None, ln)],
                         t(L(f'{nm["en"]} on TV — live in Canada, the USA & worldwide', f'{nm["ar"]} مباشر — في كندا وأمريكا وحول العالم')),
                         t(L(f'Every match live on {c_en} with Hossam TV, plus the table and kick-off times in your time zone.',
                             f'كل المباريات مباشرة على {c_ar} مع Hossam TV، مع الترتيب ومواعيد المباريات بتوقيتك.')))
        body = hero + f"""
<section class="sec first"><div class="wrap mp-wrap">
  <div class="lg-ch">{icon('tv')}<div><small>{t(L('Channel', 'القناة'))}</small><b>{chn}</b></div>{btn_trial(c)}</div>
  {upcoming}
  {table}
  {results}
  <h2 class="st-h">{t(L('Other leagues', 'دوريات أخرى'))}</h2>
  <div class="tb-tabs lg-others">{others}</div>
  <a class="st-more" href="{c.href('matches.html')}">{icon('ball')}<span>{t(L('All matches, results & tables', 'كل المباريات والنتائج والترتيب'))}</span>{icon('arrow', 'flip')}</a>
</div></section>
{LOCAL_TIME_JS}
"""
        title = t(L(f'{nm["en"]} on TV in Canada & the USA — Live, {"Table & " if sid else ""}Kick-off Times',
                    f'{nm["ar"]} مباشر في كندا وأمريكا — {"الترتيب و" if sid else ""}مواعيد المباريات والقناة'))
        desc = t(L(f'Watch the {nm["en"]} live in Canada, the USA and worldwide on {c_en}. Current table, upcoming big matches in your time zone and last results — free trial with Hossam TV.',
                   f'شاهد {nm["ar"]} مباشرة في كندا وأمريكا وحول العالم على {c_ar}. الترتيب الحالي ومواعيد المباريات الكبيرة بتوقيتك وآخر النتائج — تجربة مجانية مع Hossam TV.'))
        return title, desc, body
    return build


# ----------------------------------------------------------------------------
# RAMADAN SERIES — every series with its poster and the day it starts (no channels, no times). Fully automatic:
# _source/matches/fetch_ramadan.py collects them from elCinema + Wikipedia once a day ("Update matches" Action) into
# assets/data/ramadan.json. The page is built from that file and assets/ramadan.js re-reads it on every visit
# (the site's copy, else a CDN copy of the same file, else what was written into the HTML).
# Before this Ramadan starts, last Ramadan's series are shown too ("watch again").
# ----------------------------------------------------------------------------
RAMADAN = [  # (first day, last day, Hijri year) — expected dates; the exact start depends on the moon sighting
    ('2026-02-18', '2026-03-19', 1447),
    ('2027-02-08', '2027-03-09', 1448),
    ('2028-01-28', '2028-02-25', 1449),
    ('2029-01-16', '2029-02-13', 1450),
]
MONTHS_AR = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']


def ramadan_season(today=None):
    """(start, end, year) of the Ramadan to show: the next one, the current one, or the one that ended < 2 weeks ago."""
    from datetime import date, timedelta
    today = today or date.today()
    for a, b, _ in RAMADAN:
        if date.fromisoformat(b) + timedelta(days=14) >= today:
            return date.fromisoformat(a), date.fromisoformat(b), date.fromisoformat(a).year
    a, b, _ = RAMADAN[-1]
    return date.fromisoformat(a), date.fromisoformat(b), date.fromisoformat(a).year


def _rm_status(c, today=None):
    from datetime import date
    today = today or date.today()
    a, b, yr = ramadan_season(today)
    if today < a:
        n = (a - today).days
        day = a.strftime('%a %-d %b %Y') if not c.ar else f'{a.day} {MONTHS_AR[a.month - 1]} {a.year}'
        return c.t(L(f'Ramadan starts in about {n} days — expected {day}', f'باقي حوالي {n} يوم على رمضان — متوقع {day}'))
    if today <= b:
        n = (today - a).days + 1
        return c.t(L(f'Day {n} of Ramadan — Ramadan Kareem', f'اليوم {n} من رمضان — رمضان كريم'))
    return c.t(L(f'Ramadan {yr} has ended — see you next year', f'انتهى رمضان {yr} — نراكم العام القادم'))


def _rm_data():
    import json, os
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'assets', 'data', 'ramadan.json'), encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _rm_date(c, iso):
    """'2027-02-08' -> 'Mon, Feb 8' / 'الاثنين 8 فبراير'."""
    from datetime import date
    try:
        d = date.fromisoformat(iso)
    except Exception:
        return ''
    days_ar = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
    return f'{days_ar[d.weekday()]} {d.day} {MONTHS_AR[d.month - 1]}' if c.ar else d.strftime('%a, %b %-d')


def _rm_cards(c, items, start):
    import html
    esc = lambda x: html.escape(str(x or ''))
    out = []
    for x in items:
        main = (x.get('ar') or x.get('en')) if c.ar else (x.get('en') or x.get('ar'))
        other = x.get('en') if c.ar else x.get('ar')
        hue = sum(map(ord, str(x.get('ar') or x.get('en')))) % 6
        out.append(f'<li class="rm-card"><div class="rm-poster rm-h{hue}"><span class="rm-gen" aria-hidden="true">{icon("moon")}<em class="rm-nopo">{c.t(L("No poster yet", "لا يوجد بوستر بعد"))}</em><b>{esc(main)}</b></span>'
                   + (f'<img src="{esc(x["poster"])}" alt="{esc(main)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">' if x.get('poster') else '')
                   + f'</div><div class="rm-info"><b class="rm-title">{esc(main)}</b>'
                   + (f'<small>{esc(other)}</small>' if other and other != main else '')
                   + f'<span class="rm-t">{esc(_rm_date(c, x.get("date") or start))}</span>'
                   + (f'<small class="rm-stars">{esc(x.get("stars"))}</small>' if x.get('stars') else '') + '</div></li>')
    return ''.join(out)


def ramadan_page(c):
    from datetime import date
    t = c.t
    a, b, yr = ramadan_season()
    d = _rm_data()
    cur = (d.get('season') or {}) if (d.get('season') or {}).get('year') == yr else {}
    last = d.get('last') or {}
    cur_items = cur.get('series') or []
    last_items = ((last.get('series') or []) if last.get('year') == yr - 1 else [])[:last.get('top') or 48]   # the most popular
    show_last = date.today() < a or not cur_items
    labels = {'new': t(L('New', 'جديد')),
              'before': t(L('Ramadan starts in about {n} days — expected {d}', 'باقي حوالي {n} يوم على رمضان — متوقع {d}')),
              'during': t(L('Day {n} of Ramadan — Ramadan Kareem', 'اليوم {n} من رمضان — رمضان كريم')),
              'after': t(L('Ramadan {y} has ended — see you next year', 'انتهى رمضان {y} — نراكم العام القادم'))}
    hero = page_hero(c, [(None, t(L('Ramadan series', 'مسلسلات رمضان')))],
                     t(L(f'Ramadan {yr} series', f'مسلسلات رمضان {yr}')),
                     t(L('Every series and the day it starts — all on Hossam TV.', 'كل المسلسلات وموعد بدايتها — كلها على Hossam TV.')))
    body = hero + f'''
<section class="sec first rm-sec"><div class="wrap rm-wrap" data-rm data-start="{a.isoformat()}" data-end="{b.isoformat()}" data-year="{yr}" data-l="{html_attr_json(labels)}" data-src="{c.root}assets/data/ramadan.json" data-cdn="https://cdn.jsdelivr.net/gh/hossamurai/hossamurai.github.io@main/assets/data/ramadan.json">
  <div class="lg-ch rm-status">{icon('moon')}<div><small>{t(L('Ramadan', 'رمضان'))} {yr}</small><b data-rm-status>{_rm_status(c)}</b></div>{btn_trial(c)}</div>
  <ul class="rm-list" data-rm-list="season">{_rm_cards(c, cur_items, a.isoformat())}</ul>
  <p class="rm-empty" data-rm-empty{' hidden' if cur_items else ''}>{t(L('This year’s series appear here as they are announced — automatically.', 'مسلسلات هذا العام تظهر هنا أول ما يتم الإعلان عنها — تلقائياً.'))}</p>
  <div class="rm-last" data-rm-last{'' if show_last and last_items else ' hidden'}>
    <h2 class="rm-h">{t(L(f'Ramadan {yr - 1} — watch again', f'رمضان {yr - 1} — شاهدها من جديد'))}</h2>
    <ul class="rm-list" data-rm-list="last">{_rm_cards(c, last_items, last.get('start') or '')}</ul>
  </div>
  <p class="matches-note">{t(L('Updated automatically.', 'يتم التحديث تلقائياً.'))}</p>
</div></section>
<script src="{c.root}assets/ramadan.js" defer></script>
''' + cta_block(c)
    return (t(L(f'Ramadan {yr} Series — Full List & Start Dates', f'مسلسلات رمضان {yr} — القائمة الكاملة ومواعيد العرض')),
            t(L(f'All Ramadan {yr} series with posters and the day each one starts, plus last year’s series. Watch them in Canada, the USA or anywhere with Hossam TV.',
                f'كل مسلسلات رمضان {yr} بالبوسترات وموعد بداية كل مسلسل، ومسلسلات العام الماضي. شاهدها في كندا أو أمريكا أو أي مكان مع Hossam TV.')),
            body)


def ramadan_teaser(c):
    """Slim link on the home page from 60 days before Ramadan until it ends (the site is rebuilt every 6 hours)."""
    from datetime import date, timedelta
    a, b, yr = ramadan_season()
    if not (a - timedelta(days=60) <= date.today() <= b):
        return ''
    return (f'<section class="sec rm-teaser-sec"><div class="wrap"><a class="st-more rm-teaser" href="{c.href("ramadan-series.html")}">{icon("moon")}'
            f'<span>{c.t(L(f"Ramadan {yr} series", f"مسلسلات رمضان {yr}"))}</span>{icon("arrow", "flip")}</a></div></section>')

def fix_page(c):
    # the step-by-step troubleshooter; markup holds both languages (.en/.ar), CSS is scoped under .fixp
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fix')
    html = open(os.path.join(d, 'body.html'), encoding='utf-8').read()
    css = open(os.path.join(d, 'fix.css'), encoding='utf-8').read()
    html = html.replace('data-page="speed-test.html" href="/"', f'data-page="speed-test.html" href="{c.href("speed-test.html")}"')
    body = f'''<style>{theme_css(css)}</style>
<div class="fixp">
{html}
</div>
<script src="{c.root}assets/fix.js" defer></script>'''
    return (c.t(L('Fix a problem', 'حل مشكلة')),
            c.t(L('Step-by-step fixes for freezing, login and app problems.', 'حلول خطوة بخطوة للتقطيع ومشاكل الدخول والتطبيقات.')),
            body)


PAGE_BUILDERS = [
    ('home', 'index.html', 'home', home),
    ('plans', 'plans.html', 'plans', plans),
    ('channels', 'channels.html', 'channels', channels),
    ('setup', 'setup/index.html', 'setup', setup_index),
    ('help', 'help.html', 'help', help_page),
    ('fix', 'fix.html', 'fix', fix_page),
    ('about', 'about.html', 'about', about),
    ('policies', 'policies.html', None, policies),
]
PAGE_BUILDERS += [('matches', 'matches.html', 'matches', matches_page), ('speed', 'speed-test.html', 'speed', speed_page)]
PAGE_BUILDERS += [('ramadan', 'ramadan-series.html', None, ramadan_page)]
PAGE_BUILDERS += [('tv-' + sl, 'arabic-tv-' + sl + '.html', None, country_page(sl, nm, wh, tz, ct)) for sl, nm, wh, tz, ct in COUNTRY_PAGES]
MATCH_PAGES = [('match-' + sl, 'match/' + sl + '.html', 'matches', match_page(sl, e, r)) for sl, e, r in match_list()]
PAGE_BUILDERS += MATCH_PAGES
PAGE_BUILDERS += [('league-' + x[2], 'league/' + x[2] + '.html', 'matches', league_page(*x)) for x in LEAGUE_PAGES]
DEVICE_PAGES = [('setup-' + d['slug'], 'setup/' + d['slug'] + '.html', 'setup', device_page(d['slug'])) for d in DEVICES]
