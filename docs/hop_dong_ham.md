# HỢP ĐỒNG GIAO TIẾP HÀM GIỮA CÁC TẦNG (SERVICES & VIEWS)

> **Tài liệu**: `docs/hop_dong_ham.md`  
> **Mục đích**: Quy định chuẩn tên hàm, tham số, kiểu dữ liệu trả về và quy ước xử lý lỗi giữa Backend (Thành viên A & C) và Frontend GUI (Thành viên B).  
> **Phiên bản**: 1.1 (Cập nhật phân quyền 3 vai trò: `admin`, `le_tan`, `bac_si`)

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
Hệ thống chốt **3 vai trò**: `admin`, `le_tan` và `bac_si`.  
> [!IMPORTANT]
> **Cơ chế thực thi**:
> - Phân quyền chức năng do **tầng Giao diện (UI / Thành viên B)** thực hiện: ẩn tab hoặc khóa (disable) nút bấm tương ứng sau khi đăng nhập.
> - Riêng các thao tác của `QuanLyTaiKhoan`, Service tự kiểm tra thông qua tham số `nguoi_thuc_hien` (xem mục 2.5).
> - Dữ liệu của vai trò `bac_si` được lọc theo **mã bác sĩ gắn với tài khoản** (xem mục 1.2.1).

| Chức năng nghiệp vụ | `admin` | `le_tan` | `bac_si` | Cơ chế UI / Service thực hiện |
| :--- | :---: | :---: | :---: | :--- |
| Xem danh sách bệnh nhân, bác sĩ | ✓ | ✓ | ✓ | Bác sĩ chỉ xem danh sách bệnh nhân / lịch hẹn liên quan đến mình |
| Thêm bệnh nhân mới (`them`) | ✓ | ✓ | ✗ | Lễ tân và Admin thực hiện |
| Đặt lịch hẹn, sửa lịch, hủy lịch hẹn | ✓ | ✓ | ✗ | Lễ tân tiếp nhận và điều phối |
| Sửa thông tin, Xóa hồ sơ bệnh nhân (`sua`, `xoa`) | ✓ | ✗ | ✗ | UI disable / ẩn nút Sửa & Xóa |
| Quản lý bác sĩ (`QuanLyBacSi`) | ✓ | ✗ | ✗ | UI ẩn chức năng quản lý nhân sự |
| Quản lý tài khoản (`QuanLyTaiKhoan`) | ✓ | ✗ | ✗ | UI ẩn tab Quản trị tài khoản |
| Tạo phiếu khám (`tao_phieu_kham`), Thêm dịch vụ | ✓ | ✓ | ✓ | Bác sĩ hoặc Lễ tân có thể thao tác trên phiếu khám |
| Thu tiền thanh toán (`thanh_toan`) | ✓ | ✓ | ✗ | Lễ tân thu tiền và in hóa đơn |
| Hoàn tất khám & Kê đơn (`hoan_tat_kham`) | ✓ | ✗ | ✓ | Bác sĩ và Admin thực hiện (Lễ tân không có quyền chẩn đoán & kê đơn) |
| Xem lịch khám của chính mình | ✓ | ✗ | ✓ | Bác sĩ chỉ xem lịch trực và lịch hẹn của cá nhân mình |
| Tab Thống kê doanh thu & Xuất báo cáo | ✓ | ✗ | ✗ | UI ẩn hoàn toàn Tab Thống kê |

#### 1.2.1. Phạm vi dữ liệu của vai trò `bac_si`
Tài khoản vai trò `bac_si` được gắn với một bác sĩ qua trường `ma_bac_si` (mã 9 số) của `TaiKhoan`. Sau khi đăng nhập, UI lấy mã này bằng `QuanLyTaiKhoan.tim_theo_ten(ten).ma_bac_si` và dùng để lọc dữ liệu:

| Màn hình | Dữ liệu bác sĩ được xem | Hàm dùng |
| :--- | :--- | :--- |
| Lịch hẹn, lịch trực | Chỉ lịch hẹn của chính mình | `QuanLyLichHen.loc_lich_hen(ma_bac_si=...)` |
| Danh sách bệnh nhân | Chỉ bệnh nhân có lịch hẹn hoặc phiếu khám với mình | `QuanLyLichHen.lay_ma_benh_nhan_cua_bac_si` + `QuanLyPhieuKham.lay_theo_bac_si`, rồi `QuanLyBenhNhan.lay_theo_cac_ma` |
| Phiếu khám | Chỉ phiếu có `ma_bac_si` trùng mã của mình; chỉ được hoàn tất khám với phiếu của mình | `QuanLyPhieuKham.lay_theo_bac_si` |

