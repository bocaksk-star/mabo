# Builds the extra pages of mabodigital.dev: service pages, case studies and privacy policy, in EN and SK.
import os, json, datetime, html
from bs4 import BeautifulSoup
from content import SERVICES, CASES, CASE_TEXT, PRIVACY, UI

SITE = 'https://mabodigital.dev'
E = html.escape
MARK = '<svg viewBox="0 0 64 64" width="32" height="32" aria-hidden="true"><rect width="64" height="64" rx="15" fill="#1B3FD0"/><polyline points="13,45 13,20 26,34 39,20 39,45" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/><circle cx="50" cy="44.5" r="4" fill="#FFB020"/></svg>'

EXTRA_CSS = '''
.sub .wrap{gap:64px}
.crumbs{font-family:var(--mono);font-size:12.5px;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px}
.crumbs a{color:var(--muted)}
.sub h1{font-size:clamp(2.2rem,6.5vw,4.2rem)}
.sub .hero{gap:22px}
.blk{display:flex;flex-direction:column;gap:20px;max-width:820px}
.blk p{margin:0;max-width:68ch}
.ticks{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 32px}
.ticks li{padding-left:22px;position:relative}
.ticks li::before{content:"";position:absolute;left:0;top:.55em;width:10px;height:6px;border-left:2px solid var(--accent);border-bottom:2px solid var(--accent);transform:rotate(-45deg)}
.steps{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:20px;counter-reset:st;border-top:2px solid var(--ink);padding-top:20px}
.steps li{counter-increment:st;display:flex;flex-direction:column;gap:6px}
.steps li::before{content:counter(st,decimal-leading-zero);font-family:var(--mono);font-size:12px;color:var(--accent);font-weight:700}
.steps b{font-family:var(--display);font-size:1.2rem}
.steps span{color:var(--muted);font-size:15.5px}
.faq{display:flex;flex-direction:column;border-top:2px solid var(--ink)}
.faq details{border-bottom:1px solid var(--line);padding:16px 0}
.faq summary{cursor:pointer;font-weight:600;font-size:17px;list-style:none;display:flex;justify-content:space-between;gap:16px}
.faq summary::after{content:"+";font-family:var(--mono);color:var(--accent);font-size:20px;line-height:1}
.faq details[open] summary::after{content:"–"}
.faq details p{margin:10px 0 0;color:var(--muted);max-width:68ch}
.callout{border:1.5px solid var(--line);border-radius:12px;padding:26px;display:flex;flex-direction:column;gap:14px;background:var(--surface)}
.callout h2{font-size:clamp(1.4rem,3.4vw,2rem)}
.callout p{margin:0;color:var(--muted)}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin:0}
.kpis dt{font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.kpis dd{margin:0;font-family:var(--display);font-weight:800;font-size:2.2rem;line-height:1.1;font-variant-numeric:tabular-nums}
.case-head{display:flex;align-items:center;gap:16px}
.case-head img{width:64px;height:64px;border-radius:14px}
.more{margin:0;font-family:var(--mono);font-size:13.5px}
.morelist{display:flex;flex-wrap:wrap;gap:10px}
.morelist a{display:inline-flex;align-items:center;gap:8px;border:1.5px solid var(--line);border-radius:8px;padding:8px 12px;text-decoration:none;color:var(--ink);font-family:var(--mono);font-size:13px}
.morelist a:hover{border-color:var(--accent)}
.morelist img{width:22px;height:22px;border-radius:6px}
.legal h2{font-size:1.35rem}
.legal .blk{gap:12px}
.sitefoot{border-top:2px solid var(--ink);padding-top:22px;font-family:var(--mono);font-size:12.5px;color:var(--muted);display:flex;flex-wrap:wrap;gap:8px 24px;justify-content:space-between}
.sitefoot a{color:var(--muted)}
@media (max-width:720px){.ticks{grid-template-columns:minmax(0,1fr)}.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''

def fmt_date(d, lang):
    return f'{d.day}. {d.month}. {d.year}' if lang == 'sk' else d.strftime('%-d %b %Y')

def num(v, lang):
    s = f'{v:,}' if isinstance(v, int) else str(v)
    return s.replace(',', ' ').replace('.', ',') if lang == 'sk' else s

def head(lang, path, alt_path, title, desc, font, style, ld):
    en_p, sk_p = (path, alt_path) if lang == 'en' else (alt_path, path)
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{SITE}{path}">
<link rel="alternate" hreflang="en" href="{SITE}{en_p}">
<link rel="alternate" hreflang="sk" href="{SITE}{sk_p}">
<link rel="alternate" hreflang="x-default" href="{SITE}{en_p}">
<meta name="author" content="Marian Boledovic">
<meta name="theme-color" content="#1B3FD0">
<meta property="og:type" content="website">
<meta property="og:site_name" content="MaBo Digital">
<meta property="og:locale" content="{'sk_SK' if lang=='sk' else 'en_US'}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{font}<style>*,*::before,*::after{{box-sizing:border-box}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{style}
<style>{EXTRA_CSS}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
'''

