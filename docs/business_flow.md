# Luồng nghiệp vụ ZeroTag-Reel MVP

## 1. Mục đích tài liệu

Tài liệu này mô tả các luồng nghiệp vụ chính của ZeroTag-Reel MVP.

Mỗi luồng xác định:

* Tác nhân thực hiện
* Điều kiện trước
* Dữ liệu đầu vào
* Các bước xử lý
* Thay đổi trạng thái component/reel
* ScanTransaction và Event phát sinh
* Kết quả trả về Dashboard hoặc Gateway
* Trường hợp ngoại lệ

Mọi nguồn scan đều đi qua Backend API.

```text
Dashboard / Gateway Simulator / Gateway thật
→ POST /api/v1/scans
→ Backend xử lý nghiệp vụ
→ Database
→ Response + gateway_action
```

Một lần scan tạo:

```text
1 ScanTransaction
+ N Event
```

`ScanTransaction` lưu kết quả cuối cùng của lần scan.

`Event` lưu từng bước chi tiết để tạo audit trail.

---

# 2. Khái niệm và trạng thái chung

## 2.1. Component status

Các trạng thái component/reel trong MVP:

```text
REGISTERED
IN_STOCK
ISSUED
BLOCKED
SCRAPPED
```

Ý nghĩa:

* `REGISTERED`: hồ sơ đã được tạo nhưng reel chưa được xác nhận nhập kho.
* `IN_STOCK`: reel đang có mặt trong kho và có thể được kiểm tra/cấp phát.
* `ISSUED`: reel đã được cấp cho khu vực hoặc dây chuyền sản xuất.
* `BLOCKED`: reel bị khóa do bất thường hoặc cần kiểm tra thủ công.
* `SCRAPPED`: reel bị loại bỏ khỏi vòng đời sử dụng.

`RETURNED` không được sử dụng làm trạng thái thường trực trong MVP.

Khi trả reel về kho:

```text
ISSUED → IN_STOCK
```

và hệ thống ghi event `RETURN_TO_STOCK`.

---

## 2.2. Scan mode

MVP sử dụng bốn scan mode:

```text
INBOUND
BOM_CHECK
RETURN
VERIFY
```

---

## 2.3. Scan result

Các kết quả scan cấp cao:

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

## 2.4. Gateway action

Backend trả về hành động cho Gateway:

```text
GREEN + SHORT_BEEP
RED + LONG_BEEP
YELLOW + DOUBLE_BEEP
OFF + NONE
```

Ý nghĩa:

* `GREEN + SHORT_BEEP`: xử lý hợp lệ.
* `RED + LONG_BEEP`: lỗi hoặc bị từ chối.
* `YELLOW + DOUBLE_BEEP`: cảnh báo cần kiểm tra.
* `OFF + NONE`: trạng thái chờ.

---

# 3. Luồng INBOUND — Nhập reel vào kho

## 3.1. Mục tiêu

Xác nhận reel đã có mặt trong kho vật lý và sẵn sàng tham gia workflow quản lý.

## 3.2. Tác nhân

* Nhân viên kho
* Dashboard Scan Input
* ZeroGateway hoặc Gateway Simulator

## 3.3. Điều kiện trước

* Gateway tồn tại và đang được phép gửi dữ liệu.
* Component đã được đăng ký trong hệ thống.
* Component không ở trạng thái `SCRAPPED`.
* Component không ở trạng thái `BLOCKED`.

## 3.4. Dữ liệu đầu vào

```text
request_id
gateway_id
mode = INBOUND
location
zerotag_id hoặc tag_uid
read_at
```

## 3.5. Luồng chính

1. Gateway hoặc Dashboard gửi scan request.
2. Backend validate request.
3. Backend tìm component theo `zerotag_id` hoặc `tag_uid`.
4. Backend kiểm tra trạng thái hiện tại.
5. Nếu component đang ở trạng thái `REGISTERED`, chuyển sang `IN_STOCK`.
6. Backend tạo một ScanTransaction.
7. Backend ghi các Event liên quan.
8. Backend trả kết quả hợp lệ.

## 3.6. Chuyển trạng thái

```text
REGISTERED → IN_STOCK
```

Nếu reel đã ở trạng thái `IN_STOCK`:

```text
IN_STOCK → IN_STOCK
```

Hệ thống không tạo thêm component mới.

