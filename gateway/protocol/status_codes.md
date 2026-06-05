# Status Codes

## 1. Scan Modes

- `INBOUND`
- `BOM_CHECK`
- `RETURN`
- `VERIFY`

## 2. Scan Results

- `VALID`
- `WRONG_PART`
- `LOT_MISMATCH`
- `DATECODE_MISMATCH`
- `UNKNOWN_TAG`
- `BLOCKED_TAG`
- `QR_RFID_MISMATCH`
- `TAMPER_WARNING`

Không sử dụng:

- `LOT_AND_DATECODE_MISMATCH`

Nhiều lỗi đồng thời được lưu trong `violations`.

## 3. Component Status

- `REGISTERED`
- `IN_STOCK`
- `ISSUED`
- `BLOCKED`
- `SCRAPPED`

Không sử dụng `RETURNED` làm trạng thái thường trực trong MVP.

## 4. Event Result

- `OK`
- `WARNING`
- `FAIL`

## 5. Event Type

- `REEL_SCANNED`
- `WAREHOUSE_IN`
- `BOM_CHECK_STARTED`
- `BOM_MATCH_OK`
- `BOM_MATCH_FAIL`
- `LOT_MISMATCH`
- `DATECODE_MISMATCH`
- `WARNING_ISSUED`
- `UNKNOWN_TAG`
- `RETURN_TO_STOCK`
- `COMPONENT_ISSUED`
- `VERIFICATION_PASSED`
- `VERIFICATION_FAILED`
- `TAMPER_WARNING`
- `BLOCKED_TAG`
- `TAG_BLOCKED`

## 6. LED

- `OFF`
- `GREEN`
- `YELLOW`
- `RED`

## 7. Buzzer

- `NONE`
- `SHORT_BEEP`
- `DOUBLE_BEEP`
- `LONG_BEEP`

## 8. Gateway Type

- `SIMULATOR`
- `ESP32_NFC`
- `ESP32_RFID`
- `ESP32_UHF`

## 9. Gateway Status

- `ONLINE`
- `OFFLINE`
- `DISABLED`

## 10. MSL Status

- `NORMAL`
- `WARNING`
- `NEED_BAKE`

MSL Status không phải Scan Result.

## 11. Technical Error Codes

- `INVALID_JSON`
- `MISSING_REQUIRED_FIELD`
- `INVALID_FIELD_VALUE`
- `INVALID_SCAN_MODE`
- `UNKNOWN_GATEWAY`
- `UNKNOWN_BOM`
- `UNKNOWN_BOM_REF`
- `REQUEST_ID_CONFLICT`
- `DATABASE_ERROR`
- `INTERNAL_ERROR`