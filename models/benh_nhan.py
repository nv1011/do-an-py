from models.nguoi import Nguoi
from utils.validators import la_email_hop_le, la_ma_benh_nhan_hop_le, ngay_tu_ma_benh_nhan, la_ma_bhyt_hop_le
from datetime import date

class BenhNhan(Nguoi):
    def __init__(self, ma_dinh_danh, ho_ten, dia_chi, tinh_thanh, xa_phuong, gioi_tinh, ngay_sinh, sdt, so_bhyt, tien_su_benh, nhom_mau, email):
        if not la_ma_benh_nhan_hop_le(ma_dinh_danh):
            raise ValueError("Mã bệnh nhân phải gồm 14 chữ số, 8 số đầu là ngày hợp lệ!")
        super().__init__(ma_dinh_danh, ho_ten, dia_chi, tinh_thanh, xa_phuong, gioi_tinh, ngay_sinh, sdt)
        self.so_bhyt = so_bhyt
        self._tien_su_benh = (tien_su_benh or "Không có").strip()
        self.nhom_mau = nhom_mau
        self.email = email

    @property
    def so_bhyt(self):
        return self._so_bhyt

    @so_bhyt.setter
    def so_bhyt(self, value):
        val = (value or "").strip()
        if not val or val == "Không có":
            self._so_bhyt = "Không có"
        else:
            if not la_ma_bhyt_hop_le(val):
                raise ValueError("Số thẻ BHYT không hợp lệ!")
            self._so_bhyt = val

    @property
    def tien_su_benh(self):
        return self._tien_su_benh

    @tien_su_benh.setter
    def tien_su_benh(self, value):
        self._tien_su_benh = (value or "Không có").strip()

    @property
    def nhom_mau(self):
        return self._nhom_mau

    @nhom_mau.setter
    def nhom_mau(self, value):
        val = (value or "Chưa rõ").strip().upper()
        if val not in ("A", "B", "AB", "O", "CHƯA RÕ", "CHUA RO"):
            raise ValueError("Nhóm máu phải thuộc: A, B, AB, O hoặc Chưa rõ!")
        self._nhom_mau = "Chưa rõ" if val in ("CHƯA RÕ", "CHUA RO") else val

    @property
    def ngay_dang_ky(self):
        return ngay_tu_ma_benh_nhan(self._ma_dinh_danh)

    @property
    def ngay_tham_kham(self):
        """Thuộc tính tương thích ngược với ngay_dang_ky."""
        return self.ngay_dang_ky

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        value = (value or "").strip()
        if value and not la_email_hop_le(value):
            raise ValueError("Email không hợp lệ!")
        self._email = value

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "so_bhyt": self._so_bhyt,
            "email": self._email,
            "tien_su_benh": self._tien_su_benh,
            "nhom_mau": self._nhom_mau,
            "ngay_dang_ky": str(self.ngay_dang_ky)
        })
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
                    **Nguoi._truong_chung_tu_dict(d),
                    so_bhyt=d["so_bhyt"],
                    email=d["email"],
                    tien_su_benh=d["tien_su_benh"],
                    nhom_mau=d["nhom_mau"],
                )
    
    def __str__(self):
            return super().__str__() + (f"Số BHYT: {self._so_bhyt}\n"
                 f"Nhóm máu: {self._nhom_mau}\n"
                 f"Tiền sử bệnh: {self._tien_su_benh}\n"
                 f"Ngày đăng ký: {self.ngay_dang_ky}\n")
        