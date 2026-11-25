/* OnePay paygate (tài liệu HD01-KT-TS, lần ban hành 02 — bản PDF trong thư mục dự án).
   Chữ ký vpc_SecureHash (mục II-4.4):
     - lấy mọi tham số bắt đầu bằng "vpc_" hoặc "user_" (bỏ vpc_SecureHash / vpc_SecureHashType, bỏ giá trị rỗng)
     - sắp xếp key theo alphabet (phân biệt hoa thường), nối "key=value&key=value" bằng GIÁ TRỊ GỐC (không encode)
     - HMAC-SHA256 với HashCode đã GIẢI MÃ HEX làm khóa, kết quả hex VIẾT HOA.
   Đã thử trên sandbox 25/11/2026: khóa dạng chuỗi -> INVALID_INVOICE, khóa giải mã hex -> vào trang thanh toán.
   (Ví dụ C400B076… in trong tài liệu không khớp cách nào — đừng dùng nó để kiểm tra.) */

const enc = new TextEncoder();
const hexToBytes = (hex) => new Uint8Array(hex.match(/../g).map((b) => parseInt(b, 16)));

export function rawData(params) {
  return Object.keys(params)
    .filter((k) => (k.startsWith("vpc_") || k.startsWith("user_")) && k !== "vpc_SecureHash" && k !== "vpc_SecureHashType")
    .filter((k) => params[k] !== undefined && params[k] !== null && String(params[k]) !== "")
    .sort()
    .map((k) => k + "=" + params[k])
    .join("&");
}

export async function sign(params, hashCode) {
  const key = await crypto.subtle.importKey("raw", hexToBytes(hashCode), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = new Uint8Array(await crypto.subtle.sign("HMAC", key, enc.encode(rawData(params))));
  return Array.from(mac, (b) => b.toString(16).padStart(2, "0")).join("").toUpperCase();
}

/* So sánh thời gian hằng để không lộ chữ ký qua thời gian phản hồi */
export async function verify(params, hashCode) {
  const got = String(params.vpc_SecureHash || "").toUpperCase();
  const want = await sign(params, hashCode);
  if (got.length !== want.length) return false;
  let diff = 0;
  for (let i = 0; i < want.length; i++) diff |= got.charCodeAt(i) ^ want.charCodeAt(i);
  return diff === 0;
}

const base = (env) => (env.ONEPAY_BASE_URL || "https://mtf.onepay.vn").replace(/\/$/, "");

/* Tạo URL chuyển khách sang trang thanh toán OnePay (mục II-4.2, phương thức GET) */
export async function payUrl(env, { ref, orderInfo, amountVnd, ip, locale, cardList }) {
  const p = {
    vpc_Version: "2",
    vpc_Currency: env.ONEPAY_CURRENCY || "VND",
    vpc_Command: "pay",
    vpc_AccessCode: env.ONEPAY_ACCESS_CODE,
    vpc_Merchant: env.ONEPAY_MERCHANT,
    vpc_Locale: locale === "vn" ? "vn" : "en",
    vpc_ReturnURL: env.SITE_URL + "/api/onepay/return",
    vpc_CallbackURL: env.SITE_URL + "/api/onepay/ipn",
    vpc_MerchTxnRef: ref,
    vpc_OrderInfo: orderInfo,
    vpc_Amount: String(amountVnd * 100), // OnePay bắt nhân 100 kể cả VND
    vpc_TicketNo: ip,
  };
  if (cardList) p.vpc_CardList = cardList;
  p.vpc_SecureHash = await sign(p, env.ONEPAY_HASH_CODE);
  return base(env) + "/paygate/vpcpay.op?" + new URLSearchParams(p).toString();
}

/* QueryDR (mục II-5): hỏi trạng thái giao dịch khi chưa nhận được ReturnURL/IPN.
   Trả về object tham số đã xác thực chữ ký, hoặc null nếu lỗi mạng / chữ ký sai. */
export async function queryDR(env, ref) {
  const p = {
    vpc_Command: "queryDR",
    vpc_Version: "2",
    vpc_MerchTxnRef: ref,
    vpc_Merchant: env.ONEPAY_MERCHANT,
    vpc_AccessCode: env.ONEPAY_ACCESS_CODE,
    vpc_User: env.ONEPAY_USER,
    vpc_Password: env.ONEPAY_PASSWORD,
  };
  p.vpc_SecureHash = await sign(p, env.ONEPAY_HASH_CODE);
  try {
    const r = await fetch(base(env) + "/msp/api/v1/vpc/invoices/queries", {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(p).toString(),
    });
    const res = Object.fromEntries(new URLSearchParams(await r.text()));
    if (!(await verify(res, env.ONEPAY_HASH_CODE))) {
      console.error("queryDR: chữ ký phản hồi sai", ref);
      return null;
    }
    return res;
  } catch (err) {
    console.error("queryDR: lỗi gọi API", ref, String(err));
    return null;
  }
}
