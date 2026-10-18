"""Tiện ích dùng chung toàn hệ thống: tìm kiếm tiếng Việt, ngày tháng, giờ giấc và kiểm tra dữ liệu."""
import calendar
import re
import unicodedata
from datetime import date

# Hằng số năm nhỏ nhất cho bộ chọn ngày
NAM_NHO_NHAT = 1900


# ------------------------------------------------------------------ Tìm kiếm tiếng Việt
def bo_dau(chuoi: str) -> str:
    """'Nguyễn Đức' -> 'Nguyen Duc' (bỏ dấu tiếng Việt)."""
    chuoi = chuoi.replace("đ", "d").replace("Đ", "D")  # đ không tách được bằng NFD
    phan_tach = unicodedata.normalize("NFD", chuoi)
    return "".join(c for c in phan_tach if unicodedata.category(c) != "Mn")


def chuan_hoa(chuoi: str) -> str:
    """Bỏ dấu, viết thường, gộp khoảng trắng thừa."""
    return " ".join(bo_dau(chuoi).lower().split())


def khop_ten(ten: str, tu_khoa: str) -> bool:
    """Mỗi từ trong từ khóa phải là phần ĐẦU của một từ nào đó trong tên.

    VD: 'an' -> khớp 'Nguyễn Văn An'; 'van an' -> khớp 'Nguyễn Văn An'.
    """
    cac_tu_khoa = chuan_hoa(tu_khoa).split()
    cac_tu_ten = chuan_hoa(ten).split()
    return all(any(tu.startswith(tk) for tu in cac_tu_ten) for tk in cac_tu_khoa)


def khop_chuoi(gia_tri: str, tu_khoa: str) -> bool:
    """Từ khóa nằm ở bất kỳ đâu trong giá trị (dùng cho mã, SĐT, BHYT)."""
    return chuan_hoa(tu_khoa) in chuan_hoa(gia_tri)


def khop(khoa: str, gia_tri: str, tu_khoa: str) -> bool:
    """Nếu khoa == 'ho_ten' thì so khớp theo từ; các trường khác so khớp theo chuỗi con."""
    if khoa == "ho_ten":
        return khop_ten(gia_tri, tu_khoa)
    return khop_chuoi(gia_tri, tu_khoa)


# ------------------------------------------------------------------ Kiểm tra dữ liệu nhập
def la_sdt_hop_le(sdt) -> bool:
    """Số điện thoại di động Việt Nam: đúng 10 chữ số, bắt đầu bằng số 0."""
    s = str(sdt).strip()
    return bool(re.fullmatch(r"0\d{9}", s))


def la_email_hop_le(email: str) -> bool:
    """Dạng đơn giản: ten@ten-mien.duoi, không có khoảng trắng."""
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(email).strip()))


# ------------------------------------------------------------------ Chọn ngày (DatePicker)
def so_thang_toi_da(nam, hom_nay: date = None, gioi_han_hom_nay: bool = True) -> int:
    """Ngày sinh: năm hiện tại chỉ được chọn đến tháng hiện tại.

    Lịch hẹn (gioi_han_hom_nay=False): luôn 12 tháng.
    """
    if not gioi_han_hom_nay:
        return 12
    hom_nay = hom_nay or date.today()
    return hom_nay.month if nam == hom_nay.year else 12


def so_ngay_toi_da(nam, thang, hom_nay: date = None, gioi_han_hom_nay: bool = True) -> int:
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


# ------------------------------------------------------------------ Giờ và lịch hẹn
def danh_sach_gio(tu_gio: int = 7, den_gio: int = 18, buoc_phut: int = 15) -> list[str]:
    """Tạo danh sách các mốc giờ khám bệnh (VD: ['07:00', '07:15', ...])."""
    return [
        f"{p // 60:02d}:{p % 60:02d}"
        for p in range(tu_gio * 60, den_gio * 60, buoc_phut)
    ]


def gio_ra_phut(gio: str) -> int:
    """Chuyển đổi chuỗi 'HH:MM' sang số phút tính từ 00:00."""
    gio_so, phut_so = gio.split(":")
    return int(gio_so) * 60 + int(phut_so)


def phut_ra_gio(phut: int) -> str:
    """Chuyển đổi số phút sang chuỗi 'HH:MM'."""
    return f"{phut // 60:02d}:{phut % 60:02d}"


def gio_ket_thuc(gio_bat_dau: str, thoi_luong: int) -> str:
    """Tính giờ kết thúc = giờ bắt đầu + thời lượng (phút)."""
    return phut_ra_gio(gio_ra_phut(gio_bat_dau) + thoi_luong)


def tim_lich_trung(danh_sach: list[dict], ma_bac_si: str, ngay, gio_bat_dau: str, thoi_luong: int, bo_qua_ma: str = None) -> dict | None:
    """Kiểm tra xung đột thời gian giữa các ca khám của cùng một bác sĩ trong ngày."""
    bd = gio_ra_phut(gio_bat_dau)
    kt = bd + thoi_luong
    for lich in danh_sach:
        if bo_qua_ma and (lich.get("ma") == bo_qua_ma or lich.get("ma_lich_hen") == bo_qua_ma):
            continue
        bs = lich.get("ma_bac_si")
        ng = lich.get("ngay") or lich.get("ngay_hen")
        if bs != ma_bac_si or ng != ngay:
            continue
        g = lich.get("gio") or lich.get("gio_bat_dau")
        tl = lich.get("thoi_luong", 30)
        bd_kia = gio_ra_phut(g)
        kt_kia = bd_kia + tl
        if bd < kt_kia and bd_kia < kt:
            return lich
    return None
