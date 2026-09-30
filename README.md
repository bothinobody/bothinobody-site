# bothinobody.com

Sitio de Bothi Nobody: Guías y Palancas (2.ª edición), la saga, soundtrack y apoyo.

Sitio estático: `index.html` + `img/`. Sin build.
Se publica como Cloudflare Worker con assets estáticos (`wrangler.jsonc`),
conectado a este repo: cada push a `main` se despliega solo.
