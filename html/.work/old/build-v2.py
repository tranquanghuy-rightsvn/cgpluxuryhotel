#!/usr/bin/env python3
"""Generate the static pages of the diamondseahotel.com clone (content: CGP Luxury Hotel).
Header/footer HTML is repeated per page (no server includes). Run from the html/ folder."""
import os, re, time
VER = time.strftime("%Y%m%d%H%M")

MAP = "https://www.google.com/maps?q=78+Tr%E1%BA%A7n+Kh%C3%A1t+Ch%C3%A2n,+H%E1%BB%99i+An,+Qu%E1%BA%A3ng+Nam&z=15&output=embed"
FB = "https://www.facebook.com/profile.php?id=61564529174870"
PHONE, PHONE_TEL, EMAIL = "(+84) 98 924 46 24", "+84989244624", "cgpluxuryhotelhoian@gmail.com"
NEWS_IDS = ["goi-luu-tru", "kham-pha-hoi-an", "solo-traveller", "dat-phong-online"]
PKG_MENU = [(6, "Complete Stay Experience"), (2, "Romantic Escape"), (3, "Honeymoon Package"), (4, "Family Holiday"),
            (9, "Work &amp; Relax Package"), (10, "CGP Signature Luxury Stay"), (11, "Solo Escape")]

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
}


def header(R, cur):
    def a(href, key, label, name):
        c = ' class="is-current"' if cur == name else ""
        return f'<a href="{href}"{c} data-i18n="{key}">{label}</a>'
    sub = "".join(f'<li><a href="{R}dat-phong/?pkg={i}">{n}</a></li>' for i, n in PKG_MENU)
    return f'''<header class="site-header">
  <div class="port">
    <div class="header-bar">
      <button type="button" class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
      <a class="logo" href="{R or './'}" aria-label="CGP Luxury Hotel"><span class="logo-mark">CGP</span><span class="logo-name">Luxury Hotel</span><span class="logo-stars">★★★★</span></a>
      <nav class="nav">
        <ul class="menu">
          <li>{a(R or "./", "nav.home", "Home", "home")}</li>
          <li>{a(R + "gioi-thieu/", "nav.about", "About", "about")}</li>
          <li>{a((R or "./") + "#packages", "nav.packages", "Packages", "")}<ul class="sub-menu">{sub}</ul></li>
          <li>{a((R or "./") + "#services", "nav.services", "Services", "")}</li>
          <li>{a(R + "tin-tuc/", "nav.news", "News", "news")}</li>
          <li>{a(R + "dat-phong/", "nav.book", "Book now", "book")}</li>
        </ul>
      </nav>
      <div class="lang"><button type="button" class="lang-btn" aria-label="Language"></button><ul class="lang-menu"></ul></div>
    </div>
  </div>
</header>'''


def footer(R):
    return f'''<footer class="site-footer">
  <div class="port">
    <div class="f-info">
      <h4>CGP Luxury Hotel</h4>
      <p><strong>Premium CGP Hotel Hoi An</strong></p>
      <p><span data-i18n="f.addr">Address:</span> <span data-i18n="c.addrv">78 Tran Khat Chan, Hoi An City, Quang Nam, Vietnam</span></p>
      <p><span data-i18n="f.phone">Phone:</span> <a href="tel:{PHONE_TEL}">{PHONE}</a></p>
      <p><span data-i18n="f.hotline">Hotline:</span> <a href="tel:{PHONE_TEL}">{PHONE}</a></p>
      <p><span data-i18n="f.email">Email:</span> <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
    <div>
      <h4 data-i18n="f.quick">Quick Link</h4>
      <ul class="f-links">
        <li><a href="{R}gioi-thieu/" data-i18n="nav.about">About Us</a></li>
        <li><a href="{R or "./"}#packages" data-i18n="nav.packages">Packages</a></li>
        <li><a href="{R or "./"}#services" data-i18n="nav.services">Services</a></li>
        <li><a href="{R}tin-tuc/" data-i18n="nav.news">News</a></li>
        <li><a href="{R}dat-phong/" data-i18n="nav.book">Book now</a></li>
      </ul>
    </div>
    <div>
      <h4 data-i18n="f.policy">Terms &amp; Conditions</h4>
      <ul class="f-links">
        <li><a href="{R}dat-phong/" data-i18n="f.terms">Terms &amp; Conditions</a></li>
        <li><a href="#" data-i18n="f.pay">Payment Policy</a></li>
        <li><a href="#" data-i18n="f.privacy">Information Security Policy</a></li>
        <li><a href="#" data-i18n="f.refund">Return and refund Policy</a></li>
      </ul>
    </div>
    <div>
      <h4 data-i18n="f.find">Find us on</h4>
      <div class="social">
        <a href="{FB}" target="_blank" rel="noopener" aria-label="Facebook">{SVG["fb"]}</a>
        <a href="https://wa.me/{PHONE_TEL[1:]}" target="_blank" rel="noopener" aria-label="WhatsApp">{SVG["wa"]}</a>
        <a href="mailto:{EMAIL}" aria-label="Email">{SVG["at"]}</a>
      </div>
    </div>
  </div>
</footer>'''


