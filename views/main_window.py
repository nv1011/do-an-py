"""Cửa sổ chính: Menu + Notebook + thanh trạng thái."""
import tkinter as tk
from tkinter import ttk, messagebox

import config
from views.tab_benh_nhan import TabBenhNhan
from views.tai_khoan_dialog import DialogDoiMatKhau
from views.tab_lich_hen import TabLichHen
from views.tab_phieu_kham import TabPhieuKham


class MainWindow(tk.Tk):
    def __init__(self, ten_dang_nhap="admin", vai_tro="admin"):
        super().__init__()
        self.ten_dang_nhap = ten_dang_nhap
        self.vai_tro = vai_tro
        self.ket_thuc = "thoat"

        self.title(config.TIEU_DE_APP)
        self.geometry(config.KICH_THUOC_CUA_SO)
        self.minsize(*config.KICH_THUOC_TOI_THIEU)
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

        menu_bao_cao = tk.Menu(thanh_menu, tearoff=0)
        menu_bao_cao.add_command(label="Xuất báo cáo", command=self._chua_co)
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
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=ten)
            self.tabs[ten] = frame

        TabBenhNhan(self.tabs["Bệnh nhân"], thong_bao=self.trang_thai.set,
                   vai_tro=self.vai_tro).pack(fill="both", expand=True)

        TabLichHen(self.tabs["Lịch hẹn"], thong_bao=self.trang_thai.set,
                   vai_tro=self.vai_tro).pack(fill="both", expand=True)

        TabPhieuKham(self.tabs["Phiếu khám"], thong_bao=self.trang_thai.set,
                     vai_tro=self.vai_tro).pack(fill="both", expand=True)

        ttk.Label(self.tabs["Thống kê"], text="Tab Thống kê (đang phát triển)").pack(expand=True)

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
