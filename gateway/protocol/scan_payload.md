# Scan Payload

## 1. Mục đích

Payload này được dùng chung cho:

* Dashboard Scan Input
* Gateway Simulator
* ESP32/NFC Gateway
* ESP32/RFID Gateway
* ESP32/UHF Gateway sau này

Endpoint:

```http
POST /api/v1/scans
```

---

## 2. Payload tổng quát

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

## 3. Field

| Field        | Kiểu        | Mô tả                         |
| ------------ | ----------- | ----------------------------- |
| `request_id` | string      | Mã request duy nhất           |
| `gateway_id` | string      | Mã Gateway                    |
| `mode`       | string      | Scan mode                     |
| `location`   | string      | Vị trí scan                   |
| `zerotag_id` | string/null | ZeroTag ID                    |
| `tag_uid`    | string/null | UID/EPC vật lý                |
| `qr_id`      | string/null | ZeroTag ID đọc từ QR          |
| `rfid_id`    | string/null | ZeroTag ID đọc/ánh xạ từ RFID |
| `bom_code`   | string/null | Mã BOM                        |
| `bom_ref`    | string/null | Dòng BOM                      |
| `read_at`    | datetime    | Thời điểm đọc tag             |

---

## 4. Scan mode

```text
INBOUND
BOM_CHECK
RETURN
VERIFY
```

---

## 5. Field bắt buộc

### INBOUND

Bắt buộc:

```text
request_id
gateway_id
mode
location
read_at
zerotag_id hoặc tag_uid
```

### BOM_CHECK

Bắt buộc:

```text
request_id
gateway_id
mode
location
read_at
zerotag_id hoặc tag_uid
bom_code
bom_ref
```

### RETURN

Bắt buộc:

```text
request_id
gateway_id
mode
location
read_at
zerotag_id hoặc tag_uid
```

### VERIFY

Bắt buộc:

```text
request_id
gateway_id
mode
location
read_at
qr_id
rfid_id
```

Khuyến nghị gửi thêm:

```text
tag_uid
```

---

## 6. Ví dụ INBOUND

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

---

## 7. Ví dụ BOM_CHECK

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

---

## 8. Ví dụ RETURN

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

---

## 9. Ví dụ VERIFY

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

## 10. Quy tắc request ID

* `request_id` phải duy nhất.
* Retry phải dùng lại cùng `request_id`.
* Retry phải giữ nguyên payload.
* Không tạo request mới cho cùng một lần đọc tag.
* Trùng ID nhưng khác payload sẽ trả `409 Conflict`.

---

## 11. Quy tắc thời gian

`read_at` dùng ISO 8601 và phải có timezone.

Ví dụ:

```text
2026-06-06T09:30:00+07:00
```

---

## 12. Quy tắc dữ liệu

* Field không sử dụng có thể bỏ khỏi payload hoặc gửi `null`.
* Không gửi chuỗi rỗng thay cho `null`.
* `bom_code` và `bom_ref` chỉ dùng cho `BOM_CHECK`.
* `qr_id` và `rfid_id` bắt buộc với `VERIFY`.
* Gateway không tự tạo component khi gặp unknown tag.
* Gateway không tự quyết định scan result.
