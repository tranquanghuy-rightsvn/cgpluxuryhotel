# Báo cáo clone — diamondseahotel.com → CGP Luxury Hotel Hội An (lần 2: clone 1:1)

Lần 1 dựng giao diện mới "theo cảm hứng" → khách không duyệt. Lần này **clone đúng HTML/CSS của trang gốc**
(đo computed style bằng Chrome headless), chỉ thay nội dung bằng dữ liệu CGP (fanpage + `info-rooms.docx`).

## Trang đã clone

| Trang clone | Trang gốc tương ứng |
|---|---|
| `index.html` | `/` (header, banner + hộp "Book rooms", giới thiệu + slider, bản đồ + liên hệ, Featured Promotion → **Featured Packages**, Featured Services, Rooms & Suites → **Stay Packages**, News & Events, footer) |
| `gioi-thieu/index.html` | `/about-us` (banner trang con; trang gốc trống nên ghép lại các khối có sẵn của trang chủ) |
| `tin-tuc/index.html` | `/news` (danh sách + sidebar Search / Recent Posts / Room List → Package List) |
| `tin-tuc/<bài>/index.html` ×4 | `/news/<bài>` |
| `dat-phong/index.html` | `/booking` — clone widget Exely 5 bước: Details of your stay → Select a room (gói) → Select a rate plan (chi tiết gói) → Enter your details + Payment method (PayOne) → xác nhận |

Font giữ đúng như trang gốc đang hiển thị: tiêu đề Times (trang gốc khai báo "Playfair Display" nhưng không tải được → trình duyệt dùng Times), menu/nút Lato 700, nội dung Arial, widget đặt phòng Open Sans + Lora. Lato không có dấu tiếng Việt/Nga → riêng các ký tự đó mượn Open Sans.

## File

- HTML: 8 trang (trên) — sinh bằng `.work/build.py`
- CSS: `css/fonts.css`, `css/main.css` (header, footer, nút, banner trang con, sidebar), `css/home.css`, `css/news.css`, `css/booking.css`
- JS: `js/i18n.js` (6 ngôn ngữ), `js/data.js` (13 gói + 4 tin), `js/main.js`, `js/booking.js`
- Ảnh: 17 ảnh khách sạn (từ fanpage), 2 icon mũi tên slider + cờ vi/en (từ site gốc), cờ ko/zh/ru/de (SVG tự vẽ)
- Font: Lato 700, Open Sans 400/700, Lora 400 (self-host)

## Pixel-diff (1366×768, so từng section)

Ảnh khách sạn khác ảnh gốc (cố ý), nên đo 2 kiểu:
- **Che ảnh**: mọi ảnh/bản đồ phủ cùng màu xám ở cả 2 bên → đo đúng bố cục, màu, chữ.
- **Thô**: ảnh thật → chủ yếu phản ánh việc đã thay ảnh, không dùng để chấm.

| Section | Che ảnh | Thô |
|---|---|---|
| Header | 98.13% | 41.88% |
| Banner | 99.15% | 28.81% |
| Hộp đặt phòng trên banner | 98.22% | — |
| Giới thiệu + liên hệ | 97.28% | 74.29% |
| Featured Packages | 98.44% | 65.90% |
| Featured Services | 97.52% | 97.53% |
| 4 ô dịch vụ | 98.02% | 19.60% |
| Stay Packages (lưới 3+2+2) | 97.72% | 57.66% |
| News & Events | 97.11% | 61.13% |
| Footer | 96.60% | 92.82% |
| Trang Tin tức (dưới banner) | 97.73% | — |
| Trang bài viết (dưới banner) | 93.95% | — |
| Đặt phòng — bước 1 (form tìm phòng) | 93.49% (thô) | |
| Đặt phòng — bước nhập thông tin | 94.87% (thô) | |
| Đặt phòng — bước chọn gói | 79.33% (thô, khác ảnh phòng) | |

