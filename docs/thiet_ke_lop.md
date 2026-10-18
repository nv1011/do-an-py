# TÀI LIỆU THIẾT KẾ LỚP VÀ CHUẨN DỮ LIỆU JSON (CLASS DESIGN & JSON SCHEMA)

> **Dự án**: Phần mềm Quản lý Lịch hẹn Phòng khám (Clinic Appointment Management System)  
> **Công nghệ**: Python 3.10+, Tkinter / ttk, OOP (Lập trình hướng đối tượng), Lưu trữ JSON  
> **Thành viên nhóm**: Nhóm 3 người  
> **Tài liệu mục tiêu**: Chốt thuộc tính, kiểu dữ liệu từng lớp, quan hệ giữa các lớp và chuẩn JSON Schema lưu trữ dữ liệu.

---

> ### QUY TẮC PHỐI HỢP & NGUỒN CHUẨN CỦA DỰ ÁN
> 1. **Lớp đã chạy (`Nguoi`, `BenhNhan`, `BacSi`)**: **Code thực tế là nguồn chuẩn gốc (Code thắng)**, tài liệu thiết kế này được cập nhật hoàn toàn đồng bộ với code.
> 2. **Lớp sắp triển khai (`ChuyenKhoa`, `DichVu`, `LichHen`, `PhieuKham`, `TaiKhoan`)**: Tài liệu thiết kế này là đích kỹ thuật chuẩn mực để các thành viên dựa vào viết mã.
> 3. **Nguyên tắc "Một nguồn sự thật" (Single Source of Truth)**: Các thuộc tính tính toán / suy ra từ mã (`hoc_vi`, `nam_vao_lam`, `ngay_dang_ky`, `tong_tien`) không lưu dư thừa trong file JSON để tránh xung đột dữ liệu.

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG

Dự án áp dụng mô hình kiến trúc phân tầng (Layered Architecture):

```
+-------------------------------------------------------------+
|                     VIEWS (Giao diện Tkinter)               |
|  DangNhapView | MainWindow | TabBenhNhan | TabLichHen | ... |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   SERVICES (Tầng Xử lý Nghiệp vụ)           |
|  QuanLyTaiKhoan | QuanLyBenhNhan | QuanLyBacSi | ...        |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                      MODELS (Tầng Thực thể OOP)             |
|  Nguoi (ABC) -> BenhNhan, BacSi | ChuyenKhoa | LichHen | ...|
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|               JSON STORE (Lưu trữ và Truy xuất File)        |
|  data/*.json (benh_nhan, bac_si, lich_hen, phieu_kham, ...) |
+-------------------------------------------------------------+
```

- **Tính kế thừa & Trừu tượng**: `Nguoi` là lớp cơ sở trừu tượng (`ABC`), hai lớp `BenhNhan` và `BacSi` kế thừa và mở rộng.
- **Tính đóng gói**: Các thuộc tính cốt lõi được bảo vệ (`_attribute`), truy xuất và kiểm tra tính hợp lệ thông qua các `@property` và `@setter`.
- **Tuần tự hóa dữ liệu**: Mọi lớp Model đều cài đặt hai phương thức chuẩn:
  - `to_dict(self) -> dict`: Chuyển đối tượng thành từ điển để chuẩn bị ghi ra JSON.
  - `from_dict(cls, d: dict)`: Khởi tạo lại đối tượng từ dữ liệu từ điển đọc từ JSON.

---

## 2. SƠ ĐỒ QUAN HỆ LỚP (CLASS DIAGRAM)

```mermaid
classDiagram
    direction TB

    class Nguoi {
        <<Abstract>>
        #str _ma_dinh_danh
        #str _ho_ten
        #str _gioi_tinh
        #date _ngay_sinh
        #str _dia_chi
        #str _tinh_thanh
        #str _xa_phuong
        #str _sdt
        +ma_dinh_danh: str
        +ho_ten: str
        +gioi_tinh: str
        +ngay_sinh: date
        +tuoi: int
        +dia_chi: str
        +tinh_thanh: str
        +xa_phuong: str
        +dia_chi_day_du: str
        +sdt: str
        +to_dict()* dict
        +_truong_chung_tu_dict(d)$ dict
    }

    class BenhNhan {
        #str _so_bhyt
        #str _tien_su_benh
        #str _nhom_mau
        #str _email
        +so_bhyt: str
        +tien_su_benh: str
        +nhom_mau: str
        +email: str
        +ngay_dang_ky: date
        +to_dict() dict
        +from_dict(d)$ BenhNhan
    }

    class BacSi {
        #list _lich_lam_viec
        #float _luong_cb
        +ma_chuyen_khoa: str
        +hoc_vi: str
        +nam_vao_lam: int
        +lich_lam_viec: list
        +luong_cb: float
        +to_dict() dict
        +from_dict(d)$ BacSi
    }

    class ChuyenKhoa {
        -str ma_chuyen_khoa
        -str ten_chuyen_khoa
        -str mo_ta
        +to_dict() dict
        +from_dict(d)$ ChuyenKhoa
    }

    class DichVu {
        -str ma_dich_vu
        -str ten_dich_vu
        -str ma_chuyen_khoa
        -float don_gia
        -str mo_ta
        +to_dict() dict
        +from_dict(d)$ DichVu
    }

    class LichHen {
        -str ma_lich_hen
        -str ma_benh_nhan
        -str ma_bac_si
        -date ngay_hen
        -str gio_bat_dau
        -int thoi_luong
        -str trang_thai
        -str ly_do_kham
        +gio_ket_thuc: str
        +kiem_tra_trung_lich(lich_khac) bool
        +to_dict() dict
        +from_dict(d)$ LichHen
    }

    class PhieuKham {
        -str ma_phieu_kham
        -str ma_lich_hen
        -str ma_benh_nhan
        -str ma_bac_si
        -date ngay_kham
        -str trieu_chung
        -str chan_doan
        -list danh_sach_dich_vu
        -list don_thuoc
        -str loi_dan
        -date ngay_tai_kham
        -str trang_thai_kham
        -str trang_thai_thanh_toan
        +tong_tien: float
        +to_dict() dict
        +from_dict(d)$ PhieuKham
    }

    class TaiKhoan {
        -str ten_dang_nhap
        -str mat_khau_hash
        -str salt
        -str vai_tro
        -bool trang_thai
        -date ngay_tao
        +xac_thuc(mat_khau_nhap) bool
        +to_dict() dict
        +from_dict(d)$ TaiKhoan
    }

    Nguoi <|-- BenhNhan : Kế thừa
    Nguoi <|-- BacSi : Kế thừa
    BacSi --> ChuyenKhoa : Thuộc chuyên khoa (ma_chuyen_khoa)
    DichVu --> ChuyenKhoa : Thuộc chuyên khoa (ma_chuyen_khoa)
    LichHen --> BenhNhan : Đặt cho (ma_benh_nhan)
    LichHen --> BacSi : Đặt với (ma_bac_si)
    PhieuKham --> BenhNhan : Khám cho (ma_benh_nhan)
    PhieuKham --> BacSi : Bác sĩ phụ trách (ma_bac_si)
    PhieuKham --> LichHen : Tạo từ lịch hẹn (ma_lich_hen)
    PhieuKham o-- DichVu : Chứa danh sách dịch vụ
```

