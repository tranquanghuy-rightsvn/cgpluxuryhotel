/* Worker "cgpluxuryhotel": phục vụ site tĩnh html/ + API thanh toán OnePay.
   Luồng (tài liệu OnePay mục II-3):
     1. POST /api/booking          trang đặt phòng gửi thông tin khách -> lưu đơn "pending" (D1),
                                   tính tiền TỪ BẢNG GIÁ server (packages.json), trả URL OnePay đã ký
     2. khách thanh toán trên trang OnePay
     3. GET  /api/onepay/return    OnePay chuyển trình duyệt khách về -> xác thực chữ ký, cập nhật đơn,
                                   chuyển về dat-phong/#kq=<mã>.<token> để hiện kết quả
        GET|POST /api/onepay/ipn   OnePay gọi server-to-server (kể cả khi khách đóng trình duyệt)
     4. lần đầu đơn chuyển sang "paid" -> gửi email xác nhận cho khách + email báo khách sạn (đúng 1 lần)
     5. cron 10 phút: đơn pending quá 15 phút -> QueryDR hỏi OnePay (mục II-5)
   GET /api/booking/status?code=&t=  trang kết quả hỏi trạng thái đơn (token chống dò đơn của người khác). */
import PACKAGES from "./packages.json";
import { payUrl, verify, queryDR } from "./onepay.js";
import { sendPaidMails } from "./mail.js";

const LANGS = ["vi", "en", "ko", "zh", "ru", "de"];
const CARD_LIST = { card: "INTERCARD", atm: "DOMESTIC", qr: "QR" }; // vpc_CardList, mục II-4.2

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const now = () => new Date().toISOString();
const randHex = (n) => Array.from(crypto.getRandomValues(new Uint8Array(n)), (b) => b.toString(16).padStart(2, "0")).join("");
const ymd = (s) => /^\d{4}-\d{2}-\d{2}$/.test(s || "") && !isNaN(Date.parse(s + "T00:00:00Z"));
const addDays = (s, n) => new Date(Date.parse(s + "T00:00:00Z") + n * 864e5).toISOString().slice(0, 10);
const vnToday = () => new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10); // ngày hiện tại giờ VN
const clip = (v, n) => String(v == null ? "" : v).trim().slice(0, n);
const bookingPage = (env, lang) => env.SITE_URL + (lang === "vi" ? "" : "/" + lang) + "/dat-phong/";

/* Mã đặt phòng: CGP + 7 ký tự, không có chữ dễ nhầm (0/O, 1/I). Dùng luôn làm vpc_MerchTxnRef. */
function newCode() {
  const A = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ";
  return "CGP" + Array.from(crypto.getRandomValues(new Uint8Array(7)), (b) => A[b % A.length]).join("");
}

/* ---------------------------------------------------------------- 1. tạo đơn + URL thanh toán */
async function createBooking(req, env) {
  let d;
  try {
    d = await req.json();
  } catch {
    return json({ error: "bad_json" }, 400);
  }
  const pkg = PACKAGES[String(d.pkg)];
  const lang = LANGS.includes(d.lang) ? d.lang : "vi";
  const b = {
    pkg: String(d.pkg),
    checkin: d.checkin,
    adults: Math.min(4, Math.max(1, parseInt(d.adults, 10) || 1)),
    children: Math.min(3, Math.max(0, parseInt(d.children, 10) || 0)),
    first_name: clip(d.first, 60),
    last_name: clip(d.last, 60),
    phone: clip(d.phone, 30),
    email: clip(d.email, 120).toLowerCase(),
    country: clip(d.country, 60),
    note: clip(d.note, 1000),
    promo: clip(d.promo, 20),
    newsletter: d.newsletter ? 1 : 0,
    pay_method: CARD_LIST[d.pay] ? d.pay : "card",
    lang,
  };
  const bad = [];
  if (!pkg) bad.push("pkg");
  if (!ymd(b.checkin) || b.checkin < vnToday() || b.checkin > addDays(vnToday(), 730)) bad.push("checkin");
  if (!b.first_name) bad.push("first");
  if (!b.last_name) bad.push("last");
  if (!/^[+\d][\d\s().-]{6,}$/.test(b.phone)) bad.push("phone");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(b.email)) bad.push("email");
  if (d.agree !== true) bad.push("agree");
  if (bad.length) return json({ error: "invalid", fields: bad }, 400);

  // Gói có số đêm cố định: ngày trả phòng và giá tính ở server, không lấy từ trình duyệt
  b.checkout = addDays(b.checkin, pkg.nights);
  b.amount_usd = pkg.usd;
  const rate = Number(env.USD_VND_RATE);
  if (!(rate > 0)) return json({ error: "config" }, 500);
  b.amount_vnd = Math.round((pkg.usd * rate) / 1000) * 1000; // làm tròn nghìn đồng
  b.code = newCode();
  b.view_token = randHex(12);
  b.status = "pending";
  b.created_at = now();

  const cols = Object.keys(b);
  await env.DB.prepare(`INSERT INTO bookings (${cols.join(",")}) VALUES (${cols.map(() => "?").join(",")})`).bind(...cols.map((k) => b[k])).run();

  // vpc_TicketNo: IP khách, tối đa 15 ký tự (IPv6 dài hơn -> cắt bớt; OnePay chỉ dùng để tham khảo)
  const ip = (req.headers.get("cf-connecting-ip") || "127.0.0.1").slice(0, 15);
  const url = await payUrl(env, {
    ref: b.code,
    orderInfo: b.code, // ≤34 ký tự, không dấu, không ký tự đặc biệt
    amountVnd: b.amount_vnd,
    ip,
    locale: lang === "vi" ? "vn" : "en",
    cardList: CARD_LIST[b.pay_method],
  });
  return json({ code: b.code, payUrl: url });
}

