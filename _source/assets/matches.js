/* Hossam TV — matches ticker + live-score bar (ES5). Used by every page, including help.html.
   - [data-ticker]: this week's big matches (assets/data/matches.json, refreshed every 6 hours by a GitHub Action)
   - [data-live]:   only while a match is on — score, minute and goal scorers from ESPN (Egyptian league: TheSportsDB),
                    refreshed every 30 s; a match leaves both bars as soon as it's over */
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
  /* fill a scrolling track: the items are repeated until they're wider than the bar, then doubled,
     so even a single match scrolls in a seamless loop.
     No flicker: nothing is rebuilt if the text didn't change, and the scroll speed (animation duration) is only changed
     when the width changes a lot — changing it restarts/jumps the scroll. */
  function fill(track, group){
    var sig = lang() + '|' + group.textContent;
    if(track.getAttribute('data-sig') === sig && track.children.length) return;
    track.setAttribute('data-sig', sig);
    while(track.firstChild) track.removeChild(track.firstChild);
    track.appendChild(group);
    var win = track.parentNode, need = Math.max((win && win.getBoundingClientRect().width) || 0, 800), items = Array.prototype.slice.call(group.children), n = 0;
    while(group.getBoundingClientRect().width < need && group.getBoundingClientRect().width > 0 && n++ < 12){
      items.forEach(function(it){ group.appendChild(it.cloneNode(true)); });
    }
    track.appendChild(group.cloneNode(true));
    var old = parseFloat(track.style.animationDuration) || 0, dur = Math.max(20, Math.round((group.getBoundingClientRect().width || 1200) / 45));
    if(!old || Math.abs(dur - old) / old > 0.2) track.style.animationDuration = dur + 's';
    save();
  }
  /* remember what the bars showed, so the next page opens with them already in place (no jump while loading) */
  function save(){
    try{
      var c = { t: Date.now(), lang: document.documentElement.lang };
      [['[data-ticker]', 'ticker'], ['[data-live]', 'live']].forEach(function(p){
        var b = document.querySelector(p[0]), tr = b && b.querySelector('.ticker-track');
        c[p[1]] = b && !b.hidden && tr ? { html: tr.innerHTML, dur: tr.style.animationDuration } : null;
      });
      localStorage.setItem('htv-bars', JSON.stringify(c));
    }catch(e){}
  }

  /* ---------- this week's matches ---------- */
  function renderTicker(){
    var now = Date.now();
    var list = ((data && data.events) || []).filter(function(e){ return !finished[e.id] && Date.parse(e.utc) + 2 * 3600e3 > now; }).slice(0, 20);
    Array.prototype.forEach.call(document.querySelectorAll('[data-ticker]'), function(bar){
      var track = bar.querySelector('.ticker-track');
      if(!list.length){ bar.hidden = true; save(); return; }
      var g = el('span', 'ticker-group');
      list.forEach(function(e){
        var k = new Date(e.utc), on = now >= k.getTime() && now < k.getTime() + 2 * 3600e3, it = el('span', 'tk');
        /* each match reads: ◆ TEAMS · kick-off in the visitor's time zone · channel */
        it.appendChild(el('span', 'tk-teams', nm(e.home) + ' – ' + nm(e.away)));
        if(on) it.appendChild(el('span', 'tk-live', T('live')));
        else {
          it.appendChild(el('span', 'tk-time', hm(k, TZ || undefined) + ' · ' + tzLabel()));
        }
        var ch = channel(e); if(ch) it.appendChild(el('span', 'tk-ch', ch));
        g.appendChild(it);
      });
      bar.hidden = false;
      fill(track, g);
    });
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
    location.href = root + lang() + '/match/' + slug(e.home.en) + '-vs-' + slug(e.away.en) + '-' + e.utc.slice(0, 10) + '.ics';
  }

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
  function renderNext(){
    var boxes = document.querySelectorAll('[data-next]');
    if(!boxes.length) return;
    var now = Date.now();
    nextEvent = ((data && data.events) || []).filter(function(e){ return e.top && !finished[e.id] && Date.parse(e.utc) > now; })   /* high-profile matches only */
      .sort(function(a, b){ return Date.parse(a.utc) - Date.parse(b.utc); })[0] || null;
    Array.prototype.forEach.call(boxes, function(box){
      if(!nextEvent){ box.hidden = true; return; }
      var e = nextEvent, k = new Date(e.utc), ch = channel(e);
      box.querySelector('[data-next-league]').textContent = T('next') + ' · ' + nm(e.league);
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
    });
    tick();
    if(!nextTimer) nextTimer = setInterval(tick, 1000);
  }
  function tick(){
    if(document.hidden || !nextEvent) return;
    var left = Date.parse(nextEvent.utc) - Date.now();
    if(left <= 0){ renderNext(); return; }                     /* kicked off: the live bar takes over, show the next one */
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
    var bars = document.querySelectorAll('[data-live]');
    if(!bars.length || document.hidden) return;   /* no polling in a background tab */
    var on = liveNow();
    if(!on.length){ Array.prototype.forEach.call(bars, function(b){ b.hidden = true; }); document.documentElement.classList.remove('htv-live-on'); save(); return; }
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
      if(Object.keys(finished).length) renderTicker();
      renderLive(rows);
      /* the matches page shows the same live score */
      window.htvFinished = finished;
      window.htvLive = {};
      rows.forEach(function(r){ window.htvLive[r.e.id] = { hs: r.hs, as: r.as, clock: r.clock, state: r.state }; });
      try{ document.dispatchEvent(new CustomEvent('htv:live')); }catch(e){}
    });
  }
  function renderLive(rows){
    document.documentElement.classList.toggle('htv-live-on', rows.length > 0);
    Array.prototype.forEach.call(document.querySelectorAll('[data-live]'), function(bar){
      var track = bar.querySelector('.ticker-track');
      if(!rows.length){ bar.hidden = true; save(); return; }
      var g = el('span', 'ticker-group');
      rows.forEach(function(r){
        var it = el('span', 'lv' + (flashUntil[r.e.id] > Date.now() ? ' lv-goal' : '') + (r.state === 'post' ? ' lv-ft' : ''));
        if(flashUntil[r.e.id] > Date.now()) it.appendChild(el('span', 'lv-flash', T('goal')));
        if(r.clock) it.appendChild(el('span', 'lv-clock', r.clock));
        it.appendChild(el('span', 'lv-team', nm(r.e.home)));
        /* digits read left-to-right: in Arabic the home team is on the right, so its score goes on the right */
        if(r.hs != null){ it.appendChild(el('span', 'lv-score', lang() === 'ar' ? r.as + ' – ' + r.hs : r.hs + ' – ' + r.as)); }
        else it.appendChild(el('span', 'lv-vs', '–'));
        it.appendChild(el('span', 'lv-team', nm(r.e.away)));
        var sc = r.g.all;
        if(sc.length) it.appendChild(el('span', 'lv-goals', '⚽ ' + sc.join(' · ')));
        var ch = channel(r.e); if(ch) it.appendChild(el('span', 'tk-ch', ch));
        g.appendChild(it);
      });
      bar.hidden = false;
      fill(track, g);
    });
  }

  /* ---------- start ---------- */
  var src = document.querySelector('[data-ticker]') || document.querySelector('[data-live]') || document.querySelector('[data-next]') || document.querySelector('[data-results]');
  if(!src || !window.fetch) return;
  fetch(src.getAttribute('data-src'), { cache: 'no-cache' })
    .then(function(r){ return r.ok ? r.json() : null; })
    .then(function(d){
      data = d; renderTicker(); renderNext(); renderResults(); pollLive();
      setInterval(pollLive, 30e3);          /* live scores every 30 s */
      setInterval(renderTicker, 5 * 60e3);  /* move finished matches off the ticker */
    })['catch'](function(){});
  /* the admin's channels arrive a moment later (site-data) -> redraw */
  document.addEventListener('htv:channels', function(){ if(data){ renderTicker(); renderNext(); pollLive(); } });
  /* back to the tab -> fresh scores right away */
  document.addEventListener('visibilitychange', function(){ if(!document.hidden && data) pollLive(); });
  /* help.html switches language without reloading */
  if(window.MutationObserver) new MutationObserver(function(){ if(data){ renderTicker(); renderNext(); renderResults(); pollLive(); } })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
})();
