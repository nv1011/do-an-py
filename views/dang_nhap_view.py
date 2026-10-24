"""Màn hình đăng nhập."""
import tkinter as tk
from tkinter import ttk

import config
from views import helpers
from views import tai_khoan_gia
from views.tai_khoan_dialog import DialogTaoTaiKhoan


class DangNhapView(tk.Tk):
    def __init__(self, xac_thuc=tai_khoan_gia.xac_thuc, khi_thanh_cong=None,
                 tao_tai_khoan=tai_khoan_gia.tao_tai_khoan):
        super().__init__()
        self.xac_thuc = xac_thuc
        self.tao_tai_khoan = tao_tai_khoan
        self.khi_thanh_cong = khi_thanh_cong

        self.title(f"{config.TIEU_DE_APP} - Đăng nhập")
        t = helpers.ty_le_man_hinh(self)
        self.geometry(helpers.kich_thuoc(self, config.KICH_THUOC_DANG_NHAP))
        self.minsize(int(520 * t), int(520 * t))
        self.configure(bg=config.MAU_NEN)
        self.option_add("*Font", config.FONT_CHUNG)

        self.var_ten = tk.StringVar()
        self.var_mat_khau = tk.StringVar()
        self.var_loi = tk.StringVar()

        self._tao_giao_dien()

        self.ent_ten.focus_set()
        self.bind("<Return>", lambda _e: self.dang_nhap())
        self.protocol("WM_DELETE_WINDOW", self.thoat)

    def _tao_giao_dien(self):
        the = tk.Frame(self, bg="white", highlightbackground=config.MAU_VIEN, highlightthickness=1)
        the.place(relx=0.5, rely=0.5, anchor="center", width=int(380 * helpers.ty_le_man_hinh(self)),
                  height=int(480 * helpers.ty_le_man_hinh(self)))

        logo = tk.Frame(the, bg="#eeeeee", width=80, height=80,
                        highlightbackground="#bbbbbb", highlightthickness=1)
        logo.pack(pady=(24, 10))
        logo.pack_propagate(False)
        tk.Label(logo, text="Logo", bg="#eeeeee", fg=config.MAU_CHU_MO).pack(expand=True)

        tk.Label(the, text="QUẢN LÝ PHÒNG KHÁM", bg="white",
                 font=config.FONT_TIEU_DE).pack()
        tk.Label(the, text="Đăng nhập để tiếp tục", bg="white", fg=config.MAU_CHU_MO).pack(pady=(2, 14))

        tk.Label(the, text="Tên đăng nhập", bg="white", anchor="w").pack(fill="x", padx=32)
        self.ent_ten = ttk.Entry(the, textvariable=self.var_ten)
        self.ent_ten.pack(fill="x", padx=32, pady=(2, 10), ipady=3)

        tk.Label(the, text="Mật khẩu", bg="white", anchor="w").pack(fill="x", padx=32)
        self.ent_mat_khau = ttk.Entry(the, textvariable=self.var_mat_khau, show="•")
        self.ent_mat_khau.pack(fill="x", padx=32, pady=(2, 6), ipady=3)

        tk.Label(the, textvariable=self.var_loi, bg="white", fg=config.MAU_LOI,
                 anchor="w", height=1).pack(fill="x", padx=32, pady=(0, 8))

        khung_nut = tk.Frame(the, bg="white")
        khung_nut.pack(fill="x", padx=32)
        khung_nut.columnconfigure(0, weight=1, uniform="nut")
        khung_nut.columnconfigure(1, weight=1, uniform="nut")
        tk.Button(khung_nut, text="Đăng nhập", font=config.FONT_DAM,
                  bg=config.MAU_NHAN_MANH, command=self.dang_nhap).grid(
            row=0, column=0, sticky="ew", padx=(0, 6), ipady=4)
        tk.Button(khung_nut, text="Thoát", bg="#e0e0e0", command=self.thoat).grid(
            row=0, column=1, sticky="ew", padx=(6, 0), ipady=4)
        tk.Button(the, text="Chưa có tài khoản? Tạo tài khoản", bg="white", fg=config.MAU_VIEN_CHON,
                  relief="flat", cursor="hand2", command=self.tao_tai_khoan_moi).pack(pady=(12, 0))

    def dang_nhap(self):
        ten = self.var_ten.get().strip()
        mat_khau = self.var_mat_khau.get()

        if not ten or not mat_khau:
            self.var_loi.set("Vui lòng nhập tên đăng nhập và mật khẩu")
            return

        vai_tro = self.xac_thuc(ten, mat_khau)
        if vai_tro is None:
            self.var_loi.set("Sai tên đăng nhập hoặc mật khẩu")
            self.var_mat_khau.set("")
            self.ent_mat_khau.focus_set()
            return

        self.var_loi.set("")
        self.ket_qua = (ten, vai_tro)
        self.destroy()
        if self.khi_thanh_cong:
            self.khi_thanh_cong(ten, vai_tro)

    def tao_tai_khoan_moi(self):
        hop_thoai = DialogTaoTaiKhoan(self, self.tao_tai_khoan)
        self.wait_window(hop_thoai)
        if hop_thoai.ten_moi:
            self.var_ten.set(hop_thoai.ten_moi)
            self.var_mat_khau.set("")
            self.var_loi.set("")
            self.ent_mat_khau.focus_set()

    def thoat(self):
        self.destroy()


if __name__ == "__main__":
    DangNhapView().mainloop()
