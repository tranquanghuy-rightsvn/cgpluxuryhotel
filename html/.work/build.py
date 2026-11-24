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


SITE = "https://cgpgrouphotel.com"  # absolute base for canonical / hreflang / sitemap / og / JSON-LD
VER = time.strftime("%Y%m%d%H%M")
subprocess.run(["node", ".work/export.cjs"], check=True, stdout=subprocess.DEVNULL)
D = json.load(open(".work/i18n.json", encoding="utf-8"))
LANGS = D["langs"]
DEFAULT = "vi"
P = {p["id"]: p for p in D["P"]}
for _p in P.values():
    _p["slug"] = slugify(_p["names"][1])
NEWS = D["NEWS"]

# extra content for the Nov 2026 photo set (.work/extra_i18n.py)
import sys
sys.path.insert(0, ".work")
import extra_i18n as X
for _k, _v in X.T.items():
    for _i, _l in enumerate(LANGS):
        D["T"][_l][_k] = _v[_i]
D["INC"]["famroom"] = X.FAMROOM
for _iso, _v in X.SHORT.items():
    for _i, _l in enumerate(LANGS):
        D["short"][_l][_iso] = _v[_i]
for _n in NEWS:
    _n.update(X.NEWS_EXTRA.get(_n["id"], {}))
NEWS = X.NEWS_NEW + NEWS

# Smart content news (replaces the short news above): ../content/tin-tuc/<slug>/<lang>.html, each starting with
# <!-- smart-content\ntitle: ...\ndescription: ...\ncover: <image name>\ndate: YYYY-MM-DD\n--> followed by the
# designed article body (tv-* blocks, css/blocks.css). Placeholders expanded per page by smart_html():
#   <img data-img="name" [data-sizes="..."] alt="...">  -> responsive WebP <img>
#   href="@/path/"                                       -> link in the page's language
#   <div data-gallery="a b c"></div>                     -> thumbnail grid + lightbox
#   <i data-ic="name"></i>                               -> inline SVG icon (SC_ICONS)
SMART_DIR = "../content/tin-tuc"
def _smart_meta(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"\s*<!--\s*smart-content\s*\n(.*?)-->\s*", raw, re.S)
    meta = dict(l.split(":", 1) for l in m.group(1).strip().split("\n"))
    return {k.strip(): v.strip() for k, v in meta.items()}, raw[m.end():]
if os.path.isdir(SMART_DIR):
    _smart = []
    for _slug in sorted(os.listdir(SMART_DIR)):
        _dir = f"{SMART_DIR}/{_slug}"
        if not os.path.isfile(f"{_dir}/vi.html"):
            continue
        _vi, _ = _smart_meta(f"{_dir}/vi.html")
        _n = {"id": _slug, "date": _vi["date"], "img": _vi["cover"], "title": [], "body": [], "html": [], "smart": True}
        for _l in LANGS:
            _f = f"{_dir}/{_l}.html" if os.path.isfile(f"{_dir}/{_l}.html") else f"{_dir}/vi.html"
            _m, _html = _smart_meta(_f)
            _n["title"].append(_m["title"]); _n["body"].append(_m["description"]); _n["html"].append(_html)
        _n["imgs"] = []  # gallery photos come from the body itself
        _smart.append(_n)
    if _smart:
        NEWS = sorted(_smart, key=lambda n: n["date"], reverse=True)

# responsive images: images/webp/<name>-<w>.webp at several widths (never upscaled) + intrinsic sizes
# news images keep the plain JPEG (+ images/thumbs/<name>.jpg) as before.
from concurrent.futures import ThreadPoolExecutor
WIDTHS = (480, 640, 800, 1200, 1600)
DIMS, VARIANTS = {}, {}
for _line in subprocess.run(["magick", "identify", "-format", "%t %w %h\n"] + sorted(f"images/{f}" for f in os.listdir("images") if f.endswith(".jpg")),
                            capture_output=True, text=True, check=True).stdout.split("\n"):
    if _line.strip():
        _n, _w, _h = _line.split()
        DIMS[_n] = (int(_w), int(_h))
        VARIANTS[_n] = [w for w in WIDTHS if w < int(_w)] + [min(int(_w), WIDTHS[-1])]
os.makedirs("images/webp", exist_ok=True)
_jobs, _keep = [], set()
for _n, _ws in VARIANTS.items():
    for _w in _ws:
        _dst = f"images/webp/{_n}-{_w}.webp"
        _keep.add(os.path.basename(_dst))
        if not os.path.exists(_dst) or os.path.getmtime(_dst) < os.path.getmtime(f"images/{_n}.jpg"):
            _jobs.append((f"images/{_n}.jpg", _dst, _w))
def _webp(job):
    src, dst, w = job
    subprocess.run(["cwebp", "-quiet", "-q", "78", "-m", "5", "-resize", str(w), "0", src, "-o", dst], check=True)
with ThreadPoolExecutor(8) as _ex:
    list(_ex.map(_webp, _jobs))
for _f in os.listdir("images/webp"):
    if _f not in _keep:
        os.remove("images/webp/" + _f)

# JPEG thumbnails only for the news pages
_news_imgs = {x for n in NEWS for x in [n["img"]] + n.get("imgs", [])} | {p["img"] for p in P.values()}  # + package photos in the news sidebar
os.makedirs("images/thumbs", exist_ok=True)
for _n in _news_imgs:
    _src, _dst = f"images/{_n}.jpg", f"images/thumbs/{_n}.jpg"
    if not os.path.exists(_dst) or os.path.getmtime(_dst) < os.path.getmtime(_src):
        subprocess.run(["magick", _src, "-resize", "720x720>", "-strip", "-quality", "78", "-interlace", "Plane", _dst], check=True)
for _f in os.listdir("images/thumbs"):
    if _f[:-4] not in _news_imgs:
        os.remove("images/thumbs/" + _f)

# Banners: one pre-cropped WebP per screen class (mobile <=600 / tablet <=991 / desktop), served with <picture>.
# Each crop ratio is the *narrowest* box ratio of that class (measured: home banner 508px tall on mobile, 600px on
# tablet; page banner 260px tall up to 991px, 384px above), so object-fit: cover shows exactly what it showed with
# the full photo -- only the pixels that were never visible are dropped.
BANNER_MQ = ("(max-width: 600px)", "(min-width: 601px) and (max-width: 991px)", "(min-width: 992px)")
BANNER_CROPS = {"hero": ((0.55, 480), (0.98, 1100), (0, 1920)),   # (min width/height ratio, max output width)
                "page": ((1.2, 640), (2.3, 1200), (2.55, 1920))}
os.makedirs("images/banner", exist_ok=True)
_banner_keep = set()
def banner_file(n, kind, k):
    """images/banner/<n>-<kind>-<m|t|d>.webp -> (path from root, width, height); generated when missing/stale."""
    a, cap = BANNER_CROPS[kind][k]
    W, H = DIMS[n]
    cw, ch = (round(H * a), H) if a and W / H > a else ((W, round(W / a)) if a and W / H < a else (W, H))
    ow = min(cw, cap); oh = round(ch * ow / cw)
    rel = f"images/banner/{n}-{kind}-{'mtd'[k]}.webp"
    _banner_keep.add(os.path.basename(rel))
    if not os.path.exists(rel) or os.path.getmtime(rel) < os.path.getmtime(f"images/{n}.jpg"):
        subprocess.run(["magick", f"images/{n}.jpg", "-gravity", "center", "-crop", f"{cw}x{ch}+0+0", "+repage",
                        "-resize", f"{ow}x", "-strip", "-quality", "76", "-define", "webp:method=6", rel], check=True)
    return rel, ow, oh

