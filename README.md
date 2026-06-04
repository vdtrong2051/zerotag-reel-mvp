# ZeroTag-Reel MVP

ZeroTag-Reel MVP là bản nguyên mẫu phần mềm theo hướng **software-first** cho hệ thống quản lý và truy xuất cuộn linh kiện SMT bằng ZeroTag ID.

Mục tiêu của MVP là mô phỏng quy trình:

```text
ZeroTag Smart Label / QR / RFID
→ ZeroGateway hoặc Dashboard Scan
→ Backend API
→ Xử lý nghiệp vụ
→ Cơ sở dữ liệu SQLite
→ Dashboard hiển thị kết quả
```

Dự án tập trung vào bài toán quản lý reel/tray/carton linh kiện trong môi trường EMS/SMT, đặc biệt là kiểm tra đúng BOM, truy xuất lot/date-code, ghi nhận event log và mô phỏng xác thực nhãn thông minh.

---

## 1. Phạm vi MVP

MVP hiện tại tập trung vào các chức năng chính sau:

* Quản lý danh sách linh kiện/reel/tray/carton
* Hồ sơ số linh kiện: Digital Component Passport
* Kiểm tra đúng BOM: BOM Matching
* Cảnh báo sai mã linh kiện
* Cảnh báo đúng mã nhưng sai lot/date-code
* Ghi nhận lịch sử sự kiện: Event Log
* Truy xuất lot/date-code
* Theo dõi MSL ở mức mô phỏng đơn giản
* Mô phỏng anti-tamper và verification
* Mô phỏng ZeroGateway bằng HTTP payload

---

## 2. Nguyên tắc thiết kế

Dự án được thiết kế theo nguyên tắc:

```text
Dashboard không đọc database trực tiếp.
Gateway không xử lý nghiệp vụ BOM.
Mọi nguồn scan đều đi qua Backend API.
Backend là nơi xử lý nghiệp vụ trung tâm.
```

Điều này giúp hệ thống dễ mở rộng về sau. Khi có phần cứng thật như ESP32, NFC, RFID hoặc UHF reader, phần cứng chỉ cần gửi dữ liệu scan về backend theo cùng một chuẩn payload.

---

## 3. Kiến trúc tổng quan

```text
ZeroTag Smart Label
QR / NFC / RFID / UHF
        │
        ▼
ZeroGateway / Gateway Simulator / Dashboard Scan
        │
        ▼
Backend API
        │
        ▼
Business Services
BOM Matching / Inventory / Event Log / Traceability
        │
        ▼
SQLite Database
        │
        ▼
Dashboard
```

---

## 4. Công nghệ sử dụng

### Backend

* Python 3.12
* FastAPI
* Uvicorn
* SQLAlchemy
* Pydantic
* SQLite

### Dashboard

* Streamlit
* Pandas
* Requests hoặc HTTPX

### Kiểm thử và hỗ trợ phát triển

* Pytest
* Black
* Ruff
* Postman hoặc Thunder Client
* Git

### Mô phỏng phần cứng

* Gateway Simulator bằng Python
* Sample JSON payload
* HTTP request tới Backend API
* ESP32/NFC/RFID/UHF sẽ được bổ sung ở giai đoạn sau

---

## 5. Cấu trúc thư mục dự kiến

```text
zerotag-reel-mvp/
│
├── backend/              # Backend API và xử lý nghiệp vụ
├── dashboard/            # Giao diện dashboard Streamlit
├── gateway/              # Mô phỏng gateway và protocol phần cứng
├── data/                 # Dữ liệu mẫu và file export
├── docs/                 # Tài liệu kiến trúc, API, database, demo
├── requirements.txt      # Danh sách thư viện Python
├── .env.example          # Mẫu cấu hình môi trường
├── .gitignore            # Danh sách file/thư mục không đưa lên Git
└── README.md             # Tài liệu tổng quan dự án
```

---

## 6. Luồng nghiệp vụ chính

### Luồng 1: Nhập kho

```text
Người dùng hoặc gateway quét ZeroTag ID
→ Backend kiểm tra ID
→ Cập nhật trạng thái IN_STOCK
→ Ghi event WAREHOUSE_IN
```

### Luồng 2: Kiểm tra đúng BOM

```text
Chọn BOM cần kiểm tra
→ Quét ZeroTag ID
→ Backend tra hồ sơ linh kiện
→ So sánh part number và lot/date-code
→ Trả kết quả VALID / WRONG_PART / LOT_MISMATCH
→ Ghi event log
```

### Luồng 3: Truy xuất lot/date-code

```text
Nhập lot hoặc date-code
→ Backend tìm các reel liên quan
→ Trả về hồ sơ linh kiện và lịch sử event
```

### Luồng 4: Verification / Anti-tamper

```text
Quét QR ID và RFID ID
→ Backend kiểm tra khớp/không khớp
→ Trả kết quả VERIFIED / UNKNOWN_TAG / QR_RFID_MISMATCH / TAMPER_WARNING
```

---

## 7. Kế hoạch phát triển 7 ngày

* Ngày 0: Tạo môi trường, cấu trúc folder, file cấu hình và dữ liệu mẫu ban đầu
* Ngày 1: Chốt kiến trúc, API contract, database schema và business flow
* Ngày 2: Dựng backend skeleton, database và seed data
* Ngày 3: Làm scan flow, BOM Matching và Event Log
* Ngày 4: Dựng dashboard core theo UI design
* Ngày 5: Làm Traceability, MSL Tracking và Verification
* Ngày 6: Làm Gateway Simulator và mock phần cứng
* Ngày 7: Test tổng, polish UI, viết demo script và đóng gói MVP

---

## 8. Giới hạn hiện tại của MVP

MVP hiện tại chưa nhằm mục tiêu triển khai công nghiệp hoàn chỉnh. Các giới hạn gồm:

* Chưa đọc tag RF thật trong giai đoạn phần mềm đầu tiên
* ZeroGateway đang được mô phỏng bằng HTTP payload
* Chưa tích hợp ERP/MES/WMS
* Chưa tracking realtime toàn bộ kho
* Anti-tamper mới mô phỏng ở mức nghiệp vụ
* MSL Tracking là phiên bản đơn giản để demo
* Chưa tối ưu cho môi trường kim loại phức tạp

---

## 9. Mục tiêu demo

MVP cần chứng minh được rằng:

```text
Một ZeroTag ID có thể liên kết với hồ sơ số của reel/tray/carton.
Hệ thống có thể kiểm tra đúng BOM.
Hệ thống có thể cảnh báo sai mã hoặc sai lot/date-code.
Hệ thống có thể ghi event log.
Hệ thống có thể truy xuất lại lịch sử sử dụng linh kiện.
Gateway thật sau này có thể thay thế gateway simulator mà không phá kiến trúc.
```

---

## 10. Ghi chú

ZeroTag-Reel MVP không nhằm thay thế hoàn toàn barcode, QR, RFID hoặc hệ thống quản lý kho hiện có. Dự án định vị là một lớp nhận diện và ghi nhận sự kiện bổ sung, giúp tăng khả năng kiểm soát linh kiện trong workflow EMS/SMT.
