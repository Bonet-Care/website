// Cloudflare Pages Function: GET /geo
// Returns the visitor's country and region as Cloudflare already knows them. It stores nothing and logs nothing,
// and it never returns an IP address. js/consent.js turns the answer into "strict" or "open".
export const onRequestGet = ({ request }) => {
  const cf = request.cf || {};
  const country = typeof cf.country === 'string' && /^[A-Z0-9]{2}$/.test(cf.country) ? cf.country : 'XX';
  const region = typeof cf.regionCode === 'string' && /^[A-Za-z0-9-]{1,6}$/.test(cf.regionCode) ? cf.regionCode : null;
  // The web app at app.bonet.care (and the native shells) read this to choose the analytics consent mode. No cookies are involved.
  const ALLOWED = ['https://app.bonet.care', 'https://localhost', 'capacitor://localhost'];
  const origin = request.headers.get('origin');
  const cors = origin && ALLOWED.includes(origin) ? { 'access-control-allow-origin': origin, vary: 'Origin' } : {};
  return new Response(JSON.stringify({ country, region }), {
    headers: {
      ...cors,
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'private, no-store',
      'x-content-type-options': 'nosniff',
    },
  });
};
