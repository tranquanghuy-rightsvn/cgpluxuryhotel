/* AsiaPay PayDollar PayGate — "Client Post Through Browser" (https://developer.asiapay.com/integration-guide).
   Luồng:
     - Trình duyệt khách POST form (merchantId, orderRef, amount, currCode, ..., secureHash) sang payForm.jsp
     - PayDollar gửi Datafeed (POST form, server-to-server) tới URL khai báo trong Merchant Admin
       > Profile > Payment Options. Trang datafeed phải in ra "OK".
     - successUrl / failUrl / cancelUrl chỉ để HIỂN THỊ (tài liệu: "DO NOT use this URL to update your system").
       Khi khách quay về, server hỏi lại trạng thái bằng Merchant API (orderApi.jsp, actionType=Query).
   Secure hash (mục "Manual Secure Hashing"):
     - gửi đi:  SHA1( merchantId|orderRef|currCode|amount|payType|secret )
     - datafeed: SHA1( src|prc|successcode|Ref|PayRef|Cur|Amt|payerAuth|secret )
     SHA-1 là mặc định; tài khoản đặt SHA-256 thì đổi biến ASIAPAY_HASH_ALGO. Kết quả hex chữ thường
     (ví dụ trong tài liệu: 56100908|1280204670187|344|10|N|gMAVIEGVpqHvxoNEqbrZRuBDFT1B0icW
      -> 13068c0ef09139ea711d36bde16785a2d30b9a30). */

const enc = new TextEncoder();

const base = (env) => (env.ASIAPAY_BASE_URL || "https://test.paydollar.com/b2cDemo").replace(/\/$/, "");
export const CURRENCY = { VND: "704", USD: "840" };
/* Ngôn ngữ trang thanh toán (tham số lang). PayDollar không có tiếng Hàn -> tiếng Anh. */
const LANG = { vi: "V", en: "E", ko: "E", zh: "X", ru: "R", de: "G" };

async function digest(env, s) {
  const algo = String(env.ASIAPAY_HASH_ALGO || "SHA-1").toUpperCase() === "SHA-256" ? "SHA-256" : "SHA-1";
  const buf = new Uint8Array(await crypto.subtle.digest(algo, enc.encode(s)));
  return Array.from(buf, (b) => b.toString(16).padStart(2, "0")).join("");
}

function sameText(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export function requestHash(env, f) {
  return digest(env, [f.merchantId, f.orderRef, f.currCode, f.amount, f.payType, env.ASIAPAY_SECURE_HASH_SECRET].join("|"));
}

/* Datafeed: secureHash có thể chứa nhiều giá trị cách nhau dấu phẩy (giai đoạn đổi secret) -> khớp 1 cái là được. */
export async function verifyDatafeed(env, p) {
  const want = await digest(env, [p.src, p.prc, p.successcode, p.Ref, p.PayRef, p.Cur, p.Amt, p.payerAuth, env.ASIAPAY_SECURE_HASH_SECRET].map((v) => v ?? "").join("|"));
  return String(p.secureHash || "").split(",").some((h) => sameText(h.trim().toLowerCase(), want));
}

/* Các trường form POST sang trang thanh toán PayDollar */
export async function payForm(env, { ref, amount, lang, back }) {
  const f = {
    merchantId: env.ASIAPAY_MERCHANT_ID,
    orderRef: ref, // ≤ 35 ký tự
    currCode: CURRENCY[env.ASIAPAY_CURRENCY || "VND"],
    amount: String(amount), // VND: số nguyên, không phần thập phân
    payType: "N", // Normal Payment (Sale)
    payMethod: env.ASIAPAY_PAY_METHOD || "CC",
    lang: LANG[lang] || "E",
    mpsMode: "NIL",
    successUrl: back("ok"),
    failUrl: back("fail"),
    cancelUrl: back("cancel"),
    redirect: "3", // tự quay về site sau 3 giây ở trang kết quả PayDollar
  };
  f.secureHash = await requestHash(env, f);
  return { action: base(env) + "/eng/payment/payForm.jsp", fields: f };
}

/* Merchant API "Query": trả về mảng record (có thể nhiều record cho 1 orderRef nếu khách thử lại thẻ),
   [] nếu chưa có giao dịch, null nếu lỗi mạng / đăng nhập API sai. */
export async function queryOrder(env, ref) {
  const body = new URLSearchParams({
    merchantId: env.ASIAPAY_MERCHANT_ID,
    loginId: env.ASIAPAY_API_LOGIN,
    password: env.ASIAPAY_API_PASSWORD,
    actionType: "Query",
    orderRef: ref,
  });
  try {
    const r = await fetch(base(env) + "/eng/merchant/api/orderApi.jsp", {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded", "user-agent": "Mozilla/5.0 (compatible; CGPLuxuryHotel-Booking/1.0; +https://cgpgrouphotel.com)", accept: "text/xml,application/xml,*/*" },
      body: body.toString(),
    });
    const xml = await r.text();
    if (!r.ok || !/<records\b/i.test(xml)) {
      console.error("asiapay query: phản hồi lạ", ref, r.status, xml.slice(0, 300));
      return null;
    }
    return [...xml.matchAll(/<record>([\s\S]*?)<\/record>/g)].map(([, rec]) => {
      const o = {};
      for (const [, k, v] of rec.matchAll(/<(\w+)>([^<]*)<\/\1>/g)) o[k] = v.trim();
      return o;
    });
  } catch (err) {
    console.error("asiapay query: lỗi gọi API", ref, String(err));
    return null;
  }
}

const PAID = ["Accepted", "Authorized", "Captured", "Capturing", "Accepted_Adj"];
const PENDING = ["Pending", "Pending_feedback", "Pending_3D"];

/* Gộp các record Query thành 1 kết quả cùng dạng với datafeed để index.js xử lý chung. */
export function summarize(records) {
  if (!records || !records.length) return null;
  const paid = records.find((r) => PAID.includes(r.orderStatus));
  const r = paid || records.find((x) => PENDING.includes(x.orderStatus)) || records[records.length - 1];
  return {
    state: paid ? "paid" : PENDING.includes(r.orderStatus) ? "pending" : "failed",
    Ref: r.ref, PayRef: r.payRef, Amt: r.amt, Cur: r.cur, prc: r.prc, src: r.src,
    payMethod: r.payMethod, pan: r.panMasked || (r.panLast4 ? "****" + r.panLast4 : ""), status: r.orderStatus,
  };
}