def page(path, R, title, css, cur, body, scripts=()):
    links = "".join(f'<link rel="stylesheet" href="{R}css/{c}.css?v={VER}">\n' for c in ["fonts", "main"] + list(css))
    js = "".join(f'<script src="{R}js/{s}.js?v={VER}"></script>\n' for s in ["i18n", "data", "main"] + list(scripts))
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{links}</head>
<body data-root="{R}">
{header(R, cur)}
<main>
{body}
</main>
{footer(R)}
{js}</body>
</html>
'''
    if path.endswith("/"): path += "index.html"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(path, "w", encoding="utf-8").write(html)


def banner_page(R, img, key, text, cls=""):
    attr = f' data-i18n="{key}"' if key else " data-post-title"
    return f'''<section class="banner-page" style="background-image:url({R}images/{img}.jpg)">
  <div class="port"><h1 class="{cls}"{attr}>{text}</h1></div>
</section>'''


INTRO = "Set in a quiet area close to the centre of Hoi An, CGP Luxury Hotel offers a refined stay with modern design, premium amenities, elegant spaces and attentive service around the clock."


def intro_block(R):
    imgs = "".join(f'\n        <img src="{R}images/{n}.jpg" alt="" loading="lazy" width="1320" height="880">' for n in ["room-double-balcony", "suite-gold", "exterior-day", "room-twin-window", "suite-lounge"])
    return f'''<div class="intro-row">
      <div class="intro-card">
        <h1 class="headline dash" data-i18n="intro.title">CGP Luxury Hotel Hoi An</h1>
        <p data-i18n="intro.text">{INTRO}</p>
        <div class="btns">
          <a class="btn btn--sm" href="{R}gioi-thieu/" data-i18n="btn.details">View details</a>
          <a class="btn btn--sm" href="{R}dat-phong/" data-i18n="bt.bookroom">Book a room</a>
        </div>
      </div>
      <div class="intro-slider" data-fade="img">{imgs}
        <button type="button" class="arrow arrow--prev" aria-label="Previous"></button>
        <button type="button" class="arrow arrow--next" aria-label="Next"></button>
      </div>
    </div>'''


def contact_block():
    return f'''<div class="contact-row">
      <div class="map"><iframe src="{MAP}" title="Map" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      <div class="contact-card">
        <div class="c-item"><i>{SVG["pin"]}</i><div><h3 data-i18n="c.addr">Address</h3><p data-i18n="c.addrv">78 Tran Khat Chan, Hoi An City, Quang Nam, Vietnam</p></div></div>
        <div class="c-item"><i>{SVG["phone"]}</i><div><h3 data-i18n="c.phone">Phone</h3><a href="tel:{PHONE_TEL}">{PHONE}</a></div></div>
        <div class="c-item"><i>{SVG["mail"]}</i><div><h3 data-i18n="c.email">Email</h3><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
      </div>
    </div>'''


def services_block(R):
    tiles = "".join(
        f'<figure class="tile"><img src="{R}images/{img}.jpg" alt="" loading="lazy" width="660" height="440">'
        f'<figcaption class="tile-cap"><span class="tile-label" data-i18n="tile{i}.s">{s}</span><strong class="tile-title" data-i18n="tile{i}.t">{t}</strong></figcaption>'
        f'<a class="tile-hover" href="{R}dat-phong/"><span class="tile-label" data-i18n="tile{i}.s">{s}</span><strong class="tile-title" data-i18n="tile{i}.t">{t}</strong></a></figure>'
        for i, (img, s, t) in enumerate([("pool", "Relax", "Outdoor swimming pool"), ("balcony-view", "Views", "Balcony with rice-field views"),
                                         ("bathtub", "Bathroom", "Relaxing bathtub"), ("suite-gold", "Stay", "Elegant rooms &amp; suites")], 1))
    return f'''<section class="svc-head" id="services">
  <div class="port">
    <h2 class="headline dash" data-i18n="svc.title">Featured Services</h2>
    <p class="sub-title" data-i18n="svc.text">Whether you are here for a short weekend break or a longer holiday, enjoy modern comforts together with warm Vietnamese hospitality.</p>
  </div>
