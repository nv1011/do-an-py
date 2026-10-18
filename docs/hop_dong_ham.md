# HỢP ĐỒNG GIAO TIẾP HÀM GIỮA CÁC TẦNG (SERVICES & VIEWS)

> **Tài liệu**: `docs/hop_dong_ham.md`  
> **Mục đích**: Quy định chuẩn tên hàm, tham số, kiểu dữ liệu trả về và quy ước xử lý lỗi giữa Backend (Thành viên A & C) và Frontend GUI (Thành viên B).  
> **Phiên bản**: 1.0 (Chốt phạm vi Tuần 9)

---

## 1. QUY ƯỚC CHUNG

### 1.1. Kiểu trả về cho các hàm thao tác (Thêm / Sửa / Xóa / Nghiệp vụ)
Hầu hết các thao tác ghi dữ liệu đều trả về một bộ giá trị `tuple`:
```python
tuple[bool, str, Any | None]
# Phần tử 0 (bool): True nếu thành công, False nếu thất bại
# Phần tử 1 (str): Thông điệp phản hồi (dùng để hiển thị messagebox cho người dùng)
# Phần tử 2 (tùy chọn): Dữ liệu trả về kèm theo (đối tượng vừa tạo, kết quả tính toán...)
```
*Ví dụ:*
```python
thanh_cong, thong_diep, benh_nhan = ql_bn.them(du_lieu_form)
if thanh_cong:
    messagebox.showinfo("Thành công", thong_diep)
else:
    messagebox.showerror("Lỗi", thong_diep)
```

### 1.2. Phân quyền vai trò người dùng (Access Control)
Hệ thống chốt **2 vai trò duy nhất**: `admin` và `le_tan`.  
> [!IMPORTANT]
> **Cơ chế thực thi**: Phân quyền do **tầng Giao diện (UI / Thành viên B)** thực hiện (ẩn các tab hoặc khóa/disable các nút bấm tương ứng sau khi đăng nhập). Tầng Service thực hiện xử lý nghiệp vụ khi được gọi.

| Chức năng nghiệp vụ | `admin` | `le_tan` | Cơ chế UI thực hiện |
| :--- | :---: | :---: | :--- |
| Xem danh sách bệnh nhân, bác sĩ, lịch hẹn | ✓ | ✓ | Toàn quyền xem |
| Thêm bệnh nhân mới (`them`) | ✓ | ✓ | Mở form nhập liệu |
| Đặt lịch hẹn, sửa lịch, hủy lịch hẹn | ✓ | ✓ | Tiếp nhận và điều phối |
| Sửa thông tin, Xóa hồ sơ bệnh nhân (`sua`, `xoa`) | ✓ | ✗ | **UI disable / ẩn nút Sửa & Xóa** |
| Quản lý bác sĩ (`QuanLyBacSi`) | ✓ | ✗ | **UI ẩn chức năng quản lý nhân sự** |
| Quản lý tài khoản (`QuanLyTaiKhoan`) | ✓ | ✗ | **UI ẩn tab Quản trị tài khoản** |
| Tạo phiếu khám (`tao_phieu_kham`), Thêm dịch vụ | ✓ | ✓ | Lễ tân lập phiếu khám ban đầu |
| Thu tiền thanh toán (`thanh_toan`) | ✓ | ✓ | Lễ tân thu tiền và in hóa đơn |
| **Hoàn tất khám (`hoan_tat_kham`)** | **✓** | **✗** | **Lễ tân không có quyền** (Chỉ admin / bác sĩ chuyên môn mới chẩn đoán & kê đơn) |
| Tab Thống kê doanh thu & Xuất báo cáo | ✓ | ✗ | **UI ẩn hoàn toàn Tab Thống kê** |

### 1.3. Quy chuẩn Truyền dữ liệu Ngày tháng (Date Format)
- **Giao tiếp View ↔ Service**: Luôn truyền chuỗi theo chuẩn Việt Nam **`DD-MM-YYYY`** (Ví dụ: `"15-05-1990"`).
- **Service xử lý**: Service sẽ parse chuỗi `DD-MM-YYYY` sang đối tượng `datetime.date`, đồng thời kiểm tra tính hợp lệ bằng `utils.validators.la_ngay_hop_le` (bao gồm xử lý năm nhuận, ngày 29/02, 30/02...). Nếu ngày không hợp lệ, trả về `(False, "Ngày tháng không hợp lệ!")`.

### 1.4. Chia sẻ Hàm Kiểm tra Dữ liệu (Validation)
- Thành viên B **import trực tiếp các hàm kiểm tra từ `utils/validators.py`** (`la_sdt_hop_le`, `la_ma_bhyt_hop_le`, `la_ngay_hop_le`, `la_email_hop_le`) để kiểm tra dữ liệu trực tiếp trên form giao diện.
- Tránh việc tự viết hoặc copy lại các biểu thức Regex, giúp đảm bảo tính đồng bộ tuyệt đối khi có thay đổi nghiệp vụ.

---

## 2. CHI TIẾT HỢP ĐỒNG CÁC LỚP QUẢN LÝ (SERVICES)

