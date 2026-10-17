"""Tab Bệnh nhân: tìm kiếm + bảng Treeview + form thông tin
"""
import tkinter as tk
from tkinter import ttk, messagebox

import config
from views import helpers
from views.widgets.date_picker import DatePicker

# khóa, tiêu đề cột, độ rộng
CAC_COT = [
    ("ma", "Mã", 70),
    ("ho_ten", "Họ tên", 170),
    ("ngay_sinh", "Ngày sinh", 95),
    ("sdt", "SĐT", 105),
    ("bhyt", "Mã BHYT", 150),
    ("tinh", "Tỉnh/Thành", 100),
]

TIM_THEO = {"Họ tên": "ho_ten", "Mã": "ma", "SĐT": "sdt", "Mã BHYT": "bhyt"}

DANH_SACH_TINH = ["Hà Nội", "Đà Nẵng", "TP.HCM", "Hải Phòng", "Cần Thơ"]
DANH_SACH_GIOI_TINH = ["Nam", "Nữ", "Khác"]

# Dữ liệu giả
DU_LIEU_GIA = [
    ("BN001", "Nguyễn Văn An", "12/03/1990", "0912345678", "HN4010123456789", "Hà Nội", "Nam", "an.nguyen@mail.com"),
    ("BN002", "Trần Thị Bình", "25/07/1985", "0987654321", "DN4010987654321", "Đà Nẵng", "Nữ", "binh.tran@mail.com"),
    ("BN003", "Lê Minh Châu", "03/11/2001", "0901122334", "HC4011122233344", "TP.HCM", "Nữ", "chau.le@mail.com"),
    ("BN004", "Phạm Quốc Dũng", "18/05/1978", "0934455667", "HP4015566778899", "Hải Phòng", "Nam", "dung.pham@mail.com"),
    ("BN005", "Hoàng Thu Hà", "30/09/1995", "0977788990", "CT4017788990011", "Cần Thơ", "Nữ", "ha.hoang@mail.com"),
    ("BN006", "Vũ Đức Huy", "09/02/1969", "0966677889", "HN4016677889900", "Hà Nội", "Nam", "huy.vu@mail.com"),
    ("BN007", "Đặng Mỹ Linh", "21/12/2003", "0955566778", "DN4015566778800", "Đà Nẵng", "Nữ", "linh.dang@mail.com"),
    ("BN008", "Bùi Anh Khoa", "14/08/1999", "0944455667", "HC4014455667711", "TP.HCM", "Nam", "khoa.bui@mail.com"),
]
KHOA_DU_LIEU = ("ma", "ho_ten", "ngay_sinh", "sdt", "bhyt", "tinh", "gioi_tinh", "email")


