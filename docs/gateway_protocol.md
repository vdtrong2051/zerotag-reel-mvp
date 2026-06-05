# Gateway Protocol — ZeroTag-Reel MVP

## 1. Mục tiêu

Tài liệu này định nghĩa giao tiếp giữa ZeroGateway và Backend API của ZeroTag-Reel MVP.

Trong MVP, ZeroGateway có thể là:

* Gateway Simulator bằng Python
* Dashboard Scan Input
* ESP32 kết nối NFC reader
* ESP32 kết nối HF RFID reader
* ESP32 kết nối UHF RFID reader trong giai đoạn sau

Gateway Simulator và gateway phần cứng phải sử dụng cùng API contract.

Khi thay Gateway Simulator bằng phần cứng thật, backend không được yêu cầu thay đổi luồng nghiệp vụ.

---

## 2. Nguyên tắc kiến trúc

Gateway là thiết bị thu nhận dữ liệu và phản hồi trạng thái.

Gateway không phải nơi xử lý nghiệp vụ.

Luồng tổng quát:

```text
Smart Label
→ Gateway
→ POST /api/v1/scans
→ Backend xử lý
→ Gateway nhận response
→ Gateway điều khiển LED/buzzer
```

---

## 3. Trách nhiệm của Gateway

Gateway có trách nhiệm:

* Đọc ZeroTag ID
* Đọc UID hoặc EPC vật lý của tag
* Đọc QR/DataMatrix nếu có
* Tạo `request_id`
* Ghi nhận thời điểm đọc tag
* Tạo scan payload
* Gửi HTTP request đến backend
* Nhận response
* Thực hiện `gateway_action`
* Hiển thị lỗi kết nối nếu backend không phản hồi

Gateway không được:

* Truy cập database
* Tự kiểm tra BOM
* Tự kiểm tra lot/date-code
* Tự quyết định tag hợp lệ
* Tự thay đổi trạng thái component
* Tự tạo Event Log
* Tự đăng ký unknown tag
* Lưu bản sao database nghiệp vụ

---

## 4. Trách nhiệm của Backend

Backend có trách nhiệm:

* Validate scan payload
* Kiểm tra Gateway
* Ánh xạ mã nhận diện về component
* Kiểm tra trạng thái component
* Kiểm tra BOM
* Kiểm tra part number
* Kiểm tra lot/date-code
* Kiểm tra quantity
* Xử lý Verification
* Tạo ScanTransaction
* Ghi Event
* Thay đổi trạng thái component khi nghiệp vụ yêu cầu
* Trả kết quả nghiệp vụ
* Trả `gateway_action`

---

## 5. Giao thức truyền thông MVP

MVP sử dụng:

```text
HTTP POST + JSON
```

Endpoint:

```http
POST /api/v1/scans
```

Content type:

```http
Content-Type: application/json
```

Encoding:

```text
UTF-8
```

Backend local mặc định:

```text
http://127.0.0.1:8000
```

Endpoint đầy đủ:

```text
http://127.0.0.1:8000/api/v1/scans
```

Trong phần cứng thật, địa chỉ backend sẽ được cấu hình bằng biến môi trường hoặc firmware configuration.

---

## 6. Scan mode

Gateway hỗ trợ bốn mode:

```text
INBOUND
BOM_CHECK
RETURN
VERIFY
```

### `INBOUND`

Xác nhận component đã nhập kho.

```text
REGISTERED → IN_STOCK
```

### `BOM_CHECK`

Kiểm tra component với một dòng BOM cụ thể.

```text
bom_code + bom_ref
```

BOM_CHECK không tự động chuyển component sang `ISSUED`.

### `RETURN`

Trả component từ khu sản xuất về kho.

```text
ISSUED → IN_STOCK
```

### `VERIFY`

Đối chiếu QR, RFID và UID vật lý.

Nếu phát hiện bất thường, component có thể chuyển sang `BLOCKED`.

---

## 7. Scan payload chuẩn

Payload tổng quát:

```json
{
  "request_id": "REQ-BOM-0001",
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

## 8. Mã nhận diện

### `zerotag_id`

Mã nghiệp vụ của ZeroTag.

Ví dụ:

```text
ZT-R1001
```

### `tag_uid`

UID hoặc EPC vật lý của NFC/RFID/UHF tag.

Ví dụ:

```text
UID-R1001
```

### `qr_id`

ZeroTag ID được đọc từ QR hoặc DataMatrix.

Ví dụ:

```text
ZT-R1001
```

### `rfid_id`

ZeroTag ID được đọc từ dữ liệu RFID hoặc được Gateway ánh xạ từ RFID.

Ví dụ:

```text
ZT-R1001
```

Phân biệt:

```text
rfid_id
→ mã nghiệp vụ trong dữ liệu RFID

