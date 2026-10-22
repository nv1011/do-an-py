"""Thử nghiệm thủ công và kiểm thử QuanLyBenhNhan.

Chạy từ terminal gốc dự án:
    py -m tests.test_quan_ly_benh_nhan
"""
from datetime import date
from services.json_store import JsonStore
from services.quan_ly_benh_nhan import QuanLyBenhNhan
import tempfile
from pathlib import Path


def chay_thu_nghiem():
    print("=" * 60)
    print("BẮT ĐẦU CHẠY THỬ NGHIỆM THỦ CÔNG: QUẢN LÝ BỆNH NHÂN")
    print("=" * 60)

    # 1. Khởi tạo và nạp dữ liệu thật từ data/benh_nhan.json
    ql = QuanLyBenhNhan()
    danh_sach = ql.lay_tat_ca()
    print(f"\n1. Đọc dữ liệu ban đầu:")
    print(f"   -> Đã nạp thành công {len(danh_sach)} bệnh nhân từ data/benh_nhan.json.")

    # 2. Thử nghiệm tìm kiếm không dấu theo tiêu chí HỌ TÊN
    print(f"\n2. Thử tìm kiếm theo HỌ TÊN (tiêu chí 1):")
    ket_qua_ten = ql.tim_kiem("van an", tieu_chi="ho_ten")
    print(f"   -> Tìm 'van an': {len(ket_qua_ten)} kết quả:")
    for bn in ket_qua_ten:
        print(f"      + [{bn.ma_dinh_danh}] {bn.ho_ten} | SĐT: {bn.sdt} | BHYT: {bn.so_bhyt}")

    # 3. Thử nghiệm tìm kiếm theo SỐ BHYT
    print(f"\n3. Thử tìm kiếm theo SỐ BHYT (tiêu chí 2):")
    ket_qua_bhyt = ql.tim_kiem("4010987654321", tieu_chi="bhyt")
    print(f"   -> Tìm BHYT '4010987654321': {len(ket_qua_bhyt)} kết quả:")
    for bn in ket_qua_bhyt:
        print(f"      + [{bn.ma_dinh_danh}] {bn.ho_ten} | BHYT: {bn.so_bhyt}")

    # 4. Thử nghiệm tìm kiếm KẾT HỢP ĐA TIÊU CHÍ (Họ tên + BHYT)
    print(f"\n4. Thử tìm kiếm KẾT HỢP ĐỒNG THỜI (Họ tên + BHYT):")
    ket_qua_ket_hop = ql.tim_kiem(ho_ten="Nguyen", so_bhyt="4010")
    print(f"   -> Tìm họ tên có 'Nguyen' VÀ BHYT chứa '4010': {len(ket_qua_ket_hop)} kết quả:")
    for bn in ket_qua_ket_hop:
        print(f"      + [{bn.ma_dinh_danh}] {bn.ho_ten} | BHYT: {bn.so_bhyt}")

    # 5. Thử nghiệm thêm bệnh nhân mới với chuẩn ngày DD-MM-YYYY
    print(f"\n5. Thử THÊM BỆNH NHÂN MỚI (chuẩn ngày Việt Nam DD-MM-YYYY):")
    du_lieu_moi = {
        "ho_ten": "Hoàng Minh Tuấn",
        "dia_chi": "99 Lê Duẩn",
        "tinh_thanh": "Đà Nẵng",
        "xa_phuong": "Phường Thạch Thang",
        "gioi_tinh": "Nam",
        "ngay_sinh": "25-12-1998",        # Chuỗi ngày chuẩn DD-MM-YYYY
        "sdt": "0911223344",
        "so_bhyt": "4019988776655",       # 13 số
        "tien_su_benh": "Không có",
        "nhom_mau": "O",
        "email": "tuan.hoang@gmail.com"
    }
    
    # Dùng store ảo trong thư mục tạm để không làm bẩn file data thật
    with tempfile.TemporaryDirectory() as tmp:
        store_tam = JsonStore(thu_muc_data=tmp)
        ql_tam = QuanLyBenhNhan(json_store=store_tam, ten_file="test_bn.json")
        
        ok, msg, bn_moi = ql_tam.them(du_lieu_moi)
        print(f"   -> Kết quả: {ok} | {msg}")
        if ok:
            print(f"      + Mã sinh tự động: {bn_moi.ma_dinh_danh}")
            print(f"      + Tuổi tính tự động: {bn_moi.tuoi} tuổi")
            print(f"      + Ngày đăng ký trích xuất: {bn_moi.ngay_dang_ky}")

        # 6. Thử nghiệm BẪY LỖI NGÀY KHÔNG TỒN TẠI (VD: 30/02/2027)
        print(f"\n6. Bẫy lỗi: Thử thêm ngày sinh 30/02/2027:")
        du_lieu_loi_ngay = dict(du_lieu_moi, ngay_sinh="30-02-2027", sdt="0988776655")
        ok_loi, msg_loi, _ = ql_tam.them(du_lieu_loi_ngay)
        print(f"   -> Kết quả chặn lỗi: {not ok_loi} | Thông điệp: '{msg_loi}'")

        # 7. Thử nghiệm BẪY LỖI TRÙNG SỐ ĐIỆN THOẠI
        print(f"\n7. Bẫy lỗi: Thử thêm bệnh nhân trùng SĐT '0911223344':")
        du_lieu_trung_sdt = dict(du_lieu_moi, ho_ten="Người Khác", sdt="0911223344")
        ok_sdt, msg_sdt, _ = ql_tam.them(du_lieu_trung_sdt)
        print(f"   -> Kết quả chặn lỗi: {not ok_sdt} | Thông điệp: '{msg_sdt}'")

        # 8. Thử nghiệm SỬA thông tin bệnh nhân
        print(f"\n8. Thử SỬA thông tin bệnh nhân:")
        ok_sua, msg_sua = ql_tam.sua(bn_moi.ma_dinh_danh, {
            "ho_ten": "Hoàng Minh Tuấn (Đã đổi tên)",
            "dia_chi": "100 Bạch Đằng"
        })
        print(f"   -> Kết quả sửa: {ok_sua} | {msg_sua}")
        bn_da_sua = ql_tam.tim_theo_ma(bn_moi.ma_dinh_danh)
        print(f"      + Tên sau sửa: {bn_da_sua.ho_ten} | Địa chỉ mới: {bn_da_sua.dia_chi_day_du}")

        # 9. Thử nghiệm XÓA bệnh nhân
        print(f"\n9. Thử XÓA bệnh nhân:")
        ok_xoa, msg_xoa = ql_tam.xoa(bn_moi.ma_dinh_danh)
        print(f"   -> Kết quả xóa: {ok_xoa} | {msg_xoa}")
        print(f"      + Số bệnh nhân còn lại trong danh sách: {len(ql_tam.lay_tat_ca())}")

    print("\n" + "=" * 60)
    print("HOÀN THÀNH TẤT CẢ CÁC BÀI THỬ NGHIỆM THỦ CÔNG -> TỐT!")
    print("=" * 60)


if __name__ == "__main__":
    chay_thu_nghiem()