---

## 3. ĐẶC TẢ CHI TIẾT THUỘC TÍNH VÀ KIỂU DỮ LIỆU CÁC LỚP MODEL

### 3.1. Lớp Trừu tượng `Nguoi` (`models/nguoi.py`)
Lớp trừu tượng định nghĩa các thông tin cơ bản của một cá nhân trong hệ thống phòng khám.

| Thuộc tính nội bộ | Property | Kiểu Python | Kiểu JSON | Ràng buộc / Validation | Mô tả |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `_ma_dinh_danh` | `ma_dinh_danh` | `str` | `string` | Bắt buộc, không rỗng *(tính duy nhất do Service kiểm tra)* | Mã định danh duy nhất |
| `_ho_ten` | `ho_ten` | `str` | `string` | Không được rỗng sau khi `strip()` | Họ và tên đầy đủ |
| `_gioi_tinh` | `gioi_tinh` | `str` | `string` | Một trong: `"Nam"`, `"Nữ"` hoặc `"Khác"` | Giới tính |
| `_ngay_sinh` | `ngay_sinh` | `date` | `string` (`YYYY-MM-DD`) | Hợp lệ, không lớn hơn ngày hiện tại | Ngày sinh |
| `_dia_chi` | `dia_chi` | `str` | `string` | Chuỗi văn bản tự do | Địa chỉ số nhà, tên đường |
| `_tinh_thanh` | `tinh_thanh` | `str` | `string` | Không được để trống | Tỉnh hoặc Thành phố |
| `_xa_phuong` | `xa_phuong` | `str` | `string` | Không được để trống | Phường, Xã hoặc Thị trấn |
| `_sdt` | `sdt` | `str` | `string` | Regex `^0\d{9}$` (đúng 10 số, bắt đầu bằng `0`) | Số điện thoại di động |

**Thuộc tính tính toán (Read-only Computed Properties):**
- `tuoi -> int`: Tính toán từ `_ngay_sinh` so với `date.today()`.
- `dia_chi_day_du -> str`: Ghép chuỗi `f"{_dia_chi}, {_xa_phuong}, {_tinh_thanh}"`.

**Phương thức:**
- `to_dict(self) -> dict`: *(Abstract method)* Tuần tự hóa các trường chung.
- `_truong_chung_tu_dict(d: dict) -> dict`: *(Static method)* Trích xuất trường chung và chuyển đổi chuỗi ngày ISO sang `date`.

---

### 3.2. Lớp `BenhNhan` (`models/benh_nhan.py`)
Kế thừa từ `Nguoi`, quản lý thông tin hành chính và hồ sơ y tế cơ bản của bệnh nhân.

| Thuộc tính | Kiểu Python | Kiểu JSON | Ràng buộc / Validation | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| *Thuộc tính kế thừa* | Xem lớp `Nguoi` | - | - | Các thuộc tính kế thừa từ `Nguoi` |
| `_so_bhyt` | `str` | `string` | Regex `^[A-Z]{2}\d{13}$` hoặc `"Không có"` | Số thẻ bảo hiểm y tế |
| `_tien_su_benh` | `str` | `string` | Chuỗi văn bản (Mặc định `"Không có"`) | Tiền sử bệnh án, dị ứng thuốc |
| `_nhom_mau` | `str` | `string` | Thuộc: `"A"`, `"B"`, `"AB"`, `"O"`, `"Chưa rõ"` | Nhóm máu bệnh nhân |
| `_email` | `str` | `string` | Regex email hợp lệ (hoặc rỗng) | Địa chỉ email để nhận thông báo |

**Quy chuẩn Mã bệnh nhân (`ma_dinh_danh`):**
- Định dạng: Chuỗi đúng 14 chữ số (`re.fullmatch(r"\d{14}", ma)`).
- 8 chữ số đầu tiên: Ngày đăng ký tạo hồ sơ dạng `DDMMYYYY` (được kiểm tra hợp lệ bằng `datetime.strptime`).
- 6 chữ số sau: Số thứ tự tiếp nhận bệnh nhân trong ngày.
- **Thuộc tính tính toán**: `ngay_dang_ky -> date` (tự động giải mã từ 8 chữ số đầu, không lưu thừa vào JSON).

**Phương thức:**
- `to_dict(self) -> dict`: Xuất từ điển thông tin bệnh nhân.
- `from_dict(cls, d: dict) -> BenhNhan`: Tạo đối tượng `BenhNhan` từ dữ liệu dict.

---

### 3.3. Lớp `BacSi` (`models/bac_si.py`)
Kế thừa từ `Nguoi`, lưu trữ thông tin đội ngũ bác sĩ, chuyên khoa, học vị và lịch trực.

| Thuộc tính | Kiểu Python | Kiểu JSON | Ràng buộc / Validation | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| *Thuộc tính kế thừa* | Xem lớp `Nguoi` | - | Họ tên **không lưu tiền tố học vị** (chỉ lưu "Nguyễn Văn An") | Các thuộc tính từ `Nguoi` |
| `_lich_lam_viec` | `list[str]` | `array[string]` | Danh sách các ca trực (VD: `["T2_SANG", "T4_CHIEU"]`) | Lịch trực trong tuần |
| `_luong_cb` | `float` | `number` | Giá trị >= 0 | Mức lương cơ bản (VND) |

**Quy chuẩn Mã bác sĩ (`ma_dinh_danh`):**
- Định dạng: Đúng 9 chữ số (`re.fullmatch(r"\d{9}", ma)`).
  - Vị trí `0:2` (2 số đầu): Mã học vị (Tra cứu từ `config.HOC_VI`: `"01"` -> `"TS"`, `"02"` -> `"ThS"`, `"03"` -> `"BS"`).
  - Vị trí `2:4` (2 số tiếp theo): Mã chuyên khoa (`ma_chuyen_khoa`).
  - Vị trí `4:6` (2 số tiếp theo): 2 số cuối của năm vào làm (suy ra năm 4 chữ số thông qua `nam_tu_ma_bac_si`).
  - Vị trí `6:9` (3 số cuối): Số thứ tự bác sĩ.

**Thuộc tính tính toán (Read-only Computed Properties):**
- `ma_chuyen_khoa -> str`: Trích xuất `ma_dinh_danh[2:4]`.
- `hoc_vi -> str`: Tra cứu tên học vị theo `config.HOC_VI`.
- `nam_vao_lam -> int`: Trích xuất năm 4 chữ số từ mã bác sĩ qua `nam_tu_ma_bac_si`.

**Phương thức:**
- `to_dict(self) -> dict`
- `from_dict(cls, d: dict) -> BacSi`

---

### 3.4. Lớp `ChuyenKhoa` (`models/chuyen_khoa.py`)
Đại diện cho các phòng chuyên khoa y tế trong phòng khám.

| Thuộc tính | Kiểu Python | Kiểu JSON | Ràng buộc / Validation | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `ma_chuyen_khoa` | `str` | `string` | Đúng 2 chữ số (VD: `"01"`, `"02"`), duy nhất | Mã chuyên khoa định danh |
| `ten_chuyen_khoa` | `str` | `string` | Không được rỗng (VD: "Nội khoa", "Nhi khoa") | Tên gọi chuyên khoa |
| `mo_ta` | `str` | `string` | Chuỗi văn bản | Mô tả chức năng và phạm vi khám |