## 3.7. Event phát sinh

```text
REEL_SCANNED
WAREHOUSE_IN
```

## 3.8. Kết quả

```text
status: VALID
led: GREEN
buzzer: SHORT_BEEP
```

## 3.9. Trường hợp ngoại lệ

### Tag không tồn tại

```text
status: UNKNOWN_TAG
```

Không thay đổi trạng thái component.

Event:

```text
REEL_SCANNED
UNKNOWN_TAG
```

### Tag đã bị khóa

```text
status: BLOCKED_TAG
```

Component tiếp tục ở trạng thái `BLOCKED`.

### Component đã bị loại bỏ

Component ở trạng thái `SCRAPPED` không được nhập lại bằng luồng INBOUND.

Backend từ chối thao tác và không thay đổi trạng thái.

---

# 4. Luồng BOM_CHECK — Kiểm tra reel đúng BOM

## 4.1. Mục tiêu

Kiểm tra một reel với một dòng BOM cụ thể trước khi cấp phát cho sản xuất.

## 4.2. Tác nhân

* Nhân viên kho
* Nhân viên cấp phát SMT
* Dashboard
* ZeroGateway hoặc Gateway Simulator

## 4.3. Điều kiện trước

* Component tồn tại.
* Component ở trạng thái `IN_STOCK`.
* Component không bị `BLOCKED`.
* BOM tồn tại và đang hoạt động.
* Dòng BOM tồn tại.

## 4.4. Xác định dòng BOM

BOM_CHECK sử dụng:

```text
bom_code + bom_ref
```

Ví dụ:

```text
bom_code: PCB-DEMO-01
bom_ref: R12
```

Backend sử dụng hai giá trị này để xác định đúng dòng BOM cần kiểm tra.

`bom_item_id` chỉ dùng nội bộ trong database.

## 4.5. Dữ liệu đầu vào

```text
request_id
gateway_id
mode = BOM_CHECK
location
zerotag_id hoặc tag_uid
bom_code
bom_ref
read_at
```

## 4.6. Thứ tự xử lý

Backend thực hiện theo thứ tự:

```text
1. Validate request
2. Kiểm tra gateway
3. Tìm component
4. Kiểm tra trạng thái BLOCKED
5. Tìm BOM
6. Tìm dòng BOM theo bom_code + bom_ref
7. So sánh part number
8. So sánh lot
9. So sánh date-code
10. Kiểm tra quantity khả dụng
11. Tạo ScanTransaction
12. Ghi Event
13. Trả response
```

## 4.7. Chuyển trạng thái

BOM_CHECK chỉ kiểm tra, không tự động cấp phát:

```text
IN_STOCK → IN_STOCK
```

Sau khi BOM_CHECK trả `VALID`, người vận hành có thể thực hiện thao tác xác nhận cấp phát riêng:

```text
IN_STOCK → ISSUED
```

Thao tác xác nhận cấp phát không phải một scan mode trong MVP hiện tại.

---

# 5. BOM_CHECK hợp lệ

## 5.1. Điều kiện hợp lệ

* Part number đúng.
* Lot đúng.
* Date-code nằm trong khoảng cho phép.
* Component không bị khóa.
* Quantity khả dụng được hiển thị để người vận hành kiểm tra.

Trong MVP v0.1, quantity không tạo một scan result riêng.

Nếu quantity không đủ, thao tác xác nhận cấp phát phải bị chặn hoặc yêu cầu người vận hành xử lý thủ công.

## 5.2. Event phát sinh

```text
REEL_SCANNED
BOM_CHECK_STARTED
BOM_MATCH_OK
```

## 5.3. Kết quả

```text
status: VALID
led: GREEN
buzzer: SHORT_BEEP
```

Component vẫn ở trạng thái:

```text
IN_STOCK
```

---

# 6. BOM_CHECK sai part number

## 6.1. Điều kiện

Part number của reel không khớp với part number yêu cầu tại `bom_ref`.

Ví dụ:

```text
BOM: PCB-DEMO-01
BOM Ref: R12
Required Part: RES-10K-0603
Scanned Part: CAP-10UF-0805
```

## 6.2. Event phát sinh

```text
REEL_SCANNED
BOM_CHECK_STARTED
BOM_MATCH_FAIL
WARNING_ISSUED
```

## 6.3. Kết quả

