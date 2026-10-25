"""Bộ chọn ngày gồm 3 ô: Năm, Tháng, Ngày."""
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

    # ------------------------------------------------------------ nội bộ
    @staticmethod
    def _doc(cb):
        """Giá trị số đang chọn của ô, hoặc None nếu còn là chữ gợi ý."""
        gia_tri = cb.get()
        return int(gia_tri) if gia_tri.isdigit() else None

    def _cap_nhat_danh_sach(self):
        """Tính lại danh sách tháng, ngày theo năm/tháng đang chọn."""
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

    # ------------------------------------------------------------ dùng bên ngoài
    def get(self):
        nam, thang, ngay = (self._doc(self.cb_nam), self._doc(self.cb_thang),
                            self._doc(self.cb_ngay))
        if None in (nam, thang, ngay):
            return ""
        return f"{ngay:02d}/{thang:02d}/{nam}"

    def get_phan(self):
        """(năm, tháng, ngày); phần chưa chọn là None."""
        return (self._doc(self.cb_nam), self._doc(self.cb_thang),
                self._doc(self.cb_ngay))

    def get_date(self):
        """datetime.date, hoặc None nếu chưa chọn đủ / ngày không tồn tại."""
        chuoi = self.get()
        if not chuoi:
            return None
        try:
            return datetime.strptime(chuoi, "%d/%m/%Y").date()
        except ValueError:
            return None

    def set(self, chuoi):
        """Nhận 'dd/mm/yyyy'; chuỗi sai định dạng thì xóa trắng."""
        try:
            ngay, thang, nam = (int(p) for p in chuoi.split("/"))
        except ValueError:
            self.clear()
            return
        self.cb_nam.set(str(nam))
        self.cb_thang.set(str(thang))
        self._cap_nhat_danh_sach()
        self.cb_ngay.set(str(ngay))

    def set_date(self, ngay):
        self.set(ngay.strftime("%d/%m/%Y"))

    def clear(self):
        self.cb_nam.set(CHO_NAM)
        self.cb_thang.set(CHO_THANG)
        self.cb_ngay.set(CHO_NGAY)
        self._cap_nhat_danh_sach()

    def bat(self, bat_len=True):
        """Bật/tắt cả 3 ô."""
        trang_thai = "readonly" if bat_len else "disabled"
        for cb in (self.cb_nam, self.cb_thang, self.cb_ngay):
            cb.configure(state=trang_thai)