**Phương thức:**
- `to_dict(self) -> dict`
- `from_dict(cls, d: dict) -> ChuyenKhoa`

---

### 3.5. Lớp `DichVu` (`models/dich_vu.py`)
Đại diện cho các dịch vụ y tế, khám lâm sàng, xét nghiệm và chẩn đoán hình ảnh.

| Thuộc tính | Kiểu Python | Kiểu JSON | Ràng buộc / Validation | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `ma_dich_vu` | `str` | `string` | Tiền tố `"DV"` + 3 số (VD: `"DV001"`), duy nhất | Mã dịch vụ khám bệnh |
| `ten_dich_vu` | `str` | `string` | Không được rỗng | Tên dịch vụ (VD: "Khám lâm sàng nội khoa") |
| `ma_chuyen_khoa` | `str` | `string` | Khóa ngoại tham chiếu `ChuyenKhoa` | Chuyên khoa cung cấp |
| `don_gia` | `float` | `number` | Giá trị >= 0 | Đơn giá niêm yết (VND) |
| `mo_ta` | `str` | `string` | Chuỗi văn bản | Ghi chú yêu cầu thực hiện |

**Phương thức:**
- `to_dict(self) -> dict`
- `from_dict(cls, d: dict) -> DichVu`

---

### 3.6. Lớp `LichHen` (`models/lich_hen.py`)
Đại diện cho lịch hẹn đặt trước của bệnh nhân với bác sĩ (quản lý khung giờ và điều phối).

| Thuộc tính | Kiểu Python | Kiểu JSON | Ràng buộc / Validation | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `ma_lich_hen` | `str` | `string` | Tiền tố `"LH"` + số (VD: `"LH001"`), duy nhất | Mã số lịch hẹn |
| `ma_benh_nhan` | `str` | `string` | Khóa ngoại tham chiếu `BenhNhan.ma_dinh_danh` | Bệnh nhân đặt lịch |
| `ma_bac_si` | `str` | `string` | Khóa ngoại tham chiếu `BacSi.ma_dinh_danh` | Bác sĩ phụ trách |
| `ngay_hen` | `date` | `string` (`YYYY-MM-DD`) | Hợp lệ *(ràng buộc >= hôm nay do Service kiểm tra khi tạo mới)* | Ngày hẹn khám |
| `gio_bat_dau` | `str` | `string` (`HH:MM`) | Định dạng 24h từ `config.GIO_BAT_DAU_KHAM` đến `config.GIO_KET_THUC_KHAM` | Giờ bắt đầu ca khám |
| `thoi_luong` | `int` | `integer` | Bội số 15 phút, > 0 (VD: 30, 45, 60) | Thời lượng dự kiến (phút) |
| `trang_thai` | `str` | `string` | `"Cho_kham"`, `"Da_kham"`, `"Da_huy"`, `"Vang"` | Trạng thái của lịch hẹn |
| `ly_do_kham` | `str` | `string` | Chuỗi văn bản | Triệu chứng ban đầu |

**Thuộc tính tính toán (Computed Properties):**
- `gio_ket_thuc -> str`: Cộng `thoi_luong` phút vào `gio_bat_dau` (VD: `08:00` + 30 phút -> `08:30`).

**Quy tắc kiểm tra trùng lịch (`kiem_tra_trung_lich`):**
- Chỉ xét các lịch hẹn có cùng bác sĩ và cùng ngày.
- **Bỏ qua các lịch hẹn đã hủy hoặc vắng mặt (`trang_thai in ("Da_huy", "Vang")`)**.
- **Bỏ qua chính mã lịch hẹn đang chỉnh sửa** (để người dùng có thể cập nhật thông tin khác mà không tự báo trùng với chính mình).
- Điều kiện xung đột thời gian giữa 2 ca:
  `max(bat_dau_1, bat_dau_2) < min(ket_thuc_1, ket_thuc_2)`

**Phương thức:**
- `to_dict(self) -> dict`
- `from_dict(cls, d: dict) -> LichHen`

---

### 3.7. Lớp `PhieuKham` (`models/phieu_kham.py`)
Đại diện cho phiếu khám bệnh ghi nhận kết quả chuyên môn, chỉ định dịch vụ, đơn thuốc và thanh toán.

| Thuộc tính | Kiểu Python | Kiểu JSON | Ràng buộc / Validation | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `ma_phieu_kham` | `str` | `string` | Tiền tố `"PK"` + số (VD: `"PK001"`), duy nhất | Mã số phiếu khám bệnh |
| `ma_lich_hen` | `str \| None` | `string \| null` | Khóa ngoại tham chiếu `LichHen` (nếu có) | Mã lịch hẹn liên kết |
| `ma_benh_nhan` | `str` | `string` | Khóa ngoại tham chiếu `BenhNhan.ma_dinh_danh` | Bệnh nhân được khám |
| `ma_bac_si` | `str` | `string` | Khóa ngoại tham chiếu `BacSi.ma_dinh_danh` | Bác sĩ thực hiện khám |
| `ngay_kham` | `date` | `string` (`YYYY-MM-DD`) | Mặc định ngày tạo phiếu | Ngày khám bệnh |
| `trieu_chung` | `str` | `string` | Không để trống | Triệu chứng ban đầu |
| `chan_doan` | `str` | `string` | Có thể rỗng khi đang khám, bắt buộc khi hoàn tất | Kết luận chẩn đoán bệnh |
| `danh_sach_dich_vu` | `list[dict]` | `array[object]` | Gồm: `ma_dich_vu`, `ten_dich_vu`, `don_gia`, `so_luong` | Dịch vụ chỉ định (bao gồm khám lâm sàng) |
| `don_thuoc` | `list[dict]` | `array[object]` | Gồm: `ten_thuoc`, `don_vi`, `so_luong`, `cach_dung` | Toa thuốc điều trị |
| `loi_dan` | `str` | `string` | Chuỗi văn bản | Lời dặn dò của bác sĩ |
| `ngay_tai_kham` | `date \| None` | `string \| null` | Ngày hẹn tái khám (nếu có) | Lịch hẹn tái khám |
| `trang_thai_kham` | `str` | `string` | `"Dang_kham"` hoặc `"Hoan_thanh"` | Tiến độ ca khám |
| `trang_thai_thanh_toan`| `str` | `string` | `"Chua_thanh_toan"` hoặc `"Da_thanh_toan"` | Tình trạng thu ngân |

**Thuộc tính tính toán (Computed Properties):**
- `tong_tien -> float`: Tính tự động từ danh sách dịch vụ:
  $$\text{tong\_tien} = \sum (\text{don\_gia} \times \text{so\_luong})$$
  *(Tiền công khám được xem là một dịch vụ `DV001` nằm trong danh sách dịch vụ; không lưu `tien_kham` hay `tong_tien` cứng trong JSON để tránh đếm trùng).*

**Phương thức:**
- `to_dict(self) -> dict`
- `from_dict(cls, d: dict) -> PhieuKham`

---

