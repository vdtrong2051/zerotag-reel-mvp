# UI Reference

Các màn hình UI design tham chiếu cho dashboard MVP:

1. Overview Dashboard
2. Component Inventory
3. Digital Component Passport
4. BOM Matching - Correct BOM
5. BOM Matching - Wrong Part
6. BOM Matching - Lot/Date-code Warning
7. Event Log
8. MSL Tracking
9. Anti-tamper & Verification

Nguyên tắc khi build UI:

- UI chỉ gọi backend API.
- UI không xử lý nghiệp vụ BOM.
- UI không đọc database trực tiếp.
- UI hiển thị trạng thái từ backend response.
- Màu trạng thái:
  - Xanh: hợp lệ
  - Đỏ: lỗi
  - Vàng: cảnh báo
  - Xám/trắng: thông tin bình thường
