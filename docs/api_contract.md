# API Contract — ZeroTag-Reel MVP

## 1. Mục tiêu

API của ZeroTag-Reel MVP là giao diện thống nhất giữa:

* Dashboard Streamlit
* Gateway Simulator
* QR Scanner
* ZeroGateway dùng ESP32/NFC/RFID/UHF trong tương lai

Mọi nguồn scan đều sử dụng cùng endpoint:

```http
POST /api/v1/scans
```

Dashboard và Gateway chỉ gửi dữ liệu đầu vào, sau đó hiển thị hoặc thực thi kết quả do Backend trả về.

Dashboard và Gateway không tự xử lý:

* BOM Matching
* Lot/date-code checking
* Verification
* Thay đổi trạng thái component
* Event Logging

---

# 2. Quy ước chung

## 2.1. Base URL

Môi trường local:

```text
http://127.0.0.1:8000
```

API prefix:

```text
/api/v1
```

Ví dụ:

```text
http://127.0.0.1:8000/api/v1/scans
```

---

## 2.2. Content type

Request và response sử dụng:

```http
Content-Type: application/json
```

Encoding:

```text
UTF-8
```

---

## 2.3. Quy ước đặt tên field

API sử dụng `snake_case`.

Ví dụ:

```text
zerotag_id
gateway_id
bom_code
bom_ref
transaction_id
processed_at
```

---

## 2.4. Định dạng thời gian

Thời gian sử dụng ISO 8601 kèm timezone.

Ví dụ:

```text
2026-06-06T09:30:00+07:00
```

---

## 2.5. Kết quả nghiệp vụ và HTTP status

Các kết quả như:

```text
WRONG_PART
LOT_MISMATCH
UNKNOWN_TAG
BLOCKED_TAG
```

là kết quả nghiệp vụ, không phải lỗi kỹ thuật của HTTP.

Vì vậy, nếu backend đã nhận và xử lý request thành công, API vẫn trả:

```http
200 OK
```

HTTP lỗi chỉ dùng cho trường hợp request sai cấu trúc, tài nguyên cấu hình không tồn tại hoặc backend gặp lỗi.

---

# 3. Các mã nhận diện

## 3.1. `zerotag_id`

Mã nghiệp vụ của ZeroTag.

Ví dụ:

```text
ZT-R1001
```

Mã này liên kết vật thể thật với Digital Component Passport.

---

## 3.2. `tag_uid`

UID hoặc EPC vật lý của NFC/RFID/UHF tag.

Ví dụ:

```text
UID-R1001
```

`tag_uid` được dùng để ánh xạ về một component đã đăng ký.

---

## 3.3. `qr_id`

ZeroTag ID được đọc từ QR hoặc DataMatrix.

Ví dụ:

```text
ZT-R1001
```

---

## 3.4. `rfid_id`

ZeroTag ID được lưu trong payload RFID hoặc được Gateway ánh xạ từ RFID.

Ví dụ:

```text
ZT-R1001
```

`rfid_id` khác với `tag_uid`.

```text
rfid_id
→ mã nghiệp vụ đọc từ dữ liệu RFID

tag_uid
→ UID/EPC vật lý của tag
```

---

# 4. Endpoint scan thống nhất

```http
POST /api/v1/scans
```

Endpoint này xử lý bốn scan mode:

```text
INBOUND
BOM_CHECK
RETURN
VERIFY
```

---

# 5. Scan request schema

## 5.1. Request đầy đủ

```json
{
  "request_id": "REQ-20260606-0001",
  "gateway_id": "ZG-001",
  "mode": "BOM_CHECK",
  "location": "SMT Issue Station 01",
  "zerotag_id": "ZT-R1001",
  "tag_uid": "UID-R1001",
  "qr_id": null,
  "rfid_id": null,
  "bom_code": "PCB-DEMO-01",
  "bom_ref": "R12",
  "read_at": "2026-06-06T09:30:00+07:00"
}
```

---

## 5.2. Mô tả field