class TabBenhNhan(ttk.Frame):
    def __init__(self, parent, thong_bao=None, vai_tro="admin"):
        """thong_bao: hàm nhận 1 chuỗi để hiện lên thanh trạng thái (có thể bỏ trống).
        vai_tro: "admin" dùng đủ chức năng; "le_tan" chỉ được tìm kiếm và xem."""
        super().__init__(parent)
        self.thong_bao = thong_bao or (lambda _s: None)
        self.vai_tro = vai_tro
        self.cac_nut_sua_doi = []  # Thêm, Sửa, Xóa: le_tan không được dùng

        self.du_lieu = [dict(zip(KHOA_DU_LIEU, dong)) for dong in DU_LIEU_GIA]

        self.var_tu_khoa = tk.StringVar()
        self.var_ho_ten = tk.StringVar()
        self.var_gioi_tinh = tk.StringVar(value="Nam")
        self.var_sdt = tk.StringVar()
        self.var_bhyt = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_tinh = tk.StringVar()

        # Frame của tab chỉ dùng pack(); từng khối bên trong tự dùng một kiểu bố cục
        self._tao_thanh_tim_kiem()
        khung_chinh = ttk.Frame(self)
        khung_chinh.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        khung_chinh.columnconfigure(0, weight=1)  # bảng giãn theo cửa sổ
        khung_chinh.columnconfigure(1, weight=0)  # form giữ độ rộng cố định
        khung_chinh.rowconfigure(0, weight=1)
        self._tao_bang(khung_chinh).grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._tao_form(khung_chinh).grid(row=0, column=1, sticky="ns")

        self.hien_thi(self.du_lieu)
        self.ap_dung_phan_quyen()

    # ----------------------------------------------------- giao diện
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
        form = ttk.LabelFrame(cha, text="Thông tin bệnh nhân", padding=12)
        form.columnconfigure(0, weight=1)

        def nhan(text, row):
            ttk.Label(form, text=text).grid(row=row, column=0, sticky="w", pady=(6, 0))

        nhan("Họ tên", 0)
        ttk.Entry(form, textvariable=self.var_ho_ten, width=34).grid(row=1, column=0, sticky="ew")

        nhan("Ngày sinh (năm / tháng / ngày)", 2)
        self.chon_ngay_sinh = DatePicker(form)
        self.chon_ngay_sinh.grid(row=3, column=0, sticky="ew")

        nhan("Giới tính", 4)
        khung_gt = ttk.Frame(form)
        khung_gt.grid(row=5, column=0, sticky="w")
        for i, gt in enumerate(DANH_SACH_GIOI_TINH):
            ttk.Radiobutton(khung_gt, text=gt, value=gt, variable=self.var_gioi_tinh).pack(
                side="left", padx=(0 if i == 0 else 12, 0))

        nhan("Số điện thoại", 6)
        ttk.Entry(form, textvariable=self.var_sdt).grid(row=7, column=0, sticky="ew")
        nhan("Mã BHYT", 8)
        ttk.Entry(form, textvariable=self.var_bhyt).grid(row=9, column=0, sticky="ew")
        nhan("Email", 10)
        ttk.Entry(form, textvariable=self.var_email).grid(row=11, column=0, sticky="ew")

        nhan("Tỉnh/Thành", 12)
        ttk.Combobox(form, textvariable=self.var_tinh, values=DANH_SACH_TINH,
                     state="readonly").grid(row=13, column=0, sticky="ew")
        nhan("Phường/Xã", 14)
        cb_xa = ttk.Combobox(form, state="disabled")
        cb_xa.set("Chọn phường/xã")
        cb_xa.grid(row=15, column=0, sticky="ew")

        khung_nut = ttk.Frame(form)
        khung_nut.grid(row=16, column=0, sticky="ew", pady=(18, 0))
        for i, (chu, lenh) in enumerate([("Thêm", self.them), ("Sửa", self.sua),
                                         ("Xóa", self.xoa), ("Làm mới", self.lam_moi_form)]):
            khung_nut.columnconfigure(i, weight=1, uniform="nut")
            nut = ttk.Button(khung_nut, text=chu, command=lenh)
            nut.grid(row=0, column=i, sticky="ew", padx=2)
            if chu in ("Thêm", "Sửa", "Xóa"):
                self.cac_nut_sua_doi.append(nut)
        return form

    def ap_dung_phan_quyen(self):
        """Khóa các nút Thêm/Sửa/Xóa nếu không phải admin."""
        if self.vai_tro != "admin":
            for nut in self.cac_nut_sua_doi:
                nut.state(["disabled"])

    # ----------------------------------------------------------- hiển thị
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
        self.var_sdt.set(b["sdt"])
        self.var_bhyt.set(b["bhyt"])
        self.var_email.set(b["email"])
        self.var_tinh.set(b["tinh"])

    # --------------------------------------------------------------------- hỗ trợ
    def _ma_dang_chon(self):
        chon = self.tree.selection()
        return chon[0] if chon else None

    def _tim_theo_ma(self, ma):
        return next((b for b in self.du_lieu if b["ma"] == ma), None)

    def _ma_moi(self):
        so_lon_nhat = max((int(b["ma"][2:]) for b in self.du_lieu), default=0)
        return f"BN{so_lon_nhat + 1:03d}"

    def _doc_form(self):
        """Đọc form, kiểm tra tối thiểu. Trả về dict hoặc None nếu có lỗi.
        (Kiểm tra kỹ hơn bằng Regex là việc của A: validators.)"""
        ho_ten = self.var_ho_ten.get().strip()
        ngay_sinh = self.chon_ngay_sinh.get()
        if not ho_ten:
            messagebox.showwarning(config.TIEU_DE_APP, "Vui lòng nhập họ tên.", parent=self)
            return None
        if not ngay_sinh:
            messagebox.showwarning(config.TIEU_DE_APP,
                                   "Vui lòng chọn đủ ngày sinh (năm, tháng, ngày).", parent=self)
            return None
        return {
            "ho_ten": ho_ten,
            "ngay_sinh": ngay_sinh,
            "gioi_tinh": self.var_gioi_tinh.get(),
            "sdt": self.var_sdt.get().strip(),
            "bhyt": self.var_bhyt.get().strip(),
            "email": self.var_email.get().strip(),
            "tinh": self.var_tinh.get(),
        }

    # ----------------------------------------------------------------------------------- chức năng
    def tim(self):
        """Tìm không cần chính xác: không phân biệt hoa/thường và dấu tiếng Việt.
        Họ tên: mỗi từ khóa là phần đầu của một từ trong tên ('an', 'van an', 'nguyen van an').
        Mã / SĐT / Mã BHYT: từ khóa nằm ở bất kỳ đâu."""
        khoa = TIM_THEO[self.cb_tim_theo.get()]
        tu_khoa = self.var_tu_khoa.get()
        ket_qua = [b for b in self.du_lieu if helpers.khop(khoa, b[khoa], tu_khoa)]
        self.hien_thi(ket_qua)
        self.thong_bao(f"Tìm thấy {len(ket_qua)} bệnh nhân")

    def lam_moi_danh_sach(self):
        self.var_tu_khoa.set("")
        self.hien_thi(self.du_lieu)
        self.thong_bao("Đã làm mới danh sách")

    def lam_moi_form(self):
        self.tree.selection_remove(self.tree.selection())
        for bien in (self.var_ho_ten, self.var_sdt, self.var_bhyt, self.var_email, self.var_tinh):
            bien.set("")
        self.chon_ngay_sinh.clear()
        self.var_gioi_tinh.set("Nam")

    def them(self):
        du_lieu_form = self._doc_form()
        if not du_lieu_form:
            return
        du_lieu_form["ma"] = self._ma_moi()
        self.du_lieu.append(du_lieu_form)
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
        self._tim_theo_ma(ma).update(du_lieu_form)
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
        self.du_lieu.remove(b)
        self.hien_thi(self.du_lieu)
        self.lam_moi_form()
        self.thong_bao(f"Đã xóa bệnh nhân {ma}")