### 1.3. Quy chuẩn Truyền dữ liệu Ngày tháng (Date Format)
- **Giao tiếp View ↔ Service**: Luôn truyền chuỗi theo chuẩn Việt Nam **`DD-MM-YYYY`** (Ví dụ: `"15-05-1990"`).
- **Service xử lý**: Service sẽ parse chuỗi `DD-MM-YYYY` sang đối tượng `datetime.date`, đồng thời kiểm tra tính hợp lệ bằng `utils.validators.la_ngay_hop_le` (bao gồm xử lý năm nhuận, ngày 29/02, 30/02...). Nếu ngày không hợp lệ, trả về `(False, "Ngày tháng không hợp lệ!")`.

### 1.4. Chia sẻ Hàm Kiểm tra Dữ liệu (Validation)
- Thành viên B **import trực tiếp các hàm kiểm tra từ `utils/validators.py`** (`la_sdt_hop_le`, `la_ma_bhyt_hop_le`, `la_ngay_hop_le`, `la_email_hop_le`) để kiểm tra dữ liệu trực tiếp trên form giao diện.
- Tránh việc tự viết hoặc copy lại các biểu thức Regex, giúp đảm bảo tính đồng bộ tuyệt đối khi có thay đổi nghiệp vụ.

### 1.5. Viết Docstring cho hàm
Mọi hàm trong tầng Service đều phải viết docstring ngay dưới dòng khai báo def để mô tả chi tiết chức năng, tham số và giá trị trả về
*Ví dụ:*
```python
def ten_ham(tham_so):
    """Mô tả ngắn gọn chức năng của hàm. VD: 'Kiểm tra tính hợp lệ của...'."""
    # Nội dung hàm...
```

---

## 2. CHI TIẾT HỢP ĐỒNG CÁC LỚP QUẢN LÝ (SERVICES)

### 2.1. `QuanLyBenhNhan` (`services/quan_ly_benh_nhan.py`)

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `lay_tat_ca()` | `list[BenhNhan]` | Lấy danh sách toàn bộ bệnh nhân từ bộ nhớ/file JSON |
| `tim_theo_ma(ma)` | `BenhNhan \| None` | Tìm chính xác bệnh nhân theo mã định danh (14 số) |
| `lay_theo_cac_ma(cac_ma)` | `list[BenhNhan]` | *(Mới)* Lấy các bệnh nhân có mã nằm trong tập `cac_ma`. Dùng cho vai trò `bac_si` (danh sách bệnh nhân liên quan đến mình) |
| `tim_kiem(tu_khoa = "", tieu_chi = "ho_ten", ho_ten = None, so_bhyt = None, **tieu_chi_khac)` | `list[BenhNhan]` | Tìm kiếm tiếng Việt không dấu. Hỗ trợ 2 tiêu chí cốt lõi: **Họ tên (`ho_ten`)** và **Số BHYT (`bhyt`/`so_bhyt`)**, kèm các tiêu chí mở rộng (`sdt`, `ma`). Hỗ trợ cả tìm đơn tiêu chí lẫn kết hợp đa tiêu chí |
| `tim_kiem_ket_hop(ho_ten = "", so_bhyt = "", sdt = "", ma = "")` | `list[BenhNhan]` | Tìm kiếm kết hợp đồng thời nhiều tiêu chí (ít nhất 2 tiêu chí bắt buộc hỗ trợ: Họ tên và Số BHYT, lọc theo điều kiện AND) |
| `them(du_lieu: dict)` | `tuple[bool, str, BenhNhan \| None]` | Thêm bệnh nhân mới. Tự động kiểm tra trùng `ma_dinh_danh`, `sdt`, validate regex SĐT `0\d{9}` và email. Quyền: `admin`, `le_tan` |
| `sua(ma, du_lieu_moi)` | `tuple[bool, str]` | Cập nhật thông tin bệnh nhân có mã `ma`. Quyền: Chỉ `admin` |
| `xoa(ma)` | `tuple[bool, str]` | Xóa bệnh nhân. Quyền: Chỉ `admin`. Phải kiểm tra ràng buộc: không xóa nếu bệnh nhân đang có lịch hẹn hoặc phiếu khám chưa kết thúc |
| `sinh_ma_moi(ngay_dang_ky = None)` | `str` | Sinh mã bệnh nhân 14 số tự động: 8 số đầu là `DDMMYYYY` của ngày đăng ký, 6 số sau là số thứ tự tăng dần trong ngày |

