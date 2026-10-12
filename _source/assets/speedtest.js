/* Hossam TV — internet speed test for streaming (speed-test.html). ES5.
   1) delay: 10 tiny requests -> ping (median) and jitter (how much it varies)
   2) download from Cloudflare's speed-test server for up to 8 s (25 MB at most) -> speed, sampled every 0.5 s
      -> stability: does the speed hold steady, or keep dropping (that's what makes TV freeze)?
   The verdict weighs all three: speed for the quality, stability for freezing, ping for how fast channels start. */
(function(){
  'use strict';
  var box = document.querySelector('[data-speedtest]');
  if(!box) return;
  var A = function(k){ return box.getAttribute('data-l-' + k) || ''; };
  var $ = function(sel){ return box.querySelector(sel); };
  var go = $('[data-st-start]'), again = $('[data-st-again]'), readout = $('[data-st-readout]'), stats = $('[data-st-stats]');
  var num = $('[data-st-num]'), msg = $('[data-st-msg]'), arc = $('[data-st-arc]'), needle = $('[data-st-needle]');
  var pingEl = $('[data-st-ping]'), jitEl = $('[data-st-jitter]'), stabEl = $('[data-st-stab]');
  var nameIn = $('[data-st-name]'), logBox = document.querySelector('[data-st-log]'), logList = document.querySelector('[data-st-log-list]');
  var AR = document.documentElement.lang === 'ar';
  var hint = $('[data-st-hint]'), tips = document.querySelector('[data-st-tips]'), tiles = document.querySelectorAll('[data-need]');
  var CF = 'https://speed.cloudflare.com/__down?bytes=';
  var LIMIT = 8000, BYTES = 25000000, MARKS = [0, 5, 10, 25, 50, 100], SLICE = 500, WARMUP = 1500;
  var arcLen = arc.getTotalLength ? arc.getTotalLength() : 408;
  arc.style.strokeDasharray = arcLen; arc.style.strokeDashoffset = arcLen;
  var shown = 0, target = 0, raf = 0;

  /* ---------- gauge ---------- */
  function frac(m){
    if(m <= 0) return 0;
    for(var i = 1; i < MARKS.length; i++){
      if(m <= MARKS[i]) return (i - 1 + (m - MARKS[i - 1]) / (MARKS[i] - MARKS[i - 1])) / (MARKS.length - 1);
    }
    return 1;
  }
  function draw(){
    shown += (target - shown) * 0.18;
    if(Math.abs(target - shown) < 0.05) shown = target;
    var f = frac(shown);
    arc.style.strokeDashoffset = arcLen * (1 - f);
    needle.style.transform = 'rotate(' + (-135 + f * 270) + 'deg)';   /* the glowing dot rides the 270° ring */
    num.textContent = shown >= 100 ? Math.round(shown) : (Math.round(shown * 10) / 10).toFixed(shown < 10 ? 1 : 0);
    raf = shown !== target ? requestAnimationFrame(draw) : 0;
  }
  function setSpeed(m){ target = m; if(!raf) raf = requestAnimationFrame(draw); }
  function setState(cls){ box.className = box.className.replace(/\bst-(good|ok|bad|run)\b/g, '').trim() + (cls ? ' st-' + cls : ''); }
  function stat(el, text, cls){ el.textContent = text; el.className = cls || ''; }
  function mark(mbps){
    Array.prototype.forEach.call(tiles, function(t){
      var need = +t.getAttribute('data-need');
      t.classList.toggle('pass', mbps != null && mbps >= need);
      t.classList.toggle('fail', mbps != null && mbps < need);
    });
  }
  function median(a){ var b = a.slice().sort(function(x, y){ return x - y; }); var m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2; }

  /* ---------- 1) delay ---------- */
  function measurePing(){
    var times = [], i = 0;
    function one(){
      var t = performance.now();
      return fetch(CF + '0&r=' + Math.random(), { cache: 'no-store' }).then(function(r){ return r.arrayBuffer(); }).then(function(){
        times.push(performance.now() - t);
        return ++i < 11 ? one() : null;
      });
    }
    return one().then(function(){
      var s = times.slice(1);                       /* the first one also opens the connection: skip it */
      var jit = 0; for(var k = 1; k < s.length; k++) jit += Math.abs(s[k] - s[k - 1]);
      return { ping: median(s), jitter: s.length > 1 ? jit / (s.length - 1) : 0 };
    });
  }

  /* ---------- 2) download + stability ---------- */
  function measureDownload(){
    return new Promise(function(resolve){
      var ctrl = window.AbortController ? new AbortController() : null, bytes = 0, t0 = 0, sliceStart = 0, sliceBytes = 0, samples = [];
      var guard = setTimeout(function(){ if(ctrl) ctrl.abort(); }, LIMIT + 4000);
      function avg(){ var s = (performance.now() - t0) / 1000; return s > 0 ? bytes * 8 / s / 1e6 : 0; }
      function done(){ clearTimeout(guard); resolve({ mbps: avg(), ok: bytes > 200000, samples: samples }); }
      fetch(CF + BYTES, { cache: 'no-store', signal: ctrl ? ctrl.signal : undefined })
        .then(function(r){
          if(!r.ok || !r.body) throw new Error('bad');
          var reader = r.body.getReader(); t0 = sliceStart = performance.now();
          function pump(){
            return reader.read().then(function(x){
              var now = performance.now();
              if(x.done || now - t0 > LIMIT){ try{ reader.cancel(); }catch(e){} return done(); }
              bytes += x.value.length; sliceBytes += x.value.length;
              if(now - sliceStart >= SLICE){                                     /* speed of the last half-second */
                var gaps = Math.floor((now - sliceStart) / SLICE) - 1;           /* nothing arrived for a while = stalled slices */
                if(now - t0 > WARMUP){
                  for(var g = 0; g < gaps; g++) samples.push(0);
                  samples.push(sliceBytes * 8 / ((now - sliceStart - gaps * SLICE) / 1000) / 1e6);
                }
                sliceStart = now; sliceBytes = 0;
              }
              setSpeed(avg());
              return pump();
            });
          }
          return pump();
        })['catch'](function(){ done(); });
    });
  }
  /* steady = the half-second speeds stay close to their middle value and never collapse */
  function stability(samples, mbps){
    if(samples.length < 4) return { stable: true, score: 1 };
    var mid = median(samples), low = Math.min.apply(null, samples);
    var mean = samples.reduce(function(a, b){ return a + b; }, 0) / samples.length;
    var sd = Math.sqrt(samples.reduce(function(a, b){ return a + (b - mean) * (b - mean); }, 0) / samples.length);
    var cv = mean ? sd / mean : 0;
    var dips = low < mid * 0.35 && low < 10;                                     /* a real drop, not a fast line wobbling */
    return { stable: cv < 0.35 && !dips, score: cv };
  }

  /* ---------- verdict ---------- */
  function finish(p, d){
    again.hidden = false;
    if(!d.ok){ setState('bad'); setSpeed(0); msg.textContent = A('error'); mark(null); return; }
    var st = stability(d.samples, d.mbps), mbps = d.mbps;
    setSpeed(mbps);
    stat(stabEl, st.stable ? A('stable') : A('shaky'), st.stable ? 'good' : 'warn');
    if(p){
      stat(pingEl, Math.round(p.ping) + ' ms', p.ping < 150 ? 'good' : 'warn');
      stat(jitEl, Math.round(p.jitter) + ' ms', p.jitter < 50 ? 'good' : 'warn');
    }
    var shaky = !st.stable || (p && (p.jitter >= 150 || p.ping >= 300));
    if(mbps < 5){ setState('bad'); msg.textContent = A('rslow'); }               /* speed alone sets the verdict and colour */
    else if(mbps >= 25){ setState('good'); msg.textContent = A('r4k'); }
    else if(mbps >= 10){ setState('ok'); msg.textContent = A('rhd'); }
    else { setState('ok'); msg.textContent = A('rsd'); }
    if(hint) hint.hidden = !shaky || mbps < 5;                                   /* dips/delay: a calm tip, not an alarm */
    mark(mbps);
    if(tips) tips.hidden = mbps >= 25 && !shaky;
    send({ mbps: Math.round(mbps * 10) / 10, ping: p ? Math.round(p.ping) : null, jitter: p ? Math.round(p.jitter) : null, stable: !!st.stable });
  }

  /* ---------- name + "Latest tests": each result goes to n8n (site-speed) so Hossam sees it without asking ---------- */
  try{ if(nameIn) nameIn.value = localStorage.getItem('htv-name') || ''; }catch(e){}
  function where(){ var z = ''; try{ z = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; }catch(e){} return z.split('/').pop().replace(/_/g, ' '); }
  function send(r){
    var n = nameIn ? nameIn.value.trim() : '';
    if(!n || !window.fetch || !window.URLSearchParams) return;
    r.name = n; r.where = where(); r.lang = AR ? 'ar' : 'en';
    var body = new URLSearchParams(); body.append('p', JSON.stringify(r));
    fetch(box.getAttribute('data-api'), { method: 'POST', body: body, credentials: 'omit' })
      .then(function(x){ return x.json()['catch'](function(){ return {}; }); })
      .then(function(){})['catch'](function(){});
    r.at = new Date().toISOString();
    try{ var m = mine(); m.unshift(r); localStorage.setItem('htv-mytests', JSON.stringify(m.slice(0, 5))); }catch(e){}
    renderLog(merge(lastLog));
  }
  var lastLog = [];
  function ago(iso){
    var m = Math.max(0, Math.round((Date.now() - Date.parse(iso)) / 60000));
    if(m < 1) return AR ? 'الآن' : 'just now';
    if(m < 60) return AR ? 'منذ ' + m + ' د' : m + ' min ago';
    var h = Math.round(m / 60); if(h < 24) return AR ? 'منذ ' + h + ' س' : h + ' h ago';
    var d = Math.round(h / 24); return AR ? 'منذ ' + d + ' يوم' : d + ' d ago';
  }
  function renderLog(list){
    if(!logBox || !logList || !list || !list.length) return;
    lastLog = list;
    while(logList.firstChild) logList.removeChild(logList.firstChild);
    list.slice(0, 10).forEach(function(r){
      var row = document.createElement('div'); row.className = 'st-log-row';
      var who = document.createElement('div'); who.className = 'st-log-who';
      var b = document.createElement('b'); b.textContent = String(r.name || '').slice(0, 30); who.appendChild(b);
      var sm = document.createElement('small'); sm.textContent = [r.where, ago(r.at)].filter(Boolean).join(' · '); who.appendChild(sm);
      var sp = document.createElement('div'); sp.className = 'st-log-num ' + (r.mbps >= 25 ? 'good' : r.mbps >= 5 ? 'ok' : 'bad'); sp.dir = 'ltr'; sp.textContent = r.mbps + ' Mbps';
      var ex = document.createElement('div'); ex.className = 'st-log-ex'; ex.dir = 'ltr';
      ex.textContent = (r.ping != null ? r.ping + ' ms' : '—') + ' · ' + (r.stable ? A('stable') : A('shaky'));
      row.appendChild(who); row.appendChild(sp); row.appendChild(ex);
      logList.appendChild(row);
    });
    logBox.hidden = false;
  }
  /* the list: fetched fresh here (site-data is cached for 2 min elsewhere, which would hide a test just taken);
     the visitor's own recent tests are kept on the phone too, so they never vanish on refresh */
  function mine(){ try{ return JSON.parse(localStorage.getItem('htv-mytests') || '[]').filter(function(r){ return Date.now() - Date.parse(r.at) < 7 * 864e5; }); }catch(e){ return []; } }
  function merge(list){
    var all = (list || []).concat(mine()), seen = {}, out = [];
    all.sort(function(a, b){ return Date.parse(b.at) - Date.parse(a.at); }).forEach(function(r){
      var k = String(r.name).toLowerCase() + '|' + r.mbps + '|' + Math.round(Date.parse(r.at) / 120000);   /* same test from both sources */
      if(!seen[k]){ seen[k] = 1; out.push(r); }
    });
    return out.slice(0, 10);
  }
  if(mine().length) renderLog(merge([]));
  if(window.fetch) fetch(box.getAttribute('data-api').replace(/site-speed$/, 'site-data'), { cache: 'no-store', credentials: 'omit' })
    .then(function(r){ return r.ok ? r.json() : null; })
    .then(function(d){ if(d && d.speedtests) renderLog(merge(d.speedtests)); })['catch'](function(){});
  function run(){
    if(nameIn && !nameIn.value.trim()){ msg.textContent = A('needname'); nameIn.focus(); nameIn.classList.add('st-need-name'); return; }
    if(nameIn){ nameIn.classList.remove('st-need-name'); try{ localStorage.setItem('htv-name', nameIn.value.trim()); }catch(e){} }
    if(!window.fetch || !window.ReadableStream || !window.Promise){ window.open('https://fast.com', '_blank', 'noopener'); return; }
    go.hidden = true; if(hint) hint.hidden = true; readout.hidden = false; again.hidden = true; stats.hidden = false;
    stat(pingEl, '—'); stat(jitEl, '—'); stat(stabEl, '—');
    setState('run'); shown = 0; setSpeed(0); mark(null); msg.textContent = A('ping');
    var p = null;
    measurePing().then(function(r){ p = r; stat(pingEl, Math.round(r.ping) + ' ms'); stat(jitEl, Math.round(r.jitter) + ' ms'); }, function(){})
      .then(function(){ msg.textContent = A('testing'); return measureDownload(); })
      .then(function(d){ finish(p, d); });
  }
  go.addEventListener('click', run);
  again.addEventListener('click', run);
})();
