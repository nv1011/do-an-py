"""Tab Bệnh nhân: tìm kiếm, bảng và form thông tin (nối QuanLyBenhNhan của A)."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import config
from services.quan_ly_benh_nhan import QuanLyBenhNhan
from utils.validators import la_sdt_hop_le, la_ma_bhyt_hop_le, la_email_hop_le
from views.dia_chi import DiaChi
from views.widgets.date_picker import DatePicker

# (khóa trong to_dict, tiêu đề cột, độ rộng)
CAC_COT = [
    ("ma_dinh_danh", "Mã", 125),
    ("ho_ten", "Họ tên", 160),
    ("ngay_sinh", "Ngày sinh", 90),
    ("sdt", "SĐT", 95),
    ("so_bhyt", "Mã BHYT", 140),
    ("tinh_thanh", "Tỉnh/Thành", 95),
]

TIM_THEO = {"Họ tên": "ho_ten", "Mã": "ma", "SĐT": "sdt", "Mã BHYT": "bhyt"}

DANH_SACH_GIOI_TINH = ["Nam", "Nữ", "Khác"]
DANH_SACH_NHOM_MAU = ["A", "B", "AB", "O", "Chưa rõ"]
CHO_TINH, CHO_XA = "Chọn tỉnh/thành", "Chọn phường/xã"


def dinh_dang_ngay(chuoi_iso):
    """'1990-03-12' -> '12/03/1990'."""
    return date.fromisoformat(chuoi_iso).strftime("%d/%m/%Y")


class TabBenhNhan(ttk.Frame):
    def __init__(self, parent, thong_bao=None, vai_tro="admin", quan_ly=None, dia_chi=None):
        super().__init__(parent)
        self.thong_bao = thong_bao or (lambda _s: None)
        self.vai_tro = vai_tro
        self.ql = quan_ly or QuanLyBenhNhan()
        self.dia_chi = dia_chi or DiaChi()
        self.cac_nut_chi_admin = []

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

        self.hien_thi(self.ql.lay_tat_ca())
        self.ap_dung_phan_quyen()
        self.after(200, self._nap_tinh)     # mở cửa sổ xong mới nạp danh sách

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
        self.cb_tinh = ttk.Combobox(form, state="readonly", width=16)
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
            if chu in ("Sửa", "Xóa"):
                self.cac_nut_chi_admin.append(nut)

        self._xoa_form()
        return form

    def ap_dung_phan_quyen(self):
        """Lễ tân được thêm bệnh nhân; chỉ admin được sửa, xóa."""
        if self.vai_tro != "admin":
            for nut in self.cac_nut_chi_admin:
                nut.state(["disabled"])

    # ------------------------------------------------------------ tỉnh / phường xã
    def _nap_tinh(self):
        self.cb_tinh["values"] = self.dia_chi.lay_danh_sach_tinh()
        if self.dia_chi.dung_mau:
            self.thong_bao(f"Đang dùng danh sách tỉnh mẫu ({self.dia_chi.loi})")

    def _khi_chon_tinh(self):
        """Đổi tỉnh thì danh sách phường/xã đổi theo và phải chọn lại phường/xã."""
        self._cap_nhat_xa(self.cb_tinh.get())
        self.cb_xa.set(CHO_XA)

    def _cap_nhat_xa(self, tinh, them=None):
        """Nạp phường/xã của tỉnh; 'them' là giá trị đã lưu nhưng chưa có trong danh sách."""
        ds = self.dia_chi.lay_danh_sach_xa(tinh) if tinh else []
        if them and them not in ds:
            ds.append(them)
        self.cb_xa["values"] = ds

    # ------------------------------------------------------------ hiển thị
    def hien_thi(self, danh_sach):
        self.tree.delete(*self.tree.get_children())
        for bn in danh_sach:
            d = bn.to_dict()
            d["ngay_sinh"] = dinh_dang_ngay(d["ngay_sinh"])
            self.tree.insert("", "end", iid=d["ma_dinh_danh"],
                             values=tuple(d[khoa] for khoa, _t, _r in CAC_COT))

    def _khi_chon_dong(self, _event):
        ma = self._ma_dang_chon()
        bn = self.ql.tim_theo_ma(ma) if ma else None
        if not bn:
            return
        d = bn.to_dict()
        self.var_ho_ten.set(d["ho_ten"])
        self.chon_ngay_sinh.set(dinh_dang_ngay(d["ngay_sinh"]))
        self.var_gioi_tinh.set(d["gioi_tinh"])
        self.cb_nhom_mau.set(d["nhom_mau"])
        self.var_sdt.set(d["sdt"])
        self.var_bhyt.set("" if d["so_bhyt"] == "Không có" else d["so_bhyt"])
        self.var_email.set(d["email"])
        self.var_dia_chi.set(d["dia_chi"])
        if d["tinh_thanh"] not in self.cb_tinh["values"]:
            self.cb_tinh["values"] = list(self.cb_tinh["values"]) + [d["tinh_thanh"]]
        self.cb_tinh.set(d["tinh_thanh"])
        self._cap_nhat_xa(d["tinh_thanh"], d["xa_phuong"])
        self.cb_xa.set(d["xa_phuong"])
        self.var_tien_su.set("" if d["tien_su_benh"] == "Không có" else d["tien_su_benh"])

    # ------------------------------------------------------------ hỗ trợ
    def _ma_dang_chon(self):
        chon = self.tree.selection()
        return chon[0] if chon else None

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
        """Kiểm tra nhanh trên form (dùng validators của A); trả về dict hoặc None nếu lỗi."""
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
        tinh, xa = self.cb_tinh.get(), self.cb_xa.get()

        if not ho_ten:
            return loi("Họ tên không được để trống.")
        if not ngay_sinh:
            return loi("Vui lòng chọn đủ ngày sinh (năm, tháng, ngày).")
        if not gioi_tinh:
            return loi("Vui lòng chọn giới tính.")
        if not la_sdt_hop_le(sdt):
            return loi("Số điện thoại phải gồm 10 chữ số và bắt đầu bằng số 0.")
        if bhyt and not la_ma_bhyt_hop_le(bhyt):
            return loi("Mã BHYT phải gồm đúng 13 chữ số (hoặc để trống).")
        if email and not la_email_hop_le(email):
            return loi("Email không hợp lệ.")
        if not dia_chi:
            return loi("Vui lòng nhập địa chỉ (số nhà, tên đường).")
        if tinh in ("", CHO_TINH):
            return loi("Vui lòng chọn Tỉnh/Thành.")
        if xa in ("", CHO_XA):
            return loi("Vui lòng chọn Phường/Xã.")

        return {
            "ho_ten": ho_ten,
            "ngay_sinh": ngay_sinh.replace("/", "-"),   # hợp đồng hàm: DD-MM-YYYY
            "gioi_tinh": gioi_tinh,
            "nhom_mau": self.cb_nhom_mau.get(),
            "sdt": sdt,
            "so_bhyt": bhyt,
            "email": email,
            "dia_chi": dia_chi,
            "tinh_thanh": tinh,
            "xa_phuong": xa,
            "tien_su_benh": self.var_tien_su.get().strip(),
        }

    def _bao_ket_qua(self, thanh_cong, thong_diep):
        """Hiện kết quả trả về từ lớp quản lý của A."""
        if thanh_cong:
            messagebox.showinfo(config.TIEU_DE_APP, thong_diep, parent=self)
            self.thong_bao(thong_diep)
        else:
            messagebox.showerror(config.TIEU_DE_APP, thong_diep, parent=self)
        return thanh_cong

    # ------------------------------------------------------------ chức năng
    def tim(self):
        """Tìm không cần chính xác (không phân biệt hoa/thường và dấu), do QuanLyBenhNhan xử lý."""
        ket_qua = self.ql.tim_kiem(self.var_tu_khoa.get(), TIM_THEO[self.cb_tim_theo.get()])
        self.hien_thi(ket_qua)
        self.thong_bao(f"Tìm thấy {len(ket_qua)} bệnh nhân")

    def lam_moi_danh_sach(self):
        self.var_tu_khoa.set("")
        self.hien_thi(self.ql.lay_tat_ca())
        self.thong_bao("Đã làm mới danh sách")

    def lam_moi_form(self):
        self.tree.selection_remove(self.tree.selection())
        self._xoa_form()

    def them(self):
        du_lieu = self._doc_form()
        if not du_lieu:
            return
        thanh_cong, thong_diep, _bn = self.ql.them(du_lieu)
        if self._bao_ket_qua(thanh_cong, thong_diep):
            self.var_tu_khoa.set("")
            self.hien_thi(self.ql.lay_tat_ca())
            self.lam_moi_form()

    def sua(self):
        ma = self._ma_dang_chon()
        if not ma:
            messagebox.showinfo(config.TIEU_DE_APP, "Hãy chọn một bệnh nhân trong bảng trước.", parent=self)
            return
        du_lieu = self._doc_form()
        if not du_lieu:
            return
        thanh_cong, thong_diep = self.ql.sua(ma, du_lieu)
        if self._bao_ket_qua(thanh_cong, thong_diep):
            self.hien_thi(self.ql.lay_tat_ca())
            self.tree.selection_set(ma)

    def xoa(self):
        ma = self._ma_dang_chon()
        bn = self.ql.tim_theo_ma(ma) if ma else None
        if not bn:
            messagebox.showinfo(config.TIEU_DE_APP, "Hãy chọn một bệnh nhân trong bảng trước.", parent=self)
            return
        if not messagebox.askyesno(config.TIEU_DE_APP,
                                   f"Xóa bệnh nhân {ma} - {bn.ho_ten}?", parent=self):
            return
        thanh_cong, thong_diep = self.ql.xoa(ma)
        if self._bao_ket_qua(thanh_cong, thong_diep):
            self.hien_thi(self.ql.lay_tat_ca())
            self.lam_moi_form()
