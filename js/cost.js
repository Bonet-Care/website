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
  var inp = {}, out = {};
  ['visits', 'cost', 'days', 'mins'].forEach(function (k) { inp[k] = $('[data-in="' + k + '"]'); });
  ['visits', 'cost', 'days', 'mins', 'pdays', 'mins_month', 'per_day', 'between'].forEach(function (k) { out[k] = $('[data-out="' + k + '"]'); });
  var last = {};
  function set(k, text) {
    var el = out[k]; if (!el || el.textContent === text) return;
    el.textContent = text;
    if (!reduce && el.closest('.cb-stat') && last[k] !== undefined) { el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop'); }
    last[k] = text;
  }
  function update() {
    var v = +inp.visits.value, c = +inp.cost.value, d = +inp.days.value, m = +inp.mins.value;
    var pd = Math.round(d * weeks);
    set('visits', num(v)); set('cost', c > 0 ? money(c) : notset); set('days', num(d)); set('mins', num(m));
    set('pdays', num(pd)); set('mins_month', num(pd * m)); set('per_day', money(price / pd, 2));
    set('between', v > 0 ? num(pd / v, pd % v === 0 ? 0 : 1) : '-');
    var bars = $('[data-bars]'), hint = $('[data-hint]'), show = c > 0;
    bars.hidden = !show; hint.hidden = show;
    if (show) {
      var top = Math.max(c, price);
      $('[data-bar="visit"]').style.transform = 'scaleX(' + (c / top).toFixed(3) + ')';
      $('[data-bar="prem"]').style.transform = 'scaleX(' + (price / top).toFixed(3) + ')';
      $('[data-val="visit"]').textContent = money(c);
    }
  }
  Object.keys(inp).forEach(function (k) { inp[k].addEventListener('input', update); });
  update();
})();
