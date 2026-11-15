# -*- coding: utf-8 -*-
"""Patch build.py: real pages for packages list, 13 package details, services; replace #anchors and the JS modal. Run from html/."""
p = ".work/build.py"
s = open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:80])
    s = s.replace(a, b)


# --- slugs + helpers -------------------------------------------------------
rep('PKG_MENU = [6, 2, 3, 4, 9, 10, 11]',
    '''PKG_MENU = [6, 2, 3, 4, 9, 10, 11]
CATS = ["relax", "romance", "family", "long", "sig", "solo"]
SERVICES = [("s1", "pool"), ("s2", "balcony-view"), ("s3", "bathtub"), ("s4", "room-romantic"), ("s5", "exterior-night"), ("s6", "room-desk")]


def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")''')
rep('P = {p["id"]: p for p in D["P"]}',
    'P = {p["id"]: p for p in D["P"]}\nfor _p in P.values():\n    _p["slug"] = slugify(_p["names"][1])')
rep('    def img(self, n): return f"{self.R}images/{n}.jpg"',
    '''    def img(self, n): return f"{self.R}images/{n}.jpg"
    def pkg(self, pid): return self.url(f'goi-luu-tru/{P[pid]["slug"]}/')
    def inc(self, k, p): return D["T"][self.lang]["__inc"][k].replace("{N}", self.nights(p["nights"])).replace("{n}", str(p["nights"]))''')

# --- header / footer links -------------------------------------------------
rep('''    sub = "".join(f'<li><a href="{c.url("dat-phong/")}?pkg={i}">{e(c.name(i))}</a></li>' for i in PKG_MENU)''',
    '''    sub = "".join(f'<li><a href="{c.pkg(i)}">{e(c.name(i))}</a></li>' for i in PKG_MENU)''')
rep('''          <li><a href="{c.home}#packages">{e(c.t("nav.packages"))}</a><ul class="sub-menu">{sub}</ul></li>
          <li><a href="{c.home}#services">{e(c.t("nav.services"))}</a></li>''',
    '''          <li>{a("goi-luu-tru/", "nav.packages", "packages")}<ul class="sub-menu">{sub}</ul></li>
          <li>{a("dich-vu/", "nav.services", "services")}</li>''')
rep('''        <li><a href="{c.home}#packages">{e(c.t("nav.packages"))}</a></li>
        <li><a href="{c.home}#services">{e(c.t("nav.services"))}</a></li>''',
    '''        <li><a href="{c.url("goi-luu-tru/")}">{e(c.t("nav.packages"))}</a></li>
        <li><a href="{c.url("dich-vu/")}">{e(c.t("nav.services"))}</a></li>''')
rep('''        <li><a href="{c.url("dat-phong/")}">{e(c.t("f.terms"))}</a></li>''',
    '''        <li><a href="{c.url("dat-phong/")}#terms">{e(c.t("f.terms"))}</a></li>''')

# --- cards: link to the package page instead of the JS modal ---------------
rep('''        out += (f'<article class="post"><a class="post-img" href="{c.url("dat-phong/")}?pkg={i}" data-detail="{i}"><img src="{c.img(p["img"])}" alt="{n}" loading="lazy" width="660" height="440"></a>'
                f'<div class="post-body"><h3 class="post-title"><a href="{c.url("dat-phong/")}?pkg={i}" data-detail="{i}">{n}</a></h3>'
                f'<div class="post-btns"><a class="btn" href="{c.url("dat-phong/")}?pkg={i}" data-detail="{i}">{e(c.t("btn.details"))}</a>\'''',
    '''        out += (f'<article class="post"><a class="post-img" href="{c.pkg(i)}"><img src="{c.img(p["img"])}" alt="{n}" loading="lazy" width="660" height="440"></a>'
                f'<div class="post-body"><h3 class="post-title"><a href="{c.pkg(i)}">{n}</a></h3>'
                f'<div class="post-btns"><a class="btn" href="{c.pkg(i)}">{e(c.t("btn.details"))}</a>\'''')
rep('''def room_cards(c, ids):
    out = ""
    for k, i in enumerate(ids):
        p, n = P[i], e(c.name(i))
        href = f'{c.url("dat-phong/")}?pkg={i}'
        out += (f'<article class="room{" is-wide" if k > 2 else ""}"><a class="room-img" href="{href}" data-detail="{i}">''',
    '''def room_cards(c, ids, wide_from=3):
    out = ""
    for k, i in enumerate(ids):
        p, n = P[i], e(c.name(i))
        href = c.pkg(i)
        out += (f'<article class="room{" is-wide" if k >= wide_from else ""}"><a class="room-img" href="{href}">''')
