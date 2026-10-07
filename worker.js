// bothinobody.com — sirve el sitio estático y una sola ruta dinámica:
// /api/substack → últimas publicaciones de bothinobody.substack.com (caché 30 min).
const FEED = 'https://bothinobody.substack.com/feed';

function tag(item, name) {
  const m = item.match(new RegExp('<' + name + '[^>]*>(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?</' + name + '>'));
  return m ? m[1].trim() : '';
}

async function substack(request, ctx) {
  const cache = caches.default;
  const key = new Request(new URL('/api/substack', request.url).toString());
  const hit = await cache.match(key);
  if (hit) return hit;

  let posts = [];
  try {
    const r = await fetch(FEED, { headers: { 'User-Agent': 'bothinobody.com' } });
    if (r.ok) {
      const xml = await r.text();
      posts = [...xml.matchAll(/<item>([\s\S]*?)<\/item>/g)].slice(0, 6).map(m => ({
        title: tag(m[1], 'title'),
        link: tag(m[1], 'link'),
        date: tag(m[1], 'pubDate'),
        description: tag(m[1], 'description'),
      })).filter(p => p.title && p.link.startsWith('https://'));
    }
  } catch (e) { /* sin feed: lista vacía, la página conserva su respaldo */ }

  const res = new Response(JSON.stringify({ posts }), {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': posts.length ? 'public, max-age=1800' : 'no-store',
    },
  });
  if (posts.length) ctx.waitUntil(cache.put(key, res.clone()));
  return res;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/api/substack') return substack(request, ctx);
    return env.ASSETS.fetch(request);
  },
};
