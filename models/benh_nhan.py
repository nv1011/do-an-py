from models.nguoi import Nguoi
from datetime import date

class BenhNhan(Nguoi):
    def __init__(self, ma_dinh_danh, ho_ten, dia_chi, gioi_tinh, ngay_sinh, sdt, so_bhyt, tien_su_benh, nhom_mau, ngay_tham_kham ):
        super().__init__(ma_dinh_danh, ho_ten, dia_chi, gioi_tinh, ngay_sinh, sdt)
        self.so_bhyt=so_bhyt
        self._tien_su_benh=tien_su_benh
        self._nhom_mau=nhom_mau
        self._ngay_tham_kham=ngay_tham_kham

    @property
    def so_bhyt(self):
        return self.so_bhyt

    @so_bhyt.setter
    def so_bhyt(self,value):
        if not value.strip():
            self.so_bhyt="Không có"
        else:
            self.so_bhyt=value

    @property
    def tien_su_benh(self):
        return self._tien_su_benh

    @property
    def nhom_mau(self):
        return self._nhom_mau

    @property
    def ngay_tham_kham(self):
        return self._ngay_tham_kham

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "so_bhyt": self._so_bhyt,
            "tien_su_benh": self._tien_su_benh,
            "nhom_mau": self._nhom_mau,
            "ngay_tham_kham": self._ngay_tham_kham      
        })
        return d

    def from_dict(cls, d):
        return cls(
                    **Nguoi._truong_chung_tu_dict(d),
                    so_bhyt=d["so_bhyt"],
                    tien_su_benh=d["tien_su_benh"],
                    nhom_mau=d["nhom_mau"],
                    ngay_tham_kham=d["ngay_tham_kham"],
                )
    
    def __str__(self):
            return super().__str__() + (f"Số BHYT: {self._so_bhyt}\n"
                 f"Nhóm máu: {self._nhom_mau}\n"
                 f"Tiền sử bệnh: {self._tien_su_benh}\n"
                 f"Ngày thăm khám: {self._ngay_tham_kham}\n")
        