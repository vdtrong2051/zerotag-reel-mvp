# Demo Script - ZeroTag-Reel MVP

## Mục tiêu demo

Chứng minh ZeroTag-Reel MVP có thể:

- Quản lý hồ sơ số của reel/tray/carton.
- Kiểm tra đúng BOM.
- Cảnh báo sai mã linh kiện.
- Cảnh báo sai lot/date-code.
- Ghi event log.
- Truy xuất lịch sử theo lot/date-code.
- Mô phỏng gateway phần cứng qua HTTP payload.

## Kịch bản demo

### Bước 1: Mở Overview

Hiển thị tổng quan số lượng reel, số event, số cảnh báo.

### Bước 2: Mở Component Inventory

Xem danh sách linh kiện mẫu.

### Bước 3: Mở Digital Passport

Chọn ZT-R1001 để xem hồ sơ số.

### Bước 4: BOM Matching đúng

Scan ZT-R1001 với BOM PCB-DEMO-01.

Kết quả: VALID.

### Bước 5: BOM Matching sai mã

Scan ZT-R1005 với BOM PCB-DEMO-01.

Kết quả: WRONG_PART.

### Bước 6: BOM Matching sai lot

Scan ZT-R1008 với BOM PCB-DEMO-01.

Kết quả: LOT_MISMATCH.

### Bước 7: Xem Event Log

Kiểm tra các event vừa phát sinh.

### Bước 8: Traceability

Tìm theo lot L2026A01.

### Bước 9: Verification

Kiểm tra case ZT-R1015 để demo QR/RFID mismatch.

### Bước 10: Gateway Simulator

Chạy gateway simulator gửi payload trực tiếp về backend.
