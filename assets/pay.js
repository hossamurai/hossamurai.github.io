/* Hossam TV — payment page (ES5). Payment methods for Egypt / Canada & rest of world (by the visitor's location), and
   "pay later": a day up to one week ahead, sent to the bot (n8n site-pay), which reminds the customer on WhatsApp that day.
   The bot's link carries the customer's key (#k=…), so the page greets them and needs no login; otherwise it asks for
   the username and password. */
(function(){
  'use strict';
  var box = document.querySelector('[data-pay]');
  if(!box) return;
  var AR = document.documentElement.lang === 'ar';
  var A = function(k){ return box.getAttribute('data-l-' + k) || ''; }, M = function(k){ return box.getAttribute('data-msg-' + k) || ''; };
  var each = function(sel, fn, root){ Array.prototype.forEach.call((root || document).querySelectorAll(sel), fn); };
  var api = box.getAttribute('data-api'), loc = box.getAttribute('data-locale');
  var form = box.querySelector('[data-py-form]'), date = form.querySelector('[name="date"]'), meth = form.querySelector('[name="method"]');
  var user = form.querySelector('[name="username"]'), pass = form.querySelector('[name="password"]'), msg = form.querySelector('.remind-msg');
  var key = (/[#&]k=([a-z0-9]{6,20})/i.exec(location.hash || '') || [])[1] || '';
  var who = null, region = 'intl', busy = false;
  var iso = function(d){ return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); };
  var day = function(s){ try{ return new Date(s + 'T12:00:00').toLocaleDateString(loc, { weekday: 'long', day: 'numeric', month: 'long' }); }catch(e){ return s; } };
  function setRange(min, max){ date.min = min; date.max = max; if(date.value && (date.value < min || date.value > max)) date.value = ''; }
  var t = new Date(); t.setDate(t.getDate() + 1); var tomorrow = iso(t); t.setDate(t.getDate() + 6);
  setRange(tomorrow, iso(t));

  /* region: the customer's (from the bot), the visitor's country (Cloudflare via site-data), the phone's time zone */
  function setRegion(r){
    region = r;
    each('[data-py-reg]', function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-py-reg') === r ? 'true' : 'false'); }, box);
    each('[data-py-list]', function(l){ l.hidden = l.getAttribute('data-py-list') !== r; }, box);
    var keep = meth.value;
    while(meth.options.length > 1) meth.remove(1);
    each('[data-py-list="' + r + '"] [data-pay-m]', function(a){ var o = document.createElement('option'); o.value = o.textContent = a.getAttribute('data-pay-m'); meth.appendChild(o); }, box);
    meth.value = keep; if(meth.value !== keep) meth.value = '';
  }
  var touched = false;
  each('[data-py-reg]', function(b){ b.addEventListener('click', function(){ touched = true; setRegion(b.getAttribute('data-py-reg')); }); }, box);
  var tz = ''; try{ tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; }catch(e){}
  setRegion(window.htvCountry === 'EG' || (!window.htvCountry && tz === 'Africa/Cairo') ? 'eg' : 'intl');
  document.addEventListener('htv:country', function(e){ if(!touched && !who) setRegion(e.detail === 'EG' ? 'eg' : 'intl'); });

  /* a method -> WhatsApp to Hossam with it filled in (and the username when known) */
  each('[data-pay-m]', function(a){
    a.addEventListener('click', function(){
      var text = A('wa').replace('{m}', a.getAttribute('data-pay-m')) + (who && who.username ? '\n' + A('user') + ': ' + who.username : '');
      a.href = 'https://wa.me/' + box.getAttribute('data-wa') + '?text=' + encodeURIComponent(text);
    });
  }, box);

  function post(data){
    var body = new URLSearchParams(); body.append('p', JSON.stringify(data));
    return fetch(api, { method: 'POST', body: body, credentials: 'omit' }).then(function(r){ return r.json()['catch'](function(){ return {}; }); });
  }
  function say(k, ok, d){ msg.textContent = M(k).replace('{d}', d || ''); msg.className = 'remind-msg' + (ok ? ' ok' : ' err'); msg.hidden = false; }
  function greet(d){
    who = d;
    var w = box.querySelector('[data-py-who]'); w.textContent = '';
    var h = document.createElement('b'); h.textContent = A('hi').replace('{n}', d.name || '').replace(/\s+$/, ''); w.appendChild(h);
    if(d.amount){ var s = document.createElement('span'); s.textContent = A('due').replace('{a}', d.amount); w.appendChild(s); }
    if(d.promised){ var p = document.createElement('span'); p.textContent = A('planned').replace('{d}', day(d.promised)); w.appendChild(p); }
    w.hidden = false;
    if(d.region) setRegion(d.region);
    if(d.min && d.max) setRange(d.min, d.max);
    each('[data-py-login]', function(x){ x.hidden = true; }, form);
  }
  if(key && window.fetch && window.URLSearchParams){
    post({ action: 'info', k: key, lang: AR ? 'ar' : 'en' }).then(function(d){ if(d && d.ok && d.status === 'found') greet(d); })['catch'](function(){});
  }

  form.addEventListener('submit', function(e){
    e.preventDefault();
    if(busy) return;
    var hp = form.querySelector('[name="website"]');
    if(!who && (!user.value.trim() || !pass.value)){ say('login'); (user.value.trim() ? pass : user).focus(); return; }
    if(!date.value){ say('empty'); date.focus(); return; }
    if(date.value < date.min || date.value > date.max){ say('bad_day', false, day(date.max)); date.focus(); return; }
    if(!window.fetch || !window.URLSearchParams){ say('error'); return; }
    busy = true; var btn = form.querySelector('button[type="submit"]'); btn.disabled = true;
    post({ action: 'later', k: who ? key : '', username: who ? '' : user.value.trim(), password: who ? '' : pass.value, date: date.value, method: meth.value, lang: AR ? 'ar' : 'en', website: hp ? hp.value : '' })
      .then(function(d){
        var st = d && d.status;
        if(d && d.ok && st === 'saved'){ say('saved', true, day(d.promised || date.value)); if(!who) greet(d); else { who.promised = d.promised; greet(who); } }
        else if(st === 'bad_day'){ if(d.min && d.max) setRange(d.min, d.max); say('bad_day', false, day(d.max || date.max)); }
        else if(st && M(st)){ say(st); }
        else say('error');
      })['catch'](function(){ say('error'); })
      .then(function(){ busy = false; btn.disabled = false; });
  });
})();
