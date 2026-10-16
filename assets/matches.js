/* Hossam TV — match cards row under the header (ES5). Used by every page.
   - [data-strip]: a swipeable row of small match cards — live matches first (score + minute from ESPN / TheSportsDB,
                   refreshed every 30 s), then this week's big matches (assets/data/matches.json, refreshed every 6 hours
                   by a GitHub Action) with kick-off in the visitor's time zone and the channel. Each card opens the matches
                   page on that match's countdown (with Add to calendar); the last card opens all matches. A match leaves the row as soon as it's over. */
(function(){
  'use strict';
  var L = {
    en: { mine: 'Your time', live: 'LIVE', ht: 'HT', ft: 'FT', goal: 'GOAL!', og: 'OG', pen: 'pen', soon: 'Kick-off soon',
          next: 'Big match', d: 'days', h: 'hrs', m: 'min', s: 'sec' },
    ar: { mine: 'بتوقيتك', live: 'مباشر', ht: 'استراحة', ft: 'انتهت', goal: 'جووول!', og: 'عكسي', pen: 'جزاء', soon: 'تبدأ قريباً',
          next: 'قمة قادمة', d: 'يوم', h: 'ساعة', m: 'دقيقة', s: 'ثانية' }
  };
  var ESPN = 'https://site.api.espn.com/apis/site/v2/sports/soccer/';
  var LIVE_BEFORE = 5 * 60e3, LIVE_AFTER = 150 * 60e3;   /* a match counts as "on" from 5 min before kick-off to 2.5 h after */
  var SDB = 'https://www.thesportsdb.com/api/v1/json/3/lookupevent.php?id=';
  var NO_DATA_AFTER = 115 * 60e3;   /* no score source answered: assume a match lasts ~1 h 55 min */
  var data = null, lastScore = {}, flashUntil = {}, finished = {};

  /* channel per league: the admin bot can override it ("channel: Premier League = beIN Sports 1"), via site-data.
     "English / عربي" in the admin's text gives a different name per language. */
  function key(t){ return String(t || '').toLowerCase().replace(/[^a-z\u0600-\u06ff]+/g, ''); }
  function channel(e){
    var o = window.htvChannels || {}, lg = e.league || {}, names = [key(lg.en), key(lg.ar)], hit = null;
    Object.keys(o).forEach(function(k){
      var kk = key(k);
      if(kk && names.some(function(n){ return n && (n === kk || n.indexOf(kk) >= 0 || kk.indexOf(n) >= 0); })) hit = String(o[k]);
    });
    if(hit){ var parts = hit.split(/\s+\/\s+/); return lang() === 'ar' && parts[1] ? parts[1] : parts[0]; }
    return e.channel ? (lang() === 'ar' ? e.channel.ar : e.channel.en) : '';
  }
  window.htvChannelFor = channel;

  /* the visitor's own time zone (from the browser — no permission needed); English shows its city, e.g. "Vancouver" */
  var TZ = ''; try{ TZ = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; }catch(e){}
  function tzLabel(){
    if(lang() === 'ar' || !/\//.test(TZ)) return T('mine');
    return TZ.split('/').pop().replace(/_/g, ' ');
  }

  function lang(){ return document.documentElement.lang === 'ar' ? 'ar' : 'en'; }
  function T(k){ return L[lang()][k]; }
  function nm(x){ return x ? (lang() === 'ar' ? x.ar : x.en) : ''; }
  function el(tag, cls, text){ var e = document.createElement(tag); if(cls) e.className = cls; if(text != null) e.textContent = text; return e; }
  function hm(d, tz){
    try{ return d.toLocaleString(lang() === 'ar' ? 'ar-EG' : 'en-US', { timeZone: tz || undefined, weekday: 'short', hour: 'numeric', minute: '2-digit', hour12: true }).toUpperCase(); }catch(e){ return ''; }
  }
  /* ---------- the match cards row ---------- */
  var liveRows = [];
  function slugOf(x){ return String(x || '').normalize('NFKD').replace(/[^\x00-\x7f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); }
  function teamLine(x, score, win){
    var t = el('span', 'ms-t' + (win ? ' win' : ''));
    var n = lang() === 'ar' ? nm(x) : short(nm(x));
    if(x && x.logo){ var im = el('img'); im.alt = ''; im.width = 20; im.height = 20; im.loading = 'lazy'; im.src = x.logo;
      im.onerror = function(){ var c = el('i', 'ms-ini', (n.replace(/^(?:al|el|ال)[\s-]?/i, '').charAt(0) || '?').toUpperCase()); this.parentNode.replaceChild(c, this); }; t.appendChild(im); }
    else t.appendChild(el('i', 'ms-ini', (n.replace(/^(?:al|el|ال)[\s-]?/i, '').charAt(0) || '?').toUpperCase()));
    t.appendChild(el('b', null, n));
    if(score != null) t.appendChild(el('em', null, String(score)));
    return t;
  }
  function renderStrip(){
    var strips = document.querySelectorAll('[data-strip]');
    if(!strips.length) return;
    var now = Date.now(), live = {}, order = [];
    liveRows.forEach(function(r){ live[r.e.id] = r; });
    var list = ((data && data.events) || []).filter(function(e){ return !finished[e.id] && (live[e.id] || Date.parse(e.utc) + 2 * 3600e3 > now); });
    list.sort(function(a, b){ return (live[b.id] ? 1 : 0) - (live[a.id] ? 1 : 0) || Date.parse(a.utc) - Date.parse(b.utc); });   /* live first */
    list = list.slice(0, 12);
    Array.prototype.forEach.call(strips, function(box){
      var track = box.querySelector('[data-strip-track]'), root = box.getAttribute('data-root') || '', L2 = lang();
      if(!list.length){ box.hidden = true; save(); return; }
      var frag = document.createDocumentFragment();
      list.forEach(function(e){
        var r = live[e.id], k = new Date(e.utc), goal = r && flashUntil[e.id] > now;
        var href = root + L2 + '/matches.html#m=' + encodeURIComponent(e.id);   /* the matches page opens on this match's countdown */
        var a = el('a', 'ms-card' + (r ? ' ms-live' : '') + (goal ? ' ms-goal' : '')); a.href = href;
        var top = el('span', 'ms-top');
        if(goal) top.appendChild(el('span', 'ms-flag', T('goal')));
        else if(r){ var lv = el('span', 'ms-flag'); lv.appendChild(el('i', 'live-dot')); lv.appendChild(document.createTextNode(' ' + (r.clock || T('live')))); top.appendChild(lv); }
        else top.appendChild(el('span', 'ms-when', hm(k, TZ || undefined)));
        a.appendChild(top);
        var hs = r && r.hs != null ? +r.hs : null, as = r && r.as != null ? +r.as : null;
        a.appendChild(teamLine(e.home, hs, hs != null && hs > as));
        a.appendChild(teamLine(e.away, as, as != null && as > hs));
        var ch = channel(e); if(ch) a.appendChild(el('span', 'ms-ch', ch));
        frag.appendChild(a);
      });
      var all = el('a', 'ms-card ms-all'); all.href = root + L2 + '/matches.html';
      all.appendChild(el('b', null, L2 === 'ar' ? 'كل المباريات' : 'All matches'));
      all.appendChild(el('span', 'ms-arrow', L2 === 'ar' ? '←' : '→'));
      frag.appendChild(all);
      var keep = track.scrollLeft;
      while(track.firstChild) track.removeChild(track.firstChild);
      track.appendChild(frag);
      track.scrollLeft = keep;      /* a refresh doesn't jump the row back to the start */
      box.hidden = false;
    });
    save();
  }
  /* the cards float over the top of the page: the first section slides up behind the row (same total height, so nothing jumps) */
  function floatStrip(){
    var b = document.querySelector('[data-strip]'), m = document.querySelector('main'), f = m && m.firstElementChild;
    while(f && /^(STYLE|SCRIPT)$/.test(f.tagName)) f = f.nextElementSibling;
    if(f && f.classList.contains('fixp')) f = f.firstElementChild;
    if(!b || !f) return;
    f.style.paddingTop = '';
    var h = b.hidden ? 0 : b.offsetHeight;
    b.style.marginBottom = h ? -h + 'px' : '';
    if(h) f.style.paddingTop = (parseFloat(getComputedStyle(f).paddingTop) || 0) + h + 'px';
  }
  floatStrip();
  window.addEventListener('resize', floatStrip);
  /* the row drifts slowly back and forth so it's clear it scrolls; a touch, hover or tap stops it for a while */
  function driftStrip(){
    var b = document.querySelector('[data-strip]'), tr = b && b.querySelector('[data-strip-track]');
    if(!tr || !window.requestAnimationFrame || (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)) return;
    var SPEED = 18, dir = 1, pos = null, last = 0, holdUntil = Date.now() + 2500, busy = false;
    var rtl = getComputedStyle(tr).direction === 'rtl';
    var hold = function(ms){ holdUntil = Date.now() + ms; pos = null; tr.style.scrollSnapType = ''; };
    ['pointerdown', 'touchstart', 'wheel', 'focusin'].forEach(function(ev){ tr.addEventListener(ev, function(){ hold(8000); }, { passive: true }); });
    tr.addEventListener('mouseenter', function(){ busy = true; hold(1e9); });
    tr.addEventListener('mouseleave', function(){ busy = false; hold(2500); });
    function step(t){
      var dt = last ? Math.min(t - last, 100) / 1000 : 0; last = t;
      var max = tr.scrollWidth - tr.clientWidth;
      if(!busy && !b.hidden && !document.hidden && max > 4 && Date.now() > holdUntil){
        if(pos === null) pos = Math.abs(tr.scrollLeft);
        tr.style.scrollSnapType = 'none';
        pos += dir * SPEED * dt;
        if(pos >= max){ pos = max; dir = -1; hold(3000); }
        else if(pos <= 0){ pos = 0; dir = 1; hold(3000); }
        tr.scrollLeft = rtl ? -pos : pos;
      }
      requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  driftStrip();
  /* remember the row, so the next page opens with it already in place (no jump while loading) */
  function save(){
    floatStrip();
    try{
      var b = document.querySelector('[data-strip]'), tr = b && b.querySelector('[data-strip-track]');
      localStorage.setItem('htv-strip', JSON.stringify({ t: Date.now(), lang: document.documentElement.lang, html: b && !b.hidden && tr ? tr.innerHTML : '' }));
    }catch(e){}
  }

  /* ---------- countdown to the next big match (home + matches page) ---------- */
  var nextTimer = 0, nextEvent = null;
  /* shorter English names so both team boxes fit on one line */
  var SHORT = { 'Manchester United': 'Man United', 'Manchester City': 'Man City', 'Paris Saint-Germain': 'PSG', 'Borussia Dortmund': 'Dortmund',
                'Internazionale': 'Inter Milan', 'Tottenham Hotspur': 'Tottenham', 'Bayern Munich': 'Bayern', 'Atlético Madrid': 'Atlético',
                'Atletico Madrid': 'Atlético', 'Newcastle United': 'Newcastle', 'Paris Saint Germain': 'PSG', 'Pyramids FC': 'Pyramids' };
  function short(n){ return SHORT[n] || n; }
  window.htvShort = short;   /* also used by the matches list (assets/site.js) */
  function logo(img, team){
    if(!img) return;
    var src = team && team.logo;
    if(!src){ img.hidden = true; img.removeAttribute('src'); return; }
    img.onerror = function(){ this.hidden = true; };
    if(img.getAttribute('src') !== src) img.src = src;
    img.hidden = false;
  }
  /* "Add to calendar": a tiny .ics file (works with Google, Apple and Samsung calendars) with a reminder 30 min before */
  /* Android: Google Calendar opens with the match filled in.
     iPhone / iPad / computers: the site's .ics file for this match (built with the match page) -> "Add to Calendar". */
  function slug(x){ return String(x || '').normalize('NFKD').replace(/[^\x00-\x7f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); }
  function addToCalendar(e, box){
    if(!e) return;
    var t = new Date(e.utc), end = new Date(t.getTime() + 2 * 3600e3), ch = channel(e);
    var title = nm(e.home) + ' – ' + nm(e.away) + ' (' + nm(e.league) + ')';
    if(/Android/i.test(navigator.userAgent)){
      var f = function(d){ return d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, ''); };
      window.open('https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + encodeURIComponent(title) +
        '&dates=' + f(t) + '/' + f(end) + '&details=' + encodeURIComponent((ch ? ch + ' · ' : '') + (box.getAttribute('data-l-cal') || '')), '_blank', 'noopener');
      return;
    }
    var root = (box.getAttribute('data-src') || '').replace(/assets\/data\/matches\.json$/, '');
    location.href = root + lang() + '/cal/' + e.id + '.ics';
  }

  /* ---------- every match: a countdown [data-cd="<utc>"] and an "Add to calendar" link [data-cal="<utc>"] ----------
     (rows of the matches list, league pages, match pages). The link is the match's .ics file (iPhone / computers);
     on Android it opens Google Calendar instead. */
  function cdText(left){
    var d = Math.floor(left / 864e5), h = Math.floor(left / 36e5) % 24, m = Math.floor(left / 6e4) % 60, s = Math.floor(left / 1e3) % 60;
    return (d ? d + (lang() === 'ar' ? ' يوم ' : 'd ') : '') + pad(h) + ':' + pad(m) + ':' + pad(s);
  }
  function tickRows(){
    if(document.hidden) return;
    var now = Date.now();
    Array.prototype.forEach.call(document.querySelectorAll('[data-cd]'), function(c){
      var left = Date.parse(c.getAttribute('data-cd')) - now, box = c.closest ? c.closest('.mt-act') || c : c;
      if(left <= 0){ box.hidden = true; return; }                      /* kicked off: the live score takes over */
      var t = cdText(left); if(c.lastChild && c.lastChild.nodeType === 3){ if(c.lastChild.nodeValue !== t) c.lastChild.nodeValue = t; } else c.appendChild(document.createTextNode(t));
    });
  }
  setInterval(tickRows, 1000); tickRows();
  window.htvTickRows = tickRows;   /* the matches list (assets/site.js) calls it after drawing */
  document.addEventListener('click', function(ev){
    var a = ev.target.closest ? ev.target.closest('a[data-cal]') : null;
    if(!a || !/Android/i.test(navigator.userAgent)) return;
    ev.preventDefault();
    var t = new Date(a.getAttribute('data-cal')), end = new Date(t.getTime() + 2 * 3600e3);
    var f = function(d){ return d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, ''); };
    window.open('https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + encodeURIComponent(a.getAttribute('data-cal-t') || '') +
      '&dates=' + f(t) + '/' + f(end) + '&details=' + encodeURIComponent((lang() === 'ar' ? 'شاهدها مباشرة على Hossam TV — hossamservices.com' : 'Watch live on Hossam TV — hossamservices.com')), '_blank', 'noopener');
  });

  /* ---------- last week's results (matches page) ---------- */
  function renderResults(){
    var box = document.querySelector('[data-results]');
    if(!box) return;
    var list = (data && data.results) || [], wrap = box.querySelector('[data-results-list]');
    if(!list.length){ box.hidden = true; return; }
    while(wrap.firstChild) wrap.removeChild(wrap.firstChild);
    list.forEach(function(r){
      var row = el('div', 'rs-row'), d = new Date(r.utc);
      var meta = el('div', 'rs-meta');
      var day = ''; try{ day = d.toLocaleDateString(lang() === 'ar' ? 'ar-EG' : 'en-US', { timeZone: TZ || undefined, weekday: 'short', day: 'numeric', month: 'short' }); }catch(x){}
      meta.textContent = nm(r.league) + ' · ' + day;
      row.appendChild(meta);
      var line = el('div', 'rs-line');
      [['home', r.hs, r.as], ['away', r.as, r.hs]].forEach(function(p, i){
        var side = el('div', 'rs-team' + (p[1] > p[2] ? ' win' : ''));
        var img = el('img'); img.alt = ''; img.width = 26; img.height = 26; img.loading = 'lazy';
        var tn = short(nm(r[p[0]]));
        var ini = function(){ var c = el('span', 'mt-ini rs-ini', (tn.replace(/^(?:al|el|ال)[\s-]?/i, '').charAt(0) || '?').toUpperCase()); c.setAttribute('aria-hidden', 'true'); return c; };
        logo(img, r[p[0]]);
        if(img.hidden) img = ini(); else img.onerror = function(){ this.replaceWith(ini()); };   /* no badge: the first letter */
        side.appendChild(img); side.appendChild(el('span', null, tn));
        if(i === 1){ line.appendChild(el('b', 'rs-score', lang() === 'ar' ? r.as + ' – ' + r.hs : r.hs + ' – ' + r.as));   /* RTL: home team is on the right */ }
        line.appendChild(side);
      });
      row.appendChild(line);
      wrap.appendChild(row);
    });
    box.hidden = false;
  }

  function pad(n){ return (n < 10 ? '0' : '') + n; }
  /* home page: one line under the hero — "⚽ Roma vs Real Madrid · in 20 hours · Watch it live →" (opens the free-trial form) */
  function renderNextLine(){
    var line = document.querySelector('[data-next-line]');
    if(!line) return;
    var now = Date.now(), e = ((data && data.events) || []).filter(function(x){ return x.top && !finished[x.id] && Date.parse(x.utc) > now; })
      .sort(function(a, b){ return Date.parse(a.utc) - Date.parse(b.utc); })[0];
    if(!e){ line.hidden = true; return; }
    var A = function(k){ return line.getAttribute('data-l-' + k) || ''; }, left = Date.parse(e.utc) - now, when;
    if(left < 36e5) when = A('in') + ' ' + Math.max(1, Math.round(left / 6e4)) + ' ' + A('m');
    else if(left < 864e5) when = A('in') + ' ' + Math.round(left / 36e5) + ' ' + A('h');
    else when = hm(new Date(e.utc), TZ || undefined);
    line.querySelector('[data-next-line-teams]').textContent = short(nm(e.home)) + (lang() === 'ar' ? ' ضد ' : ' vs ') + short(nm(e.away));
    line.querySelector('[data-next-line-when]').textContent = when;
    line.hidden = false;
  }

  function renderNext(){
    renderNextLine();
    var boxes = document.querySelectorAll('[data-next]');
    if(!boxes.length) return;
    var now = Date.now();
    var want = pickedId(), picked = want ? ((data && data.events) || []).filter(function(e){ return String(e.id) === want && !finished[e.id]; })[0] : null;
    nextEvent = picked || ((data && data.events) || []).filter(function(e){ return e.top && !finished[e.id] && Date.parse(e.utc) > now; })   /* high-profile matches only */
      .sort(function(a, b){ return Date.parse(a.utc) - Date.parse(b.utc); })[0] || null;
    Array.prototype.forEach.call(boxes, function(box){
      if(!nextEvent){ box.hidden = true; return; }
      var e = nextEvent, k = new Date(e.utc), ch = channel(e);
      box.querySelector('[data-next-league]').textContent = e.top ? T('next') + ' · ' + nm(e.league) : nm(e.league);
      box.querySelector('[data-next-home]').textContent = short(nm(e.home));
      box.querySelector('[data-next-away]').textContent = short(nm(e.away));
      /* logos only when both teams have one, so the two boxes stay alike */
      var hl = box.querySelector('[data-next-home-logo]'), al = box.querySelector('[data-next-away-logo]'), both = e.home.logo && e.away.logo;
      logo(hl, both ? e.home : null); logo(al, both ? e.away : null);
      hl.onerror = al.onerror = function(){ hl.hidden = al.hidden = true; };
      var cal = box.querySelector('[data-next-cal]');
      if(cal && !cal.getAttribute('data-on')){ cal.setAttribute('data-on', '1'); cal.addEventListener('click', function(){ addToCalendar(nextEvent, box); }); }
      box.querySelector('[data-next-when]').textContent = hm(k, TZ || undefined) + ' · ' + tzLabel() + (ch ? ' · ' + ch : '');
      ['d', 'h', 'm', 's'].forEach(function(u){ box.querySelector('[data-next-l="' + u + '"]').textContent = T(u); });
      box.hidden = false;
      /* opened from a match card: bring this countdown into view (once per pick) */
      if(picked && box.getAttribute('data-shown') !== want){
        box.setAttribute('data-shown', want);
        setTimeout(function(){ try{ box.scrollIntoView({ behavior: 'smooth', block: 'center' }); }catch(x){ box.scrollIntoView(); } }, 60);
      }
    });
    tick();
    if(!nextTimer) nextTimer = setInterval(tick, 1000);
  }
  function pickedId(){ var m = /[#&]m=([^&]+)/.exec(location.hash || ''); return m ? decodeURIComponent(m[1]) : ''; }
  /* a picked match that has kicked off: "● LIVE  1 – 0  54'" instead of the countdown */
  function showLive(e){
    var on = Date.now() >= Date.parse(e.utc), lv = (window.htvLive || {})[e.id];
    Array.prototype.forEach.call(document.querySelectorAll('[data-next]'), function(box){
      var count = box.querySelector('.nm-count'), lb = box.querySelector('[data-next-livebox]');
      if(!lb) return;
      count.hidden = on; lb.hidden = !on;
      var cal = box.querySelector('[data-next-cal]'); if(cal) cal.hidden = on;          /* nothing to add to a calendar once it's on */
      if(on) box.querySelector('[data-next-league]').textContent = nm(e.league);        /* "Big match ·" → just the league */
      if(!on) return;
      lb.textContent = '';
      var tag = el('span', 'nm-live-tag'); tag.appendChild(el('i', 'live-dot')); tag.appendChild(document.createTextNode(' ' + T('live'))); lb.appendChild(tag);
      if(lv && lv.hs != null) lb.appendChild(el('b', 'nm-live-score', lang() === 'ar' ? lv.as + ' – ' + lv.hs : lv.hs + ' – ' + lv.as));
      if(lv && lv.clock) lb.appendChild(el('span', 'nm-live-clock', lv.clock));
    });
  }
  function tick(){
    if(document.hidden || !nextEvent) return;
    var left = Date.parse(nextEvent.utc) - Date.now();
    showLive(nextEvent);
    if(left <= 0){ if(pickedId() === String(nextEvent.id)) return; renderNext(); return; }   /* kicked off: a picked match shows its live score, otherwise the next one */
    var v = { d: Math.floor(left / 864e5), h: Math.floor(left / 36e5) % 24, m: Math.floor(left / 6e4) % 60, s: Math.floor(left / 1e3) % 60 };
    Array.prototype.forEach.call(document.querySelectorAll('[data-next]'), function(box){
      ['d', 'h', 'm', 's'].forEach(function(u){ var b = box.querySelector('[data-next-v="' + u + '"]'); var t = u === 'd' ? String(v[u]) : pad(v[u]); if(b.textContent !== t) b.textContent = t; });
    });
  }

  /* ---------- live scores ---------- */
  function liveNow(){
    var now = Date.now();
    return ((data && data.events) || []).filter(function(e){ var k = Date.parse(e.utc); return !finished[e.id] && now >= k - LIVE_BEFORE && now < k + LIVE_AFTER; });
  }
  /* ESPN's "day" is US Eastern: ask for the kick-off date there */
  function espnDay(utc){
    try{
      var p = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(utc));
      return p.replace(/-/g, '');
    }catch(e){ return utc.slice(0, 10).replace(/-/g, ''); }
  }
  function goals(comp, homeId){
    var out = { home: [], away: [], all: [] };
    /* in the order they were scored */
    (comp.details || []).slice().sort(function(a, b){ return (parseInt(a.clock && a.clock.displayValue, 10) || 0) - (parseInt(b.clock && b.clock.displayValue, 10) || 0); })
    .forEach(function(d){
      if(!d.scoringPlay) return;
      var who = (d.athletesInvolved && d.athletesInvolved[0] && (d.athletesInvolved[0].shortName || d.athletesInvolved[0].displayName)) || '';
      var min = (d.clock && d.clock.displayValue) || '';
      var tag = d.ownGoal ? ' (' + T('og') + ')' : d.penaltyKick ? ' (' + T('pen') + ')' : '';
      var side = d.team && String(d.team.id) === String(homeId) ? 'home' : 'away';
      out[side].push(who + ' ' + min + tag);
      out.all.push(who + ' ' + min + tag);
    });
    return out;
  }
  function pollLive(){
    if(!document.querySelector('[data-strip],[data-matches]') || document.hidden) return;   /* no polling in a background tab */
    var on = liveNow();
    if(!on.length){ if(liveRows.length) renderLive([]); return; }
    /* one ESPN request per league + day */
    var want = {}, rows = [];
    on.forEach(function(e){ if(e.espn && e.code) want[e.code + '|' + espnDay(e.utc)] = 1; });
    var keys = Object.keys(want), results = {};
    var jobs = keys.map(function(key){
      var parts = key.split('|');
      return fetch(ESPN + parts[0] + '/scoreboard?dates=' + parts[1], { cache: 'no-store' })
        .then(function(r){ return r.ok ? r.json() : null; })
        .then(function(d){ ((d && d.events) || []).forEach(function(ev){ results[ev.id] = ev; }); })['catch'](function(){});
    });
    /* Egyptian league (not on ESPN): TheSportsDB, one request per match */
    var sdb = {};
    on.forEach(function(e){
      if(e.espn || String(e.id).charAt(0) !== 's') return;
      jobs.push(fetch(SDB + String(e.id).slice(1), { cache: 'no-store' })
        .then(function(r){ return r.ok ? r.json() : null; })
        .then(function(d){ var x = d && d.events && d.events[0]; if(x) sdb[e.id] = x; })['catch'](function(){}));
    });
    Promise.all(jobs).then(function(){
      on.forEach(function(e){
        var ev = e.espn && results[e.espn];
        var row = { e: e, state: 'in', clock: '', hs: null, as: null, g: { home: [], away: [], all: [] } };
        if(ev){
          var comp = ev.competitions[0], st = ev.status || {}, ty = st.type || {};
          var home = null, away = null;
          (comp.competitors || []).forEach(function(c){ if(c.homeAway === 'home') home = c; else away = c; });
          row.state = ty.state || 'in';
          row.clock = ty.state === 'post' ? T('ft') : (ty.name === 'STATUS_HALFTIME' || /^half\s*-?time$/i.test(ty.description || '') || ty.shortDetail === 'HT') ? T('ht') : (st.displayClock || '');
          if(home && away){ row.hs = home.score; row.as = away.score; row.g = goals(comp, home.team && home.team.id); }
          if(row.state === 'pre' && Date.parse(e.utc) > Date.now()){ row.clock = T('soon'); }
          /* a new goal since the last check -> flash for 12 s */
          var sc = row.hs + '-' + row.as, prev = lastScore[e.id];
          if(prev != null && prev !== sc && row.state === 'in') flashUntil[e.id] = Date.now() + 12e3;
          lastScore[e.id] = sc;
        }
        var x = sdb[e.id];
        if(!ev && x){
          var stt = String(x.strStatus || '').toUpperCase(), prog = String(x.strProgress || '').replace(/[^\d+]/g, '');
          row.state = /^(FT|AET|PEN|MATCH FINISHED|AP|AWD|WO|CANC|PST|ABD)/.test(stt) ? 'post'
                    : /^(NS|NOT STARTED|TBD|)$/.test(stt) ? 'pre' : 'in';
          row.clock = stt === 'HT' ? T('ht') : row.state === 'pre' ? T('soon') : prog ? prog + "'" : '';
          if(x.intHomeScore != null && x.intHomeScore !== '' && row.state !== 'pre'){ row.hs = x.intHomeScore; row.as = x.intAwayScore; }
          var sc2 = row.hs + '-' + row.as, prev2 = lastScore[e.id];
          if(prev2 != null && prev2 !== sc2 && row.state === 'in') flashUntil[e.id] = Date.now() + 12e3;
          lastScore[e.id] = sc2;
        }
        /* over -> off both bars; no source at all -> assume ~1 h 55 min */
        if(row.state === 'post' || (!ev && !x && Date.now() > Date.parse(e.utc) + NO_DATA_AFTER)){ finished[e.id] = true; return; }
        rows.push(row);
      });
      renderLive(rows);
      /* the matches page shows the same live score */
      window.htvFinished = finished;
      window.htvLive = {};
      rows.forEach(function(r){ window.htvLive[r.e.id] = { hs: r.hs, as: r.as, clock: r.clock, state: r.state }; });
      try{ document.dispatchEvent(new CustomEvent('htv:live')); }catch(e){}
    });
  }
  function renderLive(rows){ liveRows = rows; renderStrip(); if(nextEvent) showLive(nextEvent); }

  /* ---------- start ---------- */
  var src = document.querySelector('[data-strip]') || document.querySelector('[data-next-line]') || document.querySelector('[data-next]') || document.querySelector('[data-results]');
  if(!src || !window.fetch) return;
  fetch(src.getAttribute('data-src'), { cache: 'no-cache' })
    .then(function(r){ return r.ok ? r.json() : null; })
    .then(function(d){
      data = d; renderStrip(); renderNext(); renderResults(); pollLive();
      setInterval(pollLive, 30e3);          /* live scores every 30 s */
      setInterval(function(){ renderStrip(); renderNextLine(); }, 60e3);   /* kick-off times pass, finished matches leave */
    })['catch'](function(){});
  /* the admin's channels arrive a moment later (site-data) -> redraw */
  document.addEventListener('htv:channels', function(){ if(data){ renderStrip(); renderNext(); pollLive(); } });
  /* a match card tapped while already on the matches page */
  window.addEventListener('hashchange', function(){ if(data) renderNext(); });
  /* back to the tab -> fresh scores right away */
  document.addEventListener('visibilitychange', function(){ if(!document.hidden && data) pollLive(); });
  /* the page language changes without reloading */
  if(window.MutationObserver) new MutationObserver(function(){ if(data){ renderStrip(); renderNext(); renderResults(); pollLive(); } })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
})();
