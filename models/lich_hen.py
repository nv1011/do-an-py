from utils.helpers import so_ngay_toi_da, so_thang_toi_da
from utils.validators import la_ma_bac_si_hop_le, la_ma_benh_nhan_hop_le, la_ngay_hop_le
from config import BUOC_THOI_LUONG_PHUT, GIO_BAT_DAU_KHAM, GIO_KET_THUC_KHAM
import re
from datetime import date, datetime

class LichHen:
    def __init__(self, ma_lich_hen, ma_benh_nhan, ma_bac_si, ngay_hen, gio_bat_dau, thoi_luong, trang_thai, ly_do_kham):
        if not re.fullmatch(r"LH\d{3,}", ma_lich_hen):
            raise ValueError("Mã lịch hẹn phải có dạng LH001!")
        if not la_ma_benh_nhan_hop_le(ma_benh_nhan):
            raise ValueError("Mã bệnh nhân không hợp lệ!")
        self._ma_lich_hen = ma_lich_hen
        self._ma_benh_nhan = ma_benh_nhan
        self.ma_bac_si = ma_bac_si
        self.ngay_hen = ngay_hen
        self.gio_bat_dau = gio_bat_dau
        self.thoi_luong = thoi_luong
        self.trang_thai = trang_thai
        self.ly_do_kham = ly_do_kham

    @property
    def ma_lich_hen(self):
        return self._ma_lich_hen

    @property
    def ma_benh_nhan(self):
        return self._ma_benh_nhan

    @property
    def ma_bac_si(self):
        return self._ma_bac_si

    @ma_bac_si.setter
    def ma_bac_si(self, value):
        if not la_ma_bac_si_hop_le(value):
            raise ValueError("Mã bác sĩ không hợp lệ!")
        self._ma_bac_si = value

    @property
    def thoi_luong(self):
        return self._thoi_luong

    @thoi_luong.setter
    def thoi_luong(self, value):
        if not isinstance(value, int) or value <= 0 or value % BUOC_THOI_LUONG_PHUT != 0:
            raise ValueError(f"Thời lượng phải là bội số của {BUOC_THOI_LUONG_PHUT} phút!")
        self._thoi_luong = value

    @property
    def gio_bat_dau(self):
        return self._gio_bat_dau
    
    @gio_bat_dau.setter
    def gio_bat_dau(self, value):
        if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", str(value)):
            raise ValueError("Giờ bắt đầu phải có dạng HH:MM!")
        if not GIO_BAT_DAU_KHAM <= value < GIO_KET_THUC_KHAM:
            raise ValueError(f"Giờ khám phải từ {GIO_BAT_DAU_KHAM} đến {GIO_KET_THUC_KHAM}!")
        self._gio_bat_dau = value

    @property
    def gio_ket_thuc(self):
        gio, phut = map(int, self._gio_bat_dau.split(":"))
        tong = gio * 60 + phut + self._thoi_luong
        return f"{tong // 60:02d}:{tong % 60:02d}"

    @property
    def ngay_hen(self):
        return self._ngay_hen

    @ngay_hen.setter
    def ngay_hen(self, value):
        if isinstance(value, str):
            value = value.strip()
            parsed = False
            for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                try:
                    value = datetime.strptime(value, fmt).date()
                    parsed = True
                    break
                except ValueError:
                    continue
            if not parsed:
                raise ValueError("Ngày hẹn phải có định dạng YYYY-MM-DD hoặc DD-MM-YYYY!")
        elif isinstance(value, datetime):
            value = value.date()
        elif not isinstance(value, date):
            raise ValueError("Ngày hẹn không hợp lệ!")
        
        if not la_ngay_hop_le(value.day, value.month, value.year):
            raise ValueError("Ngày hẹn không tồn tại trên thực tế!")
        self._ngay_hen = value

    @property
    def trang_thai(self):
        return self._trang_thai

    @trang_thai.setter
    def trang_thai(self, value):
        val = (value or "").strip()
        trang_thai_hop_le = ("Cho_kham", "Da_kham", "Da_huy", "Vang")
        if val not in trang_thai_hop_le:
            raise ValueError(f"Trạng thái lịch hẹn phải thuộc: {', '.join(trang_thai_hop_le)}")
        self._trang_thai = val

    @property
    def ly_do_kham(self):
        return self._ly_do_kham

    @ly_do_kham.setter
    def ly_do_kham(self, value):
        self._ly_do_kham = (value or "").strip()

    def to_dict(self):
        return {
            "ma_lich_hen": self._ma_lich_hen,
            "ma_benh_nhan": self._ma_benh_nhan,
            "ma_bac_si": self._ma_bac_si,
            "ngay_hen": str(self._ngay_hen),
            "gio_bat_dau": self._gio_bat_dau,
            "thoi_luong": self._thoi_luong,
            "trang_thai": self._trang_thai,
            "ly_do_kham": self._ly_do_kham,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            ma_lich_hen=d["ma_lich_hen"],
            ma_benh_nhan=d["ma_benh_nhan"],
            ma_bac_si=d["ma_bac_si"],
            ngay_hen=date.fromisoformat(d["ngay_hen"]),
            gio_bat_dau=d["gio_bat_dau"],
            thoi_luong=d["thoi_luong"],
            trang_thai=d["trang_thai"],
            ly_do_kham=d.get("ly_do_kham", ""),
        )

    def __str__(self):
        return (f"Mã lịch: {self._ma_lich_hen}\n"
                f"Mã BN: {self._ma_benh_nhan}\n"
                f"Mã BS: {self._ma_bac_si}\n"
                f"Ngày hẹn: {self._ngay_hen.strftime('%d-%m-%Y')}\n"
                f"Giờ: {self._gio_bat_dau} - {self.gio_ket_thuc}\n"
                f"Trạng thái: {self._trang_thai}\n"
                f"Lý do: {self._ly_do_kham}\n")