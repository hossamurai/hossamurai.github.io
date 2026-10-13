/* Ramadan series page (xx/ramadan-series.html): poster, name and the day each series starts.
   Three sources, so the list never fails:
   1. live — the admin bot's "Ramadan series | …" knowledge through n8n site-data (assets/bot.js fires "htv:series";
      if it hasn't arrived after 6 s this script asks n8n itself once more), so a change in the bot shows on the next visit;
   2. assets/data/bot.json — the last good copy, saved by the "Update matches" Action every 6 hours;
   3. the list written into the HTML at build time (also what search engines read).
   A source only replaces the list when the one above it hasn't answered.
   Posters: the admin's link, else the series' poster found on Wikipedia (bot.json "posters"), else a designed title card. */
(function(){
  var box = document.querySelector('[data-rm]'); if(!box) return;
  function attr(n, d){ try{ return JSON.parse(box.getAttribute(n)) || d; }catch(e){ return d; } }
  var Lb = attr('data-l', {}), series = attr('data-series', []), posters = attr('data-posters', {});
  var ar = document.documentElement.lang === 'ar', loc = ar ? 'ar-EG' : 'en-US';
  var start = box.getAttribute('data-start'), end = box.getAttribute('data-end'), year = box.getAttribute('data-year');
  var list = box.querySelector('[data-rm-list]'), empty = box.querySelector('[data-rm-empty]');
  var DAY = 864e5;

  function ymd(s){ var p = String(s || '').split('-'); return p.length === 3 ? Date.UTC(+p[0], +p[1] - 1, +p[2]) : NaN; }
  function todayUTC(){ var d = new Date(); return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()); }
  function el(tag, cls, txt){ var e = document.createElement(tag); if(cls) e.className = cls; if(txt != null) e.textContent = txt; return e; }
  function day(ms, year){ try{ var o = { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC' }; if(year) o.year = 'numeric'; return new Date(ms).toLocaleDateString(loc, o); }catch(e){ return ''; } }

  /* status: days to go / day N / ended */
  (function(){
    var s = box.querySelector('[data-rm-status]'), t = todayUTC(), a = ymd(start), b = ymd(end);
    var txt = t < a ? Lb.before.replace('{n}', Math.round((a - t) / DAY)).replace('{d}', day(a, true))
            : t <= b ? Lb.during.replace('{n}', Math.round((t - a) / DAY) + 1)
            : Lb.after.replace('{y}', year);
    if(s && txt) s.textContent = txt;
  })();

  function when(x){ var d = ymd(x.date); return isNaN(d) ? ymd(start) : d; }

  function render(){
    var items = series.filter(function(x){ return x && (x.ar || x.en); }).sort(function(a, b){
      return when(a) - when(b) || String(a.ar || a.en).localeCompare(String(b.ar || b.en));
    });
    list.textContent = '';
    var t = todayUTC();
    items.forEach(function(x){
      var main = ar ? (x.ar || x.en) : (x.en || x.ar), other = ar ? x.en : x.ar, key = x.ar || x.en;
      var li = el('li', 'rm-card'), hue = 0; for(var i = 0; i < key.length; i++) hue += key.charCodeAt(i);
      var pos = el('div', 'rm-poster rm-h' + (hue % 6)), gen = el('span', 'rm-gen');
      gen.setAttribute('aria-hidden', 'true'); gen.innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-moon"/></svg>';
      gen.appendChild(el('b', '', main)); pos.appendChild(gen);
      var src = x.poster || posters[key];
      if(src && /^https:\/\//.test(src)){ var im = new Image(); im.alt = main; im.loading = 'lazy'; im.referrerPolicy = 'no-referrer'; im.onerror = function(){ this.remove(); }; im.src = src; pos.appendChild(im); }
      var d = when(x);
      if(t >= d && t < d + 3 * DAY){ li.className += ' rm-now'; pos.appendChild(el('i', 'rm-live', Lb.new)); }   /* "New" for its first 3 days */
      var info = el('div', 'rm-info');
      info.appendChild(el('b', 'rm-title', main));
      if(other && other !== main) info.appendChild(el('small', '', other));
      info.appendChild(el('span', 'rm-t', day(d)));
      if(x.stars) info.appendChild(el('small', 'rm-stars', x.stars));
      li.appendChild(pos); li.appendChild(info); list.appendChild(li);
    });
    empty.hidden = items.length > 0;
  }

  render();                                                   /* 3: the copy in the HTML */
  var gotLive = false;
  function live(d){ if(Array.isArray(d)){ gotLive = true; series = d; render(); } }
  if(window.htvSeries) live(window.htvSeries);
  document.addEventListener('htv:series', function(e){ live(e.detail); });
  function getJSON(u, ok){ try{ fetch(u, { cache: 'no-store', credentials: 'omit' }).then(function(r){ return r.ok ? r.json() : null; }).then(function(d){ if(d) ok(d); })['catch'](function(){}); }catch(e){} }
  /* 2: the saved copy (and the Wikipedia posters) — its series only while the live list hasn't come */
  getJSON(box.getAttribute('data-src'), function(d){
    if(d.posters) posters = d.posters;
    if(!gotLive && Array.isArray(d.series) && d.series.length) series = d.series;
    render();
  });
  /* 1 again: n8n didn't answer bot.js in time -> one more try */
  setTimeout(function(){ if(!gotLive) getJSON('https://n8n.hossamservices.com/webhook/site-data', function(d){ live(d.series); }); }, 6000);
})();
