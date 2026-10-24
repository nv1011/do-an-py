"""Chạy thử giao diện: đăng nhập -> cửa sổ chính."""
from views.dang_nhap_view import DangNhapView
from views.main_window import MainWindow


def chay():
    while True:
        ket_qua = {}

        def khi_thanh_cong(ten, vai_tro):
            ket_qua["ten"] = ten
            ket_qua["vai_tro"] = vai_tro

        DangNhapView(khi_thanh_cong=khi_thanh_cong).mainloop()
        if not ket_qua:
            break

        cua_so = MainWindow(ket_qua["ten"], ket_qua["vai_tro"])
        cua_so.mainloop()
        if cua_so.ket_thuc != "dang_xuat":
            break


if __name__ == "__main__":
    chay()
