"""Tab Phiếu khám: danh sách phiếu và form lập phiếu."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import config
from views import helpers
from views.tab_lich_hen import (DU_LIEU_BENH_NHAN_GIA, DU_LIEU_BAC_SI_GIA, _tao_lich_gia)

CAC_COT = [
    ("ma", "Mã phiếu", 75),
    ("ngay", "Ngày khám", 90),
    ("benh_nhan", "Bệnh nhân", 150),
    ("bac_si", "Bác sĩ", 150),
    ("chan_doan", "Chẩn đoán", 150),
    ("tong_tien", "Tổng tiền", 100),
]
TIM_THEO = {"Bệnh nhân": "benh_nhan", "Mã phiếu": "ma", "Chẩn đoán": "chan_doan"}
CHO_LICH = "Chọn lịch hẹn"

# NỐI A: danh mục dịch vụ (models/dich_vu.py của A) - tên và đơn giá
DANH_SACH_DICH_VU = [
    ("Khám tổng quát", 150000),
    ("Xét nghiệm máu", 200000),
    ("Siêu âm", 250000),
    ("X-quang", 180000),
    ("Điện tim", 120000),
]


class TabPhieuKham(ttk.Frame):
    def __init__(self, parent, thong_bao=None, vai_tro="admin"):
        super().__init__(parent)
        self.thong_bao = thong_bao or (lambda _s: None)
        self.vai_tro = vai_tro
        self.cac_nut_sua_doi = []

        # NỐI A: lấy danh sách thật từ lớp quản lý bệnh nhân / bác sĩ / lịch hẹn
        self.ten_benh_nhan = dict(DU_LIEU_BENH_NHAN_GIA)
        self.ten_bac_si = {m: f"{self._hoc_vi(m)}. {t}" for m, t in DU_LIEU_BAC_SI_GIA}
        self.ds_lich_hen = {l["ma"]: l for l in _tao_lich_gia()}
        self.du_lieu = self._tao_phieu_gia()   # NỐI A: lay_tat_ca()

        self.ma_dang_sua = None
        self.lich_cho = []
        self.var_tu_khoa = tk.StringVar()
        self.var_chan_doan = tk.StringVar()
        self.var_benh_nhan = tk.StringVar(value="-")
        self.var_bac_si = tk.StringVar(value="-")
        self.var_ngay = tk.StringVar(value="-")
        self.var_tong = tk.StringVar(value=helpers.dinh_dang_tien(0))
        self.var_dich_vu = {ten: tk.BooleanVar(value=False) for ten, _g in DANH_SACH_DICH_VU}

        self._tao_thanh_tim_kiem()
        khung_chinh = ttk.Frame(self)
        khung_chinh.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        khung_chinh.columnconfigure(0, weight=1)
        khung_chinh.columnconfigure(1, weight=0)
        khung_chinh.rowconfigure(0, weight=1)
        self._tao_bang(khung_chinh).grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._tao_form(khung_chinh).grid(row=0, column=1, sticky="ns")

        self.hien_thi(self.du_lieu)
        self._cap_nhat_ds_lich()
        self.ap_dung_phan_quyen()

    @staticmethod
    def _hoc_vi(ma_bac_si):
        return getattr(config, "hoc_vi", {}).get(ma_bac_si[:2], "BS")

    def _tao_phieu_gia(self):
        """Hai phiếu giả cho hai lịch hẹn đầu của hôm nay."""
        mau = [
            ("PK001", "LH001", "Viêm họng cấp", ["Khám tổng quát"], "Sốt nhẹ, đau họng 2 ngày",
             "Paracetamol 500mg x 10 viên", "Uống nhiều nước ấm"),
            ("PK002", "LH002", "Viêm dạ dày", ["Khám tổng quát", "Siêu âm"], "Đau thượng vị",
             "Omeprazol 20mg x 14 viên", "Tránh đồ cay, tái khám sau 2 tuần"),
        ]
        ket_qua = []
        for ma, ma_lich, chan_doan, dich_vu, trieu_chung, don_thuoc, loi_dan in mau:
            lich = self.ds_lich_hen[ma_lich]
            ket_qua.append({
                "ma": ma, "ma_lich_hen": ma_lich, "ma_benh_nhan": lich["ma_benh_nhan"],
                "ma_bac_si": lich["ma_bac_si"], "ngay": lich["ngay"],
                "trieu_chung": trieu_chung, "chan_doan": chan_doan, "dich_vu": dich_vu,
                "don_thuoc": don_thuoc, "loi_dan": loi_dan,
                "tong_tien": self._tinh_tong(dich_vu),
            })
        return ket_qua

    # ------------------------------------------------------------ giao diện
    def _tao_thanh_tim_kiem(self):
        thanh = ttk.Frame(self)
        thanh.pack(fill="x", padx=10, pady=10)
        thanh.columnconfigure(2, weight=1)

        ttk.Label(thanh, text="Tìm theo:").grid(row=0, column=0, padx=(0, 6))
        self.cb_tim_theo = ttk.Combobox(thanh, values=list(TIM_THEO), state="readonly", width=12)
        self.cb_tim_theo.current(0)
        self.cb_tim_theo.grid(row=0, column=1, padx=(0, 8))
        o_tim = ttk.Entry(thanh, textvariable=self.var_tu_khoa)
        o_tim.grid(row=0, column=2, sticky="ew", padx=(0, 8))
        o_tim.bind("<Return>", lambda _e: self.tim())
        ttk.Button(thanh, text="Tìm", command=self.tim).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(thanh, text="Làm mới", command=self.lam_moi_danh_sach).grid(row=0, column=4)

    def _tao_bang(self, cha):
        khung = ttk.Frame(cha)
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
        return khung

    def _tao_form(self, cha):
        form = ttk.LabelFrame(cha, text="Phiếu khám (* là bắt buộc)", padding=12)
        form.columnconfigure(0, weight=1)

        def nhan(text, row):
            ttk.Label(form, text=text).grid(row=row, column=0, sticky="w", pady=(6, 0))

        nhan("Lịch hẹn *", 0)
        self.cb_lich = ttk.Combobox(form, state="readonly", width=44)
        self.cb_lich.grid(row=1, column=0, sticky="ew")
        self.cb_lich.bind("<<ComboboxSelected>>", lambda _e: self._khi_chon_lich())

        khung_tt = ttk.Frame(form)
        khung_tt.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        for i, (chu, bien) in enumerate([("Bệnh nhân:", self.var_benh_nhan),
                                         ("Bác sĩ:", self.var_bac_si),
                                         ("Ngày khám:", self.var_ngay)]):
            ttk.Label(khung_tt, text=chu).grid(row=i, column=0, sticky="w", padx=(0, 8))
            ttk.Label(khung_tt, textvariable=bien).grid(row=i, column=1, sticky="w")

        nhan("Triệu chứng", 3)
        self.o_trieu_chung = tk.Text(form, height=2, width=44, wrap="word")
        self.o_trieu_chung.grid(row=4, column=0, sticky="ew")

        nhan("Chẩn đoán *", 5)
        ttk.Entry(form, textvariable=self.var_chan_doan).grid(row=6, column=0, sticky="ew")

        nhan("Dịch vụ đã dùng * (tick để chọn)", 7)
        khung_dv = ttk.Frame(form)
        khung_dv.grid(row=8, column=0, sticky="ew")
        for ten, gia in DANH_SACH_DICH_VU:
            ttk.Checkbutton(khung_dv, text=f"{ten} - {helpers.dinh_dang_tien(gia)}",
                            variable=self.var_dich_vu[ten],
                            command=self._cap_nhat_tong).pack(anchor="w")
        khung_tong = ttk.Frame(form)
        khung_tong.grid(row=9, column=0, sticky="ew", pady=(4, 0))
        ttk.Label(khung_tong, text="Tổng tiền:").pack(side="left")
        ttk.Label(khung_tong, textvariable=self.var_tong,
                  font=config.FONT_TIEU_DE).pack(side="left", padx=8)

        nhan("Đơn thuốc", 10)
        self.o_don_thuoc = tk.Text(form, height=3, width=44, wrap="word")
        self.o_don_thuoc.grid(row=11, column=0, sticky="ew")

        nhan("Lời dặn", 12)
        self.o_loi_dan = tk.Text(form, height=2, width=44, wrap="word")
        self.o_loi_dan.grid(row=13, column=0, sticky="ew")

        form.rowconfigure(14, weight=1)
        khung_nut = ttk.Frame(form)
        khung_nut.grid(row=15, column=0, sticky="ew", pady=(14, 0))
        for i, (chu, lenh) in enumerate([("Lưu phiếu", self.them), ("Sửa", self.sua),
                                         ("Xóa", self.xoa), ("Làm mới", self.lam_moi_form)]):
            khung_nut.columnconfigure(i, weight=1, uniform="nut")
            nut = ttk.Button(khung_nut, text=chu, command=lenh)
            nut.grid(row=0, column=i, sticky="ew", padx=2)
            if chu != "Làm mới":
                self.cac_nut_sua_doi.append(nut)
        return form

    def ap_dung_phan_quyen(self):
        """Khóa các nút Lưu/Sửa/Xóa nếu không phải admin."""
        if self.vai_tro != "admin":
            for nut in self.cac_nut_sua_doi:
                nut.state(["disabled"])

    # ------------------------------------------------------------ hỗ trợ
    @staticmethod
    def _tinh_tong(ds_dich_vu):
        gia = dict(DANH_SACH_DICH_VU)
        return sum(gia[ten] for ten in ds_dich_vu)

    def _dich_vu_da_chon(self):
        return [ten for ten, _g in DANH_SACH_DICH_VU if self.var_dich_vu[ten].get()]

    def _cap_nhat_tong(self):
        self.var_tong.set(helpers.dinh_dang_tien(self._tinh_tong(self._dich_vu_da_chon())))

    @staticmethod
    def _lay_text(o):
        return o.get("1.0", "end").strip()

    @staticmethod
    def _dat_text(o, noi_dung):
        o.delete("1.0", "end")
        o.insert("1.0", noi_dung)

    def _ma_dang_chon(self):
        chon = self.tree.selection()
        return chon[0] if chon else None

    def _tim_theo_ma(self, ma):
        return next((p for p in self.du_lieu if p["ma"] == ma), None)

    def _ma_moi(self):
        so_lon_nhat = max((int(p["ma"][2:]) for p in self.du_lieu), default=0)
        return f"PK{so_lon_nhat + 1:03d}"

    def _nhan_lich(self, lich):
        ten = self.ten_benh_nhan[lich["ma_benh_nhan"]]
        return f"{lich['ma']} - {ten} - {lich['gio']} ({lich['ngay']:%d/%m/%Y})"

    def _cap_nhat_ds_lich(self):
        """Ô chọn lịch hẹn chỉ liệt kê lịch đã tới ngày khám và chưa có phiếu."""
        da_co = {p["ma_lich_hen"] for p in self.du_lieu}
        hom_nay = date.today()
        self.lich_cho = sorted(
            (l for l in self.ds_lich_hen.values()
             if l["ma"] not in da_co and l["ngay"] <= hom_nay),
            key=lambda l: (l["ngay"], l["gio"]))
        self.cb_lich["values"] = [self._nhan_lich(l) for l in self.lich_cho]
        self.cb_lich.set(CHO_LICH)

    def _hien_thong_tin_lich(self, lich):
        if lich:
            self.var_benh_nhan.set(f"{self.ten_benh_nhan[lich['ma_benh_nhan']]} ({lich['ma_benh_nhan']})")
            self.var_bac_si.set(self.ten_bac_si[lich["ma_bac_si"]])
            self.var_ngay.set(f"{lich['ngay']:%d/%m/%Y}")
        else:
            for bien in (self.var_benh_nhan, self.var_bac_si, self.var_ngay):
                bien.set("-")

    def _khi_chon_lich(self):
        i = self.cb_lich.current()
        self._hien_thong_tin_lich(self.lich_cho[i] if i >= 0 else None)

    def _xoa_form(self):
        self.ma_dang_sua = None
        self.cb_lich.state(["!disabled"])
        self._cap_nhat_ds_lich()
        self._hien_thong_tin_lich(None)
        self._dat_text(self.o_trieu_chung, "")
        self.var_chan_doan.set("")
        for bien in self.var_dich_vu.values():
            bien.set(False)
        self._cap_nhat_tong()
        self._dat_text(self.o_don_thuoc, "")
        self._dat_text(self.o_loi_dan, "")

    def _doc_form(self, can_lich_moi):
        """Kiểm tra form. Trả về dict hoặc None nếu có lỗi."""
        def loi(noi_dung):
            messagebox.showwarning(config.TIEU_DE_APP, noi_dung, parent=self)
            return None

        chan_doan = self.var_chan_doan.get().strip()
        dich_vu = self._dich_vu_da_chon()
        if can_lich_moi and self.cb_lich.current() < 0:
            return loi("Vui lòng chọn lịch hẹn.")
        if not chan_doan:
            return loi("Chẩn đoán không được để trống.")
        if not dich_vu:
            return loi("Vui lòng chọn ít nhất một dịch vụ.")
        return {
            "trieu_chung": self._lay_text(self.o_trieu_chung),
            "chan_doan": chan_doan,
            "dich_vu": dich_vu,
            "don_thuoc": self._lay_text(self.o_don_thuoc),
            "loi_dan": self._lay_text(self.o_loi_dan),
            "tong_tien": self._tinh_tong(dich_vu),
        }

    # ------------------------------------------------------------ hiển thị
    def hien_thi(self, danh_sach):
        self.tree.delete(*self.tree.get_children())
        for p in danh_sach:
            self.tree.insert("", "end", iid=p["ma"], values=(
                p["ma"], f"{p['ngay']:%d/%m/%Y}", self.ten_benh_nhan[p["ma_benh_nhan"]],
                self.ten_bac_si[p["ma_bac_si"]], p["chan_doan"],
                helpers.dinh_dang_tien(p["tong_tien"])))

    def _khi_chon_dong(self, _event):
        ma = self._ma_dang_chon()
        p = self._tim_theo_ma(ma) if ma else None
        if not p:
            return
        self.ma_dang_sua = ma
        lich = self.ds_lich_hen[p["ma_lich_hen"]]
        self.lich_cho = [lich]
        self.cb_lich["values"] = [self._nhan_lich(lich)]
        self.cb_lich.current(0)
        self.cb_lich.state(["disabled"])
        self._hien_thong_tin_lich(lich)
        self._dat_text(self.o_trieu_chung, p["trieu_chung"])
        self.var_chan_doan.set(p["chan_doan"])
        for ten, bien in self.var_dich_vu.items():
            bien.set(ten in p["dich_vu"])
        self._cap_nhat_tong()
        self._dat_text(self.o_don_thuoc, p["don_thuoc"])
        self._dat_text(self.o_loi_dan, p["loi_dan"])

    # ------------------------------------------------------------ chức năng
    def tim(self):
        """Tìm không cần chính xác: không phân biệt hoa/thường và dấu tiếng Việt."""
        khoa = TIM_THEO[self.cb_tim_theo.get()]
        tu_khoa = self.var_tu_khoa.get()
        ket_qua = []
        for p in self.du_lieu:
            gia_tri = {"benh_nhan": self.ten_benh_nhan[p["ma_benh_nhan"]],
                       "ma": p["ma"], "chan_doan": p["chan_doan"]}[khoa]
            if helpers.khop("ho_ten" if khoa == "benh_nhan" else khoa, gia_tri, tu_khoa):
                ket_qua.append(p)
        self.hien_thi(ket_qua)
        self.thong_bao(f"Tìm thấy {len(ket_qua)} phiếu khám")

    def lam_moi_danh_sach(self):
        self.var_tu_khoa.set("")
        self.hien_thi(self.du_lieu)
        self.thong_bao("Đã làm mới danh sách")

    def lam_moi_form(self):
        self.tree.selection_remove(self.tree.selection())
        self._xoa_form()

    def them(self):
        if self.ma_dang_sua:
            messagebox.showinfo(config.TIEU_DE_APP,
                                "Phiếu này đã lập. Bấm Làm mới để lập phiếu cho lịch hẹn khác.",
                                parent=self)
            return
        du_lieu_form = self._doc_form(can_lich_moi=True)
        if not du_lieu_form:
            return
        lich = self.lich_cho[self.cb_lich.current()]
        du_lieu_form.update({"ma": self._ma_moi(), "ma_lich_hen": lich["ma"],
                             "ma_benh_nhan": lich["ma_benh_nhan"],
                             "ma_bac_si": lich["ma_bac_si"], "ngay": lich["ngay"]})
        self.du_lieu.append(du_lieu_form)   # NỐI A: them(...)
        self.hien_thi(self.du_lieu)
        self.lam_moi_form()
        self.thong_bao(f"Đã lưu phiếu khám {du_lieu_form['ma']}")

    def sua(self):
        if not self.ma_dang_sua:
            messagebox.showinfo(config.TIEU_DE_APP, "Hãy chọn một phiếu trong bảng trước.", parent=self)
            return
        du_lieu_form = self._doc_form(can_lich_moi=False)
        if not du_lieu_form:
            return
        ma = self.ma_dang_sua
        self._tim_theo_ma(ma).update(du_lieu_form)   # NỐI A
        self.hien_thi(self.du_lieu)
        self.tree.selection_set(ma)
        self.thong_bao(f"Đã cập nhật phiếu khám {ma}")

    def xoa(self):
        ma = self._ma_dang_chon()
        if not ma:
            messagebox.showinfo(config.TIEU_DE_APP, "Hãy chọn một phiếu trong bảng trước.", parent=self)
            return
        if not messagebox.askyesno(config.TIEU_DE_APP, f"Xóa phiếu khám {ma}?", parent=self):
            return
        self.du_lieu.remove(self._tim_theo_ma(ma))   # NỐI A: xoa(ma)
        self.hien_thi(self.du_lieu)
        self.lam_moi_form()
        self.thong_bao(f"Đã xóa phiếu khám {ma}")