# social share images: 1200x630 JPEG (the size Facebook / Zalo / X expect)
os.makedirs("images/og", exist_ok=True)
def og_file(n):
    rel = f"images/og/{n}.jpg"
    if not os.path.exists(rel) or os.path.getmtime(rel) < os.path.getmtime(f"images/{n}.jpg"):
        subprocess.run(["magick", f"images/{n}.jpg", "-resize", "1200x630^", "-gravity", "center", "-extent", "1200x630",
                        "-strip", "-quality", "82", "-interlace", "Plane", rel], check=True)
    return rel

# branded share image (every page's og:image): .work/og-share.html rendered by headless Chrome -> images/og/share.jpg
SHARE_IMG = "images/og/share.jpg"
_tpl = ".work/og-share.html"
if not os.path.exists(SHARE_IMG) or os.path.getmtime(SHARE_IMG) < max(os.path.getmtime(_tpl), os.path.getmtime("images/hero-facade-night.jpg")):
    _png = "images/og/_share.png"
    subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1200,630", "--virtual-time-budget=3000", "--allow-file-access-from-files",
                    "--screenshot=" + os.path.abspath(_png), "file://" + os.path.abspath(_tpl)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["magick", _png, "-strip", "-quality", "86", "-interlace", "Plane", SHARE_IMG], check=True)
    os.remove(_png)
SHARE_ALT = "CGP Group - CGP Luxury Hotel Hoi An"

# header logo: shown 90px tall (~140px wide) -> 420px WebP covers 3x screens (the PNG is 557px / 105 KB)
if not os.path.exists("images/logo.webp") or os.path.getmtime("images/logo.webp") < os.path.getmtime("images/logo.png"):
    subprocess.run(["magick", "images/logo.png", "-resize", "420x", "-strip", "-quality", "90", "-define", "webp:method=6", "images/logo.webp"], check=True)
LOGO_WH = tuple(int(x) for x in subprocess.run(["magick", "identify", "-format", "%w %h", "images/logo.webp"], capture_output=True, text=True, check=True).stdout.split())
NAMES = {"vi": "Tiếng Việt", "en": "English", "ko": "한국어", "zh": "中文", "ru": "Русский", "de": "Deutsch"}
FLAGS = {"vi": "vi.png", "en": "en.png", "ko": "ko.svg", "zh": "zh.svg", "ru": "ru.svg", "de": "de.svg"}
LOCALE = {"vi": "vi_VN", "en": "en_GB", "ko": "ko_KR", "zh": "zh_CN", "ru": "ru_RU", "de": "de_DE"}

# Google Maps: official embed endpoint (/maps/embed?pb=...) — the old "?q=...&output=embed" form 301-redirects with
# X-Frame-Options: SAMEORIGIN, which some mobile browsers (Android) refuse to show inside an iframe.
import base64 as _b64, urllib.parse as _up
MAP_QUERY = "CGP Luxury Hotel, 67 Lý Thường Kiệt, Hội An"
MAP = "https://www.google.com/maps/embed?pb=!1m3!2m1!1z" + _b64.b64encode(MAP_QUERY.encode()).decode().rstrip("=") + "!6i16"
# Maps URLs API: opens the Google Maps app on Android/iOS, the website elsewhere
MAP_LINK = "https://www.google.com/maps/search/?api=1&query=" + _up.quote(MAP_QUERY)
FB = "https://www.facebook.com/profile.php?id=61564529174870"
PHONE, PHONE_TEL, EMAIL = "(+84) 905 926 638", "+84905926638", "cgpluxuryhotelhoian@gmail.com"
PKG_MENU = [6, 2, 3, 4, 9, 10, 11]
CATS = ["relax", "romance", "family", "long", "sig", "solo"]
GALLERY_OLD = ["hero-facade-night", "hero-facade-day", "room-pool-view", "suite-arch-romantic", "town-view-window", "room-petals-balcony",
           "grand-suite-arch", "suite-onyx-front", "towel-hearts", "bath-glass-view", "family-ricefield-view", "balcony-view",
           "deluxe-gold-panel", "suite-onyx", "bath-rose", "marble-double", "family-twin-balcony", "suite-sunset",
           "suite-gold", "room-romantic", "bathtub", "suite-onyx-window", "suite-sofa-curtains", "marble-room",
           "standard-double", "bathroom-classic", "room-window", "room-twin", "room-twin-window", "room-double-balcony",
           "room-bathtub-view", "room-desk", "room-sofa", "suite-lounge", "suite-arch", "pool"]
PKG_PHOTOS = {1: ["room-pool-view", "town-view-window", "bath-glass-view", "pool-day-3", "floating-breakfast-1", "room-101-1"],
              2: ["towel-hearts", "room-petals-balcony", "bath-rose", "couple-bed-breakfast-1", "couple-balcony-2", "room-500-1"],
              3: ["suite-arch-romantic", "towel-hearts", "bath-rose", "couple-suite", "room-500-8", "couple-arch-door"],
              4: ["family-twin-balcony", "family-ricefield-view", "bathroom-classic", "room-501-2", "kids-pool-float", "kids-pool-jump"],
              5: ["standard-double", "marble-room", "bathroom-classic", "room-103-1", "room-502-1", "breakfast-table"],
              6: ["room-pool-view", "marble-double", "bath-glass-view", "room-301-2", "floating-breakfast-2", "garden-cafe-1"],
              7: ["room-petals-balcony", "suite-arch-romantic", "towel-hearts", "couple-bed-breakfast-3", "breakfast-couple-2", "room-500-2"],
              8: ["town-view-window", "deluxe-gold-panel", "family-ricefield-view", "guest-balcony-rice", "balcony-reading", "bike-couple-1"],
              9: ["marble-double", "standard-double", "suite-onyx-window", "room-103-4", "guest-window-coffee", "drink-tea"],
              10: ["grand-suite-arch", "suite-onyx-front", "bath-glass-view", "room-500-3", "room-500-12", "lobby-2"],
              11: ["suite-sofa-curtains", "suite-onyx", "town-view-window", "guest-suite-sofa", "pool-reading-hat", "guest-poolside-1"],
              12: ["suite-onyx-window", "bath-rose", "room-pool-view", "guest-pool-reading-1", "balcony-view-1", "drink-watermelon"],
              13: ["suite-onyx-front", "grand-suite-arch", "deluxe-gold-panel", "room-500-5", "guest-pool-ladder", "floating-breakfast-3"]}
GROUP_FILL = {"relax": ["pool-day-3", "lobby-2"], "family": ["room-501-3", "kids-pool-float"],
              "long": ["room-103-4", "guest-window-coffee"], "sig": ["room-500-1", "room-500-3"],
              "romance": ["couple-suite", "couple-bed-breakfast-2"], "solo": ["guest-suite-sofa", "balcony-reading"]}
