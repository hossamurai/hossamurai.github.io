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
      wait.hidden = true; foot.hidden = false;
    })['catch'](fail);
})();
