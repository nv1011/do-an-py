from abc import ABC, abstractmethod
from datetime import date

class LichHen(ABC):
    def __init__(self, ma_lich_hen, ma_benh_nhan, ma_bac_si, ngay_hen, gio_bat_dau, thoi_luong, trang_thai,ly_do_kham):
        self._ma_lich_hen=ma_lich_hen
        self._ma_benh_nhan=ma_benh_nhan
        self._ma_bac_si=ma_bac_si
        self._ngay_hen=ngay_hen
        self._gio_bat_dau=gio_bat_dau
        self._thoi_luong=thoi_luong
        self._trang_thai=trang_thai
        self._ly_do_kham=ly_do_kham

    @property
    def ma_lich_hen(self):
        return self._ma_lich_hen