# -*- coding: utf-8 -*-
"""Patch build.py: FAQ blocks, gallery page + strips, extra package photos, filler photos on the package list. Run from html/."""
p = ".work/build.py"
s = open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, a[:90])
    s = s.replace(a, b)


rep('SERVICES = [', '''GALLERY = ["exterior-night", "exterior-day", "room-pool-view", "suite-arch-romantic", "town-view-window", "room-petals-balcony",
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
SERVICES = [''')

# helpers: FAQ + gallery
rep("\ndef jsonld(obj):", '''
def faq_block(c, n=9):
    items = "".join(f'<details class="faq-item"><summary>{e(c.t(f"faq.q{i}"))}</summary><p>{e(c.t(f"faq.a{i}"))}</p></details>' for i in range(1, n + 1))
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": c.t(f"faq.q{i}"), "acceptedAnswer": {"@type": "Answer", "text": c.t(f"faq.a{i}")}} for i in range(1, n + 1)]}
    return f\'\'\'<section class="faq-sec">
  <div class="port">
    <h2 class="headline dash">{e(c.t("faq.title"))}</h2>
    <div class="faq">{items}</div>
  </div>
</section>
{jsonld(data)}\'\'\'


def gallery_grid(c, imgs, uid, cls="gal-grid"):
    """Thumbnails + CSS-only lightbox (:target), no JS."""
    alt = e(c.t("intro.title"))
    thumbs = "".join(f'<a class="gal-item" href="#{uid}-{k}"><img src="{c.img(n)}" alt="{alt} – {k + 1}" loading="lazy" width="660" height="440"></a>' for k, n in enumerate(imgs))
    boxes = "".join(f'<div class="lb" id="{uid}-{k}"><a class="lb-bg" href="#{uid}" aria-label="Close"></a><img src="{c.img(n)}" alt="{alt} – {k + 1}" loading="lazy">'
                    f'<a class="lb-x" href="#{uid}" aria-label="Close">&times;</a>'
                    + (f'<a class="lb-prev" href="#{uid}-{k - 1}" aria-label="Previous"></a>' if k else "")
                    + (f'<a class="lb-next" href="#{uid}-{k + 1}" aria-label="Next"></a>' if k < len(imgs) - 1 else "") + "</div>" for k, n in enumerate(imgs))
    return f'<div class="{cls}" id="{uid}">{thumbs}</div>{boxes}'


def jsonld(obj):''')

# package list: filler photos + FAQ
rep('''        ids = [i for i in sorted(P) if P[i]["cat"] == cat]
        groups += f\'\'\'<section class="pk-group">
  <div class="port">
    <h2 class="headline dash">{e(c.t("cat." + cat))}</h2>
    <div class="rooms-grid rooms-grid--list">{room_cards(c, ids, wide_from=99)}</div>''',
    '''        ids = [i for i in sorted(P) if P[i]["cat"] == cat]
        fill = "".join(f'<figure class="room room-photo"><img src="{c.img(n)}" alt="{e(c.t("cat." + cat))}" loading="lazy" width="660" height="440"></figure>'
                       for n in GROUP_FILL[cat][:(3 - len(ids) % 3) % 3])
        groups += f\'\'\'<section class="pk-group">
  <div class="port">
    <h2 class="headline dash">{e(c.t("cat." + cat))}</h2>
    <div class="rooms-grid rooms-grid--list">{room_cards(c, ids, wide_from=99)}{fill}</div>''')
rep('''    body = banner_page(c, "suite-sunset", c.t("pk.title")) + f'\\n<p class="port pk-intro sub-title">{e(c.t("pk.text"))}</p>\\n' + groups''',
    '''    body = banner_page(c, "suite-sunset", c.t("pk.title")) + f'\\n<p class="port pk-intro sub-title">{e(c.t("pk.text"))}</p>\\n' + groups + "\\n" + faq_block(c)''')

# package detail: photo strip under the main image
rep('''    <div class="pd-media"><img src="{c.img(p["img"])}" alt="{e(name)}" width="1320" height="880"><a class="pd-ribbon" href="{c.url("dat-phong/")}?pkg={pid}">{e(c.t("btn.book"))}</a></div>''',
    '''    <div class="pd-media"><img src="{c.img(p["img"])}" alt="{e(name)}" width="1320" height="880"><a class="pd-ribbon" href="{c.url("dat-phong/")}?pkg={pid}">{e(c.t("btn.book"))}</a></div>
    {gallery_grid(c, PKG_PHOTOS[pid], "pd-gal", "pd-thumbs")}''')

# home: FAQ before news
rep('''<section class="news-sec">
  <div class="port">
    <h2 class="headline dash">{e(c.t("nw.title"))}</h2>''',
    '''{faq_block(c)}

<section class="news-sec">
  <div class="port">
    <h2 class="headline dash">{e(c.t("nw.title"))}</h2>''')

# about: gallery strip + FAQ
rep('''{services_block(c)}
<section class="intro" style="padding:40px 0 60px">''',
    '''{services_block(c)}
<section class="gal-sec">
  <div class="port">
    <h2 class="headline dash">{e(c.t("gal.title"))}</h2>
    {gallery_grid(c, GALLERY[:8], "ab-gal", "gal-grid gal-grid--4")}
    <p class="more-row"><a class="btn" href="{c.url("thu-vien-anh/")}">{e(c.t("gal.more"))}</a></p>
  </div>
</section>
{faq_block(c)}
<section class="intro" style="padding:40px 0 60px">''')
rep('''page(c, f'{c.t("ab.banner")} | {c.t("intro.title")}', c.t("intro.text"), ["home", "news"], "about", about)''',
    '''page(c, f'{c.t("ab.banner")} | {c.t("intro.title")}', c.t("intro.text"), ["home", "news", "pages"], "about", about)''')

# footer: gallery link (the original footer also has "Gallery")
rep('''        <li><a href="{c.url("dich-vu/")}">{e(c.t("nav.services"))}</a></li>
        <li><a href="{c.url("tin-tuc/")}">''',
    '''        <li><a href="{c.url("dich-vu/")}">{e(c.t("nav.services"))}</a></li>
        <li><a href="{c.url("thu-vien-anh/")}">{e(c.t("gal.title"))}</a></li>
        <li><a href="{c.url("tin-tuc/")}">''')

# gallery page
rep("\ndef build_services(lang):", '''
def build_gallery(lang):
    c = Ctx(lang, "thu-vien-anh/")
    body = f\'\'\'{banner_page(c, "grand-suite-arch", c.t("gal.title"))}
<section class="gal-sec gal-page">
  <div class="port">
    <p class="sub-title">{e(c.t("gal.sub"))}</p>
    {gallery_grid(c, GALLERY, "gal")}
  </div>
</section>\'\'\'
    page(c, f'{c.t("gal.title")} | {c.t("intro.title")}', c.t("gal.sub"), ["home", "pages"], "gallery", body, og_img="room-pool-view")


def build_services(lang):''')
rep("    build_services(l)\n", "    build_services(l)\n    build_gallery(l)\n")
rep('"goi-luu-tru/", "dich-vu/", "tin-tuc/"', '"goi-luu-tru/", "dich-vu/", "thu-vien-anh/", "tin-tuc/"')
open(p, "w", encoding="utf-8").write(s)
print("patched")
