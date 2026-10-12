/* Hossam TV — league tables on the matches page (ES5).
   Data: assets/data/standings.json, refreshed every 6 hours by the "Update matches" GitHub Action. */
(function(){
  'use strict';
  var box = document.querySelector('[data-standings]');
  if(!box || !window.fetch) return;
  var ar = document.documentElement.lang === 'ar', KEY = 'htv-table';
  var tabs = box.querySelector('[data-st-tabs]'), body = box.querySelector('[data-st-body]'), leagues = [];
  function el(tag, cls, text){ var e = document.createElement(tag); if(cls) e.className = cls; if(text != null) e.textContent = text; return e; }
  function show(id){
    var lg = leagues.filter(function(l){ return l.id === id; })[0] || leagues[0];
    Array.prototype.forEach.call(tabs.children, function(b){ b.setAttribute('aria-selected', b.getAttribute('data-id') === lg.id ? 'true' : 'false'); });
    while(body.firstChild) body.removeChild(body.firstChild);
    lg.rows.forEach(function(r){
      var tr = el('tr'), td = el('td', 'tb-team'), team = el('div', 'tb-tm'); td.appendChild(team);
      tr.appendChild(el('td', 'tb-rank', String(r.rank)));
      if(r.logo){
        var img = el('img'); img.src = r.logo; img.alt = ''; img.width = 22; img.height = 22; img.loading = 'lazy';
        img.onerror = function(){ this.style.visibility = 'hidden'; };
        team.appendChild(img);
      }
      team.appendChild(el('span', null, ar ? r.ar : r.en));
      tr.appendChild(td);
      tr.appendChild(el('td', 'tb-num', String(r.p)));
      var gd = el('td', 'tb-num'); gd.dir = 'ltr'; gd.textContent = r.gd; tr.appendChild(gd);
      tr.appendChild(el('td', 'tb-pts', String(r.pts)));
      body.appendChild(tr);
    });
    try{ localStorage.setItem(KEY, lg.id); }catch(e){}
  }
  fetch(box.getAttribute('data-src'), { cache: 'no-cache' })
    .then(function(r){ return r.ok ? r.json() : null; })
    .then(function(d){
      leagues = ((d && d.leagues) || []).filter(function(l){ return l.rows && l.rows.length; });
      if(!leagues.length) return;
      leagues.forEach(function(l){
        var b = el('button', 'tb-tab', ar ? l.name.ar : l.name.en);
        b.type = 'button'; b.setAttribute('role', 'tab'); b.setAttribute('data-id', l.id);
        b.addEventListener('click', function(){ show(l.id); });
        tabs.appendChild(b);
      });
      var saved = null; try{ saved = localStorage.getItem(KEY); }catch(e){}
      show(saved || leagues[0].id);
      box.hidden = false;
    })['catch'](function(){});
})();