def shell(lang, alt_path, inner):
    u = UI[lang]
    nav = ''.join(f'<a href="{h}">{E(t)}</a>' for h, t in u['nav'])
    if lang == 'en':
        sw = f'<a id="lang-sk" href="{alt_path}" hreflang="sk" lang="sk">SVK</a><a id="lang-en" href="#" aria-current="page">ENG</a>'
    else:
        sw = f'<a id="lang-sk" href="#" aria-current="page">SVK</a><a id="lang-en" href="{alt_path}" hreflang="en" lang="en">ENG</a>'
    return f'''<body class="sub">
<div class="wrap" id="top">
  <header class="top">
    <a class="brand" href="{u['home']}" aria-label="MaBo Digital">{MARK}<span><b>MaBo</b> Digital</span></a>
    <nav aria-label="{'Sekcie' if lang=='sk' else 'Sections'}">{nav}<span class="lang" role="group" aria-label="Language / Jazyk">{sw}</span></nav>
  </header>
{inner}
  <footer class="sitefoot"><span>{E(u['footer_line'])} · <a href="mailto:hello@mabodigital.dev">hello@mabodigital.dev</a></span><span><a href="{u['priv_path']}">{E(u['footer_priv'])}</a> · © 2026</span></footer>
</div>
</body>
</html>
'''

def crumbs(lang, items):
    home = UI[lang]['home']
    parts = [f'<a href="{home}">MaBo Digital</a>'] + [f'<a href="{h}">{E(t)}</a>' if h else f'<span>{E(t)}</span>' for h, t in items]
    return '<nav class="crumbs" aria-label="Breadcrumb">' + '<span aria-hidden="true">/</span>'.join(parts) + '</nav>'

def bc_ld(lang, items):
    home = UI[lang]['home']
    all_items = [('MaBo Digital', SITE + home)] + items
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(all_items)]}

def callout(lang, title=None, text=None, cta=None):
    u = UI[lang]
    return f'''  <section class="callout">
    <h2>{E(title or u['similar'])}</h2>
    <p>{E(text or u['similar_p'])}</p>
    <div class="actions"><a class="btn primary" href="{u['home']}#contact">{E(cta or u['contact_cta'])}</a></div>
  </section>'''

def service_page(key, lang, font, style):
    d = SERVICES[key][lang]; alt = SERVICES[key]['sk' if lang == 'en' else 'en']['path']
    secs = []
    for title, kind, body in d['sections']:
        if kind == 'list':
            inner = '<ul class="ticks">' + ''.join(f'<li>{E(x)}</li>' for x in body) + '</ul>'
        elif kind == 'steps':
            inner = '<ol class="steps">' + ''.join(f'<li><b>{E(a)}</b><span>{E(b)}</span></li>' for a, b in body) + '</ol>'
        else:
            link = 'https://domainer.bocak-sk.workers.dev'
            inner = f'<p>{E(body)}</p><p class="more"><a href="{link}" target="_blank" rel="noopener">{"Otvoriť Doménový Miner" if lang=="sk" else "Open Doménový Miner"} ↗</a></p>'
        secs.append(f'  <section class="blk"><h2>{E(title)}</h2>{inner}</section>')
    # proof: links to case studies
    proof_links = ''.join(f'<a href="{case_path(c, lang)}"><img src="/logos/{c["logo"]}.png" alt="" width="22" height="22">{E(c["name"])}</a>' for c in CASES)
    secs.append(f'  <section class="blk"><h2>{"Výsledky" if lang=="sk" else "Proof"}</h2><p>{E(d["proof"])}</p><div class="morelist">{proof_links}</div></section>')
    faq = '<div class="faq">' + ''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in d['faq']) + '</div>'
    secs.append(f'  <section class="blk"><h2>{E(UI[lang]["faq"])}</h2>{faq}</section>')
    inner = f'''  {crumbs(lang, [(None, d['h1'])])}
  <section class="hero">
    <p class="eyebrow">{E(d['eyebrow'])}</p>
    <h1>{E(d['h1'])}</h1>
    <p class="lede">{E(d['lede'])}</p>
    <div class="actions"><a class="btn primary" href="{UI[lang]['home']}#contact">{E(d['cta'])}</a></div>
  </section>
''' + '\n'.join(secs) + '\n' + callout(lang, cta=d['cta'])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "name": d['h1'], "description": d['desc'], "url": SITE + d['path'], "provider": {"@id": SITE + "/#business"}, "areaServed": ["SK", "CZ", "Worldwide"], "inLanguage": lang},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d['faq']]},
        bc_ld(lang, [(d['h1'], SITE + d['path'])])]}
    return d['path'], head(lang, d['path'], alt, d['title'], d['desc'], font, style, ld) + shell(lang, alt, inner)