/* ---------------------------------------------------------------- 3/4. xử lý kết quả (Return, IPN, QueryDR dùng chung) */
/* Bất biến: đơn đã "paid" không bao giờ bị đổi trạng thái; email chỉ gửi bởi lệnh UPDATE thắng cuộc đua
   (Return và IPN có thể tới cùng lúc — test case IPN-02/03/04, OC-04). */
async function applyResult(env, p, source) {
  const ref = p.vpc_MerchTxnRef;
  if (!ref) return { found: false };
  const b = await env.DB.prepare("SELECT * FROM bookings WHERE code = ?").bind(ref).first();
  if (!b) return { found: false };
  if (p.vpc_Merchant && p.vpc_Merchant !== env.ONEPAY_MERCHANT) {
    console.error(source, "sai merchant", ref, p.vpc_Merchant);
    return { found: true, b };
  }
  const code = String(p.vpc_TxnResponseCode ?? "");
  const amountOk = p.vpc_Amount === String(b.amount_vnd * 100);
  const t = now();

  if (code === "0" && amountOk) {
    const r = await env.DB.prepare(
      "UPDATE bookings SET status='paid', resp_code=?, resp_message=?, txn_no=?, card_type=?, card_num=?, paid_at=?, updated_at=?, paid_via=? WHERE code=? AND status<>'paid'",
    ).bind(code, clip(p.vpc_Message, 200), clip(p.vpc_TransactionNo, 32), clip(p.vpc_Card, 10), clip(p.vpc_CardNum, 20), t, t, source, ref).run();
    if (r.meta.changes === 1) {
      const paid = await env.DB.prepare("SELECT * FROM bookings WHERE code = ?").bind(ref).first();
      return { found: true, b: paid, justPaid: true };
    }
    return { found: true, b: await env.DB.prepare("SELECT * FROM bookings WHERE code = ?").bind(ref).first() };
  }
  if (code === "0" && !amountOk) {
    // Thành công nhưng số tiền không khớp: KHÔNG coi là thành công (mục II-4.3), để pending cho khách sạn kiểm tra
    console.error(source, "số tiền không khớp", ref, p.vpc_Amount, "!=", b.amount_vnd * 100);
    await env.DB.prepare("UPDATE bookings SET resp_code=?, resp_message=?, updated_at=? WHERE code=? AND status='pending'")
      .bind("AMOUNT_MISMATCH", "amount " + clip(p.vpc_Amount, 20), t, ref).run();
    return { found: true, b };
  }
  if (code === "100" || code === "300" || code === "") return { found: true, b }; // QueryDR: đang xử lý -> hỏi tiếp
  await env.DB.prepare("UPDATE bookings SET status='failed', resp_code=?, resp_message=?, updated_at=? WHERE code=? AND status IN ('pending','failed')")
    .bind(clip(code, 10), clip(p.vpc_Message, 200), t, ref).run();
  return { found: true, b: await env.DB.prepare("SELECT * FROM bookings WHERE code = ?").bind(ref).first() };
}

async function mailIfJustPaid(env, res) {
  if (!res.justPaid) return;
  const ok = await sendPaidMails(env, res.b);
  if (ok) await env.DB.prepare("UPDATE bookings SET email_sent_at=? WHERE code=?").bind(now(), res.b.code).run();
}