---

### 2.2. `QuanLyBacSi` (`services/quan_ly_bac_si.py`)

Quyền thao tác ghi (`them`, `sua`, `xoa`): Chỉ `admin`. Các hàm xem dùng được cho cả 3 vai trò.

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `lay_tat_ca()` | `list[BacSi]` | Lấy toàn bộ danh sách bác sĩ |
| `tim_theo_ma(ma)` | `BacSi \| None` | Tìm bác sĩ theo mã định danh 9 số |
| `lay_theo_chuyen_khoa(ma_khoa)` | `list[BacSi]` | Lấy danh sách bác sĩ thuộc một chuyên khoa cụ thể |
| `them(du_lieu)` | `tuple[bool, str, BacSi \| None]` | Thêm bác sĩ mới. Tự động kiểm tra trùng mã 9 số |
| `sua(ma, du_lieu_moi)` | `tuple[bool, str]` | Sửa thông tin bác sĩ |
| `xoa(ma)` | `tuple[bool, str]` | Xóa bác sĩ (kiểm tra không xóa nếu đang có lịch hẹn đang chờ hoặc đang có tài khoản `bac_si` gắn với mã này) |

---

### 2.3. `QuanLyLichHen` (`services/quan_ly_lich_hen.py`)

Quyền đặt, sửa, hủy lịch: `admin`, `le_tan`. Vai trò `bac_si` chỉ xem lịch của mình.

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `lay_tat_ca()` | `list[LichHen]` | Lấy toàn bộ lịch hẹn |
| `loc_lich_hen(ngay = None, ma_bac_si = None)` | `list[LichHen]` | Lọc lịch hẹn phục vụ hiển thị Treeview và Thẻ lịch hẹn (AppointmentCard) trên Tab Lịch hẹn. Vai trò `bac_si` luôn truyền `ma_bac_si` của chính mình |
| `lay_ma_benh_nhan_cua_bac_si(ma_bac_si)` | `set[str]` | *(Mới)* Mã các bệnh nhân có lịch hẹn với bác sĩ này (trừ lịch `Da_huy`). Dùng cho danh sách bệnh nhân của vai trò `bac_si` |
| `lay_danh_sach_bac_si_ranh(ngay, gio_bat_dau, thoi_luong, ma_khoa = None)` | `list[BacSi]` | Lấy danh sách các bác sĩ có lịch trực trong buổi đó và **chưa bị trùng lịch hẹn** trong khung giờ yêu cầu |
| `kiem_tra_trung_lich(ma_bac_si, ngay, gio_bat_dau, thoi_luong, ma_lich_hen_bo_qua = None)` | `tuple[bool, str]` | Trả về `(True, "Trùng lịch...")` nếu bác sĩ đã có lịch hẹn giao nhau thời gian; trả về `(False, "")` nếu rảnh. **Bỏ qua lịch `Da_huy`, `Vang` và chính mã lịch đang chỉnh sửa** |
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
| `lay_theo_bac_si(ma_bs: str)` | `list[PhieuKham]` | *(Mới)* Lấy các phiếu khám do bác sĩ này phụ trách. Dùng cho vai trò `bac_si` |
| `tao_phieu_kham(du_lieu: dict)` | `tuple[bool, str, PhieuKham \| None]` | Khởi tạo phiếu khám ban đầu (có thể từ lịch hẹn hoặc khám vãng lai). Trạng thái khám ban đầu là `"Dang_kham"`. Quyền: `admin`, `le_tan`, `bac_si` |
| `them_dich_vu(ma_pk: str, ma_dv: str, so_luong: int = 1)` | `tuple[bool, str]` | Thêm dịch vụ cận lâm sàng vào phiếu (chụp lại đơn giá dịch vụ tại thời điểm khám). Quyền: `admin`, `le_tan`, `bac_si` |
| `xoa_dich_vu(ma_pk: str, ma_dv: str)` | `tuple[bool, str]` | Bỏ dịch vụ đã chọn khỏi phiếu khám. Quyền: `admin`, `le_tan`, `bac_si` |
| `hoan_tat_kham(ma_pk: str, chan_doan: str, loi_dan: str, don_thuoc: list, ngay_tai_kham: str = None)` | `tuple[bool, str]` | Hoàn thành chẩn đoán và kê đơn, chuyển `trang_thai_kham = "Hoan_thanh"`. **Quyền: `admin`, `bac_si` (Lễ tân không có quyền).** Vai trò `bac_si` chỉ hoàn tất phiếu có `ma_bac_si` trùng mã của mình |
| `thanh_toan(ma_pk: str)` | `tuple[bool, str, float]` | Xác nhận bệnh nhân đã thanh toán viện phí (`trang_thai_thanh_toan = "Da_thanh_toan"`), trả về tổng tiền đã thu. Quyền: `admin`, `le_tan` (bác sĩ không có quyền) |
| `sinh_ma_moi()` | `str` | Sinh mã tự động `PK001`, `PK002`... |