rep('''                f'<div class="room-body"><h3 class="room-title"><a href="{href}" data-detail="{i}">{n}</a></h3>''',
    '''                f'<div class="room-body"><h3 class="room-title"><a href="{href}">{n}</a></h3>''')
rep('''                f'<div class="room-foot"><a class="btn" href="{href}" data-detail="{i}">{e(c.t("btn.detailsShort"))}</a>\'''',
    '''                f'<div class="room-foot"><a class="btn" href="{href}">{e(c.t("btn.detailsShort"))}</a>\'''')
rep('''    pk = "".join(f'<li><a href="{c.url("dat-phong/")}?pkg={i}"><img''', '''    pk = "".join(f'<li><a href="{c.pkg(i)}"><img''')
rep('''f'<a class="tile-hover" href="{c.url("dat-phong/")}">''', '''f'<a class="tile-hover" href="{c.url("dich-vu/")}">''')
rep('''<section class="svc-head" id="services">''', '''<section class="svc-head">''')
rep('''<section class="rooms" id="packages">
  <div class="port">
    <h2 class="headline dash">{e(c.t("pk.title"))}</h2>
    <div class="rooms-grid">{room_cards(c, [1, 5, 8, 7, 11, 12, 13])}</div>''',
    '''<section class="rooms">
  <div class="port">
    <h2 class="headline dash">{e(c.t("pk.title"))}</h2>
    <div class="rooms-grid">{room_cards(c, [1, 5, 8, 7, 11, 12, 13])}</div>
    <p class="more-row"><a class="btn" href="{c.url("goi-luu-tru/")}">{e(c.t("pk.viewall"))}</a></p>''')

# --- new pages -------------------------------------------------------------
NEW = r"""

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def build_packages(lang):
    # list page, grouped by the collection structure of info-rooms.docx
    c = Ctx(lang, "goi-luu-tru/")
    groups = ""
    for cat in CATS:
        ids = [i for i in sorted(P) if P[i]["cat"] == cat]
        groups += f'''<section class="pk-group">
  <div class="port">
    <h2 class="headline dash">{e(c.t("cat." + cat))}</h2>
    <div class="rooms-grid rooms-grid--list">{room_cards(c, ids, wide_from=99)}</div>
  </div>
</section>'''
    body = banner_page(c, "suite-sunset", c.t("pk.title")) + f'\n<p class="port pk-intro sub-title">{e(c.t("pk.text"))}</p>\n' + groups
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
                                      "address": {"@type": "PostalAddress", "streetAddress": "78 Tran Khat Chan", "addressLocality": "Hoi An", "addressRegion": "Quang Nam", "addressCountry": "VN"}}})
        desc = c.pick(p["desc"])
        page(c, f'{name} | {c.t("intro.title")}', desc[:157] + ("…" if len(desc) > 157 else ""), ["home", "pages"], "packages", body, og_img=p["img"])


def build_services(lang):
    c = Ctx(lang, "dich-vu/")
    rows = ""
    for k, (key, img) in enumerate(SERVICES):
        t = e(c.t(key + ".t"))
        text = f'<div class="svc-text"><h2>{t}</h2><p>{e(c.t(key + ".d"))}</p><a class="btn btn--sm" href="{c.url("goi-luu-tru/")}">{e(c.t("svc.cta"))}</a></div>'
        pic = f'<div class="svc-img"><img src="{c.img(img)}" alt="{t}" loading="lazy" width="660" height="440"></div>'
        rows += f'<article class="svc-row{" is-rev" if k % 2 else ""}">{pic if k % 2 == 0 else text}{text if k % 2 == 0 else pic}</article>'
    body = f'''{banner_page(c, "pool", c.t("svc.page"))}
<section class="svc-page">
  <div class="port">
    <p class="sub-title svc-intro">{e(c.t("svc.text"))}</p>
    {rows}
  </div>
</section>'''
    page(c, f'{c.t("svc.page")} | {c.t("intro.title")}', c.t("svc.text"), ["home", "pages"], "services", body)
"""
rep("\n# ------------------------------------------------------------------ pages\ndef build(lang):", NEW + "\n# ------------------------------------------------------------------ pages\ndef build(lang):")
rep("for l in LANGS:\n    build(l)\n", "for l in LANGS:\n    build(l)\n    build_packages(l)\n    build_services(l)\n")
rep('slugs = ["", "gioi-thieu/", "tin-tuc/", "dat-phong/"] + [f\'tin-tuc/{n["id"]}/\' for n in NEWS]',
    'slugs = ["", "gioi-thieu/", "goi-luu-tru/", "dich-vu/", "tin-tuc/", "dat-phong/"] + [f\'goi-luu-tru/{P[i]["slug"]}/\' for i in sorted(P)] + [f\'tin-tuc/{n["id"]}/\' for n in NEWS]')
open(p, "w", encoding="utf-8").write(s)
print("patched")
