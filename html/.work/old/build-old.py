#!/usr/bin/env python3
"""Generate the static pages (header/footer repeated in each file). Run from the html/ folder."""
import os

MAP = "https://www.google.com/maps?q=78+Tr%E1%BA%A7n+Kh%C3%A1t+Ch%C3%A2n,+H%E1%BB%99i+An,+Qu%E1%BA%A3ng+Nam&z=15&output=embed"
FB = "https://www.facebook.com/profile.php?id=61564529174870"
LANGS = [("vi", "Tiếng Việt"), ("en", "English"), ("ko", "한국어"), ("zh", "中文"), ("ru", "Русский"), ("de", "Deutsch")]


def header(R, cur):
    def a(href, key, label, name):
        c = ' class="is-current"' if cur == name else ""
        return f'<a href="{href}"{c} data-i18n="{key}">{label}</a>'
    langs = "".join(f'<button type="button" data-lang="{c}">{n}</button>' for c, n in LANGS)
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{R}index.html" aria-label="CGP Luxury Hotel"><span class="logo-mark">CGP</span><span class="logo-sub">Luxury Hotel</span></a>
    <button type="button" class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span></button>
    <nav class="nav">
      {a(R + "index.html", "nav.home", "Trang chủ", "home")}
      {a(R + "gioi-thieu/index.html", "nav.about", "Giới thiệu", "about")}
      {a(R + "index.html#packages", "nav.packages", "Gói lưu trú", "")}
      {a(R + "index.html#services", "nav.services", "Dịch vụ", "")}
      {a(R + "tin-tuc/index.html", "nav.news", "Tin tức", "news")}
      <a class="nav-cta" href="{R}dat-phong/index.html" data-i18n="nav.book">Đặt phòng</a>
      <div class="lang">
        <button type="button" class="lang-btn" aria-label="Language"><span>VI</span></button>
        <div class="lang-menu">{langs}</div>
      </div>
    </nav>
  </div>
</header>'''


def contact():
    return f'''<div class="contact-grid">
      <div class="map"><iframe src="{MAP}" title="Map" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      <div class="contact-box">
        <div class="contact-item">
          <i><svg viewBox="0 0 24 24"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg></i>
          <div><h3 class="h-md" data-i18n="c.addr">Địa chỉ</h3><p data-i18n="c.addrv">78 Trần Khát Chân, TP. Hội An, Quảng Nam, Việt Nam</p></div>
        </div>
        <div class="contact-item">
          <i><svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg></i>
          <div><h3 class="h-md" data-i18n="c.phone">Điện thoại</h3><a href="tel:+84989244624">(+84) 98 924 46 24</a></div>
        </div>
        <div class="contact-item">
          <i><svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 7l9 6 9-6"/></svg></i>
          <div><h3 class="h-md" data-i18n="c.email">Email</h3><a href="mailto:cgpluxuryhotelhoian@gmail.com">cgpluxuryhotelhoian@gmail.com</a></div>
        </div>
      </div>
    </div>'''


def cta(R):
    return f'''<section class="cta-band" style="background-image:url({R}images/exterior-night.jpg)">
  <div class="wrap">
    <h2 data-i18n="cta.title">Sẵn sàng cho kỳ nghỉ tại Hội An?</h2>
    <p data-i18n="cta.text">Đặt trực tiếp trên website để nhận ưu đãi tốt nhất và được hỗ trợ 24/24.</p>
    <a class="btn" href="{R}dat-phong/index.html" data-i18n="box.cta">Đặt ngay</a>
  </div>