### 3.8. Lớp `TaiKhoan` (`models/tai_khoan.py`)
Quản lý tài khoản đăng nhập và phân quyền hệ thống (bảo mật bằng mật khẩu băm có salt).

| Thuộc tính | Kiểu Python | Kiểu JSON | Ràng buộc / Validation | Mô tả |
| :--- | :--- | :--- | :--- | :--- |
| `ten_dang_nhap` | `str` | `string` | Duy nhất, >= 3 ký tự, không chứa dấu cách | Tên tài khoản |
| `mat_khau_hash` | `str` | `string` | Chuỗi SHA-256 (64 ký tự hex) | Mật khẩu đã băm kèm salt |
| `salt` | `str` | `string` | Chuỗi ngẫu nhiên 32 ký tự hex | Chuỗi muối chống tra từ điển |
| `vai_tro` | `str` | `string` | Đúng một trong 2 vai trò: `"admin"`, `"le_tan"` | Phân quyền sử dụng |
| `trang_thai` | `bool` | `boolean` | `True` (hoạt động), `False` (bị khóa) | Trạng thái tài khoản |
| `ngay_tao` | `date` | `string` (`YYYY-MM-DD`) | Ngày tạo tài khoản | Ngày cấp |

**Phương thức:**
- `xac_thuc(self, mat_khau_nhap: str) -> bool`: So khớp mã băm SHA-256 của `(mat_khau_nhap + self.salt)` với `self.mat_khau_hash`.
- `to_dict(self) -> dict`
- `from_dict(cls, d: dict) -> TaiKhoan`

---

## 4. TỔNG QUAN TẦNG DỊCH VỤ (SERVICES)

Chi tiết hợp đồng hàm giữa Services và Views được quy định tại file riêng [`docs/hop_dong_ham.md`](file:///c:/Others/Coding/Study/DoAnPython/docs/hop_dong_ham.md).

- **`JsonStore` (`services/json_store.py`)**: Đọc/ghi JSON an toàn với `with open`, atomic write qua file tạm, tự động sao lưu vào `backup/`.
- **`QuanLyBenhNhan` (`services/quan_ly_benh_nhan.py`)**: CRUD bệnh nhân, tìm kiếm gần đúng tiếng Việt không dấu qua `utils.helpers.khop`, sinh mã 14 số tự động.
- **`QuanLyBacSi` (`services/quan_ly_bac_si.py`)**: Quản lý thông tin bác sĩ, lọc theo khoa.
- **`QuanLyLichHen` (`services/quan_ly_lich_hen.py`)**: Lọc lịch hẹn cho Treeview và Thẻ lịch hẹn, kiểm tra trùng lịch (bỏ qua lịch hủy và lịch đang sửa), tìm bác sĩ rảnh theo ca.
- **`QuanLyPhieuKham` (`services/quan_ly_phieu_kham.py`)**: Lập phiếu khám ban đầu (`Dang_kham`), thêm dịch vụ, hoàn tất khám (`chan_doan` + đơn thuốc), thanh toán viện phí.
- **`QuanLyTaiKhoan` (`services/quan_ly_tai_khoan.py`)**: Xác thực đăng nhập bằng `utils.validators.xac_thuc_mat_khau`, đổi mật khẩu, phân quyền `admin` / `le_tan`.
- **`ThongKe` (`services/thong_ke.py`)**: Thống kê doanh thu, số ca khám theo bác sĩ phục vụ vẽ biểu đồ Canvas, xuất file `.csv`.

---

## 5. ĐẶC TẢ JSON SCHEMA CHO CÁC TẬP TIN DỮ LIỆU (DATA LAYER)

Toàn bộ các file trong thư mục `data/` tuân thủ JSON Schema chuẩn sau:

---

### 5.1. File `data/benh_nhan.json`

#### JSON Schema:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DanhSachBenhNhan",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "ma_dinh_danh",
      "ho_ten",
      "dia_chi",
      "tinh_thanh",
      "xa_phuong",
      "gioi_tinh",
      "ngay_sinh",
      "sdt",
      "so_bhyt",
      "tien_su_benh",
      "nhom_mau",
      "email"
    ],
    "properties": {
      "ma_dinh_danh": {
        "type": "string",
        "pattern": "^\\d{14}$",
        "description": "Mã bệnh nhân gồm 14 chữ số, 8 số đầu là ngày đăng ký dạng DDMMYYYY"
      },
      "ho_ten": {
        "type": "string",
        "minLength": 1
      },
      "dia_chi": {
        "type": "string"
      },
      "tinh_thanh": {
        "type": "string",
        "minLength": 1
      },
      "xa_phuong": {
        "type": "string",
        "minLength": 1
      },
      "gioi_tinh": {
        "type": "string",
        "enum": ["Nam", "Nữ"]
      },
      "ngay_sinh": {
        "type": "string",
        "format": "date"
      },
      "sdt": {
        "type": "string",
        "pattern": "^0\\d{9}$",
        "description": "Số điện thoại di động 10 số bắt đầu bằng 0"
      },
      "so_bhyt": {
        "type": "string"
      },
      "tien_su_benh": {
        "type": "string"
      },
      "nhom_mau": {
        "type": "string",
        "enum": ["A", "B", "AB", "O", "Chưa rõ"]
      },
      "email": {
        "type": "string"
      }
    }
  }
}
```

#### Dữ liệu mẫu (`data/benh_nhan.json`):
```json
[
  {
    "ma_dinh_danh": "12102026000001",
    "ho_ten": "Nguyễn Văn An",
    "dia_chi": "123 Cầu Giấy",
    "tinh_thanh": "Hà Nội",
    "xa_phuong": "Phường Dịch Vọng",
    "gioi_tinh": "Nam",
    "ngay_sinh": "1990-03-12",
    "sdt": "0912345678",
    "so_bhyt": "HN4010123456789",
    "tien_su_benh": "Viêm loét dạ dày",
    "nhom_mau": "O",
    "email": "nguyenvanan@gmail.com"
  },
  {
    "ma_dinh_danh": "12102026000002",
    "ho_ten": "Trần Thị Bình",
    "dia_chi": "45 Nguyễn Tri Phương",
    "tinh_thanh": "Đà Nẵng",
    "xa_phuong": "Phường Thạc Gián",
    "gioi_tinh": "Nữ",
    "ngay_sinh": "1985-07-25",
    "sdt": "0987654321",
    "so_bhyt": "DN4010987654321",
    "tien_su_benh": "Tăng huyết áp nhẹ",
    "nhom_mau": "A",
    "email": "binh.tran@mail.com"
  }
]
```

---

### 5.2. File `data/bac_si.json`

#### JSON Schema:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DanhSachBacSi",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "ma_dinh_danh",
      "ho_ten",
      "dia_chi",
      "tinh_thanh",
      "xa_phuong",
      "gioi_tinh",
      "ngay_sinh",
      "sdt",
      "lich_lam_viec",
      "luong_cb"
    ],
    "properties": {
      "ma_dinh_danh": {
        "type": "string",
        "pattern": "^\\d{9}$",
        "description": "Mã bác sĩ 9 số: 2 số học vị, 2 số chuyên khoa, 2 số năm vào làm, 3 số thứ tự"
      },
      "ho_ten": {
        "type": "string",
        "minLength": 1,
        "description": "Họ và tên bác sĩ (không kèm tiền tố học vị TS/BS)"
      },
      "dia_chi": { "type": "string" },
      "tinh_thanh": { "type": "string" },
      "xa_phuong": { "type": "string" },
      "gioi_tinh": { "type": "string", "enum": ["Nam", "Nữ"] },
      "ngay_sinh": { "type": "string", "format": "date" },
      "sdt": { "type": "string", "pattern": "^0\\d{9}$" },
      "lich_lam_viec": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Danh sách các ca trực (VD: 'T2_SANG', 'T4_CHIEU')"
      },
      "luong_cb": {
        "type": "number",
        "minimum": 0
      }
    }
  }
}
```

