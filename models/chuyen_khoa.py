from utils.validators import la_ma_chuyen_khoa_hop_le


class ChuyenKhoa:


    def __init__(self, ma_chuyen_khoa, ten_chuyen_khoa, mo_ta=""):
        self.ma_chuyen_khoa = ma_chuyen_khoa
        self.ten_chuyen_khoa = ten_chuyen_khoa
        self.mo_ta = mo_ta

    @property
    def ma_chuyen_khoa(self):
        return self._ma_chuyen_khoa

    @ma_chuyen_khoa.setter
    def ma_chuyen_khoa(self, value):
        val = str(value).strip() if value is not None else ""
        if not la_ma_chuyen_khoa_hop_le(val):
            raise ValueError("Mã chuyên khoa không hợp lệ (phải gồm đúng 2 chữ số, VD: '01', '02')!")
        self._ma_chuyen_khoa = val

    @property
    def ten_chuyen_khoa(self):
        return self._ten_chuyen_khoa

    @ten_chuyen_khoa.setter
    def ten_chuyen_khoa(self, value):
        val = str(value).strip() if value is not None else ""
        if not val:
            raise ValueError("Tên chuyên khoa không được để trống!")
        self._ten_chuyen_khoa = val

    @property
    def mo_ta(self):
        return self._mo_ta

    @mo_ta.setter
    def mo_ta(self, value):
        self._mo_ta = str(value).strip() if value is not None else ""

    def to_dict(self):
        """Tuần tự hóa đối tượng ChuyenKhoa thành dictionary chuẩn để lưu JSON."""
        return {
            "ma_chuyen_khoa": self._ma_chuyen_khoa,
            "ten_chuyen_khoa": self._ten_chuyen_khoa,
            "mo_ta": self._mo_ta,
        }

    @classmethod
    def from_dict(cls, d):
        """Khởi tạo đối tượng ChuyenKhoa từ dictionary đọc từ JSON."""
        return cls(
            ma_chuyen_khoa=d["ma_chuyen_khoa"],
            ten_chuyen_khoa=d["ten_chuyen_khoa"],
            mo_ta=d.get("mo_ta", ""),
        )

    def __str__(self):
        return f"[{self._ma_chuyen_khoa}] {self._ten_chuyen_khoa}"

    def __repr__(self):
        return f"ChuyenKhoa(ma='{self._ma_chuyen_khoa}', ten='{self._ten_chuyen_khoa}')"

    def __eq__(self, other):
        if isinstance(other, ChuyenKhoa):
            return self._ma_chuyen_khoa == other._ma_chuyen_khoa
        return False

    def __hash__(self):
        return hash(self._ma_chuyen_khoa)