| Field        | Kiểu        | Bắt buộc chung | Mô tả                                         |
| ------------ | ----------- | -------------: | --------------------------------------------- |
| `request_id` | string      |             Có | Mã duy nhất cho request, dùng chống gửi trùng |
| `gateway_id` | string      |             Có | Gateway gửi scan                              |
| `mode`       | string      |             Có | `INBOUND`, `BOM_CHECK`, `RETURN`, `VERIFY`    |
| `location`   | string      |             Có | Vị trí scan                                   |
| `zerotag_id` | string/null |   Có điều kiện | ZeroTag ID do client cung cấp                 |
| `tag_uid`    | string/null |   Có điều kiện | UID/EPC vật lý                                |
| `qr_id`      | string/null |   Có điều kiện | ZeroTag ID đọc từ QR                          |
| `rfid_id`    | string/null |   Có điều kiện | ZeroTag ID đọc/ánh xạ từ RFID                 |
| `bom_code`   | string/null |   Có điều kiện | Mã BOM                                        |
| `bom_ref`    | string/null |   Có điều kiện | Dòng BOM cụ thể                               |
| `read_at`    | datetime    |             Có | Thời điểm Gateway đọc tag                     |

---

## 5.3. Quy tắc nhận diện

Đối với `INBOUND`, `BOM_CHECK` và `RETURN`, request phải có ít nhất một trong hai field:

```text
zerotag_id
tag_uid
```

Gateway Simulator nên gửi cả hai để hỗ trợ demo và đối chiếu.

Đối với `VERIFY`, request phải có:

```text
qr_id
rfid_id
```

`tag_uid` được khuyến nghị gửi thêm để kiểm tra UID vật lý đã đăng ký.

---

# 6. Field bắt buộc theo scan mode

| Field                       |  INBOUND | BOM_CHECK |   RETURN |         VERIFY |
| --------------------------- | -------: | --------: | -------: | -------------: |
| `request_id`                |       Có |        Có |       Có |             Có |
| `gateway_id`                |       Có |        Có |       Có |             Có |
| `mode`                      |       Có |        Có |       Có |             Có |
| `location`                  |       Có |        Có |       Có |             Có |
| `read_at`                   |       Có |        Có |       Có |             Có |
| `zerotag_id` hoặc `tag_uid` |       Có |        Có |       Có | Không bắt buộc |
| `bom_code`                  |    Không |        Có |    Không |          Không |
| `bom_ref`                   |    Không |        Có |    Không |          Không |
| `qr_id`                     |    Không |     Không |    Không |             Có |
| `rfid_id`                   |    Không |     Không |    Không |             Có |
| `tag_uid`                   | Tùy chọn |  Tùy chọn | Tùy chọn |    Khuyến nghị |

Field không sử dụng trong một mode phải được gửi dưới dạng `null` hoặc bỏ khỏi payload.

---

# 7. Request theo từng mode

## 7.1. INBOUND

```json
{
  "request_id": "REQ-IN-0001",
  "gateway_id": "ZG-002",
  "mode": "INBOUND",
  "location": "Warehouse Inbound Gate",
  "zerotag_id": "ZT-R1001",
  "tag_uid": "UID-R1001",
  "read_at": "2026-06-06T09:00:00+07:00"
}
```

Nghiệp vụ:

```text
REGISTERED → IN_STOCK
```

---

## 7.2. BOM_CHECK

```json
{
  "request_id": "REQ-BOM-0001",
  "gateway_id": "ZG-001",
  "mode": "BOM_CHECK",
  "location": "SMT Issue Station 01",
  "zerotag_id": "ZT-R1001",
  "tag_uid": "UID-R1001",
  "bom_code": "PCB-DEMO-01",
  "bom_ref": "R12",
  "read_at": "2026-06-06T09:30:00+07:00"
}
```

BOM_CHECK luôn xác định một dòng BOM bằng:

```text
bom_code + bom_ref
```

---

## 7.3. RETURN

```json
{
  "request_id": "REQ-RETURN-0001",
  "gateway_id": "ZG-002",
  "mode": "RETURN",
  "location": "Warehouse Return Gate",
  "zerotag_id": "ZT-R1001",
  "tag_uid": "UID-R1001",
  "read_at": "2026-06-06T16:00:00+07:00"
}
```

Nghiệp vụ:

```text
ISSUED → IN_STOCK
```

---

## 7.4. VERIFY

