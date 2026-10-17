"""Hàm thuần cho giao diện (không dùng tkinter nên dễ kiểm tra):
- tìm kiếm không cần chính xác (bỏ dấu, không phân biệt hoa/thường)
- tính số tháng/số ngày hợp lệ cho bộ chọn ngày sinh
"""
import calendar
import unicodedata
from datetime import date

NAM_NHO_NHAT = 1900


# ------------------------------------------------------------ tìm kiếm
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


# ------------------------------------------------------------ ngày sinh
def so_thang_toi_da(nam, hom_nay=None):
    """Năm hiện tại chỉ được chọn đến tháng hiện tại (không có ngày sinh ở tương lai)."""
    hom_nay = hom_nay or date.today()
    return hom_nay.month if nam == hom_nay.year else 12


def so_ngay_toi_da(nam, thang, hom_nay=None):
    """Số ngày được chọn cho (năm, tháng); nam/thang có thể là None nếu chưa chọn.
    - tháng 4, 6, 9, 11: 30 ngày; các tháng còn lại: 31 ngày
    - tháng 2: 28 ngày, năm nhuận 29 ngày
    - chưa chọn năm mà chọn tháng 2: cho tối đa 29 (chờ chọn năm rồi cắt lại)
    - tháng hiện tại của năm hiện tại: chỉ đến ngày hôm nay
    """
    hom_nay = hom_nay or date.today()
    if thang is None:
        ngay = 31
    else:
        nam_de_tinh = nam if nam is not None else 2000  # 2000 là năm nhuận
        ngay = calendar.monthrange(nam_de_tinh, thang)[1]
    if nam == hom_nay.year and thang == hom_nay.month:
        ngay = min(ngay, hom_nay.day)
    return ngay
