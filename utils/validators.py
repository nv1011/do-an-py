from datetime import date
import re

def la_ma_bac_si_hop_le(ma):
    return bool(re.fullmatch(r"\d{9}", ma))

def nam_tu_ma_bac_si(ma):
    """Suy ra năm vào làm đầy đủ (4 chữ số) từ 2 số năm trong mã bác sĩ."""
    yy = int(ma[4:6])
    nam = 2000 + yy
    if nam > date.today().year:   # năm ở tương lai thì thuộc thế kỷ trước
        nam -= 100
    return nam