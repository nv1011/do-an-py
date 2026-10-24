"""Tab Thống kê (chỉ admin): lượt khám và doanh thu bằng biểu đồ Canvas."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date

import config
from views import helpers
from views.du_lieu_gia import QuanLyPhieuKhamGia, ThongKeGia
from views.widgets.bieu_do import BieuDoCot, BieuDoDuong, BieuDoTron
from views.widgets.date_picker import DatePicker

SO_NAM_XEM = 4


class TabThongKe(ttk.Frame):
    def __init__(self, parent, thong_bao=None, thong_ke=None):
        super().__init__(parent)
        self.thong_bao = thong_bao or (lambda _m: None)
        if thong_ke is None:                                   # NỐI A: ThongKe(...)
            thong_ke = ThongKeGia(QuanLyPhieuKhamGia())
        self.thong_ke = thong_ke

        self._tao_thanh_loc()
        self._tao_the_tong()
        self._tao_bieu_do()
        self.cap_nhat()

    def _tao_thanh_loc(self):
        khung = ttk.Frame(self)
        khung.pack(fill="x", padx=8, pady=8)
        hom_nay = date.today()
        ttk.Label(khung, text="Năm:").pack(side="left")
        self.cb_nam = ttk.Combobox(khung, state="readonly", width=6,
                                   values=[str(n) for n in range(hom_nay.year, hom_nay.year - SO_NAM_XEM, -1)])
        self.cb_nam.set(str(hom_nay.year))
        self.cb_nam.pack(side="left", padx=(4, 16))

        ttk.Label(khung, text="Từ ngày:").pack(side="left")
        self.dp_tu = DatePicker(khung, nam_nho_nhat=hom_nay.year - SO_NAM_XEM + 1)
        self.dp_tu.pack(side="left", padx=(4, 8))
        self.dp_tu.set_date(date(hom_nay.year, 1, 1))
        ttk.Label(khung, text="Đến ngày:").pack(side="left")
        self.dp_den = DatePicker(khung, nam_nho_nhat=hom_nay.year - SO_NAM_XEM + 1)
        self.dp_den.pack(side="left", padx=(4, 12))
        self.dp_den.set_date(hom_nay)

        ttk.Button(khung, text="Xem", command=self.cap_nhat).pack(side="left")
        ttk.Button(khung, text="Xuất báo cáo (CSV)", command=self.xuat_bao_cao).pack(side="right")

    def _tao_the_tong(self):
        khung = ttk.Frame(self)
        khung.pack(fill="x", padx=8)
        self.var_luot, self.var_thu = tk.StringVar(), tk.StringVar()
        self.o_luot, self.o_thu = (ttk.LabelFrame(khung, padding=(12, 4)) for _ in range(2))
        for o, bien in ((self.o_luot, self.var_luot), (self.o_thu, self.var_thu)):
            o.pack(side="left", padx=(0, 8))
            ttk.Label(o, textvariable=bien, font=config.FONT_TIEU_DE).pack()

    def _tao_bieu_do(self):
        khung = ttk.Frame(self)
        khung.pack(fill="both", expand=True, padx=8, pady=8)
        for c in (0, 1):
            khung.columnconfigure(c, weight=1, uniform="bd")
            khung.rowconfigure(c, weight=1)
        self.bd_luot = BieuDoCot(khung, "Lượt khám theo tháng")
        self.bd_thu = BieuDoDuong(khung, "Doanh thu theo tháng (đồng)", dinh_dang=lambda v: helpers.dinh_dang_tien(int(v)))
        self.bd_bs = BieuDoCot(khung, "Lượt khám theo bác sĩ (trong khoảng ngày)")
        self.bd_khoa = BieuDoTron(khung, "Cơ cấu chuyên khoa (trong khoảng ngày)")
        self.bd_luot.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=(0, 4))
        self.bd_thu.grid(row=0, column=1, sticky="nsew", padx=(4, 0), pady=(0, 4))
        self.bd_bs.grid(row=1, column=0, sticky="nsew", padx=(0, 4), pady=(4, 0))
        self.bd_khoa.grid(row=1, column=1, sticky="nsew", padx=(4, 0), pady=(4, 0))

    # ------------------------------------------------------------ dữ liệu
    def _khoang_ngay(self):
        tu, den = self.dp_tu.get_date(), self.dp_den.get_date()
        if not tu or not den:
            return None, None, "Chọn đủ ngày bắt đầu và kết thúc!"
        if tu > den:
            return None, None, "Từ ngày phải trước hoặc bằng đến ngày!"
        return tu, den, ""

    @staticmethod
    def _ten_ngan(ten):
        """'TS. Nguyễn Văn An' -> 'TS. An'."""
        phan = ten.split()
        return f"{phan[0]} {phan[-1]}" if len(phan) > 2 else ten

    def cap_nhat(self):
        nam = int(self.cb_nam.get())
        theo_thang = self.thong_ke.thong_ke_theo_thang(nam)
        luot = [(t, v["luot_kham"]) for t, v in theo_thang.items()]
        thu = [(t, v["doanh_thu"]) for t, v in theo_thang.items()]
        self.bd_luot.dat_du_lieu(luot)
        self.bd_thu.dat_du_lieu(thu)
        self.o_luot.configure(text=f"Lượt khám năm {nam}")
        self.o_thu.configure(text=f"Doanh thu năm {nam}")
        self.var_luot.set(f"{sum(v for _t, v in luot)} lượt")
        self.var_thu.set(helpers.dinh_dang_tien(int(sum(v for _t, v in thu))))

        tu, den, loi = self._khoang_ngay()
        if loi:
            self.thong_bao(loi)
            messagebox.showwarning(config.TIEU_DE_APP, loi, parent=self)
            return
        theo_bs = self.thong_ke.thong_ke_luot_kham_theo_bac_si(tu, den)
        self.bd_bs.dat_du_lieu([(self._ten_ngan(ten), v) for ten, v in theo_bs.items()])
        self.bd_khoa.dat_du_lieu(list(self.thong_ke.thong_ke_co_cau_chuyen_khoa(tu, den).items()))
        self.thong_bao(f"Đã cập nhật thống kê năm {nam}")

    def xuat_bao_cao(self):
        tu, den, loi = self._khoang_ngay()
        if loi:
            messagebox.showwarning(config.TIEU_DE_APP, loi, parent=self)
            return
        duong_dan = filedialog.asksaveasfilename(
            parent=self, defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile=f"bao_cao_{tu:%d%m%Y}_{den:%d%m%Y}.csv")
        if not duong_dan:
            return
        ok, tb = self.thong_ke.xuat_bao_cao_csv(duong_dan, tu, den)
        self.thong_bao(tb)
        (messagebox.showinfo if ok else messagebox.showwarning)(config.TIEU_DE_APP, tb, parent=self)
