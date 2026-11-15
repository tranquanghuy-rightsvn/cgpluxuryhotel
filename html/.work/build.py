#!/usr/bin/env python3
"""Static multi-language build of the diamondseahotel.com clone (content: CGP Luxury Hotel).

Every language gets its own pre-rendered pages (SEO):
  vi -> /            en -> /en/   ko -> /ko/   zh -> /zh/   ru -> /ru/   de -> /de/
  pages: ""  gioi-thieu/  tin-tuc/  tin-tuc/<id>/  dat-phong/
Text comes from js/i18n.js + js/data.js (exported by .work/export.cjs -> .work/i18n.json).
Run from the html/ folder:  node .work/export.cjs && python3 .work/build.py
"""
import html as H, json, os, re, shutil, subprocess, time

SITE = ""  # set to "https://your-domain" before going live (hreflang/canonical need absolute URLs)
VER = time.strftime("%Y%m%d%H%M")
subprocess.run(["node", ".work/export.cjs"], check=True, stdout=subprocess.DEVNULL)
D = json.load(open(".work/i18n.json", encoding="utf-8"))
LANGS = D["langs"]
DEFAULT = "vi"
P = {p["id"]: p for p in D["P"]}
NEWS = D["NEWS"]
NAMES = {"vi": "Tiếng Việt", "en": "English", "ko": "한국어", "zh": "中文", "ru": "Русский", "de": "Deutsch"}
FLAGS = {"vi": "vi.png", "en": "en.png", "ko": "ko.svg", "zh": "zh.svg", "ru": "ru.svg", "de": "de.svg"}
LOCALE = {"vi": "vi_VN", "en": "en_GB", "ko": "ko_KR", "zh": "zh_CN", "ru": "ru_RU", "de": "de_DE"}

MAP = "https://www.google.com/maps?q=78+Tr%E1%BA%A7n+Kh%C3%A1t+Ch%C3%A2n,+H%E1%BB%99i+An,+Qu%E1%BA%A3ng+Nam&z=15&output=embed"
FB = "https://www.facebook.com/profile.php?id=61564529174870"
PHONE, PHONE_TEL, EMAIL = "(+84) 98 924 46 24", "+84989244624", "cgpluxuryhotelhoian@gmail.com"
PKG_MENU = [6, 2, 3, 4, 9, 10, 11]

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


def lang_url(lang, slug):
    return SITE + "/" + ("" if lang == DEFAULT else lang + "/") + slug


# ------------------------------------------------------------------ layout
def header(c, cur):
    def a(slug, key, name):
        cls = ' class="is-current"' if cur == name else ""
        return f'<a href="{c.url(slug)}"{cls}>{e(c.t(key))}</a>'
    sub = "".join(f'<li><a href="{c.url("dat-phong/")}?pkg={i}">{e(c.name(i))}</a></li>' for i in PKG_MENU)
    langs = "".join(
        f'<li><a href="{c.R + ("" if l == DEFAULT else l + "/") + c.slug or "./"}" hreflang="{l}" lang="{l}"{" class=is-active" if l == c.lang else ""}>'
        f'<img src="{c.R}images/flags/{FLAGS[l]}" alt="">{NAMES[l]}</a></li>' for l in LANGS)
    return f'''<header class="site-header">
  <div class="port">
    <div class="header-bar">
      <button type="button" class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
      <a class="logo" href="{c.home}" aria-label="CGP Luxury Hotel"><span class="logo-mark">CGP</span><span class="logo-name">Luxury Hotel</span><span class="logo-stars">★★★★</span></a>
      <nav class="nav">
        <ul class="menu">
          <li>{a("", "nav.home", "home")}</li>
          <li>{a("gioi-thieu/", "nav.about", "about")}</li>
          <li><a href="{c.home}#packages">{e(c.t("nav.packages"))}</a><ul class="sub-menu">{sub}</ul></li>
          <li><a href="{c.home}#services">{e(c.t("nav.services"))}</a></li>
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
        <li><a href="{c.home}#packages">{e(c.t("nav.packages"))}</a></li>
        <li><a href="{c.home}#services">{e(c.t("nav.services"))}</a></li>
        <li><a href="{c.url("tin-tuc/")}">{e(c.t("nav.news"))}</a></li>
        <li><a href="{c.url("dat-phong/")}">{e(c.t("nav.book"))}</a></li>
      </ul>
    </div>
    <div>
      <h4>{e(c.t("f.policy"))}</h4>
      <ul class="f-links">
        <li><a href="{c.url("dat-phong/")}">{e(c.t("f.terms"))}</a></li>
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


def page(c, title, desc, css, cur, body, scripts=(), og_img="exterior-night"):
    links = "".join(f'<link rel="stylesheet" href="{c.R}css/{x}.css?v={VER}">\n' for x in ["fonts", "main"] + list(css))
    js = "".join(f'<script src="{c.R}js/{s}.js?v={VER}"></script>\n' for s in ["i18n", "data", "main"] + list(scripts))
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
                   for n in ["room-double-balcony", "suite-gold", "exterior-day", "room-twin-window", "suite-lounge"])
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
                  f'<a class="tile-hover" href="{c.url("dat-phong/")}"><span class="tile-label">{s}</span><strong class="tile-title">{t}</strong></a></figure>')
    return f'''<section class="svc-head" id="services">
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
        out += (f'<article class="post"><a class="post-img" href="{c.url("dat-phong/")}?pkg={i}" data-detail="{i}"><img src="{c.img(p["img"])}" alt="{n}" loading="lazy" width="660" height="440"></a>'
                f'<div class="post-body"><h3 class="post-title"><a href="{c.url("dat-phong/")}?pkg={i}" data-detail="{i}">{n}</a></h3>'
                f'<div class="post-btns"><a class="btn" href="{c.url("dat-phong/")}?pkg={i}" data-detail="{i}">{e(c.t("btn.details"))}</a>'
                f'<a class="btn" href="{c.url("dat-phong/")}?pkg={i}">{e(c.t("btn.book"))}</a></div></div></article>')
    return out


