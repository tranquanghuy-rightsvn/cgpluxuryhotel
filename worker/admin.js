/* API cho trang quản trị GAS (GAS.md mục V). Chỉ GAS gọi (server-to-server), xác thực bằng header
   x-admin-key = Worker secret ADMIN_API_KEY. Quyền admin/editor do GAS kiểm tra trước khi gọi.
     GET  /api/admin/bookings?status=&handled=&q=&page=   danh sách, 50 đơn/trang, mới nhất trước
     POST /api/admin/bookings/<code>   {handled?: bool, note?: string, by: email}   */
const PAGE = 50;
const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const STATUSES = ["pending", "paid", "failed", "expired"];

async function authorized(req, env) {
  const want = env.ADMIN_API_KEY || "";
  const got = req.headers.get("x-admin-key") || "";
  if (want.length < 24) return false; // chưa cấu hình secret -> đóng hẳn API
  const enc = new TextEncoder();
  const [a, b] = await Promise.all([got, want].map((s) => crypto.subtle.digest("SHA-256", enc.encode(s))));
  const x = new Uint8Array(a), y = new Uint8Array(b);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

async function list(url, env) {
  const q = url.searchParams;
  const where = [], args = [];
  if (STATUSES.includes(q.get("status"))) { where.push("status = ?"); args.push(q.get("status")); }
  if (q.get("handled") === "1" || q.get("handled") === "0") { where.push("handled = ?"); args.push(+q.get("handled")); }
  const s = String(q.get("q") || "").trim().slice(0, 60);
  if (s) {
    where.push("(code LIKE ? OR email LIKE ? OR phone LIKE ? OR (first_name || ' ' || last_name) LIKE ? OR (last_name || ' ' || first_name) LIKE ?)");
    for (let i = 0; i < 5; i++) args.push("%" + s + "%");
  }
  const w = where.length ? " WHERE " + where.join(" AND ") : "";
  const page = Math.max(1, parseInt(q.get("page"), 10) || 1);
  const total = (await env.DB.prepare("SELECT COUNT(*) AS n FROM bookings" + w).bind(...args).first()).n;
  const { results } = await env.DB.prepare(
    "SELECT code, status, pkg, checkin, checkout, adults, children, first_name, last_name, phone, email, country, note, promo, newsletter," +
      " lang, amount_usd, amount_vnd, resp_code, resp_message, txn_no, card_type, card_num, paid_via, created_at, updated_at, paid_at," +
      " email_sent_at, handled, handled_by, handled_at, staff_note FROM bookings" + w + " ORDER BY created_at DESC LIMIT ? OFFSET ?",
  ).bind(...args, PAGE, (page - 1) * PAGE).all();
  return json({ total, page, pageSize: PAGE, bookings: results });
}

async function update(code, req, env) {
  let d;
  try { d = await req.json(); } catch { return json({ error: "bad_json" }, 400); }
  const b = await env.DB.prepare("SELECT code FROM bookings WHERE code = ?").bind(code).first();
  if (!b) return json({ error: "not_found" }, 404);
  const sets = [], args = [];
  if (typeof d.handled === "boolean") { sets.push("handled = ?"); args.push(d.handled ? 1 : 0); }
  if (typeof d.note === "string") { sets.push("staff_note = ?"); args.push(d.note.trim().slice(0, 2000)); }
  if (!sets.length) return json({ error: "nothing" }, 400);
  sets.push("handled_by = ?", "handled_at = ?");
  args.push(String(d.by || "").slice(0, 120), new Date().toISOString());
  await env.DB.prepare("UPDATE bookings SET " + sets.join(", ") + " WHERE code = ?").bind(...args, code).run();
  return json({ ok: true, booking: await env.DB.prepare("SELECT code, handled, handled_by, handled_at, staff_note FROM bookings WHERE code = ?").bind(code).first() });
}

export async function adminApi(req, env, url) {
  if (!(await authorized(req, env))) return json({ error: "unauthorized" }, 401);
  if (url.pathname === "/api/admin/bookings" && req.method === "GET") return list(url, env);
  const m = /^\/api\/admin\/bookings\/([A-Z0-9]{4,20})$/.exec(url.pathname);
  if (m && req.method === "POST") return update(m[1], req, env);
  return json({ error: "not_found" }, 404);
}
