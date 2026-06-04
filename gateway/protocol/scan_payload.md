# Scan Payload

Payload này dùng chung cho:

- Dashboard Scan Input
- Gateway Simulator
- ESP32/NFC/RFID/UHF Gateway sau này

## Fields

- gateway_id: mã gateway
- zerotag_id: mã ZeroTag ID
- tag_uid: UID hoặc EPC thật của tag
- mode: INBOUND, BOM_CHECK, RETURN, VERIFY
- location: vị trí scan
- bom_code: mã BOM nếu đang ở chế độ BOM_CHECK

## Example

{
  "gateway_id": "ZG-001",
  "zerotag_id": "ZT-R1001",
  "tag_uid": "UID-R1001",
  "mode": "BOM_CHECK",
  "location": "SMT Issue Station 01",
  "bom_code": "PCB-DEMO-01"
}