def room_cards(c, ids):
    out = ""
    for k, i in enumerate(ids):
        p, n = P[i], e(c.name(i))
        href = f'{c.url("dat-phong/")}?pkg={i}'
        out += (f'<article class="room{" is-wide" if k > 2 else ""}"><a class="room-img" href="{href}" data-detail="{i}"><img src="{c.img(p["img"])}" alt="{n}" loading="lazy" width="660" height="440"></a>'
                f'<div class="room-body"><h3 class="room-title"><a href="{href}" data-detail="{i}">{n}</a></h3><p class="room-text">{e(c.pick(p["tag"]))}</p>'
                f'<div class="room-foot"><a class="btn" href="{href}" data-detail="{i}">{e(c.t("btn.detailsShort"))}</a>'
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
    pk = "".join(f'<li><a href="{c.url("dat-phong/")}?pkg={i}"><img src="{c.img(P[i]["img"])}" alt="" loading="lazy"><span>{e(c.name(i))}</span></a></li>' for i in range(1, 8))
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


# ------------------------------------------------------------------ pages
def build(lang):
    # Home
    c = Ctx(lang, "")
    slides = "".join(f'<div class="banner-slide" style="background-image:url({c.img(n)})"></div>' for n in ["exterior-night", "suite-sunset", "balcony-view", "room-twin-window", "suite-gold"])
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

<section class="rooms" id="packages">
  <div class="port">
    <h2 class="headline dash">{e(c.t("pk.title"))}</h2>
    <div class="rooms-grid">{room_cards(c, [1, 5, 8, 7, 11, 12, 13])}</div>
  </div>
</section>

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
    page(c, f'{c.t("intro.title")} | {c.t("box.sub")}', c.t("intro.text"), ["home"], "home", home)

    # About
    c = Ctx(lang, "gioi-thieu/")
    about = f'''{banner_page(c, "exterior-night", c.t("ab.banner"))}
<section class="intro about-sec">
  <div class="port">
    {intro_block(c, "h2")}
  </div>
</section>
{services_block(c)}
<section class="intro" style="padding:40px 0 60px">
  <div class="port">
    {contact_block(c)}
  </div>
</section>'''
    page(c, f'{c.t("ab.banner")} | {c.t("intro.title")}', c.t("intro.text"), ["home", "news"], "about", about)

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
    <div class="tl" id="tl"><noscript><p style="padding:32px">{e(c.t("bk.bannersub"))} — {PHONE} · {EMAIL}</p></noscript></div>
  </div>
</section>
<div class="gateway" id="gateway" hidden><div><i></i><p>{e(c.t("pay.proc"))}</p></div></div>'''
    page(c, f'{c.t("bk.banner")} | {c.t("intro.title")}', c.t("bk.bannersub"), ["booking"], "book", booking, scripts=["booking"])


for l in LANGS:
    if l != DEFAULT and os.path.isdir(l):
        shutil.rmtree(l)  # regenerated below
for l in LANGS:
    build(l)

# sitemap with hreflang alternates
slugs = ["", "gioi-thieu/", "tin-tuc/", "dat-phong/"] + [f'tin-tuc/{n["id"]}/' for n in NEWS]
urls = ""
for s in slugs:
    for l in LANGS:
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{lang_url(x, s)}"/>' for x in LANGS)
        urls += f"  <url><loc>{lang_url(l, s)}</loc>{alts}</url>\n"
open("sitemap.xml", "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")
print("built", len(LANGS), "languages x", len(slugs), "pages")
