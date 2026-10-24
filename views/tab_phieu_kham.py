"""Tab Phiếu khám: Đang khám -> Hoàn thành -> Thanh toán (theo docs/hop_dong_ham.md)."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import config
from views import helpers
from views.du_lieu_gia import QuanLyPhieuKhamGia, QuanLyBacSiGia
from views.widgets.date_picker import DatePicker

TAT_CA = "Tất cả"
TRANG_THAI_KHAM = {"Dang_kham": "Đang khám", "Hoan_thanh": "Hoàn thành"}
TRANG_THAI_TT = {"Chua_thanh_toan": "Chưa thanh toán", "Da_thanh_toan": "Đã thanh toán"}
CAC_LOC = [TAT_CA, "Đang khám", "Chưa thanh toán", "Đã thanh toán"]

CAC_COT = [
    ("ma", "Mã phiếu", 80), ("ngay", "Ngày khám", 90), ("benh_nhan", "Bệnh nhân", 160),
    ("bac_si", "Bác sĩ", 150), ("kham", "Khám", 90), ("thanh_toan", "Thanh toán", 110),
    ("tien", "Tổng tiền", 90),
]


def _tien(so):
    return helpers.dinh_dang_tien(int(so))


class DialogTaoPhieu(tk.Toplevel):
    """Hộp thoại lập phiếu khám mới."""

    def __init__(self, parent, ds_benh_nhan, ds_bac_si, khi_luu):
        super().__init__(parent)
        self.title("Tạo phiếu khám")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.khi_luu = khi_luu
        self.ds_bn = {f"{b.ma_dinh_danh} - {b.ho_ten}": b.ma_dinh_danh for b in ds_benh_nhan}
        self.ds_bs = {f"{b.ma_dinh_danh} - {b.hoc_vi}. {b.ho_ten}": b.ma_dinh_danh for b in ds_bac_si}

        khung = ttk.Frame(self, padding=12)
        khung.pack(fill="both", expand=True)
        ttk.Label(khung, text="Bệnh nhân *").grid(row=0, column=0, sticky="w", pady=4)
        self.cb_bn = ttk.Combobox(khung, values=list(self.ds_bn), state="readonly", width=40)
        self.cb_bn.grid(row=0, column=1, pady=4)
        ttk.Label(khung, text="Bác sĩ *").grid(row=1, column=0, sticky="w", pady=4)
        self.cb_bs = ttk.Combobox(khung, values=list(self.ds_bs), state="readonly", width=40)
        self.cb_bs.grid(row=1, column=1, pady=4)
        ttk.Label(khung, text="Triệu chứng *").grid(row=2, column=0, sticky="nw", pady=4)
        self.txt = tk.Text(khung, width=40, height=4)
        self.txt.grid(row=2, column=1, pady=4)

        nut = ttk.Frame(khung)
        nut.grid(row=3, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(nut, text="Tạo phiếu", command=self._luu).pack(side="left", padx=4)
        ttk.Button(nut, text="Hủy", command=self.destroy).pack(side="left", padx=4)
        self.grab_set()

    def _luu(self):
        du_lieu = {
            "ma_benh_nhan": self.ds_bn.get(self.cb_bn.get()),
            "ma_bac_si": self.ds_bs.get(self.cb_bs.get()),
            "trieu_chung": self.txt.get("1.0", "end").strip(),
        }
        if self.khi_luu(du_lieu):
            self.destroy()


class TabPhieuKham(ttk.Frame):
    def __init__(self, parent, thong_bao=None, vai_tro="admin", quan_ly=None,
                 ql_benh_nhan=None, ql_bac_si=None):
        super().__init__(parent)
        self.thong_bao = thong_bao or (lambda _m: None)
        self.vai_tro = vai_tro
        self.ql = quan_ly or QuanLyPhieuKhamGia()      # NỐI A: QuanLyPhieuKham
        self.ql_bn = ql_benh_nhan
        self.ql_bs = ql_bac_si or QuanLyBacSiGia()     # NỐI A: QuanLyBacSi
        self.ma_dang_chon = None
        self.don_thuoc = []
        self.dich_vu = {f"{d['ma_dich_vu']} - {d['ten_dich_vu']} - {_tien(d['don_gia'])}": d["ma_dich_vu"]
                        for d in self.ql.lay_dich_vu()}

        self._tao_loc()
        self._tao_bang()
        self._tao_chi_tiet()
        self.lam_moi()

    # ------------------------------------------------------------ giao diện
    def _tao_loc(self):
        khung = ttk.Frame(self)
        khung.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(khung, text="Tìm:").pack(side="left")
        self.var_tim = tk.StringVar()
        self.var_tim.trace_add("write", lambda *_: self._nap_bang())
        ttk.Entry(khung, textvariable=self.var_tim, width=28).pack(side="left", padx=(4, 12))
        ttk.Label(khung, text="Trạng thái:").pack(side="left")
        self.cb_loc = ttk.Combobox(khung, values=CAC_LOC, state="readonly", width=16)
        self.cb_loc.set(TAT_CA)
        self.cb_loc.pack(side="left", padx=4)
        self.cb_loc.bind("<<ComboboxSelected>>", lambda _e: self._nap_bang())
        ttk.Button(khung, text="Tạo phiếu khám", command=self._mo_tao_phieu).pack(side="right")

    def _tao_bang(self):
        khung = ttk.Frame(self)
        khung.pack(fill="both", expand=True, padx=8)
        self.bang = ttk.Treeview(khung, columns=[c[0] for c in CAC_COT], show="headings",
                                 height=8, selectmode="browse")
        for khoa, tieu_de, rong in CAC_COT:
            self.bang.heading(khoa, text=tieu_de)
            self.bang.column(khoa, width=rong, anchor="e" if khoa == "tien" else "w")
        thanh = ttk.Scrollbar(khung, orient="vertical", command=self.bang.yview)
        self.bang.configure(yscrollcommand=thanh.set)
        self.bang.pack(side="left", fill="both", expand=True)
        thanh.pack(side="right", fill="y")
        self.bang.bind("<<TreeviewSelect>>", self._khi_chon)

    def _tao_chi_tiet(self):
        goc = ttk.Frame(self)
        goc.pack(fill="x", padx=8, pady=(4, 8))
        for c in (0, 1):
            goc.columnconfigure(c, weight=1, uniform="ct")
        goc.rowconfigure(0, weight=1)
        trai = ttk.LabelFrame(goc, text=" Thông tin và dịch vụ ", padding=6)
        phai = ttk.LabelFrame(goc, text=" Kết quả khám và đơn thuốc ", padding=6)
        trai.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        phai.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        # --- trái: thông tin, dịch vụ, tiền
        self.var_ten = tk.StringVar(value="Chọn một phiếu ở bảng trên")
        self.var_ma_bn = tk.StringVar()
        self.var_bs = tk.StringVar()
        self.var_ngay = tk.StringVar()
        self.var_trieu_chung = tk.StringVar()
        ttk.Label(trai, textvariable=self.var_ten, font=config.FONT_TIEU_DE).pack(anchor="w")
        tt = ttk.Frame(trai)
        tt.pack(fill="x", pady=(0, 4))
        tt.columnconfigure(1, weight=1)
        for i, (nhan, bien) in enumerate((("Mã bệnh nhân:", self.var_ma_bn), ("Bác sĩ:", self.var_bs),
                                          ("Ngày khám:", self.var_ngay), ("Triệu chứng:", self.var_trieu_chung))):
            ttk.Label(tt, text=nhan, foreground=config.MAU_CHU_PHU).grid(row=i, column=0, sticky="w", padx=(0, 8))
            ttk.Label(tt, textvariable=bien, wraplength=330).grid(row=i, column=1, sticky="w")

        self.bang_dv = ttk.Treeview(trai, columns=("ten", "gia", "sl", "tt"), show="headings",
                                    height=2, selectmode="browse")
        for khoa, td, rong, neo in (("ten", "Dịch vụ", 190, "w"), ("gia", "Đơn giá", 80, "e"),
                                    ("sl", "SL", 35, "center"), ("tt", "Thành tiền", 90, "e")):
            self.bang_dv.heading(khoa, text=td)
            self.bang_dv.column(khoa, width=rong, anchor=neo, stretch=(khoa == "ten"))
        self.bang_dv.pack(fill="x")

        them = ttk.Frame(trai)
        them.pack(fill="x", pady=4)
        self.cb_dv = ttk.Combobox(them, values=list(self.dich_vu), state="readonly")
        self.cb_dv.pack(side="left", fill="x", expand=True)
        self.sp_sl = ttk.Spinbox(them, from_=1, to=99, width=4)
        self.sp_sl.set(1)
        self.sp_sl.pack(side="left", padx=6)
        self.nut_them_dv = ttk.Button(them, text="Thêm", width=7, command=self._them_dv)
        self.nut_them_dv.pack(side="left")
        self.nut_xoa_dv = ttk.Button(them, text="Bỏ dòng", width=8, command=self._xoa_dv)
        self.nut_xoa_dv.pack(side="left", padx=(6, 0))

        cuoi = ttk.Frame(trai)
        cuoi.pack(fill="x")
        self.var_tong = tk.StringVar(value="Tổng tiền: 0 đ")
        ttk.Label(cuoi, textvariable=self.var_tong, font=config.FONT_TONG_TIEN).pack(side="left")
        self.nut_thanh_toan = ttk.Button(cuoi, text="Thanh toán", command=self._thanh_toan)
        self.nut_thanh_toan.pack(side="right")

        # --- phải: chẩn đoán, lời dặn, đơn thuốc, tái khám
        phai.columnconfigure(0, weight=1)
        ttk.Label(phai, text="Chẩn đoán *").grid(row=0, column=0, sticky="w")
        self.ent_chan_doan = ttk.Entry(phai)
        self.ent_chan_doan.grid(row=1, column=0, sticky="ew", pady=(0, 3))
        ttk.Label(phai, text="Lời dặn").grid(row=2, column=0, sticky="w")
        self.ent_loi_dan = ttk.Entry(phai)
        self.ent_loi_dan.grid(row=3, column=0, sticky="ew", pady=(0, 3))

        ttk.Label(phai, text="Đơn thuốc").grid(row=4, column=0, sticky="w")
        self.bang_thuoc = ttk.Treeview(phai, columns=("ten", "dv", "sl", "cd"), show="headings",
                                       height=2, selectmode="browse")
        for khoa, td, rong, neo in (("ten", "Tên thuốc", 130, "w"), ("dv", "Đơn vị", 60, "w"),
                                    ("sl", "SL", 40, "center"), ("cd", "Cách dùng", 150, "w")):
            self.bang_thuoc.heading(khoa, text=td)
            self.bang_thuoc.column(khoa, width=rong, anchor=neo, stretch=(khoa in ("ten", "cd")))
        self.bang_thuoc.grid(row=5, column=0, sticky="nsew")

        nhap = ttk.Frame(phai)
        nhap.grid(row=6, column=0, sticky="ew", pady=4)
        nhap.columnconfigure(0, weight=3)
        nhap.columnconfigure(3, weight=3)
        self.ent_thuoc, self.ent_dv, self.ent_sl, self.ent_cd = (ttk.Entry(nhap) for _ in range(4))
        self.ent_dv.configure(width=7)
        self.ent_sl.configure(width=5)
        for cot, (nhan, o) in enumerate((("Tên thuốc", self.ent_thuoc), ("Đơn vị", self.ent_dv),
                                         ("SL", self.ent_sl), ("Cách dùng", self.ent_cd))):
            ttk.Label(nhap, text=nhan, foreground=config.MAU_CHU_PHU).grid(row=0, column=cot, sticky="w", padx=(0, 4))
            o.grid(row=1, column=cot, sticky="ew", padx=(0, 4))
        self.nut_them_thuoc = ttk.Button(nhap, text="Thêm", width=7, command=self._them_thuoc)
        self.nut_them_thuoc.grid(row=1, column=4, padx=(0, 4))
        self.nut_xoa_thuoc = ttk.Button(nhap, text="Bỏ dòng", width=8, command=self._xoa_thuoc)
        self.nut_xoa_thuoc.grid(row=1, column=5)

        cuoi_p = ttk.Frame(phai)
        cuoi_p.grid(row=7, column=0, sticky="ew")
        ttk.Label(cuoi_p, text="Ngày tái khám:").pack(side="left")
        self.dp_tai_kham = DatePicker(cuoi_p, nam_nho_nhat=date.today().year,
                                      nam_lon_nhat=date.today().year + 2, nam_tang_dan=True,
                                      gioi_han_hom_nay=False)
        self.dp_tai_kham.pack(side="left", padx=6)
        self.nut_hoan_tat = ttk.Button(cuoi_p, text="Hoàn tất khám", command=self._hoan_tat)
        self.nut_hoan_tat.pack(side="right")

        self._dat_trang_thai()

    # ------------------------------------------------------------ dữ liệu bảng
    def lam_moi(self):
        """Nạp lại bảng, giữ phiếu đang chọn."""
        self._nap_bang()
        if self.ma_dang_chon and self.bang.exists(self.ma_dang_chon):
            self.bang.selection_set(self.ma_dang_chon)
        else:
            self.ma_dang_chon = None
            self._hien_chi_tiet(None)

    def _ten_bn(self, ma):
        if self.ql_bn:
            bn = self.ql_bn.tim_theo_ma(ma)
            if bn:
                return bn.ho_ten
        return ma

    def _ten_bs(self, ma):
        bs = self.ql_bs.tim_theo_ma(ma)
        return f"{bs.hoc_vi}. {bs.ho_ten}" if bs else ma

    def _nap_bang(self):
        tu_khoa, loc = self.var_tim.get().strip(), self.cb_loc.get()
        self.bang.delete(*self.bang.get_children())
        for pk in sorted(self.ql.lay_tat_ca(), key=lambda p: (p.ngay_kham, p.ma_phieu_kham), reverse=True):
            ten_bn, ten_bs = self._ten_bn(pk.ma_benh_nhan), self._ten_bs(pk.ma_bac_si)
            if loc == "Đang khám" and pk.trang_thai_kham != "Dang_kham":
                continue
            if loc == "Chưa thanh toán" and not (pk.trang_thai_kham == "Hoan_thanh"
                                                  and pk.trang_thai_thanh_toan == "Chua_thanh_toan"):
                continue
            if loc == "Đã thanh toán" and pk.trang_thai_thanh_toan != "Da_thanh_toan":
                continue
            if tu_khoa and not (helpers.khop_chuoi(pk.ma_phieu_kham, tu_khoa)
                                or helpers.khop_chuoi(pk.ma_benh_nhan, tu_khoa)
                                or helpers.khop_ten(ten_bn, tu_khoa)):
                continue
            self.bang.insert("", "end", iid=pk.ma_phieu_kham, values=(
                pk.ma_phieu_kham, pk.ngay_kham.strftime("%d/%m/%Y"), ten_bn, ten_bs,
                TRANG_THAI_KHAM[pk.trang_thai_kham],
                TRANG_THAI_TT[pk.trang_thai_thanh_toan] if pk.trang_thai_kham == "Hoan_thanh" else "-",
                _tien(pk.tong_tien)))

    def _khi_chon(self, _e=None):
        chon = self.bang.selection()
        self.ma_dang_chon = chon[0] if chon else None
        self._hien_chi_tiet(self.ql.tim_theo_ma(self.ma_dang_chon) if self.ma_dang_chon else None)

    # ------------------------------------------------------------ chi tiết
    def _hien_chi_tiet(self, pk):
        self.bang_dv.delete(*self.bang_dv.get_children())
        self.bang_thuoc.delete(*self.bang_thuoc.get_children())
        self._dat_noi_dung(self.ent_chan_doan, "")
        self._dat_noi_dung(self.ent_loi_dan, "")
        self.dp_tai_kham.clear()
        self.don_thuoc = []
        if pk is None:
            self.var_ten.set("Chọn một phiếu ở bảng trên")
            for bien in (self.var_ma_bn, self.var_bs, self.var_ngay, self.var_trieu_chung):
                bien.set("")
            self.var_tong.set("Tổng tiền: 0 đ")
            self._dat_trang_thai()
            return
        self.var_ten.set(f"{pk.ma_phieu_kham} - {self._ten_bn(pk.ma_benh_nhan)}")
        self.var_ma_bn.set(pk.ma_benh_nhan)
        self.var_bs.set(self._ten_bs(pk.ma_bac_si))
        self.var_ngay.set(pk.ngay_kham.strftime("%d/%m/%Y"))
        self.var_trieu_chung.set(pk.trieu_chung)
        for x in pk.danh_sach_dich_vu:
            self.bang_dv.insert("", "end", iid=x["ma_dich_vu"], values=(
                x["ten_dich_vu"], _tien(x["don_gia"]), x["so_luong"], _tien(x["don_gia"] * x["so_luong"])))
        self.var_tong.set(f"Tổng tiền: {_tien(pk.tong_tien)}")
        self._dat_noi_dung(self.ent_chan_doan, pk.chan_doan)
        self._dat_noi_dung(self.ent_loi_dan, pk.loi_dan)
        self.don_thuoc = [dict(t) for t in pk.don_thuoc]
        self._ve_thuoc()
        if pk.ngay_tai_kham:
            self.dp_tai_kham.set_date(pk.ngay_tai_kham)
        self._dat_trang_thai(pk)

    @staticmethod
    def _dat_noi_dung(o, noi_dung):
        o.configure(state="normal")
        o.delete(0, "end")
        o.insert(0, noi_dung or "")

    def _ve_thuoc(self):
        self.bang_thuoc.delete(*self.bang_thuoc.get_children())
        for i, t in enumerate(self.don_thuoc):
            self.bang_thuoc.insert("", "end", iid=str(i),
                                   values=(t["ten_thuoc"], t["don_vi"], t["so_luong"], t["cach_dung"]))

    def _dat_trang_thai(self, pk=None):
        """Bật/tắt ô theo trạng thái phiếu và vai trò."""
        dang_kham = bool(pk) and pk.trang_thai_kham == "Dang_kham"
        la_admin = self.vai_tro == "admin"
        sua_ho_so = dang_kham and la_admin

        def bat(cac_o, on):
            for o in cac_o:
                o.configure(state="normal" if on else "disabled")

        bat((self.nut_them_dv, self.nut_xoa_dv), dang_kham)
        self.cb_dv.configure(state="readonly" if dang_kham else "disabled")
        self.sp_sl.configure(state="normal" if dang_kham else "disabled")
        bat((self.ent_chan_doan, self.ent_loi_dan, self.ent_thuoc, self.ent_dv, self.ent_sl,
             self.ent_cd, self.nut_them_thuoc, self.nut_xoa_thuoc, self.nut_hoan_tat), sua_ho_so)
        self.dp_tai_kham.bat(sua_ho_so)
        cho_tt = bool(pk) and pk.trang_thai_kham == "Hoan_thanh" and pk.trang_thai_thanh_toan == "Chua_thanh_toan"
        bat((self.nut_thanh_toan,), cho_tt)

    # ------------------------------------------------------------ thao tác
    def _bao(self, ok, thong_diep):
        self.thong_bao(thong_diep)
        if not ok:
            messagebox.showwarning(config.TIEU_DE_APP, thong_diep, parent=self)
        return ok

    def _mo_tao_phieu(self):
        ds_bn = self.ql_bn.lay_tat_ca() if self.ql_bn else []
        DialogTaoPhieu(self, ds_bn, self.ql_bs.lay_tat_ca(), self._tao_phieu)

    def _tao_phieu(self, du_lieu):
        ok, tb, pk = self.ql.tao_phieu_kham(du_lieu)
        if not self._bao(ok, tb):
            return False
        self.ma_dang_chon = pk.ma_phieu_kham
        self.var_tim.set("")
        self.cb_loc.set(TAT_CA)
        self.lam_moi()
        return True

    def _them_dv(self):
        ma_dv = self.dich_vu.get(self.cb_dv.get())
        if not ma_dv:
            self._bao(False, "Chưa chọn dịch vụ!")
            return
        try:
            so_luong = int(self.sp_sl.get())
        except ValueError:
            so_luong = 0
        if self._bao(*self.ql.them_dich_vu(self.ma_dang_chon, ma_dv, so_luong)):
            self.lam_moi()

    def _xoa_dv(self):
        chon = self.bang_dv.selection()
        if not chon:
            self._bao(False, "Chọn dịch vụ cần bỏ trong bảng dịch vụ!")
            return
        if self._bao(*self.ql.xoa_dich_vu(self.ma_dang_chon, chon[0])):
            self.lam_moi()

    def _them_thuoc(self):
        ten = self.ent_thuoc.get().strip()
        try:
            so_luong = int(self.ent_sl.get())
        except ValueError:
            so_luong = 0
        if not ten:
            self._bao(False, "Tên thuốc không được để trống!")
            return
        if so_luong <= 0:
            self._bao(False, "Số lượng thuốc phải là số nguyên dương!")
            return
        self.don_thuoc.append({"ten_thuoc": ten, "don_vi": self.ent_dv.get().strip(),
                               "so_luong": so_luong, "cach_dung": self.ent_cd.get().strip()})
        for o in (self.ent_thuoc, self.ent_dv, self.ent_sl, self.ent_cd):
            o.delete(0, "end")
        self._ve_thuoc()

    def _xoa_thuoc(self):
        chon = self.bang_thuoc.selection()
        if chon:
            del self.don_thuoc[int(chon[0])]
            self._ve_thuoc()

    def _hoan_tat(self):
        if self.vai_tro != "admin":
            self._bao(False, "Lễ tân không có quyền hoàn tất khám!")
            return
        if self._bao(*self.ql.hoan_tat_kham(
                self.ma_dang_chon, self.ent_chan_doan.get(), self.ent_loi_dan.get(),
                self.don_thuoc, self.dp_tai_kham.get().replace("/", "-") or None)):
            self.lam_moi()

    def _thanh_toan(self):
        pk = self.ql.tim_theo_ma(self.ma_dang_chon)
        if not pk or not messagebox.askyesno(
                config.TIEU_DE_APP, f"Thu {_tien(pk.tong_tien)} cho phiếu {pk.ma_phieu_kham}?", parent=self):
            return
        ok, tb, _so_tien = self.ql.thanh_toan(self.ma_dang_chon)
        if self._bao(ok, tb):
            self.lam_moi()