#### Dữ liệu mẫu (`data/bac_si.json`):
```json
[
  {
    "ma_dinh_danh": "010120001",
    "ho_ten": "Nguyễn Văn An",
    "dia_chi": "78 Đường Hai Bà Trưng",
    "tinh_thanh": "Hà Nội",
    "xa_phuong": "Phường Tràng Tiền",
    "gioi_tinh": "Nam",
    "ngay_sinh": "1978-05-15",
    "sdt": "0903123456",
    "lich_lam_viec": ["T2_SANG", "T4_SANG", "T6_SANG"],
    "luong_cb": 25000000
  },
  {
    "ma_dinh_danh": "030222002",
    "ho_ten": "Lê Thị Mai",
    "dia_chi": "120 Nguyễn Văn Linh",
    "tinh_thanh": "Đà Nẵng",
    "xa_phuong": "Phường Nam Dương",
    "gioi_tinh": "Nữ",
    "ngay_sinh": "1988-11-20",
    "sdt": "0918765432",
    "lich_lam_viec": ["T3_CHIEU", "T5_CHIEU", "T7_SANG"],
    "luong_cb": 18000000
  }
]
```

---

### 5.3. File `data/chuyen_khoa.json`

#### JSON Schema:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DanhSachChuyenKhoa",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["ma_chuyen_khoa", "ten_chuyen_khoa", "mo_ta"],
    "properties": {
      "ma_chuyen_khoa": {
        "type": "string",
        "pattern": "^\\d{2}$",
        "description": "Mã chuyên khoa gồm 2 chữ số (VD: '01', '02')"
      },
      "ten_chuyen_khoa": { "type": "string", "minLength": 1 },
      "mo_ta": { "type": "string" }
    }
  }
}
```

#### Dữ liệu mẫu (`data/chuyen_khoa.json`):
```json
[
  {
    "ma_chuyen_khoa": "01",
    "ten_chuyen_khoa": "Nội khoa",
    "mo_ta": "Khám và điều trị các bệnh lý tim mạch, tiêu hóa, hô hấp, nội tiết"
  },
  {
    "ma_chuyen_khoa": "02",
    "ten_chuyen_khoa": "Nhi khoa",
    "mo_ta": "Khám và điều trị các bệnh lý cho trẻ sơ sinh và trẻ em"
  }
]
```

---

### 5.4. File `data/dich_vu.json`

#### JSON Schema:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DanhSachDichVu",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["ma_dich_vu", "ten_dich_vu", "ma_chuyen_khoa", "don_gia", "mo_ta"],
    "properties": {
      "ma_dich_vu": {
        "type": "string",
        "pattern": "^DV\\d{3}$"
      },
      "ten_dich_vu": { "type": "string", "minLength": 1 },
      "ma_chuyen_khoa": { "type": "string", "pattern": "^\\d{2}$" },
      "don_gia": { "type": "number", "minimum": 0 },
      "mo_ta": { "type": "string" }
    }
  }
}
```

#### Dữ liệu mẫu (`data/dich_vu.json`):
```json
[
  {
    "ma_dich_vu": "DV001",
    "ten_dich_vu": "Khám lâm sàng nội khoa",
    "ma_chuyen_khoa": "01",
    "don_gia": 150000,
    "mo_ta": "Khám và tư vấn sức khỏe tổng quát với bác sĩ chuyên khoa"
  },
  {
    "ma_dich_vu": "DV002",
    "ten_dich_vu": "Nội soi Tai Mũi Họng",
    "ma_chuyen_khoa": "04",
    "don_gia": 250000,
    "mo_ta": "Nội soi ống mềm không đau chất lượng cao"
  }
]
```

---

### 5.5. File `data/lich_hen.json`

#### JSON Schema:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DanhSachLichHen",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "ma_lich_hen",
      "ma_benh_nhan",
      "ma_bac_si",
      "ngay_hen",
      "gio_bat_dau",
      "thoi_luong",
      "trang_thai",
      "ly_do_kham"
    ],
    "properties": {
      "ma_lich_hen": {
        "type": "string",
        "pattern": "^LH\\d{3,}$"
      },
      "ma_benh_nhan": { "type": "string", "pattern": "^\\d{14}$" },
      "ma_bac_si": { "type": "string", "pattern": "^\\d{9}$" },
      "ngay_hen": { "type": "string", "format": "date" },
      "gio_bat_dau": { "type": "string", "pattern": "^([01]\\d|2[0-3]):[0-5]\\d$" },
      "thoi_luong": { "type": "integer", "minimum": 15 },
      "trang_thai": {
        "type": "string",
        "enum": ["Cho_kham", "Da_kham", "Da_huy", "Vang"]
      },
      "ly_do_kham": { "type": "string" }
    }
  }
}
```

#### Dữ liệu mẫu (`data/lich_hen.json`):
```json
[
  {
    "ma_lich_hen": "LH001",
    "ma_benh_nhan": "12102026000002",
    "ma_bac_si": "010120001",
    "ngay_hen": "2026-10-12",
    "gio_bat_dau": "08:00",
    "thoi_luong": 30,
    "trang_thai": "Cho_kham",
    "ly_do_kham": "Khám định kỳ huyết áp"
  },
  {
    "ma_lich_hen": "LH002",
    "ma_benh_nhan": "12102026000003",
    "ma_bac_si": "010120001",
    "ngay_hen": "2026-10-12",
    "gio_bat_dau": "08:30",
    "thoi_luong": 30,
    "trang_thai": "Cho_kham",
    "ly_do_kham": "Đau bụng thượng vị"
  }
]
```

---

### 5.6. File `data/phieu_kham.json`

#### JSON Schema:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DanhSachPhieuKham",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "ma_phieu_kham",
      "ma_benh_nhan",
      "ma_bac_si",
      "ngay_kham",
      "trieu_chung",
      "chan_doan",
      "danh_sach_dich_vu",
      "don_thuoc",
      "trang_thai_kham",
      "trang_thai_thanh_toan"
    ],
    "properties": {
      "ma_phieu_kham": { "type": "string", "pattern": "^PK\\d{3,}$" },
      "ma_lich_hen": { "type": ["string", "null"] },
      "ma_benh_nhan": { "type": "string", "pattern": "^\\d{14}$" },
      "ma_bac_si": { "type": "string", "pattern": "^\\d{9}$" },
      "ngay_kham": { "type": "string", "format": "date" },
      "trieu_chung": { "type": "string" },
      "chan_doan": { "type": "string", "description": "Kết luận chẩn đoán (có thể rỗng khi đang khám)" },
      "danh_sach_dich_vu": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["ma_dich_vu", "ten_dich_vu", "don_gia", "so_luong"],
          "properties": {
            "ma_dich_vu": { "type": "string" },
            "ten_dich_vu": { "type": "string" },
            "don_gia": { "type": "number", "minimum": 0 },
            "so_luong": { "type": "integer", "minimum": 1 }
          }
        }
      },
      "don_thuoc": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["ten_thuoc", "don_vi", "so_luong", "cach_dung"],
          "properties": {
            "ten_thuoc": { "type": "string" },
            "don_vi": { "type": "string" },
            "so_luong": { "type": "integer", "minimum": 1 },
            "cach_dung": { "type": "string" }
          }
        }
      },
      "loi_dan": { "type": "string" },
      "ngay_tai_kham": { "type": ["string", "null"], "format": "date" },
      "trang_thai_kham": { "type": "string", "enum": ["Dang_kham", "Hoan_thanh"] },
      "trang_thai_thanh_toan": { "type": "string", "enum": ["Chua_thanh_toan", "Da_thanh_toan"] }
    }
  }
}
```

