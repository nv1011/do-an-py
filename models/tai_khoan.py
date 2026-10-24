
import re
from datetime import date, datetime
from config import DANH_SACH_VAI_TRO, VAI_TRO_ADMIN, VAI_TRO_LE_TAN
from utils.validators import tao_salt, bam_mat_khau, xac_thuc_mat_khau


class TaiKhoan:

    def __init__(self, ten_dang_nhap, mat_khau_hash, salt,
                 vai_tro, trang_thai=True, ngay_tao=None):
        self.ten_dang_nhap = ten_dang_nhap
        self.mat_khau_hash = mat_khau_hash
        self.salt = salt
        self.vai_tro = vai_tro
        self.trang_thai = trang_thai

        if ngay_tao is None:
            self._ngay_tao = date.today()
        elif isinstance(ngay_tao, str):
            self._ngay_tao = date.fromisoformat(ngay_tao.strip())
        elif isinstance(ngay_tao, date):
            self._ngay_tao = ngay_tao
        else:
            raise ValueError("Ngày tạo tài khoản không hợp lệ!")

    @property
    def ten_dang_nhap(self):
        return self._ten_dang_nhap

    @ten_dang_nhap.setter
    def ten_dang_nhap(self, value):
        val = (value or "").strip()
        if len(val) < 3:
            raise ValueError("Tên đăng nhập phải có ít nhất 3 ký tự!")
        if " " in val:
            raise ValueError("Tên đăng nhập không được chứa khoảng trắng!")
        if not re.fullmatch(r"^[a-zA-Z0-9_]+$", val):
            raise ValueError("Tên đăng nhập chỉ được gồm chữ cái, chữ số và dấu gạch dưới!")
        self._ten_dang_nhap = val

    @property
    def mat_khau_hash(self):
        return self._mat_khau_hash

    @mat_khau_hash.setter
    def mat_khau_hash(self, value):
        val = (value or "").strip()
        if not re.fullmatch(r"^[a-fA-F0-9]{64}$", val):
            raise ValueError("Mã băm mật khẩu phải là chuỗi SHA-256 (64 ký tự hex)!")
        self._mat_khau_hash = val.lower()

    @property
    def salt(self):
        return self._salt

    @salt.setter
    def salt(self, value):
        val = (value or "").strip()
        if not re.fullmatch(r"^[a-fA-F0-9]{32}$", val):
            raise ValueError("Chuỗi salt phải là 32 ký tự hex!")
        self._salt = val.lower()

    @property
    def vai_tro(self):
        """Vai trò sử dụng hệ thống ('admin' hoặc 'le_tan')."""
        return self._vai_tro

    @vai_tro.setter
    def vai_tro(self, value):
        val = (value or "").strip().lower()
        if val not in DANH_SACH_VAI_TRO:
            hop_le = ", ".join(DANH_SACH_VAI_TRO)
            raise ValueError(f"Vai trò không hợp lệ! Chỉ chấp nhận: {hop_le}")
        self._vai_tro = val

    @property
    def trang_thai(self):
        return self._trang_thai

    @trang_thai.setter
    def trang_thai(self, value):
        self._trang_thai = bool(value)

    @property
    def ngay_tao(self):
        return self._ngay_tao

    def xac_thuc(self, mat_khau_nhap):
        if not mat_khau_nhap:
            return False
        return xac_thuc_mat_khau(mat_khau_nhap, self._salt, self._mat_khau_hash)

    def doi_mat_khau(self, mat_khau_moi):
        val = (mat_khau_moi or "").strip()
        if len(val) < 6:
            raise ValueError("Mật khẩu mới phải có ít nhất 6 ký tự!")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", val):
            raise ValueError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt!")
            
        salt_moi = tao_salt()
        hash_moi = bam_mat_khau(val, salt_moi)
        self._salt = salt_moi
        self._mat_khau_hash = hash_moi

    def khoa(self):
        self._trang_thai = False

    def mo_khoa(self):
        self._trang_thai = True

    def to_dict(self):
        return {
            "ten_dang_nhap": self._ten_dang_nhap,
            "mat_khau_hash": self._mat_khau_hash,
            "salt": self._salt,
            "vai_tro": self._vai_tro,
            "trang_thai": self._trang_thai,
            "ngay_tao": str(self._ngay_tao),
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            ten_dang_nhap=d["ten_dang_nhap"],
            mat_khau_hash=d["mat_khau_hash"],
            salt=d["salt"],
            vai_tro=d["vai_tro"],
            trang_thai=d.get("trang_thai", True),
            ngay_tao=d.get("ngay_tao"),
        )

    @classmethod
    def tao_moi(cls, ten_dang_nhap, mat_khau_tho, vai_tro):
        val = (mat_khau_tho or "").strip()
        if len(val) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự!")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", val):
            raise ValueError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt!")

        salt = tao_salt()
        mk_hash = bam_mat_khau(val, salt)
        return cls(
            ten_dang_nhap=ten_dang_nhap,
            mat_khau_hash=mk_hash,
            salt=salt,
            vai_tro=vai_tro,
            trang_thai=True,
            ngay_tao=date.today(),
        )

    def __str__(self):
        tt = "Đang hoạt động" if self._trang_thai else "Bị khóa"
        return f"Tài khoản: {self._ten_dang_nhap} | Vai trò: {self._vai_tro} | Trạng thái: {tt} | Ngày tạo: {self._ngay_tao}"