Ghi chú: footer gốc cao hơn 112px vì có ảnh huy hiệu TripAdvisor/Agoda/Booking + logo Bộ Công Thương — không phải của CGP nên bỏ. Trang bài viết thấp hơn do bài CGP ngắn hơn bài gốc. Chỉ số trang con chỉ đo phần dưới banner vì header trang con của site gốc bị lỗi khi chụp headless.

## Responsive / không vỡ giao diện

Đã kiểm tra 1366, 768, 375 cho cả 5 loại trang: không scroll ngang, không ảnh vỡ, không thiếu chữ dịch. Mobile theo bố cục gốc (header trắng: ☰ trái, logo giữa, ngôn ngữ phải; các khối xếp dọc). 1920 chưa chụp lại ở lần 2.

## Giả định / chưa phải thật

- **PayOne chưa tích hợp**: bấm "Pay with PayOne" chỉ hiện màn chờ rồi sinh mã đặt phòng giả; không gọi API, không lưu đơn, không gửi email. Trang có ghi "Demo".
- Ngôn ngữ mặc định là **English** (giống site gốc và nội dung docx); đổi bằng nút cờ. Bản dịch Hàn/Trung/Nga/Đức chưa qua người bản ngữ duyệt.
- "Log in" trên hộp đặt phòng trang chủ (giữ cho giống gốc) dẫn sang trang đặt phòng; widget không có đăng nhập.
- "Extra room +" hiện ghi chú liên hệ khách sạn (demo không hỗ trợ nhiều phòng).
- Bản đồ là iframe Google Maps (cần internet); khi chụp headless ô bản đồ hiển thị trống.
- Link chính sách thanh toán / bảo mật / hoàn huỷ để `#`.

## Cập nhật theo góp ý (2026-11-15)

- Bỏ thanh 4px trên đỉnh header ở mọi trang và mọi trạng thái; thêm `?v=` vào link CSS/JS để trình duyệt không dùng bản cũ.
- Banner trang chủ bỏ ảnh hồ bơi có con vịt.
- Font tiêu đề: Playfair Display (self-host) thay cho Times.
- Tiêu đề thẻ gói cách ảnh 12px.
- Mục "Tin tức & Sự kiện" không còn tràn mép: 3 thẻ/khung, có mũi tên + chấm.
- URL dạng `/slug/` (không còn `index.html` trong link). Cần chạy qua web server.
- **Đa ngôn ngữ dạng trang tĩnh riêng (SEO)**: tiếng Việt ở `/`, các ngôn ngữ khác ở `/en/ /ko/ /zh/ /ru/ /de/` → 48 trang. Mỗi trang có nội dung dịch sẵn trong HTML, `<html lang>`, `<title>`, meta description, canonical, `hreflang` (+ `x-default`), Open Graph; có `sitemap.xml` kèm hreflang. Nút đổi ngôn ngữ là link thật.
- Tên 13 gói đã dịch sang cả 6 ngôn ngữ.
- **Trước khi chạy thật:** điền domain vào `SITE` trong `.work/build.py` rồi build lại — Google yêu cầu URL tuyệt đối cho canonical/hreflang/sitemap; hiện đang để dạng `/en/...`.
- Build: `cd html && python3 .work/build.py` (tự xuất dữ liệu từ `js/i18n.js` + `js/data.js`).
- Gói lưu trú khớp nguyên văn docx (đã đối chiếu tự động 13/13): danh sách quyền lợi đúng thứ tự và câu chữ, thêm đoạn Description (hiện trong popup "Xem chi tiết" và bước chi tiết gói khi đặt phòng), nút Call to Action riêng từng gói, đủ 8 điều khoản chung. Đã dịch sang 6 ngôn ngữ.
- Favicon: `favicon.ico`, `seo/favicon.svg`, `seo/apple-touch-icon.png`, `seo/icon-192/512.png`, `seo/site.webmanifest` (logo chữ CGP vàng đồng trên nền navy, tạm thời như logo).
