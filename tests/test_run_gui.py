"""File chạy thử riêng cho phần giao diện

Luồng: màn hình đăng nhập -> đăng nhập đúng -> cửa sổ chính.
Bấm Hệ thống -> Đăng xuất thì quay lại màn hình đăng nhập; Thoát thì tắt hẳn.
Tài khoản thử: admin / admin123   hoặc   letan / letan123
"""
from views.dang_nhap_view import DangNhapView
from views.main_window import MainWindow


def chay():
    while True:
        ket_qua = {}

        def khi_thanh_cong(ten, vai_tro):
            ket_qua["ten"] = ten
            ket_qua["vai_tro"] = vai_tro

        DangNhapView(khi_thanh_cong=khi_thanh_cong).mainloop()
        if not ket_qua:  # bấm Thoát ở màn hình đăng nhập
            break

        cua_so = MainWindow(ket_qua["ten"], ket_qua["vai_tro"])
        cua_so.mainloop()
        if cua_so.ket_thuc != "dang_xuat":
            break


if __name__ == "__main__":
    chay()
