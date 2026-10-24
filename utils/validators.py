"""Kiểm tra định dạng dữ liệu nhập, giải mã mã định danh và băm mật khẩu."""
import calendar
import hashlib
import re
import secrets
from datetime import date, datetime

# ------------------------------------------------------------ Ngày tháng & năm nhuận

def la_nam_nhuan(nam):
    """Trả về True nếu 'nam' là năm nhuận."""
    return (nam % 4 == 0 and nam % 100 != 0) or (nam % 400 == 0)

def la_ngay_hop_le(ngay, thang, nam):
    """Trả về True nếu (ngày, tháng, năm) là một ngày có thật. VD: 30/02 -> False."""
    try:
        datetime(nam, thang, ngay)
        return True
    except ValueError:
        return False

def so_thang_toi_da(nam, hom_nay=None):
    """Số tháng được chọn: năm hiện tại chỉ đến tháng hiện tại, năm khác là 12."""
    hom_nay = hom_nay or date.today()
    return hom_nay.month if nam == hom_nay.year else 12

def so_ngay_toi_da(nam, thang, hom_nay=None):
    """Số ngày được chọn cho (năm, tháng); năm hoặc tháng có thể là None nếu chưa chọn.
 
    Tháng hiện tại của năm hiện tại chỉ được chọn đến ngày hôm nay.
    """
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
def la_sdt_hop_le(sdt):
    """Số điện thoại di động Việt Nam: đúng 10 chữ số ASCII, bắt đầu bằng số 0."""
    return bool(re.fullmatch(r"0\d{9}", str(sdt).strip()))

def la_ma_bhyt_hop_le(so_bhyt):
    """Số thẻ BHYT hợp lệ: đúng 13 chữ số, hoặc rỗng, hoặc 'Không có'."""
    val = (so_bhyt or "").strip()
    if not val or val == "Không có":
        return True
    return bool(re.fullmatch(r"\d{13}", val))

def la_email_hop_le(email):
    """Kiểm tra định dạng email hợp lệ, không khoảng trống, có hỗ trợ tên miền đa cấp độ VD: 'an@mail.co.uk' -> True."""
    return bool(re.fullmatch(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", str(email).strip()))

# ----------------------------Mã định danh
def la_ma_benh_nhan_hop_le(ma):
    """Mã bệnh nhân gồm đúng 14 chữ số, 8 số đầu là ngày đăng ký hợp lệ."""
    if not re.fullmatch(r"\d{14}", str(ma)):
        return False
    try:
        ngay_tu_ma_benh_nhan(ma)
    except ValueError:
        return False
    return True

def ngay_tu_ma_benh_nhan(ma):
    """Lấy ngày đăng ký (date) từ 8 số đầu của mã bệnh nhân (định dạng DDMMYYYY)."""
    return datetime.strptime(ma[0:8], "%d%m%Y").date()


def la_ma_bac_si_hop_le(ma):
    """Mã bác sĩ gồm đúng 9 chữ số."""
    return bool(re.fullmatch(r"\d{9}", ma))

def nam_tu_ma_bac_si(ma):
    """Suy ra năm vào làm đầy đủ (4 chữ số) từ 2 số năm trong mã bác sĩ.
 
    VD: '26' -> 2026; '99' -> 1999 (năm ở tương lai thì thuộc thế kỷ trước).
    """
    yy = int(ma[4:6])
    nam = 2000 + yy
    if nam > date.today().year:
        nam -= 100
    return nam

# ------------------------------------------------------------ Tiện ích bảo mật tài khoản (Salt & Hashing)

def tao_salt() -> str:
    """Tạo salt ngẫu nhiên 32 ký tự hex (16 bytes)."""
    return secrets.token_hex(16)

def bam_mat_khau(mat_khau: str, salt: str) -> str:
    """Băm mật khẩu kết hợp salt bằng thuật toán SHA-256, trả về chuỗi 64 ký tự hex."""
    return hashlib.sha256((mat_khau + salt).encode("utf-8")).hexdigest()

def xac_thuc_mat_khau(mat_khau_nhap: str, salt: str, mat_khau_hash: str) -> bool:
    """Xác thực mật khẩu người dùng nhập vào so với mã băm đã lưu."""
    hash_nhap=bam_mat_khau(mat_khau_nhap, salt)
    return secrets.compare_digest(hash_nhap, mat_khau_hash)