---

### 2.5. `QuanLyTaiKhoan` (`services/quan_ly_tai_khoan.py`)

> [!NOTE]
> **Quy ước tham số `nguoi_thuc_hien`**: luôn là **tên đăng nhập** của người đang thao tác (không phải tên vai trò). Service tra tài khoản đó và chỉ cho phép khi tài khoản là `admin` và đang hoạt động. Giá trị mặc định là `None` (từ chối), không bao giờ mặc định là `admin`.

| Tên hàm & Tham số | Kiểu trả về | Mô tả & Lưu ý |
| :--- | :--- | :--- |
| `lay_tat_ca()` | `list[TaiKhoan]` | Lấy danh sách tài khoản. Quyền: Chỉ `admin` |
| `tim_theo_ten(ten: str)` | `TaiKhoan \| None` | Tìm tài khoản theo tên đăng nhập (không phân biệt hoa thường). UI dùng để lấy `vai_tro` và `ma_bac_si` sau khi đăng nhập |
| `xac_thuc(ten_dang_nhap: str, mat_khau_nhap: str)` | `str \| None` | Băm mật khẩu nhập với `salt` lưu trong file để so khớp. Trả về tên vai trò (`"admin"`, `"le_tan"` hoặc `"bac_si"`) nếu đúng; trả về `None` nếu sai hoặc tài khoản bị khóa |
| `doi_mat_khau(ten: str, mk_cu: str, mk_moi: str)` | `tuple[bool, str]` | Kiểm tra mật khẩu cũ, sinh salt mới và băm lưu mật khẩu mới. Người dùng tự đổi mật khẩu của mình (mọi vai trò) |
| `tao_tai_khoan(ten: str, mat_khau: str, vai_tro: str, nguoi_thuc_hien: str = None, ma_bac_si: str = None)` | `tuple[bool, str, TaiKhoan \| None]` | Quyền: Chỉ `admin`. Khi `vai_tro == "bac_si"` thì **bắt buộc** `ma_bac_si` hợp lệ và có trong `QuanLyBacSi`, đồng thời mã đó chưa có tài khoản khác |
| `khoa_tai_khoan(ten: str, nguoi_thuc_hien: str = None)` | `tuple[bool, str]` | Quyền: Chỉ `admin`. Khóa không cho tài khoản đăng nhập. Không khóa `admin` mặc định, không tự khóa chính mình |
| `mo_khoa_tai_khoan(ten: str, nguoi_thuc_hien: str = None)` | `tuple[bool, str]` | Quyền: Chỉ `admin`. Mở khóa tài khoản đã bị khóa |
| `dat_lai_mat_khau(ten: str, mat_khau_moi: str, nguoi_thuc_hien: str = None)` | `tuple[bool, str]` | Quyền: Chỉ `admin`. Đặt lại mật khẩu không cần biết mật khẩu cũ |
| `xoa_tai_khoan(ten: str, nguoi_thuc_hien: str = None)` | `tuple[bool, str]` | Quyền: Chỉ `admin`. Không xóa `admin` mặc định, không tự xóa chính mình |

---

### 2.6. `ThongKe` (`services/thong_ke.py`)

> [!NOTE]
> **Quy chuẩn tính toán Thống kê** (chỉ vai trò `admin` sử dụng):
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
