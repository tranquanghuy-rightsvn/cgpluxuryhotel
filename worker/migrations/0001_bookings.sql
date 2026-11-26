-- Đơn đặt phòng + trạng thái thanh toán AsiaPay PayDollar. code = orderRef gửi PayDollar.
-- status: pending (chờ thanh toán) | paid | failed (khách huỷ / ngân hàng từ chối) | expired (bỏ dở > 1 ngày)
CREATE TABLE bookings (
  code          TEXT PRIMARY KEY,
  view_token    TEXT NOT NULL,          -- cho trang kết quả xem đơn, chống dò mã đơn
  status        TEXT NOT NULL DEFAULT 'pending',
  pkg           TEXT NOT NULL,
  checkin       TEXT NOT NULL,
  checkout      TEXT NOT NULL,
  adults        INTEGER NOT NULL,
  children      INTEGER NOT NULL DEFAULT 0,
  first_name    TEXT NOT NULL,
  last_name     TEXT NOT NULL,
  phone         TEXT NOT NULL,
  email         TEXT NOT NULL,
  country       TEXT,
  note          TEXT,
  promo         TEXT,
  newsletter    INTEGER NOT NULL DEFAULT 0,
  pay_method    TEXT,                   -- card (Visa / Mastercard / JCB)
  lang          TEXT NOT NULL,
  amount_usd    INTEGER NOT NULL,
  amount_vnd    INTEGER NOT NULL,       -- số tiền gửi PayDollar (VND, số nguyên)
  resp_code     TEXT,                   -- prc (mã phản hồi chính) gần nhất
  resp_message  TEXT,
  txn_no        TEXT,                   -- PayRef (mã giao dịch PayDollar)
  card_type     TEXT,
  card_num      TEXT,                   -- dạng che 491891******5005 (từ Query API)
  paid_via      TEXT,                   -- datafeed | back | query
  created_at    TEXT NOT NULL,
  updated_at    TEXT,
  paid_at       TEXT,
  email_sent_at TEXT
);
CREATE INDEX bookings_status_created ON bookings (status, created_at);