SERVICES = [("s1", "pool", ["pool-day-2", "pool-day-4", "guest-poolside-2"]),
            ("s2", "breakfast-table", ["breakfast-couple-1", "couple-bed-breakfast-2", "breakfast-couple-3"]),
            ("s13", "restaurant-1", ["buffet-1", "buffet-2", "dish-egg-baguette"]),
            ("s14", "dish-chicken-rice", ["dish-herb-platter", "dish-fried-pastry", "dish-sandwich"]),
            ("s3", "bathtub", ["room-500-7", "room-500-15", "room-301-11"]),
            ("s4", "room-romantic", ["couple-bed-breakfast-3", "couple-arch-door", "couple-balcony-1"]),
            ("s5", "hero-facade-night", ["facade-bougainvillea-2", "lobby-1", "reception-desk"]),
            ("s6", "room-desk", ["room-103-4", "guest-window-coffee", "drink-tea"]),
            ("s7", "floating-breakfast-2", ["floating-breakfast-1", "floating-breakfast-3", "pool-reading-hat"]),
            ("s8", "bike-couple-1", ["facade-bougainvillea-3", "facade-bougainvillea-4", "facade-bougainvillea-5"]),
            ("s9", "garden-cafe-1", ["garden-cafe-2", "drink-orange", "drink-watermelon"]),
            ("s10", "staff-2", ["staff-1", "staff-4", "staff-5"]),
            ("s11", "reception-desk", ["lobby-checkin", "lobby-welcome", "lobby-4"]),
            ("s12", "kids-pool-jump", ["kids-pool-float", "room-501-1", "pool-day-1"])]

# room types (photo folders Phong 101 ... 502)
def _r(no, n): return [f"room-{no}-{k}" for k in range(1, n + 1)]
ROOMS = [("r1", _r(101, 7) + _r(102, 7)), ("r2", _r(103, 6)), ("r3", _r(301, 11)),
         ("r4", _r(500, 10)), ("r5", _r(501, 8)), ("r6", _r(502, 7))]
AMENITIES = [f"room-500-{k}" for k in range(11, 17)]
EXPERIENCES = [("ex1", "floating-breakfast-2"), ("ex2", "breakfast-table"), ("ex3", "guest-balcony-rice"),
               ("ex4", "bike-couple-1"), ("ex5", "garden-cafe-1"), ("ex6", "guest-poolside-3")]
GAL_SECTIONS = [
    ("c1", ["hero-facade-night", "hero-facade-day", "facade-bougainvillea-1", "facade-bougainvillea-2", "facade-bougainvillea-3",
            "facade-bougainvillea-4", "facade-bougainvillea-5", "pool-day-1", "pool-day-2", "pool-day-3", "pool-day-4", "pool",
            "hero-pool-night", "lobby-1", "lobby-2", "lobby-3", "lobby-4", "lobby-5", "garden-cafe-1", "garden-cafe-2", "garden-cafe-3", "restaurant-1"]),
    ("c2", [n for _, imgs in ROOMS for n in imgs] + AMENITIES + GALLERY_OLD[2:]),
    ("c3", ["buffet-1", "buffet-2", "dish-chicken-rice", "dish-herb-platter", "dish-fried-pastry", "dish-egg-baguette", "dish-sandwich",
            "floating-breakfast-1", "floating-breakfast-2", "floating-breakfast-3", "breakfast-table", "breakfast-couple-1",
            "breakfast-couple-2", "breakfast-couple-3", "couple-bed-breakfast-1", "couple-bed-breakfast-2", "couple-bed-breakfast-3",
            "drink-orange", "drink-watermelon", "drink-tea", "bike-couple-1", "guest-balcony-rice", "balcony-view-1", "balcony-view-2",
            "balcony-reading", "guest-window-coffee", "couple-balcony-1", "couple-balcony-2", "couple-suite", "couple-arch-door",
            "couple-poolside", "guest-suite-sofa", "guest-pool-door", "guest-poolside-1", "guest-poolside-2", "guest-poolside-3",
            "guest-poolside-4", "guest-pool-ladder", "guest-pool-reading-1", "guest-pool-reading-2", "pool-reading-hat",
            "kids-pool-jump", "kids-pool-float"]),
    ("c4", ["reception-desk", "lobby-checkin", "lobby-welcome", "staff-1", "staff-2", "staff-3", "staff-4", "staff-5", "staff-6"]),
]
GALLERY = GAL_SECTIONS[0][1][:4] + ["room-500-1", "room-101-1", "floating-breakfast-2", "room-301-2"]


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

BLANK = "data:image/gif;base64,R0lGODlhAQABAAAAACw="
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
        self.preload = ""               # <link rel=preload> for the LCP banner, filled by banner()

    def t(self, k): return D["T"][self.lang][k]
    def pick(self, arr): return arr[self.i]
    def name(self, pid): return self.pick(P[pid]["names"])
    def nights(self, n): return D["nights"][self.lang][str(n)]
    def date(self, iso):
        if iso in D["short"][self.lang]:
            return D["short"][self.lang][iso]
        y, m, d = (int(x) for x in iso.split("-"))
        ru = ["янв.", "февр.", "мар.", "апр.", "мая", "июн.", "июл.", "авг.", "сент.", "окт.", "нояб.", "дек."]
        de = ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sept.", "Okt.", "Nov.", "Dez."]
        return {"vi": f"{d} thg {m}, {y}", "en": f"{d} {time.strftime('%b', time.strptime(str(m), '%m'))} {y}", "ko": f"{y}년 {m}월 {d}일",
                "zh": f"{y}年{m}月{d}日", "ru": f"{d} {ru[m - 1]} {y} г.", "de": f"{d}. {de[m - 1]} {y}"}[self.lang]
    def url(self, slug=""): return self.L + slug if (self.L + slug) else "./"
    def img(self, n): return f"{self.R}images/{n}.jpg"
    def th(self, n): return f"{self.R}images/thumbs/{n}.jpg"
    def wh(self, n): w, h = DIMS[n]; return f'width="{w}" height="{h}"'
    def webp(self, n, w): return f"{self.R}images/webp/{n}-{w}.webp"
    def srcset(self, n): return ", ".join(f"{self.webp(n, w)} {w}w" for w in VARIANTS[n])
    def pic(self, n, sizes):
        """src (JPEG fallback) + WebP srcset + sizes + intrinsic width/height."""
        return f'src="{self.img(n)}" srcset="{self.srcset(n)}" sizes="{sizes}" {self.wh(n)}'
    def bgimg(self, n, eager=False):
        """Full-bleed responsive background photo (sits under the banner content, object-fit: cover)."""
        load = 'fetchpriority="high"' if eager else 'loading="lazy"'
        return f'<img class="bg-img" {self.pic(n, "100vw")} alt="" {load}>'
    def banner(self, n, kind, eager=False, defer=False):
        """Banner photo: <picture> with one WebP per screen class (mobile / tablet / desktop), see BANNER_CROPS."""
        files = [banner_file(n, kind, k) for k in range(3)]
        srcs = "".join(f'<source media="{BANNER_MQ[k]}" srcset="{self.R}{f}" width="{w}" height="{h}">' for k, (f, w, h) in enumerate(files[:2]))
        f, w, h = files[2]
        if eager:
            self.preload += "".join(f'<link rel="preload" as="image" type="image/webp" href="{self.R}{p}" media="{BANNER_MQ[k]}" fetchpriority="high">\n'
                                    for k, (p, _, _) in enumerate(files))
        load = 'fetchpriority="high"' if eager else 'loading="lazy"'
        if defer:  # hidden slider slides: js/main.js swaps data-* in after window "load", so they never compete with the LCP photo
            srcs = srcs.replace(" srcset=", " data-srcset=")
            return f'<picture>{srcs}<img class="bg-img" src="{BLANK}" data-src="{self.R}{f}" width="{w}" height="{h}" alt="" decoding="async"></picture>'
        return f'<picture>{srcs}<img class="bg-img" src="{self.R}{f}" width="{w}" height="{h}" alt="" {load} decoding="async"></picture>'
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
      <a class="logo" href="{c.home}" aria-label="CGP Luxury Hotel"><img src="{c.R}images/logo.webp" alt="CGP Luxury Hotel" width="{LOGO_WH[0]}" height="{LOGO_WH[1]}"></a>
      <nav class="nav">
        <ul class="menu">
          <li>{a("", "nav.home", "home")}</li>
          <li>{a("gioi-thieu/", "nav.about", "about")}</li>
          <li>{a("phong-nghi/", "nav.rooms", "rooms")}</li>
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
        <li><a href="{c.url("phong-nghi/")}">{e(c.t("nav.rooms"))}</a></li>
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


