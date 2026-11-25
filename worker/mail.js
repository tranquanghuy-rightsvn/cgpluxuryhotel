/* Email sau khi thanh toán OnePay thành công, gửi qua Cloudflare Email Service (binding EMAIL):
     - khách: xác nhận đặt phòng, đúng ngôn ngữ khách đã đặt (vi/en/ko/zh/ru/de)
     - khách sạn (HOTEL_NOTIFY_EMAIL): báo có đơn mới đã thanh toán, tiếng Việt.
   Gửi lỗi -> chỉ ghi log, không làm hỏng xử lý thanh toán. Chưa cấu hình EMAIL (chạy local) -> in email ra log. */
import PACKAGES from "./packages.json";

const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const LOCALE = { vi: "vi-VN", en: "en-GB", ko: "ko-KR", zh: "zh-CN", ru: "ru-RU", de: "de-DE" };
const day = (ymd, lang) => new Date(ymd + "T00:00:00Z").toLocaleDateString(LOCALE[lang] || "vi-VN", { timeZone: "UTC", weekday: "long", day: "numeric", month: "long", year: "numeric" });
const usd = (n) => "USD " + Number(n).toLocaleString("en-US");
const vnd = (n) => Number(n).toLocaleString("vi-VN") + " ₫";

const HOTEL = {
  name: "CGP Luxury Hotel",
  addr: "67 Lý Thường Kiệt, TP. Hội An, Quảng Nam, Việt Nam",
  phone: "(+84) 905 926 638",
  email: "cgpluxuryhotelhoian@gmail.com",
};

/* [vi, en, ko, zh, ru, de] */
const T = {
  subject: ["Xác nhận đặt phòng {code} — CGP Luxury Hotel", "Booking confirmation {code} — CGP Luxury Hotel", "예약 확인 {code} — CGP 럭셔리 호텔", "预订确认 {code} — CGP 奢华酒店", "Подтверждение бронирования {code} — CGP Luxury Hotel", "Buchungsbestätigung {code} — CGP Luxury Hotel"],
  title: ["Đặt phòng thành công!", "Your booking is confirmed!", "예약이 완료되었습니다!", "预订成功！", "Бронирование подтверждено!", "Ihre Buchung ist bestätigt!"],
  hello: ["Kính gửi {name},", "Dear {name},", "{name} 님께,", "尊敬的 {name}：", "Уважаемый(ая) {name},", "Liebe/r {name},"],
  intro: ["Cảm ơn quý khách đã lựa chọn CGP Luxury Hotel. Chúng tôi đã nhận được thanh toán và xác nhận đặt phòng của quý khách như sau:", "Thank you for choosing CGP Luxury Hotel. We have received your payment and your booking is confirmed:", "CGP 럭셔리 호텔을 선택해 주셔서 감사합니다. 결제가 완료되어 아래와 같이 예약이 확정되었습니다.", "感谢您选择 CGP 奢华酒店。我们已收到您的付款，您的预订已确认：", "Спасибо, что выбрали CGP Luxury Hotel. Мы получили оплату, ваше бронирование подтверждено:", "Vielen Dank, dass Sie sich für das CGP Luxury Hotel entschieden haben. Wir haben Ihre Zahlung erhalten, Ihre Buchung ist bestätigt:"],
  code: ["Mã đặt phòng", "Booking code", "예약 번호", "预订编号", "Код бронирования", "Buchungscode"],
  pkg: ["Gói lưu trú", "Package", "패키지", "套餐", "Пакет", "Paket"],
  ci: ["Nhận phòng", "Check-in", "체크인", "入住", "Заезд", "Anreise"],
  co: ["Trả phòng", "Check-out", "체크아웃", "退房", "Выезд", "Abreise"],
  from: ["từ 14:00", "from 14:00", "14:00부터", "14:00 起", "с 14:00", "ab 14:00"],
  till: ["trước 12:00", "until 12:00", "12:00까지", "12:00 前", "до 12:00", "bis 12:00"],
  guests: ["Số khách", "Guests", "인원", "人数", "Гости", "Gäste"],
  adults: ["{n} người lớn", "{n} adult(s)", "성인 {n}명", "{n} 位成人", "взрослых: {n}", "{n} Erwachsene"],
  kids: ["{n} trẻ em", "{n} child(ren)", "어린이 {n}명", "{n} 位儿童", "детей: {n}", "{n} Kind(er)"],
  paid: ["Đã thanh toán", "Amount paid", "결제 금액", "已付金额", "Оплачено", "Bezahlt"],
  txn: ["Mã giao dịch OnePay", "OnePay transaction no.", "OnePay 거래 번호", "OnePay 交易号", "Номер транзакции OnePay", "OnePay-Transaktionsnr."],
  note: ["Yêu cầu riêng", "Special request", "요청 사항", "特别要求", "Особые пожелания", "Besondere Wünsche"],
  bring: ["Vui lòng mang theo giấy tờ tùy thân (CCCD/hộ chiếu) khi nhận phòng. Nếu cần thay đổi hoặc hỗ trợ, quý khách chỉ cần trả lời email này hoặc gọi cho chúng tôi.", "Please bring your ID or passport at check-in. If you need any change or assistance, simply reply to this email or call us.", "체크인 시 신분증 또는 여권을 지참해 주세요. 변경이나 도움이 필요하시면 이 메일에 회신하시거나 전화해 주세요.", "办理入住时请携带身份证件或护照。如需更改或协助，请直接回复本邮件或致电我们。", "Пожалуйста, возьмите с собой паспорт при заезде. Если нужны изменения или помощь — просто ответьте на это письмо или позвоните нам.", "Bitte bringen Sie beim Check-in Ihren Ausweis oder Reisepass mit. Für Änderungen oder Fragen antworten Sie einfach auf diese E-Mail oder rufen Sie uns an."],
  bye: ["Hẹn gặp quý khách tại Hội An!", "We look forward to welcoming you in Hoi An!", "호이안에서 뵙기를 기대합니다!", "期待在会安与您相见！", "Ждём вас в Хойане!", "Wir freuen uns, Sie in Hoi An begrüßen zu dürfen!"],
  auto: ["Email tự động từ cgpgrouphotel.com", "Automatic email from cgpgrouphotel.com", "cgpgrouphotel.com 자동 발송 메일", "来自 cgpgrouphotel.com 的自动邮件", "Автоматическое письмо от cgpgrouphotel.com", "Automatische E-Mail von cgpgrouphotel.com"],
};
const LANGS = ["vi", "en", "ko", "zh", "ru", "de"];
/* vi/ko/zh viết Họ trước Tên ("Nguyen Van A"), các tiếng còn lại Tên trước */
const fullName = (b, lang) => (["vi", "ko", "zh"].includes(lang) ? b.last_name + " " + b.first_name : b.first_name + " " + b.last_name);
const tr = (key, lang, vars = {}) => {
  let s = T[key][Math.max(0, LANGS.indexOf(lang))];
  for (const k in vars) s = s.replace("{" + k + "}", vars[k]);
  return s;
};

