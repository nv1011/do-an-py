"""Kiểm thử thủ công và kiểm tra toàn diện PhieuKham & QuanLyPhieuKham.

Chạy từ terminal gốc dự án:
    py -m tests.test_quan_ly_phieu_kham
"""
import sys
from pathlib import Path

THU_MUC_GOC = Path(__file__).resolve().parent.parent
if str(THU_MUC_GOC) not in sys.path:
    sys.path.insert(0, str(THU_MUC_GOC))

import tempfile
from datetime import date
from services.json_store import JsonStore
from services.quan_ly_phieu_kham import QuanLyPhieuKham
from models.phieu_kham import PhieuKham


def chay_kiem_thu():
    print("=" * 65)
    print("BẮT ĐẦU KIỂM THỬ: PHIẾU KHÁM & QUẢN LÝ PHIẾU KHÁM")
    print("=" * 65)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        store = JsonStore(thu_muc_data=tmp_dir, thu_muc_backup=tmp_dir / "backup")

        # Chuẩn bị file dich_vu.json mẫu trong thư mục tạm
        file_dv = tmp_dir / "dich_vu.json"
        store.ghi_file(file_dv, [
            {"ma_dich_vu": "DV001", "ten_dich_vu": "Khám lâm sàng nội khoa", "don_gia": 150000},
            {"ma_dich_vu": "DV002", "ten_dich_vu": "Đo điện tim (ECG)", "don_gia": 120000},
            {"ma_dich_vu": "DV003", "ten_dich_vu": "Siêu âm bụng tổng quát", "don_gia": 200000},
        ])

        file_pk = tmp_dir / "phieu_kham.json"
        ql = QuanLyPhieuKham(json_store=store, ten_file=file_pk)

        # 1. Tạo phiếu khám mới
        print("\n1. Tạo phiếu khám ban đầu (Khám vãng lai):")
        ok, msg, pk1 = ql.tao_phieu_kham({
            "ma_benh_nhan": "12102026000002",
            "ma_bac_si": "010120001",
            "trieu_chung": "Đau đầu, chóng mặt",
        })
        assert ok, f"Tạo phiếu thất bại: {msg}"
        assert pk1.trang_thai_kham == "Dang_kham"
        assert pk1.trang_thai_thanh_toan == "Chua_thanh_toan"
        print(f"   -> [OK] {msg} (Mã: {pk1.ma_phieu_kham})")

        # 2. Thêm dịch vụ vào phiếu khám
        print("\n2. Thêm dịch vụ khám lâm sàng và cận lâm sàng:")
        ok_dv1, msg_dv1 = ql.them_dich_vu(pk1.ma_phieu_kham, "DV001", so_luong=1)
        assert ok_dv1
        ok_dv2, msg_dv2 = ql.them_dich_vu(pk1.ma_phieu_kham, "DV003", so_luong=1)
        assert ok_dv2
        # Kiểm tra tính tổng tiền: 150.000 + 200.000 = 350.000
        assert pk1.tong_tien == 350000.0
        print(f"   -> [OK] Đã thêm 2 dịch vụ, tổng tiền: {pk1.tong_tien:,.0f} đ")

        # 3. Thử thanh toán trước khi hoàn tất khám (Bắt buộc phải chặn)
        print("\n3. Kiểm tra ràng buộc: Không cho thanh toán khi đang khám:")
        ok_tt_fail, msg_tt_fail, _ = ql.thanh_toan(pk1.ma_phieu_kham)
        assert not ok_tt_fail
        print(f"   -> [OK] Đã chặn đúng: {msg_tt_fail}")

        # 4. Hoàn tất khám, kê đơn thuốc và hẹn tái khám
        print("\n4. Bác sĩ hoàn tất khám & Kê đơn thuốc:")
        ok_ht, msg_ht = ql.hoan_tat_kham(
            ma_pk=pk1.ma_phieu_kham,
            chan_doan="Rối loạn tiền đình",
            loi_dan="Uống thuốc đúng giờ, tránh thức khuya",
            don_thuoc=[
                {"ten_thuoc": "Betaserc 16mg", "don_vi": "Viên", "so_luong": 20, "cach_dung": "Sáng 1 viên, tối 1 viên"}
            ],
            ngay_tai_kham=date.today().strftime("%d-%m-%Y"),
            nguoi_thuc_hien={"vai_tro": "bac_si", "ma_bac_si": "010120001"}
        )
        assert ok_ht, f"Hoàn tất khám lỗi: {msg_ht}"
        assert pk1.trang_thai_kham == "Hoan_thanh"
        print(f"   -> [OK] {msg_ht}")

        # 5. Thanh toán viện phí
        print("\n5. Lễ tân thu tiền viện phí:")
        ok_tt, msg_tt, tien = ql.thanh_toan(pk1.ma_phieu_kham)
        assert ok_tt
        assert tien == 350000.0
        assert pk1.trang_thai_thanh_toan == "Da_thanh_toan"
        print(f"   -> [OK] {msg_tt} (Thu {tien:,.0f} đ)")

        # 6. Kiểm tra nạp lại từ file JSON (kiểm tra tính toàn vẹn dữ liệu)
        print("\n6. Đọc lại dữ liệu từ file JSON:")
        ql2 = QuanLyPhieuKham(json_store=store, ten_file=file_pk)
        pk_reloaded = ql2.tim_theo_ma(pk1.ma_phieu_kham)
        assert pk_reloaded is not None
        assert pk_reloaded.chan_doan == "Rối loạn tiền đình"
        assert pk_reloaded.trang_thai_kham == "Hoan_thanh"
        assert pk_reloaded.trang_thai_thanh_toan == "Da_thanh_toan"
        assert pk_reloaded.tong_tien == 350000.0
        print(f"   -> [OK] Tải lại dữ liệu hoàn toàn chính xác!")

    print("\n" + "=" * 65)
    print("TẤT CẢ CÁC BÀI TEST PHIẾU KHÁM ĐỀU THÀNH CÔNG RỰC RỠ!")
    print("=" * 65)


if __name__ == "__main__":
    chay_kiem_thu()
