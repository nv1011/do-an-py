"""Tài khoản giả để thử giao diện."""
import hashlib
import re

MAU_TEN_DANG_NHAP = re.compile(r"[A-Za-z0-9_]{3,20}")
DO_DAI_MAT_KHAU_TOI_THIEU = 6
DO_DAI_MAT_KHAU_TOI_DA = 32


def _bam(mat_khau):
    return hashlib.sha256(mat_khau.encode("utf-8")).hexdigest()


_TAI_KHOAN = {
    "admin": (_bam("admin123"), "admin"),
    "letan": (_bam("letan123"), "le_tan"),
}


def xac_thuc(ten, mat_khau):
    thong_tin = _TAI_KHOAN.get(ten)
    if thong_tin and thong_tin[0] == _bam(mat_khau):
        return thong_tin[1]
    return None


def kiem_tra_mat_khau_moi(ten, mat_khau, nhap_lai):
    """Ném ValueError nếu mật khẩu mới không hợp lệ."""
    if not mat_khau:
        raise ValueError("Mật khẩu không được để trống.")
    if not DO_DAI_MAT_KHAU_TOI_THIEU <= len(mat_khau) <= DO_DAI_MAT_KHAU_TOI_DA:
        raise ValueError(f"Mật khẩu phải dài từ {DO_DAI_MAT_KHAU_TOI_THIEU} "
                         f"đến {DO_DAI_MAT_KHAU_TOI_DA} ký tự.")
    if " " in mat_khau:
        raise ValueError("Mật khẩu không được chứa khoảng trắng.")
    if mat_khau.lower() == ten.lower():
        raise ValueError("Mật khẩu không được trùng với tên đăng nhập.")
    if mat_khau != nhap_lai:
        raise ValueError("Mật khẩu nhập lại không khớp.")


def tao_tai_khoan(ten, mat_khau, nhap_lai):
    """Tạo tài khoản mới, vai trò mặc định là le_tan."""
    ten = ten.strip()
    if not ten:
        raise ValueError("Tên đăng nhập không được để trống.")
    if not MAU_TEN_DANG_NHAP.fullmatch(ten):
        raise ValueError("Tên đăng nhập gồm 3-20 ký tự: chữ không dấu, số hoặc dấu gạch dưới.")
    if ten.lower() in (k.lower() for k in _TAI_KHOAN):
        raise ValueError("Tên đăng nhập đã tồn tại.")
    kiem_tra_mat_khau_moi(ten, mat_khau, nhap_lai)
    _TAI_KHOAN[ten] = (_bam(mat_khau), "le_tan")
    return "le_tan"


def doi_mat_khau(ten, mat_khau_cu, mat_khau_moi, nhap_lai):
    if xac_thuc(ten, mat_khau_cu) is None:
        raise ValueError("Mật khẩu hiện tại không đúng.")
    kiem_tra_mat_khau_moi(ten, mat_khau_moi, nhap_lai)
    if mat_khau_moi == mat_khau_cu:
        raise ValueError("Mật khẩu mới phải khác mật khẩu hiện tại.")
    _TAI_KHOAN[ten] = (_bam(mat_khau_moi), _TAI_KHOAN[ten][1])
