# GAS CMS — CGP Luxury Hotel (cgpgrouphotel.com)

Quyết định nghiệp vụ CHỐT cho trang quản trị. Đọc toàn bộ file này trước khi sửa bất kỳ file nào
trong `gas/`. Code lệch khỏi file này = sửa code hoặc hỏi lại chủ dự án, không tự đổi file này.

- Apps Script: script ID `17cnYLE_yoAFTIfn_cfFQ6jWhZ8jXv_1jIJ7jiQa_D0m2AYD04rXgdny3`
- Web app `/exec`: `https://script.google.com/macros/s/AKfycby8KtHsZnuVNy3l1-nX4pUS-zYyhfW79HrydD2BXBkg0ZgeFvUuvRdE7iWknTtcG9HH/exec`
- Trang vào: `https://cgpgrouphotel.com/admin/` (nhúng iframe, kèm link thoát mở thẳng `/exec`)
- Dự án mẫu: xevip (skill free-cms-static-site-pipeline). `gas/` nằm trong `.gitignore`, deploy bằng clasp.

## 0. Phạm vi (đúng 5 mục)

1. Tin tức — thêm/sửa/xoá bài, 6 ngôn ngữ, nút dịch tự động.
2. Đơn đặt phòng — xem đơn từ website (D1 của Worker), đánh dấu đã xử lý.
3. Gói lưu trú & giá — sửa giá, bật/tắt, sửa tên/tagline/mô tả (6 ngôn ngữ).
4. Tỷ giá USD → VND — số dùng để quy đổi khi thu tiền qua AsiaPay.
5. Người dùng trang quản trị — root / admin / editor.

Không làm: thêm/xoá gói, đổi số đêm/số khách/danh sách "bao gồm"/ảnh của gói, sửa các trang tĩnh khác
(giới thiệu, phòng nghỉ, dịch vụ, thư viện ảnh), form liên hệ.

## I. Đăng nhập & phân quyền

1. Luồng: nhập email → gửi OTP qua Gmail → nhập mã → vào Admin. Không mật khẩu, không dựa session Google.
2. Chỉ email có trong Sheet `Users` mới được gửi OTP.
3. Chủ script (account deploy) luôn là `root` ngầm định, không lưu trong Sheet, không hiện trong UI.
4. Ma trận quyền (server kiểm tra ở MỌI hàm, không tin UI):

   | Chức năng | editor | admin | root |
   |---|---|---|---|
   | Tin tức (thêm/sửa/xoá, dịch) | ✔ | ✔ | ✔ |
   | Đơn đặt phòng (xem, đánh dấu đã xử lý, ghi chú) | ✘ | ✔ | ✔ |
   | Gói lưu trú & giá | ✘ | ✔ | ✔ |
   | Tỷ giá USD→VND | ✘ | ✔ | ✔ |
   | Người dùng: thêm/xoá/đổi quyền `editor`, `admin` | ✘ | ✔ | ✔ |

   - editor cố ý KHÔNG thấy thông tin khách đặt phòng (họ tên, điện thoại, email).
   - Qua CMS chỉ gán được `admin`/`editor`; dòng `root` chỉ sửa tay trong Sheet.
   - Không ai tự xoá / tự hạ quyền chính mình.
5. OTP sống 10 phút, cooldown 60 giây/email, sai tối đa 5 lần. Token phiên 30 ngày, lưu localStorage.

## II. Tin tức

