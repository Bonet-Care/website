/* Cost board on the home page. Everything is computed in the browser; nothing is sent anywhere. Price and trial come from data attributes. */
(function () {
  'use strict';
  var root = document.querySelector('[data-cost]');
  if (!root) return;
  var cur = root.getAttribute('data-cur') || '', price = parseFloat(root.getAttribute('data-price')) || 0;
  var weeks = parseFloat(root.getAttribute('data-weeks')) || 4.33, notset = root.getAttribute('data-notset') || '-';
  var tag = root.getAttribute('data-lang') === 'yue' ? 'zh-HK' : (root.getAttribute('data-lang') || 'en');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var num = function (n, d) { try { return new Intl.NumberFormat(tag, { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }).format(n); } catch (e) { return n.toFixed(d || 0); } };
  var money = function (n, d) { return cur + num(n, d); };
  var $ = function (s) { return root.querySelector(s); };
  /* visits a month for each coarse answer: now and then = about one visit every two months */
  var VPM = { none: 0, some: 0.5, month: 1, often: 3 };
  var inp = {}, out = {};
  ['cost', 'days', 'mins'].forEach(function (k) { inp[k] = $('[data-in="' + k + '"]'); });
  ['cost', 'days', 'mins', 'pdays', 'mins_month', 'per_day'].forEach(function (k) { out[k] = $('[data-out="' + k + '"]'); });
  var cells = root.querySelectorAll('[data-days] i'), pup = $('[data-pup]'), msg = $('[data-msg]'), costField = $('[data-costfield]');
  var last = {};
  function set(k, text) {
    var el = out[k]; if (!el || el.textContent === text) return;
    el.textContent = text;
    if (!reduce && el.closest('.cb-stat') && last[k] !== undefined) { el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop'); }
    last[k] = text;
  }
  function ther() { var r = root.querySelector('[data-ther]:checked'); return r ? r.value : 'none'; }
  function update() {
    var c = +inp.cost.value, d = +inp.days.value, m = +inp.mins.value, t = ther(), v = VPM[t] || 0;
    if (!v) c = 0;
    var pd = Math.round(d * weeks);
    set('days', num(d)); set('mins', num(m)); set('cost', c > 0 ? money(c) : notset);
    set('pdays', num(pd)); set('mins_month', num(pd * m)); set('per_day', money(price / pd, 2));
    ['cost', 'days', 'mins'].forEach(function (k) { var i = inp[k]; i.style.setProperty('--p', ((i.value - i.min) / (i.max - i.min) * 100).toFixed(1) + '%'); });
    for (var n = 0; n < cells.length; n++) { cells[n].className = Math.floor((n + 1) * pd / cells.length) > Math.floor(n * pd / cells.length) ? 'on' : ''; }
    if (pup) { var want = d >= 5 ? 'cheer' : d >= 3 ? 'wave' : 'encourage'; var src = '/img/mascot/' + want + '.webp'; if (pup.getAttribute('src') !== src) pup.setAttribute('src', src); }
    if (costField) costField.hidden = !v;
    var tip = $('[data-tip]'); if (tip) tip.hidden = c > 0;
    msg.textContent = v ? root.getAttribute('data-msg-n').replace('{n}', num(Math.round(pd / v))) : root.getAttribute('data-msg-none');
    var bars = $('[data-bars]'), show = c > 0;
    bars.hidden = !show;
    if (show) {
      var top = Math.max(c, price);
      $('[data-bar="visit"]').style.transform = 'scaleX(' + (c / top).toFixed(3) + ')';
      $('[data-bar="prem"]').style.transform = 'scaleX(' + (price / top).toFixed(3) + ')';
      $('[data-val="visit"]').textContent = money(c);
    }
  }
  root.addEventListener('input', update); root.addEventListener('change', update);
  var fm = root.querySelector('form'); if (fm) fm.addEventListener('submit', function (e) { e.preventDefault(); });
  update();
})();
