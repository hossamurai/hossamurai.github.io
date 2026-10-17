/* Hossam TV — private payment page (ES5 + WebCrypto). The details are encrypted in the page;
   the key is the part of the link after # (browsers never send it to the server).
   PBKDF2-SHA256 (slow on purpose) -> AES-GCM. A wrong or missing key shows "invalid link". */
(function(){
  var box = document.querySelector('[data-pk]');
  if(!box) return;
  var wait = document.querySelector('[data-pk-wait]'), bad = document.querySelector('[data-pk-bad]'), foot = document.querySelector('[data-pk-foot]');
  var key = decodeURIComponent((location.hash || '').replace(/^#(k=)?/, '')).trim();
  /* the language switch keeps the key */
  var lang = document.querySelector('.lang'); if(lang && key) lang.href = lang.href.split('#')[0] + '#' + key;
  var fail = function(){ wait.hidden = true; bad.hidden = false; };
  var C = window.crypto && window.crypto.subtle;
  if(!key || !C || !window.TextEncoder){ fail(); return; }
  var d; try{ d = JSON.parse(box.getAttribute('data-blob')); }catch(e){ fail(); return; }
  var bin = function(s){ var b = atob(s), a = new Uint8Array(b.length); for(var i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return a; };
  C.importKey('raw', new TextEncoder().encode(key), 'PBKDF2', false, ['deriveKey'])
    .then(function(k){ return C.deriveKey({ name: 'PBKDF2', salt: bin(d.salt), iterations: d.iter, hash: 'SHA-256' }, k, { name: 'AES-GCM', length: 256 }, false, ['decrypt']); })
    .then(function(k){ return C.decrypt({ name: 'AES-GCM', iv: bin(d.iv) }, k, bin(d.ct)); })
    .then(function(buf){
      box.innerHTML = new TextDecoder().decode(buf);
      box.removeAttribute('data-blob');
      wait.hidden = true;
      /* steps: where from -> which method -> that method's details; the phone's back button goes one step back */
      var MENUS = { region: 1, eg: 1, intl: 1, bank: 1 };
      var show = function(id){
        var found = false;
        Array.prototype.forEach.call(box.querySelectorAll('[data-step]'), function(s){ var on = s.getAttribute('data-step') === id; s.hidden = !on; found = found || on; });
        if(!found) return show('region');
        foot.hidden = !!MENUS[id];
        window.scrollTo(0, 0);
      };
      box.addEventListener('click', function(e){
        var b = e.target.closest ? e.target.closest('[data-go]') : null; if(!b) return;
        var id = b.getAttribute('data-go');
        if(b.classList.contains('pk-back') && history.state && history.state.pk){ history.back(); return; }
        try{ history.pushState({ pk: id }, '', location.href); }catch(err){}
        show(id);
      });
      window.addEventListener('popstate', function(e){ show(e.state && e.state.pk || 'region'); });
      show(history.state && history.state.pk || 'region');
    })['catch'](fail);
})();
