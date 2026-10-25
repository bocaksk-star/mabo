# Builds the extra pages of mabodigital.dev: service pages, case studies and privacy policy, in EN and SK.
import os, json, datetime, html
from bs4 import BeautifulSoup
from content import SERVICES, CASES, CASE_TEXT, PRIVACY, TERMS, UI, HUMAN, PROFILES, APP, PLAYSTORE_URL

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
  <footer class="sitefoot"><span>{E(u['footer_line'])} · <a href="mailto:hello@mabodigital.dev">hello@mabodigital.dev</a></span><span><a href="{u['priv_path']}">{E(u['footer_priv'])}</a> · <a href="{u['terms_path']}">{E(u['footer_terms'])}</a> · © 2026</span></footer>
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
            link = 'https://dominer.sk'
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
    others = ''.join(f'<a href="{case_path(o, lang)}"><img src="/logos/{o["logo"]}.png" alt="" width="22" height="22">{E(o["name"])}</a>' for o in CASES if o is not c)
    inner = f'''  {crumbs(lang, [(u['home'] + '#work', u['back']), (None, c['name'])])}
  <section class="hero">
    <p class="eyebrow">{E(u['case_eyebrow'])} · {E(c['url'].replace('https://', ''))}</p>
    <div class="case-head"><img src="/logos/{c['logo']}.png" alt="{E(c['name'])} logo" width="64" height="64"><h1>{E(title)}</h1></div>
    <p class="lede">{E(intro)}</p>
    <div class="actions"><a class="btn" href="{c['url']}" target="_blank" rel="noopener">{E(u['visit'])} {E(c['url'].replace('https://', ''))} ↗</a></div>
  </section>
  <section class="blk"><h2>{E(u['built'])}</h2><p>{E(desc_p)}</p><ul class="ticks">{''.join(f'<li>{E(f)}</li>' for f in feats)}</ul><ul class="tags">{''.join(f'<li>{E(t)}</li>' for t in tags)}</ul></section>
  <section class="blk"><h2>{E(u['results'])}</h2><p>{E(result)}</p><p class="period">{E(u['period'])}: {fmt_date(start, lang)} – {fmt_date(end, lang)} · {c['days']} {u['days']}</p>{kpis}{chart_svg(c, lang)}<p class="src" style="font-family:var(--mono);font-size:12.5px;color:var(--muted);margin:0">{E(u['src'])}</p></section>
{callout(lang)}
  <section class="blk"><h2>{E(u['more'])}</h2><div class="morelist">{others}</div></section>'''
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": title, "description": intro, "inLanguage": lang, "url": SITE + path, "author": {"@id": SITE + "/#marian"}, "publisher": {"@id": SITE + "/#business"},
         "image": SITE + f'/logos/{c["logo"]}.png', "datePublished": "2026-10-08", "about": {"@type": "WebSite", "name": c['name'], "url": c['url']}},
        bc_ld(lang, [(u['back'], SITE + u['home'] + '#work'), (c['name'], SITE + path)])]}
    return path, head(lang, path, alt, f'{c["name"]}: {"prípadová štúdia" if lang=="sk" else "case study"} | MaBo Digital', result, font, style, ld) + shell(lang, alt, inner)

def privacy_page(lang, font, style, DOC=None):
    DOC = DOC or PRIVACY
    d = DOC[lang]; alt = DOC['sk' if lang == 'en' else 'en']['path']
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
    for lang in ('en', 'sk'):
        out.append(privacy_page(lang, font, style, TERMS))
    pairs.append((TERMS['en']['path'], TERMS['sk']['path']))
    for lang in ('en', 'sk'):
        out.append(human_page(lang, font, style))
    pairs.append((HUMAN['en']['path'], HUMAN['sk']['path']))
    for lang in ('en', 'sk'):
        out.append(app_page(lang, font, style))
    pairs.append((APP['en']['path'], APP['sk']['path']))
    for path, doc in out:
        d = os.path.join(root, path.strip('/'))
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(doc)
    return pairs


