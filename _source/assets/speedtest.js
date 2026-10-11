/* Hossam TV — internet speed test (speed-test.html). Downloads test data from Cloudflare's speed-test server
   for up to 8 seconds (25 MB at most — kind to mobile data) and says whether it's enough for SD / HD / 4K. ES5. */
(function(){
  'use strict';
  var box = document.querySelector('[data-speedtest]');
  if(!box) return;
  var A = function(k){ return box.getAttribute('data-l-' + k) || ''; };
  var btn = box.querySelector('[data-st-start]'), num = box.querySelector('[data-st-num]'), msg = box.querySelector('[data-st-msg]');
  var bar = box.querySelector('[data-st-bar]'), tips = document.querySelector('[data-st-tips]');
  var tiles = document.querySelectorAll('[data-need]');
  var LIMIT = 8000, BYTES = 25000000;
  function fmt(m){ return m >= 100 ? String(Math.round(m)) : String(Math.round(m * 10) / 10); }
  function setState(cls){ box.className = box.className.replace(/\bst-(good|ok|bad|run)\b/g, '').trim() + (cls ? ' st-' + cls : ''); }
  function mark(mbps){
    Array.prototype.forEach.call(tiles, function(t){
      var need = +t.getAttribute('data-need');
      t.classList.toggle('pass', mbps != null && mbps >= need);
      t.classList.toggle('fail', mbps != null && mbps < need);
    });
  }
  function finish(mbps, ok){
    btn.disabled = false; btn.textContent = A('again'); bar.style.width = '100%';
    if(!ok){ setState('bad'); num.textContent = '—'; msg.textContent = A('error'); mark(null); return; }
    num.textContent = fmt(mbps);
    if(mbps >= 25){ setState('good'); msg.textContent = A('r4k'); }
    else if(mbps >= 10){ setState('ok'); msg.textContent = A('rhd'); }
    else if(mbps >= 5){ setState('ok'); msg.textContent = A('rsd'); }
    else { setState('bad'); msg.textContent = A('rslow'); }
    mark(mbps);
    if(tips) tips.hidden = mbps >= 25;
  }
  btn.addEventListener('click', function(){
    if(!window.fetch || !window.ReadableStream){ window.open('https://fast.com', '_blank', 'noopener'); return; }
    btn.disabled = true; btn.textContent = A('testing'); setState('run'); num.textContent = '0'; msg.textContent = A('wait'); bar.style.width = '0%'; mark(null);
    var ctrl = window.AbortController ? new AbortController() : null, bytes = 0, t0 = 0;
    var guard = setTimeout(function(){ if(ctrl) ctrl.abort(); }, LIMIT + 4000);
    function speedNow(){ var s = (performance.now() - t0) / 1000; return s > 0 ? bytes * 8 / s / 1e6 : 0; }
    fetch('https://speed.cloudflare.com/__down?bytes=' + BYTES, { cache: 'no-store', signal: ctrl ? ctrl.signal : undefined })
      .then(function(r){
        if(!r.ok || !r.body) throw new Error('bad');
        var reader = r.body.getReader(); t0 = performance.now();
        function pump(){
          return reader.read().then(function(x){
            var el = performance.now() - t0;
            if(x.done || el > LIMIT){ try{ reader.cancel(); }catch(e){} clearTimeout(guard); return finish(speedNow(), bytes > 200000); }
            bytes += x.value.length;
            num.textContent = fmt(speedNow());                                   /* live number while it runs */
            bar.style.width = Math.min(100, Math.max(el / LIMIT, bytes / BYTES) * 100) + '%';
            return pump();
          });
        }
        return pump();
      })['catch'](function(){ clearTimeout(guard); finish(t0 ? speedNow() : 0, t0 && bytes > 200000); });
  });
})();
