# Gateway Response

## 1. Mục đích

Backend trả response để Gateway:

* Hiển thị kết quả
* Điều khiển LED
* Điều khiển buzzer
* Phân biệt lỗi nghiệp vụ và lỗi kỹ thuật
* Nhận biết request replay

---

## 2. Response tổng quát

```json
{
  "request_id": "REQ-BOM-0001",
  "transaction_id": "TX-000001",
  "mode": "BOM_CHECK",
  "status": "VALID",
  "message": "Correct part number, lot and date-code",
  "violations": [],
  "gateway_action": {
    "led": "GREEN",
    "buzzer": "SHORT_BEEP"
  },
  "replayed": false,
  "processed_at": "2026-06-06T09:30:01+07:00"
}
```

Gateway phải đọc tối thiểu:

```text
status
message
gateway_action.led
gateway_action.buzzer
replayed
```

---

## 3. Scan result

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

---

## 4. LED

```text
OFF
GREEN
YELLOW
RED
```

| Result              | LED      |
| ------------------- | -------- |
| `VALID`             | `GREEN`  |
| `WRONG_PART`        | `RED`    |
| `LOT_MISMATCH`      | `YELLOW` |
| `DATECODE_MISMATCH` | `YELLOW` |
| `UNKNOWN_TAG`       | `RED`    |
| `BLOCKED_TAG`       | `RED`    |
| `QR_RFID_MISMATCH`  | `RED`    |
| `TAMPER_WARNING`    | `RED`    |

---

## 5. Buzzer

```text
NONE
SHORT_BEEP
DOUBLE_BEEP
LONG_BEEP
```

| Result              | Buzzer        |
| ------------------- | ------------- |
| `VALID`             | `SHORT_BEEP`  |
| `WRONG_PART`        | `LONG_BEEP`   |
| `LOT_MISMATCH`      | `DOUBLE_BEEP` |
| `DATECODE_MISMATCH` | `DOUBLE_BEEP` |
| `UNKNOWN_TAG`       | `LONG_BEEP`   |
| `BLOCKED_TAG`       | `LONG_BEEP`   |
| `QR_RFID_MISMATCH`  | `LONG_BEEP`   |
| `TAMPER_WARNING`    | `LONG_BEEP`   |

---

## 6. Nhiều vi phạm

```json
{
  "status": "LOT_MISMATCH",
  "violations": [
    "LOT_MISMATCH",
    "DATECODE_MISMATCH"
  ],
  "gateway_action": {
    "led": "YELLOW",
    "buzzer": "DOUBLE_BEEP"
  }
}
```

Gateway thực hiện action theo `gateway_action`, không tự chọn action từ danh sách `violations`.

---

## 7. Replay response

Nếu Gateway retry cùng `request_id` và cùng payload:

```json
{
  "request_id": "REQ-BOM-0001",
  "transaction_id": "TX-000001",
  "status": "VALID",
  "gateway_action": {
    "led": "GREEN",
    "buzzer": "SHORT_BEEP"
  },
  "replayed": true
}
```

Gateway xử lý replay giống response bình thường.

---

## 8. Error response

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

Gateway không được retry lỗi validation hoặc cấu hình.

---

## 9. Trạng thái cục bộ

| Gateway state       | LED                      | Buzzer                |
| ------------------- | ------------------------ | --------------------- |
| Idle                | `OFF`                    | `NONE`                |
| Đang đọc tag        | `YELLOW` nhấp nháy       | `NONE`                |
| Đang chờ backend    | `YELLOW` nhấp nháy       | `NONE`                |
| Timeout/mất kết nối | `YELLOW` nhấp nháy nhanh | `LONG_BEEP`           |
| Backend trả kết quả | Theo `gateway_action`    | Theo `gateway_action` |

Trạng thái cục bộ không phải scan result nghiệp vụ.

---

## 10. Quy tắc xử lý

* Gateway không tự sửa `gateway_action`.
* HTTP `200` có thể chứa kết quả nghiệp vụ không hợp lệ.
* `UNKNOWN_TAG` không phải HTTP `404`.
* Retry chỉ thực hiện với timeout hoặc lỗi mạng.
* Retry phải giữ nguyên `request_id`.
* Sau khi hiển thị kết quả, Gateway trở về trạng thái idle.
