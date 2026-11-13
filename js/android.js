/* Android early-access form. Only loaded when the android_early_access build flag is on. Posts JSON to the early-access function; needs its host in connect-src. */
(function () {
  'use strict';
  var f = document.querySelector('[data-android-form]'); if (!f) return;
  var ENDPOINT = 'https://iobqgteovbdgqbqzpirx.supabase.co/functions/v1/android-early-access';
  var status = f.querySelector('[data-android-status]');
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!f.reportValidity()) return;
    var d = new FormData(f);
    var body = { email: d.get('email'), name: d.get('name'), device: d.get('device'), language: d.get('language'), consent: !!d.get('consent'), website: d.get('website') || '' };
    status.textContent = 'Sending...';
    fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json(); })
      .then(function (j) { status.textContent = j.ok ? 'Thank you. The download button is below.' : (j.error || 'Something went wrong. Please try again.'); if (j.ok && j.download_url) { var a = document.createElement('a'); a.className = 'btn'; a.href = j.download_url; a.textContent = 'Download Bonet'; f.appendChild(a); } })
      .catch(function () { status.textContent = 'Something went wrong. Please try again.'; });
  });
})();
