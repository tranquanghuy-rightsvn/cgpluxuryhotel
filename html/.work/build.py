#!/usr/bin/env python3
"""Static multi-language build of the diamondseahotel.com clone (content: CGP Luxury Hotel).

Every language gets its own pre-rendered pages (SEO):
  vi -> /            en -> /en/   ko -> /ko/   zh -> /zh/   ru -> /ru/   de -> /de/
  pages: ""  gioi-thieu/  tin-tuc/  tin-tuc/<id>/  dat-phong/
Text comes from .work/src/i18n.js + .work/src/data.js (exported by .work/export.cjs -> .work/i18n.json).
All text is written into the HTML at build time; the site ships no translation JS.
Run from the html/ folder:  node .work/export.cjs && python3 .work/build.py
"""
import html as H, json, os, re, shutil, subprocess, time

def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


SITE = ""  # set to "https://your-domain" before going live (hreflang/canonical need absolute URLs)
VER = time.strftime("%Y%m%d%H%M")
subprocess.run(["node", ".work/export.cjs"], check=True, stdout=subprocess.DEVNULL)
D = json.load(open(".work/i18n.json", encoding="utf-8"))
LANGS = D["langs"]
DEFAULT = "vi"
P = {p["id"]: p for p in D["P"]}
for _p in P.values():
    _p["slug"] = slugify(_p["names"][1])
NEWS = D["NEWS"]
NAMES = {"vi": "Tiếng Việt", "en": "English", "ko": "한국어", "zh": "中文", "ru": "Русский", "de": "Deutsch"}
FLAGS = {"vi": "vi.png", "en": "en.png", "ko": "ko.svg", "zh": "zh.svg", "ru": "ru.svg", "de": "de.svg"}
LOCALE = {"vi": "vi_VN", "en": "en_GB", "ko": "ko_KR", "zh": "zh_CN", "ru": "ru_RU", "de": "de_DE"}

MAP = "https://www.google.com/maps?q=67+L%C3%BD+Th%C6%B0%E1%BB%9Dng+Ki%E1%BB%87t,+H%E1%BB%99i+An,+Qu%E1%BA%A3ng+Nam&z=15&output=embed"
FB = "https://www.facebook.com/profile.php?id=61564529174870"
PHONE, PHONE_TEL, EMAIL = "(+84) 905 926 638", "+84905926638", "cgpluxuryhotelhoian@gmail.com"
PKG_MENU = [6, 2, 3, 4, 9, 10, 11]
CATS = ["relax", "romance", "family", "long", "sig", "solo"]
GALLERY = ["hero-facade-night", "hero-facade-day", "room-pool-view", "suite-arch-romantic", "town-view-window", "room-petals-balcony",
           "grand-suite-arch", "suite-onyx-front", "towel-hearts", "bath-glass-view", "family-ricefield-view", "balcony-view",
           "deluxe-gold-panel", "suite-onyx", "bath-rose", "marble-double", "family-twin-balcony", "suite-sunset",
           "suite-gold", "room-romantic", "bathtub", "suite-onyx-window", "suite-sofa-curtains", "marble-room",
           "standard-double", "bathroom-classic", "room-window", "room-twin", "room-twin-window", "room-double-balcony",
           "room-bathtub-view", "room-desk", "room-sofa", "suite-lounge", "suite-arch", "pool"]
PKG_PHOTOS = {1: ["room-pool-view", "town-view-window", "bath-glass-view"], 2: ["towel-hearts", "room-petals-balcony", "bath-rose"],
              3: ["suite-arch-romantic", "towel-hearts", "bath-rose"], 4: ["family-twin-balcony", "family-ricefield-view", "bathroom-classic"],
              5: ["standard-double", "marble-room", "bathroom-classic"], 6: ["room-pool-view", "marble-double", "bath-glass-view"],
              7: ["room-petals-balcony", "suite-arch-romantic", "towel-hearts"], 8: ["town-view-window", "deluxe-gold-panel", "family-ricefield-view"],
              9: ["marble-double", "standard-double", "suite-onyx-window"], 10: ["grand-suite-arch", "suite-onyx-front", "bath-glass-view"],
              11: ["suite-sofa-curtains", "suite-onyx", "town-view-window"], 12: ["suite-onyx-window", "bath-rose", "room-pool-view"],
              13: ["suite-onyx-front", "grand-suite-arch", "deluxe-gold-panel"]}
GROUP_FILL = {"relax": ["room-pool-view", "town-view-window"], "family": ["family-twin-balcony", "family-ricefield-view"],
              "long": ["marble-double", "suite-onyx-window"], "sig": ["grand-suite-arch", "suite-onyx-front"],
              "romance": ["towel-hearts", "suite-arch-romantic"], "solo": ["suite-sofa-curtains", "suite-onyx"]}
SERVICES = [("s1", "pool"), ("s2", "balcony-view"), ("s3", "bathtub"), ("s4", "room-romantic"), ("s5", "hero-facade-night"), ("s6", "room-desk")]


SVG = {
    "pin": '<svg viewBox="0 0 24 24"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "phone": '<svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24"><path d="M3 10.5 12 4l9 6.5V20H3z"/><path d="m3 10.5 9 6 9-6M3 20l7-6M21 20l-7-6"/></svg>',
    "fb": '<svg viewBox="0 0 24 24"><path d="M14 8V6.2c0-.8.2-1.2 1.4-1.2H17V2h-2.6C11.3 2 10 3.5 10 6.1V8H8v3h2v11h4V11h2.7l.3-3z"/></svg>',
    "wa": '<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 0 0-8.7 15l-1.3 5 5.1-1.3A10 10 0 1 0 12 2zm5.8 14.2c-.2.7-1.4 1.3-2 1.4-.5.1-1.2.1-1.9-.1a17 17 0 0 1-1.7-.6 13.6 13.6 0 0 1-5.2-4.6c-.4-.5-1-1.5-1-2.8s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.3 0 .5l-.3.5-.4.4c-.1.2-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.4 2.4 1.5.3.1.5.1.7-.1l.9-1.1c.2-.3.4-.2.7-.1l2 1c.3.1.5.2.5.3.1.2.1.7-.1 1.3z"/></svg>',
    "at": '<svg viewBox="0 0 24 24"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5z"/></svg>',
    "search": '<svg viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg>',
    "cal": '<svg viewBox="0 0 24 24"><path d="M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 16H5V9h14v11zM7 11h3v3H7zm4 0h3v3h-3zm4 0h2v3h-2zm-8 4h3v3H7zm4 0h3v3h-3z"/></svg>',
    "user": '<svg viewBox="0 0 24 24"><path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm0 2c-3 0-8 1.5-8 4.5V21h16v-2.5C20 15.5 15 14 12 14z"/></svg>',
    "date": '<svg viewBox="0 0 448 512" aria-hidden="true"><path d="M12 192h424v280c0 22-18 40-40 40H52c-22 0-40-18-40-40V192zm424-44v-36c0-22-18-40-40-40h-40V20c0-6-6-12-12-12h-40c-6 0-12 6-12 12v52H156V20c0-6-6-12-12-12h-40c-6 0-12 6-12 12v52H52c-22 0-40 18-40 40v36c0 6 6 12 12 12h400c6 0 12-6 12-12z"/></svg>',
}