def case_path(c, lang):
    return f'/work/{c["slug"]}/' if lang == 'en' else f'/sk/projekty/{c["slug"]}/'

def chart_svg(c, lang):
    W, H, L, R, T, B = 640, 200, 44, 14, 12, 26
    data = c['series']; n = len(data); mx = max(data)
    step = 10 ** (len(str(mx)) - 1); top = ((mx + step - 1) // step) * step if mx > 0 else 10
    x = lambda i: L + i * (W - L - R) / (n - 1)
    y = lambda v: T + (1 - v / top) * (H - T - B)
    pts = ' '.join(f'{x(i):.1f},{y(v):.1f}' for i, v in enumerate(data))
    start = datetime.date.fromisoformat(c['start']); end = start + datetime.timedelta(days=n - 1)
    grid = ''.join(f'<line class="grid" x1="{L}" x2="{W-R}" y1="{y(v):.1f}" y2="{y(v):.1f}"/><text x="{L-8}" y="{y(v)+4:.1f}" text-anchor="end">{num(int(v), lang)}</text>' for v in (0, top // 2, top))
    lab = f'<text x="{L}" y="{H-6}">{fmt_date(start, lang)}</text><text x="{W-R}" y="{H-6}" text-anchor="end">{fmt_date(end, lang)}</text>'
    area = f'<polygon class="ar" points="{x(0):.1f},{y(0):.1f} {pts} {x(n-1):.1f},{y(0):.1f}"/>'
    return (f'<figure class="chart"><figcaption>{E(UI[lang]["perday"])}</figcaption>'
            f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{E(c["name"])}: {E(UI[lang]["perday"])}">{grid}{lab}{area}'
            f'<polyline class="ln" points="{pts}"/><circle class="dot" r="4.5" cx="{x(n-1):.1f}" cy="{y(data[-1]):.1f}"/></svg></figure>')

def case_page(c, lang, soup_en, soup_sk, font, style):
    u = UI[lang]; alt = case_path(c, 'sk' if lang == 'en' else 'en'); path = case_path(c, lang)
    title, intro, result = CASE_TEXT[lang][c['slug']]
    art = (soup_en if lang == 'en' else soup_sk).select_one(f'article#{c["art"]}')
    desc_p = art.select_one('.cols p').get_text(' ', strip=True)
    feats = [li.get_text(' ', strip=True) for li in art.select('.cols ul li')]
    tags = [li.get_text(' ', strip=True) for li in art.select('ul.tags li')]
    start = datetime.date.fromisoformat(c['start']); end = start + datetime.timedelta(days=c['days'] - 1)
    pct = ' %' if lang == 'sk' else '%'
    kpis = (f'<dl class="kpis"><div><dt>{u["imp"]}</dt><dd>{num(c["imp"], lang)}</dd></div><div><dt>{u["clk"]}</dt><dd>{num(c["clk"], lang)}</dd></div>'
            f'<div><dt>{u["ctr"]}</dt><dd>{num(c["ctr"], lang)}{pct}</dd></div><div><dt>{u["pos"]}</dt><dd>{num(c["pos"], lang)}</dd></div></dl>')
    qrows = ''.join(f'<tr><td>{E(q)}</td><td>{num(i, lang)}</td><td>{num(p, lang)}</td></tr>' for q, i, p in c['q'])
    qtable = f'<table class="q"><thead><tr><th>{u["query"]}</th><th>{u["imp"]}</th><th>{u["pos"]}</th></tr></thead><tbody>{qrows}</tbody></table>'
    others = ''.join(f'<a href="{case_path(o, lang)}"><img src="/logos/{o["logo"]}.png" alt="" width="22" height="22">{E(o["name"])}</a>' for o in CASES if o is not c)
    inner = f'''  {crumbs(lang, [(u['home'] + '#work', u['back']), (None, c['name'])])}
  <section class="hero">
    <p class="eyebrow">{E(u['case_eyebrow'])} · {E(c['url'].replace('https://', ''))}</p>
    <div class="case-head"><img src="/logos/{c['logo']}.png" alt="{E(c['name'])} logo" width="64" height="64"><h1>{E(title)}</h1></div>
    <p class="lede">{E(intro)}</p>
    <div class="actions"><a class="btn" href="{c['url']}" target="_blank" rel="noopener">{E(u['visit'])} {E(c['url'].replace('https://', ''))} ↗</a></div>
  </section>
  <section class="blk"><h2>{E(u['built'])}</h2><p>{E(desc_p)}</p><ul class="ticks">{''.join(f'<li>{E(f)}</li>' for f in feats)}</ul><ul class="tags">{''.join(f'<li>{E(t)}</li>' for t in tags)}</ul></section>
  <section class="blk"><h2>{E(u['results'])}</h2><p>{E(result)}</p><p class="period">{E(u['period'])}: {fmt_date(start, lang)} – {fmt_date(end, lang)} · {c['days']} {u['days']}</p>{kpis}{chart_svg(c, lang)}{qtable}<p class="src" style="font-family:var(--mono);font-size:12.5px;color:var(--muted);margin:0">{E(u['src'])}</p></section>
{callout(lang)}
  <section class="blk"><h2>{E(u['more'])}</h2><div class="morelist">{others}</div></section>'''
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": title, "description": intro, "inLanguage": lang, "url": SITE + path, "author": {"@id": SITE + "/#marian"}, "publisher": {"@id": SITE + "/#business"},
         "image": SITE + f'/logos/{c["logo"]}.png', "datePublished": "2026-10-08", "about": {"@type": "WebSite", "name": c['name'], "url": c['url']}},
        bc_ld(lang, [(u['back'], SITE + u['home'] + '#work'), (c['name'], SITE + path)])]}
    return path, head(lang, path, alt, f'{c["name"]}: {"prípadová štúdia" if lang=="sk" else "case study"} | MaBo Digital', result, font, style, ld) + shell(lang, alt, inner)

