/* Hossam TV — shared behaviour (ES5 so it also runs on older TV browsers) */
(function(){
  'use strict';
  var doc = document.documentElement;
  var AR = doc.lang === 'ar';

  function store(k, v){
    try{ if(v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); }catch(e){ return null; }
  }
  function each(sel, fn, root){ Array.prototype.forEach.call((root || document).querySelectorAll(sel), fn); }

  /* remember language when the visitor switches */
  each('[data-setlang]', function(a){
    a.addEventListener('click', function(){ store('htv-lang', a.getAttribute('data-setlang')); });
  });

  /* mobile menu */
  var nav = document.querySelector('.nav'), menuBtn = document.getElementById('menuBtn');
  if(nav && menuBtn){
    var setMenu = function(open){
      nav.classList.toggle('open', open);
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    menuBtn.addEventListener('click', function(){ setMenu(!nav.classList.contains('open')); });
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape') setMenu(false); });
    document.addEventListener('click', function(e){ if(!nav.contains(e.target)) setMenu(false); });
  }

  /* region switcher (plan cards) */
  var REGION_KEY = 'htv-region';
  function detectRegion(){
    var tz = '';
    try{ tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; }catch(e){}
    return tz === 'Africa/Cairo' ? 'eg' : 'intl';
  }
  function setRegion(id, save){
    each('[data-region-btn]', function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-region-btn') === id ? 'true' : 'false'); });
    each('[data-region-panel]', function(p){ p.hidden = p.getAttribute('data-region-panel') !== id; });
    if(save) store(REGION_KEY, id);
  }
  /* ISO country (Cloudflare) -> dial code used by the forms' country lists ('ca'/'us' in the trial form, '1' in the phone box) */
  var ISO_DIAL = { EG:'20', SA:'966', AE:'971', KW:'965', QA:'974', BH:'973', OM:'968', JO:'962', LB:'961', IQ:'964', PS:'970', SY:'963', YE:'967',
    SD:'249', LY:'218', TN:'216', DZ:'213', MA:'212', TR:'90', GB:'44', DE:'49', FR:'33', NL:'31', BE:'32', CH:'41', AT:'43', SE:'46', NO:'47',
    DK:'45', IT:'39', ES:'34', IE:'353', AU:'61', CA:'1', US:'1' };
  /* country code (from Cloudflare via site-data, by IP) -> prices tab */
  function regionOf(cc){ return cc === 'EG' ? 'eg' : 'intl'; }
  /* visitors in the UAE (by IP): we stopped serving it */
  var aeNote = function(iso){ if(iso === 'AE') each('[data-ae-note]', function(n){ n.hidden = false; }); };
  aeNote(window.htvCountry); document.addEventListener('htv:country', function(e){ aeNote(e.detail); });
  if(document.querySelector('[data-region-panel]')){
    var r = store(REGION_KEY);
    /* a tab the visitor tapped wins; then the real country (when site-data arrives); the phone's time zone is only the first guess */
    var chose = !!document.querySelector('[data-region-panel="' + r + '"]');
    if(!chose) r = window.htvCountry ? regionOf(window.htvCountry) : detectRegion();
    setRegion(r, false);
    if(!chose) document.addEventListener('htv:country', function(e){ if(!store(REGION_KEY)) setRegion(regionOf(e.detail), false); });
    each('[data-region-btn]', function(b){
      b.addEventListener('click', function(){ setRegion(b.getAttribute('data-region-btn'), true); });
    });
  }

  /* "Canada & rest of world" prices are in USD: next to them, the rough amount in the visitor's own currency
     (country from Cloudflare by IP via site-data; until it arrives, Canada from the time zone). Rates refreshed once a day. */
  var EURO = /^(DE|FR|NL|BE|AT|IT|ES|IE|PT|FI|GR|LU|SK|SI|EE|LV|LT|MT|CY|HR)$/;
  var CUR = { CA: 'CAD', GB: 'GBP', AU: 'AUD', NZ: 'NZD', CH: 'CHF', SE: 'SEK', NO: 'NOK', DK: 'DKK', PL: 'PLN', TR: 'TRY', SA: 'SAR', AE: 'AED',
    KW: 'KWD', QA: 'QAR', BH: 'BHD', OM: 'OMR', JO: 'JOD', IQ: 'IQD', MA: 'MAD', DZ: 'DZD', TN: 'TND', LY: 'LYD', EG: 'EGP', MX: 'MXN', BR: 'BRL',
    IN: 'INR', PK: 'PKR', MY: 'MYR', ZA: 'ZAR', JP: 'JPY' };
  function curOf(iso){ return EURO.test(iso || '') ? 'EUR' : CUR[iso] || ''; }
  function curName(code){
    if(code === 'CAD') return AR ? 'دولار كندي' : 'CAD';
    if(!AR) return code;
    try{ return new Intl.DisplayNames(['ar'], { type: 'currency' }).of(code) || code; }catch(e){ return code; }
  }
  var fxRates = null; try{ fxRates = JSON.parse(store('htv-fx') || 'null'); }catch(e){}
  var fxWait = null;
  /* the day's USD rates (cached one day); cb runs when they're in */
  function fxLoad(cb){
    if(fxRates && Date.now() - fxRates.t < 864e5){ if(cb) cb(); return; }
    if(!window.fetch) return;
    if(!fxWait) fxWait = fetch('https://open.er-api.com/v6/latest/USD').then(function(r){ return r.json(); }).then(function(d){
      if(d && d.rates && d.rates.CAD){ fxRates = { r: d.rates, t: Date.now() }; store('htv-fx', JSON.stringify(fxRates)); }
    })['catch'](function(){});
    if(cb) fxWait.then(cb);
  }
  /* "≈ 48 CAD" for a USD amount in a given currency, or '' */
  function fxMoney(usd, cur){
    var rate = cur && fxRates && fxRates.r && fxRates.r[cur];
    if(!rate && cur === 'CAD') rate = 1.38;
    if(!rate || cur === 'USD') return '';
    var n = usd * rate, r = n >= 1000 ? Math.round(n / 10) * 10 : Math.round(n);
    return '≈ ' + (cur === 'CAD' && !AR ? '$' + r.toLocaleString('en-US') + ' CAD' : r.toLocaleString('en-US') + ' ' + curName(cur));
  }
  window.htvMoney = function(usd){ var l = window.htvLocal; return l ? fxMoney(usd, l.cur) : ''; };   /* in the visitor's currency */
  (function(){
    var spans = document.querySelectorAll('[data-cad]');
    var tz = ''; try{ tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; }catch(e){}
    var canada = /^America\/(Toronto|Montreal|Vancouver|Edmonton|Calgary|Winnipeg|Regina|Swift_Current|Halifax|Moncton|Glace_Bay|Goose_Bay|St_Johns|Whitehorse|Dawson|Dawson_Creek|Fort_Nelson|Creston|Yellowknife|Inuvik|Iqaluit|Rankin_Inlet|Cambridge_Bay|Resolute|Atikokan|Nipigon|Thunder_Bay|Rainy_River|Pangnirtung|Blanc-Sablon)$/.test(tz);
    var cur = '';
    function show(){
      var r = cur && fxRates && fxRates.r && fxRates.r[cur];
      if(!r && cur === 'CAD') r = 1.38;
      window.htvLocal = r ? { cur: cur, rate: r } : null;
      if(r) window.htvCadRate = cur === 'CAD' ? r : 0;
      try{ document.dispatchEvent(new CustomEvent('htv:cad')); }catch(e){}
      Array.prototype.forEach.call(spans, function(s){
        if(!r){ s.hidden = true; return; }
        s.textContent = s.hasAttribute('data-cad-short') ? (AR ? ' أمريكي' : ' USD')       /* the 2-year price: just name the currency */
          : (AR ? ' أمريكي (' : ' USD (') + window.htvMoney(+s.getAttribute('data-cad')) + ')';
        s.hidden = false;
      });
    }
    function setCountry(iso){
      var c = curOf(iso); if(c === cur) return; cur = c; show();
      if(cur) fxLoad(show);
    }
    setCountry(window.htvCountry || (canada ? 'CA' : ''));
    document.addEventListener('htv:country', function(e){ setCountry(e.detail); });
  })();

  /* savings calculator (plans page): cable/satellite bill vs Hossam TV Basic, in CAD for visitors in Canada */
  (function(){
    var box = document.querySelector('[data-savings]');
    if(!box) return;
    var range = box.querySelector('[data-bill-range]'), bill = box.querySelector('[data-bill]'), save = box.querySelector('[data-save]'), note = box.querySelector('[data-calc-note]');
    var basic = +box.getAttribute('data-basic') || 35;
    function money(n){ var l = window.htvLocal; return l && l.cur !== 'CAD' ? Math.round(n).toLocaleString('en-US') + ' ' + l.cur : '$' + Math.round(n).toLocaleString('en-US') + (l ? ' CAD' : ''); }
    function upd(){
      var rate = window.htvLocal ? window.htvLocal.rate : 1, month = +range.value, year = month * 12, plan = basic * rate;
      bill.textContent = money(month);
      save.textContent = money(Math.max(0, year - plan));
      note.textContent = note.getAttribute('data-l').replace('{y}', money(year)).replace('{b}', money(plan));
      range.style.setProperty('--p', ((month - range.min) / (range.max - range.min) * 100) + '%');
    }
    range.addEventListener('input', upd);
    document.addEventListener('htv:cad', upd);
    upd();
  })();

  /* plan tabs (setup pages) — the chosen plan is remembered across device pages */
  var PLAN_KEY = 'htv-plan';
  function setPlan(id, save){
    each('[data-plan-btn]', function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-plan-btn') === id ? 'true' : 'false'); });
    each('[data-panel]', function(p){ p.hidden = p.getAttribute('data-panel') !== id; });
    if(save) store(PLAN_KEY, id);
  }
  if(document.querySelector('[data-plan-btn]')){
    var saved = store(PLAN_KEY);
    if(saved && document.querySelector('[data-panel="' + saved + '"]')) setPlan(saved, false);
    each('[data-plan-btn]', function(b){
      b.addEventListener('click', function(){ setPlan(b.getAttribute('data-plan-btn'), true); });
    });
  }

  /* copy-to-clipboard for app codes */
  var toastEl = document.getElementById('toast'), toastT;
  function toast(msg){
    if(!toastEl) return;
    toastEl.textContent = msg; toastEl.classList.add('show');
    clearTimeout(toastT); toastT = setTimeout(function(){ toastEl.classList.remove('show'); }, 1400);
  }
  function copy(text){
    var done = function(){ toast(AR ? 'تم النسخ' : 'Copied'); };
    var fallback = function(){
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try{ document.execCommand('copy'); done(); }catch(e){}
      document.body.removeChild(ta);
    };
    if(navigator.clipboard && window.isSecureContext){ navigator.clipboard.writeText(text).then(done, fallback); }
    else fallback();
  }
  document.addEventListener('click', function(e){
    var c = e.target.closest ? e.target.closest('[data-copy]') : null;
    if(c){ e.preventDefault(); copy(c.getAttribute('data-copy')); }
  });

  /* help-page search */
  var q = document.getElementById('helpSearch');
  if(q){
    var empty = document.getElementById('helpEmpty');
    var norm = function(s){ return (s || '').toLowerCase().replace(/[ً-ْ]/g, '').replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي'); };
    q.addEventListener('input', function(){
      var term = norm(q.value.trim()), shown = 0;
      each('[data-search-item]', function(it){
        var hit = !term || norm(it.textContent + ' ' + (it.getAttribute('data-k') || '')).indexOf(term) > -1;
        it.hidden = !hit; if(hit) shown++;
        if(it.tagName === 'DETAILS'){
          if(term && hit && !it.open){ it.open = true; it.setAttribute('data-auto', ''); }
          else if(!term && it.hasAttribute('data-auto')){ it.open = false; it.removeAttribute('data-auto'); }
        }
      });
      each('[data-search-group]', function(g){
        g.hidden = !g.querySelector('[data-search-item]:not([hidden])');
      });
      if(empty) empty.style.display = shown ? 'none' : 'block';
    });
  }

  /* open a FAQ/troubleshooting item when linked directly (#id) */
  if(location.hash){
    var target = document.getElementById(location.hash.slice(1));
    if(target && target.tagName === 'DETAILS') target.open = true;
  }

  var yr = document.getElementById('yr');
  if(yr) yr.textContent = new Date().getFullYear();
  /* renewal reminders: username + password + WhatsApp number are checked by n8n (site-link webhook),
     which saves the number on the account in the Customers table. Nothing is stored on the website. */
  each('[data-remind]', function(f){
    var user = f.querySelector('[name="username"]'), pass = f.querySelector('[name="password"]'), phone = f.querySelector('[name="phone"]');
    var cc = f.querySelector('[name="cc"]');
    /* preselect the country code from the visitor's time zone (no location permission needed) */
    if(cc){
      var tz = ''; try{ tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; }catch(e){}
      var TZ_CC = { 'Africa/Cairo':'20', 'Asia/Riyadh':'966', 'Asia/Dubai':'971', 'Asia/Kuwait':'965', 'Asia/Qatar':'974', 'Asia/Bahrain':'973',
        'Asia/Muscat':'968', 'Asia/Amman':'962', 'Asia/Beirut':'961', 'Asia/Baghdad':'964', 'Asia/Gaza':'970', 'Asia/Hebron':'970',
        'Asia/Damascus':'963', 'Asia/Aden':'967', 'Africa/Khartoum':'249', 'Africa/Tripoli':'218', 'Africa/Tunis':'216', 'Africa/Algiers':'213',
        'Africa/Casablanca':'212', 'Europe/Istanbul':'90', 'Europe/London':'44', 'Europe/Berlin':'49', 'Europe/Paris':'33', 'Europe/Amsterdam':'31',
        'Europe/Brussels':'32', 'Europe/Zurich':'41', 'Europe/Vienna':'43', 'Europe/Stockholm':'46', 'Europe/Oslo':'47', 'Europe/Copenhagen':'45',
        'Europe/Rome':'39', 'Europe/Madrid':'34', 'Europe/Dublin':'353' };
      var code = TZ_CC[tz] || (/^America\/(New_York|Chicago|Denver|Los_Angeles|Phoenix|Anchorage|Detroit|Toronto|Vancouver|Edmonton|Winnipeg|Halifax|Regina|St_Johns|Indiana|Kentucky|Boise)/.test(tz) ? '1' : '')
        || (/^Australia\//.test(tz) ? '61' : '');
      if(code && cc.querySelector('option[value="' + code + '"]')) cc.value = code;
      cc.setAttribute('data-home', cc.value);
      /* the closed box only shows the code (e.g. +1); the list still shows country names */
      var ccShow = f.querySelector('.cc-show');
      var showCc = function(){ if(ccShow) ccShow.textContent = '+' + cc.value; };
      cc.addEventListener('change', showCc); showCc();
      var ccTouched = false; cc.addEventListener('change', function(e){ if(e.isTrusted) ccTouched = true; });
      var ccFromIp = function(iso){ var d = ISO_DIAL[iso]; if(!ccTouched && d && cc.querySelector('option[value="' + d + '"]')){ cc.value = d; cc.setAttribute('data-home', d); showCc(); } };
      if(window.htvCountry) ccFromIp(window.htvCountry);
      document.addEventListener('htv:country', function(e){ ccFromIp(e.detail); });
      f.addEventListener('reset', function(){ setTimeout(showCc, 0); });
    }
    var hp = f.querySelector('[name="website"]'), msg = f.querySelector('.remind-msg'), btn = f.querySelector('[type="submit"]'), show = f.querySelector('.remind-show');
    var busy = false;
    function say(key, ok){
      msg.textContent = msg.getAttribute('data-msg-' + key) || '';
      msg.className = 'remind-msg' + (ok ? ' ok' : ' err');
      msg.hidden = false;
    }
    function bad(el, on){ el.setAttribute('aria-invalid', on ? 'true' : 'false'); }
    if(show) show.addEventListener('click', function(){
      var on = pass.type === 'password';
      pass.type = on ? 'text' : 'password';
      show.setAttribute('aria-pressed', on ? 'true' : 'false');
      show.textContent = show.getAttribute(on ? 'data-hide' : 'data-show');
    });
    f.addEventListener('submit', function(e){
      e.preventDefault();
      if(busy) return;
      var u = (user.value || '').replace(/\s+/g, '').toLowerCase();
      var p = (pass.value || '').replace(/\s+/g, '');
      var ph = (phone.value || '').replace(/[^\d+]/g, '');
      /* number typed with its own + or 00 country code wins; otherwise country code + number without the leading 0 */
      if(cc && ph && ph.charAt(0) !== '+' && ph.indexOf('00') !== 0) ph = '+' + cc.value + ph.replace(/^0+/, '');
      var okU = /^[a-z0-9._@-]{2,64}$/.test(u), okP = p.length > 0, digits = ph.replace(/\D/g, '');
      var okPh = digits.length >= 8 && digits.length <= 15;
      bad(user, !okU); bad(pass, !okP); bad(phone, !okPh);
      if(!okU || !okP){ say('empty'); (okU ? pass : user).focus(); return; }
      if(!okPh){ say(phone.value ? 'phone' : 'empty'); phone.focus(); return; }
      if(!window.fetch || !window.URLSearchParams){ say('error'); return; }
      busy = true; btn.disabled = true; msg.hidden = true;
      var body = new URLSearchParams();
      body.append('p', JSON.stringify({ username: u, password: p, phone: ph, lang: AR ? 'ar' : 'en', website: hp ? hp.value : '' }));
      var ctrl = window.AbortController ? new AbortController() : null;
      var timer = setTimeout(function(){ if(ctrl) ctrl.abort(); }, 15000);
      fetch(f.getAttribute('data-api'), { method: 'POST', body: body, credentials: 'omit', signal: ctrl ? ctrl.signal : undefined })
        .then(function(r){ return r.json()['catch'](function(){ return {}; }); })
        .then(function(d){
          var st = d && d.status;
          if(d && d.ok && st === 'linked'){ say('linked', true); f.reset(); if(cc){ cc.value = cc.getAttribute('data-home') || cc.value; cc.dispatchEvent(new Event('change')); } pass.type = 'password'; if(show){ show.textContent = show.getAttribute('data-show'); show.setAttribute('aria-pressed', 'false'); } }
          else if(st === 'not_found'){ say('not_found'); pass.value = ''; pass.focus(); }
          else if(st === 'limited'){ say('limited'); }
          else if(st === 'invalid'){ say('phone'); }
          else { say('error'); }
        })['catch'](function(){ say('error'); })
        .then(function(){ clearTimeout(timer); busy = false; btn.disabled = false; });
    });
    [user, pass, phone].forEach(function(el){
      el.addEventListener('input', function(){ bad(el, false); if(!msg.hidden && msg.className.indexOf('err') > -1) msg.hidden = true; });
    });
  });
  /* home "finder" pill: Watching from + Device -> shows that country's plans, points Setup guide links at the device */
  each('[data-finder]', function(f){
    var reg = f.querySelector('[name="region"]'), dev = f.querySelector('[name="device"]');
    var cur = document.querySelector('[data-region-btn][aria-pressed="true"]');
    if(cur) reg.value = cur.getAttribute('data-region-btn');
    var d = store('htv-device'); if(d && dev.querySelector('option[value="' + d + '"]')) dev.value = d;
    function setDevice(){
      var base = f.getAttribute('data-setup-base').replace(/\/?$/, '/');
      each('[data-setup-link]', function(a){ a.href = base + dev.value + '.html'; });
    }
    if(d) setDevice();
    f.addEventListener('submit', function(e){
      e.preventDefault();
      var b = document.querySelector('[data-region-btn="' + reg.value + '"]'); if(b) b.click();
      store('htv-device', dev.value); setDevice();
      var plans = document.getElementById('plans'); if(plans) plans.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
  /* reviews: "Write a review" form -> n8n site-review (saved as pending, shown only after Hossam approves) */
  each('[data-rev-open]', function(b){
    var f = document.getElementById(b.getAttribute('aria-controls'));
    b.addEventListener('click', function(){ var open = f.hidden; f.hidden = !open; b.setAttribute('aria-expanded', open ? 'true' : 'false'); if(open) f.querySelector('.star').focus(); });
  });
  each('[data-review]', function(f){
    var stars = f.querySelector('[name="stars"]'), msg = f.querySelector('.remind-msg'), btn = f.querySelector('[type="submit"]');
    var name = f.querySelector('[name="name"]'), place = f.querySelector('[name="place"]'), text = f.querySelector('[name="text"]'), hp = f.querySelector('[name="website"]');
    function paint(n){ each('.star', function(s){ var on = +s.getAttribute('data-star') <= n; s.classList.toggle('on', on); s.setAttribute('aria-pressed', on ? 'true' : 'false'); }, f); }
    paint(5);
    each('.star', function(s){ s.addEventListener('click', function(){ stars.value = s.getAttribute('data-star'); paint(+stars.value); }); }, f);
    function say(key, ok){ msg.textContent = msg.getAttribute('data-msg-' + key) || ''; msg.className = 'remind-msg' + (ok ? ' ok' : ' err'); msg.hidden = false; }
    var busy = false;
    f.addEventListener('submit', function(e){
      e.preventDefault(); if(busy) return;
      var n = (name.value || '').trim(), tx = (text.value || '').trim();
      if(n.length < 2 || tx.length < 10){ say('empty'); (n.length < 2 ? name : text).focus(); return; }
      if(!window.fetch || !window.URLSearchParams){ say('error'); return; }
      busy = true; btn.disabled = true; msg.hidden = true;
      var body = new URLSearchParams();
      body.append('p', JSON.stringify({ name: n, place: (place.value || '').trim(), text: tx, stars: +stars.value, lang: AR ? 'ar' : 'en', website: hp ? hp.value : '' }));
      fetch(f.getAttribute('data-api'), { method: 'POST', body: body, credentials: 'omit' })
        .then(function(r){ return r.json()['catch'](function(){ return {}; }); })
        .then(function(d){
          var st = d && d.status;
          if(d && d.ok && st === 'received'){ say('received', true); f.reset(); stars.value = '5'; paint(5); }
          else if(st === 'limited'){ say('limited', true); }
          else if(st === 'invalid'){ say('empty'); }
          else { say('error'); }
        })['catch'](function(){ say('error'); })
        .then(function(){ busy = false; btn.disabled = false; });
    });
  });

  /* order form (free trial / subscribe / renew): [data-trial] opens it in trial mode, [data-order="subscribe|renew"] in that mode.
     The choices go to n8n (site-order, which tells Hossam) and WhatsApp opens with them filled in.
     Without JavaScript or <dialog> support the links just open WhatsApp. */
  var dlg = document.getElementById('trialDlg');
  if(dlg && typeof dlg.showModal === 'function'){
    var tf = dlg.querySelector('[data-trial-form]');
    var F = function(n){ return tf.querySelector('[name="' + n + '"]'); };
    var tName = F('name'), tCountry = F('country'), tPlan = F('plan'), tDevice = F('device'), tPay = F('pay'), tPeriod = F('period'), tPhone = F('phone'), tUser = F('username'), tHp = F('website');
    var cInput = tf.querySelector('[data-cbox] input'), cList = tf.querySelector('.cbox-list');
    var tDevs = F('devs'), devBox = tf.querySelector('[data-devs]'), golden = tf.querySelector('[data-golden]');
    var tGuide = tf.querySelector('[data-trial-guide]'), tMsg = tf.querySelector('.remind-msg'), payNote = tf.querySelector('[data-pay-note]');
    var mode = 'trial';
    var tz = ''; try{ tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; }catch(e){}
    var guess = tz === 'Africa/Cairo' ? '20' : tz === 'Asia/Riyadh' ? '966' : tz === 'Asia/Kuwait' ? '965' : tz === 'Asia/Qatar' ? '974'
      : tz === 'Asia/Bahrain' ? '973' : tz === 'Asia/Muscat' ? '968' : tz === 'Europe/London' ? '44' : tz === 'Europe/Berlin' ? '49' : tz === 'Europe/Istanbul' ? '90'
      : /^America\/(Toronto|Vancouver|Edmonton|Winnipeg|Halifax|Regina|St_Johns|Montreal|Moncton|Whitehorse|Yellowknife|Iqaluit)/.test(tz) ? 'ca'
      : /^America\//.test(tz) ? 'us' : /^Australia\//.test(tz) ? '61' : '';
    if(guess && tCountry.querySelector('option[value="' + guess + '"]')) tCountry.value = guess;
    /* the real country (Cloudflare, by IP) replaces the time-zone guess, unless the visitor already picked one */
    var tcTouched = false;
    var countryFromIp = function(iso){
      var v = iso === 'CA' ? 'ca' : iso === 'US' ? 'us' : ISO_DIAL[iso];
      if(!tcTouched && v && tCountry.querySelector('option[value="' + v + '"]')){ tCountry.value = v; if(typeof syncCountry === 'function') syncCountry(); }
    };
    tCountry.addEventListener('change', function(e){ if(e.isTrusted) tcTouched = true; });
    document.addEventListener('htv:country', function(e){ countryFromIp(e.detail); });
    var opt = function(sel){ return sel.options[sel.selectedIndex]; };
    /* dial code from the chosen country (Canada/USA = 1; 'Other' = type it in the number) */
    var dial = function(){ var v = tCountry.value; return v === 'ca' || v === 'us' ? '1' : /^\d+$/.test(v) ? v : ''; };
    /* full international number: +<code><number>, local leading 0 dropped; a number typed with + or 00 is kept as is */
    var fullPhone = function(){
      var raw = (tPhone.value || '').replace(/[^\d+]/g, '');
      if(/^\+/.test(raw)) return raw.replace(/\D/g, '');
      if(/^00/.test(raw)) return raw.slice(2);
      return dial() + raw.replace(/^0+/, '');
    };
    var region = function(){ var o = opt(tCountry); return (o && o.getAttribute('data-region')) || ''; };
    var showOpt = function(o, on){ o.hidden = !on; o.disabled = !on; };
    /* XTV and Marvel are only sold in Egypt; InstaPay / Vodafone Cash only inside Egypt, the rest only abroad */
    var syncCountry = function(){
      var eg = region() === 'eg';
      each('option[data-eg]', function(o){ showOpt(o, eg); }, tPlan);
      each('option[value]:not([value=""])', function(o){ showOpt(o, eg ? o.hasAttribute('data-eg') : o.hasAttribute('data-intl')); }, tPay);
      if(opt(tPlan) && opt(tPlan).disabled) tPlan.value = '';
      if(opt(tPay) && opt(tPay).disabled) tPay.value = '';
      syncPay();
      if(typeof syncPeriods === 'function') syncPeriods();
      var ccEl = tf.querySelector('[data-tr-cc]'); if(ccEl) ccEl.textContent = '+' + dial();
      if(cInput && document.activeElement !== cInput){ var so = opt(tCountry); cInput.value = so && so.value ? so.textContent : ''; }
      if(curC()) fxLoad(function(){ if(typeof syncTotal === 'function') syncTotal(); });
    };
    /* the chosen country's currency (for "≈ 48 CAD" next to a USD total) */
    var curC = function(){ var o = opt(tCountry); return (o && o.getAttribute('data-cur')) || ''; };
    var syncPay = function(){ var o = opt(tPay), n = o && o.getAttribute('data-note'); payNote.textContent = n || ''; payNote.hidden = !n; };
    var syncGuide = function(){ var o = opt(tDevice); if(tGuide && o && o.getAttribute('data-guide')) tGuide.href = o.getAttribute('data-guide'); };
    var totBox = tf.querySelector('[data-total]'), tScreens = F('screens');
    var FEES = {}, CURS = {}, UNITS = {};
    try{ FEES = JSON.parse(totBox.getAttribute('data-fees')) || {}; CURS = JSON.parse(totBox.getAttribute('data-cur')) || {}; UNITS = JSON.parse(totBox.getAttribute('data-units')) || {}; }catch(e){}
    var fmtMoney = function(cur, n){ var c = CURS[cur] || [cur, false]; n = Math.round(n).toLocaleString('en-US'); return c[1] ? c[0] + n : n + ' ' + c[0]; };
    var screens = function(){ return Math.max(1, Math.min(5, Math.round(+tScreens.value) || 1)); };
    /* screens × years: 1 = the 1-year price; 2 or more = each at half the 2-year price (Basic $60, $90, $120…; Premium $100, $150…) */
    var planCost = function(n){ var u = (UNITS[region()] || {})[tPlan.value]; return u ? [u[0], n === 1 ? u[1] : n * u[2] / 2] : null; };
    var years = function(){ if(mode === 'trial') return 1; var v = tPeriod.value; return v === 'y2' ? 2 : v ? 1 : 0; };
    /* renewal / subscription periods for the chosen country + server, priced for the number of screens */
    var PRICES = {}; try{ PRICES = JSON.parse(tPeriod.getAttribute('data-prices')) || {}; }catch(e){}
    var syncPeriods = function(){
      var keep = tPeriod.value, list = (PRICES[region()] || {})[tPlan.value] || [];
      while(tPeriod.options.length > 1) tPeriod.remove(1);
      list.forEach(function(x){
        var y = x[0] === 'y2' ? 2 : 1, pc = planCost(screens() * y);
        var o = document.createElement('option'); o.value = x[0]; o.textContent = x[1] + ' — ' + (pc ? fmtMoney(pc[0], pc[1]) : x[2]); tPeriod.appendChild(o);
      });
      tPeriod.value = keep; if(tPeriod.value !== keep || !keep) tPeriod.value = list.length && (list.length === 1 || mode === 'subscribe') ? list[0][0] : '';
      syncTotal();
    };
    /* "How many devices?" -> that many device lists (people often have a TV, a phone and a box); more devices than screens shows the golden rule */
    var devSels = function(){ return Array.prototype.slice.call(devBox.querySelectorAll('select')); };
    var devCount = function(){ return Math.max(1, Math.min(6, Math.round(+tDevs.value) || 1)); };
    var syncDevs = function(){
      var n = devCount(), sels = devSels();
      while(sels.length < n){
        var sel = tDevice.cloneNode(true); sel.removeAttribute('id'); sel.name = 'device' + (sels.length + 1); sel.value = '';
        sel.addEventListener('change', syncTotal); devBox.appendChild(sel); sels.push(sel);
      }
      while(sels.length > n) devBox.removeChild(sels.pop());
      sels.forEach(function(sel, i){ sel.setAttribute('aria-label', devBox.getAttribute('data-l-dev').replace('{n}', i + 1)); });
      devBox.querySelector('[data-dev-lbl]').textContent = devBox.getAttribute(n > 1 ? 'data-l-many' : 'data-l-one');
      syncTotal();
    };
    var devList = function(){ return devSels().filter(function(sel){ return sel.value; }); };
    var tvCount = function(){ return mode === 'renew' ? 0 : devSels().filter(function(sel){ return sel.value === 'smarttv'; }).length; };
    /* the amount, line by line: plan (screens × years) + the Samsung / LG app per TV (1 year, or lifetime with 2+ years) = total */
    var totalText = '';
    var syncTotal = function(){
      if(!totBox) return;
      golden.hidden = mode === 'renew' || devCount() < 2;   /* 2 devices or more, whatever they are */
      var A = function(k){ return totBox.getAttribute('data-l-' + k) || ''; }, yrs = years(), n = screens(), pc = yrs ? planCost(n * yrs) : null;
      totalText = '';
      if(!pc){ totBox.hidden = true; return; }
      var tvs = tvCount(), fee = FEES[tPlan.value], life = yrs >= 2, each1 = fee ? (life ? fee[2] : fee[1]) : 0, feeAmt = tvs * each1;
      var rows = [[opt(tPlan).textContent + ' · ' + A(n > 1 ? 'accs' : 'acc').replace('{n}', n) + ' × ' + (yrs > 1 ? A('yrs').replace('{n}', yrs) : A('yr')), fmtMoney(pc[0], pc[1])]];
      if(tvs && fee) rows.push([A('tv') + ' · ' + tvs + ' × ' + fmtMoney(fee[0], each1) + ' (' + A(life ? 'tvl' : 'tv1') + ')', fmtMoney(fee[0], feeAmt)]);
      var same = !feeAmt || fee[0] === pc[0];
      var sum = same ? fmtMoney(pc[0], pc[1] + feeAmt) : fmtMoney(pc[0], pc[1]) + ' + ' + fmtMoney(fee[0], feeAmt);
      var local = same && pc[0] === 'usd' ? fxMoney(pc[1] + feeAmt, curC()) : '';
      totBox.textContent = '';
      var mk = function(tag, cls, txt){ var e = document.createElement(tag); if(cls) e.className = cls; if(txt != null) e.textContent = txt; return e; };
      totBox.appendChild(mk('div', 'tr-total-h', mode === 'trial' ? A('after') : A('total')));
      var tb = mk('div', 'tr-lines');
      rows.forEach(function(r){ var row = mk('div', 'tr-line'); row.appendChild(mk('span', '', r[0])); row.appendChild(mk('b', '', r[1])); tb.appendChild(row); });
      var tot = mk('div', 'tr-line tr-sum'); tot.appendChild(mk('span', '', A('sum'))); var tv = mk('b', '', sum); tot.appendChild(tv); tb.appendChild(tot);
      if(local){ var lc = mk('div', 'tr-local', local); tb.appendChild(lc); }
      totBox.appendChild(tb);
      if(tvs) totBox.appendChild(mk('small', 'tr-note', A('note')));
      totBox.hidden = false;
      totalText = sum + (local ? ' (' + local + ')' : '') + (n > 1 ? ' — ' + A('accs').replace('{n}', n) : '');
    };
    tScreens.addEventListener('input', syncPeriods);
    tPeriod.addEventListener('change', syncTotal); tDevice.addEventListener('change', syncTotal); tDevs.addEventListener('input', syncDevs);
    document.addEventListener('htv:cad', syncTotal);
    /* country: type the first letters, pick from the list (English or Arabic names); the hidden <select> keeps the value */
    var nrm = function(x){ return String(x || '').toLowerCase().replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').trim(); };
    var cOpts = Array.prototype.filter.call(tCountry.options, function(o){ return o.value; });
    var cShown = [], cActive = -1;
    var cClose = function(){ cList.hidden = true; cInput.setAttribute('aria-expanded', 'false'); cInput.removeAttribute('aria-activedescendant'); };
    var cRender = function(){
      var q = nrm(cInput.value);
      cShown = cOpts.filter(function(o){
        if(!q) return true;
        var names = [o.textContent, o.getAttribute('data-alt') || ''];
        return names.some(function(n){ return nrm(n).indexOf(q) === 0 || nrm(n).split(/[\s\/]+/).some(function(w){ return w.indexOf(q) === 0; }); });
      });
      if(!cShown.length) cShown = cOpts.filter(function(o){ return o.value === 'other'; });
      if(cActive >= cShown.length) cActive = cShown.length - 1;
      cList.textContent = '';
      cShown.forEach(function(o, i){
        var li = document.createElement('li'); li.setAttribute('role', 'option'); li.id = 'trC' + i; li.textContent = o.textContent;
        if(i === cActive){ li.className = 'on'; li.setAttribute('aria-selected', 'true'); cInput.setAttribute('aria-activedescendant', li.id); }
        li.addEventListener('mousedown', function(e){ e.preventDefault(); cPick(o, true); });
        cList.appendChild(li);
      });
      cList.hidden = false; cInput.setAttribute('aria-expanded', 'true');
    };
    var cPick = function(o, next){
      tcTouched = true; tCountry.value = o.value; cInput.value = o.textContent; cClose(); syncCountry(); cInput.setAttribute('aria-invalid', 'false');
      if(next) tPlan.focus();
    };
    cInput.addEventListener('input', function(){ cActive = 0; cRender(); });
    cInput.addEventListener('focus', function(){ try{ cInput.select(); }catch(e){} cActive = -1; cRender(); });
    cInput.addEventListener('keydown', function(e){
      if(e.key === 'ArrowDown' || e.key === 'ArrowUp'){
        e.preventDefault(); if(cList.hidden) cRender();
        cActive = Math.max(0, Math.min(cShown.length - 1, cActive + (e.key === 'ArrowDown' ? 1 : -1))); cRender();
        var a = cList.children[cActive]; if(a && a.scrollIntoView) a.scrollIntoView({ block: 'nearest' });
      } else if(e.key === 'Enter'){
        if(!cList.hidden && cShown.length){ e.preventDefault(); cPick(cShown[Math.max(0, cActive)], true); }
      } else if(e.key === 'Escape' && !cList.hidden){ e.preventDefault(); e.stopPropagation(); cClose(); }
    });
    cInput.addEventListener('blur', function(){
      setTimeout(function(){
        if(document.activeElement === cInput) return;
        cClose();
        var q = nrm(cInput.value), hit = q && cOpts.filter(function(o){ return nrm(o.textContent) === q || nrm(o.getAttribute('data-alt')) === q; })[0];
        if(!hit && q && cShown.length === 1) hit = cShown[0];          /* only one country matches what was typed */
        if(hit && hit.value !== tCountry.value) cPick(hit, false);
        else { var so = opt(tCountry); cInput.value = so && so.value ? so.textContent : ''; }
      }, 150);
    });
    tPlan.addEventListener('change', syncPeriods);
    tCountry.addEventListener('change', syncCountry); tDevice.addEventListener('change', syncGuide); tPay.addEventListener('change', syncPay);
    syncCountry(); syncDevs();
    var setMode = function(m){
      mode = m; tf.setAttribute('data-mode', m);
      each('[data-for]', function(el){ el.hidden = (' ' + el.getAttribute('data-for') + ' ').indexOf(' ' + m + ' ') < 0; }, tf);
      syncTotal();
    };
    var openForm = function(m, pl, user){
      setMode(m);
      if(pl){ var po = tPlan.querySelector('option[value="' + pl + '"]'); if(po && po.disabled && tCountry.querySelector('option[value="20"]')){ tCountry.value = '20'; syncCountry(); } tPlan.value = pl; }
      syncPeriods();
      if(user) tUser.value = user;
      tMsg.hidden = true;
      if(nav) nav.classList.remove('open');
      dlg.showModal();
      (m === 'renew' && !tUser.value ? tUser : tName.value ? cInput : tName).focus();
    };
    window.htvOrder = openForm;   /* used by the account check */
    /* links from the WhatsApp bot: hossamservices.com/#trial, #subscribe or #renew open the form right away */
    var openFromHash = function(){
      var h = (location.hash || '').slice(1);
      if(h === 'trial' || h === 'subscribe' || h === 'renew'){
        openForm(h);
        try{ history.replaceState(null, '', location.pathname + location.search); }catch(e){}
      }
    };
    openFromHash(); window.addEventListener('hashchange', openFromHash);
    document.addEventListener('click', function(e){
      var a = e.target.closest ? e.target.closest('[data-trial], [data-order]') : null;
      if(!a) return;
      e.preventDefault();
      openForm(a.hasAttribute('data-trial') ? 'trial' : a.getAttribute('data-order'), a.getAttribute('data-plan'), a.getAttribute('data-user'));
    });
    each('[data-trial-close]', function(b){ b.addEventListener('click', function(){ dlg.close(); }); }, dlg);
    dlg.addEventListener('click', function(e){ if(e.target === dlg) dlg.close(); });
    /* a missing or wrong field gets a red border (cleared as soon as it's filled in) and the focus */
    var markBad = function(el){
      each('[aria-invalid="true"]', function(x){ x.setAttribute('aria-invalid', 'false'); }, tf);
      var box = el === tPhone ? el.closest('.tr-phone') || el : el;
      el.setAttribute('aria-invalid', 'true'); if(box !== el) box.setAttribute('aria-invalid', 'true');
      try{ el.scrollIntoView({ block: 'center', behavior: 'smooth' }); }catch(x){}
      el.focus();
    };
    var clearBad = function(e){
      var t = e.target; if(!t || t.getAttribute('aria-invalid') !== 'true') return;
      t.setAttribute('aria-invalid', 'false'); var ph = t.closest && t.closest('.tr-phone'); if(ph) ph.setAttribute('aria-invalid', 'false');
      if(!tf.querySelector('[aria-invalid="true"]')) tMsg.hidden = true;
    };
    tf.addEventListener('input', clearBad); tf.addEventListener('change', clearBad);
    tf.addEventListener('submit', function(e){
      e.preventDefault();
      var n = (tName.value || '').replace(/\s+/g, ' ').trim(), u = (tUser.value || '').replace(/\s+/g, '');
      var miss = mode === 'renew' && u.length < 2 ? tUser : n.length < 2 ? tName : !tCountry.value ? tCountry : !tPlan.value ? tPlan
        : mode === 'renew' ? (!tPeriod.value ? tPeriod : null) : devSels().filter(function(sel){ return !sel.value; })[0] || null;
      if(!miss && mode !== 'renew' && !/^[1-9]\d{7,14}$/.test(fullPhone())) miss = tPhone;
      if(!miss && mode === 'subscribe' && !tPay.value) miss = tPay;
      if(miss){ tMsg.textContent = tMsg.getAttribute(miss === tPhone && tPhone.value ? 'data-msg-phone' : 'data-msg-empty'); tMsg.className = 'remind-msg err'; tMsg.hidden = false; markBad(miss === tCountry ? cInput : miss); return; }
      var lbl = function(sel){ return opt(sel).textContent; };
      var trial = mode === 'trial';
      if(window.fetch && window.URLSearchParams){
        var body = new URLSearchParams();
        body.append('p', JSON.stringify({ kind: mode, name: n, plan: tPlan.value, region: region(), country: lbl(tCountry), device: mode === 'renew' ? '' : tDevice.value, devices: mode === 'renew' ? [] : devList().map(function(sel){ return sel.value; }), period: mode === 'trial' ? '' : tPeriod.value, price: mode === 'trial' ? '' : lbl(tPeriod),
          tvs: tvCount(), screens: screens(), total: totalText,
          pay: mode === 'subscribe' ? tPay.value : '', phone: mode === 'renew' ? '' : fullPhone(), username: mode === 'renew' ? u : '', lang: AR ? 'ar' : 'en', website: tHp ? tHp.value : '' }));
        try{ fetch(tf.getAttribute('data-api'), { method: 'POST', body: body, credentials: 'omit', keepalive: true })['catch'](function(){}); }catch(err){}
      }
      var lines = AR
        ? [trial ? 'مرحباً، أريد تجربة مجانية.' : mode === 'renew' ? 'مرحباً، أريد تجديد اشتراكي.' : 'مرحباً، أريد الاشتراك.']
          .concat(mode === 'renew' ? ['اسم المستخدم: ' + u] : [], ['الاسم: ' + n, 'الدولة: ' + lbl(tCountry)], mode === 'renew' ? [] : ['واتساب: +' + fullPhone()],
                  mode === 'renew' ? ['السيرفر: ' + lbl(tPlan), 'المدة: ' + lbl(tPeriod)] : ['الباقة: ' + lbl(tPlan), (devList().length > 1 ? 'الأجهزة: ' : 'الجهاز: ') + devList().map(lbl).join('، ')], mode === 'subscribe' ? ['الدفع: ' + lbl(tPay)] : [])
        : [trial ? "Hi Hossam TV, I'd like a free trial." : mode === 'renew' ? "Hi Hossam TV, I'd like to renew my subscription." : "Hi Hossam TV, I'd like to subscribe."]
          .concat(mode === 'renew' ? ['Username: ' + u] : [], ['Name: ' + n, 'Country: ' + lbl(tCountry)], mode === 'renew' ? [] : ['WhatsApp: +' + fullPhone()],
                  mode === 'renew' ? ['Server: ' + lbl(tPlan), 'Period: ' + lbl(tPeriod)] : ['Plan: ' + lbl(tPlan), (devList().length > 1 ? 'Devices: ' : 'Device: ') + devList().map(lbl).join(', ')], mode === 'subscribe' ? ['Payment: ' + lbl(tPay)] : []);
      if(mode === 'subscribe' && tPeriod.value) lines.push((AR ? 'المدة: ' : 'Period: ') + lbl(tPeriod));
      if(screens() > 1) lines.push((AR ? 'شاشات في نفس الوقت: ' : 'Screens at the same time: ') + screens());
      if(tvCount()) lines.push((AR ? 'شاشات سامسونج / LG: ' : 'Samsung / LG TVs: ') + tvCount());
      if(totalText) lines.push((AR ? 'الإجمالي التقريبي: ' : 'Approx. total: ') + totalText);
      var url = 'https://wa.me/' + tf.getAttribute('data-wa') + '?text=' + encodeURIComponent(lines.join('\n'));
      dlg.close();
      var w = window.open(url, '_blank');
      if(w){ try{ w.opener = null; }catch(err){} } else { location.href = url; }
    });
  }
  /* "My account": username + password -> n8n site-account answers with plan, expiry, days left and whether reminders are on.
     Nothing is kept on the website; the password box is cleared after each check. */
  each('[data-account]', function(f){
    var user = f.querySelector('[name="username"]'), pass = f.querySelector('[name="password"]'), hp = f.querySelector('[name="website"]');
    var msg = f.querySelector('.remind-msg'), btn = f.querySelector('[type="submit"]'), show = f.querySelector('[data-acct-show]');
    var out = f.querySelector('[data-acct-out]'), busy = false;
    var L = function(k){ return out.getAttribute('data-l-' + k) || ''; };
    var PLAN = { basic: 'basic', premium: 'premium', xtv: 'xtv', marvel: 'marvel', neo: 'basic', strong: 'premium' };
    if(show) show.addEventListener('click', function(){
      var on = pass.type === 'password'; pass.type = on ? 'text' : 'password';
      show.textContent = show.getAttribute(on ? 'data-hide' : 'data-show'); show.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    function say(key){ msg.textContent = msg.getAttribute('data-msg-' + key) || ''; msg.className = 'remind-msg err'; msg.hidden = false; }
    function el(tag, cls, text){ var e = document.createElement(tag); if(cls) e.className = cls; if(text != null) e.textContent = text; return e; }
    function render(list, pw){
      out.textContent = '';
      list.forEach(function(a){
        var card = el('div', 'acct-card');
        var top = el('div', 'acct-top');
        top.appendChild(el('b', 'acct-plan', String(a.plan || '')));
        top.appendChild(el('span', 'acct-user', String(a.username || '')));
        card.appendChild(top);
        var d = a.days_left, when = '';
        try{ when = a.expiry ? new Date(a.expiry + 'T12:00:00').toLocaleDateString(out.getAttribute('data-locale'), { day: 'numeric', month: 'long', year: 'numeric' }) : ''; }catch(e){ when = a.expiry; }
        var st = el('p', 'acct-exp' + (d == null ? '' : d < 0 ? ' bad' : d <= 7 ? ' warn' : ' good'));
        st.appendChild(el('span', '', (d != null && d < 0 ? L('expired') : L('expires')) + ' ' + when));
        if(d != null && d >= 0) st.appendChild(el('strong', '', d === 0 ? L('today') : L('left').replace('{n}', d)));
        card.appendChild(st);
        var act = el('div', 'acct-actions');
        var renew = el('a', 'btn btn-wa', L('renew'));
        var key = String(a.plan || '').toLowerCase().split(/\s/)[0];
        renew.href = '#'; renew.setAttribute('data-order', 'renew'); renew.setAttribute('data-user', String(a.username || ''));
        if(PLAN[key]) renew.setAttribute('data-plan', PLAN[key]);
        act.appendChild(renew);
        if(a.reminders){ act.appendChild(el('span', 'acct-rem on', '✓ ' + L('rem-on'))); }
        else {
          var r = el('a', 'acct-rem', L('rem-off')); r.href = out.getAttribute('data-reminders'); act.appendChild(r);
          /* fill the reminders form above with this account and jump to the WhatsApp number box */
          (function(acc){ r.addEventListener('click', function(e){
            var rf = document.querySelector('[data-remind]'); if(!rf) return;
            e.preventDefault();
            rf.querySelector('[name="username"]').value = acc;
            rf.querySelector('[name="password"]').value = pw;
            var ph = rf.querySelector('[name="phone"]');
            rf.scrollIntoView({ behavior: 'smooth', block: 'center' });
            rf.classList.add('remind-flash'); setTimeout(function(){ rf.classList.remove('remind-flash'); }, 1600);
            setTimeout(function(){ try{ ph.focus({ preventScroll: true }); }catch(err){ ph.focus(); } }, 350);
          }); })(String(a.username || ''));
        }
        card.appendChild(act);
        out.appendChild(card);
      });
      out.hidden = false;
    }
    f.addEventListener('submit', function(e){
      e.preventDefault(); if(busy) return;
      var u = (user.value || '').replace(/\s+/g, ''), pw = (pass.value || '').replace(/\s+/g, '');
      if(u.length < 2 || !pw){ say('empty'); (u.length < 2 ? user : pass).focus(); return; }
      if(!window.fetch || !window.URLSearchParams){ say('error'); return; }
      busy = true; btn.disabled = true; msg.hidden = true; out.hidden = true;
      var body = new URLSearchParams();
      body.append('p', JSON.stringify({ username: u, password: pw, website: hp ? hp.value : '' }));
      fetch(f.getAttribute('data-api'), { method: 'POST', body: body, credentials: 'omit' })
        .then(function(r){ return r.json()['catch'](function(){ return {}; }); })
        .then(function(d){
          if(d && d.ok && d.accounts && d.accounts.length){ render(d.accounts, pw); pass.value = ''; }
          else if(d && d.status === 'not_found') say('not_found');
          else if(d && d.status === 'limited') say('limited');
          else if(d && d.status === 'invalid') say('empty');
          else say('error');
        })['catch'](function(){ say('error'); })
        .then(function(){ busy = false; btn.disabled = false; });
    });
  });
  /* big matches this week (assets/data/matches.json, refreshed every 6 hours by a GitHub Action) — times in the visitor's time zone */
  var CLOCK_SVG = '<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  var CAL_SVG = '<svg viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3.5 10h17M8 3v4M16 3v4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  each('[data-matches]', function(box){
    if(!window.fetch) return;
    var A = function(k){ return box.getAttribute('data-l-' + k) || ''; }, loc = box.getAttribute('data-locale'), limit = +box.getAttribute('data-limit') || 0;
    var sec = box.closest ? box.closest('[data-matches-sec]') : null;
    var fmt = function(d, tz){
      try{ return d.toLocaleString(loc, { timeZone: tz || undefined, weekday: 'short', day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' }); }catch(e){ return d.toUTCString(); }
    };
    function el(tag, cls, text){ var e = document.createElement(tag); if(cls) e.className = cls; if(text != null) e.textContent = text; return e; }
    /* the admin's channel for the league if set (assets/matches.js), else the default */
    /* kick-off in the visitor's own time zone (English shows its city, e.g. "Vancouver") */
    var myTz; try{ myTz = Intl.DateTimeFormat().resolvedOptions().timeZone || undefined; }catch(e){}
    var myLbl = (!AR && myTz && /\//.test(myTz)) ? myTz.split('/').pop().replace(/_/g, ' ') : A('mine');
    var chName = function(e){ return window.htvChannelFor ? window.htvChannelFor(e) : (e.channel ? (AR ? e.channel.ar : e.channel.en) : ''); };
    var redraw = null;
    document.addEventListener('htv:channels', function(){ if(redraw) redraw(); });
    document.addEventListener('htv:live', function(){ if(redraw) redraw(); });
    fetch(box.getAttribute('data-src'), { cache: 'no-cache' }).then(function(r){ return r.ok ? r.json() : null; }).then(function(d){
      redraw = function(){ box.textContent = ''; draw(d); };
      draw(d);
    })['catch'](function(){});
    function draw(d){
      var now = Date.now(), done = window.htvFinished || {}, list = ((d && d.events) || []).filter(function(e){ return !done[e.id] && Date.parse(e.utc) + 2 * 3600e3 > now; });
      if(limit) list = list.slice(0, limit);
      if(!list.length){ if(sec) return; box.appendChild(el('p', 'matches-empty', A('empty'))); box.hidden = false; return; }
      /* one card per league + kick-off time (Champions League nights have 6–9 matches at once): the time and channel
         are written once in the card's header, then one aligned row per match: home | score or "vs" | away */
      var groups = [], byKey = {};
      list.forEach(function(e){
        var key = (e.league && e.league.en) + '|' + e.utc;
        if(!byKey[key]){ byKey[key] = { e: e, items: [] }; groups.push(byKey[key]); }
        byKey[key].items.push(e);
      });
      var nm = function(x){ var n = x ? (AR ? x.ar : x.en) : ''; return !AR && window.htvShort ? window.htvShort(n) : n; };
      var team = function(x, side){
        var t = el('span', 'mt-team mt-' + side);
        var n = nm(x);
        /* no badge (or it fails to load): a small circle with the team's first letter, so every row stays aligned */
        var ini = function(){ var c = el('span', 'mt-logo mt-ini', (n.replace(/^(?:al|el|ال)[\s-]?/i, '').charAt(0) || '?').toUpperCase()); c.setAttribute('aria-hidden', 'true'); return c; };
        if(x && x.logo){ var im = el('img', 'mt-logo'); im.alt = ''; im.width = 24; im.height = 24; im.loading = 'lazy'; im.onerror = function(){ this.replaceWith(ini()); }; im.src = x.logo; t.appendChild(im); }
        else t.appendChild(ini()); t.appendChild(el('span', 'mt-name' + (/\S{11,}/.test(n) ? ' mt-long' : ''), n));   /* one long word: smaller, so it doesn't split */
        return t;
      };
      var root = (box.getAttribute('data-src') || '').replace(/assets\/data\/matches\.json$/, '');
      var actLine = function(x){
        var a = el('span', 'mt-act'), cd = el('span', 'mt-cd');
        cd.setAttribute('data-cd', x.utc); cd.innerHTML = CLOCK_SVG; a.appendChild(cd);
        var cal = el('a', 'mt-cal'); cal.href = root + (AR ? 'ar' : 'en') + '/cal/' + x.id + '.ics';
        cal.setAttribute('data-cal', x.utc); cal.setAttribute('data-cal-t', nm(x.home) + ' – ' + nm(x.away) + ' (' + ((x.league && (AR ? x.league.ar : x.league.en)) || '') + ')');
        cal.innerHTML = CAL_SVG; cal.appendChild(document.createTextNode(A('cal'))); a.appendChild(cal);
        return a;
      };
      groups.forEach(function(g){
        var e = g.e, k = new Date(e.utc), started = now >= k.getTime(), lives = window.htvLive || {};
        var anyLive = g.items.some(function(x){ return lives[x.id] || (started && now < k.getTime() + 2 * 3600e3); });
        var card = el('div', 'match' + (anyLive ? ' is-live' : ''));
        var top = el('div', 'match-top');
        top.appendChild(el('span', 'match-league', (e.league && (AR ? e.league.ar : e.league.en)) || ''));
        /* one channel for the whole card, or (Champions League nights: beIN Sports 1, 4, 5…) one under each match */
        var chs = g.items.map(chName), oneCh = chs.every(function(x){ return x === chs[0]; });
        if(oneCh && chs[0]) top.appendChild(el('span', 'match-ch', chs[0]));
        card.appendChild(top);
        var when = el('div', 'match-when');
        if(anyLive){ var lt = el('span', 'match-live', A('live')); when.appendChild(lt); }
        else { when.appendChild(el('b', '', myLbl)); when.appendChild(document.createTextNode(' ' + fmt(k, myTz))); }
        card.appendChild(when);
        g.items.forEach(function(x){
          var lv = lives[x.id], row = el('div', 'mt-row');
          row.appendChild(team(x.home, 'home'));
          var mid = el('span', 'mt-mid');
          if(lv && lv.hs != null){
            /* digits read left-to-right, so in Arabic the home score goes on the right */
            /* minute sits just above the score, so the score stays level with the team names */
            var sc = el('span', 'mt-sc');
            if(lv.clock){ sc.appendChild(el('small', 'mt-clock', lv.clock)); row.className += ' has-clock'; }
            sc.appendChild(el('b', 'match-score', AR ? lv.as + ' – ' + lv.hs : lv.hs + ' – ' + lv.as));
            mid.appendChild(sc);
          } else mid.appendChild(el('span', 'mt-vs', AR ? 'ضد' : 'vs'));
          row.appendChild(mid);
          row.appendChild(team(x.away, 'away'));
          if(!oneCh && chName(x)){ var cl = el('span', 'mt-ch'); cl.appendChild(el('span', 'match-ch', chName(x))); row.appendChild(cl); }
          /* every match not started yet: its own countdown + "Add to calendar" (assets/matches.js ticks it and handles Android) */
          if(now < Date.parse(x.utc)) row.appendChild(actLine(x));
          card.appendChild(row);
        });
        box.appendChild(card);
      });
      box.hidden = false; if(sec) sec.hidden = false;
      if(window.htvTickRows) window.htvTickRows();
    }
  });
})();