e = lambda s: H.escape(str(s), quote=True)


class Ctx:
    """Per-page context: language, asset root (R), language link base (L), current slug."""
    def __init__(self, lang, slug):
        self.lang, self.slug = lang, slug
        self.i = LANGS.index(lang)
        prefix = "" if lang == DEFAULT else lang + "/"
        depth = (prefix + slug).count("/")
        self.R = "../" * depth          # site root (assets)
        self.L = self.R + prefix        # link base for this language
        self.home = self.L or "./"

    def t(self, k): return D["T"][self.lang][k]
    def pick(self, arr): return arr[self.i]
    def name(self, pid): return self.pick(P[pid]["names"])
    def nights(self, n): return D["nights"][self.lang][str(n)]
    def date(self, iso): return D["short"][self.lang][iso]
    def url(self, slug=""): return self.L + slug if (self.L + slug) else "./"
    def img(self, n): return f"{self.R}images/{n}.jpg"
    def pkg(self, pid): return self.url(f'goi-luu-tru/{P[pid]["slug"]}/')
    def inc(self, k, p): return D["INC"][k][self.i].replace("{N}", self.nights(p["nights"])).replace("{n}", str(p["nights"]))


def lang_url(lang, slug):
    return SITE + "/" + ("" if lang == DEFAULT else lang + "/") + slug


# ------------------------------------------------------------------ layout
def header(c, cur):
    def a(slug, key, name):
        cls = ' class="is-current"' if cur == name else ""
        return f'<a href="{c.url(slug)}"{cls}>{e(c.t(key))}</a>'
    sub = "".join(f'<li><a href="{c.pkg(i)}">{e(c.name(i))}</a></li>' for i in PKG_MENU)
    langs = "".join(
        f'<li><a href="{c.R + ("" if l == DEFAULT else l + "/") + c.slug or "./"}" hreflang="{l}" lang="{l}"{" class=is-active" if l == c.lang else ""}>'
        f'<img src="{c.R}images/flags/{FLAGS[l]}" alt="">{NAMES[l]}</a></li>' for l in LANGS)
    return f'''<header class="site-header">
  <div class="port">
    <div class="header-bar">
      <button type="button" class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
      <a class="logo" href="{c.home}" aria-label="CGP Luxury Hotel"><img src="{c.R}images/logo.png" alt="CGP Luxury Hotel" width="557" height="360"></a>
      <nav class="nav">
        <ul class="menu">
          <li>{a("", "nav.home", "home")}</li>
          <li>{a("gioi-thieu/", "nav.about", "about")}</li>
          <li>{a("goi-luu-tru/", "nav.packages", "packages")}<ul class="sub-menu">{sub}</ul></li>
          <li>{a("dich-vu/", "nav.services", "services")}</li>
          <li>{a("tin-tuc/", "nav.news", "news")}</li>
          <li>{a("dat-phong/", "nav.book", "book")}</li>
        </ul>
      </nav>
      <div class="lang"><button type="button" class="lang-btn" aria-label="Language"><img src="{c.R}images/flags/{FLAGS[c.lang]}" alt=""><span>{NAMES[c.lang]}</span></button><ul class="lang-menu">{langs}</ul></div>
    </div>
  </div>
</header>'''


def footer(c):
    return f'''<footer class="site-footer">
  <div class="port">
    <div class="f-info">
      <h4>CGP Luxury Hotel</h4>
      <p><strong>Premium CGP Hotel Hoi An</strong></p>
      <p>{e(c.t("f.addr"))} {e(c.t("c.addrv"))}</p>
      <p>{e(c.t("f.phone"))} <a href="tel:{PHONE_TEL}">{PHONE}</a></p>
      <p>{e(c.t("f.hotline"))} <a href="tel:{PHONE_TEL}">{PHONE}</a></p>
      <p>{e(c.t("f.email"))} <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
    <div>
      <h4>{e(c.t("f.quick"))}</h4>
      <ul class="f-links">
        <li><a href="{c.url("gioi-thieu/")}">{e(c.t("nav.about"))}</a></li>
        <li><a href="{c.url("goi-luu-tru/")}">{e(c.t("nav.packages"))}</a></li>
        <li><a href="{c.url("dich-vu/")}">{e(c.t("nav.services"))}</a></li>
        <li><a href="{c.url("thu-vien-anh/")}">{e(c.t("gal.title"))}</a></li>
        <li><a href="{c.url("tin-tuc/")}">{e(c.t("nav.news"))}</a></li>
        <li><a href="{c.url("dat-phong/")}">{e(c.t("nav.book"))}</a></li>
      </ul>
    </div>
    <div>
      <h4>{e(c.t("f.policy"))}</h4>
      <ul class="f-links">
        <li><a href="{c.url("dat-phong/")}#terms">{e(c.t("f.terms"))}</a></li>
        <li><a href="#">{e(c.t("f.pay"))}</a></li>
        <li><a href="#">{e(c.t("f.privacy"))}</a></li>
        <li><a href="#">{e(c.t("f.refund"))}</a></li>
      </ul>
    </div>
    <div>
      <h4>{e(c.t("f.find"))}</h4>
      <div class="social">
        <a href="{FB}" target="_blank" rel="noopener" aria-label="Facebook">{SVG["fb"]}</a>
        <a href="https://wa.me/{PHONE_TEL[1:]}" target="_blank" rel="noopener" aria-label="WhatsApp">{SVG["wa"]}</a>
        <a href="mailto:{EMAIL}" aria-label="Email">{SVG["at"]}</a>
      </div>
    </div>
  </div>
</footer>'''


def page(c, title, desc, css, cur, body, scripts=(), og_img="hero-day"):
    links = "".join(f'<link rel="stylesheet" href="{c.R}css/{x}.css?v={VER}">\n' for x in ["fonts", "main"] + list(css))
    js = "".join(f'<script src="{c.R}js/{s}.js?v={VER}"></script>\n' for s in ["main"] + list(scripts))
    alt = "".join(f'<link rel="alternate" hreflang="{l}" href="{lang_url(l, c.slug)}">\n' for l in LANGS)
    alt += f'<link rel="alternate" hreflang="x-default" href="{lang_url(DEFAULT, c.slug)}">\n'
    doc = f'''<!DOCTYPE html>
<html lang="{c.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{lang_url(c.lang, c.slug)}">
{alt}<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:locale" content="{LOCALE[c.lang]}">
<meta property="og:image" content="{SITE}/images/{og_img}.jpg">
<link rel="icon" href="{c.R}favicon.ico" sizes="any">
<link rel="icon" href="{c.R}seo/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{c.R}seo/apple-touch-icon.png">
<link rel="manifest" href="{c.R}seo/site.webmanifest">
<meta name="theme-color" content="#002040">
{links}</head>
<body data-root="{c.R or "./"}" data-base="{c.home}">
{header(c, cur)}
<main>
{body}
</main>
{footer(c)}
{js}</body>
</html>
'''
    path = ("" if c.lang == DEFAULT else c.lang + "/") + c.slug + "index.html"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(path, "w", encoding="utf-8").write(doc)


