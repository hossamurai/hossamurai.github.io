/* Ramadan series page (xx/ramadan-series.html).
   Three sources, so the list never fails:
   1. live — the admin bot's "Ramadan series | …" knowledge through n8n site-data (assets/bot.js fires "htv:series";
      if it hasn't arrived after 6 s this script asks n8n itself once more), so a time changed in the bot shows on the next visit;
   2. assets/data/bot.json — the last good copy, saved by the "Update matches" Action every 6 hours;
   3. the list written into the HTML at build time (also what search engines read).
   A source only replaces the list when the one above it hasn't answered.
   Each time is shown in the visitor's own time zone, with the channel's time (Cairo / KSA / UAE) under it. */
(function(){
  var box = document.querySelector('[data-rm]'); if(!box) return;
  function attr(n, d){ try{ return JSON.parse(box.getAttribute(n)) || d; }catch(e){ return d; } }
  var Lb = attr('data-l', {}), ZONES = attr('data-zones', {}), series = attr('data-series', []), posters = attr('data-posters', {});
  var ar = document.documentElement.lang === 'ar', loc = ar ? 'ar-EG' : 'en-US';
  var start = box.getAttribute('data-start'), end = box.getAttribute('data-end'), year = box.getAttribute('data-year');
  var list = box.querySelector('[data-rm-list]'), empty = box.querySelector('[data-rm-empty]'), chs = box.querySelector('[data-rm-chs]');
  var DAY = 864e5, pick = '';

  function ymd(s){ var p = s.split('-'); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }
  function todayUTC(){ var d = new Date(); return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()); }
  function el(tag, cls, txt){ var e = document.createElement(tag); if(cls) e.className = cls; if(txt != null) e.textContent = txt; return e; }

  /* status: days to go / day N / ended */
  (function(){
    var s = box.querySelector('[data-rm-status]'), t = todayUTC(), a = ymd(start), b = ymd(end);
    var txt = t < a ? Lb.before.replace('{n}', Math.round((a - t) / DAY)).replace('{d}', new Date(a).toLocaleDateString(loc, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }))
            : t <= b ? Lb.during.replace('{n}', Math.round((t - a) / DAY) + 1)
            : Lb.after.replace('{y}', year);
    if(s && txt) s.textContent = txt;
  })();

  /* "21:00" in zone "Cairo" -> that moment on the day shown (today during Ramadan, else the first day) */
  function instant(hm, zone){
    var m = /^(\d{1,2}):(\d{2})$/.exec(hm || ''); if(!m) return null;
    var t = todayUTC(), a = ymd(start), b = ymd(end), day = t >= a && t <= b ? t : a, off = ZONES[zone] != null ? ZONES[zone] : 2;
    return day + ((+m[1] - off) * 60 + +m[2]) * 6e4;
  }
  function fmt(ms, tz){ var o = { hour: 'numeric', minute: '2-digit' }; if(tz) o.timeZone = tz; try{ return new Date(ms).toLocaleTimeString(loc, o); }catch(e){ return ''; } }
  function chName(ch){ var p = String(ch || '').split(' / '); return ar && p[1] ? p[1].trim() : p[0].trim(); }
  function order(x){ var k = instant(x.time, x.zone); if(k == null) return 1e9; var cm = ((k / 6e4 + 120) % 1440 + 1440) % 1440; return (cm - 360 + 1440) % 1440; }

  function render(){
    var items = series.filter(function(x){ return x && (x.ar || x.en); }).sort(function(a, b){ return order(a) - order(b); });
    var names = [];
    items.forEach(function(x){ var c = chName(x.ch); if(c && names.indexOf(c) < 0) names.push(c); });
    if(pick && names.indexOf(pick) < 0) pick = '';
    /* channel filter (only when there is more than one channel) */
    chs.textContent = ''; chs.hidden = names.length < 2;
    if(names.length > 1) [''].concat(names).forEach(function(n){
      var b = el('button', 'tb-tab' + (n === pick ? ' on' : ''), n || Lb.all); b.type = 'button';
      b.setAttribute('aria-pressed', n === pick ? 'true' : 'false');
      b.addEventListener('click', function(){ pick = n; render(); }); chs.appendChild(b);
    });
    list.textContent = '';
    var now = Date.now(), t = todayUTC(), during = t >= ymd(start) && t <= ymd(end), shown = 0;
    items.forEach(function(x){
      var c = chName(x.ch); if(pick && c !== pick) return;
      var main = ar ? (x.ar || x.en) : (x.en || x.ar), other = ar ? x.en : x.ar, key = x.ar || x.en;
      var li = el('li', 'rm-card'), hue = 0; for(var i = 0; i < key.length; i++) hue += key.charCodeAt(i);
      /* poster: the admin's link, else the one found on Wikipedia, else the designed title card underneath */
      var pos = el('div', 'rm-poster rm-h' + (hue % 6)), gen = el('span', 'rm-gen');
      gen.setAttribute('aria-hidden', 'true'); gen.innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-moon"/></svg>';
      gen.appendChild(el('b', '', main)); pos.appendChild(gen);
      var src = x.poster || posters[key];
      if(src && /^https:\/\//.test(src)){ var im = new Image(); im.alt = main; im.loading = 'lazy'; im.referrerPolicy = 'no-referrer'; im.onerror = function(){ this.remove(); }; im.src = src; pos.appendChild(im); }
      if(c) pos.appendChild(el('span', 'rm-chip', c));
      var info = el('div', 'rm-info');
      info.appendChild(el('b', 'rm-title', main));
      if(other && other !== main) info.appendChild(el('small', '', other));
      var k = instant(x.time, x.zone), off = ZONES[x.zone] != null ? ZONES[x.zone] : 2, tz = 'Etc/GMT' + (off > 0 ? '-' : '+') + Math.abs(off);
      var same = k != null && -new Date(k).getTimezoneOffset() === off * 60;
      var tt = el('span', 'rm-t', k == null ? Lb.soon : fmt(k)); if(k != null && !same) tt.appendChild(el('em', '', Lb.mine)); info.appendChild(tt);
      if(k != null && !same) info.appendChild(el('small', '', fmt(k, tz) + ' ' + (Lb.zn[x.zone] || Lb.zn.Cairo)));
      var r = instant(x.rerun, x.zone); if(r != null) info.appendChild(el('small', '', Lb.rerun + ' ' + fmt(r)));
      if(x.stars) info.appendChild(el('small', 'rm-stars', x.stars));
      if(during && k != null && [k - DAY, k].some(function(s){ return now >= s && now < s + 50 * 6e4; })){ li.className += ' rm-now'; pos.appendChild(el('i', 'rm-live', Lb.now)); }
      li.appendChild(pos); li.appendChild(info); list.appendChild(li); shown++;
    });
    empty.hidden = shown > 0;
  }

  render();                                                   /* 3: the copy in the HTML */
  var gotLive = false;
  function live(d){ if(Array.isArray(d)){ gotLive = true; series = d; render(); } }
  if(window.htvSeries) live(window.htvSeries);
  document.addEventListener('htv:series', function(e){ live(e.detail); });
  function getJSON(u, ok){ try{ fetch(u, { cache: 'no-store', credentials: 'omit' }).then(function(r){ return r.ok ? r.json() : null; }).then(function(d){ if(d) ok(d); })['catch'](function(){}); }catch(e){} }
  /* 2: the saved copy — only while the live list hasn't come */
  getJSON(box.getAttribute('data-src'), function(d){
    if(d.posters) posters = d.posters;
    if(!gotLive && Array.isArray(d.series) && d.series.length) series = d.series;
    render();
  });
  /* 1 again: n8n didn't answer bot.js in time -> one more try */
  setTimeout(function(){ if(!gotLive) getJSON('https://n8n.hossamservices.com/webhook/site-data', function(d){ live(d.series); }); }, 6000);
})();