def privacy_page(lang, font, style):
    d = PRIVACY[lang]; alt = PRIVACY['sk' if lang == 'en' else 'en']['path']
    secs = ''.join(f'  <section class="blk"><h2>{E(t)}</h2>' + ''.join(f'<p>{E(p)}</p>' for p in ps) + '</section>\n' for t, ps in d['sections'])
    inner = f'''  {crumbs(lang, [(None, d['h1'])])}
  <section class="hero"><h1>{E(d['h1'])}</h1><p class="period" style="font-family:var(--mono);font-size:13px;color:var(--muted);margin:0">{E(d['updated'])}</p></section>
  <div class="legal" style="display:flex;flex-direction:column;gap:40px">
{secs}  </div>'''
    ld = {"@context": "https://schema.org", "@graph": [bc_ld(lang, [(d['h1'], SITE + d['path'])])]}
    return d['path'], head(lang, d['path'], alt, d['title'], d['desc'], font, style, ld) + shell(lang, alt, inner)

def build_all(root, font, style, soup_en, soup_sk):
    out = []
    pairs = []
    for key in SERVICES:
        for lang in ('en', 'sk'):
            out.append(service_page(key, lang, font, style))
        pairs.append((SERVICES[key]['en']['path'], SERVICES[key]['sk']['path']))
    for c in CASES:
        for lang in ('en', 'sk'):
            out.append(case_page(c, lang, soup_en, soup_sk, font, style))
        pairs.append((case_path(c, 'en'), case_path(c, 'sk')))
    for lang in ('en', 'sk'):
        out.append(privacy_page(lang, font, style))
    pairs.append((PRIVACY['en']['path'], PRIVACY['sk']['path']))
    for path, doc in out:
        d = os.path.join(root, path.strip('/'))
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(doc)
    return pairs