</section>'''


def footer(R):
    return f'''<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <h3>CGP Luxury Hotel</h3>
      <p data-i18n="f.about">Khách sạn tọa lạc tại khu vực yên tĩnh, gần trung tâm Hội An – thiết kế hiện đại, tiện nghi cao cấp và dịch vụ tận tâm 24/24.</p>
      <ul style="margin-top:16px">
        <li data-i18n="c.addrv">78 Trần Khát Chân, TP. Hội An, Quảng Nam, Việt Nam</li>
        <li><a href="tel:+84989244624">(+84) 98 924 46 24</a></li>
        <li><a href="mailto:cgpluxuryhotelhoian@gmail.com">cgpluxuryhotelhoian@gmail.com</a></li>
      </ul>
    </div>
    <div>
      <h3 data-i18n="f.quick">Liên kết nhanh</h3>
      <ul class="footer-links">
        <li><a href="{R}gioi-thieu/index.html" data-i18n="nav.about">Giới thiệu</a></li>
        <li><a href="{R}index.html#packages" data-i18n="nav.packages">Gói lưu trú</a></li>
        <li><a href="{R}index.html#services" data-i18n="nav.services">Dịch vụ</a></li>
        <li><a href="{R}tin-tuc/index.html" data-i18n="nav.news">Tin tức</a></li>
        <li><a href="{R}dat-phong/index.html" data-i18n="nav.book">Đặt phòng</a></li>
      </ul>
    </div>
    <div>
      <h3 data-i18n="f.policy">Chính sách</h3>
      <ul class="footer-links">
        <li><a href="{R}dat-phong/index.html#terms" data-i18n="f.terms">Điều khoản &amp; điều kiện</a></li>
        <li><a href="#" data-i18n="f.pay">Chính sách thanh toán</a></li>
        <li><a href="#" data-i18n="f.privacy">Chính sách bảo mật thông tin</a></li>
        <li><a href="#" data-i18n="f.refund">Chính sách hoàn huỷ</a></li>
      </ul>
    </div>
    <div>
      <h3 data-i18n="f.find">Kết nối với chúng tôi</h3>
      <div class="social">
        <a href="{FB}" target="_blank" rel="noopener" aria-label="Facebook">f</a>
        <a href="tel:+84989244624" aria-label="Phone">☎</a>
        <a href="mailto:cgpluxuryhotelhoian@gmail.com" aria-label="Email">@</a>
      </div>
    </div>
  </div>
  <div class="footer-bottom"><div class="wrap" data-i18n="f.copy">© 2026 CGP Luxury Hotel Hội An. Bản demo giao diện.</div></div>
</footer>'''


def page(path, R, title, css, cur, body, scripts=(), sub=True):
    links = "".join(f'<link rel="stylesheet" href="{R}css/{c}.css">\n' for c in ["fonts", "main"] + css)
    js = "".join(f'<script src="{R}js/{s}.js"></script>\n' for s in ["i18n", "data", "main"] + list(scripts))
    cls = ' class="page-sub"' if sub else ""
    html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{links}</head>
<body{cls} data-root="{R}">
{header(R, cur)}
<main>
{body}
</main>
{footer(R)}
{js}</body>
</html>
'''
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(path, "w", encoding="utf-8").write(html)


def banner(R, img, k1, t1, k2, t2):
    return f'''<section class="page-banner" style="background-image:url({R}images/{img}.jpg)">
  <div><h1 data-i18n="{k1}">{t1}</h1><p data-i18n="{k2}">{t2}</p></div>
</section>'''


INTRO = "Tọa lạc tại khu vực yên tĩnh và gần trung tâm Hội An, CGP Luxury Hotel mang đến trải nghiệm nghỉ dưỡng đẳng cấp với thiết kế hiện đại, tiện nghi cao cấp, không gian sang trọng và dịch vụ tận tâm 24/24."

# ---------------- Home ----------------
def lazy(i):
    return "" if i == 0 else ' loading="lazy"'


R = ""
slides = "".join(
    f'<div class="hero-slide"><img src="images/{n}.jpg" alt="CGP Luxury Hotel" width="1320" height="880"{lazy(i)}></div>'
    for i, n in enumerate(["exterior-night", "suite-sunset", "balcony-view", "pool"]))
