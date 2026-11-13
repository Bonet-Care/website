/* Consent gate for bonet.care. Google Analytics is requested only from here, never from a page.
   Strict (EEA, UK, Switzerland, unknown): off until the visitor accepts. Open (elsewhere): on, with an opt-out, and
   Global Privacy Control or Do Not Track switch it off. The choice is kept in localStorage key bonet_consent. */
(function () {
  'use strict';
  var GA_ID = 'G-WMQD9MWHJN', POLICY = '2026-11-13', KEY = 'bonet_consent', YEAR = 365 * 864e5;
  var STRICT = 'AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE IS LI NO GB CH JE GG IM XX T1'.split(' ');
  var OPT_IN_REGIONS = ['CA-QC'];
  var T = {
 "en": {
  "title": "Your privacy choices",
  "body_strict": "Bonet saves a few things on your device to keep you signed in and remember your settings. We would also like to count how Bonet is used, so we can fix problems. This is optional.",
  "body_open": "We count how Bonet is used so we can fix problems. We never send your practice results. You can turn this off at any time.",
  "accept": "Accept analytics",
  "reject": "Reject analytics",
  "settings": "Settings",
  "ok": "OK",
  "panel_title": "Cookie settings",
  "necessary_title": "Needed",
  "necessary_text": "Keeps you signed in and remembers your settings. Always on.",
  "analytics_title": "Usage statistics",
  "analytics_text": "Counts how the app and website are used. Helps us fix problems. Off unless you turn it on.",
  "save": "Save my choices",
  "policy_link": "Read the Cookie Policy",
  "footer_link": "Cookie settings",
  "saved": "Saved.",
  "gpc": "Your browser sends a privacy signal, so statistics are off."
 },
 "zh-Hant": {
  "title": "您的私隱選擇",
  "body_strict": "Bonet 會在您的裝置上儲存少量資料，用來保持登入及記住設定。我們也希望統計 Bonet 的使用情況，以便修正問題。這是自願的。",
  "body_open": "我們會統計 Bonet 的使用情況，以便修正問題。我們不會傳送您的練習結果。您可以隨時關閉。",
  "accept": "接受統計",
  "reject": "拒絕統計",
  "settings": "設定",
  "ok": "知道了",
  "panel_title": "Cookie 設定",
  "necessary_title": "必要項目",
  "necessary_text": "用來保持登入及記住設定。永遠開啟。",
  "analytics_title": "使用統計",
  "analytics_text": "統計應用程式與網站的使用情況，幫助我們修正問題。除非您開啟，否則關閉。",
  "save": "儲存我的選擇",
  "policy_link": "閱讀 Cookie 政策",
  "footer_link": "Cookie 設定",
  "saved": "已儲存。",
  "gpc": "您的瀏覽器已發出私隱訊號，因此統計已關閉。"
 },
 "yue-Hant-HK": {
  "title": "你嘅私隱選擇",
  "body_strict": "Bonet 會喺你部機入面儲存少少資料，用嚟保持登入同記住設定。我哋亦想統計下 Bonet 點樣被使用，方便修正問題。呢個係自願嘅。",
  "body_open": "我哋會統計 Bonet 點樣被使用，方便修正問題。我哋唔會傳送你嘅練習結果。你隨時可以關閉。",
  "accept": "接受統計",
  "reject": "拒絕統計",
  "settings": "設定",
  "ok": "知道",
  "panel_title": "Cookie 設定",
  "necessary_title": "必要項目",
  "necessary_text": "用嚟保持登入同記住設定。一直開住。",
  "analytics_title": "使用統計",
  "analytics_text": "統計個應用程式同網站點樣被使用，幫我哋修正問題。除非你開啟，否則係關閉嘅。",
  "save": "儲存我嘅選擇",
  "policy_link": "睇 Cookie 政策",
  "footer_link": "Cookie 設定",
  "saved": "已儲存。",
  "gpc": "你嘅瀏覽器發出咗私隱訊號，所以統計已關閉。"
 },
 "zh-Hans": {
  "title": "您的隐私选择",
  "body_strict": "Bonet 会在您的设备上保存少量信息，用来保持登录并记住设置。我们也希望统计 Bonet 的使用情况，以便修复问题。这是自愿的。",
  "body_open": "我们会统计 Bonet 的使用情况，以便修复问题。我们不会发送您的练习结果。您可以随时关闭。",
  "accept": "接受统计",
  "reject": "拒绝统计",
  "settings": "设置",
  "ok": "知道了",
  "panel_title": "Cookie 设置",
  "necessary_title": "必要项目",
  "necessary_text": "用来保持登录并记住设置。始终开启。",
  "analytics_title": "使用统计",
  "analytics_text": "统计应用和网站的使用情况，帮助我们修复问题。除非您开启，否则为关闭。",
  "save": "保存我的选择",
  "policy_link": "阅读 Cookie 政策",
  "footer_link": "Cookie 设置",
  "saved": "已保存。",
  "gpc": "您的浏览器发出了隐私信号，因此统计已关闭。"
 },
 "ja": {
  "title": "プライバシーの選択",
  "body_strict": "Bonetは、ログイン状態の維持と設定の記憶のために、お使いの端末に少量の情報を保存します。問題を直すため、Bonetの使われ方を数えることも考えています。これは任意です。",
  "body_open": "問題を直すため、Bonetの使われ方を数えています。練習の結果は送りません。いつでもオフにできます。",
  "accept": "許可する",
  "reject": "許可しない",
  "settings": "設定",
  "ok": "了解",
  "panel_title": "Cookieの設定",
  "necessary_title": "必須の項目",
  "necessary_text": "ログイン状態の維持と設定の記憶に使います。常にオンです。",
  "analytics_title": "利用状況の集計",
  "analytics_text": "アプリとウェブサイトの使われ方を数え、問題の修正に役立てます。オンにしない限りオフです。",
  "save": "選択を保存",
  "policy_link": "Cookieポリシーを読む",
  "footer_link": "Cookieの設定",
  "saved": "保存しました。",
  "gpc": "お使いのブラウザがプライバシー信号を送っているため、集計はオフです。"
 },
 "es": {
  "title": "Sus opciones de privacidad",
  "body_strict": "Bonet guarda unos pocos datos en su dispositivo para mantener su sesión abierta y recordar sus ajustes. También nos gustaría contar cómo se usa Bonet para corregir problemas. Es opcional.",
  "body_open": "Contamos cómo se usa Bonet para corregir problemas. Nunca enviamos sus resultados de práctica. Puede desactivarlo cuando quiera.",
  "accept": "Aceptar estadísticas",
  "reject": "Rechazar estadísticas",
  "settings": "Ajustes",
  "ok": "Entendido",
  "panel_title": "Ajustes de cookies",
  "necessary_title": "Necesarias",
  "necessary_text": "Sirven para mantener su sesión y recordar sus ajustes. Siempre activas.",
  "analytics_title": "Estadísticas de uso",
  "analytics_text": "Cuentan cómo se usan la aplicación y el sitio web. Nos ayudan a corregir problemas. Desactivadas salvo que usted las active.",
  "save": "Guardar mis opciones",
  "policy_link": "Leer la política de cookies",
  "footer_link": "Ajustes de cookies",
  "saved": "Guardado.",
  "gpc": "Su navegador envía una señal de privacidad, por eso las estadísticas están desactivadas."
 },
 "de": {
  "title": "Ihre Datenschutz-Auswahl",
  "body_strict": "Bonet speichert wenige Angaben auf Ihrem Gerät, damit Sie angemeldet bleiben und Ihre Einstellungen erhalten bleiben. Wir möchten außerdem zählen, wie Bonet genutzt wird, um Fehler zu beheben. Das ist freiwillig.",
  "body_open": "Wir zählen, wie Bonet genutzt wird, um Fehler zu beheben. Ihre Übungsergebnisse senden wir nie. Sie können das jederzeit ausschalten.",
  "accept": "Statistik erlauben",
  "reject": "Statistik ablehnen",
  "settings": "Einstellungen",
  "ok": "Verstanden",
  "panel_title": "Cookie-Einstellungen",
  "necessary_title": "Notwendig",
  "necessary_text": "Damit Sie angemeldet bleiben und Ihre Einstellungen gespeichert werden. Immer an.",
  "analytics_title": "Nutzungsstatistik",
  "analytics_text": "Zählt, wie App und Website genutzt werden. Hilft uns, Fehler zu beheben. Aus, solange Sie sie nicht einschalten.",
  "save": "Meine Auswahl speichern",
  "policy_link": "Cookie-Richtlinie lesen",
  "footer_link": "Cookie-Einstellungen",
  "saved": "Gespeichert.",
  "gpc": "Ihr Browser sendet ein Datenschutzsignal, deshalb ist die Statistik aus."
 },
 "fr": {
  "title": "Vos choix de confidentialité",
  "body_strict": "Bonet enregistre quelques informations sur votre appareil pour vous garder connecté et retenir vos réglages. Nous aimerions aussi compter comment Bonet est utilisé, afin de corriger les problèmes. C'est facultatif.",
  "body_open": "Nous comptons comment Bonet est utilisé afin de corriger les problèmes. Nous n'envoyons jamais vos résultats d'exercices. Vous pouvez l'arrêter à tout moment.",
  "accept": "Accepter les statistiques",
  "reject": "Refuser les statistiques",
  "settings": "Réglages",
  "ok": "Compris",
  "panel_title": "Réglages des cookies",
  "necessary_title": "Nécessaires",
  "necessary_text": "Servent à vous garder connecté et à retenir vos réglages. Toujours actifs.",
  "analytics_title": "Statistiques d'utilisation",
  "analytics_text": "Comptent comment l'application et le site sont utilisés. Nous aident à corriger les problèmes. Désactivées sauf si vous les activez.",
  "save": "Enregistrer mes choix",
  "policy_link": "Lire la politique de cookies",
  "footer_link": "Réglages des cookies",
  "saved": "Enregistré.",
  "gpc": "Votre navigateur envoie un signal de confidentialité, les statistiques sont donc désactivées."
 }
};

  var W = { en: ['Close', 'On', 'Off'], 'zh-Hant': ['關閉', '開', '關'], 'yue-Hant-HK': ['閂咗佢', '開', '關'], 'zh-Hans': ['关闭', '开', '关'], ja: ['閉じる', 'オン', 'オフ'], es: ['Cerrar', 'Sí', 'No'], de: ['Schließen', 'An', 'Aus'], fr: ['Fermer', 'Oui', 'Non'] };
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } }
  function sess(k, v) { try { if (v === undefined) return sessionStorage.getItem(k); sessionStorage.setItem(k, v); } catch (e) { return null; } }
  var lang = (document.documentElement.getAttribute('lang') || 'en');
  var tr = T[lang] || T[lang.split('-')[0]] || T.en;
  var words = W[lang] || W[lang.split('-')[0]] || W.en;
  var rec = null;
  try { rec = JSON.parse(store(KEY) || 'null'); } catch (e) { rec = null; }
  var gaLoaded = false, opener = null, banner = null, dlg = null;

  function signal() { return navigator.globalPrivacyControl === true || navigator.doNotTrack === '1' || window.doNotTrack === '1'; }
  function save(analytics, mode, source) {
    rec = { v: 1, policy: POLICY, analytics: !!analytics, mode: mode, source: source, ts: new Date().toISOString(), lang: lang.split('-')[0] };
    store(KEY, JSON.stringify(rec));
    apply();
  }
  function expire(name, domain) { document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + (domain ? '; domain=' + domain : ''); }
  function loadGA() {
    if (gaLoaded) return; gaLoaded = true;
    window['ga-disable-' + GA_ID] = false;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID, { allow_google_signals: false, allow_ad_personalization_signals: false });
    var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID; document.head.appendChild(s);
  }
  function stopGA() {
    window['ga-disable-' + GA_ID] = true;
    ['_ga', '_ga_' + GA_ID.slice(2)].forEach(function (n) { expire(n); expire(n, location.hostname); expire(n, '.' + location.hostname.replace(/^www\./, '')); });
  }
  function apply() { if (rec && rec.analytics) loadGA(); else stopGA(); }

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    for (var k in (attrs || {})) { if (k === 'text') n.textContent = attrs[k]; else n.setAttribute(k, attrs[k]); }
    (kids || []).forEach(function (c) { n.appendChild(c); });
    return n;
  }
  function button(cls, text, fn) { var b = el('button', { type: 'button', 'class': cls, text: text }); b.addEventListener('click', fn); return b; }
  function close() { if (banner) { banner.remove(); banner = null; } }

  function showBanner(mode, gpc) {
    if (banner) return;
    var strict = mode === 'strict';
    var head = el('h2', { id: 'cnb-title', text: tr.title });
    var body = el('p', { text: gpc ? tr.gpc : (strict ? tr.body_strict : tr.body_open) });
    var row = el('div', { 'class': 'cnb-row' });
    if (strict) {
      row.appendChild(button('cnb-btn', tr.reject, function () { save(false, mode, 'banner'); close(); }));
      row.appendChild(button('cnb-btn', tr.accept, function () { save(true, mode, 'banner'); close(); }));
    } else {
      row.appendChild(button('cnb-btn', tr.ok, function () { if (!rec) save(!gpc, mode, gpc ? 'signal' : 'default'); close(); }));
    }
    var set = button('cnb-link', tr.settings, function () { openSettings(set, mode); });
    row.appendChild(set);
    banner = el('section', { 'class': 'cnb', role: 'region', 'aria-labelledby': 'cnb-title' }, [el('div', { 'class': 'cnb-in' }, [head, body, row])]);
    banner.addEventListener('keydown', function (e) { if (e.key === 'Escape' && strict) { save(false, mode, 'escape'); close(); } });
    var skip = document.querySelector('.skip');
    document.body.insertBefore(banner, skip ? skip.nextSibling : document.body.firstChild);
    sess('bonet_cb_seen', '1');
    if (!strict && !gpc && !rec) { /* open region default: analytics on, recorded when OK is pressed or the person leaves the notice */ rec = { v: 1, policy: POLICY, analytics: true, mode: mode, source: 'default', ts: new Date().toISOString(), lang: lang.split('-')[0] }; store(KEY, JSON.stringify(rec)); apply(); }
    if (!strict && gpc && !rec) { save(false, mode, 'signal'); }
  }

  function openSettings(from, mode) {
    if (dlg) return;
    opener = from || document.activeElement;
    mode = mode || (rec && rec.mode) || sess('bonet_mode') || 'strict';
    var on = rec ? rec.analytics : mode !== 'strict' && !signal();
    var state = el('span', { 'class': 'cnb-state', text: on ? words[1] : words[2] });
    var sw = el('button', { type: 'button', role: 'switch', 'aria-checked': String(on), 'class': 'cnb-switch', 'aria-labelledby': 'cnb-an-t' }, [el('span', { 'class': 'cnb-knob' })]);
    sw.addEventListener('click', function () { on = !on; sw.setAttribute('aria-checked', String(on)); state.textContent = on ? words[1] : words[2]; });
    var live = el('p', { 'class': 'cnb-live', 'aria-live': 'polite' });
    var h = el('h2', { id: 'cnb-dt', tabindex: '-1', text: tr.panel_title });
    var seg = location.pathname.split('/')[1];
    var policy = el('a', { href: (/^(zh-hant|yue|zh-hans|ja|es|de|fr)$/.test(seg) ? '/' + seg : '') + '/cookies', text: tr.policy_link });
    var last = rec ? el('p', { 'class': 'cnb-last', text: new Date(rec.ts).toLocaleDateString(lang) }) : null;
    var save_ = button('cnb-btn', tr.save, function () { save(on, mode, 'settings'); live.textContent = tr.saved; close(); setTimeout(closeDlg, 700); });
    var x = button('cnb-btn cnb-btn--ghost', words[0], function () { closeDlg(); });
    dlg = el('div', { 'class': 'cnb-back' }, [el('div', { 'class': 'cnb-dlg', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'cnb-dt' }, [
      h, el('p', {}, [policy]),
      el('div', { 'class': 'cnb-item' }, [el('div', {}, [el('h3', { text: tr.necessary_title }), el('p', { text: tr.necessary_text })]), el('span', { 'class': 'cnb-state', text: '✓' })]),
      el('div', { 'class': 'cnb-item' }, [el('div', {}, [el('h3', { id: 'cnb-an-t', text: tr.analytics_title }), el('p', { text: tr.analytics_text })]), el('div', { 'class': 'cnb-sw' }, [sw, state])]),
      last || el('span'), live, el('div', { 'class': 'cnb-row' }, [save_, x])])]);
    document.body.appendChild(dlg);
    h.focus();
    dlg.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); closeDlg(); return; }
      if (e.key !== 'Tab') return;
      var f = dlg.querySelectorAll('a[href], button'); if (!f.length) return;
      var a = f[0], z = f[f.length - 1];
      if (e.shiftKey && (document.activeElement === a || document.activeElement === h)) { e.preventDefault(); z.focus(); }
      else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
    });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) closeDlg(); });
  }
  function closeDlg() { if (dlg) { dlg.remove(); dlg = null; if (opener && document.contains(opener)) opener.focus(); else { var f = document.querySelector('[data-consent-open]'); if (f) f.focus(); } } }

  function boot() {
    document.addEventListener('click', function (e) {
      var t = e.target.closest && e.target.closest('[data-consent-open]');
      if (t) { e.preventDefault(); openSettings(t); }
    });
    // the legal-page and footer link works before anything else has run
    var old = store('bonet_analytics_choice');
    if (old !== null && !rec) { rec = { v: 1, policy: POLICY, analytics: old === 'on' || old === 'true' || old === '1', mode: 'open', source: 'settings', ts: new Date().toISOString(), lang: lang.split('-')[0] }; store(KEY, JSON.stringify(rec)); store('bonet_analytics_choice', null); }
    var fresh = rec && rec.policy === POLICY && (rec.mode !== 'strict' || Date.now() - Date.parse(rec.ts) < YEAR);
    if (fresh) { apply(); return; }
    var cached = sess('bonet_mode');
    if (cached) return decide(cached);
    var done = false, timer = setTimeout(function () { finish('strict'); }, 1500);
    function finish(m) { if (done) return; done = true; clearTimeout(timer); sess('bonet_mode', m); decide(m); }
    try {
      fetch('/geo', { cache: 'no-store', credentials: 'omit' }).then(function (r) { return r.json(); }).then(function (g) {
        var strict = STRICT.indexOf(g.country) > -1 || OPT_IN_REGIONS.indexOf(g.country + '-' + g.region) > -1;
        finish(strict ? 'strict' : 'open');
      }).catch(function () { finish('strict'); });
    } catch (e) { finish('strict'); }
  }
  function decide(mode) {
    if (mode === 'strict') { stopGA(); if (!sess('bonet_cb_seen')) showBanner('strict'); return; }
    var gpc = signal();
    if (gpc) { stopGA(); }
    showBanner('open', gpc);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