```text
status: WRONG_PART
led: RED
buzzer: LONG_BEEP
```

## 6.4. Chuyển trạng thái

Không thay đổi trạng thái:

```text
IN_STOCK → IN_STOCK
```

---

# 7. BOM_CHECK đúng part nhưng sai lot

## 7.1. Điều kiện

* Part number đúng.
* Lot của reel không nằm trong lot được phép.

Ví dụ:

```text
Required Lot: L2026A01
Scanned Lot: L2025X09
```

## 7.2. Event phát sinh

```text
REEL_SCANNED
BOM_CHECK_STARTED
LOT_MISMATCH
WARNING_ISSUED
```

## 7.3. Kết quả

```text
status: LOT_MISMATCH
led: YELLOW
buzzer: DOUBLE_BEEP
```

## 7.4. Chuyển trạng thái

Không thay đổi trạng thái:

```text
IN_STOCK → IN_STOCK
```

---

# 8. BOM_CHECK đúng part và lot nhưng sai date-code

## 8.1. Điều kiện

* Part number đúng.
* Lot đúng.
* Date-code nằm ngoài khoảng được cho phép.

Ví dụ:

```text
Allowed Date-code: 2520–2540
Scanned Date-code: 2518
```

## 8.2. Event phát sinh

```text
REEL_SCANNED
BOM_CHECK_STARTED
DATECODE_MISMATCH
WARNING_ISSUED
```

## 8.3. Kết quả

```text
status: DATECODE_MISMATCH
led: YELLOW
buzzer: DOUBLE_BEEP
```

## 8.4. Chuyển trạng thái

Không thay đổi trạng thái:

```text
IN_STOCK → IN_STOCK
```

---

# 9. Nhiều điều kiện không hợp lệ cùng lúc

Một reel có thể sai cả lot và date-code.

Backend vẫn trả một `status` chính, đồng thời response có thể chứa danh sách `violations`.

Ví dụ:

```json
{
  "status": "LOT_MISMATCH",
  "violations": [
    "LOT_MISMATCH",
    "DATECODE_MISMATCH"
  ]
}
```

Trong MVP, không sử dụng scan result riêng:

```text
LOT_AND_DATECODE_MISMATCH
```

Mục tiêu là giữ danh sách scan result cấp cao ổn định nhưng không làm mất thông tin chi tiết.

---

# 10. Luồng UNKNOWN_TAG

## 10.1. Điều kiện

Backend không thể tìm thấy component từ các mã nhận diện được gửi lên.

## 10.2. Xử lý

1. Backend vẫn tạo ScanTransaction.
2. Backend không tạo hoặc tự động đăng ký component mới.
3. Backend ghi Event cảnh báo.
4. Backend trả kết quả `UNKNOWN_TAG`.

## 10.3. Event phát sinh

```text
REEL_SCANNED
UNKNOWN_TAG
WARNING_ISSUED
```

## 10.4. Kết quả

```text
status: UNKNOWN_TAG
led: RED
buzzer: LONG_BEEP
```

## 10.5. Chuyển trạng thái

Không có component để thay đổi trạng thái.

---

# 11. Luồng RETURN — Trả reel về kho

## 11.1. Mục tiêu

Đưa reel đã cấp cho sản xuất trở lại trạng thái có sẵn trong kho.

## 11.2. Tác nhân

* Nhân viên kho
* Nhân viên sản xuất
* Dashboard
* ZeroGateway hoặc Gateway Simulator

## 11.3. Điều kiện trước

* Component tồn tại.
* Component đang ở trạng thái `ISSUED`.
* Component không bị `BLOCKED`.
* Component chưa bị `SCRAPPED`.

## 11.4. Dữ liệu đầu vào

```text
request_id
gateway_id
mode = RETURN
location
zerotag_id hoặc tag_uid
read_at
```

## 11.5. Luồng chính

1. Backend validate request.
2. Backend tìm component.
3. Backend kiểm tra component đang ở trạng thái `ISSUED`.
4. Backend chuyển trạng thái sang `IN_STOCK`.
5. Backend cập nhật vị trí kho nếu request có location.
6. Backend tạo ScanTransaction.
7. Backend ghi Event.
8. Backend trả kết quả hợp lệ.

## 11.6. Chuyển trạng thái

```text
ISSUED → IN_STOCK
```

