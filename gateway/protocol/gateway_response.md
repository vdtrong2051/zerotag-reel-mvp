# Gateway Response

Backend trả về response để gateway biết cần bật LED/buzzer như thế nào.

## Example

{
  "status": "VALID",
  "message": "Correct BOM and lot",
  "gateway_action": {
    "led": "GREEN",
    "buzzer": "SHORT_BEEP"
  }
}

## LED

- GREEN: hợp lệ
- RED: lỗi
- YELLOW: cảnh báo hoặc đang xử lý

## Buzzer

- SHORT_BEEP: hợp lệ
- LONG_BEEP: lỗi
- DOUBLE_BEEP: cảnh báo sai lot/date-code