tag_uid
→ UID/EPC vật lý của chip/tag
```

---

## 9. Field bắt buộc theo mode

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

Field không sử dụng có thể được bỏ khỏi payload hoặc gửi dưới dạng `null`.

---

## 10. Request ID và chống gửi trùng

Mỗi scan phải có một `request_id` duy nhất.

Ví dụ:

```text
REQ-BOM-0001
```

Gateway Simulator có thể dùng mã dễ đọc.

Gateway thật có thể dùng UUID hoặc mã kết hợp gateway ID, timestamp và sequence number.

Ví dụ:

```text
ZG-001-20260606T093000-0001
```

### Retry cùng request

Nếu Gateway không nhận được response và gửi lại request:

* Phải dùng lại cùng `request_id`
* Không được tạo `request_id` mới
* Payload phải giữ nguyên

Backend sẽ:

* Không tạo ScanTransaction trùng
* Không tạo Event trùng
* Trả lại kết quả đã xử lý
* Đặt `replayed = true`

### Trùng request ID nhưng payload khác

Backend trả:

```http
409 Conflict
```

Error code:

```text
REQUEST_ID_CONFLICT
```

---

## 11. Timeout và retry

Timeout HTTP của Gateway:

```text
5 giây
```

Số lần retry tối đa:

```text
2 lần
```

Gateway chỉ retry khi:

* Timeout
* Mất kết nối
* Không nhận được HTTP response
* Lỗi mạng tạm thời

Gateway không retry khi đã nhận:

* `200 OK`
* `400 Bad Request`
* `404 Not Found`
* `409 Conflict`
* `422 Unprocessable Entity`

Mọi lần retry phải sử dụng cùng `request_id`.

Khoảng nghỉ đề xuất:

```text
Lần đầu thất bại
→ chờ 1 giây
→ retry lần 1
→ chờ 2 giây
→ retry lần 2
```

MVP chưa triển khai offline queue dài hạn.

---

## 12. Scan response chuẩn

Response tổng quát:

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
    "status_after": "IN_STOCK"
  },
  "bom_check": {
    "bom_code": "PCB-DEMO-01",
    "bom_ref": "R12",
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

Gateway chỉ cần đọc tối thiểu:

```text
status
message
gateway_action.led
gateway_action.buzzer
```

Các field còn lại dùng cho Dashboard, Event Log và debug.

---

## 13. Scan result

MVP sử dụng đúng tám kết quả:

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

Nếu có nhiều lỗi:

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

## 14. LED mapping

Các trạng thái LED:

```text
OFF
GREEN
YELLOW
RED
```

Mapping kết quả:

| Scan result         | LED      |
| ------------------- | -------- |
| `VALID`             | `GREEN`  |
| `WRONG_PART`        | `RED`    |
| `LOT_MISMATCH`      | `YELLOW` |
| `DATECODE_MISMATCH` | `YELLOW` |
| `UNKNOWN_TAG`       | `RED`    |
| `BLOCKED_TAG`       | `RED`    |
| `QR_RFID_MISMATCH`  | `RED`    |
| `TAMPER_WARNING`    | `RED`    |

Trạng thái cục bộ:

| Gateway state    | LED                      |
| ---------------- | ------------------------ |
| Idle             | `OFF`                    |
| Đang đọc tag     | `YELLOW` nhấp nháy       |
| Đang chờ backend | `YELLOW` nhấp nháy       |
| Kết nối thất bại | `YELLOW` nhấp nháy nhanh |

Trạng thái cục bộ không thay thế kết quả nghiệp vụ từ backend.

---

## 15. Buzzer mapping

Các trạng thái buzzer:

```text
NONE
SHORT_BEEP
DOUBLE_BEEP
LONG_BEEP
```

Mapping:

| Scan result         | Buzzer        |
| ------------------- | ------------- |
| `VALID`             | `SHORT_BEEP`  |
| `WRONG_PART`        | `LONG_BEEP`   |
| `LOT_MISMATCH`      | `DOUBLE_BEEP` |
| `DATECODE_MISMATCH` | `DOUBLE_BEEP` |
| `UNKNOWN_TAG`       | `LONG_BEEP`   |
| `BLOCKED_TAG`       | `LONG_BEEP`   |
| `QR_RFID_MISMATCH`  | `LONG_BEEP`   |
| `TAMPER_WARNING`    | `LONG_BEEP`   |

Khi idle:

```text
NONE
```

---

## 16. Xử lý response tại Gateway

Gateway xử lý theo thứ tự:

```text
1. Nhận HTTP response
2. Kiểm tra HTTP status
3. Parse JSON
4. Đọc status
5. Đọc gateway_action
6. Điều khiển LED
7. Điều khiển buzzer
8. Hiển thị message nếu có màn hình
9. Trở về trạng thái idle
```

Gateway không được tự sửa `gateway_action`.

---

## 17. Business result và lỗi kỹ thuật

### Business result

Các kết quả như:

```text
WRONG_PART
LOT_MISMATCH
UNKNOWN_TAG
```

được trả với:

```http
200 OK
```

Vì backend đã nhận và xử lý request thành công.

### Lỗi kỹ thuật hoặc validation

| HTTP status | Ý nghĩa                                 |
| ----------- | --------------------------------------- |
| `400`       | JSON hoặc field sai định dạng           |
| `404`       | Gateway, BOM hoặc BOM Ref không tồn tại |
| `409`       | Request ID xung đột                     |
| `422`       | Thiếu field bắt buộc theo mode          |
| `500`       | Lỗi backend                             |
| `503`       | Database hoặc dịch vụ không khả dụng    |

Gateway không được hiểu HTTP `404` là `UNKNOWN_TAG`.

`UNKNOWN_TAG` là business result và được trả bằng HTTP `200`.

---

## 18. Error response

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

Gateway phải:

* Không retry lỗi validation
* Hiển thị lỗi cấu hình
* Không tự thay đổi trạng thái component
* Không phát sinh scan request mới nếu người dùng chưa thao tác lại

---

## 19. Trạng thái Gateway

Gateway status:

```text
ONLINE
OFFLINE
DISABLED
```

Gateway type:

```text
SIMULATOR
ESP32_NFC
ESP32_RFID
ESP32_UHF
```

Backend có thể cập nhật `last_seen_at` khi nhận request hợp lệ từ Gateway.

Gateway ở trạng thái `DISABLED` không được phép xử lý scan.

---

## 20. Gateway Simulator

Gateway Simulator phải mô phỏng đúng hành vi của phần cứng:

```text
Đọc sample payload
→ gửi HTTP POST
→ nhận response
→ hiển thị LED/buzzer giả lập
```

Gateway Simulator không được gọi database hoặc service nội bộ của backend.

Nó phải hoạt động như một client HTTP độc lập.

---

## 21. Bảo mật trong MVP

MVP chạy local nên chưa triển khai đầy đủ:

* HTTPS
* API key
* Device certificate
* Mutual TLS
* Firmware signing

Trong giai đoạn pilot, Gateway cần bổ sung:

* HTTPS
* API key hoặc device token
* Gateway authentication
* Request signature
* Secret storage an toàn

---

## 22. Ngoài phạm vi MVP

Không triển khai trong MVP v0.1:

* MQTT production
* Offline queue dài hạn
* Firmware OTA
* Multi-antenna
* RSSI filtering
* Bulk UHF reading
* Gateway mesh
* Device certificate
* Cloud device provisioning
* Hardware anti-tamper hoàn chỉnh

---

## 23. Quyết định protocol đã chốt

### GP-01 — HTTP JSON cho MVP

Gateway sử dụng HTTP POST với JSON.

### GP-02 — Một endpoint scan

```http
POST /api/v1/scans
```

### GP-03 — Gateway không xử lý nghiệp vụ

Mọi quyết định nghiệp vụ thuộc Backend.

### GP-04 — Request ID chống gửi trùng

Retry phải giữ nguyên `request_id`.

### GP-05 — Timeout 5 giây

Gateway timeout sau 5 giây.

### GP-06 — Retry tối đa 2 lần

Chỉ retry khi gặp lỗi mạng hoặc timeout.

### GP-07 — Gateway thực hiện `gateway_action`

Gateway không tự ánh xạ lại kết quả nghiệp vụ.

### GP-08 — Simulator và phần cứng dùng cùng contract

Không tạo protocol riêng cho Gateway Simulator.

### GP-09 — Không có offline queue trong MVP

Gateway không lưu hàng đợi scan dài hạn.

### GP-10 — Không dùng result tổng hợp lot/date-code

Các lỗi đồng thời được lưu trong `violations`.