HUMAN_CSS = """
.captcha{display:flex;align-items:center;gap:16px;align-self:flex-start;border:1.5px solid var(--line);border-radius:8px;background:var(--surface);padding:14px 22px 14px 16px;max-width:100%}
.captcha button{width:30px;height:30px;flex:none;border:2px solid var(--muted);border-radius:4px;background:var(--bg);cursor:pointer;display:grid;place-items:center;padding:0}
.captcha button:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.captcha .lbl{font-size:16px}
.captcha .spin{width:26px;height:26px;border-radius:50%;border:3px solid var(--line);border-top-color:var(--accent);animation:spin .8s linear infinite}
.captcha .tick{width:30px;height:30px}
.captcha .tick path{fill:none;stroke:var(--live);stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:40;stroke-dashoffset:40;animation:draw .4s ease-out forwards}
.captcha .mark{margin-left:auto;padding-left:24px;display:flex;flex-direction:column;align-items:center;gap:2px;font-family:var(--mono);font-size:10px;color:var(--muted)}
.captcha .mark svg{width:28px;height:28px}
.verified{margin:0;font-family:var(--mono);font-size:14px;color:var(--live)}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes draw{to{stroke-dashoffset:0}}
@media (prefers-reduced-motion:reduce){.captcha .spin{animation:none}.captcha .tick path{animation:none;stroke-dashoffset:0}}
.facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px 32px;margin:0;border-top:2px solid var(--ink);padding-top:22px}
.facts dt{font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.facts dd{margin:4px 0 0;font-size:17px;font-weight:600;overflow-wrap:anywhere}
.profiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:24px}
.pcard{position:relative;display:flex;flex-direction:column;border:1.5px solid var(--line);border-radius:16px;overflow:hidden;background:var(--surface);text-decoration:none;color:var(--ink);transition:transform .15s ease,border-color .15s ease}
.pcard:hover{transform:translateY(-3px);border-color:var(--pc)}
.pcard:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.pcard .band{height:72px;background:var(--pc);position:relative}
.pcard .glyph{position:absolute;right:14px;top:12px;font-family:var(--display);font-weight:800;font-size:22px;color:#FFFFFF;line-height:1}
.pcard .ava{width:76px;height:76px;border-radius:50%;margin:-38px 0 0 20px;border:4px solid var(--surface);background:var(--bg);display:grid;place-items:center;overflow:hidden;position:relative}
.pcard .ava img{width:100%;height:100%;object-fit:cover}
.pcard .ava svg{width:52px;height:52px}
.pcard .body{display:flex;flex-direction:column;gap:6px;padding:12px 20px 20px}
.pcard .net{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.pcard b{font-family:var(--display);font-size:1.3rem}
.pcard .handle{font-family:var(--mono);font-size:13px;color:var(--muted);overflow-wrap:anywhere}
.pcard .line{margin:4px 0 8px;font-size:15.5px}
.pcard .go{margin-top:auto;align-self:flex-start;font-family:var(--mono);font-size:13px;font-weight:700;padding:9px 13px;border-radius:6px;background:var(--pc);color:#FFFFFF}
.pcard.soon{opacity:.55;border-style:dashed;cursor:default}
.pcard.soon:hover{transform:none;border-color:var(--line)}
.pcard.soon .line{font-family:var(--mono);font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:0}
.soon{margin:0;font-family:var(--mono);font-size:13px;color:var(--muted)}
.ava-zoom{position:absolute;right:-2px;bottom:-2px;width:24px;height:24px;border-radius:50%;background:var(--pc);border:2px solid var(--surface);display:grid;place-items:center;color:#FFFFFF;cursor:pointer;padding:0;z-index:2}
.ava-zoom svg{width:13px;height:13px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round}
.ava-zoom:hover{filter:brightness(1.1)}
.lightbox{position:fixed;inset:0;background:rgba(6,9,16,.86);display:grid;place-items:center;z-index:200;padding:40px 20px}
.lightbox img{max-width:min(90vw,480px);max-height:80vh;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.lb-close{position:absolute;top:18px;right:22px;width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,.12);color:#FFFFFF;border:1px solid rgba(255,255,255,.3);font-size:24px;line-height:1;cursor:pointer}
.lb-close:hover{background:rgba(255,255,255,.22)}
@media (max-width:720px){.facts{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
@media (prefers-reduced-motion:reduce){.pcard,.pcard:hover{transition:none;transform:none}}
"""

