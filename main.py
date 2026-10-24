"""Chạy ứng dụng: đăng nhập -> cửa sổ chính."""
from services.quan_ly_bac_si import QuanLyBacSi
from services.quan_ly_benh_nhan import QuanLyBenhNhan
from services.quan_ly_lich_hen import QuanLyLichHen
from services.quan_ly_tai_khoan import QuanLyTaiKhoan
from views.dang_nhap_view import DangNhapView
from views.main_window import MainWindow


def main():
    ql_benh_nhan = QuanLyBenhNhan()
    ql_bac_si = QuanLyBacSi()
    ql_lich_hen = QuanLyLichHen(quan_ly_bac_si=ql_bac_si)
    ql_tai_khoan = QuanLyTaiKhoan()

    while True:
        ket_qua = {}
        DangNhapView(
            xac_thuc=ql_tai_khoan.xac_thuc,
            khi_thanh_cong=lambda ten, vai_tro: ket_qua.update(ten=ten, vai_tro=vai_tro),
        ).mainloop()
        if not ket_qua:         # đóng cửa sổ đăng nhập
            break

        cua_so = MainWindow(ket_qua["ten"], ket_qua["vai_tro"], ql_benh_nhan=ql_benh_nhan,
                            ql_bac_si=ql_bac_si, ql_lich_hen=ql_lich_hen, ql_tai_khoan=ql_tai_khoan)
        cua_so.mainloop()
        if cua_so.ket_thuc != "dang_xuat":
            break


if __name__ == "__main__":
    main()