1. Field có ô nhập (theo từng tab ngôn ngữ vi/en/ko/zh/ru/de, trừ field chung):
   - Chung: Slug (tự sinh từ tiêu đề tiếng Việt, bỏ dấu, gạch ngang; bất biến sau lần Lưu đầu),
     Ngày đăng (mặc định hôm nay), Ảnh cover (bắt buộc).
   - Theo ngôn ngữ: Tiêu đề, Mô tả ngắn (dùng làm meta description + đoạn tóm tắt ở danh sách), Nội dung.
   - Nội dung: TinyMCE tự host, có heading H2/H3, đậm/nghiêng, link, danh sách, bảng, trích dẫn và
     **CÓ chèn ảnh trong nội dung** bằng nút chèn nhanh (mở thẳng file picker, không dùng dialog Image).
   - Cả 6 ngôn ngữ đều bắt buộc (tiêu đề + mô tả + nội dung) — build hiện bài ở mọi ngôn ngữ, nên không cho
     lưu bài thiếu ngôn ngữ; nút Dịch điền sẵn 5 ngôn ngữ trong 1 lần bấm. Tab còn trống có dấu •.
   - Nút **"Dịch từ tiếng Việt"**: dịch tiêu đề + mô tả + nội dung sang 5 ngôn ngữ bằng `LanguageApp`
     (Google Translate, miễn phí, nội dung dịch dạng HTML), điền vào các tab, người dùng sửa lại rồi Lưu.
     Mã đích: en, ko, zh-CN, ru, de. Tab đã có chữ chỉ bị ghi đè sau khi xác nhận. Hàm: `translateTexts`.
   - Chỉ 1 ô TinyMCE; chuyển tab ngôn ngữ thì cất nội dung tab cũ vào bộ nhớ rồi nạp tab mới.
2. Field tự suy, không có ô nhập: `<title>` = tiêu đề + hậu tố site; ảnh share = ảnh cover; số từ (JSON-LD).
3. 6 bài "smart content" đã có (bố cục thiết kế riêng `tv-*`): CMS chỉ sửa **tiêu đề, mô tả, ảnh cover,
   ngày đăng** — nội dung khoá (không mở trong TinyMCE để khỏi vỡ bố cục). Nhận biết bằng việc file
   không có dòng `cms: 1` trong khối `<!-- smart-content -->`.
4. Danh sách bài trong Admin: đọc qua GAS từ GitHub Contents API (`content/tin-tuc/index.json`), luôn mới nhất.
5. Ảnh: nén phía client bằng canvas trước khi upload — cạnh dài tối đa 1600px, JPEG chất lượng 0.82.
   Ảnh RIÊNG 1-1 theo bài: cover `html/images/news-<slug>-<yyMMddHHmmss>.jpg` (tên mới mỗi lần tải để CI
   không dùng nhầm bản WebP cũ; ảnh cover cũ do CMS tải bị xoá lúc Lưu), ảnh trong bài
   `html/images/news/<slug>/<NN>.jpg`. Build tự sinh bản WebP nhiều cỡ cho cover như ảnh hiện có.

## III. Sửa tin tức

- Slug khoá cả server (throw) lẫn client (disable input).
- Ảnh hiển thị trong Admin dùng URL tuyệt đối `raw.githubusercontent.com/<owner>/<repo>/<branch>/...`.
- Form dùng lại giữa tạo mới/sửa: reset mọi trạng thái khoá khi mở form tạo mới.

## IV. Xoá tin tức

- Xoá đủ: 6 file ngôn ngữ + ảnh riêng của bài (cover + thư mục `news/<slug>/`) + gỡ khỏi `index.json`
  (ghi sau cùng). Ảnh riêng 1-1 nên xoá kèm an toàn.
- Bài smart content cũ: KHÔNG cho xoá qua CMS (chỉ sửa metadata) — ảnh của chúng dùng chung với trang khác.
- Bắt buộc popup xác nhận.

## V. Đơn đặt phòng

- Nguồn: D1 `bookings` của Worker. GAS gọi `GET <WORKER_API_URL>/api/admin/bookings` và
  `POST /api/admin/bookings/<code>` với header `x-admin-key: <WORKER_ADMIN_KEY>` (Worker secret
  `ADMIN_API_KEY`, so sánh thời gian hằng). Không lưu đơn vào Sheet.
- Danh sách: mới nhất trước, 50 đơn/trang, lọc theo trạng thái thanh toán (pending/paid/failed/expired)
  và "đã xử lý/chưa xử lý", tìm theo mã đơn / tên / email / điện thoại.
- Chi tiết: mọi thông tin khách + gói + ngày + số tiền USD/VND + mã giao dịch AsiaPay + thẻ + thời điểm.
- Thao tác duy nhất: đánh dấu **đã xử lý / chưa xử lý** + **ghi chú nội bộ** (lưu kèm email người làm
  và thời điểm). Không sửa/xoá/hoàn tiền đơn từ CMS (hoàn tiền làm trong Merchant Admin của AsiaPay).