tiles = "".join(
    f'<figure class="tile"><img src="images/{img}.jpg" alt="" loading="lazy" width="660" height="440"><figcaption><small data-i18n="tile{i}.s">{s}</small><strong data-i18n="tile{i}.t">{t}</strong></figcaption></figure>'
    for i, (img, s, t) in enumerate([("pool", "Thư giãn", "Hồ bơi ngoài trời"), ("balcony-view", "Tầm nhìn", "Ban công ngắm đồng lúa"), ("bathtub", "Phòng tắm", "Bồn tắm thư giãn"), ("suite-gold", "Lưu trú", "Phòng nghỉ sang trọng")], 1))
ams = "".join(f'<li data-i18n="am{i}">{t}</li>' for i, t in enumerate(
    ["Bữa sáng hằng ngày", "Đưa đón sân bay", "Massage thư giãn", "Trà chiều", "Dịch vụ giặt ủi", "Wi-Fi tốc độ cao", "Café &amp; nhà hàng", "Lễ tân 24/24"], 1))
home = f'''<section class="hero" data-fade=".hero-slide" data-auto="5500">
  {slides}
  <button type="button" class="slider-arrow slider-arrow--prev" aria-label="Previous"></button>
  <button type="button" class="slider-arrow slider-arrow--next" aria-label="Next"></button>
  <div class="wrap">
    <div class="hero-copy">
      <p data-i18n="hero.eyebrow">Hội An · Việt Nam</p>
      <h2 data-i18n="hero.title">Nghỉ dưỡng sang trọng giữa lòng Hội An</h2>
    </div>
    <form class="book-box" action="dat-phong/index.html" method="get">
      <h2 data-i18n="box.title">Đặt phòng</h2>
      <p data-i18n="box.sub">Ưu đãi tốt hơn khi đặt trực tiếp trên website</p>
      <div class="book-grid">
        <label class="field"><span data-i18n="box.checkin">Nhận phòng</span><input type="date" name="checkin" required></label>
        <label class="field"><span data-i18n="box.nights">Số đêm</span>
          <select name="nights"><option value="" data-i18n="box.allnights">Tất cả gói</option><option value="3" data-nights="3">3 đêm</option><option value="4" data-nights="4">4 đêm</option><option value="5" data-nights="5">5 đêm</option><option value="7" data-nights="7">7 đêm</option></select></label>
        <label class="field"><span data-i18n="box.guests">Số khách</span>
          <select name="guests"><option value="g2" data-i18n="gl.g2">2 khách</option><option value="g1" data-i18n="gl.g1">1 khách</option><option value="fam" data-i18n="gl.fam">Gia đình</option></select></label>
        <button type="button" class="promo-toggle" data-i18n="box.promo">Tôi có mã ưu đãi</button>
        <label class="field promo-field" hidden><span data-i18n="box.promoph">Mã ưu đãi</span><input type="text" name="promo" maxlength="20" autocomplete="off"></label>
        <button type="submit" class="btn" data-i18n="box.cta">Đặt ngay</button>
      </div>
    </form>
  </div>
  <div class="dots"></div>
</section>

<section class="section">
  <div class="wrap">
    <div class="intro-grid">
      <div class="intro-box">
        <h1 class="h-lg dash" data-i18n="intro.title">CGP Luxury Hotel Hội An</h1>
        <p class="lead" data-i18n="intro.text">{INTRO}</p>
        <a class="btn" href="gioi-thieu/index.html" data-i18n="intro.more">Xem thêm</a>
      </div>
      <div class="intro-slider" data-fade="img" data-auto="6000">
        <img src="images/room-double-balcony.jpg" alt="CGP Luxury Hotel" loading="lazy" width="1320" height="880">
        <img src="images/suite-gold.jpg" alt="" loading="lazy" width="1320" height="880">
        <img src="images/room-twin-window.jpg" alt="" loading="lazy" width="1320" height="880">
        <img src="images/exterior-day.jpg" alt="" loading="lazy" width="1320" height="880">
        <button type="button" class="slider-arrow slider-arrow--prev" aria-label="Previous"></button>
        <button type="button" class="slider-arrow slider-arrow--next" aria-label="Next"></button>
      </div>
    </div>
    {contact()}
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap">
    <h2 class="h-xl" data-i18n="feat.title">Gói lưu trú nổi bật</h2>
    <div class="carousel">
      <div class="carousel-track" data-render="featured" data-ids="6,2,4,10,9,3"></div>
      <button type="button" class="slider-arrow slider-arrow--prev" aria-label="Previous"></button>
      <button type="button" class="slider-arrow slider-arrow--next" aria-label="Next"></button>
    </div>
    <div class="dots"></div>
  </div>
</section>

<section class="section section--light" id="services" style="padding-bottom:0">
  <div class="wrap services-head">
    <h2 class="h-xl dash" data-i18n="svc.title">Dịch vụ &amp; tiện nghi</h2>
    <p class="lead" data-i18n="svc.text">Dù là kỳ nghỉ cuối tuần ngắn ngày hay một chuyến lưu trú dài, quý khách luôn được tận hưởng sự tiện nghi hiện đại cùng lòng hiếu khách ấm áp của người Việt.</p>
    <ul class="amenities">{ams}</ul>
  </div>
  <div class="service-tiles">{tiles}</div>
</section>

<section class="section" id="packages">
  <div class="wrap">
    <h2 class="h-xl dash" data-i18n="pk.title">Bộ sưu tập gói lưu trú</h2>
    <p class="lead" style="margin-top:22px" data-i18n="pk.text">13 gói lưu trú được thiết kế cho mọi hành trình: thư giãn, lãng mạn, gia đình, lưu trú dài ngày và du lịch một mình.</p>
    <div class="pkg-grid" data-render="grid" data-ids="1,5,8,7,11,12,13"></div>
    <p class="pkg-more"><a class="btn btn--navy" href="dat-phong/index.html" data-i18n="pk.all">Xem tất cả &amp; đặt phòng</a></p>
  </div>
</section>

<section class="section section--light">
  <div class="wrap">
    <h2 class="h-xl dash" data-i18n="nw.title">Tin tức &amp; ưu đãi</h2>
    <div class="news-grid" data-render="news" data-limit="3"></div>
    <p class="pkg-more"><a class="btn btn--ghost" href="tin-tuc/index.html" data-i18n="nw.all">Xem tất cả tin tức</a></p>
  </div>
</section>

{cta(R)}'''
page("index.html", "", "CGP Luxury Hotel Hội An", ["home", "pages"], "home", home, sub=False)

