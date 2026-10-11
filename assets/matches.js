/* Hossam TV — matches ticker + live-score bar (ES5). Used by every page, including help.html.
   - [data-ticker]: this week's big matches (assets/data/matches.json, refreshed every 6 hours by a GitHub Action)
   - [data-live]:   only while a match is on — score, minute and goal scorers straight from ESPN, refreshed every 30 s */
(function(){
  'use strict';
  var L = {
    en: { cairo: 'Cairo', toronto: 'Toronto', live: 'LIVE', ht: 'HT', ft: 'FT', goal: 'GOAL!', og: 'OG', pen: 'pen', soon: 'Kick-off soon' },
    ar: { cairo: 'القاهرة', toronto: 'تورونتو', live: 'مباشر', ht: 'استراحة', ft: 'انتهت', goal: 'جووول!', og: 'عكسي', pen: 'جزاء', soon: 'تبدأ قريباً' }
  };
  var ESPN = 'https://site.api.espn.com/apis/site/v2/sports/soccer/';
  var LIVE_BEFORE = 5 * 60e3, LIVE_AFTER = 150 * 60e3;   /* a match counts as "on" from 5 min before kick-off to 2.5 h after */
  var data = null, lastScore = {}, flashUntil = {};

  function lang(){ return document.documentElement.lang === 'ar' ? 'ar' : 'en'; }
  function T(k){ return L[lang()][k]; }
  function nm(x){ return x ? (lang() === 'ar' ? x.ar : x.en) : ''; }
  function el(tag, cls, text){ var e = document.createElement(tag); if(cls) e.className = cls; if(text != null) e.textContent = text; return e; }
  function hm(d, tz){
    try{ return d.toLocaleString(lang() === 'ar' ? 'ar-EG' : 'en-US', { timeZone: tz, weekday: 'short', hour: 'numeric', minute: '2-digit', hour12: true }).toUpperCase(); }catch(e){ return ''; }
  }
  function speed(track, group){ track.style.animationDuration = Math.max(20, Math.round((group.getBoundingClientRect().width || 1200) / 45)) + 's'; }
  /* fill a scrolling track: two copies make the loop seamless; a single short item just sits still */
  function fill(track, group, still){
    track.textContent = '';
    track.appendChild(group);
    if(still){ track.classList.add('still'); return; }
    track.classList.remove('still');
    track.appendChild(group.cloneNode(true));
    speed(track, group);
  }

  /* ---------- this week's matches ---------- */
  function renderTicker(){
    var now = Date.now();
    var list = ((data && data.events) || []).filter(function(e){ return Date.parse(e.utc) + 2 * 3600e3 > now; }).slice(0, 20);
    Array.prototype.forEach.call(document.querySelectorAll('[data-ticker]'), function(bar){
      var track = bar.querySelector('.ticker-track');
      if(!list.length){ bar.hidden = true; return; }
      var g = el('span', 'ticker-group');
      list.forEach(function(e){
        var k = new Date(e.utc), on = now >= k.getTime() && now < k.getTime() + 2 * 3600e3, it = el('span', 'tk');
        /* each match reads: ◆ TEAMS · Cairo time · Toronto time · channel */
        it.appendChild(el('span', 'tk-teams', nm(e.home) + ' – ' + nm(e.away)));
        if(on) it.appendChild(el('span', 'tk-live', T('live')));
        else {
          it.appendChild(el('span', 'tk-time', T('cairo') + ' ' + hm(k, 'Africa/Cairo')));
          it.appendChild(el('span', 'tk-time', T('toronto') + ' ' + hm(k, 'America/Toronto')));
        }
        if(e.channel) it.appendChild(el('span', 'tk-ch', lang() === 'ar' ? e.channel.ar : e.channel.en));
        g.appendChild(it);
      });
      bar.hidden = false;
      fill(track, g, false);
    });
  }

  /* ---------- live scores ---------- */
  function liveNow(){
    var now = Date.now();
    return ((data && data.events) || []).filter(function(e){ var k = Date.parse(e.utc); return now >= k - LIVE_BEFORE && now < k + LIVE_AFTER; });
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
    if(!bars.length) return;
    var on = liveNow();
    if(!on.length){ Array.prototype.forEach.call(bars, function(b){ b.hidden = true; }); return; }
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
        rows.push(row);
      });
      renderLive(rows);
    });
  }
  function renderLive(rows){
    Array.prototype.forEach.call(document.querySelectorAll('[data-live]'), function(bar){
      var track = bar.querySelector('.ticker-track');
      if(!rows.length){ bar.hidden = true; return; }
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
        if(r.e.channel) it.appendChild(el('span', 'tk-ch', lang() === 'ar' ? r.e.channel.ar : r.e.channel.en));
        g.appendChild(it);
      });
      bar.hidden = false;
      /* one match fits -> stays still; more than one -> scrolls like the matches bar */
      fill(track, g, rows.length < 2);
    });
  }

  /* ---------- start ---------- */
  var src = document.querySelector('[data-ticker]') || document.querySelector('[data-live]');
  if(!src || !window.fetch) return;
  fetch(src.getAttribute('data-src'), { cache: 'no-cache' })
    .then(function(r){ return r.ok ? r.json() : null; })
    .then(function(d){
      data = d; renderTicker(); pollLive();
      setInterval(pollLive, 30e3);          /* live scores every 30 s */
      setInterval(renderTicker, 5 * 60e3);  /* move finished matches off the ticker */
    })['catch'](function(){});
  /* help.html switches language without reloading */
  if(window.MutationObserver) new MutationObserver(function(){ if(data){ renderTicker(); pollLive(); } })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
})();
