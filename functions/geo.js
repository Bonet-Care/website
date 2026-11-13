// Cloudflare Pages Function: GET /geo
// Returns the visitor's country and region as Cloudflare already knows them. It stores nothing and logs nothing,
// and it never returns an IP address. js/consent.js turns the answer into "strict" or "open".
export const onRequestGet = ({ request }) => {
  const cf = request.cf || {};
  const country = typeof cf.country === 'string' && /^[A-Z0-9]{2}$/.test(cf.country) ? cf.country : 'XX';
  const region = typeof cf.regionCode === 'string' && /^[A-Za-z0-9-]{1,6}$/.test(cf.regionCode) ? cf.regionCode : null;
  return new Response(JSON.stringify({ country, region }), {
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'private, no-store',
      'x-content-type-options': 'nosniff',
    },
  });
};