def human_page(lang, font, style):
    d = HUMAN[lang]; alt = HUMAN['sk' if lang == 'en' else 'en']['path']
    facts = ''.join(f'<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k, v in d['facts'])
    big = MARK.replace('width="32" height="32"', 'width="52" height="52"')
    cards = ''
    has_soon = False
    has_photo = False
    for pr in PROFILES:
        if pr.get('soon'):
            has_soon = True
            cards += (f'<div class="pcard soon" style="--pc:{pr["color"]}">'
                      f'<span class="band"><span class="glyph" aria-hidden="true">{pr["glyph"]}</span></span><span class="ava">{big}</span>'
                      f'<span class="body"><span class="net">{E(pr["name"])}</span><b>Marian Boledovic</b>'
                      f'<span class="line">{E(pr["line"][lang])}</span></span></div>')
            continue
        if pr.get('photo'):
            has_photo = True
            ava = (f'<img src="/{pr["photo"]}" alt="Marian Boledovic" width="76" height="76">'
                   f'<button type="button" class="ava-zoom" data-full="/{pr["photo"]}" aria-label="{E(d["photo_open"])}">'
                   f'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/><path d="M11 8v6M8 11h6"/></svg></button>')
        else:
            ava = big
        cards += (f'<a class="pcard" href="{pr["url"]}" target="_blank" rel="noopener me" style="--pc:{pr["color"]}">'
                  f'<span class="band"><span class="glyph" aria-hidden="true">{pr["glyph"]}</span></span><span class="ava">{ava}</span>'
                  f'<span class="body"><span class="net">{E(pr["name"])}</span><b>Marian Boledovic</b><span class="handle">{E(pr["handle"])}</span>'
                  f'<span class="line">{E(pr["line"][lang])}</span><span class="go">{E(d["open"])} ↗</span></span></a>')
    lightbox = (f'<div class="lightbox" id="photobox" hidden><button type="button" class="lb-close" id="lb-close" aria-label="{E(d["photo_close"])}">&times;</button>'
                f'<img id="lb-img" src="" alt="Marian Boledovic"></div>') if has_photo else ''
    inner = f'''  {crumbs(lang, [(None, d['h1'])])}
  <section class="hero">
    <p class="eyebrow">{E(d['eyebrow'])}</p>
    <h1>{E(d['h1'])}</h1>
    <p class="lede">{E(d['lede'])}</p>
    <div class="captcha"><button type="button" id="cap" aria-label="{E(d['check'])}" aria-pressed="false"></button><span class="lbl">{E(d['check'])}</span><span class="mark" aria-hidden="true">{MARK}MaBo</span></div>
    <p class="verified" id="cap-out" role="status" aria-live="polite" hidden>{E(d['verified'])}</p>
  </section>
  <section class="blk" style="max-width:none"><h2>{E(d['basics'])}</h2><dl class="facts">{facts}</dl></section>
  <section class="blk" style="max-width:none"><h2>{E(d['find'])}</h2><div class="profiles">{cards}</div>{'' if has_soon else f'<p class="soon">{E(d["soon"])}</p>'}</section>
{callout(lang, d['cta_t'], d['cta_p'])}
{lightbox}
<style>{HUMAN_CSS}</style>
<script>
(function(){{
  var b=document.getElementById('cap'), out=document.getElementById('cap-out'), done=false;
  var calm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  b.addEventListener('click',function(){{
    if(done) return; done=true; b.setAttribute('aria-pressed','true');
    b.innerHTML='<span class="spin" aria-hidden="true"></span>'; b.title={json.dumps(d['checking'])};
    setTimeout(function(){{ b.innerHTML='<svg class="tick" viewBox="0 0 30 30" aria-hidden="true"><path d="M6 16l6 6L24 9"/></svg>'; b.style.borderColor='transparent'; out.hidden=false; }}, calm?0:1100);
  }});
  var box=document.getElementById('photobox');
  if(box){{
    var lbImg=document.getElementById('lb-img'), lbClose=document.getElementById('lb-close');
    var openBox=function(src){{ lbImg.src=src; box.hidden=false; document.body.style.overflow='hidden'; lbClose.focus(); }};
    var closeBox=function(){{ box.hidden=true; lbImg.src=''; document.body.style.overflow=''; }};
    document.querySelectorAll('.ava-zoom').forEach(function(z){{
      z.addEventListener('click',function(e){{ e.preventDefault(); e.stopPropagation(); openBox(z.getAttribute('data-full')); }});
    }});
    lbClose.addEventListener('click',closeBox);
    box.addEventListener('click',function(e){{ if(e.target===box) closeBox(); }});
    document.addEventListener('keydown',function(e){{ if(e.key==='Escape'&&!box.hidden) closeBox(); }});
  }}
}})();
</script>'''
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ProfilePage", "url": SITE + d['path'], "inLanguage": lang, "name": d['h1'], "mainEntity": {"@id": SITE + "/#marian"}},
        bc_ld(lang, [(d['h1'], SITE + d['path'])])]}
    return d['path'], head(lang, d['path'], alt, d['title'], d['desc'], font, style, ld) + shell(lang, alt, inner)