```json
{
  "request_id": "REQ-VERIFY-0001",
  "gateway_id": "ZG-001",
  "mode": "VERIFY",
  "location": "Verification Station 01",
  "zerotag_id": "ZT-R1015",
  "tag_uid": "UID-R9915",
  "qr_id": "ZT-R1015",
  "rfid_id": "ZT-R9915",
  "read_at": "2026-06-06T10:00:00+07:00"
}
```

---

# 8. Chống gửi request trùng

`request_id` phải là duy nhất.

## 8.1. Gửi lại cùng request

Nếu Gateway retry cùng `request_id` và cùng payload:

* Backend không tạo thêm ScanTransaction.
* Backend không tạo Event trùng.
* Backend trả lại kết quả đã xử lý trước đó.
* Response có:

```json
{
  "replayed": true
}
```

HTTP status:

```http
200 OK
```

## 8.2. Trùng request ID nhưng payload khác

Nếu cùng `request_id` nhưng payload khác:

```http
409 Conflict
```

Error code:

```text
REQUEST_ID_CONFLICT
```

---

# 9. Response envelope chung

Mọi scan response sử dụng cấu trúc:

```json
{
  "request_id": "REQ-BOM-0001",
  "transaction_id": "TX-000001",
  "mode": "BOM_CHECK",
  "status": "VALID",
  "message": "Component matches the selected BOM item",
  "violations": [],
  "component": {
    "zerotag_id": "ZT-R1001",
    "part_number": "RES-10K-0603",
    "lot_number": "L2026A01",
    "date_code": "2520",
    "quantity_current": 5000,
    "status_before": "IN_STOCK",
    "status_after": "IN_STOCK",
    "location": "Warehouse A1"
  },
  "bom_check": {
    "bom_code": "PCB-DEMO-01",
    "bom_ref": "R12",
    "required_part_number": "RES-10K-0603",
    "required_lot": "L2026A01",
    "allowed_date_code_from": "2520",
    "allowed_date_code_to": "2540",
    "required_quantity": 100,
    "quantity_sufficient": true
  },
  "gateway_action": {
    "led": "GREEN",
    "buzzer": "SHORT_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:30:01+07:00"
}
```

---

# 10. Mô tả response field

| Field            | Kiểu        | Mô tả                                    |
| ---------------- | ----------- | ---------------------------------------- |
| `request_id`     | string      | Request ID từ client                     |
| `transaction_id` | string      | Mã ScanTransaction                       |
| `mode`           | string      | Scan mode                                |
| `status`         | string      | Kết quả nghiệp vụ chính                  |
| `message`        | string      | Thông báo cho người dùng                 |
| `violations`     | array       | Danh sách lỗi chi tiết                   |
| `component`      | object/null | Snapshot component                       |
| `bom_check`      | object/null | Chi tiết BOM check                       |
| `gateway_action` | object      | LED và buzzer                            |
| `replayed`       | boolean     | Request có phải kết quả replay hay không |
| `processed_at`   | datetime    | Thời điểm backend xử lý xong             |

---

# 11. Scan result

MVP sử dụng đúng tám scan result:

```text
VALID
WRONG_PART
LOT_MISMATCH
DATECODE_MISMATCH
UNKNOWN_TAG
BLOCKED_TAG
QR_RFID_MISMATCH
TAMPER_WARNING
```

Không sử dụng:

```text
LOT_AND_DATECODE_MISMATCH
```

Nếu có nhiều lỗi, `status` lưu lỗi chính và `violations` lưu toàn bộ lỗi.

---

# 12. Thứ tự ưu tiên scan result

Backend xác định `status` chính theo thứ tự:

```text
UNKNOWN_TAG
→ BLOCKED_TAG
→ QR_RFID_MISMATCH
→ TAMPER_WARNING
→ WRONG_PART
→ LOT_MISMATCH
→ DATECODE_MISMATCH
→ VALID
```

Ví dụ reel sai cả lot và date-code:

```json
{
  "status": "LOT_MISMATCH",
  "violations": [
    "LOT_MISMATCH",
    "DATECODE_MISMATCH"
  ]
}
```

---

# 13. Gateway action mapping