#### Dữ liệu mẫu (`data/phieu_kham.json`):
```json
[
  {
    "ma_phieu_kham": "PK001",
    "ma_lich_hen": "LH001",
    "ma_benh_nhan": "12102026000002",
    "ma_bac_si": "010120001",
    "ngay_kham": "2026-10-12",
    "trieu_chung": "Chóng mặt khi thay đổi tư thế, huyết áp đo 140/90",
    "chan_doan": "Tăng huyết áp vô căn độ 1",
    "danh_sach_dich_vu": [
      {
        "ma_dich_vu": "DV001",
        "ten_dich_vu": "Khám lâm sàng nội khoa",
        "don_gia": 150000,
        "so_luong": 1
      }
    ],
    "don_thuoc": [
      {
        "ten_thuoc": "Amlodipine 5mg",
        "don_vi": "Viên",
        "so_luong": 30,
        "cach_dung": "Uống 1 viên vào buổi sáng sau ăn"
      }
    ],
    "loi_dan": "Ăn giảm muối, hạn chế căng thẳng, đo huyết áp mỗi sáng",
    "ngay_tai_kham": "2026-11-12",
    "trang_thai_kham": "Hoan_thanh",
    "trang_thai_thanh_toan": "Da_thanh_toan"
  }
]
```

---

### 5.7. File `data/tai_khoan.json`

#### JSON Schema:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DanhSachTaiKhoan",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "ten_dang_nhap",
      "mat_khau_hash",
      "salt",
      "vai_tro",
      "trang_thai",
      "ngay_tao"
    ],
    "properties": {
      "ten_dang_nhap": {
        "type": "string",
        "minLength": 3
      },
      "mat_khau_hash": {
        "type": "string",
        "pattern": "^[a-f0-9]{64}$",
        "description": "Chuỗi băm SHA-256 của mật khẩu + salt"
      },
      "salt": {
        "type": "string",
        "pattern": "^[a-f0-9]{32}$",
        "description": "Chuỗi muối ngẫu nhiên"
      },
      "vai_tro": {
        "type": "string",
        "enum": ["admin", "le_tan"],
        "description": "Chốt đúng 2 vai trò theo yêu cầu đề tài"
      },
      "trang_thai": { "type": "boolean" },
      "ngay_tao": { "type": "string", "format": "date" }
    }
  }
}
```

#### Dữ liệu mẫu (`data/tai_khoan.json`):
```json
[
  {
    "ten_dang_nhap": "admin",
    "mat_khau_hash": "0f20fb336de567e7069f3c5b0208052f5a50fb1ce95275e2671dc8c411e21f28",
    "salt": "a1b2c3d4e5f60718293a4b5c6d7e8f90",
    "vai_tro": "admin",
    "trang_thai": true,
    "ngay_tao": "2026-10-01"
  },
  {
    "ten_dang_nhap": "letan",
    "mat_khau_hash": "b77120f022c2f09fcc575df436378256e471d42cec5240b3e9858444558af422",
    "salt": "f0e1d2c3b4a5968778695a4b3c2d1e0f",
    "vai_tro": "le_tan",
    "trang_thai": true,
    "ngay_tao": "2026-10-01"
  }
]
```

---

## 6. BẢNG TỔNG HỢP ÁNH XẠ THUỘC TÍNH VÀ KIỂU DỮ LIỆU

| Thực thể | File Mã nguồn | Khóa chính (PK) | Khóa ngoại (FK) | Lưu trữ JSON | Ghi chú tích hợp |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Nguoi` | `models/nguoi.py` | `_ma_dinh_danh` | Không | Không trực tiếp | Lớp cha trừu tượng (`ABC`) |
| `BenhNhan` | `models/benh_nhan.py` | `_ma_dinh_danh` | Không | `data/benh_nhan.json` | 14 số, validate BHYT & SĐT |
| `BacSi` | `models/bac_si.py` | `_ma_dinh_danh` | `ma_chuyen_khoa` (trong mã) | `data/bac_si.json` | 9 số, lịch trực dạng list ca |
| `ChuyenKhoa` | `models/chuyen_khoa.py` | `ma_chuyen_khoa` | Không | `data/chuyen_khoa.json` | 2 chữ số |
| `DichVu` | `models/dich_vu.py` | `ma_dich_vu` | `ma_chuyen_khoa` | `data/dich_vu.json` | Tiền tố `DV` |
| `LichHen` | `models/lich_hen.py` | `ma_lich_hen` | `ma_benh_nhan`, `ma_bac_si` | `data/lich_hen.json` | Tiền tố `LH` |
| `PhieuKham` | `models/phieu_kham.py` | `ma_phieu_kham` | `ma_lich_hen`, `ma_benh_nhan`, `ma_bac_si` | `data/phieu_kham.json` | Tiền tố `PK`, dùng `chan_doan` |
| `TaiKhoan` | `models/tai_khoan.py` | `ten_dang_nhap` | Không | `data/tai_khoan.json` | Hash + salt, 2 vai trò |

---

## 7. BẢNG PHÂN CHIA VAI TRÒ VÀ KẾ HOẠCH TRIỂN KHAI (NOTION TASK MATRIX)

Dựa trên bảng phân chia công việc chính thức của nhóm (theo dõi trên Notion), dự án phân bổ vai trò cụ thể cho 3 thành viên theo lộ trình từ Tuần 9 đến Tuần 14 như sau:

### 7.1. Định vị Trách nhiệm Cốt lõi của Từng Thành viên

| Thành viên | Trách nhiệm chính (Core Responsibility) | Phạm vi Module / Thư mục chính |
| :--- | :--- | :--- |
| **Thành viên A** | **Models, OOP, JSON Store, Logic Quản lý & Xác thực** | `models/`, `services/json_store.py`, `services/quan_ly_*.py`, `utils/validators.py`, Sơ đồ lớp |
| **Thành viên B** | **Giao diện người dùng (GUI / Tkinter), Custom Widgets & Trực quan hóa** | `views/`, `views/widgets/`, Luồng tương tác, Canvas biểu đồ, Bố cục giao diện |
| **Thành viên C** | **Hạ tầng dự án, API Ngoại vi, Kiểm thử (Testing), Thống kê & Báo cáo** | Setup Repo, `config.py`, `services/api_dia_chi.py`, `services/thong_ke.py`, `services/tao_du_lieu_mau.py`, `backup/`, Test cases, Đóng gói EXE |
| **Cả nhóm** | **Tích hợp hệ thống, Rà soát, Báo cáo & Thuyết trình** | Hợp đồng hàm, Ghép nhánh Git (Merge), Slide, Báo cáo Word/PDF, Tổng duyệt Demo |

