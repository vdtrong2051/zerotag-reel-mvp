# Database Schema - ZeroTag-Reel MVP

Database MVP dùng SQLite.

## 1. components

Lưu hồ sơ số của từng reel/tray/carton.

Các trường dự kiến:

- id
- zerotag_id
- tag_uid
- part_number
- component_name
- supplier
- lot_number
- date_code
- quantity_initial
- quantity_current
- status
- location
- label_type
- tamper_status
- created_at
- updated_at

## 2. boms

Lưu thông tin BOM.

- id
- bom_code
- product_name
- description
- status
- created_at
- updated_at

## 3. bom_items

Lưu từng dòng linh kiện trong BOM.

- id
- bom_id
- required_part_number
- allowed_lot
- allowed_date_code_from
- allowed_date_code_to
- required_quantity
- bom_ref
- note

## 4. gateways

Lưu thông tin gateway.

- id
- gateway_id
- gateway_name
- location
- status
- last_seen_at
- created_at

## 5. scan_transactions

Lưu một phiên scan/kiểm tra.

- id
- transaction_id
- zerotag_id
- gateway_id
- mode
- bom_code
- final_result
- started_at
- completed_at

## 6. events

Lưu từng event nhỏ trong một transaction.

- id
- event_id
- transaction_id
- zerotag_id
- gateway_id
- event_type
- result
- message
- metadata_json
- created_at

## 7. msl_profiles

Lưu dữ liệu MSL đơn giản.

- id
- zerotag_id
- msl_level
- bag_open_time
- floor_life_limit_hours
- floor_life_used_hours
- storage_status

## 8. verification_checks

Lưu dữ liệu kiểm tra QR/RFID/anti-tamper.

- id
- zerotag_id
- qr_id
- rfid_id
- verification_result
- reason
- checked_at
