-- Theo dõi xử lý đơn trong trang quản trị GAS (GAS.md mục V): đánh dấu đã xử lý + ghi chú nội bộ.
ALTER TABLE bookings ADD COLUMN handled     INTEGER NOT NULL DEFAULT 0;
ALTER TABLE bookings ADD COLUMN handled_by  TEXT;     -- email người đánh dấu / ghi chú gần nhất
ALTER TABLE bookings ADD COLUMN handled_at  TEXT;
ALTER TABLE bookings ADD COLUMN staff_note  TEXT;
CREATE INDEX bookings_created ON bookings (created_at);
