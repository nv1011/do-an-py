import re
from datetime import date, datetime
from utils.validators import la_ma_bac_si_hop_le, la_ma_benh_nhan_hop_le, la_ngay_hop_le


class PhieuKham:

    def __init__(self, ma_phieu_kham, ma_benh_nhan, ma_bac_si, trieu_chung,
                 ma_lich_hen=None, ngay_kham=None, chan_doan="", danh_sach_dich_vu=None,
                 don_thuoc=None, loi_dan="", ngay_tai_kham=None,
                 trang_thai_kham="Dang_kham", trang_thai_thanh_toan="Chua_thanh_toan"):
        if not re.fullmatch(r"PK\d{3,}", str(ma_phieu_kham).strip()):
            raise ValueError("Mã phiếu khám phải có dạng PK001!")
        if not la_ma_benh_nhan_hop_le(ma_benh_nhan):
            raise ValueError("Mã bệnh nhân không hợp lệ!")
        if not la_ma_bac_si_hop_le(ma_bac_si):
            raise ValueError("Mã bác sĩ không hợp lệ!")

        self._ma_phieu_kham = str(ma_phieu_kham).strip()
        self._ma_benh_nhan = str(ma_benh_nhan).strip()
        self.ma_bac_si = ma_bac_si
        self.ma_lich_hen = ma_lich_hen
        self.ngay_kham = ngay_kham or date.today()
        self.trieu_chung = trieu_chung
        self.chan_doan = chan_doan
        self.danh_sach_dich_vu = danh_sach_dich_vu or []
        self.don_thuoc = don_thuoc or []
        self.loi_dan = loi_dan
        self.ngay_tai_kham = ngay_tai_kham
        self.trang_thai_kham = trang_thai_kham
        self.trang_thai_thanh_toan = trang_thai_thanh_toan

    @property
    def ma_phieu_kham(self):
        return self._ma_phieu_kham

    @property
    def ma_benh_nhan(self):
        return self._ma_benh_nhan

    @property
    def ma_bac_si(self):
        return self._ma_bac_si

    @ma_bac_si.setter
    def ma_bac_si(self, value):
        val = str(value or "").strip()
        if not la_ma_bac_si_hop_le(val):
            raise ValueError("Mã bác sĩ không hợp lệ!")
        self._ma_bac_si = val

    @property
    def ma_lich_hen(self):
        return self._ma_lich_hen

    @ma_lich_hen.setter
    def ma_lich_hen(self, value):
        val = str(value).strip() if value else None
        if val and not re.fullmatch(r"LH\d{3,}", val):
            raise ValueError("Mã lịch hẹn không hợp lệ!")
        self._ma_lich_hen = val

    @property
    def ngay_kham(self):
        return self._ngay_kham

    @ngay_kham.setter
    def ngay_kham(self, value):
        if isinstance(value, str):
            value = value.strip()
            parsed = False
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    value = datetime.strptime(value, fmt).date()
                    parsed = True
                    break
                except ValueError:
                    continue
            if not parsed:
                raise ValueError("Ngày khám không đúng định dạng!")
        elif isinstance(value, datetime):
            value = value.date()
        elif not isinstance(value, date):
            raise ValueError("Ngày khám không hợp lệ!")
        self._ngay_kham = value

    @property
    def trieu_chung(self):
        return self._trieu_chung

    @trieu_chung.setter
    def trieu_chung(self, value):
        val = str(value or "").strip()
        if not val:
            raise ValueError("Triệu chứng không được để trống!")
        self._trieu_chung = val

    @property
    def chan_doan(self):
        return self._chan_doan

    @chan_doan.setter
    def chan_doan(self, value):
        self._chan_doan = str(value or "").strip()

    @property
    def danh_sach_dich_vu(self):
        return self._danh_sach_dich_vu

    @danh_sach_dich_vu.setter
    def danh_sach_dich_vu(self, value):
        if not isinstance(value, list):
            raise ValueError("Danh sách dịch vụ phải là list!")
        self._danh_sach_dich_vu = [dict(x) for x in value]

    @property
    def don_thuoc(self):
        return self._don_thuoc

    @don_thuoc.setter
    def don_thuoc(self, value):
        if not isinstance(value, list):
            raise ValueError("Đơn thuốc phải là list!")
        self._don_thuoc = [dict(x) for x in value]

    @property
    def loi_dan(self):
        return self._loi_dan

    @loi_dan.setter
    def loi_dan(self, value):
        self._loi_dan = str(value or "").strip()

    @property
    def ngay_tai_kham(self):
        return self._ngay_tai_kham

    @ngay_tai_kham.setter
    def ngay_tai_kham(self, value):
        if not value:
            self._ngay_tai_kham = None
            return
        if isinstance(value, str):
            value = value.strip()
            parsed = False
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
                try:
                    value = datetime.strptime(value, fmt).date()
                    parsed = True
                    break
                except ValueError:
                    continue
            if not parsed:
                raise ValueError("Ngày tái khám không đúng định dạng!")
        elif isinstance(value, datetime):
            value = value.date()
        elif not isinstance(value, date):
            raise ValueError("Ngày tái khám không hợp lệ!")
        self._ngay_tai_kham = value

    @property
    def trang_thai_kham(self):
        return self._trang_thai_kham

    @trang_thai_kham.setter
    def trang_thai_kham(self, value):
        val = str(value or "").strip()
        if val not in ("Dang_kham", "Hoan_thanh"):
            raise ValueError("Trạng thái khám phải là 'Dang_kham' hoặc 'Hoan_thanh'!")
        self._trang_thai_kham = val

    @property
    def trang_thai_thanh_toan(self):
        return self._trang_thai_thanh_toan

    @trang_thai_thanh_toan.setter
    def trang_thai_thanh_toan(self, value):
        val = str(value or "").strip()
        if val not in ("Chua_thanh_toan", "Da_thanh_toan"):
            raise ValueError("Trạng thái thanh toán phải là 'Chua_thanh_toan' hoặc 'Da_thanh_toan'!")
        self._trang_thai_thanh_toan = val

    @property
    def tong_tien(self):
        """Tính tự động tổng tiền từ danh sách dịch vụ chỉ định."""
        return sum(float(dv.get("don_gia", 0)) * int(dv.get("so_luong", 1))
                   for dv in self._danh_sach_dich_vu)

    def to_dict(self):
        return {
            "ma_phieu_kham": self._ma_phieu_kham,
            "ma_lich_hen": self._ma_lich_hen,
            "ma_benh_nhan": self._ma_benh_nhan,
            "ma_bac_si": self._ma_bac_si,
            "ngay_kham": str(self._ngay_kham),
            "trieu_chung": self._trieu_chung,
            "chan_doan": self._chan_doan,
            "danh_sach_dich_vu": self._danh_sach_dich_vu,
            "don_thuoc": self._don_thuoc,
            "loi_dan": self._loi_dan,
            "ngay_tai_kham": str(self._ngay_tai_kham) if self._ngay_tai_kham else None,
            "trang_thai_kham": self._trang_thai_kham,
            "trang_thai_thanh_toan": self._trang_thai_thanh_toan,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            ma_phieu_kham=d["ma_phieu_kham"],
            ma_benh_nhan=d["ma_benh_nhan"],
            ma_bac_si=d["ma_bac_si"],
            trieu_chung=d.get("trieu_chung", ""),
            ma_lich_hen=d.get("ma_lich_hen"),
            ngay_kham=date.fromisoformat(d["ngay_kham"]) if d.get("ngay_kham") else None,
            chan_doan=d.get("chan_doan", ""),
            danh_sach_dich_vu=d.get("danh_sach_dich_vu", []),
            don_thuoc=d.get("don_thuoc", []),
            loi_dan=d.get("loi_dan", ""),
            ngay_tai_kham=date.fromisoformat(d["ngay_tai_kham"]) if d.get("ngay_tai_kham") else None,
            trang_thai_kham=d.get("trang_thai_kham", "Dang_kham"),
            trang_thai_thanh_toan=d.get("trang_thai_thanh_toan", "Chua_thanh_toan"),
        )

    def __str__(self):
        kham = "Đang khám" if self._trang_thai_kham == "Dang_kham" else "Hoàn thành"
        tt = "Đã thanh toán" if self._trang_thai_thanh_toan == "Da_thanh_toan" else "Chưa thanh toán"
        return (f"Phiếu khám: {self._ma_phieu_kham} | BN: {self._ma_benh_nhan} | BS: {self._ma_bac_si}\n"
                f"Ngày khám: {self._ngay_kham} | Khám: {kham} | Thanh toán: {tt} | Tổng tiền: {self.tong_tien:,.0f} đ\n"
                f"Triệu chứng: {self._trieu_chung} | Chẩn đoán: {self._chan_doan or 'Chưa có'}")
