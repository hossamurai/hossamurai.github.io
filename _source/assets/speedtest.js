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
  var tips = document.querySelector('[data-st-tips]'), tiles = document.querySelectorAll('[data-need]');
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
    needle.style.transform = 'rotate(' + (-90 + f * 180) + 'deg)';
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
    stat(stabEl, st.stable ? A('stable') : A('shaky'), st.stable ? 'good' : 'bad');
    if(p){
      stat(pingEl, Math.round(p.ping) + ' ms', p.ping < 100 ? 'good' : p.ping < 200 ? 'warn' : 'bad');
      stat(jitEl, Math.round(p.jitter) + ' ms', p.jitter < 30 ? 'good' : p.jitter < 80 ? 'warn' : 'bad');
    }
    var shaky = !st.stable || (p && p.jitter >= 80);
    if(mbps < 5){ setState('bad'); msg.textContent = A('rslow'); }
    else if(shaky){ setState('bad'); msg.textContent = A('unstable'); }
    else if(mbps >= 25){ setState(p && p.ping >= 200 ? 'ok' : 'good'); msg.textContent = p && p.ping >= 200 ? A('slowstart') : A('r4k'); }
    else if(mbps >= 10){ setState('ok'); msg.textContent = A('rhd'); }
    else { setState('ok'); msg.textContent = A('rsd'); }
    mark(mbps);
    if(tips) tips.hidden = mbps >= 25 && !shaky;
  }
  function run(){
    if(!window.fetch || !window.ReadableStream || !window.Promise){ window.open('https://fast.com', '_blank', 'noopener'); return; }
    go.hidden = true; readout.hidden = false; again.hidden = true; stats.hidden = false;
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