# ------------------------------------------------------------------ blocks
def banner_page(c, img, text, cls=""):
    return f'''<section class="banner-page" style="background-image:url({c.img(img)})">
  <div class="port"><h1 class="{cls}">{e(text)}</h1></div>
</section>'''


def intro_block(c, h="h1"):
    imgs = "".join(f'\n        <img src="{c.img(n)}" alt="{e(c.t("intro.title"))}" loading="lazy" width="1320" height="880">'
                   for n in ["room-double-balcony", "suite-gold", "hero-facade-day", "room-twin-window", "suite-lounge"])
    return f'''<div class="intro-row">
      <div class="intro-card">
        <{h} class="headline dash">{e(c.t("intro.title"))}</{h}>
        <p>{e(c.t("intro.text"))}</p>
        <div class="btns">
          <a class="btn btn--sm" href="{c.url("gioi-thieu/")}">{e(c.t("btn.details"))}</a>
          <a class="btn btn--sm" href="{c.url("dat-phong/")}">{e(c.t("bt.bookroom"))}</a>
        </div>
      </div>
      <div class="intro-slider" data-fade="img">{imgs}
        <button type="button" class="arrow arrow--prev" aria-label="Previous"></button>
        <button type="button" class="arrow arrow--next" aria-label="Next"></button>
      </div>
    </div>'''


def contact_block(c):
    return f'''<div class="contact-row">
      <div class="map"><iframe src="{MAP}" title="Map" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      <div class="contact-card">
        <div class="c-item"><i>{SVG["pin"]}</i><div><h3>{e(c.t("c.addr"))}</h3><p>{e(c.t("c.addrv"))}</p></div></div>
        <div class="c-item"><i>{SVG["phone"]}</i><div><h3>{e(c.t("c.phone"))}</h3><a href="tel:{PHONE_TEL}">{PHONE}</a></div></div>
        <div class="c-item"><i>{SVG["mail"]}</i><div><h3>{e(c.t("c.email"))}</h3><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
      </div>
    </div>'''


def services_block(c):
    tiles = ""
    for i, img in enumerate(["pool", "balcony-view", "bathtub", "suite-gold"], 1):
        s, t = e(c.t(f"tile{i}.s")), e(c.t(f"tile{i}.t"))
        tiles += (f'<figure class="tile"><img src="{c.img(img)}" alt="{t}" loading="lazy" width="660" height="440">'
                  f'<figcaption class="tile-cap"><span class="tile-label">{s}</span><strong class="tile-title">{t}</strong></figcaption>'
                  f'<a class="tile-hover" href="{c.url("dich-vu/")}"><span class="tile-label">{s}</span><strong class="tile-title">{t}</strong></a></figure>')
    return f'''<section class="svc-head">
  <div class="port">
    <h2 class="headline dash">{e(c.t("svc.title"))}</h2>
    <p class="sub-title">{e(c.t("svc.text"))}</p>
  </div>
</section>
<section class="svc-tiles">{tiles}</section>'''


def featured_cards(c, ids):
    out = ""
    for i in ids:
        p, n = P[i], e(c.name(i))
        out += (f'<article class="post"><a class="post-img" href="{c.pkg(i)}"><img src="{c.img(p["img"])}" alt="{n}" loading="lazy" width="660" height="440"></a>'
                f'<div class="post-body"><h3 class="post-title"><a href="{c.pkg(i)}">{n}</a></h3>'
                f'<div class="post-btns"><a class="btn" href="{c.pkg(i)}">{e(c.t("btn.details"))}</a>'
                f'<a class="btn" href="{c.url("dat-phong/")}?pkg={i}">{e(c.t("btn.book"))}</a></div></div></article>')
    return out


def room_cards(c, ids, wide_from=3):
    out = ""
    for k, i in enumerate(ids):
        p, n = P[i], e(c.name(i))
        href = c.pkg(i)
        out += (f'<article class="room{" is-wide" if k >= wide_from else ""}"><a class="room-img" href="{href}"><img src="{c.img(p["img"])}" alt="{n}" loading="lazy" width="660" height="440"></a>'
                f'<div class="room-body"><h3 class="room-title"><a href="{href}">{n}</a></h3><p class="room-text">{e(c.pick(p["tag"]))}</p>'
                f'<div class="room-foot"><a class="btn" href="{href}">{e(c.t("btn.detailsShort"))}</a>'
                f'<div><span class="price-from">{e(c.t("price.from"))}</span><span class="price">USD {p["price"]:,} {e(c.t("u." + p["unit"]))}</span></div></div></div></article>')
    return out


def news_url(c, n): return c.url(f'tin-tuc/{n["id"]}/')


def news_cards(c):
    out = ""
    for n in NEWS:
        u = news_url(c, n)
        out += (f'<article class="post"><a class="post-img" href="{u}"><img src="{c.img(n["img"])}" alt="{e(c.pick(n["title"]))}" loading="lazy" width="660" height="440"></a>'
                f'<div class="post-body"><span class="post-date">{SVG["date"]}<time datetime="{n["date"]}">{e(c.date(n["date"]))}</time></span>'
                f'<h3 class="news-title"><a href="{u}">{e(c.pick(n["title"]))}</a></h3><p class="news-text">{e(c.pick(n["body"]))}</p></div></article>')
    return out


def news_list(c):
    out = ""
    for n in NEWS:
        u = news_url(c, n)
        out += (f'<li class="news-item"><a class="post-img" href="{u}"><img src="{c.img(n["img"])}" alt="{e(c.pick(n["title"]))}" loading="lazy" width="660" height="440"></a>'
                f'<div><h2><a href="{u}">{e(c.pick(n["title"]))}</a></h2><div class="news-meta">{SVG["date"]}<time datetime="{n["date"]}">{e(c.date(n["date"]))}</time></div>'
                f'<p>{e(c.pick(n["body"]))}</p></div></li>')
    return out + f'<li class="news-none" hidden>{e(c.t("sb.none"))}</li>'


def sidebar(c):
    recent = "".join(f'<li><a href="{news_url(c, n)}"><img src="{c.img(n["img"])}" alt="" loading="lazy"><span>{e(c.pick(n["title"]))}</span></a></li>' for n in NEWS)
    pk = "".join(f'<li><a href="{c.pkg(i)}"><img src="{c.img(P[i]["img"])}" alt="" loading="lazy"><span>{e(c.name(i))}</span></a></li>' for i in range(1, 8))
    return f'''<aside class="sidebar">
      <section><h3 class="widget-title">{e(c.t("sb.search"))}</h3>
        <form class="search-box" role="search" action="{c.url("tin-tuc/")}" method="get"><input type="search" name="s" placeholder="{e(c.t("sb.looking"))}" aria-label="{e(c.t("sb.search"))}"><button type="submit" aria-label="{e(c.t("sb.search"))}">{SVG["search"]}</button></form></section>
      <section><h3 class="widget-title">{e(c.t("sb.recent"))}</h3><ul class="side-list">{recent}</ul></section>
      <section><h3 class="widget-title">{e(c.t("sb.list"))}</h3><ul class="side-list">{pk}</ul></section>
    </aside>'''