</section>
<section class="svc-tiles">{tiles}</section>'''


def sidebar(R):
    return f'''<aside class="sidebar">
      <section><h3 class="widget-title" data-i18n="sb.search">Search site</h3>
        <form class="search-box" role="search"><input type="search" data-i18n-ph="sb.looking" placeholder="Looking for..."><button type="submit" aria-label="Search">{SVG["search"]}</button></form></section>
      <section><h3 class="widget-title" data-i18n="sb.recent">Recent Posts</h3><ul class="side-list" data-render="recent"></ul></section>
      <section><h3 class="widget-title" data-i18n="sb.list">Package List</h3><ul class="side-list" data-render="pkglist"></ul></section>
    </aside>'''


# ---------------- Home ----------------
R = ""
slides = "".join(f'<div class="banner-slide" style="background-image:url(images/{n}.jpg)"></div>' for n in ["exterior-night", "suite-sunset", "balcony-view", "room-twin-window", "suite-gold"])
home = f'''<section class="banner" data-fade=".banner-slide" data-auto="6000" data-loop="1">
  {slides}
  <button type="button" class="slick-arrow slick-prev" aria-label="Previous"></button>
  <button type="button" class="slick-arrow slick-next" aria-label="Next"></button>
  <div class="dots"></div>
  <div class="banner-content">
    <div class="port">
      <div class="book-box">
        <form class="sfl" action="dat-phong/" method="get">
          <div class="sfl-title" data-i18n="box.title">Book rooms</div>
          <div class="sfl-sub" data-i18n="box.sub">Save more when you book on the website</div>
          <div class="sfl-grid">
            <label class="sfl-field"><span data-i18n="box.checkin">Check-in</span><output data-show="checkin"></output><input class="sfl-native" type="date" name="checkin" required><i>{SVG["cal"]}</i></label>
            <label class="sfl-field"><span data-i18n="box.checkout">Check-out</span><output data-show="checkout"></output><input class="sfl-native" type="date" name="checkout" required><i>{SVG["cal"]}</i></label>
            <label class="sfl-field"><span data-i18n="box.guests">Guests</span>
              <select name="adults"><option value="1" data-i18n="g.a1">1 adult</option><option value="2" selected data-i18n="g.a2">2 adults</option><option value="3" data-i18n="g.a3">3 adults</option><option value="4" data-i18n="g.a4">4 adults</option></select><i>{SVG["user"]}</i></label>
            <button type="button" class="sfl-promo" data-i18n="box.promo">I have a promotional code</button>
            <input class="sfl-promo-input" type="text" name="promo" maxlength="20" autocomplete="off" data-i18n-ph="box.promoph" hidden>
            <button type="submit" class="sfl-submit" data-i18n="box.cta">Book now</button>
            <a class="sfl-auth" href="dat-phong/">{SVG["user"]}<span data-i18n="sfl.login">Log in</span></a>
          </div>
        </form>
      </div>
    </div>
  </div>
