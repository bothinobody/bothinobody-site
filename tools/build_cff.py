#!/usr/bin/env python3
"""Genera la Biblioteca CFF (/cff/ y /cff/wp-0XX/) a partir de _data/FICHAS_CFF.md.

Reglas (de Claudio Substack, 13-oct-2026):
  - Direcciones fijas: /cff/ y /cff/wp-0XX/ (minúsculas, 3 dígitos, barra final).
  - "Copiar cita" copia la línea Cita tal cual, sin reformatear.
  - PDFs con su nombre original en /cff/pdf/. Versiones viejas se archivan (no se borran):
    agrégalas a _data/archivo.json para que aparezcan en "Versiones anteriores".
  - Título en inglés solo si hay PDF en inglés; si no, "English: coming".
  - Substack: solo si la ficha trae una URL real (https://...).
  - Nada que no venga en una ficha.
Uso: python3 tools/build_cff.py
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHAS = os.path.join(ROOT, '_data', 'FICHAS_CFF.md')
ARCHIVO = os.path.join(ROOT, '_data', 'archivo.json')  # {"CFF-WP-004": [{"archivo": "...pdf", "version": "ES v1 · 01-05-26"}]}
OUT = os.path.join(ROOT, 'cff')
e = lambda s: html.escape(s, quote=True)


def parse():
    text = open(FICHAS, encoding='utf-8').read()
    fichas = []
    for block in re.findall(r'```\s*\nFICHA CFF\n(.*?)```', text, re.S):
        f = {}
        for line in block.strip().splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                f[k.strip()] = v.strip()
        fichas.append(f)
    return fichas


def files(f):
    out = {}
    for name in [x.strip() for x in f['Archivo'].split('|')]:
        lang = name[:2]
        path = os.path.join(OUT, 'pdf', name)
        if not os.path.exists(path):
            sys.exit(f'Falta el PDF {name} de {f["ID"]}')
        out[lang] = {'name': name, 'kb': round(os.path.getsize(path) / 1024)}
    vers = {}
    for part in [x.strip() for x in f['Versión'].split('|')]:
        vers[part[:2]] = part
    return out, vers


HEAD = '''<!doctype html>
<html lang="es" data-lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="https://bothinobody.com/img/og-gyp.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gloock&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/cff/cff.css">
</head>
<body>
<header class="top">
  <a class="home" href="/">Bothi Nobody</a>
  <nav><a href="/cff/"><span lang="es">Biblioteca CFF</span><span lang="en">CFF Library</span></a></nav>
  <div class="lang" role="group" aria-label="Idioma / Language">
    <button type="button" id="b-es" data-set="es" aria-pressed="true">ES</button>
    <button type="button" id="b-en" data-set="en" aria-pressed="false">EN</button>
  </div>
</header>
<main>
'''

FOOT = '''</main>
<footer>
  <p><span lang="es">Textos bajo licencia</span><span lang="en">Texts licensed under</span> <a href="https://creativecommons.org/licenses/by-nc/4.0/deed.es">CC BY-NC 4.0</a>. <span lang="es">Uso comercial:</span><span lang="en">Commercial use:</span> <code data-u="aloh" data-d="moc.ydobonihtob">hola [at] bothinobody.com</code></p>
  <p>Cognitive Friction Fellowship · Rodrigo Flores-Morton (Bothi Nobody) <span lang="es">y la Tribu Agrajag</span><span lang="en">and the Agrajag Tribe</span></p>
</footer>
<script src="/cff/cff.js"></script>
</body>
</html>
'''


def tipo_badge(t):
    if t == 'Tratado':
        return '<span class="badge tratado"><span lang="es">Tratado</span><span lang="en">Treatise</span></span>'
    return '<span class="badge"><span lang="es">Paper</span><span lang="en">Paper</span></span>'


def num(fid):
    return fid.split('-')[-1]


def has_real(url):
    return url.startswith('https://')


def paper_page(f, archivo):
    fl, vers = files(f)
    n = num(f['ID'])
    slug = f'wp-{n}'
    en_title = f['Título EN'] if 'EN' in fl else None
    canon = f'https://bothinobody.com/cff/{slug}/'
    h = HEAD.format(title=e(f"{f['ID']} · {f['Título ES']}"), desc=e(f['Resumen']), canon=canon)
    h += f'''  <p class="crumb"><a href="/cff/">← <span lang="es">Biblioteca CFF</span><span lang="en">CFF Library</span></a></p>
  <article class="paper">
    <div class="meta-top"><span class="id">{e(f['ID'])}</span>{tipo_badge(f['Tipo'])}</div>
    <h1>{e(f['Título ES'])}</h1>
'''
    if en_title:
        h += f'    <p class="en-title">{e(en_title)}</p>\n'
    else:
        h += '    <p class="en-title muted">English: coming</p>\n'
    h += f'    <p class="resumen">{e(f["Resumen"])}</p>\n'
    h += '    <div class="downloads">\n'
    labels = {'ES': ('Español', 'Spanish'), 'EN': ('English', 'English')}
    for lang in ('ES', 'EN'):
        if lang in fl:
            x = fl[lang]
            h += (f'      <a class="dl" href="/cff/pdf/{e(x["name"])}" download>'
                  f'<b>PDF · {labels[lang][0]}</b><span>{e(vers.get(lang, ""))} · {x["kb"]} KB</span></a>\n')
    h += '    </div>\n'
    if has_real(f.get('Substack', '')):
        h += f'    <p><a href="{e(f["Substack"])}"><span lang="es">Leer en Substack →</span><span lang="en">Read on Substack →</span></a></p>\n'
    h += f'''    <section class="cita">
      <h2><span lang="es">Cómo citar</span><span lang="en">How to cite</span></h2>
      <p class="cita-text" id="cita">{e(f['Cita'])}</p>
      <button type="button" class="copy" data-copy="cita"><span lang="es">Copiar cita</span><span lang="en">Copy citation</span></button>
    </section>
'''
    old = archivo.get(f['ID'], [])
    if old:
        h += '    <section class="archive"><h2><span lang="es">Versiones anteriores</span><span lang="en">Earlier versions</span></h2><ul>\n'
        for o in old:
            h += f'      <li><a href="/cff/pdf/{e(o["archivo"])}">{e(o["version"])}</a></li>\n'
        h += '    </ul></section>\n'
    h += '  </article>\n' + FOOT
    os.makedirs(os.path.join(OUT, slug), exist_ok=True)
    open(os.path.join(OUT, slug, 'index.html'), 'w', encoding='utf-8').write(h)
    return slug, fl


def catalog(fichas, info):
    h = HEAD.format(title='Biblioteca CFF · Cognitive Friction Fellowship',
                    desc='Working papers y tratado de la Cognitive Friction Fellowship. PDFs descargables, versiones y citas.',
                    canon='https://bothinobody.com/cff/')
    h += f'''  <section class="intro">
    <span class="tag">[[Bothi]]</span>
    <h1><span lang="es">Biblioteca CFF</span><span lang="en">CFF Library</span></h1>
    <p><span lang="es">Los papers y el tratado de la Cognitive Friction Fellowship, escritos entre un humano y una tribu de IAs. Fricción intelectual antes que halagos.</span><span lang="en">The working papers and the treatise of the Cognitive Friction Fellowship, written by one human with a tribe of AIs. Intellectual friction over flattery.</span></p>
    <p class="count">{len(fichas)} <span lang="es">documentos</span><span lang="en">documents</span> · {sum(len(v) for v in info.values())} PDF</p>
  </section>
  <ol class="catalog">
'''
    for f in fichas:
        slug = f'wp-{num(f["ID"])}'
        langs = ' · '.join(sorted(info[f['ID']].keys(), key=lambda x: x != 'ES'))
        cls = ' class="is-tratado"' if f['Tipo'] == 'Tratado' else ''
        h += (f'    <li{cls}><a href="/cff/{slug}/">'
              f'<span class="row1"><span class="id">{e(f["ID"])}</span>{tipo_badge(f["Tipo"])}<span class="langs">{langs}</span></span>'
              f'<span class="t">{e(f["Título ES"])}</span>'
              f'<span class="r">{e(f["Resumen"])}</span></a></li>\n')
    h += '  </ol>\n' + FOOT
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(h)


def main():
    fichas = parse()
    archivo = json.load(open(ARCHIVO, encoding='utf-8')) if os.path.exists(ARCHIVO) else {}
    info = {}
    for f in fichas:
        _, fl = paper_page(f, archivo)
        info[f['ID']] = fl
    catalog(fichas, info)
    print(f'{len(fichas)} fichas, {sum(len(v) for v in info.values())} PDFs')


if __name__ == '__main__':
    main()