## 11.7. Event phát sinh

```text
REEL_SCANNED
RETURN_TO_STOCK
```

## 11.8. Kết quả

```text
status: VALID
led: GREEN
buzzer: SHORT_BEEP
```

## 11.9. Trạng thái không hợp lệ

Nếu component không ở trạng thái `ISSUED`, backend từ chối RETURN.

Ví dụ:

```text
IN_STOCK → RETURN
```

Không thay đổi trạng thái.

Lỗi này thuộc nhóm business error, không cần thêm một scan result mới trong Day 1.

---

# 12. Luồng VERIFY — Xác thực tag

## 12.1. Mục tiêu

Kiểm tra tính nhất quán giữa QR/DataMatrix, RFID và hồ sơ số.

## 12.2. Tác nhân

* Nhân viên kho
* Nhân viên kiểm tra
* Dashboard
* ZeroGateway hoặc Gateway Simulator

## 12.3. Dữ liệu đầu vào

```text
request_id
gateway_id
mode = VERIFY
location
zerotag_id
tag_uid
qr_id
rfid_id
read_at
```

## 12.4. Xác thực thành công

Điều kiện:

* Component tồn tại.
* QR ID và RFID ID cùng ánh xạ về một ZeroTag ID.
* Component không bị blocked.
* Không có tamper warning.

Event:

```text
REEL_SCANNED
VERIFICATION_PASSED
```

Kết quả:

```text
status: VALID
led: GREEN
buzzer: SHORT_BEEP
```

Không thay đổi trạng thái:

```text
IN_STOCK → IN_STOCK
ISSUED → ISSUED
```

---

## 12.5. QR/RFID không khớp

Điều kiện:

```text
qr_id != rfid_id
```

hoặc hai mã ánh xạ về hai component khác nhau.

Event:

```text
REEL_SCANNED
VERIFICATION_FAILED
TAG_BLOCKED
```

Kết quả:

```text
status: QR_RFID_MISMATCH
led: RED
buzzer: LONG_BEEP
```

Chuyển trạng thái:

```text
REGISTERED / IN_STOCK / ISSUED
→ BLOCKED
```

---

## 12.6. Tamper warning

Điều kiện:

* Tag có trạng thái nghi ngờ bóc/tráo.
* UID vật lý không khớp với hồ sơ đã đăng ký.
* Dữ liệu verification chỉ ra bất thường khác.

Event:

```text
REEL_SCANNED
VERIFICATION_FAILED
TAMPER_WARNING
TAG_BLOCKED
```

Kết quả:

```text
status: TAMPER_WARNING
led: RED
buzzer: LONG_BEEP
```

Chuyển trạng thái:

```text
REGISTERED / IN_STOCK / ISSUED
→ BLOCKED
```

---

## 12.7. Tag đã bị khóa

Nếu component đã ở trạng thái `BLOCKED`:

```text
BLOCKED → BLOCKED
```

Event:

```text
REEL_SCANNED
BLOCKED_TAG
```

Kết quả:

```text
status: BLOCKED_TAG
led: RED
buzzer: LONG_BEEP
```

---

# 13. Luồng xác nhận cấp phát sau BOM_CHECK

## 13.1. Mục tiêu

Chuyển reel từ kho sang trạng thái đã cấp cho sản xuất sau khi BOM_CHECK hợp lệ.

## 13.2. Điều kiện trước

* BOM_CHECK gần nhất trả `VALID`.
* Component đang ở trạng thái `IN_STOCK`.
* Quantity khả dụng đủ cho quantity yêu cầu.
* Component không bị `BLOCKED`.

## 13.3. Chuyển trạng thái

```text
IN_STOCK → ISSUED
```

## 13.4. Event phát sinh

```text
COMPONENT_ISSUED
```

## 13.5. Phạm vi MVP

Đây là thao tác xác nhận của người vận hành, không phải scan mode riêng trong bốn mode hiện tại.

API chi tiết cho thao tác này sẽ được quyết định ở giai đoạn triển khai backend.

---

# 14. Luồng MSL Tracking

## 14.1. Mục tiêu

Đánh giá tình trạng floor life của component nhạy ẩm.

## 14.2. Dữ liệu sử dụng

```text
msl_level
bag_open_time
floor_life_limit_hours
floor_life_used_hours
```

## 14.3. Trạng thái MSL