function layout(title, lines, rows, foot) {
  const row = ([k, v]) =>
    '<tr><td style="padding:8px 0;border-bottom:1px solid #eee;color:#727272;font-size:14px;width:42%">' + esc(k) +
    '</td><td style="padding:8px 0;border-bottom:1px solid #eee;font-size:14px;font-weight:bold">' + v + "</td></tr>";
  const html =
    '<!doctype html><html><body style="margin:0;background:#efece4;font-family:Arial,Helvetica,sans-serif;color:#2f3135">' +
    '<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td align="center" style="padding:24px 12px">' +
    '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:580px;background:#fff">' +
    '<tr><td style="background:#2f3135;padding:20px 28px;color:#d9b77e;font-size:20px;letter-spacing:3px;font-family:Georgia,serif">CGP LUXURY HOTEL</td></tr>' +
    '<tr><td style="padding:28px">' +
    '<h1 style="margin:0 0 16px;font-size:22px;font-weight:normal;font-family:Georgia,serif">' + esc(title) + "</h1>" +
    lines.map((l) => '<p style="margin:0 0 12px;font-size:15px;line-height:1.6">' + l + "</p>").join("") +
    '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:16px 0 20px">' + rows.map(row).join("") + "</table>" +
    foot.map((l) => '<p style="margin:0 0 12px;font-size:14px;line-height:1.6;color:#555">' + l + "</p>").join("") +
    "</td></tr>" +
    '<tr><td style="padding:16px 28px;background:#f7f5f0;font-size:12px;line-height:1.7;color:#727272">' +
    esc(HOTEL.name) + " · " + esc(HOTEL.addr) + "<br>" + esc(HOTEL.phone) + " · " + esc(HOTEL.email) + "</td></tr>" +
    "</table></td></tr></table></body></html>";
  const strip = (s) => String(s).replace(/<br\s*\/?>/g, "\n").replace(/<[^>]+>/g, "").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'");
  const text =
    "CGP LUXURY HOTEL\n\n" + title + "\n\n" + lines.map(strip).join("\n\n") + "\n\n" +
    rows.map(([k, v]) => k + ": " + strip(v)).join("\n") + "\n\n" + foot.map(strip).join("\n\n") +
    "\n\n—\n" + HOTEL.name + " · " + HOTEL.addr + "\n" + HOTEL.phone + " · " + HOTEL.email;
  return { html, text };
}

