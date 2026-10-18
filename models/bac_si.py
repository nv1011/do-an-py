from models.nguoi import Nguoi
from config import hoc_vi
from utils.validators import nam_tu_ma_bac_si, la_ma_bac_si_hop_le
from datetime import date

class BacSi(Nguoi):
    def __init__(self, ma_dinh_danh, ho_ten, dia_chi, tinh_thanh, xa_phuong,
                 gioi_tinh, ngay_sinh, sdt, lich_lam_viec, luong_cb):
        if not la_ma_bac_si_hop_le(ma_dinh_danh):
            raise ValueError("Mã bác sĩ phải gồm 9 chữ số!")
        super().__init__(ma_dinh_danh, ho_ten, dia_chi, tinh_thanh, xa_phuong, gioi_tinh, ngay_sinh, sdt)
        self._lich_lam_viec=lich_lam_viec
        self.luong_cb=luong_cb

    @property
    def ma_chuyen_khoa(self):
        return self._ma_dinh_danh[2:4]

    @property
    def hoc_vi(self):
        return hoc_vi.get(self._ma_dinh_danh[0:2], "Không rõ")

    @property
    def nam_vao_lam(self):
        return nam_tu_ma_bac_si(self._ma_dinh_danh)

    @nam_vao_lam.setter
    def nam_vao_lam(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Năm vào làm phải là số!")
        if value > date.today().year or value < 1900:
            raise ValueError("Năm vào làm không hợp lệ!")
        if value != nam_tu_ma_bac_si(self._ma_dinh_danh):
            raise ValueError("Năm vào làm không khớp với mã bác sĩ!")
        self._nam_vao_lam = value

    @property
    def lich_lam_viec(self):
        return self._lich_lam_viec

    @property
    def luong_cb(self):
        return self._luong_cb

    @luong_cb.setter
    def luong_cb(self,value):
        if value < 0:
            raise ValueError("Lương cơ bản không hợp lệ!")
        self._luong_cb=value

    def to_dict(self):
        d = super().to_dict()
        d.update({
        "lich_lam_viec": self._lich_lam_viec,
        "luong_cb": self._luong_cb,
        })
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            **Nguoi._truong_chung_tu_dict(d),
            lich_lam_viec=d["lich_lam_viec"],
            luong_cb=d["luong_cb"],
        )
    
    def __str__(self):
        return super().__str__() + (f"Mã chuyên khoa: {self.ma_chuyen_khoa}\n"
            f"Học vị: {self.hoc_vi}\n"
            f"Năm vào làm: {self.nam_vao_lam}\n")