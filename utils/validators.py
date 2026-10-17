from datetime import date, datetime
import re

def la_ma_benh_nhan_hop_le(ma):
    """Mã gồm đúng 14 chữ số và 8 số đầu là ngày có thật."""
    if not re.fullmatch(r"\d{14}", ma):
        return False
    try:
        ngay_tu_ma_benh_nhan(ma)
    except ValueError:        
        return False
    return True

def ngay_tu_ma_benh_nhan(ma):
    """Lấy ngày khám (date) từ 8 số đầu của mã bệnh nhân."""
    return datetime.strptime(ma[0:8], "%d%m%Y").date()

def la_email_hop_le(email):
    return bool(re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", email))

def la_ma_bac_si_hop_le(ma):
    return bool(re.fullmatch(r"\d{9}", ma))

def nam_tu_ma_bac_si(ma):
    """Suy ra năm vào làm đầy đủ (4 chữ số) từ 2 số năm trong mã bác sĩ."""
    yy = int(ma[4:6])
    nam = 2000 + yy
    if nam > date.today().year:   # năm ở tương lai thì thuộc thế kỷ trước
        nam -= 100
    return nam