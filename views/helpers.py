"""
- tìm kiếm không cần chính xác (bỏ dấu, không phân biệt hoa/thường)
- tính số tháng/số ngày hợp lệ cho bộ chọn ngày
- giờ giấc và kiểm tra trùng lịch hẹn
"""
import calendar
import re
import unicodedata
from datetime import date

NAM_NHO_NHAT = 1900


# ---------------------------------------------------------- tìm kiếm
def bo_dau(chuoi):
    """'Nguyễn Đức' -> 'Nguyen Duc'."""
    chuoi = chuoi.replace("đ", "d").replace("Đ", "D")  # đ không tách được bằng NFD
    phan_tach = unicodedata.normalize("NFD", chuoi)
    return "".join(c for c in phan_tach if unicodedata.category(c) != "Mn")


def chuan_hoa(chuoi):
    """Bỏ dấu, viết thường, gộp khoảng trắng thừa."""
    return " ".join(bo_dau(chuoi).lower().split())


def khop_ten(ten, tu_khoa):
    """Mỗi từ trong từ khóa phải là phần ĐẦU của một từ nào đó trong tên.
    'an'         -> khớp 'Nguyễn Văn An' (từ 'An'), không khớp 'Trần' hay 'Văn'
    'nguyen van' -> khớp 'Nguyễn Văn An'
    'van an'     -> khớp 'Nguyễn Văn An' (không cần đúng thứ tự liền nhau)
    """
    cac_tu_khoa = chuan_hoa(tu_khoa).split()
    cac_tu_ten = chuan_hoa(ten).split()
    return all(any(tu.startswith(tk) for tu in cac_tu_ten) for tk in cac_tu_khoa)


def khop_chuoi(gia_tri, tu_khoa):
    """Từ khóa nằm ở bất kỳ đâu trong giá trị (dùng cho mã, SĐT, BHYT)."""
    return chuan_hoa(tu_khoa) in chuan_hoa(gia_tri)


def khop(khoa, gia_tri, tu_khoa):
    """khoa = 'ho_ten' thì so khớp theo từ; các trường khác so khớp theo chuỗi."""
    if khoa == "ho_ten":
        return khop_ten(gia_tri, tu_khoa)
    return khop_chuoi(gia_tri, tu_khoa)


# ---------------------------------------------------------- kiểm tra dữ liệu nhập
def la_sdt_hop_le(sdt):
    return len(sdt) == 10 and sdt.isascii() and sdt.isdigit()


def la_email_hop_le(email):
    """Dạng đơn giản: ten@ten-mien.duoi, không có khoảng trắng."""
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


# ----------------------------------------------------------------- chọn ngày
def so_thang_toi_da(nam, hom_nay=None, gioi_han_hom_nay=True):
    """Ngày sinh: năm hiện tại chỉ được chọn đến tháng hiện tại.
    Lịch hẹn (gioi_han_hom_nay=False): luôn 12 tháng."""
    if not gioi_han_hom_nay:
        return 12
    hom_nay = hom_nay or date.today()
    return hom_nay.month if nam == hom_nay.year else 12


def so_ngay_toi_da(nam, thang, hom_nay=None, gioi_han_hom_nay=True):
    """Số ngày được chọn cho (năm, tháng); nam/thang có thể là None nếu chưa chọn.
    - tháng 4, 6, 9, 11: 30 ngày; các tháng còn lại: 31 ngày
    - tháng 2: 28 ngày, năm nhuận 29 ngày
    - chưa chọn năm mà chọn tháng 2: cho tối đa 29 (chờ chọn năm rồi cắt lại)
    - gioi_han_hom_nay=True: tháng hiện tại của năm hiện tại chỉ đến ngày hôm nay
    """
    hom_nay = hom_nay or date.today()
    if thang is None:
        ngay = 31
    else:
        nam_de_tinh = nam if nam is not None else 2000  # 2000 là năm nhuận
        ngay = calendar.monthrange(nam_de_tinh, thang)[1]
    if gioi_han_hom_nay and nam == hom_nay.year and thang == hom_nay.month:
        ngay = min(ngay, hom_nay.day)
    return ngay


# ------------------------------------------------------------------ giờ và lịch hẹn
def danh_sach_gio(tu_gio=7, den_gio=18, buoc_phut=15):
    return [f"{p // 60:02d}:{p % 60:02d}"
            for p in range(tu_gio * 60, den_gio * 60, buoc_phut)]


def gio_ra_phut(gio):
    gio_so, phut_so = gio.split(":")
    return int(gio_so) * 60 + int(phut_so)


def phut_ra_gio(phut):
    return f"{phut // 60:02d}:{phut % 60:02d}"


def gio_ket_thuc(gio_bat_dau, thoi_luong):
    return phut_ra_gio(gio_ra_phut(gio_bat_dau) + thoi_luong)


def tim_lich_trung(danh_sach, ma_bac_si, ngay, gio_bat_dau, thoi_luong, bo_qua_ma=None):
    bd = gio_ra_phut(gio_bat_dau)
    kt = bd + thoi_luong
    for lich in danh_sach:
        if lich["ma"] == bo_qua_ma:
            continue
        if lich["ma_bac_si"] != ma_bac_si or lich["ngay"] != ngay:
            continue
        bd_kia = gio_ra_phut(lich["gio"])
        kt_kia = bd_kia + lich["thoi_luong"]
        if bd < kt_kia and bd_kia < kt:
            return lich
    return None