---

### 7.2. Kế hoạch Chi tiết theo Từng Thành viên

#### 1. Thành viên A (Data Models, Logic Quản lý & Lưu trữ)
| Tuần | Tên công việc | Kết quả kỳ vọng | Priority | Trạng thái |
| :---: | :--- | :--- | :---: | :---: |
| **9** | Viết lớp JsonStore (đọc/ghi/sao lưu, bắt lỗi file) | File `services/json_store.py`: đọc/ghi bằng `with`, xử lý file thiếu/rỗng/sai định dạng, có sao lưu; chạy thử được với `benh_nhan.json` | High | Chưa làm |
| **9** | Viết lớp trừu tượng Nguoi, BenhNhan, BacSi (to_dict/from_dict) | `models/nguoi.py`, `models/benh_nhan.py`, `models/bac_si.py`; tạo được đối tượng hoàn chỉnh | High | Đang làm |
| **9** | Vẽ sơ đồ lớp bản nháp | `docs/so_do_lop_v0` (trên Draw.io) | Medium | Chưa làm |
| **9** | Chốt thuộc tính, kiểu dữ liệu từng lớp và JSON schema | `docs/thiet_ke_lop.md` và các file JSON mẫu hoàn chỉnh | High | Đang làm |
| **10** | TaiKhoan và đăng nhập 2 vai trò (băm mật khẩu có salt) | `services/quan_ly_tai_khoan.py`, `data/tai_khoan.json` mẫu (admin, le_tan) | High | Chưa làm |
| **10** | QuanLyBenhNhan: CRUD và tìm kiếm theo ≥ 2 tiêu chí | `services/quan_ly_benh_nhan.py`, chạy thử nghiệm thủ công được | High | Chưa làm |
| **10** | Cập nhật sơ đồ lớp v1 (thêm LichHen, TaiKhoan, lớp giao diện) | `docs/so_do_lop_v1` | High | Chưa làm |
| **10** | QuanLyBacSi: CRUD | `services/quan_ly_bac_si.py` | High | Chưa làm |
| **10** | LichHen và QuanLyLichHen có kiểm tra trùng lịch bác sĩ | `models/lich_hen.py`, `services/quan_ly_lich_hen.py`, chặn được lịch trùng | High | Chưa làm |
| **10** | `validators.py`: Regex số điện thoại và mã BHYT | `utils/validators.py` kèm các ví dụ kiểm tra đúng/sai | High | Chưa làm |
| **11** | Đổi mật khẩu và quản lý tài khoản đầy đủ (admin tạo/khóa tài khoản) | Chức năng đổi mật khẩu, mật khẩu luôn lưu dạng băm an toàn | Medium | Chưa làm |
| **11** | PhieuKham, DichVu và QuanLyPhieuKham (ghi nội dung khám, dịch vụ, tính tiền) | `models/phieu_kham.py`, `models/dich_vu.py`, `services/quan_ly_phieu_kham.py`; tạo phiếu và tính tổng tiền đúng | High | Chưa làm |
| **12** | Rà soát validators và ràng buộc dữ liệu (trùng mã, số âm, ngày không hợp lệ) | Danh sách ràng buộc đã kiểm tra, mỗi lỗi có thông báo rõ ràng | High | Chưa làm |
| **13** | Hoàn thiện sơ đồ lớp và bảng mô tả lớp, thuộc tính, phương thức | `docs/so_do_lop_final` và bảng mô tả đưa vào báo cáo | High | Chưa làm |
| **13** | Kiểm thử logic: file JSON mất/rỗng/sai định dạng, trùng mã, dữ liệu rỗng | Mỗi tình huống có test case và kết quả thực tế trong bảng kiểm thử | High | Chưa làm |
| **13** | Viết chương Thiết kế lớp và dữ liệu JSON của báo cáo | Chương báo cáo hoàn chỉnh kèm sơ đồ lớp chi tiết | High | Chưa làm |

#### 2. Thành viên B (Giao diện Tkinter & Custom Widgets)
| Tuần | Tên công việc | Kết quả kỳ vọng | Priority | Trạng thái |
| :---: | :--- | :--- | :---: | :---: |
| **9** | Dựng khung cửa sổ chính (Menu + Notebook nhiều tab) | Ảnh chụp cửa sổ chính chạy được từ `main.py` (Menu + Notebook ≥ 3 tab, dữ liệu giả) | High | Đang làm |
| **9** | Vẽ wireframe 4 màn hình (đăng nhập, chính, bệnh nhân, lịch hẹn) | Ảnh wireframe trong `docs/` | Medium | Hoàn thành |
| **9** | Form bệnh nhân với Treeview (dữ liệu giả) | `views/tab_benh_nhan.py` hiển thị bảng dữ liệu được | High | Hoàn thành |
| **10** | Tab lịch hẹn: form đặt lịch, DateEntry, Treeview, báo lỗi khi trùng | `views/tab_lich_hen.py`, demo được một lần trùng bị chặn thành công | High | Chưa làm |
| **10** | Màn hình đăng nhập và phân quyền ẩn/hiện chức năng | `views/dang_nhap_view.py`, 2 vai trò thấy giao diện/menu khác nhau | High | Đang làm |
| **10** | Nối tab bệnh nhân với QuanLyBenhNhan (thêm/sửa/xóa/tìm, Messagebox xác nhận) | Quay video màn hình hoặc ảnh chụp CRUD hoạt động thực tế | High | Chưa làm |
| **11** | Bắt đầu AppointmentCard (khung Custom Widget kế thừa tk.Frame) | `views/widgets/appointment_card.py` hiển thị được một lịch hẹn mẫu | Medium | Chưa làm |
| **11** | Tab phiếu khám: form ghi khám, chọn dịch vụ, Treeview danh sách phiếu | `views/tab_phieu_kham.py` nối với `QuanLyPhieuKham`, ảnh chụp chạy được | High | Chưa làm |
| **11** | Tìm lịch theo ngày và lọc theo bác sĩ trên tab lịch hẹn | Ô lọc ngày (DateEntry) và Combobox bác sĩ hoạt động đồng bộ | Medium | Chưa làm |
| **12** | Tab thống kê với biểu đồ Canvas (cột hoặc đường) | `views/tab_thong_ke.py` vẽ biểu đồ bằng Canvas từ `thong_ke.py`, ảnh chụp | High | Chưa làm |
| **12** | Hoàn thiện AppointmentCard và dùng trong tab lịch hẹn | Lịch hẹn hiển thị dạng thẻ trực quan, bấm vào thẻ xem chi tiết | Medium | Chưa làm |
| **13** | Kiểm thử giao diện: nhập sai, thu phóng cửa sổ, không trộn pack() và grid() | Không lỗi bố cục, mọi ô nhập sai đều hiện thông báo `messagebox` | High | Chưa làm |
| **13** | Viết chương Giao diện của báo cáo (ảnh chụp từng màn hình, mô tả widget) | Chương báo cáo giao diện hoàn chỉnh kèm ảnh minh họa | High | Chưa làm |

