"""Bộ chọn ngày sinh: 3 ô chọn theo thứ tự Năm / Tháng / Ngày

- Năm: từ năm hiện tại xuống 1900.
- Tháng: 1-12 (năm hiện tại chỉ đến tháng hiện tại).
- Ngày: tự đổi theo tháng và năm (tháng 30 ngày, tháng 31 ngày, tháng 2 có năm nhuận).
  Nếu đổi tháng/năm làm ngày đang chọn không còn hợp lệ (ví dụ 31 -> tháng 4)
  thì ngày tự lùi về ngày cuối cùng của tháng đó.
"""
from tkinter import ttk
from datetime import date

from views import helpers

CHO_NAM, CHO_THANG, CHO_NGAY = "Năm", "Tháng", "Ngày"


class DatePicker(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        nam_hien_tai = date.today().year
        cac_nam = [str(n) for n in range(nam_hien_tai, helpers.NAM_NHO_NHAT - 1, -1)]

        self.cb_nam = ttk.Combobox(self, values=cac_nam, state="readonly", width=6)
        self.cb_thang = ttk.Combobox(self, state="readonly", width=4)
        self.cb_ngay = ttk.Combobox(self, state="readonly", width=4)

        # Năm rộng hơn một chút; cả 3 ô giãn theo độ rộng của form
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=2)
        self.cb_nam.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.cb_thang.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        self.cb_ngay.grid(row=0, column=2, sticky="ew")

        self.cb_nam.bind("<<ComboboxSelected>>", lambda _e: self._cap_nhat_danh_sach())
        self.cb_thang.bind("<<ComboboxSelected>>", lambda _e: self._cap_nhat_danh_sach())

        self.clear()

    # -------------------------------------------------------------- nội bộ
    @staticmethod
    def _doc(cb):
        """Giá trị số đang chọn của ô, hoặc None nếu còn là chữ gợi ý."""
        gia_tri = cb.get()
        return int(gia_tri) if gia_tri.isdigit() else None

    def _cap_nhat_danh_sach(self):
        """Tính lại danh sách tháng, ngày theo năm/tháng đang chọn."""
        nam, thang = self._doc(self.cb_nam), self._doc(self.cb_thang)

        thang_max = helpers.so_thang_toi_da(nam)
        self.cb_thang["values"] = [str(t) for t in range(1, thang_max + 1)]
        if thang is not None and thang > thang_max:
            thang = thang_max
            self.cb_thang.set(str(thang))

        ngay_max = helpers.so_ngay_toi_da(nam, thang)
        self.cb_ngay["values"] = [str(n) for n in range(1, ngay_max + 1)]
        ngay = self._doc(self.cb_ngay)
        if ngay is not None and ngay > ngay_max:
            self.cb_ngay.set(str(ngay_max))

    # ----------------------------------------------------------------- dùng bên ngoài
    def get(self):
        nam, thang, ngay = (self._doc(self.cb_nam), self._doc(self.cb_thang),
                            self._doc(self.cb_ngay))
        if None in (nam, thang, ngay):
            return ""
        return f"{ngay:02d}/{thang:02d}/{nam}"

    def set(self, chuoi):
        """Nhận 'dd/mm/yyyy'; chuỗi sai định dạng thì xóa trắng."""
        try:
            ngay, thang, nam = (int(p) for p in chuoi.split("/"))
        except ValueError:
            self.clear()
            return
        self.cb_nam.set(str(nam))
        self.cb_thang.set(str(thang))
        self._cap_nhat_danh_sach()   # cập nhật danh sách ngày trước khi đặt ngày
        self.cb_ngay.set(str(ngay))

    def clear(self):
        self.cb_nam.set(CHO_NAM)
        self.cb_thang.set(CHO_THANG)
        self.cb_ngay.set(CHO_NGAY)
        self._cap_nhat_danh_sach()
