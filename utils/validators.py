"""Tiện ích xác thực dữ liệu, bảo mật và tìm kiếm tiếng Việt."""
import calendar
import hashlib
import re
import secrets
from datetime import date, datetime

# ------------------------------------------------------------ Ngày tháng & năm nhuận

def la_nam_nhuan(nam: int) -> bool:
    """Trả về True nếu năm là năm nhuận (chia hết 4, trừ thế kỷ không chia hết 400)."""
    return (nam % 4 == 0 and nam % 100 != 0) or (nam % 400 == 0)

def la_ngay_hop_le(ngay: int, thang: int, nam: int) -> bool:
    """Kiểm tra ngày/tháng/năm có hợp lệ theo lịch Gregorian không.

    Xử lý tháng 2 năm nhuận: VD 29/02/2024 hợp lệ, 30/02/2027 không hợp lệ.
    """
    try:
        datetime(nam, thang, ngay)
        return True
    except ValueError:
        return False

def so_thang_toi_da(nam: int, hom_nay: date = None) -> int:
    """Tháng tối đa được chọn: nếu là năm hiện tại thì chỉ đến tháng hiện tại."""
    hom_nay = hom_nay or date.today()
    return hom_nay.month if nam == hom_nay.year else 12

def so_ngay_toi_da(nam: int, thang: int, hom_nay: date = None) -> int:
    """Ngày tối đa trong tháng, có tính năm nhuận và giới hạn theo ngày hiện tại."""
    hom_nay = hom_nay or date.today()
    if thang is None:
        ngay = 31
    else:
        nam_de_tinh = nam if nam is not None else 2000
        ngay = calendar.monthrange(nam_de_tinh, thang)[1]
    if nam == hom_nay.year and thang == hom_nay.month:
        ngay = min(ngay, hom_nay.day)
    return ngay

# ------------------------------------------------------------ Kiểm tra định dạng dữ liệu (Validators)

def la_sdt_hop_le(sdt) -> bool:
    """Số điện thoại di động Việt Nam: đúng 10 chữ số ASCII, bắt đầu bằng số 0."""
    return bool(re.fullmatch(r"0\d{9}", str(sdt).strip()))

def la_ma_bhyt_hop_le(so_bhyt) -> bool:
    """Số thẻ BHYT hợp lệ theo chuẩn Việt Nam (2 chữ cái + 13 chữ số) hoặc 'Không có'."""
    val = (so_bhyt or "").strip()
    if not val or val == "Không có":
        return True
    return bool(re.fullmatch(r"[A-Z]{2}\d{13}", val))

def la_ma_benh_nhan_hop_le(ma) -> bool:
    """Mã gồm đúng 14 chữ số và 8 số đầu là ngày đăng ký hợp lệ."""
    if not re.fullmatch(r"\d{14}", str(ma)):
        return False
    try:
        ngay_tu_ma_benh_nhan(ma)
    except ValueError:
        return False
    return True

def ngay_tu_ma_benh_nhan(ma: str) -> date:
    """Lấy ngày đăng ký (date) từ 8 số đầu của mã bệnh nhân (định dạng DDMMYYYY)."""
    return datetime.strptime(ma[0:8], "%d%m%Y").date()

def la_email_hop_le(email: str) -> bool:
    """Kiểm tra định dạng email cơ bản."""
    return bool(re.fullmatch(r"[\w.+-]+@[\w-]+(\.\w+)+", email))

def la_ma_bac_si_hop_le(ma: str) -> bool:
    """Mã bác sĩ gồm đúng 9 chữ số."""
    return bool(re.fullmatch(r"\d{9}", ma))

def nam_tu_ma_bac_si(ma: str) -> int:
    """Suy ra năm vào làm đầy đủ (4 chữ số) từ 2 số năm trong mã bác sĩ."""
    yy = int(ma[4:6])
    nam = 2000 + yy
    if nam > date.today().year:   # năm ở tương lai thì thuộc thế kỷ trước
        nam -= 100
    return nam

# ------------------------------------------------------------ Tiện ích bảo mật tài khoản (Salt & Hashing)

def tao_salt() -> str:
    """Tạo salt ngẫu nhiên 32 ký tự hex (16 bytes)."""
    return secrets.token_hex(16)

def bam_mat_khau(mat_khau: str, salt: str) -> str:
    """Băm mật khẩu kết hợp salt bằng thuật toán SHA-256."""
    return hashlib.sha256((mat_khau + salt).encode("utf-8")).hexdigest()

def xac_thuc_mat_khau(mat_khau_nhap: str, salt: str, mat_khau_hash: str) -> bool:
    """Xác thực mật khẩu người dùng nhập vào so với mã băm đã lưu."""
    return bam_mat_khau(mat_khau_nhap, salt) == mat_khau_hash