# ------------------------------------------------------------------ SEO
HOTEL_ID, SITE_ID = SITE + "/#hotel", SITE + "/#website"
SECTIONS = {"gioi-thieu/": "nav.about", "phong-nghi/": "nav.rooms", "goi-luu-tru/": "nav.packages", "dich-vu/": "nav.services",
            "thu-vien-anh/": "gal.title", "tin-tuc/": "nav.news", "dat-phong/": "nav.book"}
ROBOTS = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"


def clip(s, n=158):
    """Meta description length: cut at a word boundary, add an ellipsis."""
    s = " ".join(str(s).split())
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0] if " " in s[:n] else s[:n]
    return cut.rstrip(" ,.;:–-") + "…"


def hotel_ld(c, rooms=False):
    """Hotel entity (schema.org/Hotel) in the page language; rooms=True adds the room types."""
    h = {"@type": "Hotel", "@id": HOTEL_ID, "name": "CGP Luxury Hotel Hoi An", "alternateName": ["CGP Luxury Hotel", "Premium CGP Hotel Hoi An"],
         "url": lang_url(c.lang, ""), "description": c.t("intro.text"),
         "logo": SITE + "/images/logo.png", "image": [f"{SITE}/{og_file(n)}" for n in ("hero-facade-night", "hero-facade-day", "hero-pool-night", "hero-lobby", "room-500-2")],
         "telephone": PHONE_TEL, "email": EMAIL,
         "address": {"@type": "PostalAddress", "streetAddress": "67 Lý Thường Kiệt", "addressLocality": "Hội An",
                     "addressRegion": "Quảng Nam", "addressCountry": "VN"},
         "hasMap": MAP_LINK, "sameAs": [FB], "numberOfRooms": 23, "checkinTime": "14:00", "checkoutTime": "12:00",
         "currenciesAccepted": "USD, VND", "availableLanguage": ["vi", "en", "ko", "zh", "ru", "de"],
         "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": c.t(k + ".t"), "value": True} for k, _, _ in SERVICES],
         "potentialAction": {"@type": "ReserveAction", "target": lang_url(c.lang, "dat-phong/")}}
    if rooms:
        h["containsPlace"] = [{"@type": "HotelRoom", "name": c.t(k + ".t"), "description": c.t(k + ".d"),
                               "url": lang_url(c.lang, "phong-nghi/") + "#" + k, "image": f"{SITE}/images/{imgs[0]}.jpg"} for k, imgs in ROOMS]
    return h


def page(c, title, desc, css, cur, body, scripts=(), og_img="hero-facade-day", og_type="website", ld=(), rooms_ld=False, published=None):
    links = "".join(f'<link rel="stylesheet" href="{c.R}css/{x}.css?v={VER}">\n' for x in ["fonts", "main"] + list(css))
    js = "".join(f'<script src="{c.R}js/{s}.js?v={VER}"></script>\n' for s in ["main"] + list(scripts))
    alt = "".join(f'<link rel="alternate" hreflang="{l}" href="{lang_url(l, c.slug)}">\n' for l in LANGS)
    alt += f'<link rel="alternate" hreflang="x-default" href="{lang_url(DEFAULT, c.slug)}">\n'
    url, desc = lang_url(c.lang, c.slug), clip(desc)
    og = f"{SITE}/{SHARE_IMG}"  # one branded share image site-wide (og_img still feeds the per-page JSON-LD)
    og_alt = "".join(f'<meta property="og:locale:alternate" content="{LOCALE[l]}">\n' for l in LANGS if l != c.lang)
    art = (f'<meta property="article:published_time" content="{published}T08:00:00+07:00">\n'
           f'<meta property="article:modified_time" content="{published}T08:00:00+07:00">\n') if published else ""

    # JSON-LD graph: website + hotel + this page + breadcrumb (+ page-specific nodes)
    name = title.split(" | ")[0]
    crumbs = [(c.t("nav.home"), lang_url(c.lang, ""))]
    if c.slug:
        top = c.slug.split("/")[0] + "/"
        crumbs.append((c.t(SECTIONS[top]), lang_url(c.lang, top)))
        if c.slug != top:
            crumbs.append((name, url))
    page_type = {"": "WebPage", "gioi-thieu/": "AboutPage", "thu-vien-anh/": "CollectionPage", "tin-tuc/": "CollectionPage",
                 "goi-luu-tru/": "CollectionPage", }.get(c.slug, "WebPage")
    graph = [
        {"@type": "WebSite", "@id": SITE_ID, "url": SITE + "/", "name": "CGP Luxury Hotel Hoi An", "inLanguage": LANGS, "publisher": {"@id": HOTEL_ID}},
        hotel_ld(c, rooms_ld),
        {"@type": page_type, "@id": url + "#webpage", "url": url, "name": title, "description": desc, "inLanguage": c.lang,
         "isPartOf": {"@id": SITE_ID}, "about": {"@id": HOTEL_ID},
         "primaryImageOfPage": {"@type": "ImageObject", "url": f"{SITE}/{og_file(og_img)}", "width": 1200, "height": 630},
         **({"breadcrumb": {"@id": url + "#breadcrumb"}} if c.slug else {})},
    ]
    if c.slug:
        graph.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": k + 1, "name": n_, "item": u_} for k, (n_, u_) in enumerate(crumbs)]})
    graph += list(ld)
    schema = jsonld({"@context": "https://schema.org", "@graph": graph})

    doc = f'''<!DOCTYPE html>
<html lang="{c.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{ROBOTS}">
<link rel="canonical" href="{url}">
{alt}<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="CGP Luxury Hotel Hoi An">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:locale" content="{LOCALE[c.lang]}">
{og_alt}<meta property="og:image" content="{og}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(SHARE_ALT)}">
<meta name="twitter:image:alt" content="{e(SHARE_ALT)}">
{art}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og}">
{c.preload}<link rel="icon" href="{c.R}favicon.ico" sizes="any">
<link rel="icon" href="{c.R}seo/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{c.R}seo/apple-touch-icon.png">
<link rel="manifest" href="{c.R}seo/site.webmanifest">
<meta name="theme-color" content="#002040">
{links}{schema}
</head>
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
    return f'''<section class="banner-page">{c.banner(img, "page", eager=True)}
  <div class="port"><h1 class="{cls}">{e(text)}</h1></div>