# ---------------- About ----------------
R = "../"
why = "".join(
    f'<li><h3 class="h-md" data-i18n="ab.w{i}t">{t}</h3><p data-i18n="ab.w{i}d">{d}</p></li>'
    for i, (t, d) in enumerate([("Vị trí yên tĩnh", "Không gian yên bình, gần trung tâm Hội An."), ("Thiết kế hiện đại", "Không gian sang trọng, tiện nghi cao cấp."), ("Hồ bơi ngoài trời", "Thư giãn giữa khu vườn xanh mát."), ("Dịch vụ tận tâm 24/24", "Sự hiếu khách ấm áp của người Việt.")], 1))
gal = "".join(f'<img src="{R}images/{n}.jpg" alt="" loading="lazy" width="660" height="440">' for n in
              ["exterior-day", "suite-gold", "pool", "room-romantic", "bathtub", "room-twin", "balcony-view", "suite-sunset", "room-window"])
about = f'''{banner(R, "exterior-day", "ab.banner", "Giới thiệu", "ab.bannersub", "Về CGP Luxury Hotel Hội An")}

<section class="section">
  <div class="wrap about-grid">
    <div>
      <h2 class="h-xl dash" data-i18n="ab.h1">Chào mừng đến với CGP Luxury Hotel Hội An</h2>
      <p class="lead" data-i18n="intro.text">{INTRO}</p>
      <p class="lead" data-i18n="ab.p2">Các phòng nghỉ ngập tràn ánh sáng tự nhiên với cửa sổ vòm lớn, ban công riêng nhìn ra đồng lúa và phố thị Hội An, cùng bồn tắm thư giãn ở những hạng phòng chọn lọc.</p>
      <p class="lead" data-i18n="ab.p3">Từ bữa sáng mỗi ngày, hồ bơi ngoài trời đến dịch vụ đưa đón sân bay, trà chiều và massage – đội ngũ của chúng tôi luôn sẵn sàng chăm chút từng chi tiết nhỏ cho kỳ nghỉ của quý khách.</p>
      <a class="btn" href="{R}dat-phong/index.html" data-i18n="box.cta">Đặt ngay</a>
    </div>
    <div class="about-media">
      <img src="{R}images/exterior-night.jpg" alt="CGP Luxury Hotel" width="1320" height="880">
      <img src="{R}images/suite-arch.jpg" alt="" loading="lazy" width="1320" height="880">
    </div>
  </div>
</section>

<section class="section section--light">
  <div class="wrap">
    <h2 class="h-xl dash" data-i18n="ab.why">Vì sao chọn CGP Luxury Hotel</h2>
    <ul class="why">{why}</ul>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <h2 class="h-xl dash" data-i18n="ab.gallery">Thư viện ảnh</h2>
    <div class="gallery">{gal}</div>
  </div>
</section>

<section class="section section--light">
  <div class="wrap">
    <h2 class="h-xl dash" data-i18n="ab.contact">Liên hệ &amp; vị trí</h2>
    {contact()}
  </div>
</section>

{cta(R)}'''
page("gioi-thieu/index.html", R, "Giới thiệu | CGP Luxury Hotel Hội An", ["pages"], "about", about)

