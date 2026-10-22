"""Thẻ lịch hẹn (AppointmentCard) dùng ở tab Lịch hẹn

"""
import tkinter as tk

import config

CHIEU_RONG_THE = 215
CHIEU_CAO_THE = 130
MAU_VIEN = "#444444"
MAU_VIEN_CHON = "#2e6bb0"


class AppointmentCard(tk.Frame):
    def __init__(self, parent, ma, gio_bat_dau, gio_ket_thuc, ten_benh_nhan,
                 ma_benh_nhan, ten_bac_si, thoi_luong, khi_chon=None):
        super().__init__(parent, bg="white", width=CHIEU_RONG_THE, height=CHIEU_CAO_THE,
                         highlightthickness=1, highlightbackground=MAU_VIEN)
        self.pack_propagate(False)   # giữ kích thước cố định để các thẻ đều nhau
        self.ma = ma
        self.khi_chon = khi_chon

        tk.Label(self, text=f"{gio_bat_dau} - {gio_ket_thuc}", bg=config.MAU_NHAN_MANH,
                 anchor="w", padx=10, pady=6, font=("Segoe UI", 10, "bold")).pack(fill="x")
        tk.Label(self, text=ten_benh_nhan, bg="white", anchor="w",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        for dong in (f"Mã BN: {ma_benh_nhan}", ten_bac_si, f"Thời lượng: {thoi_luong} phút"):
            tk.Label(self, text=dong, bg="white", fg="#555555", anchor="w").pack(
                anchor="w", padx=10)

        self._gan_su_kien(self)

    def _gan_su_kien(self, widget):
        """Bấm vào bất cứ chỗ nào trên thẻ (kể cả các nhãn con) đều tính là chọn thẻ."""
        widget.bind("<Button-1>", self._bam)
        for con in widget.winfo_children():
            self._gan_su_kien(con)

    def _bam(self, _event):
        if self.khi_chon:
            self.khi_chon(self.ma)

    def chon(self, duoc_chon):
        """Viền xanh đậm khi đang được chọn."""
        if duoc_chon:
            self.configure(highlightbackground=MAU_VIEN_CHON, highlightthickness=3)
        else:
            self.configure(highlightbackground=MAU_VIEN, highlightthickness=1)