| Scan result         | LED      | Buzzer        |
| ------------------- | -------- | ------------- |
| `VALID`             | `GREEN`  | `SHORT_BEEP`  |
| `WRONG_PART`        | `RED`    | `LONG_BEEP`   |
| `LOT_MISMATCH`      | `YELLOW` | `DOUBLE_BEEP` |
| `DATECODE_MISMATCH` | `YELLOW` | `DOUBLE_BEEP` |
| `UNKNOWN_TAG`       | `RED`    | `LONG_BEEP`   |
| `BLOCKED_TAG`       | `RED`    | `LONG_BEEP`   |
| `QR_RFID_MISMATCH`  | `RED`    | `LONG_BEEP`   |
| `TAMPER_WARNING`    | `RED`    | `LONG_BEEP`   |

Các giá trị LED:

```text
OFF
GREEN
YELLOW
RED
```

Các giá trị buzzer:

```text
NONE
SHORT_BEEP
DOUBLE_BEEP
LONG_BEEP
```

---

# 14. Response hợp lệ

## 14.1. VALID — BOM đúng

```json
{
  "request_id": "REQ-BOM-0001",
  "transaction_id": "TX-000001",
  "mode": "BOM_CHECK",
  "status": "VALID",
  "message": "Correct part number, lot and date-code",
  "violations": [],
  "component": {
    "zerotag_id": "ZT-R1001",
    "part_number": "RES-10K-0603",
    "lot_number": "L2026A01",
    "date_code": "2520",
    "quantity_current": 5000,
    "status_before": "IN_STOCK",
    "status_after": "IN_STOCK",
    "location": "Warehouse A1"
  },
  "bom_check": {
    "bom_code": "PCB-DEMO-01",
    "bom_ref": "R12",
    "required_part_number": "RES-10K-0603",
    "required_lot": "L2026A01",
    "allowed_date_code_from": "2520",
    "allowed_date_code_to": "2540",
    "required_quantity": 100,
    "quantity_sufficient": true
  },
  "gateway_action": {
    "led": "GREEN",
    "buzzer": "SHORT_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:30:01+07:00"
}
```

---

# 15. Response sai part number

```json
{
  "request_id": "REQ-BOM-0002",
  "transaction_id": "TX-000002",
  "mode": "BOM_CHECK",
  "status": "WRONG_PART",
  "message": "Scanned component does not match the selected BOM item",
  "violations": [
    "WRONG_PART"
  ],
  "component": {
    "zerotag_id": "ZT-R1005",
    "part_number": "CAP-10UF-0805",
    "lot_number": "L2025X09",
    "date_code": "2519",
    "quantity_current": 3000,
    "status_before": "IN_STOCK",
    "status_after": "IN_STOCK",
    "location": "Warehouse B2"
  },
  "bom_check": {
    "bom_code": "PCB-DEMO-01",
    "bom_ref": "R12",
    "required_part_number": "RES-10K-0603",
    "actual_part_number": "CAP-10UF-0805"
  },
  "gateway_action": {
    "led": "RED",
    "buzzer": "LONG_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:31:01+07:00"
}
```

---

# 16. Response sai lot

```json
{
  "request_id": "REQ-BOM-0003",
  "transaction_id": "TX-000003",
  "mode": "BOM_CHECK",
  "status": "LOT_MISMATCH",
  "message": "Correct part number but lot is not allowed",
  "violations": [
    "LOT_MISMATCH"
  ],
  "component": {
    "zerotag_id": "ZT-R1008",
    "part_number": "RES-10K-0603",
    "lot_number": "L2025X09",
    "date_code": "2520",
    "quantity_current": 5000,
    "status_before": "IN_STOCK",
    "status_after": "IN_STOCK",
    "location": "Warehouse A1"
  },
  "bom_check": {
    "bom_code": "PCB-DEMO-01",
    "bom_ref": "R12",
    "required_part_number": "RES-10K-0603",
    "required_lot": "L2026A01",
    "actual_lot": "L2025X09"
  },
  "gateway_action": {
    "led": "YELLOW",
    "buzzer": "DOUBLE_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:32:01+07:00"
}
```

---

# 17. Response sai date-code

