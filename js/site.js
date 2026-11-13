/* Progressive enhancements for bonet.care. No dependencies. Every page works without this file. */
(function () {
  'use strict';
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- text size */
  function setSize(on) {
    document.documentElement.classList.toggle('large-text', on);
    $$('[data-textsize]').forEach(function (b) { b.setAttribute('aria-pressed', on ? 'true' : 'false'); b.style.background = on ? '#e7f3fe' : ''; b.style.color = on ? '#1468b8' : ''; });
    store.set('bonet-large-text', on ? '1' : '0');
  }
  $$('[data-textsize]').forEach(function (b) { b.addEventListener('click', function () { setSize(!document.documentElement.classList.contains('large-text')); }); });
  if (store.get('bonet-large-text') === '1') setSize(true);

  /* ---- language menu: close on outside click and Escape */
  var menu = document.querySelector('.langmenu');
  if (menu) {
    document.addEventListener('click', function (e) { if (menu.open && !menu.contains(e.target)) menu.open = false; });
    menu.addEventListener('keydown', function (e) { if (e.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); } });
  }

  /* ---- switching language keeps the section the visitor is on (#plans, #faq ...) */
  $$('.langmenu a, .ftr-langs a').forEach(function (a) { a.addEventListener('click', function () { if (location.hash && a.getAttribute('href').indexOf('#') < 0) a.href = a.getAttribute('href') + location.hash; }); });

  /* ---- inner pages keep English and Cantonese text in data-en / data-zh and switch in place */
  var titleEn = document.title, tzh = document.querySelector('meta[name="x-title-zh"]');
  function setLang(l) {
    var attr = l === 'yue' ? 'data-zh' : 'data-en';
    $$('[data-en]').forEach(function (el) { var v = el.getAttribute(attr); if (v != null) el.innerHTML = v; });
    $$('[data-setlang]').forEach(function (b) { if (b.getAttribute('data-setlang') === l) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current'); });
    var cur = menu && menu.querySelector('summary span'); var b = menu && menu.querySelector('[data-setlang="' + l + '"]');
    if (cur && b) cur.textContent = b.textContent;
    document.documentElement.lang = l === 'yue' ? 'yue-Hant-HK' : 'en';
    if (tzh) document.title = l === 'yue' ? tzh.content : titleEn;
    store.set('bonet-inner-lang', l);
    if (menu) menu.open = false;
  }
  $$('[data-setlang]').forEach(function (b) { b.addEventListener('click', function () { setLang(b.getAttribute('data-setlang')); }); });
  if ($$('[data-setlang]').length && store.get('bonet-inner-lang') === 'yue') setLang('yue');

  /* ---- first-visit suggestion (never redirects) */
  var SUG = {
    en: ['en', 'View this page in English', 'Stay here', '/'], 'zh-hant': ['zh-Hant', '以繁體中文閱讀', '留在此頁', '/zh-hant/'],
    yue: ['yue-Hant-HK', '轉用廣東話睇', '留喺呢頁', '/yue/'], 'zh-hans': ['zh-Hans', '阅读简体中文版', '留在此页', '/zh-hans/'],
    ja: ['ja', '日本語で見る', 'このまま', '/ja/'], es: ['es', 'Ver esta página en español', 'Quedarme aquí', '/es/'],
    de: ['de', 'Diese Seite auf Deutsch ansehen', 'Hier bleiben', '/de/'], fr: ['fr', 'Voir cette page en français', 'Rester ici', '/fr/']
  };
  function pick(langs) {
    for (var i = 0; i < langs.length; i++) {
      var l = String(langs[i]).toLowerCase();
      if (l.indexOf('yue') === 0 || l === 'zh-hk' || l === 'zh-mo') return 'yue';
      if (l === 'zh-cn' || l === 'zh-sg' || l.indexOf('zh-hans') === 0) return 'zh-hans';
      if (l.indexOf('zh') === 0) return 'zh-hant';
      if (l.indexOf('ja') === 0) return 'ja';
      if (l.indexOf('es') === 0) return 'es';
      if (l.indexOf('de') === 0) return 'de';
      if (l.indexOf('fr') === 0) return 'fr';
      if (l.indexOf('en') === 0) return 'en';
    }
    return null;
  }
  var here = document.documentElement.getAttribute('data-site-lang');
  if (here && !store.get('bonet-lang-dismissed')) {
    var want = pick(navigator.languages || [navigator.language || 'en']);
    if (want && want !== here && SUG[want]) {
      var s = SUG[want], bar = document.createElement('div');
      bar.className = 'langbar'; bar.setAttribute('role', 'region'); bar.setAttribute('aria-label', 'Language');
      bar.innerHTML = '<div class="wrap"><span></span><span><a href="' + s[3] + '" lang="' + s[0] + '"></a> <button type="button"></button></span></div>';
      bar.querySelector('a').textContent = s[1]; bar.querySelector('button').textContent = s[2];
      bar.querySelector('span').textContent = '🌐';
      bar.querySelector('button').addEventListener('click', function () { store.set('bonet-lang-dismissed', '1'); bar.remove(); });
      document.body.insertBefore(bar, document.body.firstChild);
    }
  }

  /* ---- demo video: nothing loads until the visitor presses play */
  $$('[data-video]').forEach(function (b) {
    b.addEventListener('click', function () {
      var v = document.createElement('video');
      v.src = b.getAttribute('data-video'); v.controls = true; v.autoplay = true; v.playsInline = true; v.preload = 'auto';
      v.setAttribute('poster', b.querySelector('img').src); v.className = 'player'; v.style.cursor = 'auto';
      if (b.getAttribute('data-vtt')) { var tk = document.createElement('track'); tk.kind = 'captions'; tk.src = b.getAttribute('data-vtt'); tk.default = true; tk.label = b.getAttribute('data-lang') || ''; v.appendChild(tk); }
      b.replaceWith(v); v.play().catch(function () {});
    });
  });

  /* ---- scroll entrances (CSS does the motion; this only adds .in when something is on screen) */
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.15, rootMargin: '0px 0px -6% 0px' }) : null;
  $$('.rv, .rv-word, .rv-tilt, .rv-bars, [data-final]').forEach(function (el) { if (io) io.observe(el); else el.classList.add('in'); });

  /* ---- corgi sprite player. Sheets: one row of frames, 480 px (or 240 px on small slots). */
  var CLIPS = { wave: [20, 16], cheer: [20, 16], point: [24, 16], wiggle: [20, 16], tilt: [24, 14], sleep: [24, 12], idle: [24, 12] };
  var visible = new WeakMap();
  var sio = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { visible.set(e.target, e.isIntersecting); e.target.style.animationPlayState = e.isIntersecting && !document.hidden ? 'running' : 'paused'; });
  }) : null;
  document.addEventListener('visibilitychange', function () { $$('.sprite[data-run]').forEach(function (el) { el.style.animationPlayState = !document.hidden && visible.get(el) !== false ? 'running' : 'paused'; }); });
  function play(el, clip, loops, then) {
    var c = CLIPS[clip]; if (!c) return;
    var small = el.offsetWidth * (window.devicePixelRatio || 1) <= 260;
    el.setAttribute('data-run', clip);
    el.style.backgroundImage = 'url(/img/mascot/anim/' + clip + (small ? '-sm' : '') + '.webp)';
    el.style.backgroundSize = (c[0] * 100) + '% 100%';
    el.style.setProperty('--n', c[0]);
    el.style.animation = 'none'; void el.offsetWidth;
    if (reduce) { el.style.animation = 'none'; el.style.backgroundPosition = '0 0'; return; }
    el.style.animationDuration = (c[0] / c[1]) + 's';
    el.style.animationIterationCount = loops || 'infinite';
    /* the inline `animation: none` reset above also resets the timing function, so it must be set again here: without steps() the sheet
       slides smoothly across its frames and the corgi seems to sway left and right (that was the shake) */
    el.style.animationName = 'sprite'; el.style.animationTimingFunction = 'steps(' + c[0] + ', jump-none)'; el.style.animationFillMode = 'both'; el.style.animationPlayState = 'running';
    el.onanimationend = loops ? function () { el.onanimationend = null; play(el, then || 'idle'); } : null;
  }
  var sprites = $$('.sprite[data-clip]');
  sprites.forEach(function (el) {
    var clip = el.getAttribute('data-clip');
    if (sio) sio.observe(el);
    var start = function () { play(el, clip, el.getAttribute('data-loops') ? +el.getAttribute('data-loops') : 0, el.getAttribute('data-then')); };
    if (el.closest('[data-final]')) { var f = el.closest('[data-final]'); new MutationObserver(function () { if (f.classList.contains('in')) start(); }).observe(f, { attributes: true, attributeFilter: ['class'] }); }
    else if (clip === 'sleep') { start(); } else start();
    var btn = el.closest('.pupbtn, .pup');
    var react = el.closest('[data-hover]') || btn;
    var hov = react && react.getAttribute('data-hover');
    /* reactions play once and return to the REST clip (idle, or sleep in the footer), never to the intro clip */
    var rest = el.getAttribute('data-rest') || 'idle';
    if (btn && hov) { var go = function () { if (reduce || el.getAttribute('data-run') === hov) return; play(el, hov, 1, rest); }; btn.addEventListener('pointerenter', go); btn.addEventListener('click', go); }
  });
  /* hero corgi follows the demo: points when it starts, cheers when the goal is reached */
  var hero = document.querySelector('[data-corgi] .sprite');
  if (hero) {
    window.addEventListener('bonet:start', function () { play(hero, 'point', 1, 'idle'); });
    window.addEventListener('bonet:goal', function () { play(hero, 'cheer', 2, 'idle'); var c = hero.closest('.corgi'); c.classList.remove('hop'); void c.offsetWidth; c.classList.add('hop'); });
  }

  /* ---- hero parallax: floating icons drift a little with the pointer; transform only, off for reduced motion and small screens */
  var par = $$('[data-par]');
  if (par.length && !reduce && window.matchMedia('(min-width: 52rem)').matches) {
    var px = 0, py = 0, tick = false;
    window.addEventListener('pointermove', function (e) {
      px = (e.clientX / innerWidth - .5) * 2; py = (e.clientY / innerHeight - .5) * 2;
      if (!tick) { tick = true; requestAnimationFrame(function () { par.forEach(function (p) { p.style.setProperty('--px', px.toFixed(3)); p.style.setProperty('--py', py.toFixed(3)); }); tick = false; }); }
    }, { passive: true });
  }
})();
