"""Cửa sổ chính: Menu + Notebook + thanh trạng thái."""
import tkinter as tk
from tkinter import ttk, messagebox

import config
from views import helpers
from services.quan_ly_benh_nhan import QuanLyBenhNhan
from views.tab_benh_nhan import TabBenhNhan
from views.tai_khoan_dialog import DialogDoiMatKhau
from views.tab_lich_hen import TabLichHen
from views.tab_phieu_kham import TabPhieuKham
from views.tab_thong_ke import TabThongKe
from views.du_lieu_gia import QuanLyPhieuKhamGia, QuanLyBacSiGia, QuanLyLichHenGia, ThongKeGia


class MainWindow(tk.Tk):
    def __init__(self, ten_dang_nhap="admin", vai_tro="admin"):
        super().__init__()
        self.ten_dang_nhap = ten_dang_nhap
        self.vai_tro = vai_tro
        self.ket_thuc = "thoat"

        self.title(config.TIEU_DE_APP)
        t = helpers.ty_le_man_hinh(self)
        self.geometry(helpers.kich_thuoc(self, config.KICH_THUOC_CUA_SO))
        self.minsize(*(int(x * t) for x in config.KICH_THUOC_TOI_THIEU))
        self.configure(bg=config.MAU_NEN)
        self.option_add("*Font", config.FONT_CHUNG)

        self.tabs = {}
        self.trang_thai = tk.StringVar(value=f"Đăng nhập: {ten_dang_nhap} ({vai_tro})")

        self._tao_menu()
        self._tao_thanh_trang_thai()
        self._tao_notebook()

        self.protocol("WM_DELETE_WINDOW", self.thoat)

    # ---------- Menu ----------
    def _tao_menu(self):
        thanh_menu = tk.Menu(self)

        menu_he_thong = tk.Menu(thanh_menu, tearoff=0)
        menu_he_thong.add_command(label="Đổi mật khẩu", command=self.doi_mat_khau)
        menu_he_thong.add_command(label="Đăng xuất", command=self.dang_xuat)
        menu_he_thong.add_separator()
        menu_he_thong.add_command(label="Thoát", command=self.thoat)
        thanh_menu.add_cascade(label="Hệ thống", menu=menu_he_thong)

        if self.vai_tro == "admin":
            menu_bao_cao = tk.Menu(thanh_menu, tearoff=0)
            menu_bao_cao.add_command(label="Xuất báo cáo", command=self._xuat_bao_cao)
            thanh_menu.add_cascade(label="Báo cáo", menu=menu_bao_cao)

        menu_tro_giup = tk.Menu(thanh_menu, tearoff=0)
        menu_tro_giup.add_command(label="Giới thiệu", command=self._gioi_thieu)
        thanh_menu.add_cascade(label="Trợ giúp", menu=menu_tro_giup)

        self.config(menu=thanh_menu)

    # ---------- Notebook ----------
    def _tao_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        for ten in config.DANH_SACH_TAB:
            if ten == "Thống kê" and self.vai_tro != "admin":
                continue   # lễ tân không xem thống kê
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=ten)
            self.tabs[ten] = frame

        self.ql_benh_nhan = QuanLyBenhNhan()
        TabBenhNhan(self.tabs["Bệnh nhân"], thong_bao=self.trang_thai.set,
                   vai_tro=self.vai_tro, quan_ly=self.ql_benh_nhan).pack(fill="both", expand=True)

        # NỐI A: thay các đối tượng giả bằng QuanLyBacSi, QuanLyPhieuKham, ThongKe thật
        self.ql_bac_si = QuanLyBacSiGia()
        TabLichHen(self.tabs["Lịch hẹn"], thong_bao=self.trang_thai.set, vai_tro=self.vai_tro,
                   ql_benh_nhan=self.ql_benh_nhan, ql_bac_si=self.ql_bac_si,
                   ql_lich_hen=QuanLyLichHenGia()).pack(fill="both", expand=True)
        self.ql_phieu = QuanLyPhieuKhamGia()
        self.tab_phieu_kham = TabPhieuKham(
            self.tabs["Phiếu khám"], thong_bao=self.trang_thai.set, vai_tro=self.vai_tro,
            quan_ly=self.ql_phieu, ql_benh_nhan=self.ql_benh_nhan, ql_bac_si=self.ql_bac_si)
        self.tab_phieu_kham.pack(fill="both", expand=True)

        self.tab_thong_ke = None
        if "Thống kê" in self.tabs:
            self.tab_thong_ke = TabThongKe(
                self.tabs["Thống kê"], thong_bao=self.trang_thai.set,
                thong_ke=ThongKeGia(self.ql_phieu, self.ql_bac_si))
            self.tab_thong_ke.pack(fill="both", expand=True)

        self.notebook.bind("<<NotebookTabChanged>>", self._khi_doi_tab)

    def _khi_doi_tab(self, _e=None):
        ten = self.notebook.tab(self.notebook.select(), "text")
        if ten == "Phiếu khám":
            self.tab_phieu_kham.lam_moi()
        elif ten == "Thống kê" and self.tab_thong_ke:
            self.tab_thong_ke.cap_nhat()

    def _xuat_bao_cao(self):
        if self.tab_thong_ke:
            self.tab_thong_ke.xuat_bao_cao()

    # ---------- Thanh trạng thái ----------
    def _tao_thanh_trang_thai(self):
        ttk.Label(
            self, textvariable=self.trang_thai, relief="sunken", anchor="w", padding=(8, 3)
        ).pack(side="bottom", fill="x")

    # ---------- Lệnh ----------
    def _chua_co(self):
        messagebox.showinfo(config.TIEU_DE_APP, "Chức năng này chưa có.", parent=self)

    def _gioi_thieu(self):
        messagebox.showinfo(
            config.TIEU_DE_APP, "Ứng dụng quản lý phòng khám nhỏ\nPython + Tkinter", parent=self
        )

    def doi_mat_khau(self):
        DialogDoiMatKhau(self, self.ten_dang_nhap)

    def dang_xuat(self):
        if messagebox.askyesno(config.TIEU_DE_APP, "Bạn có chắc muốn đăng xuất?", parent=self):
            self.ket_thuc = "dang_xuat"
            self.destroy()

    def thoat(self):
        if messagebox.askyesno(config.TIEU_DE_APP, "Bạn có chắc muốn thoát?", parent=self):
            self.ket_thuc = "thoat"
            self.destroy()