```json
{
  "request_id": "REQ-BOM-0004",
  "transaction_id": "TX-000004",
  "mode": "BOM_CHECK",
  "status": "DATECODE_MISMATCH",
  "message": "Date-code is outside the allowed range",
  "violations": [
    "DATECODE_MISMATCH"
  ],
  "component": {
    "zerotag_id": "ZT-R1008",
    "part_number": "RES-10K-0603",
    "lot_number": "L2026A01",
    "date_code": "2518",
    "quantity_current": 5000,
    "status_before": "IN_STOCK",
    "status_after": "IN_STOCK",
    "location": "Warehouse A1"
  },
  "bom_check": {
    "bom_code": "PCB-DEMO-01",
    "bom_ref": "R12",
    "allowed_date_code_from": "2520",
    "allowed_date_code_to": "2540",
    "actual_date_code": "2518"
  },
  "gateway_action": {
    "led": "YELLOW",
    "buzzer": "DOUBLE_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:33:01+07:00"
}
```

---

# 18. Response unknown tag

```json
{
  "request_id": "REQ-BOM-0005",
  "transaction_id": "TX-000005",
  "mode": "BOM_CHECK",
  "status": "UNKNOWN_TAG",
  "message": "Tag is not registered in the system",
  "violations": [
    "UNKNOWN_TAG"
  ],
  "component": null,
  "bom_check": {
    "bom_code": "PCB-DEMO-01",
    "bom_ref": "R12"
  },
  "gateway_action": {
    "led": "RED",
    "buzzer": "LONG_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:34:01+07:00"
}
```

---

# 19. Response blocked tag

```json
{
  "request_id": "REQ-VERIFY-0002",
  "transaction_id": "TX-000006",
  "mode": "VERIFY",
  "status": "BLOCKED_TAG",
  "message": "Component is blocked and cannot continue in the workflow",
  "violations": [
    "BLOCKED_TAG"
  ],
  "component": {
    "zerotag_id": "ZT-R1015",
    "part_number": "MCU-STM32-DEMO",
    "status_before": "BLOCKED",
    "status_after": "BLOCKED",
    "location": "Hold Area"
  },
  "bom_check": null,
  "gateway_action": {
    "led": "RED",
    "buzzer": "LONG_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:35:01+07:00"
}
```

---

# 20. Response QR/RFID mismatch

```json
{
  "request_id": "REQ-VERIFY-0003",
  "transaction_id": "TX-000007",
  "mode": "VERIFY",
  "status": "QR_RFID_MISMATCH",
  "message": "QR ID and RFID ID do not match",
  "violations": [
    "QR_RFID_MISMATCH"
  ],
  "component": {
    "zerotag_id": "ZT-R1015",
    "part_number": "MCU-STM32-DEMO",
    "status_before": "IN_STOCK",
    "status_after": "BLOCKED",
    "location": "Hold Area"
  },
  "verification": {
    "qr_id": "ZT-R1015",
    "rfid_id": "ZT-R9915",
    "tag_uid": "UID-R9915"
  },
  "bom_check": null,
  "gateway_action": {
    "led": "RED",
    "buzzer": "LONG_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:36:01+07:00"
}
```

---

# 21. Response tamper warning

```json
{
  "request_id": "REQ-VERIFY-0004",
  "transaction_id": "TX-000008",
  "mode": "VERIFY",
  "status": "TAMPER_WARNING",
  "message": "Physical tag identity does not match the registered component",
  "violations": [
    "TAMPER_WARNING"
  ],
  "component": {
    "zerotag_id": "ZT-R1015",
    "part_number": "MCU-STM32-DEMO",
    "status_before": "IN_STOCK",
    "status_after": "BLOCKED",
    "location": "Hold Area"
  },
  "verification": {
    "qr_id": "ZT-R1015",
    "rfid_id": "ZT-R1015",
    "tag_uid": "UNKNOWN-UID"
  },
  "bom_check": null,
  "gateway_action": {
    "led": "RED",
    "buzzer": "LONG_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:37:01+07:00"
}
```

---

# 22. HTTP status

| HTTP status                 | Khi sử dụng                                                   |
| --------------------------- | ------------------------------------------------------------- |
| `200 OK`                    | Request được xử lý, bao gồm cả kết quả nghiệp vụ không hợp lệ |
| `400 Bad Request`           | JSON sai cấu trúc hoặc field không hợp lệ về định dạng        |
| `404 Not Found`             | Gateway, BOM hoặc BOM reference không tồn tại                 |
| `409 Conflict`              | `request_id` đã tồn tại nhưng payload khác                    |
| `422 Unprocessable Entity`  | Thiếu field bắt buộc theo scan mode                           |
| `500 Internal Server Error` | Lỗi backend không dự kiến                                     |
| `503 Service Unavailable`   | Database hoặc dịch vụ nền không khả dụng                      |