</section>

<section class="intro">
  <div class="port">
    {intro_block(R)}
    {contact_block()}
  </div>
</section>

<section class="posts-sec">
  <div class="port">
    <h2 class="headline dash" data-i18n="feat.title">Featured Packages</h2>
    <div class="carousel">
      <div class="carousel-view"><div class="carousel-track" data-render="featured" data-ids="6,2,3,4,10,9,12"></div></div>
      <button type="button" class="arrow arrow--prev" aria-label="Previous"></button>
      <button type="button" class="arrow arrow--next" aria-label="Next"></button>
    </div>
    <div class="dots"></div>
  </div>
</section>

{services_block(R)}

<section class="rooms" id="packages">
  <div class="port">
    <h2 class="headline dash" data-i18n="pk.title">Stay Packages</h2>
    <div class="rooms-grid" data-render="rooms" data-ids="1,5,8,7,11,12,13"></div>
  </div>
</section>

<section class="news-sec">
  <div class="port">
    <h2 class="headline dash" data-i18n="nw.title">News &amp; Events</h2>
    <div class="carousel">
      <div class="carousel-view"><div class="carousel-track" data-render="news"></div></div>
      <button type="button" class="arrow arrow--prev" aria-label="Previous" hidden></button>
      <button type="button" class="arrow arrow--next" aria-label="Next" hidden></button>
    </div>
  </div>
</section>'''
page("index.html", R, "CGP Luxury Hotel Hoi An | Official Website", ["home"], "home", home)

# ---------------- About ----------------
R = "../"
about = f'''{banner_page(R, "exterior-night", "ab.banner", "About Us")}
<section class="intro about-sec">
  <div class="port">
    {intro_block(R)}
  </div>
</section>
{services_block(R)}
<section class="intro" style="padding:40px 0 60px">
  <div class="port">
    {contact_block()}
  </div>
</section>'''
page("gioi-thieu/", R, "About Us | CGP Luxury Hotel Hoi An", ["home", "news"], "about", about)

# ---------------- News list ----------------
news = f'''{banner_page(R, "balcony-view", "nw.banner", "News")}
<section>
  <div class="port with-sidebar">
    <div><ul class="news-list" data-render="news-list"></ul></div>
    {sidebar(R)}
  </div>
</section>'''
page("tin-tuc/", R, "News | CGP Luxury Hotel Hoi An", ["home", "news"], "news", news)

# ---------------- News articles ----------------
R2 = "../../"
data = open("js/data.js", encoding="utf-8").read()
for nid in NEWS_IDS:
    m = re.search(r'id: "%s", date: "[^"]+", img: "([^"]+)",\s*title: \["[^"]*", "([^"]+)"' % nid, data)
    img, title_en = m.group(1), m.group(2)
    art = f'''{banner_page(R2, img, None, title_en, "is-post")}
<section>
  <div class="port with-sidebar is-article">
    <article class="article"><h2 class="headline" data-post-title>{title_en}</h2><div class="article-body" data-render="article" data-id="{nid}"></div></article>
    {sidebar(R2)}
  </div>
</section>'''
    page(f"tin-tuc/{nid}/index.html", R2, f"{title_en} | CGP Luxury Hotel", ["home", "news"], "news", art)

# ---------------- Booking ----------------
booking = f'''{banner_page(R, "suite-sunset", "bk.banner", "Book Now")}
<section class="bk-sec" id="terms">
  <div class="port">
    <p class="bk-save" data-i18n="box.sub">Save more when you book on the website</p>
    <div class="tl" id="tl"></div>
  </div>
</section>
<div class="gateway" id="gateway" hidden><div><i></i><p data-i18n="pay.proc">Connecting to the PayOne payment gateway…</p></div></div>'''
page("dat-phong/", R, "Book Now | CGP Luxury Hotel Hoi An", ["booking"], "book", booking, scripts=["booking"])
print("built")
