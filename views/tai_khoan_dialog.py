"""Hộp thoại Tạo tài khoản và Đổi mật khẩu."""
import tkinter as tk
from tkinter import ttk, messagebox

import config


class _HopThoai(tk.Toplevel):
    """Khung chung của hai hộp thoại."""

    def __init__(self, cha, tieu_de):
        super().__init__(cha)
        self.cha = cha
        self.title(tieu_de)
        self.configure(bg=config.MAU_NEN)
        self.resizable(False, False)
        self.transient(cha)
        self.var_loi = tk.StringVar()
        self.khung = ttk.Frame(self, padding=18)
        self.khung.pack(fill="both", expand=True)
        self.khung.columnconfigure(0, weight=1)
        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", lambda _e: self.dong_y())

    def them_o(self, row, nhan, bien, an=True):
        """Thêm một nhãn và một ô nhập; an=True thì che ký tự (mật khẩu)."""
        ttk.Label(self.khung, text=nhan).grid(row=row * 2, column=0, sticky="w", pady=(6, 0))
        o = ttk.Entry(self.khung, textvariable=bien, width=34, show="•" if an else "")
        o.grid(row=row * 2 + 1, column=0, sticky="ew")
        return o

    def them_nut(self, row, chu_dong_y):
        ttk.Label(self.khung, textvariable=self.var_loi, foreground=config.MAU_LOI,
                  wraplength=300).grid(row=row * 2, column=0, sticky="w", pady=(8, 0))
        khung_nut = ttk.Frame(self.khung)
        khung_nut.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(8, 0))
        khung_nut.columnconfigure(0, weight=1, uniform="nut")
        khung_nut.columnconfigure(1, weight=1, uniform="nut")
        ttk.Button(khung_nut, text=chu_dong_y, command=self.dong_y).grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(khung_nut, text="Hủy", command=self.destroy).grid(
            row=0, column=1, sticky="ew", padx=(4, 0))

    def hien(self):
        self.update_idletasks()
        self.grab_set()
        self.focus_set()

    def dong_y(self):
        raise NotImplementedError


class DialogTaoTaiKhoan(_HopThoai):
    """Chỉ admin được tạo tài khoản (theo hợp đồng hàm)."""

    def __init__(self, cha, ql_tai_khoan, nguoi_thuc_hien):
        super().__init__(cha, "Tạo tài khoản")
        self.ql = ql_tai_khoan
        self.nguoi_thuc_hien = nguoi_thuc_hien
        self.var_ten = tk.StringVar()
        self.var_mk = tk.StringVar()
        self.var_nhap_lai = tk.StringVar()

        o_ten = self.them_o(0, "Tên đăng nhập (không dấu, không khoảng trắng)", self.var_ten, an=False)
        ttk.Label(self.khung, text="Vai trò").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.cb_vai_tro = ttk.Combobox(self.khung, values=config.DANH_SACH_VAI_TRO, state="readonly")
        self.cb_vai_tro.set(config.VAI_TRO_LE_TAN)
        self.cb_vai_tro.grid(row=3, column=0, sticky="ew")
        self.them_o(2, "Mật khẩu", self.var_mk)
        self.them_o(3, "Nhập lại mật khẩu", self.var_nhap_lai)
        self.them_nut(4, "Tạo tài khoản")
        self.hien()
        o_ten.focus_set()

    def dong_y(self):
        if self.var_mk.get() != self.var_nhap_lai.get():
            self.var_loi.set("Mật khẩu nhập lại không khớp.")
            return
        ok, thong_diep, _tk = self.ql.tao_tai_khoan(
            self.var_ten.get(), self.var_mk.get(), self.cb_vai_tro.get(), self.nguoi_thuc_hien)
        if not ok:
            self.var_loi.set(thong_diep)
            return
        messagebox.showinfo(config.TIEU_DE_APP, thong_diep, parent=self)
        self.destroy()


class DialogDoiMatKhau(_HopThoai):
    def __init__(self, cha, ten_dang_nhap, ql_tai_khoan):
        super().__init__(cha, "Đổi mật khẩu")
        self.ten_dang_nhap = ten_dang_nhap
        self.ql = ql_tai_khoan
        self.var_cu = tk.StringVar()
        self.var_moi = tk.StringVar()
        self.var_nhap_lai = tk.StringVar()

        ttk.Label(self.khung, text=f"Tài khoản: {ten_dang_nhap}").grid(
            row=0, column=0, sticky="w")
        o_cu = self.them_o(1, "Mật khẩu hiện tại", self.var_cu)
        self.them_o(2, "Mật khẩu mới", self.var_moi)
        self.them_o(3, "Nhập lại mật khẩu mới", self.var_nhap_lai)
        self.them_nut(4, "Đổi mật khẩu")
        self.hien()
        o_cu.focus_set()

    def dong_y(self):
        if self.var_moi.get() != self.var_nhap_lai.get():
            self.var_loi.set("Mật khẩu nhập lại không khớp.")
            return
        ok, thong_diep = self.ql.doi_mat_khau(
            self.ten_dang_nhap, self.var_cu.get(), self.var_moi.get())
        if not ok:
            self.var_loi.set(thong_diep)
            return
        messagebox.showinfo(config.TIEU_DE_APP, thong_diep, parent=self)
        self.destroy()