#### 3. Thành viên C (Hạ tầng, Dữ liệu ngoại vi, Kiểm thử & Đóng gói)
| Tuần | Tên công việc | Kết quả kỳ vọng | Priority | Trạng thái |
| :---: | :--- | :--- | :---: | :---: |
| **9** | Tạo repo GitHub, khung thư mục MVC, .gitignore, requirements.txt | Repo có cấu trúc trên nhánh `main`, cả 3 người clone được | High | Hoàn thành |
| **9** | Viết config.py (đường dẫn tương đối, hằng số) | `config.py` chạy được độc lập từ mọi máy | Medium | Chưa làm |
| **9** | Gửi giảng viên câu hỏi về mẫu báo cáo và mẫu bảng đóng góp | Câu trả lời của giảng viên lưu trong thư mục `docs/` | Medium | Chưa làm |
| **9** | Viết tao_du_lieu_mau.py sinh bệnh nhân và bác sĩ bằng random | Dữ liệu sinh tự động vào `data/*.json` (≥ 20 bệnh nhân, ≥ 5 bác sĩ) | Medium | Chưa làm |
| **9** | Thử gọi API địa chỉ, xem cấu trúc JSON trả về | `docs/api_dia_chi_notes.md` (ghi rõ phiên bản API đã lựa chọn) | Medium | Chưa làm |
| **9** | Khởi tạo bảng test case (≥ 10 dòng: input và kết quả mong đợi) | Tài liệu bảng kiểm thử ban đầu `docs/bang_kiem_thu` | Medium | Chưa làm |
| **10** | Gọi API địa chỉ và lưu dia_chi.json (có cache khi mất mạng) | `services/api_dia_chi.py` + `data/dia_chi.json`; xử lý timeout/mất mạng và đọc cache | Medium | Chưa làm |
| **10** | Chạy ≥ 5 test case và ghi kết quả thực tế | Bảng kiểm thử có ≥ 5 dòng đã điền đầy đủ kết quả thực tế | High | Chưa làm |
| **10** | Ghép nhánh lần 1 vào main, chạy thử từ main.py trên máy cả 3 người | Gắn Tag `v0.1`, ảnh chụp phần mềm chạy trên máy của cả 3 thành viên | High | Chưa làm |
| **11** | Gắn dữ liệu địa chỉ (tỉnh, phường/xã) vào Combobox form bệnh nhân | Chọn tỉnh thì danh sách phường/xã tự động lọc theo, ảnh chụp minh chứng | Medium | Chưa làm |
| **11** | Viết thong_ke.py (số lượt khám, doanh thu theo tháng và theo bác sĩ) | `services/thong_ke.py` trả về kết quả chính xác theo dữ liệu mẫu | High | Chưa làm |
| **11** | Cập nhật bảng test case cho phiếu khám và thống kê | Bảng kiểm thử bổ sung thêm các kịch bản kiểm thử mới | Low | Chưa làm |
| **12** | Xuất báo cáo ra CSV/JSON (theo khoảng ngày) | Nút xuất báo cáo hoạt động, file xuất ra mở được bằng Microsoft Excel | Medium | Chưa làm |
| **12** | Chức năng sao lưu và khôi phục dữ liệu | Thư mục `backup/` có bản sao kèm dấu thời gian, khôi phục thành công | Medium | Chưa làm |
| **12** | Viết sys_info.py (dùng module sys) và hiển thị trong mục Giới thiệu | `utils/sys_info.py`, hiển thị hộp thoại thông tin phiên bản Python | Low | Chưa làm |
| **13** | Hoàn thành ≥ 10 test case; kiểm thử mất mạng khi gọi API | Bảng kiểm thử đầy đủ (ca hợp lệ, không hợp lệ, giá trị biên) kèm kết quả | High | Chưa làm |
| **13** | Soát mã: không còn except trống, không đường dẫn tuyệt đối, không dữ liệu nhạy cảm | Danh sách mã nguồn đã rà soát, ứng dụng chạy mượt trên máy khác | High | Chưa làm |
| **13** | Viết chương Chức năng bổ sung, API và Kiểm thử của báo cáo | Chương báo cáo hoàn chỉnh kèm bảng số liệu kiểm thử | High | Chưa làm |
| **14** | Đóng gói exe bằng PyInstaller và chạy thử trên máy chưa cài Python | File `.exe` đóng gói độc lập chạy được, kèm dữ liệu mẫu | High | Chưa làm |
| **14** | Ghi nguồn thư viện, API và tài liệu tham khảo | Hoàn thiện mục Tài liệu tham khảo trong báo cáo | Medium | Chưa làm |
| **14** | Tổng hợp báo cáo Word và xuất PDF | Báo cáo `.docx` và `.pdf` thống nhất định dạng, canh lề chuẩn quy cách | High | Chưa làm |
| **14** | Viết README.md hướng dẫn cài đặt và chạy | `README.md` nêu rõ phiên bản Python, thư viện, hướng dẫn sinh dữ liệu mẫu | Medium | Chưa làm |

#### 4. Phối hợp Chung (Cả Nhóm)
| Tuần | Tên công việc | Kết quả kỳ vọng | Priority | Trạng thái |
| :---: | :--- | :--- | :---: | :---: |
| **9** | Họp chốt phạm vi và hợp đồng hàm giữa A và B | `docs/hop_dong_ham.md` liệt kê danh sách tên hàm các lớp quản lý | High | Chưa làm |
| **10** | Làm slide báo cáo 5–7 trang và tập demo 5 phút | File slide thuyết trình và kịch bản demo phân công chi tiết | High | Chưa làm |
| **12** | Chốt chức năng (feature freeze): từ đây chỉ sửa lỗi | Danh sách chức năng chốt sổ, nhánh `main` đạt trạng thái chạy ổn định | High | Chưa làm |
| **13** | Ghép toàn bộ nhánh vào main và gắn tag v1.0-candidate | Gắn tag `v1.0-candidate`, cả 3 người nghiệm thu chạy thử từ `main.py` | High | Chưa làm |
| **14** | Viết báo cáo đóng góp: bảng phân công, tỷ lệ, bằng chứng git shortlog | Bảng đóng góp có chữ ký xác nhận của cả 3, kèm trích xuất `git shortlog` | High | Chưa làm |
| **14** | Làm slide cuối kỳ và tập demo 2 lần | File slide hoàn thiện, kịch bản khớp thời lượng quy định của môn học | High | Chưa làm |
| **14** | Mỗi người luyện giải thích phần của mình và hiểu sơ qua phần 2 bạn còn lại | Cả 3 thành viên sẵn sàng trả lời phản biện về mọi phần của đồ án | Medium | Chưa làm |
| **14** | Soát checklist cuối của giảng viên và nộp bài trước hạn | Gói sản phẩm hoàn chỉnh: mã nguồn, dữ liệu mẫu, báo cáo, slide, exe, hướng dẫn | High | Chưa làm |
