(function(){
  "use strict";
  var MAIN = '201117250227';

  /* =====================================================================
     LIVE DATA — hosts and outages come from the WhatsApp bot's knowledge
     (n8n workflow "Website Data API"). Needs n8n on HTTPS.
     If it can't be reached, the page uses FALLBACK_HOSTS below.
     ===================================================================== */
  var SITE_DATA_URL = 'https://n8n.hossamservices.com/webhook/site-data';
  var FALLBACK_HOSTS = {
    basic:   ['http://cf.hossamtv.site', 'http://pro.hossamtv.site'],
    premium: ['http://cf.hossam8k.site', 'http://pro.hossam8k.site'],
    xtv:     ['http://smartott.org:80', 'http://rfcot.com:80', 'http://vireexaa.com:80'],
    marvel:  ['http://fgt123.eu', 'http://mar22.sbs', 'http://mar10.sbs']
  };
  var live = { hosts: null, outages: [] };
  function getHosts(plan){ return (live.hosts && live.hosts[plan] && live.hosts[plan].length) ? live.hosts[plan] : (FALLBACK_HOSTS[plan] || []); }
  function loadLive(){
    if(!window.fetch || !SITE_DATA_URL) return;
    var ctrl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function(){ if(ctrl) ctrl.abort(); }, 4000);
    fetch(SITE_DATA_URL, ctrl ? {signal: ctrl.signal} : {})
      .then(function(r){ return r.ok ? r.json() : null; })
      .then(function(d){
        clearTimeout(timer);
        if(!d) return;
        if(d.hosts && typeof d.hosts === 'object') live.hosts = d.hosts;
        if(Array.isArray(d.outages)) live.outages = d.outages;
        if(d.channels){ window.htvChannels = d.channels; try{ document.dispatchEvent(new CustomEvent('htv:channels', { detail: d.channels })); }catch(e){} }
        if(d.prices){ PLANS.forEach(function(p){ var v = d.prices[p.id]; if(v && v.y1){ p.price.en = p.price.en.replace(/\d[\d,.]*/, v.y1); p.price.ar = p.price.ar.replace(/\d[\d,.]*/, v.y1); } }); renderPlans(); }
        if(d.ratings && d.ratings.count >= 5 && d.ratings.avg){ var rb = document.getElementById('ratingBadge'); if(rb){ rb.innerHTML = '<span class="star" aria-hidden="true">★</span><span class="en">Rated ' + d.ratings.avg + '/5 by ' + d.ratings.count + ' customers on WhatsApp</span><span class="ar">تقييم العملاء ' + d.ratings.avg + '/5 (' + d.ratings.count + ' تقييم على واتساب)</span>'; rb.hidden = false; } }
        renderAlerts();
        var ae = document.activeElement && document.activeElement.id || '';
        if(state.flow.length && !state.done && ae.indexOf('m3u') !== 0) renderFlow();
      })['catch'](function(){});
  }
  var doc = document.documentElement;
  function store(k, v){ try{ if(v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); }catch(e){ return null; } }
  function lang(){ return doc.lang === 'ar' ? 'ar' : 'en'; }
  function t(o){ return typeof o === 'string' ? o : (o[lang()] || o.en); }
  function icon(id){ return '<svg class="ic"><use href="#i-' + id + '"/></svg>'; }
  function esc(v){ return String(v == null ? '' : v).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function wa(num, text){ return 'https://wa.me/' + num + '?text=' + encodeURIComponent(text); }
  function copyBtn(v){ return '<button type="button" class="code" data-copy="' + esc(v) + '">' + esc(v) + icon('copy') + '</button>'; }
  function ext(url, label){ return '<a href="' + url + '" target="_blank" rel="noopener">' + (label || url.replace(/^https?:\/\//, '')) + '</a>'; }

  /* ------------------------------------------------ DATA ------------------------------------------------ */
  var PLANS = [
    {id:'basic',   color:'var(--c-basic)',   name:{en:'Basic', ar:'الأساسية'}, aka:'Neo 4K',    price:{en:'$35 / year', ar:'35 دولار / سنة'}},
    {id:'premium', color:'var(--c-premium)', name:{en:'Premium', ar:'بريميوم'}, aka:'Strong 4K', price:{en:'$55 / year', ar:'55 دولار / سنة'}},
    {id:'xtv',     color:'var(--c-xtv)',     name:{en:'XTV (X server)', ar:'سيرفر XTV (اكس)'}, aka:null, price:{en:'400 EGP / year', ar:'400 جنيه / سنة'}},
    {id:'marvel',  color:'var(--c-marvel)',  name:{en:'Marvel', ar:'سيرفر مارفل'}, aka:null, price:{en:'400 EGP / year', ar:'400 جنيه / سنة'}}
  ];
  var APPS = [
    {id:'4kpro',   name:'4K Pro',   cat:'plan', plans:['basic'],   fix:true},
    {id:'4kprime', name:'4K Prime', cat:'plan', plans:['basic']},
    {id:'4kxca',   name:'4K XCA',   cat:'plan', plans:['basic']},
    {id:'8kvip',   name:'8K VIP',   cat:'plan', plans:['premium'], fix:true},
    {id:'8kplus',  name:'8K Plus',  cat:'plan', plans:['premium']},
    {id:'8kprime', name:'8K Prime', cat:'plan', plans:['premium']},
    {id:'xtvapp',  name:'XTV app',  cat:'plan', plans:['xtv']},
    {id:'marvelapp', name:'Marvel app', cat:'plan', plans:['marvel']},
    {id:'smarters',  name:'IPTV Smarters', sub:{en:'Android TV / Firestick / phone', ar:'أندرويد / فايرستيك / موبايل'}, cat:'manual'},
    {id:'lite',      name:'Smarters Player Lite', sub:{en:'iPhone / Apple TV / Mac', ar:'آيفون / أبل تي في / ماك'}, cat:'manual'},
    {id:'xciptv',    name:'XCIPTV', cat:'manual'},
    {id:'televizo',  name:'Televizo', cat:'manual'},
    {id:'tivimate',  name:'TiviMate', cat:'manual'},
    {id:'sfvip',     name:'SFVIP Player', sub:{en:'Windows', ar:'ويندوز'}, cat:'manual'},
    {id:'bob',   name:'Bob Player',  sub:{en:'Samsung / LG', ar:'سامسونج / LG'}, cat:'managed', site:'https://www.bobplayer.com/login'},
    {id:'ibo',   name:'IBO Player',  sub:{en:'Samsung / LG', ar:'سامسونج / LG'}, cat:'managed', site:'https://iboplayer.com/device/login'},
    {id:'iboxp', name:'IBO XPlayer', cat:'managed', site:'https://iboxiptvplayer.com/device/login'},
    {id:'web',   name:'my.splayer.in', sub:{en:'Web browser', ar:'المتصفح'}, cat:'web', plans:['xtv','marvel']}
  ];
  var GROUPS = [
    {cat:'plan', title:{en:'Official app for your plan', ar:'التطبيق الرسمي لباقتك'}},
    {cat:'manual', title:{en:'Other players (username + password + host)', ar:'مشغلات أخرى (اسم مستخدم + باسورد + هوست)'}},
    {cat:'managed', title:{en:'Smart TV players (Device ID + Key)', ar:'تطبيقات الشاشات (Device ID + Key)'}},
    {cat:'web', title:{en:'In the browser', ar:'من المتصفح'}}
  ];
  var SYMPTOMS = [
    {id:'all',    t:{en:'Nothing works', ar:'مفيش حاجة شغالة'}, s:{en:'Nothing loads or plays', ar:'مفيش حاجة بتحمل أو بتشتغل'}},
    {id:'one',    t:{en:'Only one channel or movie', ar:'قناة أو فيلم واحد بس'}, s:{en:'Everything else works', ar:'والباقي شغال'}},
    {id:'freeze', t:{en:'Freezing / buffering', ar:'تقطيع / تحميل'}, s:{en:'Plays but keeps stopping', ar:'بيشتغل بس بيقف'}},
    {id:'login',  t:{en:"Can't log in / error", ar:'مش قادر أسجل دخول / رسالة خطأ'}, s:{en:'Authentication, expired…', ar:'Authentication أو انتهاء…'}},
    {id:'open',   t:{en:"App won't open", ar:'التطبيق مش بيفتح'}, s:{en:'Crashes or stuck on start', ar:'بيقفل أو واقف على البداية'}},
    {id:'host',   t:{en:'Empty list / need new host', ar:'القائمة فاضية / محتاج هوست جديد'}, s:{en:'0 channels, playlist empty', ar:'0 قنوات أو القائمة فاضية'}},
    {id:'k4',     t:{en:'Only 4K doesn\'t work', ar:'الـ 4K بس اللي مش شغال'}, s:{en:'Black screen on 4K', ar:'شاشة سودا على الـ 4K'}},
    {id:'av',     t:{en:'Sound or picture problem', ar:'مشكلة في الصوت أو الصورة'}, s:{en:'Sound but no picture…', ar:'صوت من غير صورة…'}},
    {id:'epg',    t:{en:'TV guide wrong or empty', ar:'دليل البرامج غلط أو فاضي'}, s:{en:'EPG times', ar:'مواعيد الـ EPG'}}
  ];

  /* ------------------------------------------------ STEPS ------------------------------------------------ */
  function hostsHTML(){
    var H = getHosts(state.plan);
    if(!H.length) return '<p>' + (lang()==='ar' ? 'اطلب الهوست من حسام على الواتساب.' : 'Ask Hossam for the host on WhatsApp.') + '</p>';
    return '<div class="host-list">' + H.map(function(h, i){
      return '<div>' + copyBtn(h) + (i === 0 ? '<small>' + (lang()==='ar' ? 'الأساسي' : 'main') + '</small>' : '<small>' + (lang()==='ar' ? 'احتياطي' : 'backup') + '</small>') + '</div>';
    }).join('') + '</div>';
  }
  function planName(){ var p = PLANS.filter(function(x){ return x.id === state.plan; })[0]; return p ? t(p.name) : ''; }
  function appObj(){ return APPS.filter(function(x){ return x.id === state.app; })[0]; }

  var NEVER_DELETE = {en:'⚠️ Never delete the app or reset the TV — the paid activation is lost and you would have to pay again.', ar:'⚠️ متمسحش التطبيق ومتعملش ريست للشاشة — التفعيل المدفوع هيضيع وهتدفع تاني.'};
  var NEVER_REINSTALL = {en:'⚠️ Don\'t uninstall or reinstall the app — some apps can\'t be downloaded again.', ar:'⚠️ متمسحش التطبيق ومتنزلوش تاني — بعض التطبيقات مش بتتنزل تاني.'};

  var STEPS = {
    magic: {t:{en:'Do the "magic trick"', ar:'اعمل "الحل السحري"'}, b:function(ar){ return ar
      ? '<ol><li>افصل الراوتر والتلفزيون/الجهاز من الكهرباء.</li><li>استنى 10 ثواني.</li><li>وصّلهم تاني واستنى الإنترنت يرجع.</li><li>افتح التطبيق وجرّب.</li></ol>'
      : '<ol><li>Unplug the router and the TV/device from power.</li><li>Wait 10 seconds.</li><li>Plug them back in and wait for the internet to come back.</li><li>Open the app and try again.</li></ol>'; }},
    inuse: {t:{en:'Make sure nobody else is watching', ar:'اتأكد إن مفيش حد تاني بيتفرج'}, b:function(ar){ return ar
      ? 'الاشتراك بيشتغل على جهاز واحد بس في نفس الوقت.<ul><li>اقفل التطبيق على أي جهاز تاني.</li><li>على أجهزة الأندرويد: Settings ← Apps ← التطبيق ← Force stop.</li><li>استنى 5–10 دقايق وجرّب تاني. (نفس الحل لو الكهرباء قطعت أو قفلت التطبيق من غير ما توقف الفيديو.)</li></ul>'
      : 'Only one device can watch at a time.<ul><li>Close the app on any other device.</li><li>Android devices: Settings → Apps → the app → Force stop.</li><li>Wait 5–10 minutes and try again. (Same fix after a power cut, or if you left the app without stopping the video.)</li></ul>'; }},
    elsewhere: {t:{en:'Try another device and mobile data', ar:'جرّب جهاز تاني وداتا الموبايل'}, b:function(ar){ return ar
      ? '<ul><li><b>اشتغل على جهاز تاني أو على داتا الموبايل؟</b> يبقى المشكلة في الجهاز أو إنترنت البيت — كمّل الخطوات.</li><li><b>مش شغال في أي مكان؟</b> شوف تاريخ انتهاء اشتراكك في الصورة اللي حسام بعتهالك على الواتساب، وشوف حالة الواتساب الأساسي لو في عطل.</li></ul>'
      : '<ul><li><b>Works on another device or on mobile data?</b> Then your device or home internet is the cause — continue.</li><li><b>Fails everywhere?</b> Check your expiry date in the picture Hossam sent you on WhatsApp, and check the main WhatsApp Status for outage news.</li></ul>'; }},
    speed: {t:{en:'Check your internet speed', ar:'اختبر سرعة الإنترنت'}, b:function(ar){ var st = (ar ? 'ar' : 'en') + '/speed-test.html'; return ar
      ? '<a class="speed-link" href="' + st + '" target="_blank" rel="noopener"><span class="speed-link-ic" aria-hidden="true">⚡</span><span><b>افتح اختبار السرعة</b><small>اعمله على التلفزيون نفسه، أو على موبايل جنبه على نفس الواي فاي.</small></span><span class="speed-link-go" aria-hidden="true">→</span></a><ul><li>5 ميجا لـ SD، و10 لـ HD، و25+ للـ 4K.</li><li>ضعيفة؟ قرّب الراوتر، استخدم كابل لو ينفع، ووقف أي تحميلات تانية.</li></ul>'
      : '<a class="speed-link" href="' + st + '" target="_blank" rel="noopener"><span class="speed-link-ic" aria-hidden="true">⚡</span><span><b>Open our speed test</b><small>Run it on the TV itself, or on a phone right next to it on the same Wi-Fi.</small></span><span class="speed-link-go" aria-hidden="true">→</span></a><ul><li>5 Mbps for SD, 10 for HD, 25+ for 4K.</li><li>Too slow? Move the router closer, use a cable if you can, and stop other downloads.</li></ul>'; }},
    wedns: {t:{en:'In Egypt on WE internet?', ar:'في مصر وعلى إنترنت WE؟'}, b:function(ar){ return ar
      ? 'لو شغال على داتا الموبايل ومش شغال على WE، ممكن WE غيّرت الـ DNS بعد تجديد الباقة:<ol><li>غيّر الـ DNS في الراوتر إلى 8.8.8.8 و 8.8.4.4.</li><li>اعمل ريستارت للراوتر من الفيشة.</li><li>مش عارف؟ كلّم خدمة عملاء WE واطلب منهم يغيروها — ولو سألوا ليه قول: "المسؤول الفني طلب مني كده".</li></ol>مش على WE؟ اضغط "الخطوة اللي بعدها".'
      : 'If it works on mobile data but not on WE, WE may have changed your router DNS after renewing your plan:<ol><li>Set the router DNS to 8.8.8.8 and 8.8.4.4.</li><li>Restart the router from the power plug.</li><li>Can\'t do it? Call WE customer service and ask them to set it — if they ask why, say "the technical support asked me to".</li></ol>Not on WE? Tap "next step".'; }},
    lower: {t:{en:'Check your login details', ar:'راجع بيانات الدخول'}, b:function(ar){ return ar
      ? '<ul><li>اسم المستخدم والباسورد <b>حروف صغيرة كلها</b> ومن غير مسافات.</li><li>على أندرويد/فايرستيك: Settings ← Date & time ← خليها <b>تلقائي</b> (الساعة الغلط بتمنع الدخول).</li></ul>'
      : '<ul><li>Username and password are <b>all lowercase</b>, with no spaces.</li><li>Android/Firestick: Settings → Date & time → set to <b>automatic</b> (a wrong clock blocks logins).</li></ul>'; }},
    hosts: {t:{en:'Switch to another host', ar:'غيّر الهوست'}, b:function(ar){ return (ar
      ? 'نفس اسم المستخدم والباسورد شغالين على كل هوستات باقة ' + esc(planName()) + '. جرّب اللي بعده:'
      : 'The same username and password work on every ' + esc(planName()) + ' host. Try the next one:') + hostsHTML()
      + '<p style="margin-top:10px">' + (ar ? 'كلهم مش شغالين؟ غالباً الهوست محجوب — كمّل.' : 'None work? The host is probably blocked — continue.') + '</p>'; }},
    playlistfix: {t:{en:'Fix the playlist in the app', ar:'صلّح الـ Playlist في التطبيق'}, b:function(ar){ return ar
      ? '<ol><li>من الشاشة الرئيسية افتح <b>Playlists</b>.</li><li>هتلاقي 2: واحدة متصلة وواحدة لأ.</li><li>اضغط <b>Edit</b> على اللي مش متصلة.</li><li>راجع اسم المستخدم والباسورد (حروف صغيرة).</li><li>اضغط <b>Update</b> ثم اتصل بيها.</li></ol>'
      : '<ol><li>On the main screen open <b>Playlists</b>.</li><li>You\'ll see 2 — one connected, one not.</li><li>Click <b>Edit</b> on the one that is not connected.</li><li>Check the username and password (lowercase).</li><li>Click <b>Update</b>, then connect to it.</li></ol>'; }},
    officialwait: {t:{en:'Use a free app while the official one updates', ar:'استخدم تطبيق مجاني لحد ما الرسمي يتحدث'}, b:function(ar){ return (ar
      ? 'التطبيقات الرسمية بتحدّث السيرفر لوحدها، بس ممكن تاخد وقت. لو مش قادر تستنى، استخدم تطبيق مجاني باسم المستخدم والباسورد والهوست: <b>IPTV Smarters</b> (بالـ Downloader) أو <b>XCIPTV</b> / <b>Televizo</b> من Google Play.'
      : 'Official apps update their server by themselves, but it can take a while. If you can\'t wait, use a free app with your username, password and host: <b>IPTV Smarters</b> (via Downloader) or <b>XCIPTV</b> / <b>Televizo</b> from Google Play.')
      + '<p style="margin-top:10px"><b>' + (ar ? 'الهوست لباقتك:' : 'Host for your plan:') + '</b></p>' + hostsHTML()
      + '<div class="warn-box">' + t(NEVER_REINSTALL) + '</div>'; }},
    cache: {t:{en:'Clear the app cache', ar:'امسح الكاش بتاع التطبيق'}, b:function(ar){ return (ar
      ? '<ol><li>Settings ← Apps ← التطبيق ← Storage ← <b>Clear cache</b>.</li><li>لسه؟ <b>Clear data</b> وبعدين سجّل دخول تاني (حروف صغيرة).</li></ol>الأسماء ممكن تختلف شوية حسب نوع الجهاز.'
      : '<ol><li>Settings → Apps → the app → Storage → <b>Clear cache</b>.</li><li>Still not working? <b>Clear data</b>, then log in again (lowercase).</li></ol>Menu names can differ slightly by brand.')
      + '<div class="warn-box">' + t(NEVER_REINSTALL) + '</div>'; }},
    mgr_reload: {t:{en:'Reload or change server', ar:'Reload أو غيّر السيرفر'}, b:function(ar){ return (ar
      ? '<ul><li>رسالة حمرا؟ اضغط <b>Reload</b>.</li><li>لسه؟ من الشاشة الرئيسية اضغط <b>Change server</b> وجرّب القوائم التانية (غالباً في 2 أو أكتر).</li><li>ظهرت <b>server urls fail</b>؟ اكتب ' + copyBtn('iboplayers.pro') + ' واضغط <b>Try again</b>.</li></ul>'
      : '<ul><li>Red error? Press <b>Reload</b>.</li><li>Still nothing? On the main screen press <b>Change server</b> and try the other playlists (there are usually 2 or more).</li><li>Seeing <b>server urls fail</b>? Enter ' + copyBtn('iboplayers.pro') + ' and press <b>Try again</b>.</li></ul>')
      + '<div class="warn-box">' + t(NEVER_DELETE) + '</div>'; }},
    mgr_playlist: {t:{en:'Update your playlist on the app\'s website', ar:'حدّث القائمة من موقع التطبيق'}, b:function(ar){
      var a = appObj() || {}, site = a.site || 'https://iboplayer.com/device/login';
      return (ar
        ? '<ol><li>اعمل رابط الـ M3U من الخانات اللي تحت وانسخه.</li><li>من الشاشة الرئيسية للتطبيق هات الـ <b>MAC (Device ID)</b> والـ <b>Device Key</b> (في النسخ القديمة اضغط Change server أو Playlists عشان تظهر).</li><li>ادخل على ' + ext(site) + ' وسجّل بيهم.</li><li>اضغط <b>Add M3U</b> والصق الرابط.</li><li>احفظ واقفل التطبيق وافتحه تاني.</li></ol>'
        : '<ol><li>Make your M3U link in the boxes below and copy it.</li><li>On the app\'s main screen find the <b>MAC (Device ID)</b> and <b>Device Key</b> (on old versions press Change server or Playlists to see them).</li><li>Go to ' + ext(site) + ' and log in with them.</li><li>Click <b>Add M3U</b> and paste the link.</li><li>Save, then close and reopen the app.</li></ol>')
        + m3uHTML(ar)
        + '<div class="warn-box">' + t(NEVER_DELETE) + '</div>'; }},
    one: {t:{en:'Only one channel or movie', ar:'قناة أو فيلم واحد بس'}, b:function(ar){ return ar
      ? 'يبقى المشكلة في المحتوى ده نفسه، مش عندك. ابعت لحسام <b>اسمه وصورة/بوستر</b> ليه على الواتساب وهو هيتابعه.'
      : 'Then the problem is that one item, not your setup. Send Hossam its <b>name and a screenshot/poster</b> on WhatsApp and he\'ll look into it.'; }, final:true},
    k4: {t:{en:'Your device can\'t play 4K', ar:'جهازك مش بيدعم الـ 4K'}, b:function(ar){ return ar
      ? 'لو الـ 4K بس اللي مش شغال والباقي تمام، يبقى الجهاز مش بيدعم 4K — ومفيش حل من ناحية الخدمة. اختار نسخة HD/FHD من نفس القناة أو الفيلم، أو استخدم جهاز بيدعم 4K.'
      : 'If only 4K fails and everything else works, your device doesn\'t support 4K — nothing can fix that on the service side. Pick the HD/FHD version of the same channel or movie, or use a 4K-capable device.'; }},
    av: {t:{en:'Change the player\'s decoder', ar:'غيّر الـ Decoder في المشغل'}, b:function(ar){ return ar
      ? 'دي نصيحة عامة للمشغل (مش مشكلة في الخدمة):<ol><li>جرّب قناة/فيلم تاني — لو واحد بس، ابعت اسمه لحسام.</li><li>من إعدادات المشغل غيّر الـ Decoder (Hardware ↔ Software). في TiviMate: Settings ← Player ← Audio.</li><li>اقفل Passthrough / SPDIF لو موجودة.</li><li>من إعدادات صوت التلفزيون خلي الـ output على <b>PCM</b>.</li></ol>'
      : 'General player tip (not a service problem):<ol><li>Try another channel/movie — if it\'s just one, send its name to Hossam.</li><li>In the player settings switch the decoder (Hardware ↔ Software). TiviMate: Settings → Player → Audio.</li><li>Turn off Passthrough / SPDIF if present.</li><li>In the TV sound settings set the output to <b>PCM</b>.</li></ol>'; }},
    epg: {t:{en:'Fix the TV guide', ar:'صلّح دليل البرامج'}, b:function(ar){ return ar
      ? 'نصيحة عامة (مش مشكلة في الخدمة):<ul><li><b>مواعيد غلط:</b> خلي التاريخ والساعة والمنطقة الزمنية في الجهاز <b>تلقائي</b>.</li><li><b>فاضي:</b> اعمل Update للـ EPG من إعدادات التطبيق أو استنى شوية — مش كل القنوات ليها دليل.</li></ul>'
      : 'General tip (not a service problem):<ul><li><b>Wrong times:</b> set the device date, time and time zone to <b>automatic</b>.</li><li><b>Empty:</b> update the EPG in the app settings, or wait a while — not every channel has a guide.</li></ul>'; }},
    web: {t:{en:'Use an app instead', ar:'استخدم تطبيق بدل المتصفح'}, b:function(ar){ return ar
      ? 'المتصفح طريقة احتياطية. الأسهل تنزّل تطبيق لجهازك — شوف ' + ext('index.html#setup','دليل التثبيت') + '.'
      : 'The browser is a backup method. The easiest fix is an app for your device — see the ' + ext('index.html#setup','setup guide') + '.'; }}
  };

  /* ---------- M3U maker (runs only in the browser — nothing is sent anywhere) ---------- */
  var m3u = {user:'', pass:'', host:0};
  function m3uLink(){
    var H = getHosts(state.plan), host = H[m3u.host] || H[0] || '';
    if(!host || !m3u.user || !m3u.pass) return '';
    return host.replace(/\/+$/, '') + '/get.php?username=' + encodeURIComponent(m3u.user) + '&password=' + encodeURIComponent(m3u.pass) + '&type=m3u_plus&output=ts';
  }
  function m3uOutHTML(ar){
    var link = m3uLink();
    return link ? '<div class="m3u-out">' + copyBtn(link) + '</div>'
      : '<p class="m3u-hint">' + (ar ? 'اكتب اسم المستخدم والباسورد وهيظهر الرابط هنا.' : 'Type your username and password and the link appears here.') + '</p>';
  }
  function m3uHTML(ar){
    var H = getHosts(state.plan);
    return '<div class="m3u"><p class="m3u-title">' + (ar ? 'اعمل رابط الـ M3U بتاعك' : 'Make your M3U link') + '</p>'
      + '<div class="m3u-grid">'
      + '<label>' + (ar ? 'اسم المستخدم' : 'Username') + '<input id="m3uUser" type="text" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" dir="ltr" value="' + esc(m3u.user) + '"></label>'
      + '<label>' + (ar ? 'الباسورد' : 'Password') + '<input id="m3uPass" type="text" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" dir="ltr" value="' + esc(m3u.pass) + '"></label>'
      + '<label>' + (ar ? 'الهوست' : 'Host') + '<select id="m3uHost" dir="ltr">' + H.map(function(h, i){ return '<option value="' + i + '"' + (i === m3u.host ? ' selected' : '') + '>' + esc(h.replace(/^https?:\/\//, '')) + (i === 0 ? (ar ? ' (الأساسي)' : ' (main)') : (ar ? ' (احتياطي)' : ' (backup)')) + '</option>'; }).join('') + '</select></label>'
      + '</div><div id="m3uOut">' + m3uOutHTML(ar) + '</div>'
      + '<p class="m3u-note">🔒 ' + (ar ? 'البيانات بتفضل على الصفحة دي بس — مش بتتبعت لأي حد. الحروف بتتحول لصغيرة تلقائياً. الرابط مش شغال؟ جرّب الهوست الاحتياطي.' : 'Your details stay on this page — nothing is sent anywhere. Letters are made lowercase automatically. Link not working? Try the backup host.') + '</p></div>';
  }
  document.addEventListener('input', function(e){
    var id = e.target && e.target.id;
    if(id !== 'm3uUser' && id !== 'm3uPass' && id !== 'm3uHost') return;
    if(id === 'm3uHost'){ m3u.host = parseInt(e.target.value, 10) || 0; }
    else {
      var v = e.target.value.toLowerCase().replace(/\s+/g, '');
      if(v !== e.target.value) e.target.value = v;
      if(id === 'm3uUser') m3u.user = v; else m3u.pass = v;
    }
    var out = document.getElementById('m3uOut'); if(out) out.innerHTML = m3uOutHTML(lang() === 'ar');
  });
  document.addEventListener('change', function(e){ if(e.target && e.target.id === 'm3uHost'){ m3u.host = parseInt(e.target.value, 10) || 0; var out = document.getElementById('m3uOut'); if(out) out.innerHTML = m3uOutHTML(lang() === 'ar'); } });

  function flowFor(){
    var a = appObj() || {}, c = a.cat, s = state.sym, f = [];
    if(c === 'smarterstv') return ['smarterstv'];
    if(s === 'one') return ['one'];
    if(s === 'k4') return ['speed', 'k4'];   /* 4K needs 25+ Mbps — check that first */
    if(s === 'av') return ['av'];
    if(s === 'epg') return ['epg'];
    if(c === 'web') return s === 'freeze' ? ['magic','speed','web'] : ['magic','web'];
    var byCat = {
      all:   {plan: (a.fix ? ['playlistfix'] : []).concat(['officialwait']), manual:['lower','hosts'], managed:['mgr_reload','mgr_playlist']},
      freeze:{plan:['officialwait'], manual:['hosts'], managed:['mgr_reload']},
      login: {plan: (a.fix ? ['playlistfix'] : []).concat(['officialwait']), manual:['hosts'], managed:['mgr_playlist']},
      open:  {plan:['cache','officialwait'], manual:['cache','hosts'], managed:[]},
      host:  {plan:['officialwait'], manual:['hosts'], managed:['mgr_playlist']}
    };
    var head = {
      all:['magic','inuse','elsewhere','speed'], freeze:['magic','speed','elsewhere','wedns'],
      login:['lower','inuse','elsewhere'], open:['magic','speed'], host:[]
    }[s] || ['magic'];
    f = head.concat((byCat[s] || {})[c] || []);
    if(s === 'all' && c !== 'managed') f.push('wedns');
    return f;
  }

  /* ------------------------------------------------ STATE + RENDER ------------------------------------------------ */
  var state = {plan:null, app:null, sym:null, i:0, flow:[], done:false};

  function outageName(o){
    var ar = lang() === 'ar', t = String(o.label || o.target || '').trim();
    if(/neo|basic|أساسي/i.test(t)) return ar ? 'الباقة الأساسية (Neo 4K)' : 'the Basic plan (Neo 4K)';
    if(/strong|premium|بريميوم/i.test(t)) return ar ? 'باقة بريميوم (Strong 4K)' : 'the Premium plan (Strong 4K)';
    if(/\bxtv\b|x\s*server|^\s*x\s*$|اكس|إكس/i.test(t)) return ar ? 'باقة XTV' : 'the XTV plan';
    if(/marvel|مارفل/i.test(t)) return ar ? 'باقة مارفل' : 'the Marvel plan';
    if(/^all$|all\s*(plans|servers)|كل/i.test(t)) return ar ? 'جميع الباقات' : 'all plans';
    return t;
  }
  function renderAlerts(){
    var box = document.getElementById('alerts'), ar = lang() === 'ar', seen = [];
    box.innerHTML = (live.outages || []).map(function(o){
      var n = outageName(o); if(!n || seen.indexOf(n) > -1) return ''; seen.push(n);
      var cap = n.charAt(0).toUpperCase() + n.slice(1);
      return '<div class="alert">' + icon('warn') + '<div><b>' + (ar ? 'توجد مشكلة مؤقتة في ' + esc(n) + '.' : esc(cap) + ' is having a temporary problem.') + '</b>'
        + '<br><small>' + (ar ? 'لو ده باقتك، مش محتاج تجرب أي خطوات — إحنا بنصلحها والخدمة هترجع لوحدها.' : 'If this is your plan, no need to try any steps — we\'re fixing it and it will come back on its own.') + '</small></div></div>';
    }).join('');
  }
  function renderPlans(){
    document.getElementById('planPick').innerHTML = PLANS.map(function(p){
      return '<button type="button" class="pick-btn" data-plan="' + p.id + '" style="--c:' + p.color + '" aria-pressed="' + (state.plan === p.id) + '">'
        + '<span class="top"><span class="sw"></span><b>' + t(p.name) + '</b></span>'
        + (p.aka ? '<small class="aka">' + (lang()==='ar' ? 'تُعرف أيضاً باسم ' : 'Also known as ') + p.aka + '</small>' : '')
        + '<span class="pr">' + t(p.price) + '</span></button>';
    }).join('');
  }
  function renderApps(){
    var el = document.getElementById('appPick');
    el.innerHTML = GROUPS.map(function(g){
      var apps = APPS.filter(function(a){
        var cat = a.cat === 'smarterstv' ? 'manual' : a.cat;
        return cat === g.cat && (!a.plans || a.plans.indexOf(state.plan) > -1);
      });
      if(!apps.length) return '';
      return '<div class="app-group"><h3>' + t(g.title) + '</h3><div class="chips">' + apps.map(function(a){
        return '<button type="button" class="chip-btn" data-app="' + a.id + '" aria-pressed="' + (state.app === a.id) + '">' + esc(a.name) + (a.sub ? '<small>' + t(a.sub) + '</small>' : '') + '</button>';
      }).join('') + '</div></div>';
    }).join('');
  }
  function renderSyms(){
    document.getElementById('symPick').innerHTML = SYMPTOMS.map(function(s){
      return '<button type="button" class="chip-btn" data-sym="' + s.id + '" aria-pressed="' + (state.sym === s.id) + '">' + t(s.t) + '<small>' + t(s.s) + '</small></button>';
    }).join('');
  }
  function contactHTML(){
    var ar = lang() === 'ar', a = appObj() || {}, sym = SYMPTOMS.filter(function(x){ return x.id === state.sym; })[0];
    var tried = state.flow.slice(0, state.i + 1).map(function(id){ return t(STEPS[id].t); });
    var lines = [
      ar ? 'مرحباً حسام، محتاج مساعدة.' : 'Hi Hossam, I need help.',
      (ar ? 'الباقة: ' : 'Plan: ') + planName(),
      (ar ? 'التطبيق: ' : 'App: ') + (a.name || '') + (a.sub ? ' (' + t(a.sub) + ')' : ''),
      (ar ? 'المشكلة: ' : 'Problem: ') + (sym ? t(sym.t) : '—'),
      (ar ? 'جربت: ' : 'Already tried: ') + (tried.length ? tried.join(' / ') : '—')
    ];
    if(a.cat === 'managed' || a.cat === 'smarterstv') lines.push(ar ? '(هبعت صورة الـ Device ID والـ Device Key)' : '(I\'ll send a photo of my Device ID and Device Key)');
    if(state.sym === 'one') lines.push(ar ? 'اسم القناة/الفيلم: ' : 'Channel/movie name: ');
    var link = wa(MAIN, lines.join('\n'));
    return '<div class="done"><div class="big">💬</div><h3>' + (ar ? 'كلّم حسام' : 'Message Hossam') + '</h3><p class="flow-body">'
      + (ar ? 'الرسالة جاهزة فيها باقتك والتطبيق وكل اللي جربته — بس اضغط إرسال.' : 'The message is ready with your plan, app and everything you tried — just press send.')
      + ((a.cat === 'managed' || a.cat === 'smarterstv') ? (ar ? ' ابعت كمان صورة الـ Device ID والـ Device Key.' : ' Also attach a photo of your Device ID and Device Key.') : '')
      + '</p><div class="flow-actions" style="justify-content:center"><a class="btn btn-wa" href="' + link + '" target="_blank" rel="noopener">' + icon('chat') + (ar ? 'ابعت لحسام على الواتساب' : 'Send to Hossam on WhatsApp') + '</a>'
      + '<button type="button" class="btn btn-ghost" data-act="restart">' + (ar ? 'ابدأ من الأول' : 'Start over') + '</button></div></div>';
  }
  function renderFlow(){
    var el = document.getElementById('flow'), ar = lang() === 'ar';
    var a = appObj() || {}, sym = SYMPTOMS.filter(function(x){ return x.id === state.sym; })[0];
    var crumb = '<div class="flow-top"><span class="flow-crumb"><b>' + esc(planName()) + '</b> · <b>' + esc(a.name || '') + '</b>' + (sym && a.cat !== 'smarterstv' ? ' · ' + t(sym.t) : '') + '</span>'
      + '<button type="button" class="btn btn-ghost btn-sm" data-act="restart">' + (ar ? 'ابدأ من الأول' : 'Start over') + '</button></div>';
    if(state.done === 'fixed'){
      el.innerHTML = crumb + '<div class="done"><div class="big">🎉</div><h3>' + (ar ? 'تمام! استمتع بالمشاهدة' : 'Great — enjoy watching!') + '</h3></div>';
      return;
    }
    if(state.done === 'contact'){ el.innerHTML = crumb + contactHTML(); return; }
    var id = state.flow[state.i], st = STEPS[id], total = state.flow.length;
    var pct = Math.round(((state.i + 1) / (total + 1)) * 100);
    var nextLabel = (st.final || state.i === total - 1) ? (ar ? 'لسه مش شغال — كلّم حسام' : 'Still not working — message Hossam') : (ar ? 'منفعش، الخطوة اللي بعدها' : 'Didn\'t work — next step');
    el.innerHTML = crumb
      + '<div class="progress" aria-hidden="true"><i style="width:' + pct + '%"></i></div>'
      + '<p class="flow-crumb" style="margin:0 0 6px">' + (ar ? 'خطوة ' : 'Step ') + (state.i + 1) + (ar ? ' من ' : ' of ') + total + '</p>'
      + '<h3>' + t(st.t) + '</h3><div class="flow-body">' + st.b(ar) + '</div>'
      + '<div class="flow-actions">'
      + (st.final ? '' : '<button type="button" class="btn btn-ok" data-act="fixed">' + icon('check') + (ar ? 'اتحلت!' : 'Fixed!') + '</button>')
      + '<button type="button" class="btn ' + (st.final ? 'btn-wa' : 'btn-ghost') + '" data-act="next">' + nextLabel + (st.final ? '' : ' ' + '<svg class="ic flip"><use href="#i-arrow"/></svg>') + '</button>'
      + (state.i > 0 ? '<button type="button" class="btn btn-ghost" data-act="back">' + (ar ? 'رجوع' : 'Back') + '</button>' : '')
      + '</div>';
  }
  function show(id, on){ document.getElementById(id).hidden = !on; }
  function go(id){ var el = document.getElementById(id); if(el) el.scrollIntoView({behavior:'smooth', block:'start'}); }
  function startFlow(){
    state.flow = flowFor(); state.i = 0; state.done = false;
    show('flowStep', true); renderFlow(); go('flowStep');
  }
  function renderAll(){
    renderAlerts(); renderPlans();
    if(state.plan){ renderApps(); }
    if(state.app){ renderSyms(); }
    if(state.flow.length){ renderFlow(); }
    renderMore();
  }

  document.addEventListener('click', function(e){
    var b;
    if((b = e.target.closest('[data-plan]'))){
      state.plan = b.getAttribute('data-plan'); state.app = null; state.sym = null; state.flow = []; m3u.host = 0;
      renderPlans(); renderApps(); show('appStep', true); show('symStep', false); show('flowStep', false); go('appStep'); return;
    }
    if((b = e.target.closest('[data-app]'))){
      state.app = b.getAttribute('data-app'); state.sym = null; state.flow = [];
      renderApps(); show('flowStep', false);
      if((appObj() || {}).cat === 'smarterstv'){ show('symStep', false); startFlow(); }
      else { renderSyms(); show('symStep', true); go('symStep'); }
      return;
    }
    if((b = e.target.closest('[data-sym]'))){ state.sym = b.getAttribute('data-sym'); renderSyms(); startFlow(); return; }
    if((b = e.target.closest('[data-act]'))){
      var act = b.getAttribute('data-act');
      if(act === 'fixed'){ state.done = 'fixed'; }
      else if(act === 'next'){ var st = STEPS[state.flow[state.i]]; if(st.final || state.i >= state.flow.length - 1) state.done = 'contact'; else state.i++; }
      else if(act === 'back'){ state.i = Math.max(0, state.i - 1); state.done = false; }
      else if(act === 'restart'){ state.plan = state.app = state.sym = null; state.flow = []; state.done = false; renderPlans(); show('appStep', false); show('symStep', false); show('flowStep', false); go('top'); return; }
      renderFlow(); go('flowStep'); return;
    }
    if((b = e.target.closest('[data-copy]'))){ e.preventDefault(); copy(b.getAttribute('data-copy')); }
  });

  /* ------------------------------------------------ OTHER QUESTIONS ------------------------------------------------ */
  var MORE = [
    {q:{en:'Can I change the video quality?', ar:'أقدر أغيّر الجودة؟'}, a:{en:'No — each channel/movie has a fixed quality. Some titles exist in more than one version (HD and 4K): search for another version.', ar:'لا — كل قناة أو فيلم ليه جودة ثابتة. بعض الأعمال ليها أكتر من نسخة (HD و 4K): دور على نسخة تانية.'}},
    {q:{en:'Wrong subtitles or audio language?', ar:'الترجمة أو اللغة غلط؟'}, a:{en:'Some titles have built-in subtitles. In Basic and Premium the same show often exists dubbed, with different subtitles, or original — search the title and pick the version you like.', ar:'بعض الأعمال الترجمة فيها ثابتة. في Basic وPremium نفس المسلسل غالباً موجود مدبلج، وبترجمات مختلفة، وأصلي — دور على الاسم واختار النسخة اللي تناسبك.'}},
    {q:{en:'Can I watch something that already aired?', ar:'أقدر أتفرج على حاجة اتعرضت خلاص؟'}, a:{en:'Basic and Premium have channels marked +6 at the end of the channel list — they replay the same channel 6 hours later.', ar:'في Basic وPremium في قنوات عليها +6 في آخر قائمة القنوات — بتعيد نفس القناة بعد 6 ساعات.'}},
    {q:{en:'The app asks for a PIN', ar:'التطبيق بيطلب PIN'}, a:{en:'Most apps use 0000 as the default PIN. We don\'t provide adult content.', ar:'أغلب التطبيقات الـ PIN الافتراضي فيها 0000. إحنا مش بنوفر محتوى للكبار.'}},
    {q:{en:'My favorites disappeared', ar:'المفضلة اتمسحت'}, a:{en:'Favorites reset when the host is changed (needed to keep the service running). Add them again: highlight the item, hold OK and choose Favorite (or press the yellow button).', ar:'المفضلة بتتمسح لما الهوست يتغير (ده لازم عشان الخدمة تفضل شغالة). ضيفها تاني: قف على المحتوى، دوس مطولاً على OK واختار Favorite (أو الزرار الأصفر).'}},
    {q:{en:'Can you add a channel, movie or series?', ar:'ممكن تضيفوا قناة أو فيلم أو مسلسل؟'}, a:{en:'New channels are usually not possible. Movies and series can be requested: send the name and poster to Hossam on WhatsApp — not guaranteed, but usually added within 2–3 days.', ar:'القنوات الجديدة غالباً مش ممكنة. الأفلام والمسلسلات ممكن تطلبها: ابعت الاسم والبوستر لحسام على الواتساب — مش مضمون، بس غالباً بتتضاف خلال 2–3 أيام.'}},
    {q:{en:'Can I delete and reinstall the app?', ar:'أقدر أمسح التطبيق وأنزله تاني؟'}, a:{en:'No. IBO Player, Bob Player and IBO XPlayer lose their paid activation (you\'d pay again), and some other apps can\'t be downloaded again.', ar:'لا. IBO Player وBob Player وIBO XPlayer بيضيع تفعيلهم المدفوع (وهتدفع تاني)، وبعض التطبيقات التانية مش بتتنزل تاني.'}}
  ];
  function renderMore(){
    document.getElementById('moreFaq').innerHTML = MORE.map(function(f){
      return '<details><summary>' + t(f.q) + icon('plus') + '</summary><p>' + t(f.a) + '</p></details>';
    }).join('');
  }

  /* ------------------------------------------------ LANGUAGE + UTIL ------------------------------------------------ */
  function setLang(l, save){
    doc.lang = l; doc.dir = l === 'ar' ? 'rtl' : 'ltr';
    if(save) store('htv-lang', l);
    var sub = document.querySelector('[data-wa="subscribe"]');
    if(sub) sub.href = wa(MAIN, l === 'ar' ? 'مرحباً، أريد تجربة مجانية.' : 'Hi Hossam TV, I\'d like a free trial.');
    document.querySelectorAll('[data-page]').forEach(function(a){ a.href = '/' + l + '/' + a.getAttribute('data-page'); });
    renderAll();
  }
  var toastT;
  function toast(msg){ var el = document.getElementById('toast'); el.textContent = msg; el.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(function(){ el.classList.remove('show'); }, 1400); }
  function copy(text){
    var done = function(){ toast(lang() === 'ar' ? 'تم النسخ' : 'Copied'); };
    if(navigator.clipboard && window.isSecureContext){ navigator.clipboard.writeText(text).then(done, fallback); } else { fallback(); }
    function fallback(){ var ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select(); try{ document.execCommand('copy'); done(); }catch(e){} document.body.removeChild(ta); }
  }

  loadLive();
  setLang(doc.lang === 'ar' ? 'ar' : 'en', false);
})();