### 2.1. `QuanLyBenhNhan` (`services/quan_ly_benh_nhan.py`)

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `lay_tat_ca()` | `list[BenhNhan]` | Lấy danh sách toàn bộ bệnh nhân từ bộ nhớ/file JSON |
| `tim_theo_ma(ma: str)` | `BenhNhan \| None` | Tìm chính xác bệnh nhân theo mã định danh (14 số) |
| `tim_kiem(tu_khoa: str = "", tieu_chi: str = "ho_ten", ho_ten: str = None, so_bhyt: str = None, **tieu_chi_khac)` | `list[BenhNhan]` | Tìm kiếm tiếng Việt không dấu. Hỗ trợ 2 tiêu chí cốt lõi: **Họ tên (`ho_ten`)** và **Số BHYT (`bhyt`/`so_bhyt`)**, kèm các tiêu chí mở rộng (`sdt`, `ma`). Hỗ trợ cả tìm đơn tiêu chí lẫn kết hợp đa tiêu chí |
| `tim_kiem_ket_hop(ho_ten: str = "", so_bhyt: str = "", sdt: str = "", ma: str = "")` | `list[BenhNhan]` | Tìm kiếm kết hợp đồng thời nhiều tiêu chí (ít nhất 2 tiêu chí bắt buộc hỗ trợ: Họ tên và Số BHYT, lọc theo điều kiện AND) |
| `them(du_lieu: dict)` | `tuple[bool, str, BenhNhan \| None]` | Thêm bệnh nhân mới. Tự động kiểm tra trùng `ma_dinh_danh`, `sdt`, validate regex SĐT `0\d{9}` và email |
| `sua(ma: str, du_lieu_moi: dict)` | `tuple[bool, str]` | Cập nhật thông tin bệnh nhân có mã `ma`. Quyền: Chỉ `admin` |
| `xoa(ma: str)` | `tuple[bool, str]` | Xóa bệnh nhân. Quyền: Chỉ `admin`. Phải kiểm tra ràng buộc: không xóa nếu bệnh nhân đang có lịch hẹn hoặc phiếu khám chưa kết thúc |
| `sinh_ma_moi(ngay_dang_ky: date = None)` | `str` | Sinh mã bệnh nhân 14 số tự động: 8 số đầu là `DDMMYYYY` của ngày đăng ký, 6 số sau là số thứ tự tăng dần trong ngày |

---

### 2.2. `QuanLyBacSi` (`services/quan_ly_bac_si.py`)

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `lay_tat_ca()` | `list[BacSi]` | Lấy toàn bộ danh sách bác sĩ |
| `tim_theo_ma(ma: str)` | `BacSi \| None` | Tìm bác sĩ theo mã định danh 9 số |
| `lay_theo_chuyen_khoa(ma_khoa: str)` | `list[BacSi]` | Lấy danh sách bác sĩ thuộc một chuyên khoa cụ thể |
| `them(du_lieu: dict)` | `tuple[bool, str, BacSi \| None]` | Thêm bác sĩ mới. Tự động kiểm tra trùng mã 9 số |
| `sua(ma: str, du_lieu_moi: dict)` | `tuple[bool, str]` | Sửa thông tin bác sĩ |
| `xoa(ma: str)` | `tuple[bool, str]` | Xóa bác sĩ (kiểm tra không xóa nếu đang có lịch hẹn đang chờ) |

---

### 2.3. `QuanLyLichHen` (`services/quan_ly_lich_hen.py`)

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `lay_tat_ca()` | `list[LichHen]` | Lấy toàn bộ lịch hẹn |
| `loc_lich_hen(ngay: date = None, ma_bac_si: str = None)` | `list[LichHen]` | Lọc lịch hẹn phục vụ hiển thị Treeview và Thẻ lịch hẹn (AppointmentCard) trên Tab Lịch hẹn |
| `lay_danh_sach_bac_si_ranh(ngay: date, gio_bat_dau: str, thoi_luong: int, ma_khoa: str = None)` | `list[BacSi]` | Lấy danh sách các bác sĩ có lịch trực trong buổi đó và **chưa bị trùng lịch hẹn** trong khung giờ yêu cầu |
| `kiem_tra_trung_lich(ma_bac_si: str, ngay: date, gio_bat_dau: str, thoi_luong: int, ma_lich_hen_bo_qua: str = None)` | `tuple[bool, str]` | Trả về `(True, "Trùng lịch...")` nếu bác sĩ đã có lịch hẹn giao nhau thời gian; trả về `(False, "")` nếu rảnh. **Bỏ qua lịch `Da_huy`, `Vang` và chính mã lịch đang chỉnh sửa** |
| `dat_lich(du_lieu: dict)` | `tuple[bool, str, LichHen \| None]` | Đặt lịch hẹn mới. **Bắt buộc kiểm tra `ngay >= date.today()`** và gọi `kiem_tra_trung_lich` trước khi lưu |
| `sua_lich(ma: str, du_lieu_moi: dict)` | `tuple[bool, str]` | Sửa thông tin lịch hẹn (kiểm tra trùng lịch có trừ chính mã này ra) |
| `huy_lich(ma: str, ly_do: str = "")` | `tuple[bool, str]` | Chuyển trạng thái lịch hẹn sang `"Da_huy"`. Giải phóng khung giờ để người khác có thể đặt |
| `sinh_ma_moi()` | `str` | Sinh mã dạng `LH001`, `LH002`... |

