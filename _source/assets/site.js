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
  /* renewal reminders: open WhatsApp with a prefilled "link my account" message.
     Sent from the customer's own WhatsApp, so the bot knows the number is theirs.
     Username + password, because some usernames repeat.
     The bot reads the last line: "#remind <username> <password>". */
  each('[data-remind]', function(f){
    var user = f.querySelector('[name="username"]'), pass = f.querySelector('[name="password"]');
    var err = f.querySelector('.remind-err'), show = f.querySelector('.remind-show');
    if(show) show.addEventListener('click', function(){
      var on = pass.type === 'password';
      pass.type = on ? 'text' : 'password';
      show.setAttribute('aria-pressed', on ? 'true' : 'false');
      show.textContent = show.getAttribute(on ? 'data-hide' : 'data-show');
    });
    f.addEventListener('submit', function(e){
      e.preventDefault();
      var u = (user.value || '').replace(/\s+/g, '').toLowerCase();
      var p = (pass.value || '').replace(/\s+/g, '');
      var okU = /^[a-z0-9._@-]{2,64}$/.test(u), okP = p.length >= 1 && p.length <= 64;
      user.setAttribute('aria-invalid', okU ? 'false' : 'true');
      pass.setAttribute('aria-invalid', okP ? 'false' : 'true');
      if(err) err.hidden = okU && okP;
      if(!okU){ user.focus(); return; }
      if(!okP){ pass.focus(); return; }
      var msg = AR
        ? 'مرحباً Hossam TV، أرجو إرسال تنبيهات التجديد على رقم الواتساب هذا.\nاسم المستخدم: ' + u + '\nكلمة المرور: ' + p + '\n#remind ' + u + ' ' + p
        : 'Hi Hossam TV, please send renewal reminders to this WhatsApp number.\nUsername: ' + u + '\nPassword: ' + p + '\n#remind ' + u + ' ' + p;
      window.open('https://wa.me/' + f.getAttribute('data-wa') + '?text=' + encodeURIComponent(msg), '_blank', 'noopener');
    });
    [user, pass].forEach(function(el){
      el.addEventListener('input', function(){ if(err && !err.hidden){ err.hidden = true; user.setAttribute('aria-invalid', 'false'); pass.setAttribute('aria-invalid', 'false'); } });
    });
  });
})();