- Cần Worker bản có thanh toán (nhánh `asiapay-integration`) đã deploy; chưa có thì tab báo rõ.

## VI. Gói lưu trú, giá, tỷ giá

- Sửa được: giá USD (số nguyên > 0), hiện/ẩn gói, tên gói, nhãn (badge), tagline, mô tả — 6 ngôn ngữ,
  có nút dịch như mục II.1.
- Tỷ giá USD→VND: 1 số nguyên (vd 26000).
- Gói ẩn: không hiện trên site, không đặt được (Worker từ chối).
- Có hiệu lực sau khi CI build + deploy xong (Worker dùng giá/tỷ giá đóng gói lúc deploy — không đọc lúc chạy).

## VII. UX chung

- 2 loại popup riêng: xác nhận (Huỷ/Đồng ý) và thông báo kết quả (Đóng). Không alert/confirm native.
- Mọi nút async: disable + spinner, tự phục hồi khi lỗi. Sau Lưu/Xoá danh sách tự cập nhật.
- Chuyển tab chỉ là hiệu ứng giao diện. Đăng nhập: 1 lượt `boot` lấy hết dữ liệu.
- Lần sau: hiện ngay từ cache (stale-while-revalidate). Key cache mang `CLIENT_BUILD` (băm tự động từ
  `app.html` + `js.html`), tự dọn key khác phiên bản.
- Giao diện tiếng Việt.

## VIII. Lưu trữ

- Google Sheet "CGP Luxury Hotel CMS" (tự tạo): `Users` (email, role). OTP/token trong CacheService/Properties.
- GitHub repo `tranquanghuy-rightsvn/cgpluxuryhotel`, nhánh `master` (đường dẫn cố định):
  - `content/tin-tuc/<slug>/<lang>.html` — 1 file/ngôn ngữ, khối `<!-- smart-content ... -->`
    (title, description, cover, date, cms) + nội dung HTML.
  - `content/tin-tuc/index.json` — danh sách bài (commit CHỐT của thao tác tin tức, trigger CI).
  - `data/packages.json` — giá + hiện/ẩn + chữ 6 ngôn ngữ của 13 gói (commit chốt, trigger CI).
  - `data/settings.json` — `{ "usd_vnd_rate": 26000 }` (commit chốt, trigger CI).
  - `html/images/news-<slug>.jpg`, `html/images/news/<slug>/NN.jpg` — ảnh.
- CI (GitHub Actions) chạy khi đổi 3 file chốt ở trên: build (`export.cjs` + `build.py`) → commit `html/`
  + `worker/packages.json` → `wrangler deploy`. Độ trễ ước tính 2–4 phút.

## IX. Bug đã gặp ở dự án này

- CI checkout đặt mọi file cùng mtime, mà build.py quyết định "ảnh phái sinh cũ chưa" bằng mtime → có thể
  tạo lại ảnh hàng loạt / gọi Chrome (chỉ có trên Mac). Cách né: workflow đẩy mtime ảnh gốc về 2000-01-01
  trước khi build, chỉ ảnh phái sinh CHƯA CÓ mới được tạo.
- build.py có nhiều danh sách id gói gõ cứng (menu, trang chủ) → ẩn gói làm KeyError. Cách né: mọi chỗ lọc
  `if i in P`; link `@/goi-luu-tru/<gói ẩn>/` trong bài smart content tự trỏ về trang danh sách gói.

## X. Script Properties

- `GITHUB_TOKEN` (fine-grained, Contents: Read & write cho repo trên), `GITHUB_OWNER`, `GITHUB_REPO`,
  `GITHUB_BRANCH` — bắt buộc.
- `WORKER_API_URL` (vd `https://cgpgrouphotel.com`), `WORKER_ADMIN_KEY` — cho tab Đơn đặt phòng.
- `SPREADSHEET_ID` — tự tạo, không cần điền.
- Hàm `setup()` (chạy tay trong trình soạn Apps Script): xin cấp quyền, tạo Sheet, điền sẵn 4 property không
  bí mật (`GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH`, `WORKER_API_URL`), báo property còn thiếu.
