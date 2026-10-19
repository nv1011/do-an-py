"""Hàm xử lý không dùng tkinter: tìm kiếm, ngày, giờ, kiểm tra dữ liệu."""
import calendar
import unicodedata
from datetime import date

NAM_NHO_NHAT = 1900


# ------------------------------------------------------------ tìm kiếm
def bo_dau(chuoi):
    """'Nguyễn Đức' -> 'Nguyen Duc'."""
    chuoi = chuoi.replace("đ", "d").replace("Đ", "D")
    phan_tach = unicodedata.normalize("NFD", chuoi)
    return "".join(c for c in phan_tach if unicodedata.category(c) != "Mn")


def chuan_hoa(chuoi):
    """Bỏ dấu, viết thường, gộp khoảng trắng thừa."""
    return " ".join(bo_dau(chuoi).lower().split())


def khop_ten(ten, tu_khoa):
    """Mỗi từ trong từ khóa phải là phần ĐẦU của một từ nào đó trong tên."""
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


# ------------------------------------------------------------ kiểm tra dữ liệu nhập
def dinh_dang_tien(so):
    """150000 -> '150.000 đ'."""
    return f"{so:,}".replace(",", ".") + " đ"


# ------------------------------------------------------------ chọn ngày
def so_thang_toi_da(nam, hom_nay=None, gioi_han_hom_nay=True):
    """Ngày sinh: năm hiện tại chỉ được chọn đến tháng hiện tại."""
    if not gioi_han_hom_nay:
        return 12
    hom_nay = hom_nay or date.today()
    return hom_nay.month if nam == hom_nay.year else 12


def so_ngay_toi_da(nam, thang, hom_nay=None, gioi_han_hom_nay=True):
    """Số ngày được chọn cho (năm, tháng); nam/thang có thể là None nếu chưa chọn."""
    hom_nay = hom_nay or date.today()
    if thang is None:
        ngay = 31
    else:
        nam_de_tinh = nam if nam is not None else 2000
        ngay = calendar.monthrange(nam_de_tinh, thang)[1]
    if gioi_han_hom_nay and nam == hom_nay.year and thang == hom_nay.month:
        ngay = min(ngay, hom_nay.day)
    return ngay


# ------------------------------------------------------------ giờ và lịch hẹn
def danh_sach_gio(tu_gio=7, den_gio=18, buoc_phut=15):
    """['07:00', '07:15', ..., '17:45']."""
    return [f"{p // 60:02d}:{p % 60:02d}"
            for p in range(tu_gio * 60, den_gio * 60, buoc_phut)]


def gio_ra_phut(gio):
    """'08:30' -> 510."""
    gio_so, phut_so = gio.split(":")
    return int(gio_so) * 60 + int(phut_so)


def phut_ra_gio(phut):
    """510 -> '08:30'."""
    return f"{phut // 60:02d}:{phut % 60:02d}"


def gio_ket_thuc(gio_bat_dau, thoi_luong):
    """('08:00', 30) -> '08:30'."""
    return phut_ra_gio(gio_ra_phut(gio_bat_dau) + thoi_luong)


def tim_lich_trung(danh_sach, ma_bac_si, ngay, gio_bat_dau, thoi_luong, bo_qua_ma=None):
    """Tìm một lịch của CÙNG bác sĩ, CÙNG ngày, có khoảng giờ chồng lên khoảng giờ mới."""
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
