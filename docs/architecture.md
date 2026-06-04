# Kiến trúc ZeroTag-Reel MVP

## 1. Kiểu kiến trúc

Dự án dùng kiến trúc:

Modular Monolith + Layered Architecture + Gateway-ready API.

Mục tiêu là build nhanh trong giai đoạn MVP nhưng vẫn giữ cấu trúc đủ sạch để sau này kết nối phần cứng thật như ESP32, NFC, RFID hoặc UHF reader.

## 2. Luồng tổng thể

ZeroTag Smart Label / QR / RFID
→ ZeroGateway hoặc Dashboard Scan
→ Backend API
→ Business Services
→ SQLite Database
→ Dashboard

## 3. Nguyên tắc thiết kế

- Dashboard không đọc database trực tiếp.
- Gateway không xử lý nghiệp vụ BOM.
- Mọi nguồn scan đều đi qua Backend API.
- Backend là nơi xử lý nghiệp vụ trung tâm.
- Phần cứng thật sau này chỉ thay thế Gateway Simulator, không làm thay đổi backend core.

## 4. Các khối chính

### Backend

Xử lý API, nghiệp vụ, database, event log và traceability.

### Dashboard

Giao diện Streamlit cho người dùng thao tác và xem dữ liệu.

### Gateway

Chứa protocol, simulator và firmware phần cứng sau này.

### Data

Chứa dữ liệu seed CSV và file export.

### Docs

Chứa tài liệu kiến trúc, API, database, gateway protocol và demo script.