```text
NORMAL
WARNING
NEED_BAKE
```

Quy tắc MVP:

```text
floor_life_used < 80% limit
→ NORMAL

80% limit ≤ floor_life_used < 100% limit
→ WARNING

floor_life_used ≥ 100% limit
→ NEED_BAKE
```

MSL status không phải scan result cấp cao.

MSL status được hiển thị trong MSL Tracking và Digital Component Passport.

---

# 15. Luồng Traceability

## 15.1. Mục tiêu

Truy xuất lịch sử của component/reel.

## 15.2. Tiêu chí tìm kiếm

* ZeroTag ID
* Part number
* Lot number
* Date-code

## 15.3. Kết quả trả về

* Thông tin component
* Trạng thái hiện tại
* Vị trí hiện tại
* ScanTransaction
* Event timeline
* BOM check history
* Verification history
* MSL status nếu có

Traceability là luồng truy vấn dữ liệu, không thay đổi trạng thái component.

---

# 16. Bảng tổng hợp chuyển trạng thái

| Nghiệp vụ              | Trạng thái trước               | Trạng thái sau |
| ---------------------- | ------------------------------ | -------------- |
| INBOUND                | REGISTERED                     | IN_STOCK       |
| INBOUND lặp            | IN_STOCK                       | IN_STOCK       |
| BOM_CHECK hợp lệ       | IN_STOCK                       | IN_STOCK       |
| BOM_CHECK không hợp lệ | IN_STOCK                       | IN_STOCK       |
| Confirm Issue          | IN_STOCK                       | ISSUED         |
| RETURN                 | ISSUED                         | IN_STOCK       |
| VERIFY hợp lệ          | IN_STOCK / ISSUED              | Không đổi      |
| QR_RFID_MISMATCH       | REGISTERED / IN_STOCK / ISSUED | BLOCKED        |
| TAMPER_WARNING         | REGISTERED / IN_STOCK / ISSUED | BLOCKED        |
| Scan BLOCKED_TAG       | BLOCKED                        | BLOCKED        |
| Admin scrap            | Bất kỳ trạng thái phù hợp      | SCRAPPED       |

---

# 17. Bảng tổng hợp luồng và event

| Luồng            | Event chính                                                        |
| ---------------- | ------------------------------------------------------------------ |
| INBOUND          | REEL_SCANNED, WAREHOUSE_IN                                         |
| BOM_CHECK hợp lệ | REEL_SCANNED, BOM_CHECK_STARTED, BOM_MATCH_OK                      |
| Sai part         | REEL_SCANNED, BOM_CHECK_STARTED, BOM_MATCH_FAIL, WARNING_ISSUED    |
| Sai lot          | REEL_SCANNED, BOM_CHECK_STARTED, LOT_MISMATCH, WARNING_ISSUED      |
| Sai date-code    | REEL_SCANNED, BOM_CHECK_STARTED, DATECODE_MISMATCH, WARNING_ISSUED |
| Unknown tag      | REEL_SCANNED, UNKNOWN_TAG, WARNING_ISSUED                          |
| RETURN           | REEL_SCANNED, RETURN_TO_STOCK                                      |
| VERIFY hợp lệ    | REEL_SCANNED, VERIFICATION_PASSED                                  |
| QR/RFID mismatch | REEL_SCANNED, VERIFICATION_FAILED, TAG_BLOCKED                     |
| Tamper warning   | REEL_SCANNED, VERIFICATION_FAILED, TAMPER_WARNING, TAG_BLOCKED     |
| Confirm Issue    | COMPONENT_ISSUED                                                   |

---

# 18. Quy tắc nhất quán

* Dashboard và Gateway không xử lý business rule.
* Mọi thay đổi trạng thái phải do Backend Service thực hiện.
* Mỗi scan phải tạo ScanTransaction.
* Event Log không được chỉnh sửa hoặc xóa trong workflow thông thường.
* Tag lạ không được tự động thêm vào database.
* BOM_CHECK phải xác định `bom_code + bom_ref`.
* BOM_CHECK không tự động chuyển component sang `ISSUED`.
* Verification bất thường chuyển component sang `BLOCKED`.
* `RETURNED` không được sử dụng làm trạng thái thường trực trong MVP.
* `SCRAPPED` chỉ được thay đổi bằng thao tác quản trị.
