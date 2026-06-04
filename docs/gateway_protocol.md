# Gateway Protocol - ZeroTag-Reel MVP

## 1. Vai trò của Gateway

ZeroGateway không xử lý nghiệp vụ BOM.

Gateway chỉ có nhiệm vụ:

- Đọc ZeroTag ID hoặc tag UID.
- Gửi scan payload về backend.
- Nhận kết quả từ backend.
- Bật LED/buzzer theo gateway_action.

## 2. Scan Payload

{
  "gateway_id": "ZG-001",
  "zerotag_id": "ZT-R1001",
  "tag_uid": "UID-R1001",
  "mode": "BOM_CHECK",
  "location": "SMT Issue Station 01",
  "bom_code": "PCB-DEMO-01"
}

## 3. Gateway Response

{
  "status": "VALID",
  "message": "Correct BOM and lot",
  "gateway_action": {
    "led": "GREEN",
    "buzzer": "SHORT_BEEP"
  }
}

## 4. LED Mapping

- GREEN: hợp lệ
- RED: lỗi nghiêm trọng
- YELLOW: cảnh báo hoặc đang đọc

## 5. Buzzer Mapping

- SHORT_BEEP: hợp lệ
- LONG_BEEP: lỗi
- DOUBLE_BEEP: sai lot/date-code hoặc cảnh báo trung bình

## 6. Các mode

- INBOUND
- BOM_CHECK
- RETURN
- VERIFY