# ---------------- News ----------------
news = f'''{banner(R, "balcony-view", "nw.banner", "Tin tức", "nw.bannersub", "Cập nhật từ CGP Luxury Hotel Hội An")}

<section class="section">
  <div class="wrap posts" data-render="news-full"></div>
</section>

{cta(R)}'''
page("tin-tuc/index.html", R, "Tin tức | CGP Luxury Hotel Hội An", ["pages"], "news", news)

# ---------------- Booking ----------------
steps = "".join(f'<li data-step="{i}"><b>{i}</b><span data-i18n="st.{i}">{t}</span></li>' for i, t in enumerate(["Chọn gói", "Thông tin khách", "Thanh toán", "Xác nhận"], 1))
cats = "".join(f'<button type="button" data-cat="{c}" data-i18n="cat.{c}">{t}</button>' for c, t in
               [("all", "Tất cả"), ("relax", "Thư giãn &amp; nghỉ dưỡng"), ("romance", "Lãng mạn &amp; kỷ niệm"), ("family", "Gia đình"), ("long", "Lưu trú dài ngày"), ("sig", "Bộ sưu tập Signature"), ("solo", "Du lịch một mình")])
terms = "".join(f'<li data-i18n="terms.{i}"></li>' for i in range(1, 6))
booking = f'''{banner(R, "suite-sunset", "bk.banner", "Đặt phòng", "bk.bannersub", "Chọn gói lưu trú phù hợp với bạn")}

<section class="section booking">
  <div class="wrap">
    <ol class="steps">{steps}</ol>
    <div class="booking-grid">
      <div class="booking-main">

        <div class="panel" data-panel="1">
          <div class="filters">
            <label class="field"><span data-i18n="box.checkin">Nhận phòng</span><input type="date" id="f-checkin"></label>
            <label class="field"><span data-i18n="box.nights">Số đêm</span>
              <select id="f-nights"><option value="" data-i18n="cat.all">Tất cả</option><option value="3" data-nights="3">3 đêm</option><option value="4" data-nights="4">4 đêm</option><option value="5" data-nights="5">5 đêm</option><option value="7" data-nights="7">7 đêm</option></select></label>
            <label class="field"><span data-i18n="box.guests">Số khách</span>
              <select id="f-guests"><option value="" data-i18n="cat.all">Tất cả</option><option value="g1" data-i18n="gl.g1">1 khách</option><option value="g2" data-i18n="gl.g2">2 khách</option><option value="fam" data-i18n="gl.fam">Gia đình</option></select></label>
          </div>
          <div class="cats">{cats}</div>
          <div class="pkg-list" id="pkg-list"></div>
        </div>

        <form class="panel" data-panel="2" hidden novalidate>
          <h2 class="h-lg dash" data-i18n="fm.title">Thông tin khách hàng</h2>
          <div class="form-grid">
            <label class="input"><span data-i18n="fm.name">Họ và tên</span><input type="text" id="g-name" autocomplete="name" required></label>
            <label class="input"><span data-i18n="c.email">Email</span><input type="email" id="g-email" autocomplete="email" required></label>
            <label class="input"><span data-i18n="fm.phone">Số điện thoại</span><input type="tel" id="g-phone" autocomplete="tel" required></label>
            <label class="input"><span data-i18n="fm.country">Quốc gia</span><input type="text" id="g-country" autocomplete="country-name"></label>
            <label class="input input--full"><span data-i18n="fm.note">Yêu cầu đặc biệt (không bắt buộc)</span><textarea id="g-note" rows="4"></textarea></label>
          </div>
          <p class="form-error" id="form-error" hidden data-i18n="fm.req"></p>
        </form>

        <div class="panel" data-panel="3" hidden>
          <h2 class="h-lg dash" data-i18n="pay.title">Phương thức thanh toán</h2>
          <div class="pay-methods">
            <label><input type="radio" name="pay" value="card" checked><span data-i18n="pay.card">Thẻ quốc tế (Visa / Mastercard / JCB)</span></label>
            <label><input type="radio" name="pay" value="atm"><span data-i18n="pay.atm">Thẻ ATM nội địa</span></label>
            <label><input type="radio" name="pay" value="qr"><span data-i18n="pay.qr">Quét mã QR</span></label>
          </div>
          <p class="pay-note" data-i18n="pay.secure">Thanh toán trực tuyến an toàn qua cổng PayOne.</p>
          <p class="pay-demo" data-i18n="pay.demo">Bản demo: chưa kết nối cổng thanh toán thật, không có giao dịch nào được thực hiện.</p>
          <label class="agree"><input type="checkbox" id="agree"><span data-i18n="pay.agree">Tôi đồng ý với điều khoản &amp; điều kiện đặt phòng</span></label>
        </div>

        <div class="panel done" data-panel="4" hidden>
          <div class="done-mark"></div>
          <h2 class="h-xl" data-i18n="ok.title">Đặt phòng thành công!</h2>
          <p class="lead" data-i18n="ok.text"></p>
          <p class="done-code"><span data-i18n="ok.code">Mã đặt phòng</span><strong id="done-code"></strong></p>
          <a class="btn" href="{R}index.html" data-i18n="ok.home">Về trang chủ</a>
        </div>

        <details class="terms" id="terms">
          <summary data-i18n="terms.title">Điều khoản chung</summary>
          <ul class="ticks">{terms}</ul>
        </details>
      </div>

      <aside class="summary">
        <h2 class="h-md" data-i18n="sum.title">Tóm tắt đặt phòng</h2>
        <div id="sum-body"></div>
        <label class="input" id="sum-promo"><span data-i18n="sum.promo">Mã ưu đãi</span><input type="text" id="f-promo" maxlength="20" autocomplete="off"></label>
        <div class="sum-actions">
          <button type="button" class="btn btn--block" id="btn-next" data-i18n="sum.next">Tiếp tục</button>
          <button type="button" class="btn btn--ghost btn--block" id="btn-back" data-i18n="sum.back" hidden>Quay lại</button>
        </div>
      </aside>
    </div>
  </div>
</section>

<div class="gateway" id="gateway" hidden><div><i></i><p data-i18n="pay.proc">Đang kết nối cổng thanh toán PayOne…</p></div></div>'''
page("dat-phong/index.html", R, "Đặt phòng | CGP Luxury Hotel Hội An", ["booking"], "book", booking, scripts=["booking"])
print("built")