</section>'''


def intro_block(c, h="h1"):
    imgs = "".join(f'\n        <img {c.pic(n, "(max-width: 991px) 100vw, 767px")} alt="{e(c.t("intro.title"))}" loading="lazy">'
                   for n in ["hero-facade-day", "lobby-2", "pool-day-3", "room-500-2", "room-301-2", "room-101-1", "garden-cafe-1", "suite-gold"])
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
      <div class="map"><iframe src="{MAP}" title="{e(c.t("map.title"))}" loading="lazy" allowfullscreen referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      <div class="contact-card">
        <div class="c-item"><i>{SVG["pin"]}</i><div><h3>{e(c.t("c.addr"))}</h3><p>{e(c.t("c.addrv"))}</p></div></div>
        <div class="c-item"><i>{SVG["phone"]}</i><div><h3>{e(c.t("c.phone"))}</h3><a href="tel:{PHONE_TEL}">{PHONE}</a></div></div>
        <div class="c-item"><i>{SVG["mail"]}</i><div><h3>{e(c.t("c.email"))}</h3><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
        <a class="btn btn--sm map-open" href="{MAP_LINK}" target="_blank" rel="noopener">{e(c.t("map.open"))}</a>
      </div>
    </div>'''


def services_block(c):
    tiles = ""
    for i, img in enumerate(["pool", "balcony-view", "bathtub", "suite-gold"], 1):
        s, t = e(c.t(f"tile{i}.s")), e(c.t(f"tile{i}.t"))
        tiles += (f'<figure class="tile"><img {c.pic(img, "(max-width: 991px) 50vw, 25vw")} alt="{t}" loading="lazy">'
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
        out += (f'<article class="post"><a class="post-img" href="{c.pkg(i)}"><img {c.pic(p["img"], "(max-width: 600px) 100vw, (max-width: 991px) 50vw, 373px")} alt="{n}" loading="lazy"></a>'
                f'<div class="post-body"><h3 class="post-title"><a href="{c.pkg(i)}">{n}</a></h3>'
                f'<div class="post-btns"><a class="btn" href="{c.pkg(i)}">{e(c.t("btn.details"))}</a>'
                f'<a class="btn" href="{c.url("dat-phong/")}?pkg={i}">{e(c.t("btn.book"))}</a></div></div></article>')
    return out


def room_cards(c, ids, wide_from=3):
    out = ""
    for k, i in enumerate(ids):
        p, n = P[i], e(c.name(i))
        href = c.pkg(i)
        out += (f'<article class="room{" is-wide" if k >= wide_from else ""}"><a class="room-img" href="{href}"><img {c.pic(p["img"], "(max-width: 600px) 100vw, (max-width: 991px) 50vw, " + ("570px" if k >= wide_from else "373px"))} alt="{n}" loading="lazy"></a>'
                f'<div class="room-body"><h3 class="room-title"><a href="{href}">{n}</a></h3><p class="room-text">{e(c.pick(p["tag"]))}</p>'
                f'<div class="room-foot"><a class="btn" href="{href}">{e(c.t("btn.detailsShort"))}</a>'
                f'<div><span class="price-from">{e(c.t("price.from"))}</span><span class="price">USD {p["price"]:,} {e(c.t("u." + p["unit"]))}</span></div></div></div></article>')
    return out


def news_url(c, n): return c.url(f'tin-tuc/{n["id"]}/')


def news_cards(c):
    out = ""
    for n in NEWS:
        u = news_url(c, n)
        out += (f'<article class="post"><a class="post-img" href="{u}"><img src="{c.th(n["img"])}" alt="{e(c.pick(n["title"]))}" loading="lazy" width="660" height="440"></a>'
                f'<div class="post-body"><span class="post-date">{SVG["date"]}<time datetime="{n["date"]}">{e(c.date(n["date"]))}</time></span>'
                f'<h3 class="news-title"><a href="{u}">{e(c.pick(n["title"]))}</a></h3><p class="news-text">{e(c.pick(n["body"]))}</p></div></article>')
    return out


def news_list(c):
    out = ""
    for n in NEWS:
        u = news_url(c, n)
        out += (f'<li class="news-item"><a class="post-img" href="{u}"><img src="{c.th(n["img"])}" alt="{e(c.pick(n["title"]))}" loading="lazy" width="660" height="440"></a>'
                f'<div><h2><a href="{u}">{e(c.pick(n["title"]))}</a></h2><div class="news-meta">{SVG["date"]}<time datetime="{n["date"]}">{e(c.date(n["date"]))}</time></div>'
                f'<p>{e(c.pick(n["body"]))}</p></div></li>')
    return out + f'<li class="news-none" hidden>{e(c.t("sb.none"))}</li>'


def sidebar(c):
    recent = "".join(f'<li><a href="{news_url(c, n)}"><img src="{c.th(n["img"])}" alt="" loading="lazy"><span>{e(c.pick(n["title"]))}</span></a></li>' for n in NEWS)
    pk = "".join(f'<li><a href="{c.pkg(i)}"><img src="{c.th(P[i]["img"])}" alt="" loading="lazy"><span>{e(c.name(i))}</span></a></li>' for i in range(1, 8))
    return f'''<aside class="sidebar">
      <section><h3 class="widget-title">{e(c.t("sb.search"))}</h3>
        <form class="search-box" role="search" action="{c.url("tin-tuc/")}" method="get"><input type="search" name="s" placeholder="{e(c.t("sb.looking"))}" aria-label="{e(c.t("sb.search"))}"><button type="submit" aria-label="{e(c.t("sb.search"))}">{SVG["search"]}</button></form></section>
      <section><h3 class="widget-title">{e(c.t("sb.recent"))}</h3><ul class="side-list">{recent}</ul></section>
      <section><h3 class="widget-title">{e(c.t("sb.list"))}</h3><ul class="side-list">{pk}</ul></section>
    </aside>'''


SC_ICONS = {
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "bed": '<path d="M3 18V7M3 14h18v4M21 14v-3a3 3 0 0 0-3-3h-7v6"/><circle cx="7" cy="11" r="2"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "rain": '<path d="M7 15a4 4 0 0 1-.6-8A6 6 0 0 1 18 8a3.5 3.5 0 0 1-.5 7z"/><path d="M8 18l-1 3M12 18l-1 3M16 18l-1 3"/>',
    "star": '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.2l1-6.2L3 9.6l6.2-.9z"/>',
    "heart": '<path d="M12 20s-7.5-4.6-9.3-9.3A5 5 0 0 1 12 6a5 5 0 0 1 9.3 4.7C19.5 15.4 12 20 12 20z"/>',
    "bike": '<circle cx="6" cy="16" r="3.5"/><circle cx="18" cy="16" r="3.5"/><path d="M6 16l4-7h5l3 7M10 9l2 7M13 6h3"/>',
    "food": '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M17 21V3c-2 1.5-3 4-3 7v3h3"/>',
    "pool": '<path d="M2 18c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5M8 15V5a2 2 0 0 1 4 0M16 15V5a2 2 0 0 0-4 0M8 9h8"/>',
    "plane": '<path d="M10 14 3 12l1.5-1.5L11 11l4-5.5c1-1.3 3.5-2 4.2-1.3.7.7 0 3.2-1.3 4.2L12.5 13l.5 6.5L11.5 21l-2-7z"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    "wallet": '<path d="M3 7h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM3 7l12-3v3"/><circle cx="16.5" cy="13.5" r="1.2"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.5-3.5 3.2-5.5 6.5-5.5s6 2 6.5 5.5"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.6c2.8-.3 5 1.4 5.5 4.4"/>',
    "camera": '<path d="M3 8h4l2-3h6l2 3h4v11H3z"/><circle cx="12" cy="13" r="3.5"/>',
    "lantern": '<path d="M12 2v3M9 5h6M8 8c0-1.7 1.8-3 4-3s4 1.3 4 3v7c0 1.7-1.8 3-4 3s-4-1.3-4-3zM8 11.5h8M10 18v2h4v-2M12 20v2"/>',
}


CREDITS = json.load(open("../content/image-credits.json", encoding="utf-8")) if os.path.exists("../content/image-credits.json") else {}
PHOTO = {"vi": "Ảnh", "en": "Photo", "ko": "사진", "zh": "图片", "ru": "Фото", "de": "Foto"}


def credit(c, name):
    """Attribution line for a Wikimedia Commons photo (required by CC BY / CC BY-SA)."""
    cr = CREDITS.get(name)
    if not cr:
        return ""
    return (f'<small class="tv-credit">{PHOTO[c.lang]}: {e(cr["artist"])} / Wikimedia Commons, '
            f'<a href="{e(cr["source"])}" target="_blank" rel="noopener">{e(cr["license"])}</a></small>')


def smart_html(c, n):
    html = n["html"][c.i]
    def _img(m):
        attrs = m.group(1)
        name = re.search(r'data-img="([^"]+)"', attrs).group(1)
        sz = re.search(r'data-sizes="([^"]+)"', attrs)
        rest = re.sub(r'\s*data-(img|sizes)="[^"]*"', "", attrs)
        return f'<img {c.pic(name, sz.group(1) if sz else "(max-width: 991px) 100vw, 865px")}{rest} loading="lazy" decoding="async">' + credit(c, name)
    html = re.sub(r"<img\s([^>]*data-img=[^>]*?)\s*/?>", _img, html)
    html = re.sub(r'href="@/([^"]*)"', lambda m: f'href="{c.url(m.group(1))}"', html)
    html = re.sub(r'<div data-gallery="([^"]+)"></div>', lambda m: gallery_grid(c, m.group(1).split(), "g" + str(abs(hash(m.group(1))) % 10**6), "gal-grid gal-grid--4"), html)
    html = re.sub(r'<i data-ic="([a-z]+)"></i>', lambda m: f'<span class="tv-ic" aria-hidden="true"><svg viewBox="0 0 24 24">{SC_ICONS[m.group(1)]}</svg></span>', html)
    return html


def smart_words(html):
    text = re.sub(r"<[^>]+>", " ", html)
    return len(H.unescape(text).split())


def article_body(c, n):
    if n.get("smart"):
        return (f'<div class="news-meta" style="margin-bottom:14px">{SVG["date"]}<time datetime="{n["date"]}">{e(c.date(n["date"]))}</time></div>'
                f'<div class="sc">{smart_html(c, n)}</div>')
    body = c.pick(n["body"])
    parts = re.split(r'(?<=[.。])\s*(?=[A-ZÀ-Ỹ가-힣一-龥А-ЯÄÖÜ])', body)
    half = (len(parts) + 1) // 2
    paras = [" ".join(parts[:half]), " ".join(parts[half:])]
    ps = "".join(f"<p>{e(x)}</p>" for x in paras if x.strip())
    thanks = c.t("ok.text").split(".")[0].split("。")[0]
    return (f'<div class="news-meta" style="margin-bottom:14px">{SVG["date"]}<time datetime="{n["date"]}">{e(c.date(n["date"]))}</time></div>{ps}'
            f'<p>{e(thanks)}.</p><p class="article-cta"><a class="btn-navy" href="{c.url("dat-phong/")}">{e(c.t("art.cta"))}</a></p>'
            f'<img class="article-img" src="{c.img(n["img"])}" alt="{e(c.pick(n["title"]))}" loading="lazy" {c.wh(n["img"])}>'
            + (f'<p>{e(c.pick(n["more"]))}</p>' if n.get("more") else "")
            + (f'<h3 class="article-h">{e(c.t("art.gal"))}</h3>' + gallery_grid(c, n["imgs"], "art-gal", "gal-grid art-gal", webp=False) if n.get("imgs") else ""))



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


def gallery_grid(c, imgs, uid, cls="gal-grid", sizes="(max-width: 991px) 50vw, 380px", webp=True):
    """Thumbnails + CSS-only lightbox (:target), no JS. `sizes` may be a function of the item index."""
    alt = e(c.t("intro.title"))
    sz = sizes if callable(sizes) else (lambda k: sizes)
    thumb = (lambda k, n: c.pic(n, sz(k))) if webp else (lambda k, n: f'src="{c.th(n)}" {c.wh(n)}')
    full = (lambda n: c.pic(n, "(max-width: 1100px) 100vw, 1100px")) if webp else (lambda n: f'src="{c.img(n)}"')
    thumbs = "".join(f'<a class="gal-item" href="#{uid}-{k}"><img {thumb(k, n)} alt="{alt} – {k + 1}" loading="lazy"></a>' for k, n in enumerate(imgs))
    boxes = "".join(f'<div class="lb" id="{uid}-{k}"><a class="lb-bg" href="#{uid}" aria-label="Close"></a><img {full(n)} alt="{alt} – {k + 1}" loading="lazy">'
                    f'<a class="lb-x" href="#{uid}" aria-label="Close">&times;</a>'
                    + (f'<a class="lb-prev" href="#{uid}-{k - 1}" aria-label="Previous"></a>' if k else "")
                    + (f'<a class="lb-next" href="#{uid}-{k + 1}" aria-label="Next"></a>' if k < len(imgs) - 1 else "") + "</div>" for k, n in enumerate(imgs))
    return f'<div class="{cls}" id="{uid}">{thumbs}</div>{boxes}'


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def feature_block(c, key, paras, imgs, pics_cls, rev=False):
    """Text + photo collage (opens in the CSS lightbox)."""
    ps = "".join(f"<p>{e(c.t(p))}</p>" for p in paras)
    uid = "ft-" + key.split(".")[-1]
    return f'''<section class="ft{" is-rev" if rev else ""}">
  <div class="port ft-row">
    <div class="ft-text"><h2 class="headline dash">{e(c.t(key + ".t"))}</h2>{ps}</div>
    {gallery_grid(c, imgs, uid, "ft-pics " + pics_cls, lambda k: ("(max-width: 991px) 100vw, 640px" if k == 0 and "lead" in pics_cls else "(max-width: 991px) 33vw, 210px"))}
  </div>
</section>'''


def video_block(c):
    feats = "".join(f"<li>{e(f)}</li>" for f in c.t("vd.f").split("|"))
    return f'''<section class="vd-sec">
  <div class="port vd-row">
    <div class="vd-media">
      <video class="vd-video" src="{c.R}videos/hotel-intro.mp4" poster="{c.webp("video-poster", 480)}" preload="metadata" playsinline width="480" height="848"></video>
      <button type="button" class="vd-play" aria-label="{e(c.t("vd.play"))}"><span class="vd-play-ring"></span><span class="vd-play-btn"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg></span><span class="vd-play-label">{e(c.t("vd.play"))}</span></button>
    </div>
    <div class="vd-text">
      <span class="vd-eye">{e(c.t("vd.eye"))}</span>
      <h2 class="headline dash">{e(c.t("vd.t"))}</h2>
      <p>{e(c.t("vd.p1"))}</p>
      <p>{e(c.t("vd.p2"))}</p>
      <ul class="vd-feats">{feats}</ul>
      <div class="btns"><a class="btn" href="{c.url("phong-nghi/")}">{e(c.t("rm.all"))}</a><a class="btn" href="{c.url("dat-phong/")}">{e(c.t("nav.book"))}</a></div>
    </div>
  </div>
</section>'''


def rooms_teaser(c):
    cards = ""
    for key, imgs in ROOMS:
        href = c.url(f"phong-nghi/#{key}")
        n = e(c.t(key + ".t"))
        no = e(c.t(key + ".no"))
        cards += (f'<article class="rm-card"><a class="rm-card-img" href="{href}"><img {c.pic(imgs[0], "(max-width: 600px) 100vw, (max-width: 991px) 50vw, 373px")} alt="{n} – {no}" loading="lazy">'
                  f'<span class="rm-count">{len(imgs)} {e(c.t("rm.photos"))}</span></a>'
                  f'<div class="rm-card-body"><span class="rm-no">{no}</span><h3><a href="{href}">{n}</a></h3><p>{e(c.t(key + ".tag"))}</p>'
                  f'<a class="rm-link" href="{href}">{e(c.t("rm.view"))}</a></div></article>')
    return f'''<section class="rm-teaser">
  <div class="port">
    <h2 class="headline dash">{e(c.t("hm.rooms.t"))}</h2>
    <p class="sub-title">{e(c.t("hm.rooms.d"))}</p>
    <div class="rm-cards">{cards}</div>
    <p class="more-row"><a class="btn" href="{c.url("phong-nghi/")}">{e(c.t("rm.all"))}</a></p>
  </div>
</section>'''


def experience_block(c):
    tiles = "".join(f'<figure class="ex-tile"><img {c.pic(img, "(max-width: 600px) 100vw, (max-width: 991px) 50vw, 373px")} alt="{e(c.t(k + ".t"))}" loading="lazy">'
                    f'<figcaption><strong>{e(c.t(k + ".t"))}</strong><span>{e(c.t(k + ".d"))}</span></figcaption></figure>' for k, img in EXPERIENCES)
    return f'''<section class="ex-sec">
  <div class="port">
    <h2 class="headline dash">{e(c.t("ex.t"))}</h2>
    <p class="sub-title">{e(c.t("ex.d"))}</p>
    <div class="ex-grid">{tiles}</div>
  </div>
</section>'''


def build_rooms(lang):
    c = Ctx(lang, "phong-nghi/")
    secs = ""
    for k, (key, imgs) in enumerate(ROOMS):
        name = e(c.t(key + ".t"))
        feats = "".join(f"<li>{e(f)}</li>" for f in c.t(key + ".f").split("|"))
        rest = len(imgs) - 5
        secs += f'''<section class="rm-sec{" is-rev" if k % 2 else ""}" id="{key}">
  <div class="port rm-row">
    <div class="rm-media" data-more="+{rest} {e(c.t("rm.photos"))}">{gallery_grid(c, imgs, "g" + key, "rm-gal", lambda k: "(max-width: 991px) 100vw, 620px" if k == 0 else "(max-width: 991px) 25vw, 150px")}</div>
    <div class="rm-text">
      <p class="rm-no">{e(c.t(key + ".no"))}</p>
      <h2 class="headline headline--sm dash">{name}</h2>
      <p class="pd-tag">{e(c.t(key + ".tag"))}</p>
      <p class="rm-desc">{e(c.t(key + ".d"))}</p>
      <h3 class="pd-h">{e(c.t("rm.feat"))}</h3>
      <ul class="pd-inc rm-feats">{feats}</ul>
      <div class="btns"><a class="btn" href="{c.url("dat-phong/")}">{e(c.t("btn.book"))}</a><a class="btn" href="{c.url("goi-luu-tru/")}">{e(c.t("nav.packages"))}</a></div>
    </div>
  </div>
</section>'''
    body = f'''{banner_page(c, "room-500-2", c.t("rm.banner"))}
<p class="port pk-intro sub-title rm-intro">{e(c.t("rm.sub"))}</p>
{secs}
<section class="rm-amen">
  <div class="port">
    <h2 class="headline dash">{e(c.t("rm.amen.t"))}</h2>
    <p class="sub-title">{e(c.t("rm.amen.d"))}</p>
    {gallery_grid(c, AMENITIES, "amen", "amen-grid", "(max-width: 991px) 33vw, 190px")}
  </div>
</section>
<section class="rm-cta">
  <div class="port"><p>{e(c.t("rm.cta"))}</p><div class="btns"><a class="btn" href="{c.url("dat-phong/")}">{e(c.t("nav.book"))}</a><a class="btn" href="{c.url("goi-luu-tru/")}">{e(c.t("pk.viewall"))}</a></div></div>
</section>'''
    page(c, f'{c.t("rm.banner")} | {c.t("intro.title")}', c.t("rm.sub"), ["home", "pages"], "rooms", body, og_img="room-500-2", rooms_ld=True)


def build_packages(lang):
    # list page, grouped by the collection structure of info-rooms.docx
    c = Ctx(lang, "goi-luu-tru/")
    groups = ""
    for cat in CATS:
        ids = [i for i in sorted(P) if P[i]["cat"] == cat]
        fill = "".join(f'<figure class="room room-photo"><img {c.pic(n, "(max-width: 991px) 50vw, 373px")} alt="{e(c.t("cat." + cat))}" loading="lazy"></figure>'
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
    <div class="pd-media"><img {c.pic(p["img"], "(max-width: 1200px) 100vw, 1160px")} alt="{e(name)}"><a class="pd-ribbon" href="{c.url("dat-phong/")}?pkg={pid}">{e(c.t("btn.book"))}</a></div>
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
                        "offeredBy": {"@id": HOTEL_ID}})
        desc = c.pick(p["desc"])
        page(c, f'{name} | {c.t("intro.title")}', desc, ["home", "pages"], "packages", body, og_img=p["img"])


