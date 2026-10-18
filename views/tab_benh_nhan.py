"""Tab Bệnh nhân: tìm kiếm, bảng và form thông tin."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import config
from views import helpers
from views.widgets.date_picker import DatePicker

CAC_COT = [
    ("ma", "Mã", 125),
    ("ho_ten", "Họ tên", 160),
    ("ngay_sinh", "Ngày sinh", 90),
    ("sdt", "SĐT", 95),
    ("bhyt", "Mã BHYT", 140),
    ("tinh", "Tỉnh/Thành", 95),
]

TIM_THEO = {"Họ tên": "ho_ten", "Mã": "ma", "SĐT": "sdt", "Mã BHYT": "bhyt"}

DANH_SACH_GIOI_TINH = ["Nam", "Nữ", "Khác"]
DANH_SACH_NHOM_MAU = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
CHO_TINH, CHO_XA = "Chọn tỉnh/thành", "Chọn phường/xã"

# NỐI C (Tuần 10): thay hai hằng số này bằng API provinces.open-api.vn của C
DANH_SACH_TINH = ["Hà Nội", "Đà Nẵng", "TP.HCM", "Hải Phòng", "Cần Thơ"]
PHUONG_XA_MAU = {
    "Hà Nội": ["Phường Hoàn Kiếm", "Phường Ba Đình", "Phường Cầu Giấy"],
    "Đà Nẵng": ["Phường Hải Châu", "Phường Thanh Khê", "Phường Sơn Trà"],
    "TP.HCM": ["Phường Bến Nghé", "Phường Bến Thành", "Phường Võ Thị Sáu"],
    "Hải Phòng": ["Phường Hồng Bàng", "Phường Ngô Quyền", "Phường Lê Chân"],
    "Cần Thơ": ["Phường Ninh Kiều", "Phường Cái Khế", "Phường An Hòa"],
}

# Dữ liệu giả (NỐI A). Mã bệnh nhân đúng định dạng của A: 14 chữ số, 8 số đầu là ngày.
KHOA_DU_LIEU = ("ma", "ho_ten", "ngay_sinh", "sdt", "bhyt", "tinh", "xa_phuong",
                "dia_chi", "gioi_tinh", "email", "nhom_mau", "tien_su")
DU_LIEU_GIA = [
    ("05102026000001", "Nguyễn Văn An", "12/03/1990", "0912345678", "4010123456789", "Hà Nội",
     "Phường Hoàn Kiếm", "12 Hàng Bạc", "Nam", "an.nguyen@mail.com", "O+", ""),
    ("05102026000002", "Trần Thị Bình", "25/07/1985", "0987654321", "4010987654321", "Đà Nẵng",
     "Phường Hải Châu", "45 Bạch Đằng", "Nữ", "binh.tran@mail.com", "A+", "Viêm dạ dày"),
    ("06102026000003", "Lê Minh Châu", "03/11/2001", "0901122334", "4011122233344", "TP.HCM",
     "Phường Bến Nghé", "8 Lê Lợi", "Nữ", "chau.le@mail.com", "B+", ""),
    ("07102026000004", "Phạm Quốc Dũng", "18/05/1978", "0934455667", "4015566778899", "Hải Phòng",
     "Phường Ngô Quyền", "23 Lạch Tray", "Nam", "dung.pham@mail.com", "AB+", "Tiểu đường"),
    ("08102026000005", "Hoàng Thu Hà", "30/09/1995", "0977788990", "4017788990011", "Cần Thơ",
     "Phường Ninh Kiều", "77 Hòa Bình", "Nữ", "ha.hoang@mail.com", "O-", ""),
    ("09102026000006", "Vũ Đức Huy", "09/02/1969", "0966677889", "4016677889900", "Hà Nội",
     "Phường Ba Đình", "5 Đội Cấn", "Nam", "huy.vu@mail.com", "A-", "Cao huyết áp"),
    ("12102026000007", "Đặng Mỹ Linh", "21/12/2003", "0955566778", "4015566778800", "Đà Nẵng",
     "Phường Sơn Trà", "19 Ngô Quyền", "Nữ", "", "B-", ""),
    ("12102026000008", "Bùi Anh Khoa", "14/08/1999", "0944455667", "4014455667711", "TP.HCM",
     "Phường Bến Thành", "102 Nguyễn Huệ", "Nam", "khoa.bui@mail.com", "O+", ""),
]


class TabBenhNhan(ttk.Frame):
    def __init__(self, parent, thong_bao=None, vai_tro="admin"):
        super().__init__(parent)
        self.thong_bao = thong_bao or (lambda _s: None)
        self.vai_tro = vai_tro
        self.cac_nut_sua_doi = []

        # NỐI A (Tuần 10): thay bằng lay_tat_ca()
        self.du_lieu = [dict(zip(KHOA_DU_LIEU, dong)) for dong in DU_LIEU_GIA]

        self.var_tu_khoa = tk.StringVar()
        self.var_ho_ten = tk.StringVar()
        self.var_gioi_tinh = tk.StringVar(value="")
        self.var_sdt = tk.StringVar()
        self.var_bhyt = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_dia_chi = tk.StringVar()
        self.var_tien_su = tk.StringVar()

        self._tao_thanh_tim_kiem()
        khung_chinh = ttk.Frame(self)
        khung_chinh.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        khung_chinh.columnconfigure(0, weight=1)
        khung_chinh.columnconfigure(1, weight=0)
        khung_chinh.rowconfigure(0, weight=1)
        self._tao_bang(khung_chinh).grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._tao_form(khung_chinh).grid(row=0, column=1, sticky="ns")

        self.hien_thi(self.du_lieu)
        self.ap_dung_phan_quyen()

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
        form = ttk.LabelFrame(cha, text="Thông tin bệnh nhân (* là bắt buộc)", padding=12)
        form.columnconfigure(0, weight=1, uniform="cot")
        form.columnconfigure(1, weight=1, uniform="cot")

        def nhan(text, row, col=0, span=2):
            ttk.Label(form, text=text).grid(row=row, column=col, columnspan=span,
                                            sticky="w", pady=(6, 0))

        nhan("Họ tên *", 0)
        ttk.Entry(form, textvariable=self.var_ho_ten, width=38).grid(
            row=1, column=0, columnspan=2, sticky="ew")

        nhan("Ngày sinh * (năm / tháng / ngày)", 2)
        self.chon_ngay_sinh = DatePicker(form)
        self.chon_ngay_sinh.grid(row=3, column=0, columnspan=2, sticky="ew")

        nhan("Giới tính *", 4, col=0, span=1)
        nhan("Nhóm máu", 4, col=1, span=1)
        khung_gt = ttk.Frame(form)
        khung_gt.grid(row=5, column=0, sticky="w")
        for i, gt in enumerate(DANH_SACH_GIOI_TINH):
            ttk.Radiobutton(khung_gt, text=gt, value=gt, variable=self.var_gioi_tinh).pack(
                side="left", padx=(0 if i == 0 else 10, 0))
        self.cb_nhom_mau = ttk.Combobox(form, values=DANH_SACH_NHOM_MAU, state="readonly", width=8)
        self.cb_nhom_mau.grid(row=5, column=1, sticky="ew")

        nhan("Số điện thoại * (10 số)", 6, col=0, span=1)
        nhan("Mã BHYT", 6, col=1, span=1)
        ttk.Entry(form, textvariable=self.var_sdt, width=16).grid(
            row=7, column=0, sticky="ew", padx=(0, 8))
        ttk.Entry(form, textvariable=self.var_bhyt, width=16).grid(row=7, column=1, sticky="ew")

        nhan("Email", 8)
        ttk.Entry(form, textvariable=self.var_email).grid(
            row=9, column=0, columnspan=2, sticky="ew")

        nhan("Địa chỉ * (số nhà, tên đường)", 10)
        ttk.Entry(form, textvariable=self.var_dia_chi).grid(
            row=11, column=0, columnspan=2, sticky="ew")

        nhan("Tỉnh/Thành *", 12, col=0, span=1)
        nhan("Phường/Xã *", 12, col=1, span=1)
        self.cb_tinh = ttk.Combobox(form, values=DANH_SACH_TINH, state="readonly", width=16)
        self.cb_tinh.grid(row=13, column=0, sticky="ew", padx=(0, 8))
        self.cb_tinh.bind("<<ComboboxSelected>>", lambda _e: self._khi_chon_tinh())
        self.cb_xa = ttk.Combobox(form, state="readonly", width=16)
        self.cb_xa.grid(row=13, column=1, sticky="ew")

        nhan("Tiền sử bệnh", 14)
        ttk.Entry(form, textvariable=self.var_tien_su).grid(
            row=15, column=0, columnspan=2, sticky="ew")

        form.rowconfigure(16, weight=1)
        khung_nut = ttk.Frame(form)
        khung_nut.grid(row=17, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        for i, (chu, lenh) in enumerate([("Thêm", self.them), ("Sửa", self.sua),
                                         ("Xóa", self.xoa), ("Làm mới", self.lam_moi_form)]):
            khung_nut.columnconfigure(i, weight=1, uniform="nut")
            nut = ttk.Button(khung_nut, text=chu, command=lenh)
            nut.grid(row=0, column=i, sticky="ew", padx=2)
            if chu in ("Thêm", "Sửa", "Xóa"):
                self.cac_nut_sua_doi.append(nut)

        self._xoa_form()
        return form

    def ap_dung_phan_quyen(self):
        """Khóa các nút Thêm/Sửa/Xóa nếu không phải admin."""
        if self.vai_tro != "admin":
            for nut in self.cac_nut_sua_doi:
                nut.state(["disabled"])

    # ------------------------------------------------------------ tỉnh / phường xã
    def _khi_chon_tinh(self):
        """Đổi tỉnh thì danh sách phường/xã đổi theo và phải chọn lại phường/xã."""
        self._cap_nhat_xa(self.cb_tinh.get())
        self.cb_xa.set(CHO_XA)

    def _cap_nhat_xa(self, tinh):
        # NỐI C (Tuần 10): lấy phường/xã của tỉnh từ API của C
        self.cb_xa["values"] = PHUONG_XA_MAU.get(tinh, [])

    # ------------------------------------------------------------ hiển thị
    def hien_thi(self, danh_sach):
        self.tree.delete(*self.tree.get_children())
        for b in danh_sach:
            self.tree.insert("", "end", iid=b["ma"],
                             values=tuple(b[khoa] for khoa, _t, _r in CAC_COT))

    def _khi_chon_dong(self, _event):
        ma = self._ma_dang_chon()
        b = self._tim_theo_ma(ma) if ma else None
        if not b:
            return
        self.var_ho_ten.set(b["ho_ten"])
        self.chon_ngay_sinh.set(b["ngay_sinh"])
        self.var_gioi_tinh.set(b["gioi_tinh"])
        self.cb_nhom_mau.set(b["nhom_mau"])
        self.var_sdt.set(b["sdt"])
        self.var_bhyt.set("" if b["bhyt"] == "Không có" else b["bhyt"])
        self.var_email.set(b["email"])
        self.var_dia_chi.set(b["dia_chi"])
        self.cb_tinh.set(b["tinh"])
        self._cap_nhat_xa(b["tinh"])
        self.cb_xa.set(b["xa_phuong"])
        self.var_tien_su.set(b["tien_su"])

    # ------------------------------------------------------------ hỗ trợ
    def _ma_dang_chon(self):
        chon = self.tree.selection()
        return chon[0] if chon else None

    def _tim_theo_ma(self, ma):
        return next((b for b in self.du_lieu if b["ma"] == ma), None)

    def _ma_moi(self):
        """Mã 14 số: 8 số đầu là ngày hôm nay (ddmmyyyy) + 6 số thứ tự tiếp theo."""
        so_lon_nhat = max((int(b["ma"][8:]) for b in self.du_lieu), default=0)
        return f"{date.today():%d%m%Y}{so_lon_nhat + 1:06d}"

    def _xoa_form(self):
        for bien in (self.var_ho_ten, self.var_sdt, self.var_bhyt, self.var_email,
                     self.var_dia_chi, self.var_tien_su):
            bien.set("")
        self.chon_ngay_sinh.clear()
        self.var_gioi_tinh.set("")
        self.cb_nhom_mau.set("")
        self.cb_tinh.set(CHO_TINH)
        self._cap_nhat_xa("")
        self.cb_xa.set(CHO_XA)

    def _doc_form(self):
        """Kiểm tra form theo điều kiện của model (A). Trả về dict hoặc None nếu có lỗi."""
        def loi(noi_dung):
            messagebox.showwarning(config.TIEU_DE_APP, noi_dung, parent=self)
            return None

        ho_ten = self.var_ho_ten.get().strip()
        ngay_sinh = self.chon_ngay_sinh.get()
        gioi_tinh = self.var_gioi_tinh.get()
        sdt = self.var_sdt.get().strip()
        bhyt = self.var_bhyt.get().strip()
        email = self.var_email.get().strip()
        dia_chi = self.var_dia_chi.get().strip()

        if not ho_ten:
            return loi("Họ tên không được để trống.")
        if not ngay_sinh:
            return loi("Vui lòng chọn đủ ngày sinh (năm, tháng, ngày).")
        if not gioi_tinh:
            return loi("Vui lòng chọn giới tính.")
        if not helpers.la_sdt_hop_le(sdt):
            return loi("Số điện thoại phải gồm đúng 10 chữ số.")
        if bhyt and not helpers.la_bhyt_hop_le(bhyt):
            return loi("Mã BHYT phải gồm đúng 13 chữ số (hoặc để trống).")
        if email and not helpers.la_email_hop_le(email):
            return loi("Email không hợp lệ.")
        if not dia_chi:
            return loi("Vui lòng nhập địa chỉ (số nhà, tên đường).")
        if self.cb_tinh.current() < 0:
            return loi("Vui lòng chọn Tỉnh/Thành.")
        if self.cb_xa.current() < 0:
            return loi("Vui lòng chọn Phường/Xã.")

        return {
            "ho_ten": ho_ten,
            "ngay_sinh": ngay_sinh,
            "gioi_tinh": gioi_tinh,
            "nhom_mau": self.cb_nhom_mau.get(),
            "sdt": sdt,
            "bhyt": bhyt or "Không có",
            "email": email,
            "dia_chi": dia_chi,
            "tinh": self.cb_tinh.get(),
            "xa_phuong": self.cb_xa.get(),
            "tien_su": self.var_tien_su.get().strip(),
        }

    # ------------------------------------------------------------ chức năng
    def tim(self):
        """Tìm không cần chính xác: không phân biệt hoa/thường và dấu tiếng Việt."""
        khoa = TIM_THEO[self.cb_tim_theo.get()]
        tu_khoa = self.var_tu_khoa.get()
        # NỐI A (Tuần 10): thay bằng tim_kiem(...) nếu A đã làm tìm kiếm tương tự
        ket_qua = [b for b in self.du_lieu if helpers.khop(khoa, b[khoa], tu_khoa)]
        self.hien_thi(ket_qua)
        self.thong_bao(f"Tìm thấy {len(ket_qua)} bệnh nhân")

    def lam_moi_danh_sach(self):
        self.var_tu_khoa.set("")
        self.hien_thi(self.du_lieu)
        self.thong_bao("Đã làm mới danh sách")

    def lam_moi_form(self):
        self.tree.selection_remove(self.tree.selection())
        self._xoa_form()

    def them(self):
        du_lieu_form = self._doc_form()
        if not du_lieu_form:
            return
        du_lieu_form["ma"] = self._ma_moi()
        self.du_lieu.append(du_lieu_form)  # NỐI A (Tuần 10): them(...)
        self.hien_thi(self.du_lieu)
        self.lam_moi_form()
        self.thong_bao(f"Đã thêm bệnh nhân {du_lieu_form['ma']}")

    def sua(self):
        ma = self._ma_dang_chon()
        if not ma:
            messagebox.showinfo(config.TIEU_DE_APP, "Hãy chọn một bệnh nhân trong bảng trước.", parent=self)
            return
        du_lieu_form = self._doc_form()
        if not du_lieu_form:
            return
        self._tim_theo_ma(ma).update(du_lieu_form)  # NỐI A (Tuần 10)
        self.hien_thi(self.du_lieu)
        self.tree.selection_set(ma)
        self.thong_bao(f"Đã cập nhật bệnh nhân {ma}")

    def xoa(self):
        ma = self._ma_dang_chon()
        if not ma:
            messagebox.showinfo(config.TIEU_DE_APP, "Hãy chọn một bệnh nhân trong bảng trước.", parent=self)
            return
        b = self._tim_theo_ma(ma)
        if not messagebox.askyesno(config.TIEU_DE_APP,
                                   f"Xóa bệnh nhân {ma} - {b['ho_ten']}?", parent=self):
            return
        self.du_lieu.remove(b)  # NỐI A (Tuần 10): xoa(ma)
        self.hien_thi(self.du_lieu)
        self.lam_moi_form()
        self.thong_bao(f"Đã xóa bệnh nhân {ma}")
