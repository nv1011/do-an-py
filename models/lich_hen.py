from abc import ABC, abstractmethod
from datetime import date

class LichHen(ABC):
    def __init__(self, ma_lich_hen, ma_benh_nhan, ma_bac_si, ngay_hen, gio_bat_dau, thoi_luong, trang_thai,ly_do_kham):
        self._ma_lich_hen=ma_lich_hen