`UNKNOWN_TAG` không trả `404`.

Nó là một kết quả nghiệp vụ và trả:

```http
200 OK
```

---

# 23. Error response envelope

Các lỗi kỹ thuật hoặc lỗi validation sử dụng:

```json
{
  "error": {
    "code": "MISSING_REQUIRED_FIELD",
    "message": "bom_ref is required when mode is BOM_CHECK",
    "details": {
      "field": "bom_ref",
      "mode": "BOM_CHECK"
    }
  },
  "request_id": "REQ-BOM-0009",
  "timestamp": "2026-06-06T09:40:00+07:00"
}
```

---

# 24. Error code MVP

```text
INVALID_JSON
MISSING_REQUIRED_FIELD
INVALID_FIELD_VALUE
INVALID_SCAN_MODE
UNKNOWN_GATEWAY
UNKNOWN_BOM
UNKNOWN_BOM_REF
REQUEST_ID_CONFLICT
DATABASE_ERROR
INTERNAL_ERROR
```

---

# 25. API đọc dữ liệu cơ bản

## 25.1. Health check

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "app": "ZeroTag Reel MVP"
}
```

---

## 25.2. Danh sách component

```http
GET /api/v1/components
```

Query parameter dự kiến:

```text
zerotag_id
part_number
lot_number
status
location
```

---

## 25.3. Chi tiết component

```http
GET /api/v1/components/{zerotag_id}
```

---

## 25.4. Danh sách BOM

```http
GET /api/v1/boms
```

---

## 25.5. Chi tiết BOM

```http
GET /api/v1/boms/{bom_code}
```

Response gồm BOM và danh sách BOMItem.

---

## 25.6. Event Log

```http
GET /api/v1/events
```

Query parameter dự kiến:

```text
zerotag_id
transaction_id
event_type
result
date_from
date_to
```

---

## 25.7. Danh sách Gateway

```http
GET /api/v1/gateways
```

---

# 26. API tổng hợp cho giai đoạn sau

Các endpoint sau thuộc Day 4–Day 5 nhưng được giữ trong API namespace:

```http
GET /api/v1/passports/{zerotag_id}
GET /api/v1/traceability/components/{zerotag_id}
GET /api/v1/traceability/lots/{lot_number}
GET /api/v1/traceability/date-codes/{date_code}
GET /api/v1/msl
GET /api/v1/verification
GET /api/v1/exports/events
```

Day 1 chỉ chốt tên và phạm vi; schema chi tiết có thể bổ sung khi triển khai module tương ứng.

---

# 27. Phân trang

Các API trả danh sách sử dụng:

```text
page
page_size
```

Giá trị mặc định:

```text
page = 1
page_size = 20
```

Giới hạn:

```text
page_size <= 100
```

Response danh sách:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

---

# 28. Quyết định API đã chốt

### API-01 — Một endpoint scan thống nhất

```http
POST /api/v1/scans
```

### API-02 — BOM_CHECK dùng BOM và reference

```text
bom_code + bom_ref
```

### API-03 — Business result trả HTTP 200

Các kết quả scan không hợp lệ vẫn trả HTTP 200 nếu request đã được xử lý.

### API-04 — Request ID là duy nhất

`request_id` được dùng để chống tạo transaction và event trùng.

### API-05 — Một response envelope chung

Tất cả scan mode dùng cùng cấu trúc response.

### API-06 — Tám scan result cố định

```text
VALID
WRONG_PART
LOT_MISMATCH
DATECODE_MISMATCH
UNKNOWN_TAG
BLOCKED_TAG
QR_RFID_MISMATCH
TAMPER_WARNING
```

### API-07 — Nhiều lỗi dùng `violations`

Không tạo thêm result `LOT_AND_DATECODE_MISMATCH`.

### API-08 — Gateway chỉ thực thi action

Backend trả:

```text
gateway_action.led
gateway_action.buzzer
```

### API-09 — Raw identification được lưu để audit

Backend lưu các mã nhận được từ request trong ScanTransaction.

### API-10 — Dashboard và Gateway dùng cùng contract

Không tạo API scan riêng cho Dashboard và Gateway.
