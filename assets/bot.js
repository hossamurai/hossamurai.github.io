/* Hossam TV — website ↔ WhatsApp-bot features (ES5 so it also runs on older TV browsers)
   1. Chat bubble: the AI bot, clearly labelled as a bot    (n8n webhook: site-chat)
   2. Prices come from the bot's knowledge                 (n8n webhook: site-data)
   3. Outage banner while a known issue is active          (site-data)
   4. Order / free-trial form before WhatsApp opens        (n8n webhook: site-order)
   Everything fails quietly: if n8n is unreachable the page works exactly as before. */
(function(){
  'use strict';
  var API = 'https://n8n.hossamservices.com/webhook/';
  var MAIN = '201117250227';
  var doc = document.documentElement;
  function ar(){ return doc.lang === 'ar'; }
  function T(en, a){ return ar() ? a : en; }
  function each(sel, fn, root){ Array.prototype.forEach.call((root || document).querySelectorAll(sel), fn); }
  function esc(v){ return String(v == null ? '' : v).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function store(k, v){ try{ if(v === undefined) return localStorage.getItem(k); if(v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); }catch(e){ return null; } }
  function closest(el, sel){ while(el && el.nodeType === 1){ if((el.matches || el.msMatchesSelector).call(el, sel)) return el; el = el.parentNode; } return null; }
  function post(path, data, keepalive){
    var body = new URLSearchParams(); body.append('p', JSON.stringify(data));
    return fetch(API + path, { method: 'POST', body: body, keepalive: !!keepalive, credentials: 'omit' });
  }
  var HELP_PAGE = !!document.getElementById('alerts');   /* help.html has its own live data */
  if(!window.fetch || !window.URLSearchParams) return;

  /* ---------------------------------------------------------------- styles */
  var css = ''
  + '.htv-alert{background:#fff4e5;border-bottom:1px solid #f3d19c;color:#5c3b00;font-size:.92rem}'
  + '.htv-alert .wrap{display:flex;gap:10px;align-items:flex-start;padding-top:10px;padding-bottom:10px}'
  + '.htv-alert .ic{color:#b76e00;margin-top:.25em}.htv-alert a{font-weight:700;white-space:nowrap}'
  + '.htv-fab{position:fixed;inset-inline-end:18px;bottom:18px;z-index:80;display:flex;align-items:center;gap:8px;height:54px;padding:0 20px 0 16px;border:0;border-radius:999px;background:var(--ink,#17140f);color:#fff;font:inherit;font-weight:700;font-size:.95rem;cursor:pointer;box-shadow:0 10px 28px rgba(23,20,15,.28)}'
  + '.htv-fab svg{width:22px;height:22px}.htv-fab:hover{background:#2c271f}.htv-fab[hidden]{display:none}'
  + '@media (max-width:720px){.htv-fab{width:52px;height:52px;padding:0;justify-content:center;bottom:14px;inset-inline-end:14px}.htv-fab>span:not(.htv-badge){display:none}.htv-fab .htv-badge{position:absolute;top:-5px;inset-inline-end:-6px;border:1.5px solid var(--ink,#17140f)}}'
  + '.htv-chat{position:fixed;inset-inline-end:18px;bottom:18px;z-index:81;width:380px;max-width:calc(100vw - 24px);height:min(600px,calc(100vh - 36px));display:flex;flex-direction:column;background:var(--surface,#fff);color:var(--ink,#17140f);border:1px solid var(--line,#e8e1d5);border-radius:20px;box-shadow:0 24px 60px rgba(23,20,15,.25);overflow:hidden}'
  + '.htv-chat[hidden]{display:none}'
  + '.htv-chat-h{display:flex;align-items:center;gap:10px;padding:12px 12px 12px 16px;border-bottom:1px solid var(--line,#e8e1d5);background:var(--surface-2,#f4efe7)}'
  + '.htv-chat-h img{width:34px;height:34px;border-radius:10px}.htv-chat-h b{display:block;font-size:.95rem;line-height:1.2}.htv-chat-h small{color:var(--muted,#6f685d);font-size:.78rem}'
  + '.htv-x{margin-inline-start:auto;width:36px;height:36px;border:0;border-radius:50%;background:transparent;color:inherit;font-size:22px;line-height:1;cursor:pointer}.htv-x:hover{background:rgba(0,0,0,.06)}'
  + '.htv-msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:8px;overscroll-behavior:contain}'
  + '.htv-m{max-width:86%;padding:9px 13px;border-radius:16px;font-size:.93rem;line-height:1.5;white-space:normal;overflow-wrap:anywhere}'
  + '.htv-m.bot{align-self:flex-start;background:var(--surface-2,#f4efe7);border-end-start-radius:4px}'
  + '.htv-m.me{align-self:flex-end;background:var(--ink,#17140f);color:#fff;border-end-end-radius:4px}'
  + '.htv-m a{color:inherit;font-weight:700}'
  + '.htv-logo{display:flex;align-items:center;gap:8px;margin-top:8px;padding:6px 10px 6px 6px;background:#fff;border:1px solid var(--line,#e8e1d5);border-radius:12px;font-size:.82rem;font-weight:700}.htv-logo img{width:40px;height:40px;border-radius:8px}'
  + '.htv-wa{display:inline-flex;align-items:center;gap:7px;margin-top:8px;padding:9px 14px;border-radius:999px;background:var(--wa,#1faa59);color:#fff!important;font-weight:700;font-size:.88rem;text-decoration:none}'
  + '.htv-typing{align-self:flex-start;display:flex;gap:4px;padding:12px 14px;background:var(--surface-2,#f4efe7);border-radius:16px}'
  + '.htv-typing i{width:7px;height:7px;border-radius:50%;background:var(--muted,#6f685d);opacity:.4;animation:htvDot 1s infinite}.htv-typing i:nth-child(2){animation-delay:.15s}.htv-typing i:nth-child(3){animation-delay:.3s}'
  + '@keyframes htvDot{50%{opacity:1;transform:translateY(-2px)}}'
  + '.htv-chips{display:flex;flex-wrap:wrap;gap:6px;padding:0 14px 10px}'
  + '.htv-chip{border:1.5px solid var(--line-2,#d8cfbf);background:transparent;color:inherit;border-radius:999px;padding:6px 12px;font:inherit;font-size:.83rem;font-weight:700;cursor:pointer}.htv-chip:hover{border-color:var(--ink,#17140f)}'
  + '.htv-in{display:flex;gap:8px;padding:10px;border-top:1px solid var(--line,#e8e1d5)}'
  + '.htv-in textarea{flex:1;resize:none;height:44px;max-height:120px;padding:11px 14px;border:1.5px solid var(--line-2,#d8cfbf);border-radius:14px;font:inherit;font-size:16px;line-height:1.35;background:#fff;color:var(--ink,#17140f)}'
  + '.htv-in textarea:focus{outline:none;border-color:var(--ink,#17140f)}'
  + '.htv-send{width:44px;height:44px;flex-shrink:0;border:0;border-radius:50%;background:var(--ink,#17140f);color:#fff;cursor:pointer;display:grid;place-items:center}.htv-send:disabled{opacity:.4;cursor:default}.htv-send svg{width:20px;height:20px}'
  + 'html[dir="rtl"] .htv-send svg{transform:scaleX(-1)}'
  + '.htv-note{padding:0 14px 8px;font-size:.72rem;color:var(--muted,#6f685d);text-align:center}.htv-note a{color:inherit;font-weight:700}'
  + '.htv-badge{display:inline-block;vertical-align:2px;margin-inline-start:6px;padding:1px 7px;border-radius:999px;background:var(--ink,#17140f);color:#fff;font-size:.62rem;font-weight:700;letter-spacing:.06em}'
  + '.htv-fab .htv-badge{background:#fff;color:var(--ink,#17140f);margin-inline-start:0}'
  + '.htv-ov{position:fixed;inset:0;z-index:95;background:rgba(23,20,15,.45);display:flex;align-items:center;justify-content:center;padding:16px}'
  + '.htv-ov[hidden]{display:none}'
  + '.htv-form{width:440px;max-width:100%;max-height:calc(100vh - 32px);overflow-y:auto;background:var(--surface,#fff);color:var(--ink,#17140f);border-radius:22px;padding:22px;box-shadow:0 24px 60px rgba(23,20,15,.3)}'
  + '.htv-form h3{font-size:1.3rem;margin:0 0 4px;padding-inline-end:36px}.htv-form p.sub{margin:0 0 14px;color:var(--muted,#6f685d);font-size:.9rem}'
  + '.htv-form .lbl{display:block;font-weight:700;font-size:.85rem;margin:14px 0 7px}'
  + '.htv-form .opts{display:flex;flex-wrap:wrap;gap:7px}'
  + '.htv-form .opt{border:1.5px solid var(--line-2,#d8cfbf);background:transparent;color:inherit;border-radius:12px;padding:8px 12px;font:inherit;font-size:.87rem;font-weight:700;cursor:pointer}'
  + '.htv-form .opt[aria-pressed="true"]{background:var(--ink,#17140f);border-color:var(--ink,#17140f);color:#fff}'
  + '.htv-form input[type=text]{width:100%;padding:11px 14px;border:1.5px solid var(--line-2,#d8cfbf);border-radius:12px;font:inherit;font-size:16px;background:#fff;color:var(--ink,#17140f)}'
  + '.htv-form .go{width:100%;margin-top:18px;display:flex;align-items:center;justify-content:center;gap:9px;padding:14px;border:0;border-radius:999px;background:var(--wa,#1faa59);color:#fff;font:inherit;font-weight:700;font-size:1rem;cursor:pointer}'
  + '.htv-form .go:disabled{opacity:.45;cursor:default}'
  + '.htv-form .fine{margin:10px 0 0;text-align:center;font-size:.8rem;color:var(--muted,#6f685d)}.htv-form .fine a{color:inherit}'
  + '.htv-form .err{color:#c0392b;font-size:.82rem;margin-top:6px;display:none}.htv-form .err.show{display:block}'
  + '.htv-form-wrap{position:relative}.htv-form .htv-x{position:absolute;top:-6px;inset-inline-end:-6px}'
  + '.htv-hp{position:absolute!important;left:-9999px!important;width:1px;height:1px;overflow:hidden}'
  + '@media (max-width:560px){.htv-chat{inset:auto 0 0 0;width:100%;max-width:100%;height:calc(100% - 56px);border-radius:20px 20px 0 0;border-bottom:0}'
  + '.htv-fab{bottom:14px;inset-inline-end:14px;height:50px;padding:0 16px 0 13px}.htv-ov{align-items:flex-end;padding:0}.htv-form{border-radius:22px 22px 0 0;max-height:92vh}}'
  + '@media (prefers-reduced-motion:reduce){.htv-typing i{animation:none}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  var ICON_CHAT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20l1.3-3.9A8 8 0 1 1 8.4 19.3L4 20Z"/><path d="M9 10.5h.01M12 10.5h.01M15 10.5h.01"/></svg>';
  var ICON_SEND = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  var ICON_WA = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20l1.3-3.9A8 8 0 1 1 8.4 19.3L4 20Z"/></svg>';
  var ICON_WARN = '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4M12 17h.01"/></svg>';

  /* ---------------------------------------------------------------- plan cards: which plan / region */
  var PLAN_RE = /--c-(xtv|marvel|basic|premium)/;
  function cardPlan(card){ var m = (card.getAttribute('style') || '').match(PLAN_RE); return m ? m[1] : ''; }
  function cardRegion(card){ var p = closest(card, '[data-region-panel]'); return p ? p.getAttribute('data-region-panel') : ''; }

  /* ---------------------------------------------------------------- 2 + 3: live data (prices, outages, ratings) */
  function setNum(el, n){ if(el && n) el.textContent = el.textContent.replace(/\d[\d,.]*/, String(n)); }
  function applyPrices(p){
    if(!p) return;
    each('article.plan', function(card){
      var plan = cardPlan(card), region = cardRegion(card), v = p[plan];
      if(!v) return;
      var amt = card.querySelector('.price .amt'), two = card.querySelector('.price-2 b');
      if(region === 'gulf') setNum(amt, v.gulf);
      else if(region === 'uae') setNum(amt, v.uae);
      else { setNum(amt, v.y1); setNum(two, v.y2); }
    });
  }
  /* customer-friendly name for what is down (the admin may write "Neo 4K", "X server", "IBO"…) */
  function outageName(o){
    var t = String(o.label || o.target || '').trim();
    if(/neo|basic|أساسي/i.test(t)) return T('the Basic plan (Neo 4K)', 'الباقة الأساسية (Neo 4K)');
    if(/strong|premium|بريميوم/i.test(t)) return T('the Premium plan (Strong 4K)', 'باقة بريميوم (Strong 4K)');
    if(/\bxtv\b|x\s*server|^\s*x\s*$|اكس|إكس/i.test(t)) return T('the XTV plan', 'باقة XTV');
    if(/marvel|مارفل/i.test(t)) return T('the Marvel plan', 'باقة مارفل');
    if(/^all$|all\s*(plans|servers)|كل/i.test(t)) return T('all plans', 'جميع الباقات');
    return t;
  }
  function applyOutages(list){
    if(!list || !list.length) return;
    var header = document.querySelector('header.nav'); if(!header) return;
    var names = [];
    list.forEach(function(o){ var n = outageName(o); if(n && names.indexOf(n) < 0) names.push(n); });
    if(!names.length) return;
    var joined = names.length === 1 ? names[0] : names.slice(0, -1).join(', ') + T(' and ', ' و') + names[names.length - 1];
    var box = document.createElement('div'); box.className = 'htv-alert'; box.setAttribute('role', 'status');
    box.innerHTML = '<div class="wrap">' + ICON_WARN + '<div>'
      + T('<b>' + esc(joined.charAt(0).toUpperCase() + joined.slice(1)) + ' ' + (names.length > 1 ? 'are' : 'is') + ' having a temporary problem.</b> We\'re already working on it — you don\'t need to restart or change anything. It will come back on its own.',
          '<b>توجد مشكلة مؤقتة في ' + esc(joined) + '.</b> نعمل على إصلاحها الآن، ولا داعي لإعادة تشغيل جهازك أو تغيير أي شيء — ستعود الخدمة تلقائياً.')
      + '</div></div>';
    header.parentNode.insertBefore(box, header.nextSibling);
  }
  function applyRatings(r){
    if(!r || r.count < 5 || !r.avg) return;
    var ul = document.querySelector('.trust'); if(!ul || ul.querySelector('.htv-rating')) return;
    var li = document.createElement('li'); li.className = 'htv-rating';
    li.innerHTML = '<span aria-hidden="true" style="color:#f5a524;font-size:1.05em">★</span>' + T('Rated ' + r.avg + '/5 by ' + r.count + ' customers', 'تقييم العملاء ' + r.avg + '/5 (' + r.count + ' تقييم)');
    ul.appendChild(li);
  }
  if(!HELP_PAGE){
    fetch(API + 'site-data', { credentials: 'omit' }).then(function(r){ return r.ok ? r.json() : null; }).then(function(d){
      if(!d) return;
      applyPrices(d.prices); applyOutages(d.outages); applyRatings(d.ratings);
    })['catch'](function(){});
  }

  /* ---------------------------------------------------------------- 4: order / free-trial form */
  var REGIONS = { eg: ['Egypt', 'مصر'], gulf: ['Saudi & Gulf', 'السعودية والخليج'], uae: ['UAE', 'الإمارات'], intl: ['Other countries', 'دول أخرى'] };
  var PLANS = { xtv: ['XTV', 'XTV'], marvel: ['Marvel', 'مارفل'], basic: ['Basic', 'الأساسية'], premium: ['Premium', 'بريميوم'] };
  var DEVICES = [['androidtv', 'Android TV / TV box', 'أندرويد تي في / بوكس'], ['firestick', 'Firestick', 'فايرستيك'], ['smarttv', 'Samsung / LG TV', 'شاشة سامسونج / LG'],
                 ['android', 'Android phone', 'موبايل أندرويد'], ['apple', 'iPhone / Apple TV', 'آيفون / أبل تي في'], ['windows', 'Windows PC', 'كمبيوتر ويندوز'], ['other', 'Other / not sure', 'جهاز آخر / لست متأكداً']];
  function regionGuess(){
    var btn = document.querySelector('[data-region-btn][aria-pressed="true"]'); if(btn) return btn.getAttribute('data-region-btn');
    var r = store('htv-region'); if(REGIONS[r]) return r;
    var tz = ''; try{ tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; }catch(e){}
    if(tz === 'Africa/Cairo') return 'eg'; if(tz === 'Asia/Dubai') return 'uae';
    if(/^Asia\/(Riyadh|Kuwait|Qatar|Bahrain|Muscat|Aden)$/.test(tz)) return 'gulf';
    return 'intl';
  }
  function plansFor(region){ return region === 'eg' ? ['xtv', 'marvel', 'basic', 'premium'] : ['basic', 'premium']; }
  var ov = null, form = { kind: '', plan: '', region: '', device: '', baseText: '', href: '' };
  function optButtons(name, list, current){
    return list.map(function(o){ return '<button type="button" class="opt" data-' + name + '="' + o[0] + '" aria-pressed="' + (o[0] === current) + '">' + esc(ar() ? o[2] : o[1]) + '</button>'; }).join('');
  }
  function renderForm(){
    var trial = form.kind === 'trial', i = ar() ? 1 : 0;
    var planList = plansFor(form.region).map(function(k){ return [k, PLANS[k][0], PLANS[k][1]]; });
    var regionList = ['eg', 'gulf', 'uae', 'intl'].map(function(k){ return [k, REGIONS[k][0], REGIONS[k][1]]; });
    var ready = form.plan && form.device && form.region;
    ov.innerHTML = '<div class="htv-form" role="dialog" aria-modal="true" aria-labelledby="htvFormT"><div class="htv-form-wrap">'
      + '<button type="button" class="htv-x" data-close aria-label="' + T('Close', 'إغلاق') + '">×</button>'
      + '<h3 id="htvFormT">' + (trial ? T('Start your free trial', 'ابدأ تجربتك المجانية') : T('Subscribe', 'اشترك الآن')) + (form.plan ? ' — ' + esc(PLANS[form.plan][i]) : '') + '</h3>'
      + '<p class="sub">' + T('Two quick taps so Hossam can get you set up faster.', 'خطوتان سريعتان ليجهّز حسام اشتراكك أسرع.') + '</p>'
      + '<span class="lbl">' + T('Where do you watch?', 'أين تشاهد؟') + '</span><div class="opts">' + optButtons('fregion', regionList, form.region) + '</div>'
      + '<span class="lbl">' + T('Plan', 'الباقة') + '</span><div class="opts">' + optButtons('fplan', planList, form.plan) + '</div>'
      + '<span class="lbl">' + T('Your device', 'جهازك') + '</span><div class="opts">' + optButtons('fdevice', DEVICES, form.device) + '</div>'
      + '<label class="lbl" for="htvName">' + T('Your name (optional)', 'اسمك (اختياري)') + '</label><input type="text" id="htvName" maxlength="40" autocomplete="given-name" value="' + esc(form.name || '') + '">'
      + '<label class="htv-hp" aria-hidden="true">Website<input type="text" id="htvHp" tabindex="-1" autocomplete="off"></label>'
      + '<button type="button" class="go" data-go' + (ready ? '' : ' disabled') + '>' + ICON_WA + T('Continue on WhatsApp', 'تابع على واتساب') + '</button>'
      + '<p class="fine">' + T('WhatsApp opens with your choices filled in — just press send.', 'سيُفتح واتساب ورسالتك جاهزة — فقط اضغط إرسال.')
      + ' <a href="' + esc(form.href) + '" target="_blank" rel="noopener" data-skip>' + T('Skip', 'تخطَّ') + '</a></p>'
      + '</div></div>';
  }
  function openForm(kind, plan, region, href){
    if(!ov){
      ov = document.createElement('div'); ov.className = 'htv-ov'; ov.hidden = true; document.body.appendChild(ov);
      ov.addEventListener('click', onFormClick);
      ov.addEventListener('input', function(e){ if(e.target.id === 'htvName') form.name = e.target.value; });
    }
    var base = ''; try{ base = decodeURIComponent((href.split('?text=')[1] || '').replace(/\+/g, ' ')); }catch(e){}
    form = { kind: kind, plan: plan || '', region: region || regionGuess(), device: form.device || '', name: form.name || '', baseText: base, href: href, fromCard: !!plan };
    if(form.plan && plansFor(form.region).indexOf(form.plan) < 0) form.plan = '';
    renderForm(); ov.hidden = false; document.body.style.overflow = 'hidden';
    var first = ov.querySelector('[data-fdevice]'); if(first) try{ first.focus({ preventScroll: true }); }catch(e){ first.focus(); }
  }
  function closeForm(){ if(ov){ ov.hidden = true; document.body.style.overflow = ''; } }
  function onFormClick(e){
    var t = e.target, b;
    if(t === ov || closest(t, '[data-close]')){ closeForm(); return; }
    if(closest(t, '[data-skip]')){ closeForm(); return; }
    if((b = closest(t, '[data-fregion]'))){ form.region = b.getAttribute('data-fregion'); if(plansFor(form.region).indexOf(form.plan) < 0) form.plan = ''; renderForm(); return; }
    if((b = closest(t, '[data-fplan]'))){ form.plan = b.getAttribute('data-fplan'); renderForm(); return; }
    if((b = closest(t, '[data-fdevice]'))){ form.device = b.getAttribute('data-fdevice'); renderForm(); var go = ov.querySelector('[data-go]'); if(go && !go.disabled) go.focus(); return; }
    if(closest(t, '[data-go]')) submitForm();
  }
  function submitForm(){
    if(!form.plan || !form.device || !form.region) return;
    var i = ar() ? 1 : 0, dev = DEVICES.filter(function(d){ return d[0] === form.device; })[0];
    var name = (document.getElementById('htvName') || {}).value || '';
    var hp = (document.getElementById('htvHp') || {}).value || '';
    var planLine = PLANS[form.plan][i] + ' (' + REGIONS[form.region][i] + ')';
    var text = form.baseText ? form.baseText
      : (form.kind === 'trial' ? T('Hi Hossam TV, I\'d like a free trial.', 'مرحباً Hossam TV، أريد تجربة مجانية.') : T('Hi Hossam TV, I\'d like to subscribe.', 'مرحباً Hossam TV، أريد الاشتراك.'));
    if(!form.fromCard) text += '\n' + T('Plan: ', 'الباقة: ') + planLine;
    text += '\n' + T('Device: ', 'الجهاز: ') + (ar() ? dev[2] : dev[1]);
    if(name.trim()) text += '\n' + T('Name: ', 'الاسم: ') + name.trim().slice(0, 40);
    try{ post('site-order', { kind: form.kind, plan: form.plan, region: form.region, device: form.device, name: name.trim(), lang: ar() ? 'ar' : 'en', website: hp }, true)['catch'](function(){}); }catch(e){}
    window.open('https://wa.me/' + MAIN + '?text=' + encodeURIComponent(text), '_blank', 'noopener');
    closeForm();
  }
  function waKind(a){
    var href = a.getAttribute('href') || '';
    if(href.indexOf('wa.me/') < 0 || href.indexOf('?text=') < 0) return '';
    var txt = ''; try{ txt = decodeURIComponent(href.split('?text=')[1]).toLowerCase(); }catch(e){ return ''; }
    if(/free trial|تجربة/.test(txt)) return 'trial';
    if(/\bsubscribe\b|الاشتراك في|أشترك/.test(txt)) return 'subscribe';
    return '';
  }
  document.addEventListener('click', function(e){
    if(e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey) return;
    var a = closest(e.target, 'a[href*="wa.me/"]'); if(!a || closest(a, '.htv-ov, .htv-chat') || a.className.indexOf('htv-') > -1) return;
    var kind = waKind(a); if(!kind) return;
    var card = closest(a, 'article.plan');
    e.preventDefault();
    openForm(kind, card ? cardPlan(card) : '', card ? cardRegion(card) : '', a.getAttribute('href'));
  });

  /* ---------------------------------------------------------------- 1: chat bubble */
  var KEY = 'htv-chat';
  var chat = null; try{ chat = JSON.parse(store(KEY) || 'null'); }catch(e){}
  if(!chat || !chat.sid || Date.now() - (chat.t || 0) > 86400000){
    var sid = ''; for(var k = 0; k < 20; k++) sid += 'abcdefghijklmnopqrstuvwxyz0123456789'.charAt(Math.floor(Math.random() * 36));
    chat = { sid: sid, t: Date.now(), msgs: [], open: false };
  }
  function save(){ chat.t = Date.now(); chat.msgs = chat.msgs.slice(-40); store(KEY, JSON.stringify(chat)); }
  var fab = document.createElement('button'); fab.type = 'button'; fab.className = 'htv-fab';
  var panel = document.createElement('div'); panel.className = 'htv-chat'; panel.hidden = true; panel.setAttribute('role', 'dialog');
  document.body.appendChild(fab); document.body.appendChild(panel);
  var busy = false;

  function fmt(text){
    var s = esc(text);
    s = s.replace(/(https?:\/\/[^\s<]+[^\s<.,;:!?)\]'"])/g, function(u){ return '<a href="' + u + '" target="_blank" rel="noopener">' + u + '</a>'; });
    s = s.replace(/(^|[\s(])((?:tinyurl\.com|bit\.ly|hossamservices\.com)\/[A-Za-z0-9_\-\/]+)/g, function(m, pre, u){ return pre + '<a href="https://' + u + '" target="_blank" rel="noopener">' + u + '</a>'; });
    s = s.replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>').replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,!?:;]|$)/g, '$1<b>$2</b>');
    return s.replace(/\n/g, '<br>');
  }
  function msgHTML(m){
    if(m.who === 'me') return '<div class="htv-m me" dir="auto">' + esc(m.text).replace(/\n/g, '<br>') + '</div>';
    return '<div class="htv-m bot" dir="auto">' + fmt(m.text)
      + (m.logo ? '<div class="htv-logo"><img src="' + esc(m.logo.src) + '" alt="" width="40" height="40">' + esc(m.logo.name) + '</div>' : '')
      + (m.wa ? '<br><a class="htv-wa" href="' + esc(m.wa) + '" target="_blank" rel="noopener">' + ICON_WA + T('Continue on WhatsApp', 'تابع على واتساب') + '</a>' : '')
      + '</div>';
  }
  function chips(){
    if(chat.msgs.length) return '';
    var list = ar() ? ['كم سعر الاشتراك؟', 'أريد تجربة مجانية', 'القنوات لا تعمل', 'أي تطبيق أستخدم على شاشتي؟']
                    : ['How much is it?', 'I want a free trial', 'Channels not working', 'Which app for my TV?'];
    return '<div class="htv-chips">' + list.map(function(c){ return '<button type="button" class="htv-chip">' + esc(c) + '</button>'; }).join('') + '</div>';
  }
  function renderChat(){
    var hello = T('Hi! 👋 I\'m Hossam TV\'s automated assistant — a bot, not a person, and not our main WhatsApp. Ask me about plans, prices, setup or any problem and I\'ll reply in seconds.',
                  'مرحباً! 👋 أنا المساعد الآلي لـ Hossam TV — بوت وليس شخصاً، ولست رقم الواتساب الرئيسي. اسألني عن الباقات والأسعار والتثبيت أو أي مشكلة وسأردّ خلال ثوانٍ.');
    fab.innerHTML = ICON_CHAT + '<span>' + T('Ask our bot', 'اسأل البوت') + '</span><span class="htv-badge">' + T('BOT', 'آلي') + '</span>';
    fab.setAttribute('aria-label', T('Chat with our automated assistant (bot)', 'تحدث مع المساعد الآلي (بوت)'));
    panel.setAttribute('aria-label', T('Chat with the Hossam TV bot', 'محادثة مع بوت Hossam TV'));
    var logoSrc = (document.querySelector('.brand img, link[rel="icon"]') || {});
    logoSrc = logoSrc.src || logoSrc.href || '/logo.png';
    panel.innerHTML = '<div class="htv-chat-h"><img src="' + esc(logoSrc) + '" alt=""><div><b>' + T('Hossam TV assistant', 'مساعد Hossam TV') + '<span class="htv-badge">' + T('BOT', 'آلي') + '</span></b><small>' + T('Automated AI replies · not a person', 'ردود آلية بالذكاء الاصطناعي · ليس شخصاً') + '</small></div>'
      + '<button type="button" class="htv-x" data-close aria-label="' + T('Close', 'إغلاق') + '">×</button></div>'
      + '<div class="htv-msgs" aria-live="polite">' + msgHTML({ who: 'bot', text: hello }) + chat.msgs.map(msgHTML).join('') + (busy ? '<div class="htv-typing" aria-label="…"><i></i><i></i><i></i></div>' : '') + '</div>'
      + chips()
      + '<form class="htv-in"><textarea rows="1" maxlength="600" dir="auto" placeholder="' + T('Type your message…', 'اكتب رسالتك…') + '" aria-label="' + T('Message', 'الرسالة') + '"></textarea>'
      + '<button type="submit" class="htv-send" aria-label="' + T('Send', 'إرسال') + '"' + (busy ? ' disabled' : '') + '>' + ICON_SEND + '</button></form>'
      + '<div class="htv-note">' + T('This is a bot. To talk to a person, ', 'هذا بوت آلي. للتحدث مع شخص، ')
      + '<a href="https://wa.me/' + MAIN + '" target="_blank" rel="noopener">' + T('message Hossam on WhatsApp', 'راسل حسام على واتساب') + '</a>.</div>';
    var box = panel.querySelector('.htv-msgs'); box.scrollTop = box.scrollHeight;
  }
  function setOpen(open){
    chat.open = open; save();
    panel.hidden = !open; fab.hidden = open;
    if(open){ renderChat(); var ta = panel.querySelector('textarea'); if(ta && window.innerWidth > 560) ta.focus(); }
    else fab.focus();
  }
  function send(text){
    text = String(text || '').trim(); if(!text || busy) return;
    chat.msgs.push({ who: 'me', text: text.slice(0, 600) }); busy = true; save(); renderChat();
    var done = function(m){ busy = false; chat.msgs.push(m); save(); if(!panel.hidden){ renderChat(); var ta = panel.querySelector('textarea'); if(ta && window.innerWidth > 560) ta.focus(); } };
    var ctrl = window.AbortController ? new AbortController() : null, timer = setTimeout(function(){ if(ctrl) ctrl.abort(); }, 90000);
    var body = new URLSearchParams(); body.append('p', JSON.stringify({ sid: chat.sid, message: text.slice(0, 600), lang: ar() ? 'ar' : 'en', page: location.pathname }));
    fetch(API + 'site-chat', { method: 'POST', body: body, credentials: 'omit', signal: ctrl ? ctrl.signal : undefined })
      .then(function(r){ return r.json(); })
      .then(function(d){ clearTimeout(timer); if(!d || !d.reply) throw new Error('empty'); done({ who: 'bot', text: d.reply, wa: d.whatsapp || '', logo: d.logo || null }); })
      ['catch'](function(){ clearTimeout(timer); done({ who: 'bot', text: T('Sorry, I couldn\'t connect. Please try again, or message us on WhatsApp.', 'عذراً، تعذّر الاتصال. حاول مرة أخرى، أو راسلنا على واتساب.'), wa: 'https://wa.me/' + MAIN }); });
  }
  fab.addEventListener('click', function(){ setOpen(true); });
  panel.addEventListener('click', function(e){
    if(closest(e.target, '[data-close]')){ setOpen(false); return; }
    var c = closest(e.target, '.htv-chip'); if(c) send(c.textContent);
  });
  panel.addEventListener('submit', function(e){ e.preventDefault(); var ta = panel.querySelector('textarea'); var v = ta.value; ta.value = ''; send(v); });
  panel.addEventListener('keydown', function(e){
    if(e.target.tagName === 'TEXTAREA' && e.key === 'Enter' && !e.shiftKey && !e.isComposing){ e.preventDefault(); var v = e.target.value; e.target.value = ''; send(v); }
  });
  panel.addEventListener('input', function(e){ if(e.target.tagName === 'TEXTAREA'){ e.target.style.height = '44px'; e.target.style.height = Math.min(120, e.target.scrollHeight + 2) + 'px'; } });
  document.addEventListener('keydown', function(e){
    if(e.key !== 'Escape') return;
    if(ov && !ov.hidden) closeForm(); else if(!panel.hidden) setOpen(false);
  });
  /* help.html switches language without reloading — keep the widget's labels in step */
  if(window.MutationObserver) new MutationObserver(function(){ renderChat(); if(ov && !ov.hidden) renderForm(); }).observe(doc, { attributes: true, attributeFilter: ['lang'] });
  renderChat();
  if(chat.open && window.innerWidth > 560) setOpen(true);
})();
