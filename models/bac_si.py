from models.nguoi import Nguoi
from config import HOC_VI, hoc_vi
from utils.validators import nam_tu_ma_bac_si, la_ma_bac_si_hop_le
from datetime import date

class BacSi(Nguoi):
    def __init__(self, ma_dinh_danh, ho_ten, dia_chi, tinh_thanh, xa_phuong,
                 gioi_tinh, ngay_sinh, sdt, lich_lam_viec, luong_cb):
        if not la_ma_bac_si_hop_le(ma_dinh_danh):
            raise ValueError("Mã bác sĩ phải gồm 9 chữ số!")
        
        # Bỏ tiền tố học vị khỏi họ tên nếu có (tránh trùng lặp với học vị suy ra từ mã)
        clean_ho_ten = (ho_ten or "").strip()
        for tien_to in ("TS. ", "BS. ", "ThS. ", "TS ", "BS ", "ThS "):
            if clean_ho_ten.startswith(tien_to):
                clean_ho_ten = clean_ho_ten[len(tien_to):].strip()
                break

        super().__init__(ma_dinh_danh, clean_ho_ten, dia_chi, tinh_thanh, xa_phuong, gioi_tinh, ngay_sinh, sdt)
        self.lich_lam_viec = lich_lam_viec
        self.luong_cb = luong_cb

    @property
    def ma_chuyen_khoa(self):
        """Mã chuyên khoa (2 ký tự vị trí 2:4)."""
        return self._ma_dinh_danh[2:4]

    @property
    def hoc_vi(self):
        """Tên học vị giải mã từ 2 ký tự đầu theo config.HOC_VI."""
        return HOC_VI.get(self._ma_dinh_danh[0:2], "Không rõ")

    @property
    def nam_vao_lam(self):
        """Năm vào làm (4 chữ số) suy ra từ 2 chữ số năm trong mã bác sĩ."""
        return nam_tu_ma_bac_si(self._ma_dinh_danh)

    @property
    def lich_lam_viec(self):
        return self._lich_lam_viec

    @lich_lam_viec.setter
    def lich_lam_viec(self, value):
        if isinstance(value, str):
            value = [c.strip() for c in value.split(",") if c.strip()]
        if not isinstance(value, list):
            raise ValueError("Lịch làm việc phải là danh sách (list) các ca trực!")
        self._lich_lam_viec = value

    @property
    def luong_cb(self):
        return self._luong_cb

    @luong_cb.setter
    def luong_cb(self, value):
        if value < 0:
            raise ValueError("Lương cơ bản không hợp lệ!")
        self._luong_cb = value

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
            f"Năm vào làm: {self.nam_vao_lam}\n"
            f"Lịch làm việc: {', '.join(self.lich_lam_viec)}\n")