---

### 2.4. `QuanLyPhieuKham` (`services/quan_ly_phieu_kham.py`)

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `lay_tat_ca()` | `list[PhieuKham]` | Lấy danh sách toàn bộ phiếu khám |
| `tim_theo_ma(ma: str)` | `PhieuKham \| None` | Tìm phiếu khám theo mã (VD: `PK001`) |
| `lay_theo_benh_nhan(ma_bn: str)` | `list[PhieuKham]` | Lấy toàn bộ lịch sử các lần khám của bệnh nhân |
| `tao_phieu_kham(du_lieu: dict)` | `tuple[bool, str, PhieuKham \| None]` | Khởi tạo phiếu khám ban đầu (có thể từ lịch hẹn hoặc khám vãng lai). Trạng thái khám ban đầu là `"Dang_kham"` |
| `them_dich_vu(ma_pk: str, ma_dv: str, so_luong: int = 1)` | `tuple[bool, str]` | Thêm dịch vụ cận lâm sàng vào phiếu (chụp lại đơn giá dịch vụ tại thời điểm khám) |
| `xoa_dich_vu(ma_pk: str, ma_dv: str)` | `tuple[bool, str]` | Bỏ dịch vụ đã chọn khỏi phiếu khám |
| `hoan_tat_kham(ma_pk: str, chan_doan: str, loi_dan: str, don_thuoc: list, ngay_tai_kham: str = None)` | `tuple[bool, str]` | Bác sĩ/Admin hoàn thành chẩn đoán và kê đơn, chuyển `trang_thai_kham = "Hoan_thanh"`. **Quyền: Chỉ admin / bác sĩ chuyên môn (Lễ tân không có quyền)** |
| `thanh_toan(ma_pk: str)` | `tuple[bool, str, float]` | Xác nhận bệnh nhân đã thanh toán viện phí (`trang_thai_thanh_toan = "Da_thanh_toan"`), trả về tổng tiền đã thu |
| `sinh_ma_moi()` | `str` | Sinh mã tự động `PK001`, `PK002`... |

---

### 2.5. `QuanLyTaiKhoan` (`services/quan_ly_tai_khoan.py`)

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `xac_thuc(ten_dang_nhap: str, mat_khau_nhap: str)` | `str \| None` | Băm mật khẩu nhập với `salt` lưu trong file để so khớp. Trả về tên vai trò (`"admin"` hoặc `"le_tan"`) nếu đúng; trả về `None` nếu sai |
| `doi_mat_khau(ten: str, mk_cu: str, mk_moi: str)` | `tuple[bool, str]` | Kiểm tra mật khẩu cũ, sinh salt mới và băm lưu mật khẩu mới |
| `tao_tai_khoan(ten: str, mat_khau: str, vai_tro: str)` | `tuple[bool, str]` | Quyền: Chỉ `admin` |
| `khoa_tai_khoan(ten: str)` | `tuple[bool, str]` | Quyền: Chỉ `admin`. Khóa không cho tài khoản đăng nhập |

---

### 2.6. `ThongKe` (`services/thong_ke.py`)

> [!NOTE]
> **Quy chuẩn tính toán Thống kê**:
> - **Lượt khám**: Số phiếu khám có `trang_thai_kham == "Hoan_thanh"` tính theo `ngay_kham`.
> - **Doanh thu**: Tổng tiền của các phiếu khám có `trang_thai_thanh_toan == "Da_thanh_toan"` tính theo `ngay_kham`.

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `thong_ke_theo_thang(nam: int)` | `dict[int, dict]` | Trả về `{tháng: {"luot_kham": n, "doanh_thu": x}}` (từ tháng 1 đến 12) phục vụ Thành viên B vẽ Canvas đồng bộ |
| `thong_ke_theo_ngay(nam: int, thang: int)` | `dict[int, dict]` | Trả về `{ngày: {"luot_kham": n, "doanh_thu": x}}` trong tháng |
| `thong_ke_doanh_thu_theo_thang(nam: int)` | `dict[int, float]` | Trả về `{tháng: tổng_tiền}` của các phiếu khám đã thanh toán trong năm |
| `thong_ke_luot_kham_theo_bac_si(tu_ngay: date, den_ngay: date)` | `dict[str, int]` | Trả về `{tên_bác_sĩ: số_ca_khám}` phục vụ vẽ biểu đồ cột/đường trên Canvas |
| `thong_ke_co_cau_chuyen_khoa(tu_ngay: date, den_ngay: date)` | `dict[str, int]` | Thống kê số lượt khám theo từng chuyên khoa |
| `xuat_bao_cao_csv(duong_dan: str, tu_ngay: date, den_ngay: date)` | `tuple[bool, str]` | Xuất dữ liệu báo cáo ra file `.csv` mở được bằng Microsoft Excel |