function guestMail(b) {
  const L = b.lang;
  const pkg = PACKAGES[b.pkg];
  const guests = tr("adults", L, { n: b.adults }) + (b.children ? ", " + tr("kids", L, { n: b.children }) : "");
  const rows = [
    [tr("code", L), '<span style="color:#3c6098;letter-spacing:1px">' + esc(b.code) + "</span>"],
    [tr("pkg", L), esc(pkg ? pkg.names[L] || pkg.names.en : "#" + b.pkg)],
    [tr("ci", L), esc(day(b.checkin, L)) + " — " + esc(tr("from", L))],
    [tr("co", L), esc(day(b.checkout, L)) + " — " + esc(tr("till", L))],
    [tr("guests", L), esc(guests)],
    [tr("paid", L), esc(vnd(b.amount_vnd)) + ' <span style="font-weight:normal;color:#727272">(' + esc(usd(b.amount_usd)) + ")</span>"],
  ];
  if (b.txn_no) rows.push([tr("txn", L), esc(b.txn_no)]);
  if (b.note) rows.push([tr("note", L), esc(b.note)]);
  return [tr("subject", L, { code: b.code }), layout(tr("title", L), [esc(tr("hello", L, { name: fullName(b, L) })), esc(tr("intro", L))], rows, [esc(tr("bring", L)), esc(tr("bye", L)), '<span style="font-size:12px;color:#999">' + esc(tr("auto", L)) + "</span>"])];
}

function hotelMail(b) {
  const pkg = PACKAGES[b.pkg];
  const rows = [
    ["Mã đặt phòng", esc(b.code)],
    ["Khách", esc(fullName(b, "vi"))],
    ["Điện thoại", esc(b.phone)],
    ["Email", esc(b.email)],
    ["Quốc gia", esc(b.country || "—")],
    ["Gói", esc(pkg ? pkg.names.vi : "#" + b.pkg)],
    ["Nhận phòng", esc(day(b.checkin, "vi"))],
    ["Trả phòng", esc(day(b.checkout, "vi"))],
    ["Số khách", esc(b.adults + " người lớn" + (b.children ? ", " + b.children + " trẻ em" : ""))],
    ["Đã thu", esc(vnd(b.amount_vnd)) + " (" + esc(usd(b.amount_usd)) + ")"],
    ["Mã giao dịch OnePay", esc(b.txn_no || "—")],
    ["Thẻ", esc([b.card_type, b.card_num].filter(Boolean).join(" ") || "—")],
    ["Ngôn ngữ khách", esc(b.lang)],
    ["Nhận tin ưu đãi", b.newsletter ? "Có" : "Không"],
  ];
  if (b.promo) rows.push(["Mã ưu đãi khách nhập", esc(b.promo)]);
  if (b.note) rows.push(["Yêu cầu riêng", esc(b.note)]);
  return ["[Đơn mới đã thanh toán] " + b.code + " — " + fullName(b, "vi"), layout("Có đơn đặt phòng mới đã thanh toán qua OnePay", ["Khách đã nhận email xác nhận. Thông tin đơn:"], rows, ["Trả lời email này sẽ gửi thẳng tới khách (" + esc(b.email) + ")."])];
}

async function send(env, to, [subject, content], replyTo) {
  if (!env.EMAIL || !to) {
    console.log("mail (chưa cấu hình EMAIL, chỉ in ra log) ->", to, "|", subject, "\n" + content.text);
    return false;
  }
  try {
    await env.EMAIL.send({
      to,
      from: { email: env.MAIL_FROM, name: "CGP Luxury Hotel" },
      ...(replyTo ? { replyTo } : {}),
      subject,
      html: content.html,
      text: content.text,
    });
    return true;
  } catch (err) {
    console.error("mail: gửi lỗi", subject, to, String(err));
    return false;
  }
}

/* Trả về true nếu email cho khách đã gửi được */
export async function sendPaidMails(env, b) {
  const guestOk = await send(env, b.email, guestMail(b), env.MAIL_REPLY_TO || HOTEL.email);
  if (env.HOTEL_NOTIFY_EMAIL) await send(env, env.HOTEL_NOTIFY_EMAIL, hotelMail(b), b.email);
  return guestOk;
}
