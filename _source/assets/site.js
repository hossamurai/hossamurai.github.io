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
    if(tz === 'Africa/Cairo') return 'eg';
    if(tz === 'Asia/Dubai') return 'uae';
    if(/^Asia\/(Riyadh|Kuwait|Qatar|Bahrain|Muscat|Aden)$/.test(tz)) return 'gulf';
    return 'intl';
  }
  function setRegion(id, save){
    each('[data-region-btn]', function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-region-btn') === id ? 'true' : 'false'); });
    each('[data-region-panel]', function(p){ p.hidden = p.getAttribute('data-region-panel') !== id; });
    if(save) store(REGION_KEY, id);
  }
  if(document.querySelector('[data-region-panel]')){
    var r = store(REGION_KEY);
    if(!document.querySelector('[data-region-panel="' + r + '"]')) r = detectRegion();
    setRegion(r, false);
    each('[data-region-btn]', function(b){
      b.addEventListener('click', function(){ setRegion(b.getAttribute('data-region-btn'), true); });
    });
  }

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
        var hit = !term || norm(it.textContent).indexOf(term) > -1;
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
          if(d && d.ok && st === 'linked'){ say('linked', true); f.reset(); if(cc) cc.value = cc.getAttribute('data-home') || cc.value; pass.type = 'password'; if(show){ show.textContent = show.getAttribute('data-show'); show.setAttribute('aria-pressed', 'false'); } }
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
})();
