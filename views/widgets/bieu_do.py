"""Biểu đồ vẽ bằng Canvas: cột, đường, tròn (donut). Dữ liệu: list các (nhãn, giá trị)."""
import math
import tkinter as tk

import config

MAU_NEN = config.MAU_BIEU_DO_NEN
MAU_CHU = config.MAU_BIEU_DO_CHU
MAU_CHU_PHU = config.MAU_BIEU_DO_CHU_PHU
MAU_LUOI = config.MAU_BIEU_DO_LUOI
MAU_DANH_MUC = config.MAU_BIEU_DO
FONT_NHO = ("Segoe UI", 8)
FONT_TIEU_DE = config.FONT_DAM


def _lam_tron_tren(gia_tri):
    """Trần "đẹp" cho trục: 1, 2, 5 x 10^n."""
    if gia_tri <= 0:
        return 1
    mu = 10 ** math.floor(math.log10(gia_tri))
    for he_so in (1, 2, 5, 10):
        if gia_tri <= he_so * mu:
            return he_so * mu
    return 10 * mu


def rut_gon(so):
    """1_500_000 -> '1,5tr'; 12_000 -> '12k'."""
    if abs(so) >= 1_000_000:
        return f"{so / 1_000_000:g}tr".replace(".", ",")
    if abs(so) >= 1_000:
        return f"{so / 1_000:g}k".replace(".", ",")
    return f"{so:g}"


class _BieuDo(tk.Canvas):
    def __init__(self, parent, tieu_de, dinh_dang=None, **kw):
        super().__init__(parent, bg=MAU_NEN, highlightthickness=1, highlightbackground=MAU_LUOI,
                         height=kw.pop("height", config.BIEU_DO_CAO), **kw)
        self.tieu_de = tieu_de
        self.dinh_dang = dinh_dang or (lambda v: f"{v:g}")
        self.du_lieu = []
        self.bind("<Configure>", lambda _e: self.ve())

    def dat_du_lieu(self, du_lieu):
        self.du_lieu = list(du_lieu)
        self.ve()

    def ve(self):
        self.delete("all")
        self.create_text(10, 10, text=self.tieu_de, anchor="nw", font=FONT_TIEU_DE, fill=MAU_CHU)
        if not self.du_lieu or not any(v for _n, v in self.du_lieu):
            r, c = self.winfo_width(), self.winfo_height()
            self.create_text(r / 2, c / 2, text="Chưa có dữ liệu", fill=MAU_CHU_PHU)
            return
        self._ve_noi_dung(self.winfo_width(), self.winfo_height())

    def _ve_truc(self, trai, tren, phai, duoi, tran):
        """Lưới ngang 4 mức + nhãn trục dọc; trả về hàm đổi giá trị -> y."""
        def y_cua(v):
            return duoi - (duoi - tren) * v / tran
        for i in range(5):
            v = tran * i / 4
            y = y_cua(v)
            self.create_line(trai, y, phai, y, fill=MAU_LUOI)
            self.create_text(trai - 6, y, text=rut_gon(v), anchor="e", font=FONT_NHO, fill=MAU_CHU_PHU)
        return y_cua

    def _ve_noi_dung(self, rong, cao):
        raise NotImplementedError


class BieuDoCot(_BieuDo):
    def _ve_noi_dung(self, rong, cao):
        trai, tren, phai, duoi = 52, 36, rong - 14, cao - 26
        tran = _lam_tron_tren(max(v for _n, v in self.du_lieu))
        y_cua = self._ve_truc(trai, tren, phai, duoi, tran)
        so_cot = len(self.du_lieu)
        o = (phai - trai) / so_cot
        rong_cot = max(4, min(o - 2, o * 0.6))
        cach_nhan = max(1, math.ceil(so_cot / 15))
        lon_nhat = max(v for _n, v in self.du_lieu)
        for i, (nhan, v) in enumerate(self.du_lieu):
            x = trai + o * i + o / 2
            if v:
                self.create_rectangle(x - rong_cot / 2, y_cua(v), x + rong_cot / 2, duoi,
                                      fill=MAU_DANH_MUC[0], outline="")
                if v == lon_nhat:
                    self.create_text(x, y_cua(v) - 4, text=self.dinh_dang(v), anchor="s",
                                     font=FONT_NHO, fill=MAU_CHU)
            if i % cach_nhan == 0:
                self.create_text(x, duoi + 4, text=str(nhan), anchor="n", font=FONT_NHO, fill=MAU_CHU_PHU)
        self.create_line(trai, duoi, phai, duoi, fill=MAU_CHU_PHU)


