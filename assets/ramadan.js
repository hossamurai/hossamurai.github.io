/* Ramadan series page (xx/ramadan-series.html): poster, name and the day each series starts — fully automatic.
   The list comes from elCinema + Wikipedia (_source/matches/fetch_ramadan.py, every 6 hours) as assets/data/ramadan.json.
   Three sources, so it never fails: the site's copy of that file → the same file from the jsDelivr CDN →
   the list already written into the HTML. Posters: the series' poster, else a designed title card. */
(function(){
  var box = document.querySelector('[data-rm]'); if(!box) return;
  var Lb = {}; try{ Lb = JSON.parse(box.getAttribute('data-l')) || {}; }catch(e){}
  var ar = document.documentElement.lang === 'ar', loc = ar ? 'ar-EG' : 'en-US';
  var start = box.getAttribute('data-start'), end = box.getAttribute('data-end'), year = +box.getAttribute('data-year');
  var DAY = 864e5;

  function ymd(s){ var p = String(s || '').split('-'); return p.length === 3 ? Date.UTC(+p[0], +p[1] - 1, +p[2]) : NaN; }
  function todayUTC(){ var d = new Date(); return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()); }
  function el(tag, cls, txt){ var e = document.createElement(tag); if(cls) e.className = cls; if(txt != null) e.textContent = txt; return e; }
  function day(ms, withYear){ try{ var o = { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC' }; if(withYear) o.year = 'numeric'; return new Date(ms).toLocaleDateString(loc, o); }catch(e){ return ''; } }

  /* status: days to go / day N / ended */
  (function(){
    var s = box.querySelector('[data-rm-status]'), t = todayUTC(), a = ymd(start), b = ymd(end);
    var txt = t < a ? Lb.before.replace('{n}', Math.round((a - t) / DAY)).replace('{d}', day(a, true))
            : t <= b ? Lb.during.replace('{n}', Math.round((t - a) / DAY) + 1)
            : Lb.after.replace('{y}', year);
    if(s && txt) s.textContent = txt;
  })();

  function fill(list, items, first, badge){
    var t = todayUTC();
    list.textContent = '';
    items.forEach(function(x){
      if(!x || !(x.ar || x.en)) return;
      var main = ar ? (x.ar || x.en) : (x.en || x.ar), other = ar ? x.en : x.ar, key = x.ar || x.en;
      var li = el('li', 'rm-card'), hue = 0; for(var i = 0; i < key.length; i++) hue += key.charCodeAt(i);
      var pos = el('div', 'rm-poster rm-h' + (hue % 6)), gen = el('span', 'rm-gen');
      gen.setAttribute('aria-hidden', 'true'); gen.innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-moon"/></svg>';
      gen.appendChild(el('b', '', main)); pos.appendChild(gen);
      if(x.poster && /^https:\/\//.test(x.poster)){ var im = new Image(); im.alt = main; im.loading = 'lazy'; im.referrerPolicy = 'no-referrer'; im.onerror = function(){ this.remove(); }; im.src = x.poster; pos.appendChild(im); }
      var d = ymd(x.date); if(isNaN(d)) d = ymd(first);
      if(badge && t >= d && t < d + 3 * DAY){ li.className += ' rm-now'; pos.appendChild(el('i', 'rm-live', Lb.new)); }   /* "New" for its first 3 days */
      var info = el('div', 'rm-info');
      info.appendChild(el('b', 'rm-title', main));
      if(other && other !== main) info.appendChild(el('small', '', other));
      if(!isNaN(d)) info.appendChild(el('span', 'rm-t', day(d)));
      if(x.stars) info.appendChild(el('small', 'rm-stars', x.stars));
      li.appendChild(pos); li.appendChild(info); list.appendChild(li);
    });
  }

  function render(d){
    var cur = d.season && d.season.year === year ? d.season.series || [] : null;
    var last = d.last && d.last.year === year - 1 ? (d.last.series || []).slice(0, d.last.top || 48) : [];   /* the most popular */
    if(!cur) return false;                       /* a file for another year: keep what the page has */
    fill(box.querySelector('[data-rm-list="season"]'), cur, start, true);
    box.querySelector('[data-rm-empty]').hidden = cur.length > 0;
    var lb = box.querySelector('[data-rm-last]');
    fill(box.querySelector('[data-rm-list="last"]'), last, d.last && d.last.start, false);
    lb.hidden = !last.length || !(todayUTC() < ymd(start) || !cur.length);
    return true;
  }

  function getJSON(u, ok, fail){
    try{ fetch(u, { cache: 'no-store', credentials: 'omit' }).then(function(r){ return r.ok ? r.json() : null; })
      .then(function(d){ if(d && d.season) ok(d); else fail(); })['catch'](fail); }catch(e){ fail(); }
  }
  /* 1: the site's copy → 2: the CDN copy → 3: keep what's written in the HTML */
  getJSON(box.getAttribute('data-src'), render, function(){ getJSON(box.getAttribute('data-cdn'), render, function(){}); });
})();
