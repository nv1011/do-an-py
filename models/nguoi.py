from abc import ABC, abstractmethod
from datetime import date

class Nguoi(ABC):
    def __init__(self,ma_dinh_danh, ho_ten, dia_chi, tinh_thanh, xa_phuong, gioi_tinh, ngay_sinh, sdt):
        self._ma_dinh_danh=ma_dinh_danh
        self.ho_ten=ho_ten
        self._gioi_tinh=gioi_tinh
        self._ngay_sinh=ngay_sinh
        self._dia_chi=dia_chi
        self._tinh_thanh = tinh_thanh
        self._xa_phuong = xa_phuong
        self.sdt=sdt


    @property
    def tinh_thanh(self):
        return self._tinh_thanh

    @tinh_thanh.setter
    def tinh_thanh(self, value):
        if not value or not value.strip():
            raise ValueError("Tỉnh/Thành phố không được rỗng!")
        self._tinh_thanh = value.strip()

    @property
    def xa_phuong(self):
        return self._xa_phuong

    @xa_phuong.setter
    def xa_phuong(self, value):
        if not value or not value.strip():
            raise ValueError("Xã/Phường không được rỗng!")
        self._xa_phuong = value.strip()

    @property
    def dia_chi_day_du(self):
        return f"{self._dia_chi}, {self._xa_phuong}, {self._tinh_thanh}"

    @property
    def ma_dinh_danh(self):
        return self._ma_dinh_danh

    @property
    def gioi_tinh(self):
        return self._gioi_tinh

    @property
    def tuoi(self):
        hom_nay = date.today()
        n = self._ngay_sinh
        return hom_nay.year - n.year - ((hom_nay.month, hom_nay.day) < (n.month, n.day))

    @property
    def ho_ten(self):
        return self._ho_ten

    @ho_ten.setter
    def ho_ten(self, value):
        if not value or not value.strip():
            raise ValueError("Họ tên không được rỗng")
        self._ho_ten = value.strip()

    @property
    def sdt(self):
        return self._sdt

    @sdt.setter
    def sdt(self, value):   
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("SĐT không hợp lệ")
        self._sdt = value

    @abstractmethod
    def to_dict(self):
        return {"ma_dinh_danh": self._ma_dinh_danh,
                "ho_ten": self._ho_ten,
                "dia_chi": self._dia_chi,
                "tinh_thanh": self._tinh_thanh,
                "xa_phuong": self._xa_phuong,
                "gioi_tinh": self._gioi_tinh,
                "ngay_sinh": str(self._ngay_sinh),
                "sdt": self._sdt,
        }

    @staticmethod
    def _truong_chung_tu_dict(d):
        return {
            "ma_dinh_danh": d["ma_dinh_danh"],
            "ho_ten": d["ho_ten"],
            "dia_chi": d["dia_chi"],
            "tinh_thanh": d["tinh_thanh"],
            "xa_phuong": d["xa_phuong"],
            "gioi_tinh": d["gioi_tinh"],
            "ngay_sinh": date.fromisoformat(d["ngay_sinh"]),
            "sdt": d["sdt"],
        }
    
    def __str__(self):
        return (f"Mã: {self.ma_dinh_danh}\n"
            f"Họ tên: {self.ho_ten}\n"
            f"SĐT: {self.sdt}\n")
    
    
    
