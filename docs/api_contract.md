# API Contract - ZeroTag-Reel MVP

## Nguyên tắc

Mọi nguồn scan đều dùng cùng một endpoint:

POST /api/v1/scans

Nguồn scan có thể là:

- Dashboard Scan Input
- Gateway Simulator
- QR Scanner
- ESP32/NFC/RFID/UHF Gateway trong tương lai

## 1. POST /api/v1/scans

### Request mẫu

{
  "gateway_id": "ZG-001",
  "zerotag_id": "ZT-R1001",
  "tag_uid": "UID-R1001",
  "mode": "BOM_CHECK",
  "location": "SMT Issue Station 01",
  "bom_code": "PCB-DEMO-01"
}

### Response mẫu - hợp lệ

{
  "status": "VALID",
  "message": "Correct BOM and lot",
  "zerotag_id": "ZT-R1001",
  "part_number": "RES-10K-0603",
  "lot_number": "L2026A01",
  "event_type": "BOM_MATCH_OK",
  "gateway_action": {
    "led": "GREEN",
    "buzzer": "SHORT_BEEP"
  }
}

### Response mẫu - sai part

{
  "status": "WRONG_PART",
  "message": "Wrong part number",
  "event_type": "BOM_MATCH_FAIL",
  "gateway_action": {
    "led": "RED",
    "buzzer": "LONG_BEEP"
  }
}

### Response mẫu - sai lot

{
  "status": "LOT_MISMATCH",
  "message": "Correct part number but wrong lot",
  "event_type": "LOT_MISMATCH",
  "gateway_action": {
    "led": "RED",
    "buzzer": "DOUBLE_BEEP"
  }
}

### Response mẫu - tag lạ

{
  "status": "UNKNOWN_TAG",
  "message": "Tag is not registered in system",
  "event_type": "UNKNOWN_TAG",
  "gateway_action": {
    "led": "RED",
    "buzzer": "LONG_BEEP"
  }
}

## 2. Các API khác

- GET /api/v1/components
- GET /api/v1/components/{zerotag_id}
- GET /api/v1/boms
- GET /api/v1/events
- GET /api/v1/passports/{zerotag_id}
- GET /api/v1/traceability/lot/{lot_number}
- GET /api/v1/msl
- GET /api/v1/verification
- GET /api/v1/gateways
- GET /api/v1/exports/events