def article_body(c, n):
    body = c.pick(n["body"])
    parts = re.split(r'(?<=[.。])\s*(?=[A-ZÀ-Ỹ가-힣一-龥А-ЯÄÖÜ])', body)
    half = (len(parts) + 1) // 2
    paras = [" ".join(parts[:half]), " ".join(parts[half:])]
    ps = "".join(f"<p>{e(x)}</p>" for x in paras if x.strip())
    thanks = c.t("ok.text").split(".")[0].split("。")[0]
    return (f'<div class="news-meta" style="margin-bottom:14px">{SVG["date"]}<time datetime="{n["date"]}">{e(c.date(n["date"]))}</time></div>{ps}'
            f'<p>{e(thanks)}.</p><p class="article-cta"><a class="btn-navy" href="{c.url("dat-phong/")}">{e(c.t("art.cta"))}</a></p>'
            f'<img class="article-img" src="{c.img(n["img"])}" alt="{e(c.pick(n["title"]))}" loading="lazy" width="1320" height="880">')



def faq_block(c, n=9):
    items = "".join(f'<details class="faq-item"><summary>{e(c.t(f"faq.q{i}"))}</summary><p>{e(c.t(f"faq.a{i}"))}</p></details>' for i in range(1, n + 1))
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": c.t(f"faq.q{i}"), "acceptedAnswer": {"@type": "Answer", "text": c.t(f"faq.a{i}")}} for i in range(1, n + 1)]}
    return f'''<section class="faq-sec">
  <div class="port">
    <h2 class="headline dash">{e(c.t("faq.title"))}</h2>
    <div class="faq">{items}</div>
  </div>
</section>
{jsonld(data)}'''


