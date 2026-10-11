/* Hossam TV — internet speed test (speed-test.html). Downloads test data from Cloudflare's speed-test server
   for up to 8 seconds (25 MB at most — kind to mobile data); a gauge shows the speed live, then the page says
   whether it's enough for SD / HD / 4K. ES5. */
(function(){
  'use strict';
  var box = document.querySelector('[data-speedtest]');
  if(!box) return;
  var A = function(k){ return box.getAttribute('data-l-' + k) || ''; };
  var go = box.querySelector('[data-st-start]'), again = box.querySelector('[data-st-again]'), readout = box.querySelector('[data-st-readout]');
  var num = box.querySelector('[data-st-num]'), msg = box.querySelector('[data-st-msg]');
  var arc = box.querySelector('[data-st-arc]'), needle = box.querySelector('[data-st-needle]');
  var tips = document.querySelector('[data-st-tips]'), tiles = document.querySelectorAll('[data-need]');
  var LIMIT = 8000, BYTES = 25000000, MARKS = [0, 5, 10, 25, 50, 100];
  var arcLen = arc.getTotalLength ? arc.getTotalLength() : 408;
  arc.style.strokeDasharray = arcLen; arc.style.strokeDashoffset = arcLen;
  var shown = 0, target = 0, raf = 0;

  /* gauge position 0..1 — stretched at the low end where the SD/HD/4K limits are */
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
  function mark(mbps){
    Array.prototype.forEach.call(tiles, function(t){
      var need = +t.getAttribute('data-need');
      t.classList.toggle('pass', mbps != null && mbps >= need);
      t.classList.toggle('fail', mbps != null && mbps < need);
    });
  }
  function finish(mbps, ok){
    again.hidden = false;
    if(!ok){ setState('bad'); setSpeed(0); msg.textContent = A('error'); mark(null); return; }
    setSpeed(mbps);
    if(mbps >= 25){ setState('good'); msg.textContent = A('r4k'); }
    else if(mbps >= 10){ setState('ok'); msg.textContent = A('rhd'); }
    else if(mbps >= 5){ setState('ok'); msg.textContent = A('rsd'); }
    else { setState('bad'); msg.textContent = A('rslow'); }
    mark(mbps);
    if(tips) tips.hidden = mbps >= 25;
  }
  function run(){
    if(!window.fetch || !window.ReadableStream){ window.open('https://fast.com', '_blank', 'noopener'); return; }
    go.hidden = true; readout.hidden = false; again.hidden = true;
    setState('run'); shown = 0; setSpeed(0); msg.textContent = A('testing'); mark(null);
    var ctrl = window.AbortController ? new AbortController() : null, bytes = 0, t0 = 0;
    var guard = setTimeout(function(){ if(ctrl) ctrl.abort(); }, LIMIT + 4000);
    function speedNow(){ var s = (performance.now() - t0) / 1000; return s > 0 ? bytes * 8 / s / 1e6 : 0; }
    fetch('https://speed.cloudflare.com/__down?bytes=' + BYTES, { cache: 'no-store', signal: ctrl ? ctrl.signal : undefined })
      .then(function(r){
        if(!r.ok || !r.body) throw new Error('bad');
        var reader = r.body.getReader(); t0 = performance.now();
        function pump(){
          return reader.read().then(function(x){
            if(x.done || performance.now() - t0 > LIMIT){ try{ reader.cancel(); }catch(e){} clearTimeout(guard); return finish(speedNow(), bytes > 200000); }
            bytes += x.value.length;
            setSpeed(speedNow());                                   /* the needle follows the speed live */
            return pump();
          });
        }
        return pump();
      })['catch'](function(){ clearTimeout(guard); finish(t0 ? speedNow() : 0, !!t0 && bytes > 200000); });
  }
  go.addEventListener('click', run);
  again.addEventListener('click', run);
})();
