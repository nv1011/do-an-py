from utils.validators import la_ma_chuyen_khoa_hop_le, la_ma_dich_vu_hop_le


class DichVu:
    def __init__(self, ma_dich_vu, ten_dich_vu, ma_chuyen_khoa, don_gia, mo_ta="", trang_thai=True):
        if not la_ma_dich_vu_hop_le(ma_dich_vu):
            raise ValueError("Mã dịch vụ phải có dạng DV001!")
        self._ma_dich_vu = str(ma_dich_vu).strip()
        self.ten_dich_vu = ten_dich_vu
        self.ma_chuyen_khoa = ma_chuyen_khoa
        self.don_gia = don_gia
        self.mo_ta = mo_ta
        self.trang_thai = trang_thai

    @property
    def ma_dich_vu(self):
        return self._ma_dich_vu

    @property
    def ten_dich_vu(self):
        return self._ten_dich_vu

    @ten_dich_vu.setter
    def ten_dich_vu(self, value):
        val = str(value or "").strip()
        if not val:
            raise ValueError("Tên dịch vụ không được để trống!")
        self._ten_dich_vu = val

    @property
    def ma_chuyen_khoa(self):
        return self._ma_chuyen_khoa

    @ma_chuyen_khoa.setter
    def ma_chuyen_khoa(self, value):
        val = str(value or "").strip()
        if not la_ma_chuyen_khoa_hop_le(val):
            raise ValueError("Mã chuyên khoa không hợp lệ!")
        self._ma_chuyen_khoa = val

    @property
    def don_gia(self):
        return self._don_gia

    @don_gia.setter
    def don_gia(self, value):
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValueError("Đơn giá không hợp lệ!")
        if val < 0:
            raise ValueError("Đơn giá dịch vụ không thể âm!")
        self._don_gia = val

    @property
    def mo_ta(self):
        return self._mo_ta

    @mo_ta.setter
    def mo_ta(self, value):
        self._mo_ta = str(value or "").strip()

    @property
    def trang_thai(self):
        return self._trang_thai

    @trang_thai.setter
    def trang_thai(self, value):
        self._trang_thai = bool(value)

    def to_dict(self):
        return {
            "ma_dich_vu": self._ma_dich_vu,
            "ten_dich_vu": self._ten_dich_vu,
            "ma_chuyen_khoa": self._ma_chuyen_khoa,
            "don_gia": self._don_gia,
            "mo_ta": self._mo_ta,
            "trang_thai": self._trang_thai,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            ma_dich_vu=d["ma_dich_vu"],
            ten_dich_vu=d["ten_dich_vu"],
            ma_chuyen_khoa=d["ma_chuyen_khoa"],
            don_gia=d["don_gia"],
            mo_ta=d.get("mo_ta", ""),
            trang_thai=d.get("trang_thai", True),
        )

    def __str__(self):
        return (f"Dịch vụ: {self._ma_dich_vu} {self._ten_dich_vu}\n"
                f"Chuyên khoa: {self._ma_chuyen_khoa}\n"
                f"Mô tả: {self._mo_ta}\n"
                f"Đơn giá: {self._don_gia}\n"
                f"Trạng thái: {self._trang_thai}\n")
