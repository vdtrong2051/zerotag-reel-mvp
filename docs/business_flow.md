# Business Flow - ZeroTag-Reel MVP

## Flow 1: Nhập kho

1. Người vận hành chọn mode INBOUND.
2. Dashboard hoặc Gateway gửi ZeroTag ID về backend.
3. Backend kiểm tra ZeroTag ID có trong hệ thống hay không.
4. Nếu có, cập nhật trạng thái IN_STOCK.
5. Ghi event WAREHOUSE_IN.
6. Trả kết quả OK về dashboard/gateway.

## Flow 2: Kiểm tra đúng BOM

1. Người vận hành chọn BOM cần kiểm tra.
2. Dashboard hoặc Gateway scan ZeroTag ID.
3. Backend tra hồ sơ linh kiện theo ZeroTag ID.
4. Backend so sánh part number với BOM.
5. Backend so sánh lot/date-code nếu part number đúng.
6. Trả kết quả VALID, WRONG_PART, LOT_MISMATCH hoặc DATECODE_MISMATCH.
7. Ghi scan transaction và event log.

## Flow 3: Sai mã linh kiện

1. ZeroTag ID tồn tại.
2. Part number của reel không nằm trong BOM đang chọn.
3. Backend trả WRONG_PART.
4. Dashboard hiển thị cảnh báo sai linh kiện.
5. Gateway nhận action RED + LONG_BEEP.

## Flow 4: Đúng mã nhưng sai lot/date-code

1. ZeroTag ID tồn tại.
2. Part number đúng với BOM.
3. Lot hoặc date-code không phù hợp yêu cầu.
4. Backend trả LOT_MISMATCH hoặc DATECODE_MISMATCH.
5. Dashboard hiển thị cảnh báo.
6. Gateway nhận action RED hoặc YELLOW.

## Flow 5: Tag lạ

1. Backend không tìm thấy ZeroTag ID.
2. Backend trả UNKNOWN_TAG.
3. Ghi event UNKNOWN_TAG.
4. Dashboard/Gateway cảnh báo.

## Flow 6: MSL Tracking

1. Backend đọc thông tin MSL của linh kiện.
2. Tính floor life used so với floor life limit.
3. Trả NORMAL, WARNING hoặc NEED_BAKE.

## Flow 7: Verification / Anti-tamper

1. Backend nhận QR ID và RFID ID.
2. So sánh hai ID.
3. Nếu khớp, trả VERIFIED.
4. Nếu không khớp, trả QR_RFID_MISMATCH hoặc TAMPER_WARNING.
