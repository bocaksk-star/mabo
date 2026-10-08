import re, os, shutil, json, datetime, html as H
from bs4 import BeautifulSoup
import sys
sys.path.insert(0, S if 'S' in dir() else '/tmp/claude-0/-home-claude/05239927-44a8-535a-8f78-3af67eef1842/scratchpad/')
S='/tmp/claude-0/-home-claude/05239927-44a8-535a-8f78-3af67eef1842/scratchpad/'
R='/home/claude/mabo-digital-site/site/'
SITE='https://mabodigital.dev'
src=open(S+'marian-boledovic-portfolio.html',encoding='utf-8').read()
src=re.sub(r'<title>.*?</title>\n','',src,count=1)
font=re.search(r'<link rel="stylesheet" href="https://fonts.googleapis[^>]+>\n',src).group(0); src=src.replace(font,'',1)
style=src[:src.index('</style>')+8]; body=src[len(style):]
style+='\n<style>.lang a{display:inline-block;font-family:var(--mono);font-size:12.5px;font-weight:700;letter-spacing:.06em;padding:6px 11px;color:var(--ink);text-decoration:none}.lang a[aria-current="page"]{background:var(--ink);color:var(--bg)}</style>'

# static site: language buttons become real links, the page language comes from the URL
body=re.sub(r'<span class="lang"[^>]*>.*?</span>',
  '<span class="lang" role="group" aria-label="Language / Jazyk"><a id="lang-sk" href="/sk/" hreflang="sk" lang="sk">SVK</a><a id="lang-en" href="/" hreflang="en" lang="en">ENG</a></span>',body,count=1,flags=re.S)
old_init=re.search(r"  document\.querySelectorAll\('\.lang button'\).*?setLang\(start, false\);",body,re.S).group(0)
body=body.replace(old_init,"  setLang(document.documentElement.lang === 'sk' ? 'sk' : 'en', false);")
a="nodes.forEach(function(el){ el.setAttribute('data-en', el.innerHTML); });"; assert a in body
body=body.replace(a,"nodes.forEach(function(el){ if (!el.hasAttribute('data-en')) el.setAttribute('data-en', el.innerHTML); });")
body=body.replace('src="logos/','src="/logos/')
from content import CASES, UI as _UI
# links from service panels to the service pages
for pid, en_href, sk_href, en_t, sk_t in [('panel-web','/web-design/','/sk/tvorba-webov/','More about web design','Viac o tvorbe webov'),('panel-seo','/seo/','/sk/seo/','More about SEO services','Viac o SEO optimalizácii')]:
    i=body.index(f'id="{pid}"'); j=body.index('</ul>', body.index('<ul class="tags">', i))+5
    body=body[:j]+f'\n      <p class="more"><a href="{en_href}" data-sk-href="{sk_href}" data-sk="{sk_t} →">{en_t} →</a></p>'+body[j:]
# case study links in the project address bars
for c in CASES:
    a_=f'<article class="project" id="{c["art"]}">'; i=body.index(a_); j=body.index('</div>', body.index('<div class="bar">', i))
    body=body[:j]+f'<a class="case" href="/work/{c["slug"]}/" data-sk-href="/sk/projekty/{c["slug"]}/" data-sk="Prípadová štúdia">Case study</a>'+body[j:]
# footer: privacy link; form: consent note
a_='<span>© 2026</span></div>\n  </section>'; assert a_ in body
body=body.replace(a_,'<span><a href="/privacy/" data-sk-href="/sk/ochrana-sukromia/" data-sk="Ochrana súkromia">Privacy</a> · <a href="/terms/" data-sk-href="/sk/obchodne-podmienky/" data-sk="Obchodné podmienky">Terms</a> · © 2026</span></div>\n  </section>')
a_='<p class="fnote" id="f-note"></p>'; assert a_ in body
body=body.replace(a_,'<p class="fnote" id="f-note" data-sk="Údaje z formulára použijem len na odpoveď. Viac v &lt;a href=&quot;/sk/ochrana-sukromia/&quot;&gt;ochrane súkromia&lt;/a&gt;.">I use the details only to reply to you. See the <a href="/privacy/">privacy policy</a>.</p>')
style=style.replace('</style>','.foot a{color:var(--muted)}\n.bar a.case{font-weight:500;white-space:nowrap}\n.more{margin:0;font-family:var(--mono);font-size:13.5px}\n</style>',1)


ORG={"@context":"https://schema.org","@graph":[
 {"@type":"ProfessionalService","@id":SITE+"/#business","name":"MaBo Digital","url":SITE+"/","logo":SITE+"/icon-512.png","image":SITE+"/og-image.png",
  "description":"Website creation and SEO for businesses in Slovakia, Czechia and abroad.","email":"hello@mabodigital.dev",
  "address":{"@type":"PostalAddress","addressLocality":"Luka","addressCountry":"SK"},
  "areaServed":[{"@type":"Country","name":"Slovakia"},{"@type":"Country","name":"Czechia"}],
  "founder":{"@id":SITE+"/#marian"},"knowsAbout":["Web design","Website development","Search engine optimization","SEO audit","Keyword research","Technical SEO","SEO tools"],"knowsLanguage":["sk","cs","en","de"],
  "hasOfferCatalog":{"@type":"OfferCatalog","name":"Services","itemListElement":[
    {"@type":"Offer","itemOffered":{"@type":"Service","name":"Web design and website development","serviceType":"Web design","description":"Custom web design, website development, launch and maintenance of fast, responsive websites."}},
    {"@type":"Offer","itemOffered":{"@type":"Service","name":"SEO services","serviceType":"Search engine optimization","description":"SEO audits, keyword research, on-page and technical SEO and rank tracking, using our own SEO tools."}}]}},
 {"@type":"Person","@id":SITE+"/#marian","name":"Marian Boledovic","jobTitle":"Web developer and SEO specialist","worksFor":{"@id":SITE+"/#business"},
  "sameAs":["https://depesa.eu","https://animeslovakia.sk","https://bocak.sk","https://slangovnik.sk","https://gramabot.sk","https://cryptogaway.com"]},
 {"@type":"WebSite","@id":SITE+"/#website","url":SITE+"/","name":"MaBo Digital","publisher":{"@id":SITE+"/#business"},"inLanguage":["en","sk"]}]}
