/* Worker "cgpluxuryhotel": phục vụ site tĩnh html/ + API thanh toán AsiaPay PayDollar (Client Post).
   Luồng:
     1. POST /api/booking            trang đặt phòng gửi thông tin khách -> lưu đơn "pending" (D1),
                                     tính tiền TỪ BẢNG GIÁ server (packages.json), trả form PayDollar đã ký secureHash
     2. trình duyệt POST form sang payForm.jsp, khách nhập thẻ trên trang PayDollar (3DS)
     3. POST /api/asiapay/datafeed   PayDollar báo kết quả server-to-server (nguồn chính thức, kể cả khi khách
                                     đóng trình duyệt). URL này phải khai báo trong Merchant Admin > Profile > Payment Options
        GET  /api/asiapay/back       successUrl/failUrl/cancelUrl: khách quay về -> hỏi Query API (không tin tham số URL),
                                     chuyển về dat-phong/#kq=<mã>.<token> để hiện kết quả
     4. lần đầu đơn chuyển sang "paid" -> gửi email xác nhận cho khách + email báo khách sạn (đúng 1 lần)
     5. cron 10 phút: đơn pending quá 15 phút -> Query API hỏi PayDollar
   GET /api/booking/status?code=&t=  trang kết quả hỏi trạng thái đơn (token chống dò đơn của người khác). */
import PACKAGES from "./packages.json";
import { payForm, verifyDatafeed, queryOrder, summarize } from "./asiapay.js";
import { sendPaidMails } from "./mail.js";
import SETTINGS from "./settings.json";
import { adminApi } from "./admin.js";

const LANGS = ["vi", "en", "ko", "zh", "ru", "de"];

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const now = () => new Date().toISOString();
const randHex = (n) => Array.from(crypto.getRandomValues(new Uint8Array(n)), (b) => b.toString(16).padStart(2, "0")).join("");
const ymd = (s) => /^\d{4}-\d{2}-\d{2}$/.test(s || "") && !isNaN(Date.parse(s + "T00:00:00Z"));
const addDays = (s, n) => new Date(Date.parse(s + "T00:00:00Z") + n * 864e5).toISOString().slice(0, 10);
const vnToday = () => new Date(Date.now() + 7 * 3600e3).toISOString().slice(0, 10); // ngày hiện tại giờ VN
const clip = (v, n) => String(v == null ? "" : v).trim().slice(0, n);
const bookingPage = (env, lang) => env.SITE_URL + (lang === "vi" ? "" : "/" + lang) + "/dat-phong/";

/* Mã đặt phòng: CGP + 7 ký tự, không có chữ dễ nhầm (0/O, 1/I). Dùng luôn làm orderRef của PayDollar. */
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
    pay_method: "card", // tài khoản AsiaPay 74002484: Visa / Mastercard / JCB
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
  const rate = Number(SETTINGS.usd_vnd_rate); // tỷ giá do CMS quản lý (data/settings.json -> build -> worker/settings.json)
  if (!(rate > 0)) return json({ error: "config" }, 500);
  b.amount_vnd = Math.round((pkg.usd * rate) / 1000) * 1000; // làm tròn nghìn đồng
  b.code = newCode();
  b.view_token = randHex(12);
  b.status = "pending";
  b.created_at = now();

  const cols = Object.keys(b);
  await env.DB.prepare(`INSERT INTO bookings (${cols.join(",")}) VALUES (${cols.map(() => "?").join(",")})`).bind(...cols.map((k) => b[k])).run();

  const back = (r) => env.SITE_URL + "/api/asiapay/back?r=" + r + "&code=" + b.code + "&t=" + b.view_token;
  const form = await payForm(env, { ref: b.code, amount: b.amount_vnd, lang, back });
  return json({ code: b.code, form });
}