class BieuDoDuong(_BieuDo):
    def __init__(self, parent, tieu_de, dinh_dang=None, mau=MAU_DANH_MUC[1], **kw):
        super().__init__(parent, tieu_de, dinh_dang, **kw)
        self.mau = mau

    def _ve_noi_dung(self, rong, cao):
        trai, tren, phai, duoi = 52, 36, rong - 24, cao - 26
        tran = _lam_tron_tren(max(v for _n, v in self.du_lieu))
        y_cua = self._ve_truc(trai, tren, phai, duoi, tran)
        n = len(self.du_lieu)
        buoc = (phai - trai) / max(n - 1, 1)
        diem = [(trai + buoc * i if n > 1 else (trai + phai) / 2, y_cua(v))
                for i, (_nhan, v) in enumerate(self.du_lieu)]
        if n > 1:
            self.create_line(*[c for p in diem for c in p], fill=self.mau, width=2, smooth=False)
        lon_nhat = max(v for _n, v in self.du_lieu)
        cach_nhan = max(1, math.ceil(n / 15))
        for i, ((x, y), (nhan, v)) in enumerate(zip(diem, self.du_lieu)):
            self.create_oval(x - 4, y - 4, x + 4, y + 4, fill=self.mau, outline=MAU_NEN, width=2)
            if v == lon_nhat:
                self.create_text(x, y - 8, text=self.dinh_dang(v), anchor="s", font=FONT_NHO, fill=MAU_CHU)
            if i % cach_nhan == 0:
                self.create_text(x, duoi + 4, text=str(nhan), anchor="n", font=FONT_NHO, fill=MAU_CHU_PHU)
        self.create_line(trai, duoi, phai, duoi, fill=MAU_CHU_PHU)


class BieuDoTron(_BieuDo):
    """Donut + chú giải có giá trị và phần trăm (không dựa vào màu đơn thuần)."""

    def _ve_noi_dung(self, rong, cao):
        tong = sum(v for _n, v in self.du_lieu)
        bk = max(30, min(cao - 60, rong * 0.35) / 2)
        cx, cy = 20 + bk, 36 + (cao - 36) / 2 - 4
        # gom từ mục thứ 8 trở đi vào "Khác"
        muc = self.du_lieu[:7] + ([("Khác", sum(v for _n, v in self.du_lieu[7:]))]
                                  if len(self.du_lieu) > 8 else self.du_lieu[7:])
        goc = 90.0
        for i, (nhan, v) in enumerate(muc):
            if not v:
                continue
            quet = -360 * v / tong
            kieu = {"fill": MAU_DANH_MUC[i], "outline": MAU_NEN, "width": 2}
            if len(muc) == 1 or v == tong:
                self.create_oval(cx - bk, cy - bk, cx + bk, cy + bk, **kieu)
            else:
                self.create_arc(cx - bk, cy - bk, cx + bk, cy + bk, start=goc, extent=quet,
                                style="pieslice", **kieu)
            goc += quet
        lo = bk * 0.55
        self.create_oval(cx - lo, cy - lo, cx + lo, cy + lo, fill=MAU_NEN, outline=MAU_NEN)
        self.create_text(cx, cy - 8, text=f"{tong:g}", font=("Segoe UI", 14, "bold"), fill=MAU_CHU)
        self.create_text(cx, cy + 10, text="lượt khám", font=FONT_NHO, fill=MAU_CHU_PHU)
        x0, y = cx + bk + 24, 44
        for i, (nhan, v) in enumerate(muc):
            self.create_rectangle(x0, y, x0 + 10, y + 10, fill=MAU_DANH_MUC[i], outline="")
            self.create_text(x0 + 16, y + 5, text=f"{nhan}: {v:g} ({100 * v / tong:.0f}%)",
                             anchor="w", font=("Segoe UI", 9), fill=MAU_CHU)
            y += 20