APP_CSS = """
.apphero{position:relative;overflow:hidden;border-radius:22px;text-decoration:none;color:#fff;min-height:300px;display:flex;align-items:flex-end;background:#0a1120}
.apphero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:68% 50%}
.apphero .scrim{position:absolute;inset:0;background:linear-gradient(100deg,rgba(5,8,17,.99) 0%,rgba(5,8,17,.96) 34%,rgba(5,8,17,.72) 48%,rgba(5,8,17,.18) 64%,rgba(5,8,17,0) 72%)}
.apphero .content{position:relative;z-index:1;padding:32px 34px;display:flex;flex-direction:column;gap:13px;max-width:400px}
.apphero .brandrow{display:flex;align-items:center;gap:11px}
.apphero img.icon{width:42px;height:42px;border-radius:11px;box-shadow:0 4px 14px rgba(0,0,0,.4)}
.apphero .appname{font-family:var(--display);font-weight:700;font-size:15px;color:#D4DAEE}
.apphero .eyebrow{font-family:var(--mono);font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#7FE8C4;text-shadow:0 1px 12px rgba(0,0,0,.5)}
.apphero .title{font-family:var(--display);font-weight:800;font-size:clamp(26px,4.4vw,38px);letter-spacing:-.015em;line-height:1.06;text-shadow:0 3px 20px rgba(0,0,0,.65)}
.apphero .sub{font-family:var(--body);font-size:14.5px;color:#C9D1EA;line-height:1.55;max-width:36ch;text-shadow:0 2px 12px rgba(0,0,0,.6)}
.apphero .badge{margin-top:8px;display:block;width:150px;filter:drop-shadow(0 6px 16px rgba(0,0,0,.4))}
.apphero .badge img{width:100%;display:block}
@media (max-width:640px){
  .apphero{min-height:280px}
  .apphero img.bg{object-position:78% 50%}
  .apphero .scrim{background:linear-gradient(105deg,rgba(5,8,17,.99) 0%,rgba(5,8,17,.97) 48%,rgba(5,8,17,.75) 62%,rgba(5,8,17,.25) 78%,rgba(5,8,17,0) 92%)}
  .apphero .content{max-width:100%;padding:26px 22px}
}
.featgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;margin:0;border-top:2px solid var(--ink);padding-top:20px}
.featgrid > div{display:flex;flex-direction:column;gap:6px}
.featgrid b{font-family:var(--display);font-size:1.1rem}
.featgrid span{color:var(--muted);font-size:15px}
.shots{display:flex;gap:14px;overflow-x:auto;padding-bottom:4px;scroll-snap-type:x proximity}
.shots img{flex:none;width:168px;border-radius:16px;border:1px solid var(--line);scroll-snap-align:start}
.appinfo{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px 32px;margin:0;border-top:2px solid var(--ink);padding-top:20px}
.appinfo dt{font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.appinfo dd{margin:2px 0 0;font-size:16px;font-weight:600}
.note{font-size:14px;color:var(--muted);border-left:3px solid var(--line);padding-left:16px;margin:0}
@media (max-width:720px){.appinfo{grid-template-columns:minmax(0,1fr)}}
"""

def app_page(lang, font, style):
    d = APP[lang]; alt = APP['sk' if lang == 'en' else 'en']['path']; u = UI[lang]
    feats = ''.join(f'<div><b>{E(t)}</b><span>{E(x)}</span></div>' for t, x in d['features'])
    shots = ''.join(f'<img src="/logos/cga-shot-{i}.jpg" alt="" width="168" loading="lazy">' for i in (1, 2, 3))
    info = ''.join(f'<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k, v in d['info'])
    badge = f'<span class="badge"><img src="/logos/google-play-badge.png" alt="Get it on Google Play"></span>'
    inner = f'''  {crumbs(lang, [(None, d['h1'])])}
  <a class="apphero" href="{PLAYSTORE_URL}" target="_blank" rel="noopener">
    <img class="bg" src="/logos/cga-hero-banner.jpg" alt="">
    <span class="scrim"></span>
    <span class="content">
      <span class="brandrow"><img class="icon" src="/logos/cga-game-icon.png" alt="">
        <span class="appname">{E(d['h1'])}</span></span>
      <span class="eyebrow">{E(d['eyebrow'])}</span>
      <span class="title">{E(d['h1'])}</span>
      <span class="sub">{E(d['lede'])}</span>
      {badge}
    </span>
  </a>
  <section class="blk" style="max-width:none"><h2>{E(d['features_h'])}</h2><div class="featgrid">{feats}</div></section>
  <section class="blk" style="max-width:none"><h2>{E(d['shots_h'])}</h2><div class="shots">{shots}</div></section>
  <section class="blk" style="max-width:none"><h2>{E(d['info_h'])}</h2><dl class="appinfo">{info}</dl><p class="note">{E(d['note_h'])}: {E(d['note'])}</p></section>
{callout(lang, d['cta_t'], d['cta_p'])}
<style>{APP_CSS}</style>'''
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "MobileApplication", "name": d['h1'], "description": d['desc'], "operatingSystem": "ANDROID", "applicationCategory": "GameApplication",
         "url": SITE + d['path'], "installUrl": PLAYSTORE_URL, "author": {"@id": SITE + "/#business"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}},
        bc_ld(lang, [(d['h1'], SITE + d['path'])])]}
    return d['path'], head(lang, d['path'], alt, d['title'], d['desc'], font, style, ld) + shell(lang, alt, inner)