LD='<script type="application/ld+json">'+json.dumps(ORG,ensure_ascii=False)+'</script>'

META={
 'en':dict(kw='web design, website development, web developer Slovakia, website creation, responsive websites, landing pages, SEO services, SEO audit, keyword research, technical SEO, rank tracking, SEO tools',path='/',locale='en_US',alt='sk_SK',
   title='MaBo Digital | Web Design, Website Development & SEO',
   desc='Web design, website development and SEO services from Slovakia: fast websites, SEO audits, keyword research and our own SEO tools. Eight live projects.',
   ogt='MaBo Digital | Web Design and SEO',ogd='Websites and SEO, built and run from Slovakia.'),
 'sk':dict(kw='tvorba webových stránok, tvorba webu, webdizajn, web na mieru, responzívny web, SEO optimalizácia, SEO audit, analýza kľúčových slov, sledovanie pozícií, SEO nástroje',path='/sk/',locale='sk_SK',alt='en_US',
   title='MaBo Digital | Tvorba webových stránok a SEO optimalizácia',
   desc='Tvorba webových stránok na mieru a SEO optimalizácia: rýchle weby, SEO audit, analýza kľúčových slov a vlastné SEO nástroje. Osem živých projektov.',
   ogt='MaBo Digital | Tvorba webov a SEO',ogd='Weby a SEO, postavené a prevádzkované na Slovensku.')}

def head(l):
  m=META[l]; url=SITE+m['path']
  return f'''<!doctype html>
<html lang="{l}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{m['title']}</title>
<meta name="description" content="{m['desc']}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{SITE}/">
<link rel="alternate" hreflang="sk" href="{SITE}/sk/">
<link rel="alternate" hreflang="x-default" href="{SITE}/">
<meta name="keywords" content="{m['kw']}">
<meta name="author" content="Marian Boledovic">
<meta name="theme-color" content="#1B3FD0">
<meta property="og:type" content="website">
<meta property="og:site_name" content="MaBo Digital">
<meta property="og:locale" content="{m['locale']}">
<meta property="og:locale:alternate" content="{m['alt']}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{m['ogt']}">
<meta property="og:description" content="{m['ogd']}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="MaBo Digital logo and name">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{font}<style>*,*::before,*::after{{box-sizing:border-box}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{style}
{LD}
</head>
<body>
'''

en=head('en')+body+'\n</body>\n</html>\n'
# Slovak page: put the Slovak text into the HTML itself so search engines can read it
soup=BeautifulSoup(body,'html.parser')
n=0
for el in soup.select('[data-sk]'):
  el['data-en']=el.decode_contents()
  el.clear(); el.append(BeautifulSoup(el['data-sk'],'html.parser')); n+=1
for el in soup.select('[data-sk-href]'):
  el['href']=el['data-sk-href']
for a in soup.select('.lang a'):
  if a.get('id')=='lang-sk': a['aria-current']='page'
skbody=str(soup)
en=en.replace('<a id="lang-en" href="/" hreflang="en" lang="en">','<a id="lang-en" href="/" hreflang="en" lang="en" aria-current="page">')
sk=head('sk')+skbody+'\n</body>\n</html>\n'

open(R+'index.html','w',encoding='utf-8').write(en)
os.makedirs(R+'sk',exist_ok=True); open(R+'sk/index.html','w',encoding='utf-8').write(sk)
os.makedirs(R+'logos',exist_ok=True)
for f in os.listdir(S+'logos/out'): shutil.copy(S+'logos/out/'+f,R+'logos/'+f)
import pages
soup_en=BeautifulSoup(body,'html.parser')
pairs=[('/','/sk/')]+pages.build_all(R, font, style, soup_en, soup)
today=datetime.date.today().isoformat()
def _alts(en_p, sk_p):
  return f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}{en_p}"/><xhtml:link rel="alternate" hreflang="sk" href="{SITE}{sk_p}"/><xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{en_p}"/>'
urls=''.join(f'  <url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod>{_alts(e_,k_)}</url>\n' for e_,k_ in pairs for p in (e_,k_))
open(R+'sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'+urls+'</urlset>\n')
open(R+'robots.txt','w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
open(R+'404.html','w',encoding='utf-8').write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>Page not found | MaBo Digital</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#EDF0F5;color:#0F1828;font-family:system-ui,sans-serif;text-align:center;padding:24px}a{color:#1B3FD0;font-weight:600}h1{font-size:2rem;margin:0 0 8px}@media (prefers-color-scheme:dark){body{background:#0C1220;color:#E7EBF4}a{color:#8CA6FF}}</style></head><body><div><h1>Page not found</h1><p>This address does not exist on mabodigital.dev. / Táto stránka neexistuje.</p><p><a href="/">Home</a> · <a href="/sk/">Slovensky</a></p></div></body></html>\n')
m=open(R+'site.webmanifest').read().replace('"src": "icon','"src": "/icon'); open(R+'site.webmanifest','w').write(m)
open(R+'_headers','w').write('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n\n/logos/*\n  Cache-Control: public, max-age=604800\n\n/*.png\n  Cache-Control: public, max-age=604800\n')
print('site built, slovak nodes:',n)