def gallery_grid(c, imgs, uid, cls="gal-grid"):
    """Thumbnails + CSS-only lightbox (:target), no JS."""
    alt = e(c.t("intro.title"))
    thumbs = "".join(f'<a class="gal-item" href="#{uid}-{k}"><img src="{c.img(n)}" alt="{alt} – {k + 1}" loading="lazy" width="660" height="440"></a>' for k, n in enumerate(imgs))
    boxes = "".join(f'<div class="lb" id="{uid}-{k}"><a class="lb-bg" href="#{uid}" aria-label="Close"></a><img src="{c.img(n)}" alt="{alt} – {k + 1}" loading="lazy">'
                    f'<a class="lb-x" href="#{uid}" aria-label="Close">&times;</a>'
                    + (f'<a class="lb-prev" href="#{uid}-{k - 1}" aria-label="Previous"></a>' if k else "")
                    + (f'<a class="lb-next" href="#{uid}-{k + 1}" aria-label="Next"></a>' if k < len(imgs) - 1 else "") + "</div>" for k, n in enumerate(imgs))
    return f'<div class="{cls}" id="{uid}">{thumbs}</div>{boxes}'


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def build_packages(lang):
    # list page, grouped by the collection structure of info-rooms.docx
    c = Ctx(lang, "goi-luu-tru/")
    groups = ""
    for cat in CATS:
        ids = [i for i in sorted(P) if P[i]["cat"] == cat]
        fill = "".join(f'<figure class="room room-photo"><img src="{c.img(n)}" alt="{e(c.t("cat." + cat))}" loading="lazy" width="660" height="440"></figure>'
                       for n in GROUP_FILL[cat][:(3 - len(ids) % 3) % 3])
        groups += f'''<section class="pk-group">
  <div class="port">
    <h2 class="headline dash">{e(c.t("cat." + cat))}</h2>
    <div class="rooms-grid rooms-grid--list">{room_cards(c, ids, wide_from=99)}{fill}</div>
  </div>
</section>'''
    body = banner_page(c, "suite-sunset", c.t("pk.title")) + f'\n<p class="port pk-intro sub-title">{e(c.t("pk.text"))}</p>\n' + groups + "\n" + faq_block(c)
    items = [{"@type": "ListItem", "position": k + 1, "url": lang_url(lang, f'goi-luu-tru/{P[i]["slug"]}/'), "name": c.name(i)} for k, i in enumerate(sorted(P))]
    body += jsonld({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": items})
    page(c, f'{c.t("pk.title")} | {c.t("intro.title")}', c.t("pk.text"), ["home", "pages"], "packages", body)

    # one page per package
    for pid in sorted(P):
        p = P[pid]
        c = Ctx(lang, f'goi-luu-tru/{p["slug"]}/')
        name = c.name(pid)
        incs = "".join(f"<li>{e(c.inc(k, p))}</li>" for k in p["inc"])
        others = [i for i in sorted(P) if P[i]["cat"] == p["cat"] and i != pid]
        others += [i for i in sorted(P) if i != pid and i not in others]
        price = f'USD {p["price"]:,}'
        body = f'''{banner_page(c, p["img"], name)}
<section class="pd">
  <div class="port">
    <div class="pd-media"><img src="{c.img(p["img"])}" alt="{e(name)}" width="1320" height="880"><a class="pd-ribbon" href="{c.url("dat-phong/")}?pkg={pid}">{e(c.t("btn.book"))}</a></div>
    {gallery_grid(c, PKG_PHOTOS[pid], "pd-gal", "pd-thumbs")}
    <div class="pd-row">
      <div class="pd-main">
        <p class="pd-tag">{e(c.pick(p["tag"]))}</p>
        <p class="pd-desc">{e(c.pick(p["desc"]))}</p>
        <h2 class="pd-h">{e(c.t("incl"))}</h2>
        <ul class="pd-inc">{incs}</ul>
        <p class="pd-note">{e(c.t("note.star"))} <a href="{c.url("dat-phong/")}#terms">{e(c.t("pd.terms"))}</a></p>
      </div>
      <aside class="pd-side">
        <ul class="pd-facts">
          <li><span>{e(c.t("pd.duration"))}:</span> {e(c.nights(p["nights"]))}</li>
          <li><span>{e(c.t("pd.guests"))}:</span> {e(c.t("gl." + p["g"]))}</li>
          <li><span>{e(c.t("pd.cat"))}:</span> {e(c.t("cat." + p["cat"]))}</li>
          <li><span>{e(c.t("pd.badge"))}:</span> {e(c.pick(p["badge"]))}</li>
        </ul>
        <div class="pd-buy"><a class="btn btn--lg" href="{c.url("dat-phong/")}?pkg={pid}">{e(c.pick(p["cta"]))}</a><span class="pd-price"><small>{e(c.t("pd.price"))}</small>{price} {e(c.t("u." + p["unit"]))}</span></div>
      </aside>
    </div>
  </div>
</section>
<section class="pd-others">
  <div class="port">
    <h2 class="headline headline--sm dash">{e(c.t("pd.other"))}</h2>
    <div class="rooms-grid rooms-grid--list">{room_cards(c, others[:6], wide_from=99)}</div>
  </div>
</section>'''
        body += jsonld({"@context": "https://schema.org", "@type": "Offer", "name": name, "description": c.pick(p["desc"]),
                        "url": lang_url(lang, c.slug), "image": SITE + "/images/" + p["img"] + ".jpg", "price": p["price"], "priceCurrency": "USD",
                        "availability": "https://schema.org/InStock", "category": c.t("cat." + p["cat"]),
                        "offeredBy": {"@type": "Hotel", "name": "CGP Luxury Hotel Hoi An", "telephone": PHONE_TEL, "email": EMAIL,
                                      "address": {"@type": "PostalAddress", "streetAddress": "67 Ly Thuong Kiet", "addressLocality": "Hoi An", "addressRegion": "Quang Nam", "addressCountry": "VN"}}})
        desc = c.pick(p["desc"])
        page(c, f'{name} | {c.t("intro.title")}', desc[:157] + ("…" if len(desc) > 157 else ""), ["home", "pages"], "packages", body, og_img=p["img"])


def build_gallery(lang):
    c = Ctx(lang, "thu-vien-anh/")
    body = f'''{banner_page(c, "grand-suite-arch", c.t("gal.title"))}
<section class="gal-sec gal-page">
  <div class="port">
    <p class="sub-title">{e(c.t("gal.sub"))}</p>
    {gallery_grid(c, GALLERY, "gal")}
  </div>
</section>'''
    page(c, f'{c.t("gal.title")} | {c.t("intro.title")}', c.t("gal.sub"), ["home", "pages"], "gallery", body, og_img="room-pool-view")


def build_services(lang):
    c = Ctx(lang, "dich-vu/")
    rows = ""
    for k, (key, img) in enumerate(SERVICES):
        t = e(c.t(key + ".t"))
        text = f'<div class="svc-text"><h2>{t}</h2><p>{e(c.t(key + ".d"))}</p><a class="btn btn--sm" href="{c.url("goi-luu-tru/")}">{e(c.t("svc.cta"))}</a></div>'
        pic = f'<div class="svc-img"><img src="{c.img(img)}" alt="{t}" loading="lazy" width="660" height="440"></div>'
        rows += f'<article class="svc-row{" is-rev" if k % 2 else ""}">{pic if k % 2 == 0 else text}{text if k % 2 == 0 else pic}</article>'
    body = f'''{banner_page(c, "suite-gold", c.t("svc.page"))}
<section class="svc-page">
  <div class="port">
    <p class="sub-title svc-intro">{e(c.t("svc.text"))}</p>
    {rows}
  </div>
</section>'''
    page(c, f'{c.t("svc.page")} | {c.t("intro.title")}', c.t("svc.text"), ["home", "pages"], "services", body)

# ------------------------------------------------------------------ booking widget (static)
BK_ICON = {
    "cal": SVG["cal"],
    "user": SVG["user"],
    "plus": '<svg viewBox="0 0 24 24"><path d="M11 5h2v14h-2z"/><path d="M5 11h14v2H5z"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" width="14" height="14" fill="#3c6098"><path d="M17 9h-1V7a4 4 0 0 0-8 0v2H7a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-9a2 2 0 0 0-2-2zm-7-2a2 2 0 1 1 4 0v2h-4V7z"/></svg>',
    "guests": '<svg viewBox="0 0 24 24"><path d="M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm7 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM9 13c-2.7 0-7 1.3-7 4v2h14v-2c0-2.7-4.3-4-7-4zm7 0c-.3 0-.7 0-1.1.1 1.3.9 2.1 2.2 2.1 3.9v2h5v-2c0-2.7-4.3-4-6-4z"/></svg>',
    "moon": '<svg viewBox="0 0 24 24"><path d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5z"/></svg>',
    "back": '<svg viewBox="0 0 24 24"><path d="M10 9V5l-7 7 7 7v-4.1c5 0 8.5 1.6 11 5.1-1-5-4-10-11-11z"/></svg>',
    "card": '<svg viewBox="0 0 24 24"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>',
    "qr": '<svg viewBox="0 0 24 24"><path d="M3 3h8v8H3V3zm2 2v4h4V5H5zm8-2h8v8h-8V3zm2 2v4h4V5h-4zM3 13h8v8H3v-8zm2 2v4h4v-4H5zm13-2h3v3h-3v-3zm-5 0h3v3h-3v-3zm3 3h3v3h-3v-3zm-3 3h3v2h-3v-2zm5 0h3v2h-3v-2z"/></svg>',
    "phone": '<svg viewBox="0 0 24 24"><path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>',
}
GUESTS = {"g1": 1, "g2": 2, "g12": 2, "fam": 4}


def booking_widget(c):
    """Every step of the booking engine pre-rendered in this page's language.
    js/booking.js only switches steps, filters/sorts cards and fills in the guest's own choices (dates, package)."""
    t = lambda k: e(c.t(k))
    fmt = lambda k, **kw: e(_fmt(c.t(k), kw))
    ic = lambda k, cls: BK_ICON[k].replace("<svg", f'<svg class="{cls}"', 1)
    usd = lambda n: f"USD {n:,}"

    def title(step, key, back=None):
        b = f'<button type="button" class="x-hnp__back" data-go="{back[1]}">{t(back[0])}</button>' if back else ""
        return f'<div class="x-hnp">{b}<h2>{t(key)}</h2></div>'

    def bar(pct):
        return f'<div class="x-hnp__bar"{"" if pct else " hidden"}><i style="width:{pct}%"></i></div>'

    langs = "".join(f'<li><a href="{c.R + ("" if l == DEFAULT else l + "/") + c.slug}" hreflang="{l}" lang="{l}"><img src="{c.R}images/flags/{FLAGS[l]}" alt="">{NAMES[l]}</a></li>' for l in LANGS)
    top = (f'<div class="x-hcp"><div class="x-hcp__crit" data-steps="1 2 3 4">'
           f'<button type="button" class="x-scb" data-go="0"><small>{t("tl.cico")}</small><b data-v="range"></b></button>'
           f'<button type="button" class="x-scb" data-go="0"><small>{t("box.guests")}</small><b data-v="guests"></b></button></div>'
           f'<div class="x-hcp__tools"><button type="button" class="hb hb--promo" data-go="0" data-promo="1" data-steps="1 2">{BK_ICON["lock"]}{t("tl.promoBtn")}</button>'
           f'<div class="hb-lang"><button type="button" class="hb" data-langmenu aria-label="Language"><img src="{c.R}images/flags/{FLAGS[c.lang]}" alt=""></button><ul>{langs}</ul></div>'
           f'<span class="hb">USD</span></div></div>')

    # step 0 — details of your stay
    ad = "".join(f'<option value="{n}"{" selected" if n == 2 else ""}>{t("g.a" + str(n))}</option>' for n in (1, 2, 3, 4))
    ch = f'<option value="0">{t("tl.child")}</option>' + "".join(f'<option value="{n}">{t("tl.c" + str(n))}</option>' for n in (1, 2))
    step0 = (title(0, "tl.details") + bar(0) +
             f'<form class="tl-body" id="f-search" novalidate><div class="psf">'
             f'<div class="psf-row"><label><span class="psf-label">{t("tl.ci")}</span><span class="x-input"><output data-for="s-ci"></output><input class="x-native" type="date" id="s-ci" required>{ic("cal", "ico-r")}</span></label>'
             f'<label><span class="psf-label">{t("tl.co")}</span><span class="x-input"><output data-for="s-co"></output><input class="x-native" type="date" id="s-co" required>{ic("cal", "ico-r")}</span></label></div>'
             f'<hr><span class="psf-label">{t("tl.stay")}</span><p class="psf-note">{t("tl.aged")}</p>'
             f'<div class="psf-row"><label class="x-input has-icon">{ic("user", "ico-l")}<select id="s-ad">{ad}</select><i class="chev"></i></label>'
             f'<label class="x-input has-icon">{ic("plus", "ico-l")}<select id="s-ch">{ch}</select><i class="chev"></i></label></div>'
             f'<p class="psf-extra-row"><button type="button" class="psf-extra" data-extra>{t("tl.extra")}{BK_ICON["plus"]}</button></p><p class="psf-note" id="s-extra" hidden>{t("tl.extraNote")}</p>'
             f'<hr><label class="x-check"><input type="checkbox" id="s-hp"><span>{t("tl.promo")}</span></label>'
             f'<label class="x-input psf-promo" hidden><input type="text" id="s-promo" maxlength="20" placeholder="{t("tl.promoBtn")}" autocomplete="off"></label>'
             f'<button type="submit" class="tl-btn tl-btn--lg">{t("tl.check")}</button><p class="tl-error" id="s-err" hidden>{t("tl.dates")}</p></div></form>')

    # step 1 — select a package
    def card(p):
        n = e(c.name(p["id"]))
        badge = f'<span class="rcard-badge">🏆 {t("tl.best1")}</span>' if p["id"] == 6 else ""
        incs = "".join(f"<li>{e(c.inc(k, p))}</li>" for k in p["inc"])
        return (f'<article class="rcard" data-card="{p["id"]}" data-cat="{p["cat"]}" data-guests="{GUESTS[p["g"]]}">'
                f'<div class="rcard-img"><img src="{c.img(p["img"])}" alt="{n}" loading="lazy" width="660" height="440">{badge}</div>'
                f'<div class="rcard-body"><div class="rcard-name"><h3>{n}</h3><button type="button" class="round-btn" data-expand aria-label="+"></button></div>'
                f'<div class="rcard-meta"><span>{BK_ICON["guests"]}{fmt("tl.upto", n=GUESTS[p["g"]])}</span><span>{BK_ICON["moon"]}{e(c.nights(p["nights"]))}</span></div>'
                f'<p class="rcard-tag">{e(c.pick(p["tag"]))}</p><ul class="rcard-more">{incs}</ul>'
                f'<div class="rcard-price"><small>{t("tl.from")} </small><b>{usd(p["price"])}</b><em>{e(c.nights(p["nights"]))} / {t("gl." + p["g"])}</em></div>'
                f'<button type="button" class="tl-btn" data-pick="{p["id"]}">{t("tl.sel")}</button></div></article>')
    cats = "".join(f'<button type="button" class="chip{" is-active" if k == "all" else ""}" data-cat="{k}">{t("cat." + k)}</button>' for k in ["all"] + CATS)
    near = (f'<aside class="near"><h6>{t("tl.near")}</h6><ul>' + "".join(f"<li>{t(k)}</li>" for k in ("tl.n1", "tl.n2", "tl.n3")) + "</ul>"
            f'<h6>{t("tl.top")}</h6><ul>' + "".join(f"<li>{t(k)}</li>" for k in ("am1", "am7", "tile1.t", "am3", "am6", "am8")) + "</ul></aside>")
    cards = [card(P[i]) for i in sorted(P)]
    cards.insert(2, near)
    step1 = (title(1, "tl.select") + bar(20) +
             f'<div class="tl-body"><div class="x-bpg"><div class="x-bpg__label">{t("tl.best")}</div><div class="x-bpg__items">'
             + "".join(f"<span><i></i>{t(k)}</span>" for k in ("tl.b1", "tl.b2", "tl.b3")) +
             f'</div><div class="x-bpg__price"><small>{t("tl.ourbest")}</small><b>{usd(min(p["price"] for p in P.values()))}</b></div></div>'
             f'<div class="filters">{cats}</div><div class="rooms-grid-tl">{"".join(cards)}</div></div>')

    # step 2 — package details, one block per package
    def rate(p):
        pid, n = p["id"], e(c.name(p["id"]))
        chips = "".join(f"<span>{e(c.inc(k, p))}</span>" for k in p["inc"][:4]) + (f'<span>+ {len(p["inc"]) - 4}</span>' if len(p["inc"]) > 4 else "")
        incs = "".join(f"<li>{e(c.inc(k, p))}</li>" for k in p["inc"])
        return (f'<div class="rp-pkg" data-pkg="{pid}" data-nights="{p["nights"]}" hidden>'
                f'<div class="rp-room"><img src="{c.img(p["img"])}" alt="" loading="lazy"><div><h3 data-k="name">{n}</h3>'
                f'<div class="rp-meta"><span>{fmt("tl.upto", n=GUESTS[p["g"]])}</span><span data-k="nights">{e(c.nights(p["nights"]))}</span><span data-k="badge">{e(c.pick(p["badge"]))}</span></div>'
                f'<div class="rp-amen">{chips}</div></div><span></span></div>'
                f'<div class="rate"><div><h4>{e(c.pick(p["tag"]))}</h4><p class="rate-desc">{e(c.pick(p["desc"]))}</p><ul class="rate-list">{incs}</ul>'
                f'<p class="rate-terms">{t("note.star")}</p></div>'
                f'<div class="rate-side"><small>{fmt("tl.priceFor", n=c.nights(p["nights"]))}</small><div class="row"><b data-k="price">{usd(p["price"])}</b>'
                f'<button type="button" class="tl-btn" data-go="3">{t("tl.sel")}</button></div>'
                f'<p class="rate-terms" data-minstay hidden>{fmt("tl.minStay", n=c.nights(p["nights"]))}<br><span data-v="range"></span></p></div></div></div>')
    terms = "".join(f"<li>• {t('terms.' + str(k))}</li>" for k in range(1, 9))
    step2 = title(2, "tl.rate", ("tl.backRooms", 1)) + bar(48) + f'<div class="tl-body">{"".join(rate(P[i]) for i in sorted(P))}<ul class="rate-terms">{terms}</ul></div>'

    # step 3 — guest details + payment
    def field(fid, key, typ, icon=None):
        pre = ic(icon, "ico-l") if icon else ""
        return f'<label class="x-input{" has-icon" if icon else ""}">{pre}<input type="{typ}" id="{fid}" placeholder="{t(key)}"{" class=pl-icon" if icon else ""}></label>'

    def opt(v, key, desc, icon):
        return f'<label class="pay-opt"><input type="radio" name="pay" value="{v}"{" checked" if v == "card" else ""}><strong>{BK_ICON[icon]}{t(key)}</strong><p>{t(desc)}</p></label>'
    terms_link = f'<a href="#terms">{t("f.terms")}</a>'
    mybk = (f'<aside class="mybk"><h2>{t("tl.mybk")}</h2><div class="mybk-n" data-v="nights"></div>'
            f'<div class="mybk-dates"><div><i data-v="ci-d"></i> <span data-v="ci-m"></span><em data-v="ci-w"></em><small>{t("tl.fromT")}</small></div><span class="mybk-sep">—</span>'
            f'<div><i data-v="co-d"></i> <span data-v="co-m"></span><em data-v="co-w"></em><small>{t("tl.tillT")}</small></div></div>'
            f'<div class="mybk-room"><div class="row"><b>{t("tl.pkg")}</b><b data-v="price"></b></div><a href="#" data-go="2" data-v="name"></a></div>'
            f'<div class="mybk-lines"><div class="row"><strong data-v="guests"></strong></div><div class="row"><span data-v="badge"></span><span data-v="price"></span></div>'
            f'<div class="row"><strong>{t("tl.svc")}</strong></div><div class="row"><span>{t("am1")}</span><span>{t("tl.incl")}</span></div>'
            f'<div class="row" data-promo-row hidden><span>{t("sum.promo")}</span><span data-v="promo"></span></div></div>'
            f'<div class="mybk-total"><div class="row"><strong>{t("tl.total")}</strong><b data-v="price"></b></div><hr><div class="row"><strong>{t("tl.paynow")}</strong><b data-v="price"></b></div>'
            f'<button type="button" class="tl-btn" id="b-book">{t("pay.btn")}</button><p class="tl-error" id="d-err" hidden>{t("tl.invalid")}</p></div>'
            f'<div class="mybk-foot">{t("tl.summary")}</div></aside>')
    step3 = (title(3, "tl.enter", ("tl.backRate", 2)) + bar(80) +
             f'<div class="tl-body"><div class="details"><div>'
             f'<section class="plate"><h3 class="plate-cap">{t("tl.customer")}</h3><div class="plate-body">'
             f'<div>{t("tl.bookfor")}<span class="seg"><label><input type="radio" name="for" value="me" checked>{t("tl.me")}</label><label><input type="radio" name="for" value="else">{t("tl.else")}</label></span></div>'
             f'<p class="small-note">{t("tl.primary")}</p><hr>'
             f'<div class="f-grid">{field("d-first", "tl.first", "text")}{field("d-last", "tl.last", "text")}{field("d-phone", "fm.phone", "tel", "phone")}{field("d-email", "c.email", "email", "mail")}</div>'
             f'<div class="f-country"><span>{t("fm.country")}</span>{field("d-country", "fm.country", "text")}</div>'
             f'<div class="consents"><p class="info">{BK_ICON["mail"]}{t("tl.conf")}</p>'
             f'<label class="x-check"><input type="checkbox" id="d-news"><span>{t("tl.cons1")}</span></label>'
             f'<label class="x-check" id="d-agree-l"><input type="checkbox" id="d-agree"><span>{t("tl.cons2").replace(t("f.terms"), terms_link)}</span></label></div></div></section>'
             f'<section class="plate"><h3 class="plate-cap">{t("tl.add")}</h3><div class="plate-body"><h4 class="h4">{t("tl.times")}</h4>'
             f'<div class="times"><span class="x-input"><small>{t("box.checkin")}</small><b>14:00 — <em>{t("tl.free")}</em></b></span><span class="x-input is-disabled"><small>{t("box.checkout")}</small><b>12:00</b></span></div>'
             f'<hr><h4 class="h4">{t("tl.req")}</h4><textarea class="x-textarea" id="d-note" placeholder="{t("tl.reqph")}"></textarea></div></section>'
             f'<section class="plate"><h3 class="plate-cap">{t("tl.paym")}</h3><div class="plate-body"><p class="pay-info">{BK_ICON["back"]}{t("tl.payinfo")}</p>'
             + opt("card", "pay.card", "tl.payCardD", "card") + opt("atm", "pay.atm", "tl.payAtmD", "card") + opt("qr", "pay.qr", "tl.payQrD", "qr") +
             f'<p class="pay-demo">{t("pay.demo")}</p></div></section></div>{mybk}</div></div>')

    # step 4 — confirmation
    step4 = (title(4, "ok.title") + bar(100) +
             f'<div class="tl-body"><div class="done"><div class="done-ico"></div><h3>{t("ok.title")}</h3><p>{t("ok.text")}</p>'
             f'<div class="done-code">{t("ok.code")}<b data-v="code"></b></div>'
             f'<p><span data-v="name"></span> · <span data-v="range"></span> · <span data-v="price"></span></p>'
             f'<p class="done-home"><a class="tl-btn" href="{c.home}">{t("ok.home")}</a></p></div></div>')

    steps = "".join(f'<div class="tl-step" data-step="{k}"{" hidden" if k else ""}>{s}</div>' for k, s in enumerate([step0, step1, step2, step3, step4]))
    return top + steps + '<p class="tl-copy">© CGP Luxury Hotel Booking Engine (demo)</p>'


def _fmt(s, kw):
    for k, v in kw.items():
        s = s.replace("{" + k + "}", str(v))
    return s


# ------------------------------------------------------------------ pages
def build(lang):
    # Home
    c = Ctx(lang, "")
    slides = "".join(f'<div class="banner-slide" style="background-image:url({c.img(n)})"></div>' for n in ["hero-facade-night", "hero-facade-day", "hero-pool-night", "hero-lobby", "hero-guests", "suite-sunset"])
    adults = "".join(f'<option value="{n}"{" selected" if n == 2 else ""}>{e(c.t("g.a" + str(n)) + c.t("g.c0"))}</option>' for n in (1, 2, 3, 4))
    home = f'''<section class="banner" data-fade=".banner-slide" data-auto="6000" data-loop="1">
  {slides}
  <button type="button" class="slick-arrow slick-prev" aria-label="Previous"></button>
  <button type="button" class="slick-arrow slick-next" aria-label="Next"></button>
  <div class="dots"></div>
  <div class="banner-content">
    <div class="port">
      <div class="book-box">
        <form class="sfl" action="{c.url("dat-phong/")}" method="get">
          <div class="sfl-title">{e(c.t("box.title"))}</div>
          <div class="sfl-sub">{e(c.t("box.sub"))}</div>
          <div class="sfl-grid">
            <label class="sfl-field"><span>{e(c.t("box.checkin"))}</span><output data-show="checkin"></output><input class="sfl-native" type="date" name="checkin" required><i>{SVG["cal"]}</i></label>
            <label class="sfl-field"><span>{e(c.t("box.checkout"))}</span><output data-show="checkout"></output><input class="sfl-native" type="date" name="checkout" required><i>{SVG["cal"]}</i></label>
            <label class="sfl-field"><span>{e(c.t("box.guests"))}</span><select name="adults">{adults}</select><i>{SVG["user"]}</i></label>
            <button type="button" class="sfl-promo">{e(c.t("box.promo"))}</button>
            <input class="sfl-promo-input" type="text" name="promo" maxlength="20" autocomplete="off" placeholder="{e(c.t("box.promoph"))}" hidden>
            <button type="submit" class="sfl-submit">{e(c.t("box.cta"))}</button>
            <a class="sfl-auth" href="{c.url("dat-phong/")}">{SVG["user"]}<span>{e(c.t("sfl.login"))}</span></a>
          </div>
        </form>
      </div>
    </div>
  </div>
</section>

<section class="intro">
  <div class="port">
    {intro_block(c)}
    {contact_block(c)}
  </div>
</section>

<section class="posts-sec">
  <div class="port">
    <h2 class="headline dash">{e(c.t("feat.title"))}</h2>
    <div class="carousel">
      <div class="carousel-view"><div class="carousel-track">{featured_cards(c, [6, 2, 3, 4, 10, 9, 12])}</div></div>
      <button type="button" class="arrow arrow--prev" aria-label="Previous"></button>
      <button type="button" class="arrow arrow--next" aria-label="Next"></button>
    </div>
    <div class="dots"></div>
  </div>
</section>

{services_block(c)}

<section class="rooms">
  <div class="port">
    <h2 class="headline dash">{e(c.t("pk.title"))}</h2>
    <div class="rooms-grid">{room_cards(c, [1, 5, 8, 7, 11, 12, 13])}</div>
    <p class="more-row"><a class="btn" href="{c.url("goi-luu-tru/")}">{e(c.t("pk.viewall"))}</a></p>
  </div>
</section>

{faq_block(c)}

<section class="news-sec">
  <div class="port">
    <h2 class="headline dash">{e(c.t("nw.title"))}</h2>
    <div class="carousel">
      <div class="carousel-view"><div class="carousel-track">{news_cards(c)}</div></div>
      <button type="button" class="arrow arrow--prev" aria-label="Previous"></button>
      <button type="button" class="arrow arrow--next" aria-label="Next"></button>
    </div>
    <div class="dots"></div>
  </div>
</section>'''
    page(c, f'{c.t("intro.title")} | {c.t("box.sub")}', c.t("intro.text"), ["home", "pages"], "home", home)

    # About
    c = Ctx(lang, "gioi-thieu/")
    about = f'''{banner_page(c, "hero-facade-night", c.t("ab.banner"))}
<section class="intro about-sec">
  <div class="port">
    {intro_block(c, "h2")}
  </div>
</section>
<section class="ab-story">
  <div class="port">
    <h2 class="headline dash">{e(c.t("ab.story.t"))}</h2>
    <div class="ab-story-body">{"".join(f"<p>{e(c.t(f'ab.story.p{i}'))}</p>" for i in range(1, 6))}</div>
  </div>
</section>
{services_block(c)}
<section class="gal-sec">
  <div class="port">
    <h2 class="headline dash">{e(c.t("gal.title"))}</h2>
    {gallery_grid(c, GALLERY[:8], "ab-gal", "gal-grid gal-grid--4")}
    <p class="more-row"><a class="btn" href="{c.url("thu-vien-anh/")}">{e(c.t("gal.more"))}</a></p>
  </div>
</section>
{faq_block(c)}
<section class="intro" style="padding:40px 0 60px">
  <div class="port">
    {contact_block(c)}
  </div>
</section>'''
    page(c, f'{c.t("ab.banner")} | {c.t("intro.title")}', c.t("intro.text"), ["home", "news", "pages"], "about", about)

    # News list
    c = Ctx(lang, "tin-tuc/")
    news = f'''{banner_page(c, "balcony-view", c.t("nw.banner"))}
<section>
  <div class="port with-sidebar">
    <div><ul class="news-list">{news_list(c)}</ul></div>
    {sidebar(c)}
  </div>
</section>'''
    page(c, f'{c.t("nw.title")} | {c.t("intro.title")}', c.t("nw.bannersub"), ["home", "news"], "news", news)

    # Articles
    for n in NEWS:
        c = Ctx(lang, f'tin-tuc/{n["id"]}/')
        title = c.pick(n["title"])
        art = f'''{banner_page(c, n["img"], title, "is-post")}
<section>
  <div class="port with-sidebar is-article">
    <article class="article"><h2 class="headline">{e(title)}</h2><div class="article-body">{article_body(c, n)}</div></article>
    {sidebar(c)}
  </div>
</section>'''
        desc = c.pick(n["body"])
        page(c, f'{title} | {c.t("intro.title")}', desc[:157] + ("…" if len(desc) > 157 else ""), ["home", "news"], "news", art, og_img=n["img"])

    # Booking (interactive widget rendered by js/booking.js in this page's language)
    c = Ctx(lang, "dat-phong/")
    booking = f'''{banner_page(c, "suite-sunset", c.t("bk.banner"))}
<section class="bk-sec" id="terms">
  <div class="port">
    <p class="bk-save">{e(c.t("box.sub"))}</p>
    <div class="tl" id="tl">{booking_widget(c)}</div>
  </div>
</section>
<div class="gateway" id="gateway" hidden><div><i></i><p>{e(c.t("pay.proc"))}</p></div></div>'''
    page(c, f'{c.t("bk.banner")} | {c.t("intro.title")}', c.t("bk.bannersub"), ["booking"], "book", booking, scripts=["booking"])


for l in LANGS:
    if l != DEFAULT and os.path.isdir(l):
        shutil.rmtree(l)  # regenerated below
for l in LANGS:
    build(l)
    build_packages(l)
    build_services(l)
    build_gallery(l)

# sitemap with hreflang alternates
slugs = ["", "gioi-thieu/", "goi-luu-tru/", "dich-vu/", "thu-vien-anh/", "tin-tuc/", "dat-phong/"] + [f'goi-luu-tru/{P[i]["slug"]}/' for i in sorted(P)] + [f'tin-tuc/{n["id"]}/' for n in NEWS]
urls = ""
for s in slugs:
    for l in LANGS:
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{lang_url(x, s)}"/>' for x in LANGS)
        urls += f"  <url><loc>{lang_url(l, s)}</loc>{alts}</url>\n"
open("sitemap.xml", "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")
print("built", len(LANGS), "languages x", len(slugs), "pages")