/* ---------------------------------------------------------------- 3/4. xử lý kết quả (Datafeed, Query API dùng chung) */
/* r = { state: paid|failed|pending, Ref, PayRef, Amt, Cur, prc, src, payMethod, pan, status }
   Bất biến: đơn đã "paid" không bao giờ bị đổi trạng thái; email chỉ gửi bởi lệnh UPDATE thắng cuộc đua
   (Datafeed và lượt khách quay về có thể tới cùng lúc). Đơn "failed" vẫn lên "paid" được: trên trang PayDollar
   khách có thể thử lại thẻ khác sau lần bị từ chối. */
const byCode = (env, code) => env.DB.prepare("SELECT * FROM bookings WHERE code = ?").bind(code).first();

async function applyResult(env, r, source) {
  const b = r && r.Ref ? await byCode(env, r.Ref) : null;
  if (!b) return { found: false };
  const t = now();
  // Kiểm tra theo tài liệu "Data Feed Validation": đúng đơn, đúng số tiền, đúng loại tiền
  const amountOk = Math.round(Number(r.Amt)) === b.amount_vnd && String(r.Cur) === "704";
  const msg = clip([r.status, "prc=" + r.prc, "src=" + r.src].filter(Boolean).join(" "), 200);

  if (r.state === "paid" && amountOk) {
    const u = await env.DB.prepare(
      "UPDATE bookings SET status='paid', resp_code=?, resp_message=?, txn_no=?, card_type=?, card_num=?, paid_at=?, updated_at=?, paid_via=? WHERE code=? AND status<>'paid'",
    ).bind(clip(r.prc, 10), msg, clip(r.PayRef, 32), clip(r.payMethod, 20), clip(r.pan, 24), t, t, source, b.code).run();
    return { found: true, b: await byCode(env, b.code), justPaid: u.meta.changes === 1 };
  }
  if (r.state === "paid") {
    // Thành công nhưng số tiền/loại tiền không khớp: KHÔNG coi là thành công, để pending cho khách sạn kiểm tra
    console.error(source, "số tiền không khớp", b.code, r.Amt, r.Cur, "!=", b.amount_vnd, "704");
    await env.DB.prepare("UPDATE bookings SET resp_code=?, resp_message=?, updated_at=? WHERE code=? AND status='pending'")
      .bind("AMOUNT_MISMATCH", clip("amount " + r.Amt + " cur " + r.Cur, 200), t, b.code).run();
    return { found: true, b };
  }
  if (r.state === "pending") return { found: true, b };
  await env.DB.prepare("UPDATE bookings SET status='failed', resp_code=?, resp_message=?, updated_at=? WHERE code=? AND status IN ('pending','failed')")
    .bind(clip(r.prc, 10), msg, t, b.code).run();
  return { found: true, b: await byCode(env, b.code) };
}

async function mailIfJustPaid(env, res) {
  if (!res.justPaid) return;
  const ok = await sendPaidMails(env, res.b);
  if (ok) await env.DB.prepare("UPDATE bookings SET email_sent_at=? WHERE code=?").bind(now(), res.b.code).run();
}

/* Datafeed: POST form-urlencoded. successcode 0 = thành công, 1 = thất bại, 2 = đang xử lý.
   AsiaPay yêu cầu trang datafeed LUÔN in "OK" (công cụ "Test Datafeed" trong Merchant Admin gửi dữ liệu mẫu
   KHÔNG có secureHash và báo fail nếu không nhận được "OK"). Chữ ký sai / thiếu -> trả "OK" nhưng KHÔNG cập nhật
   gì (chỉ log). Lỗi khi xử lý đơn thật (DB...) -> trả 500 để PayDollar gửi lại; cron Query API cũng sẽ bù. */
