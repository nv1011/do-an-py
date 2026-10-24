"""Bộ chọn ngày: 3 ô chọn theo thứ tự Năm / Tháng / Ngày

Dùng cho ngày sinh và cho ngày khám/ngày lọc ở tab Lịch hẹn.
- Tháng 4, 6, 9, 11 chỉ có 30 ngày; các tháng khác 31 ngày; tháng 2 có 28 ngày, năm nhuận 29 ngày.
- Nếu đổi tháng/năm làm ngày đang chọn không còn hợp lệ (ví dụ 31 -> tháng 4) thì ngày
  tự lùi về ngày cuối cùng của tháng đó.
- Mặc định (ngày sinh): năm từ năm hiện tại xuống 1900 và không được chọn ngày ở tương lai.
"""
from tkinter import ttk
from datetime import date, datetime

from views import helpers

CHO_NAM, CHO_THANG, CHO_NGAY = "Năm", "Tháng", "Ngày"


class DatePicker(ttk.Frame):
    def __init__(self, parent, nam_nho_nhat=helpers.NAM_NHO_NHAT, nam_lon_nhat=None,
                 nam_tang_dan=False, gioi_han_hom_nay=True, khi_doi=None):
        super().__init__(parent)
        self.gioi_han_hom_nay = gioi_han_hom_nay
        self.khi_doi = khi_doi

        nam_lon_nhat = nam_lon_nhat or date.today().year
        cac_nam = [str(n) for n in range(nam_nho_nhat, nam_lon_nhat + 1)]
        if not nam_tang_dan:
            cac_nam.reverse()

        self.cb_nam = ttk.Combobox(self, values=cac_nam, state="readonly", width=6)
        self.cb_thang = ttk.Combobox(self, state="readonly", width=4)
        self.cb_ngay = ttk.Combobox(self, state="readonly", width=4)

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=2)
        self.cb_nam.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.cb_thang.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        self.cb_ngay.grid(row=0, column=2, sticky="ew")

        self.cb_nam.bind("<<ComboboxSelected>>", lambda _e: self._khi_chon_nam_thang())
        self.cb_thang.bind("<<ComboboxSelected>>", lambda _e: self._khi_chon_nam_thang())
        self.cb_ngay.bind("<<ComboboxSelected>>", lambda _e: self._bao_doi())

        self.clear()

    @staticmethod
    def _doc(cb):
        gia_tri = cb.get()
        return int(gia_tri) if gia_tri.isdigit() else None

    def _cap_nhat_danh_sach(self):
        nam, thang = self._doc(self.cb_nam), self._doc(self.cb_thang)

        thang_max = helpers.so_thang_toi_da(nam, gioi_han_hom_nay=self.gioi_han_hom_nay)
        self.cb_thang["values"] = [str(t) for t in range(1, thang_max + 1)]
        if thang is not None and thang > thang_max:
            thang = thang_max
            self.cb_thang.set(str(thang))

        ngay_max = helpers.so_ngay_toi_da(nam, thang, gioi_han_hom_nay=self.gioi_han_hom_nay)
        self.cb_ngay["values"] = [str(n) for n in range(1, ngay_max + 1)]
        ngay = self._doc(self.cb_ngay)
        if ngay is not None and ngay > ngay_max:
            self.cb_ngay.set(str(ngay_max))

    def _khi_chon_nam_thang(self):
        self._cap_nhat_danh_sach()
        self._bao_doi()

    def _bao_doi(self):
        if self.khi_doi:
            self.khi_doi()

    def get(self):
        nam, thang, ngay = (self._doc(self.cb_nam), self._doc(self.cb_thang),
                            self._doc(self.cb_ngay))
        if None in (nam, thang, ngay):
            return ""
        return f"{ngay:02d}/{thang:02d}/{nam}"

    def get_date(self):
        chuoi = self.get()
        if not chuoi:
            return None
        try:
            return datetime.strptime(chuoi, "%d/%m/%Y").date()
        except ValueError:
            return None

    def set(self, chuoi):
        try:
            ngay, thang, nam = (int(p) for p in chuoi.split("/"))
        except ValueError:
            self.clear()
            return
        self.cb_nam.set(str(nam))
        self.cb_thang.set(str(thang))
        self._cap_nhat_danh_sach()   # cập nhật danh sách ngày trước khi đặt ngày
        self.cb_ngay.set(str(ngay))

    def set_date(self, ngay):
        self.set(ngay.strftime("%d/%m/%Y"))

    def clear(self):
        self.cb_nam.set(CHO_NAM)
        self.cb_thang.set(CHO_THANG)
        self.cb_ngay.set(CHO_NGAY)
        self._cap_nhat_danh_sach()