def build_gallery(lang):
    c = Ctx(lang, "thu-vien-anh/")
    secs = "".join(f'''<div class="gal-cat" id="{key}">
      <h2 class="headline headline--sm dash">{e(c.t("gal." + key))} <small>{len(imgs)} {e(c.t("rm.photos"))}</small></h2>
      <p class="sub-title">{e(c.t("gal." + key + "d"))}</p>
      {gallery_grid(c, imgs, "gal-" + key, "gal-masonry", "(max-width: 991px) 50vw, 290px")}
    </div>''' for key, imgs in GAL_SECTIONS)
    nav = "".join(f'<a href="#{key}">{e(c.t("gal." + key))}</a>' for key, _ in GAL_SECTIONS)
    body = f'''{banner_page(c, "pool-day-3", c.t("gal.title"))}
<section class="gal-sec gal-page">
  <div class="port">
    <p class="sub-title">{e(c.t("gal.sub"))}</p>
    <nav class="gal-nav">{nav}</nav>
    {secs}
  </div>
</section>'''
    page(c, f'{c.t("gal.title")} | {c.t("intro.title")}', c.t("gal.sub") + ". " + c.t("intro.text"), ["home", "pages"], "gallery", body, og_img="room-pool-view")


def build_services(lang):
    c = Ctx(lang, "dich-vu/")
    rows = ""
    for k, (key, img, more) in enumerate(SERVICES):
        t = e(c.t(key + ".t"))
        strip = gallery_grid(c, [img] + more, f"svc{k + 1}", "svc-thumbs", "(max-width: 991px) 25vw, 140px")
        text = f'<div class="svc-text"><h2>{t}</h2><p>{e(c.t(key + ".d"))}</p>{strip}<a class="btn btn--sm" href="{c.url("goi-luu-tru/")}">{e(c.t("svc.cta"))}</a></div>'
        pic = f'<div class="svc-img"><img {c.pic(img, "(max-width: 991px) 100vw, 580px")} alt="{t}" loading="lazy"></div>'
        rows += f'<article class="svc-row{" is-rev" if k % 2 else ""}">{pic if k % 2 == 0 else text}{text if k % 2 == 0 else pic}</article>'
    body = f'''{banner_page(c, "pool-day-2", c.t("svc.page"))}
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
                f'<div class="rcard-img"><img {c.pic(p["img"], "(max-width: 600px) 100vw, (max-width: 991px) 50vw, 380px")} alt="{n}" loading="lazy">{badge}</div>'
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
                f'<div class="rp-room"><img {c.pic(p["img"], "(max-width: 600px) 100vw, 160px")} alt="" loading="lazy"><div><h3 data-k="name">{n}</h3>'
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
    return top + steps


def _fmt(s, kw):
    for k, v in kw.items():
        s = s.replace("{" + k + "}", str(v))
    return s


# ------------------------------------------------------------------ pages
def build(lang):
    # Home
    c = Ctx(lang, "")
    slides = "".join(f'<div class="banner-slide">{c.banner(n, "hero", eager=(k == 0), defer=(k > 0))}</div>' for k, n in enumerate( ["hero-facade-night", "hero-facade-day", "hero-pool-night", "hero-lobby", "hero-guests", "pool-day-3", "room-500-2", "suite-sunset"]))
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
  </div>
</section>

{video_block(c)}

<section class="intro intro--contact">
  <div class="port">
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

{rooms_teaser(c)}

{services_block(c)}

{experience_block(c)}

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
    page(c, f'{c.t("intro.title")} | {c.t("hero.title")}', c.t("intro.text"), ["home", "pages"], "home", home)

    # About
    c = Ctx(lang, "gioi-thieu/")
    about = f'''{banner_page(c, "lobby-2", c.t("ab.banner"))}
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
{feature_block(c, "ab.arch", ["ab.arch.p"], ["facade-bougainvillea-2", "hero-facade-night", "facade-bougainvillea-4"], "ft-pics--3")}
{feature_block(c, "ab.lobby", ["ab.lobby.p"], ["lobby-2", "reception-desk", "lobby-checkin", "lobby-3", "lobby-5"], "ft-pics--lead", rev=True)}
{feature_block(c, "ab.pool", ["ab.pool.p"], ["pool-day-3", "pool-day-1", "pool-day-2", "pool-day-4", "guest-poolside-4"], "ft-pics--lead")}
{feature_block(c, "ab.team", ["ab.team.p1", "ab.team.p2"], ["staff-1", "staff-3", "staff-6", "staff-5", "lobby-welcome", "staff-4"], "ft-pics--3", rev=True)}
{services_block(c)}
{experience_block(c)}
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
    news = f'''{banner_page(c, "garden-cafe-1", c.t("nw.banner"))}
<section>
  <div class="port with-sidebar">
    <div><ul class="news-list">{news_list(c)}</ul></div>
    {sidebar(c)}
  </div>
</section>'''
    page(c, f'{c.t("nw.title")} | {c.t("intro.title")}', c.t("nw.bannersub") + ". " + c.t("intro.text"), ["home", "news", "pages"], "news", news)

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
        u = lang_url(lang, c.slug)
        post = {"@type": "BlogPosting", "@id": u + "#article", "headline": title, "description": clip(desc), "inLanguage": lang,
                "image": [f'{SITE}/{og_file(n["img"])}', f'{SITE}/images/{n["img"]}.jpg'], "datePublished": n["date"] + "T08:00:00+07:00",
                "dateModified": n["date"] + "T08:00:00+07:00", "author": {"@id": HOTEL_ID}, "publisher": {"@id": HOTEL_ID},
                "mainEntityOfPage": {"@id": u + "#webpage"}, "isPartOf": {"@id": SITE_ID}}
        if n.get("smart"):
            post["wordCount"] = smart_words(n["html"][c.i])
        page(c, f'{title} | {c.t("intro.title")}', desc, ["home", "news", "pages"] + (["blocks"] if n.get("smart") else []), "news", art, og_img=n["img"], og_type="article", ld=[post], published=n["date"])

    # Booking (interactive widget rendered by js/booking.js in this page's language)
    c = Ctx(lang, "dat-phong/")
    booking = f'''{banner_page(c, "suite-sunset", c.t("bk.banner"))}
<section class="bk-sec" id="terms">
  <div class="port">
    <div class="tl" id="tl">{booking_widget(c)}</div>
  </div>
</section>
<div class="gateway" id="gateway" hidden><div><i></i><p>{e(c.t("pay.proc"))}</p></div></div>'''
    page(c, f'{c.t("bk.banner")} | {c.t("intro.title")}', c.t("bk.bannersub") + ". " + c.t("intro.text"), ["booking"], "book", booking, scripts=["booking"])


