"""Tab Lịch hẹn: bộ lọc, bảng, thẻ lịch hẹn và form đặt lịch."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import config
from services.quan_ly_bac_si import QuanLyBacSi
from services.quan_ly_benh_nhan import QuanLyBenhNhan
from services.quan_ly_lich_hen import QuanLyLichHen
from views import helpers
from views.widgets.date_picker import DatePicker
from views.widgets.appointment_card import AppointmentCard, CHIEU_CAO_THE

CAC_COT = [
    ("ma", "Mã", 70),
    ("benh_nhan", "Bệnh nhân", 170),
    ("bac_si", "Bác sĩ", 170),
    ("ngay", "Ngày", 90),
    ("gio", "Giờ bắt đầu", 90),
    ("thoi_luong", "Thời lượng", 80),
]

TAT_CA_BAC_SI = "Tất cả bác sĩ"
CAC_THOI_LUONG = ["15", "30", "45", "60", "90", "120"]
CHO_BENH_NHAN, CHO_BAC_SI, CHO_GIO, CHO_THOI_LUONG = (
    "Chọn bệnh nhân", "Chọn bác sĩ", "Chọn giờ", "Chọn thời lượng")

VAI_TRO_DUOC_HUY = ("admin", "le_tan")


class TabLichHen(ttk.Frame):
    def __init__(self, parent, thong_bao=None, vai_tro="admin",
                 ql_benh_nhan=None, ql_bac_si=None, ql_lich_hen=None):
        super().__init__(parent)
        self.thong_bao = thong_bao or (lambda _s: None)
        self.vai_tro = vai_tro

        self.ql_bn = ql_benh_nhan or QuanLyBenhNhan()
        self.ql_bs = ql_bac_si or QuanLyBacSi()
        self.ql = ql_lich_hen or QuanLyLichHen(quan_ly_bac_si=self.ql_bs)
        self.ds_benh_nhan = [{"ma": b.ma_dinh_danh, "ho_ten": b.ho_ten}
                             for b in self.ql_bn.lay_tat_ca()]
        self.ds_bac_si = [{"ma": b.ma_dinh_danh, "ten": f"{b.hoc_vi}. {b.ho_ten}"}
                          for b in self.ql_bs.lay_tat_ca()]
        self.ten_benh_nhan = {b["ma"]: b["ho_ten"] for b in self.ds_benh_nhan}
        self.ten_bac_si = {b["ma"]: b["ten"] for b in self.ds_bac_si}
        self._nap_du_lieu()

        self.dang_hien = []
        self.cac_the = {}
        self.ma_the_dang_chon = None

        self._tao_thanh_loc()
        khung_chinh = ttk.Frame(self)
        khung_chinh.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        khung_chinh.columnconfigure(0, weight=1)
        khung_chinh.columnconfigure(1, weight=0)
        khung_chinh.rowconfigure(0, weight=1)

        khung_trai = ttk.Frame(khung_chinh)
        khung_trai.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._tao_bang(khung_trai)
        self._tao_khung_the(khung_trai)
        self._tao_form(khung_chinh).grid(row=0, column=1, sticky="ns")

        self.hien_thi()
        self.ap_dung_phan_quyen()

    # ------------------------------------------------------------ giao diện
    def _tao_thanh_loc(self):
        nam = date.today().year
        thanh = ttk.Frame(self)
        thanh.pack(fill="x", padx=10, pady=10)

        ttk.Label(thanh, text="Ngày:").grid(row=0, column=0, padx=(0, 6))
        self.loc_ngay = DatePicker(thanh, nam_nho_nhat=nam - 1, nam_lon_nhat=nam + 2,
                                   nam_tang_dan=True, gioi_han_hom_nay=False)
        self.loc_ngay.grid(row=0, column=1, padx=(0, 16))
        self.loc_ngay.set_date(date.today())

        ttk.Label(thanh, text="Bác sĩ:").grid(row=0, column=2, padx=(0, 6))
        self.cb_loc_bac_si = ttk.Combobox(
            thanh, values=[TAT_CA_BAC_SI] + [b["ten"] for b in self.ds_bac_si],
            state="readonly", width=24)
        self.cb_loc_bac_si.current(0)
        self.cb_loc_bac_si.grid(row=0, column=3, padx=(0, 16))

        ttk.Button(thanh, text="Lọc", command=self.loc).grid(row=0, column=4, padx=(0, 8))
        ttk.Button(thanh, text="Làm mới", command=self.lam_moi_bo_loc).grid(row=0, column=5)

    def _tao_bang(self, cha):
        khung = ttk.Frame(cha)
        khung.pack(fill="both", expand=True)
        khung.rowconfigure(0, weight=1)
        khung.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(khung, columns=[c[0] for c in CAC_COT],
                                 show="headings", selectmode="browse")
        for khoa, tieu_de, rong in CAC_COT:
            self.tree.heading(khoa, text=tieu_de)
            self.tree.column(khoa, width=rong, minwidth=60, anchor="w")
        thanh_cuon = ttk.Scrollbar(khung, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=thanh_cuon.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        thanh_cuon.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._khi_chon_dong)

    def _tao_khung_the(self, cha):
        """Hàng thẻ lịch hẹn, cuộn ngang khi có nhiều thẻ."""
        ttk.Label(cha, text="Lịch hẹn dạng thẻ", font=config.FONT_DAM).pack(
            anchor="w", pady=(10, 4))
        khung = ttk.Frame(cha)
        khung.pack(fill="x")

        self.canvas_the = tk.Canvas(khung, height=CHIEU_CAO_THE + 6, highlightthickness=0,
                                    bg=config.MAU_NEN)
        thanh_cuon = ttk.Scrollbar(khung, orient="horizontal", command=self.canvas_the.xview)
        self.canvas_the.configure(xscrollcommand=thanh_cuon.set)
        self.canvas_the.pack(fill="x")
        thanh_cuon.pack(fill="x")

        self.khung_the = tk.Frame(self.canvas_the, bg=config.MAU_NEN)
        self.canvas_the.create_window((0, 0), window=self.khung_the, anchor="nw")
        self.khung_the.bind(
            "<Configure>",
            lambda _e: self.canvas_the.configure(scrollregion=self.canvas_the.bbox("all")))

    def _tao_form(self, cha):
        nam = date.today().year
        form = ttk.LabelFrame(cha, text="Đặt lịch hẹn", padding=12)
        form.columnconfigure(0, weight=1, uniform="cot")
        form.columnconfigure(1, weight=1, uniform="cot")

        def nhan(text, row, col=0, span=2):
            ttk.Label(form, text=text).grid(row=row, column=col, columnspan=span,
                                            sticky="w", pady=(6, 0))

        nhan("Bệnh nhân", 0)
        self.cb_benh_nhan = ttk.Combobox(
            form, state="readonly", width=38,
            values=[f"{b['ho_ten']} ({b['ma']})" for b in self.ds_benh_nhan])
        self.cb_benh_nhan.grid(row=1, column=0, columnspan=2, sticky="ew")

        nhan("Bác sĩ", 2)
        self.cb_bac_si = ttk.Combobox(
            form, state="readonly", width=38,
            values=[f"{b['ten']} ({b['ma']})" for b in self.ds_bac_si])
        self.cb_bac_si.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.cb_bac_si.bind("<<ComboboxSelected>>", lambda _e: self._xem_truoc_trung_lich())

        nhan("Ngày khám (năm / tháng / ngày)", 4)
        self.chon_ngay = DatePicker(form, nam_nho_nhat=nam, nam_lon_nhat=nam + 2,
                                    nam_tang_dan=True, gioi_han_hom_nay=False,
                                    khi_doi=self._xem_truoc_trung_lich)
        self.chon_ngay.grid(row=5, column=0, columnspan=2, sticky="ew")

        nhan("Giờ bắt đầu", 6, col=0, span=1)
        nhan("Thời lượng (phút)", 6, col=1, span=1)
        self.cb_gio = ttk.Combobox(form, values=helpers.danh_sach_gio(),
                                   state="readonly", width=8)
        self.cb_gio.grid(row=7, column=0, sticky="ew", padx=(0, 8))
        self.cb_gio.bind("<<ComboboxSelected>>", lambda _e: self._xem_truoc_trung_lich())
        self.cb_thoi_luong = ttk.Combobox(form, values=CAC_THOI_LUONG,
                                          state="readonly", width=8)
        self.cb_thoi_luong.grid(row=7, column=1, sticky="ew")
        self.cb_thoi_luong.bind("<<ComboboxSelected>>", lambda _e: self._xem_truoc_trung_lich())

        self.khung_canh_bao = tk.Frame(form, bg=config.MAU_NEN_LOI, highlightthickness=1,
                                       highlightbackground=config.MAU_LOI)
        tk.Label(self.khung_canh_bao, text="Trùng lịch!", bg=config.MAU_NEN_LOI, fg=config.MAU_LOI,
                 font=config.FONT_DAM).pack(anchor="w", padx=10, pady=(6, 0))
        self.nhan_canh_bao = tk.Label(self.khung_canh_bao, bg=config.MAU_NEN_LOI, fg=config.MAU_LOI,
                                      justify="left", anchor="w", wraplength=270)
        self.nhan_canh_bao.pack(anchor="w", padx=10, pady=(0, 6))
        self.khung_canh_bao.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.khung_canh_bao.grid_remove()

        form.rowconfigure(9, weight=1)

        khung_nut = ttk.Frame(form)
        khung_nut.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        self.nut_huy = None
        for i, (chu, lenh) in enumerate([("Đặt lịch", self.dat_lich), ("Hủy lịch", self.huy_lich),
                                         ("Làm mới", self.lam_moi_form)]):
            khung_nut.columnconfigure(i, weight=1, uniform="nut")
            nut = ttk.Button(khung_nut, text=chu, command=lenh)
            nut.grid(row=0, column=i, sticky="ew", padx=2)
            if chu == "Hủy lịch":
                self.nut_huy = nut

        self._xoa_form()
        return form

    def ap_dung_phan_quyen(self):
        """Admin và lễ tân đều được hủy lịch."""
        if self.vai_tro not in VAI_TRO_DUOC_HUY:
            self.nut_huy.state(["disabled"])

    # ------------------------------------------------------------ hiển thị
    def _lich_theo_bo_loc(self):
        """Ngày chưa chọn = mọi ngày; 'Tất cả bác sĩ' = mọi bác sĩ."""
        ngay = self.loc_ngay.get_date()
        i = self.cb_loc_bac_si.current()
        ma_bs = self.ds_bac_si[i - 1]["ma"] if i > 0 else None
        ket_qua = [lh for lh in self.du_lieu
                   if (ngay is None or lh["ngay"] == ngay)
                   and (ma_bs is None or lh["ma_bac_si"] == ma_bs)]
        return sorted(ket_qua, key=lambda lh: (lh["ngay"], lh["gio"]))

    def hien_thi(self):
        self.dang_hien = self._lich_theo_bo_loc()

        self.tree.delete(*self.tree.get_children())
        for lh in self.dang_hien:
            self.tree.insert("", "end", iid=lh["ma"], values=(
                lh["ma"],
                self.ten_benh_nhan.get(lh["ma_benh_nhan"], lh["ma_benh_nhan"]),
                self.ten_bac_si.get(lh["ma_bac_si"], lh["ma_bac_si"]),
                lh["ngay"].strftime("%d/%m/%Y"),
                lh["gio"],
                f"{lh['thoi_luong']} phút",
            ))
        self._ve_lai_the()

    def _ve_lai_the(self):
        for the in self.khung_the.winfo_children():
            the.destroy()
        self.cac_the = {}
        self.ma_the_dang_chon = None

        if not self.dang_hien:
            tk.Label(self.khung_the, text="Không có lịch hẹn nào", bg=config.MAU_NEN,
                     fg=config.MAU_CHU_MO).pack(side="left", padx=10, pady=10)
        for lh in self.dang_hien:
            the = AppointmentCard(
                self.khung_the, ma=lh["ma"], gio_bat_dau=lh["gio"],
                gio_ket_thuc=helpers.gio_ket_thuc(lh["gio"], lh["thoi_luong"]),
                ten_benh_nhan=self.ten_benh_nhan.get(lh["ma_benh_nhan"], lh["ma_benh_nhan"]),
                ma_benh_nhan=lh["ma_benh_nhan"],
                ten_bac_si=self.ten_bac_si.get(lh["ma_bac_si"], lh["ma_bac_si"]),
                thoi_luong=lh["thoi_luong"], khi_chon=self._khi_chon_the)
            the.pack(side="left", padx=(0, 10), pady=3)
            self.cac_the[lh["ma"]] = the
        self.canvas_the.xview_moveto(0)

    def _danh_dau_the(self, ma):
        """Viền xanh cho thẻ của lịch đang chọn (ma=None: bỏ chọn)."""
        if self.ma_the_dang_chon in self.cac_the:
            self.cac_the[self.ma_the_dang_chon].chon(False)
        self.ma_the_dang_chon = ma if ma in self.cac_the else None
        if self.ma_the_dang_chon:
            self.cac_the[self.ma_the_dang_chon].chon(True)

    def _khi_chon_the(self, ma):
        self.tree.selection_set(ma)
        self.tree.see(ma)

    def _khi_chon_dong(self, _event):
        ma = self._ma_dang_chon()
        lich = self._tim_theo_ma(ma) if ma else None
        self._danh_dau_the(ma if lich else None)
        if not lich:
            return
        for i, b in enumerate(self.ds_benh_nhan):
            if b["ma"] == lich["ma_benh_nhan"]:
                self.cb_benh_nhan.current(i)
        for i, b in enumerate(self.ds_bac_si):
            if b["ma"] == lich["ma_bac_si"]:
                self.cb_bac_si.current(i)
        self.chon_ngay.set_date(lich["ngay"])
        self.cb_gio.set(lich["gio"])
        self.cb_thoi_luong.set(str(lich["thoi_luong"]))
        self._xem_truoc_trung_lich()

    # ------------------------------------------------------------ hỗ trợ
    def _ma_dang_chon(self):
        chon = self.tree.selection()
        return chon[0] if chon else None

    def _tim_theo_ma(self, ma):
        return next((lh for lh in self.du_lieu if lh["ma"] == ma), None)

    def _nap_du_lieu(self):
        """Lấy lịch hẹn từ QuanLyLichHen (bỏ lịch đã hủy)."""
        self.du_lieu = [{"ma": lh.ma_lich_hen, "ma_benh_nhan": lh.ma_benh_nhan,
                         "ma_bac_si": lh.ma_bac_si, "ngay": lh.ngay_hen,
                         "gio": lh.gio_bat_dau, "thoi_luong": lh.thoi_luong}
                        for lh in self.ql.lay_tat_ca() if lh.trang_thai != "Da_huy"]

    def _xoa_form(self):
        self.cb_benh_nhan.set(CHO_BENH_NHAN)
        self.cb_bac_si.set(CHO_BAC_SI)
        self.chon_ngay.set_date(date.today())
        self.cb_gio.set(CHO_GIO)
        self.cb_thoi_luong.set(CHO_THOI_LUONG)
        self._an_canh_bao()

    def _doc_lich_dang_nhap(self):
        """(ma_bac_si, ngay, gio, thoi_luong) nếu đã chọn đủ, ngược lại None."""
        i = self.cb_bac_si.current()
        ngay = self.chon_ngay.get_date()
        gio = self.cb_gio.get()
        thoi_luong = self.cb_thoi_luong.get()
        if i < 0 or ngay is None or ":" not in gio or not thoi_luong.isdigit():
            return None
        return self.ds_bac_si[i]["ma"], ngay, gio, int(thoi_luong)

    # ------------------------------------------------------------ cảnh báo trùng lịch
    def _hien_canh_bao(self, noi_dung):
        self.nhan_canh_bao.configure(text=noi_dung)
        self.khung_canh_bao.grid()

    def _an_canh_bao(self):
        self.khung_canh_bao.grid_remove()

    def _xem_truoc_trung_lich(self):
        """Báo trùng ngay khi chọn bác sĩ/ngày/giờ/thời lượng (chưa cần bấm Đặt lịch)."""
        thong_tin = self._doc_lich_dang_nhap()
        if thong_tin is None:
            self._an_canh_bao()
            return
        ma_bs, ngay, gio, thoi_luong = thong_tin
        trung, thong_diep = self.ql.kiem_tra_trung_lich(
            ma_bs, ngay, gio, thoi_luong, ma_lich_hen_bo_qua=self._ma_dang_chon())
        if trung:
            self._hien_canh_bao(thong_diep)
        else:
            self._an_canh_bao()

    # ------------------------------------------------------------ chức năng
    def _doc_form(self):
        """Kiểm tra form đặt lịch. Trả về dict (chưa có mã lịch hẹn) hoặc None nếu có lỗi."""
        def loi(noi_dung):
            messagebox.showwarning(config.TIEU_DE_APP, noi_dung, parent=self)

        i_bn, i_bs = self.cb_benh_nhan.current(), self.cb_bac_si.current()
        ngay = self.chon_ngay.get_date()
        gio = self.cb_gio.get()
        thoi_luong = self.cb_thoi_luong.get()

        if i_bn < 0:
            loi("Vui lòng chọn bệnh nhân.")
        elif i_bs < 0:
            loi("Vui lòng chọn bác sĩ.")
        elif ngay is None:
            loi("Vui lòng chọn đủ ngày khám (năm, tháng, ngày).")
        elif ngay < date.today():
            loi("Ngày khám không được ở quá khứ.")
        elif ":" not in gio:
            loi("Vui lòng chọn giờ bắt đầu.")
        elif not thoi_luong.isdigit():
            loi("Vui lòng chọn thời lượng.")
        else:
            return {
                "ma_benh_nhan": self.ds_benh_nhan[i_bn]["ma"],
                "ma_bac_si": self.ds_bac_si[i_bs]["ma"],
                "ngay": ngay,
                "gio": gio,
                "thoi_luong": int(thoi_luong),
            }
        return None

    def loc(self):
        self.hien_thi()
        self.thong_bao(f"Có {len(self.dang_hien)} lịch hẹn")

    def lam_moi_bo_loc(self):
        """Bỏ lọc: mọi ngày, mọi bác sĩ."""
        self.loc_ngay.clear()
        self.cb_loc_bac_si.current(0)
        self.hien_thi()
        self.thong_bao(f"Đã làm mới, có {len(self.dang_hien)} lịch hẹn")

    def lam_moi_form(self):
        self.tree.selection_remove(self.tree.selection())
        self._xoa_form()

    def dat_lich(self):
        lich = self._doc_form()
        if not lich:
            return
        trung, thong_diep = self.ql.kiem_tra_trung_lich(
            lich["ma_bac_si"], lich["ngay"], lich["gio"], lich["thoi_luong"])
        if trung:
            self._hien_canh_bao(thong_diep)
            self.thong_bao("Không đặt được lịch: bác sĩ bị trùng lịch")
            return
        ok, thong_diep, lh = self.ql.dat_lich({
            "ma_benh_nhan": lich["ma_benh_nhan"], "ma_bac_si": lich["ma_bac_si"],
            "ngay_hen": lich["ngay"].strftime("%d-%m-%Y"),     # hợp đồng hàm: DD-MM-YYYY
            "gio_bat_dau": lich["gio"], "thoi_luong": lich["thoi_luong"]})
        if not ok:
            messagebox.showwarning(config.TIEU_DE_APP, thong_diep, parent=self)
            self.thong_bao(thong_diep)
            return
        self._nap_du_lieu()
        self.lam_moi_form()
        self.hien_thi()
        self.thong_bao(thong_diep)

    def huy_lich(self):
        ma = self._ma_dang_chon()
        lich = self._tim_theo_ma(ma) if ma else None
        if not lich:
            messagebox.showinfo(config.TIEU_DE_APP,
                                "Hãy chọn một lịch hẹn trong bảng trước.", parent=self)
            return
        ten = self.ten_benh_nhan.get(lich["ma_benh_nhan"], lich["ma_benh_nhan"])
        if not messagebox.askyesno(
                config.TIEU_DE_APP,
                f"Hủy lịch {ma} của {ten} lúc {lich['gio']} "
                f"ngày {lich['ngay'].strftime('%d/%m/%Y')}?", parent=self):
            return
        ok, thong_diep = self.ql.huy_lich(ma)
        if not ok:
            messagebox.showwarning(config.TIEU_DE_APP, thong_diep, parent=self)
            self.thong_bao(thong_diep)
            return
        self._nap_du_lieu()
        self.lam_moi_form()
        self.hien_thi()
        self.thong_bao(f"Đã hủy lịch {ma}")