/* ReturnURL: trình duyệt khách quay về. Chữ ký sai -> không cập nhật gì (đơn vẫn pending, test case OC-05). */
async function onReturn(req, env, ctx) {
  const p = Object.fromEntries(new URL(req.url).searchParams);
  const okSig = await verify(p, env.ONEPAY_HASH_CODE);
  let b = null;
  if (okSig) {
    const res = await applyResult(env, p, "return");
    b = res.b;
    ctx.waitUntil(mailIfJustPaid(env, res));
  } else {
    console.error("return: chữ ký sai", p.vpc_MerchTxnRef);
    if (p.vpc_MerchTxnRef) b = await env.DB.prepare("SELECT * FROM bookings WHERE code = ?").bind(p.vpc_MerchTxnRef).first();
  }
  if (!b) return Response.redirect(env.SITE_URL + "/dat-phong/", 302);
  return Response.redirect(bookingPage(env, b.lang) + "#kq=" + b.code + "." + b.view_token, 302);
}

/* IPN: OnePay gọi server-to-server, GET (query) hoặc POST (form-urlencoded). Trả 200 + body chuẩn khi đã ghi nhận;
   khác 200 -> OnePay gọi lại (3 lần, cách 50s). */
async function onIpn(req, env, ctx) {
  const url = new URL(req.url);
  const p = Object.fromEntries(url.searchParams);
  if (req.method === "POST") {
    const body = await req.text();
    Object.assign(p, Object.fromEntries(new URLSearchParams(body)));
  }
  const plain = (s, status) => new Response(s, { status, headers: { "content-type": "text/plain" } });
  if (!(await verify(p, env.ONEPAY_HASH_CODE))) {
    console.error("ipn: chữ ký sai", p.vpc_MerchTxnRef);
    return plain("responsecode=0&desc=confirm-fail", 400);
  }
  try {
    const res = await applyResult(env, p, "ipn");
    if (!res.found) {
      console.error("ipn: không có đơn", p.vpc_MerchTxnRef);
      return plain("responsecode=0&desc=confirm-fail", 404);
    }
    ctx.waitUntil(mailIfJustPaid(env, res));
    return plain("responsecode=1&desc=confirm-success", 200);
  } catch (err) {
    console.error("ipn: lỗi xử lý", String(err));
    return plain("responsecode=0&desc=confirm-fail", 500);
  }
}

async function status(req, env) {
  const q = new URL(req.url).searchParams;
  const b = await env.DB.prepare("SELECT * FROM bookings WHERE code = ?").bind(clip(q.get("code"), 20)).first();
  if (!b || b.view_token !== q.get("t")) return json({ error: "not_found" }, 404);
  return json({
    code: b.code, status: b.status, pkg: b.pkg, checkin: b.checkin, checkout: b.checkout,
    adults: b.adults, children: b.children, usd: b.amount_usd, vnd: b.amount_vnd, emailSent: !!b.email_sent_at,
  });
}

/* ---------------------------------------------------------------- 5. cron: QueryDR cho đơn treo */
async function sweep(env) {
  const { results } = await env.DB.prepare(
    "SELECT code, created_at FROM bookings WHERE status='pending' AND created_at < ? AND created_at > ? ORDER BY created_at LIMIT 30",
  ).bind(new Date(Date.now() - 15 * 60e3).toISOString(), new Date(Date.now() - 3 * 864e5).toISOString()).all();
  for (const { code, created_at } of results) {
    const r = await queryDR(env, code);
    if (!r) continue;
    if (r.vpc_DRExists === "N") {
      // Khách chưa từng mở / đã bỏ trang thanh toán: quá 1 ngày thì đóng đơn
      if (Date.parse(created_at) < Date.now() - 864e5)
        await env.DB.prepare("UPDATE bookings SET status='expired', updated_at=? WHERE code=? AND status='pending'").bind(now(), code).run();
      continue;
    }
    await mailIfJustPaid(env, await applyResult(env, r, "querydr"));
  }
}

export default {
  async fetch(req, env, ctx) {
    const { pathname } = new URL(req.url);
    try {
      if (pathname === "/api/booking" && req.method === "POST") return await createBooking(req, env);
      if (pathname === "/api/booking/status" && req.method === "GET") return await status(req, env);
      if (pathname === "/api/onepay/return" && req.method === "GET") return await onReturn(req, env, ctx);
      if (pathname === "/api/onepay/ipn" && (req.method === "GET" || req.method === "POST")) return await onIpn(req, env, ctx);
    } catch (err) {
      console.error("api lỗi", pathname, String(err && err.stack || err));
      return json({ error: "server" }, 500);
    }
    if (pathname.startsWith("/api/")) return json({ error: "not_found" }, 404);
    return env.ASSETS.fetch(req);
  },
  async scheduled(_event, env, ctx) {
    ctx.waitUntil(sweep(env));
  },
};