for l in LANGS:
    if l != DEFAULT and os.path.isdir(l):
        shutil.rmtree(l)  # regenerated below
if os.path.isdir("tin-tuc"):  # default-language articles live next to other pages: drop the ones no longer in NEWS
    for _d in os.listdir("tin-tuc"):
        if os.path.isdir("tin-tuc/" + _d) and _d not in {n["id"] for n in NEWS}:
            shutil.rmtree("tin-tuc/" + _d)
for l in LANGS:
    build(l)
    build_packages(l)
    build_services(l)
    build_gallery(l)
    build_rooms(l)

# sitemap with hreflang alternates
slugs = ["", "gioi-thieu/", "phong-nghi/", "goi-luu-tru/", "dich-vu/", "thu-vien-anh/", "tin-tuc/", "dat-phong/"] + [f'goi-luu-tru/{P[i]["slug"]}/' for i in sorted(P)] + [f'tin-tuc/{n["id"]}/' for n in NEWS]
TODAY = time.strftime("%Y-%m-%d")
NEWS_DATE = {f'tin-tuc/{n["id"]}/': n["date"] for n in NEWS}
PRIO = {"": "1.0", "dat-phong/": "0.9", "phong-nghi/": "0.9", "goi-luu-tru/": "0.8", "gioi-thieu/": "0.8", "dich-vu/": "0.7", "thu-vien-anh/": "0.6", "tin-tuc/": "0.6"}
urls = ""
for s in slugs:
    alts = "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{lang_url(x, s)}"/>' for x in LANGS)
    alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{lang_url(DEFAULT, s)}"/>'
    for l in LANGS:
        urls += (f"  <url><loc>{lang_url(l, s)}</loc><lastmod>{NEWS_DATE.get(s, TODAY)}</lastmod>"
                 f"<changefreq>{'weekly' if s in ('', 'tin-tuc/') else 'monthly'}</changefreq><priority>{PRIO.get(s, '0.5')}</priority>{alts}</url>\n")
open("sitemap.xml", "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")

open("robots.txt", "w", encoding="utf-8").write(f"""User-agent: *
Allow: /
Disallow: /.work/
Disallow: /reports/

Sitemap: {SITE}/sitemap.xml
""")

for _f in os.listdir("images/banner"):
    if _f not in _banner_keep:
        os.remove("images/banner/" + _f)
print("built", len(LANGS), "languages x", len(slugs), "pages")