async function onDatafeed(req, env, ctx) {
  const p = Object.fromEntries(new URLSearchParams(await req.text()));
  const plain = (s, status = 200) => new Response(s, { status, headers: { "content-type": "text/plain" } });
  if (!(await verifyDatafeed(env, p))) {
    console.error("datafeed: secureHash sai/thiếu - bỏ qua", p.Ref, p.secureHash ? "có hash" : "không có hash");
    return plain("OK");
  }
  if (p.MerchantId && p.MerchantId !== String(env.ASIAPAY_MERCHANT_ID)) {
    console.error("datafeed: sai merchant", p.Ref, p.MerchantId);
    return plain("OK");
  }
  const sc = String(p.successcode);
  const res = await applyResult(env, {
    state: sc === "0" ? "paid" : sc === "2" ? "pending" : "failed",
    Ref: p.Ref, PayRef: p.PayRef, Amt: p.Amt, Cur: p.Cur, prc: p.prc, src: p.src,
    payMethod: p.payMethod, pan: "", status: "datafeed successcode=" + sc,
  }, "datafeed");
  if (!res.found) console.error("datafeed: không có đơn", p.Ref);
  ctx.waitUntil(mailIfJustPaid(env, res));
  return plain("OK");
}

/* Khách quay về từ PayDollar. Tham số r (ok/fail/cancel) chỉ để tham khảo — trạng thái lấy từ Query API.
   PayDollar có thể nối thêm "?Ref=..." vào URL -> cắt phần sau dấu "?" trong token. */
async function onBack(req, env, ctx) {
  const q = new URL(req.url).searchParams;
  const code = clip(q.get("code"), 20);
  const token = String(q.get("t") || "").split("?")[0];
  let b = code ? await byCode(env, code) : null;
  if (!b || b.view_token !== token) return Response.redirect(env.SITE_URL + "/dat-phong/", 302);
  if (b.status !== "paid") {
    const r = summarize(await queryOrder(env, b.code));
    if (r) {
      const res = await applyResult(env, r, "back");
      if (res.b) b = res.b;
      ctx.waitUntil(mailIfJustPaid(env, res));
    } else if (String(q.get("r")).startsWith("cancel") && b.status === "pending") {
      // Khách bấm huỷ và PayDollar chưa có giao dịch nào cho đơn này
      await env.DB.prepare("UPDATE bookings SET status='failed', resp_code='CANCEL', resp_message='cancelled by guest', updated_at=? WHERE code=? AND status='pending'")
        .bind(now(), b.code).run();
    }
  }
  return Response.redirect(bookingPage(env, b.lang) + "#kq=" + b.code + "." + b.view_token, 302);
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

/* ---------------------------------------------------------------- 5. cron: Query API cho đơn treo */
async function sweep(env) {
  const { results } = await env.DB.prepare(
    "SELECT code, created_at FROM bookings WHERE status='pending' AND created_at < ? AND created_at > ? ORDER BY created_at LIMIT 30",
  ).bind(new Date(Date.now() - 15 * 60e3).toISOString(), new Date(Date.now() - 3 * 864e5).toISOString()).all();
  for (const { code, created_at } of results) {
    const recs = await queryOrder(env, code);
    if (!recs) continue;
    if (!recs.length) {
      // Khách chưa từng thanh toán / bỏ dở trang PayDollar: quá 1 ngày thì đóng đơn
      if (Date.parse(created_at) < Date.now() - 864e5)
        await env.DB.prepare("UPDATE bookings SET status='expired', updated_at=? WHERE code=? AND status='pending'").bind(now(), code).run();
      continue;
    }
    await mailIfJustPaid(env, await applyResult(env, summarize(recs), "query"));
  }
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const { pathname } = url;
    try {
      if (pathname.startsWith("/api/admin/")) return await adminApi(req, env, url);
      if (pathname === "/api/booking" && req.method === "POST") return await createBooking(req, env);
      if (pathname === "/api/booking/status" && req.method === "GET") return await status(req, env);
      if (pathname === "/api/asiapay/datafeed" && req.method === "POST") return await onDatafeed(req, env, ctx);
      if (pathname === "/api/asiapay/back" && req.method === "GET") return await onBack(req, env, ctx);
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
