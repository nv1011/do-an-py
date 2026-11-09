"""Kiểm thử thủ công các chức năng của QuanLyTaiKhoan (bao gồm vai trò Bác sĩ).

Chạy từ terminal gốc dự án:
    py -m tests.test_quan_ly_tai_khoan
"""
import sys
from pathlib import Path

THU_MUC_GOC = Path(__file__).resolve().parent.parent
if str(THU_MUC_GOC) not in sys.path:
    sys.path.insert(0, str(THU_MUC_GOC))

import tempfile
from services.json_store import JsonStore
from services.quan_ly_tai_khoan import QuanLyTaiKhoan
from config import VAI_TRO_BAC_SI, VAI_TRO_ADMIN, VAI_TRO_LE_TAN


def chay_kiem_thu():
    print("=" * 65)
    print("BẮT ĐẦU KIỂM THỬ QUẢN LÝ TÀI KHOẢN (VAI TRÒ BÁC SĨ & PHÂN QUYỀN)")
    print("=" * 65)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        file_json = tmp_dir / "tai_khoan_test.json"
        store = JsonStore(thu_muc_data=tmp_dir, thu_muc_backup=tmp_dir / "backup")

        ql = QuanLyTaiKhoan(json_store=store, ten_file=file_json)

        # 1. Tạo tài khoản admin khởi đầu
        print("\n1. Khởi tạo tài khoản ban đầu:")
        # Bỏ qua kiểm tra admin khi danh sách rỗng (hoặc mock admin)
        from models.tai_khoan import TaiKhoan
        admin_tk = TaiKhoan.tao_moi("admin", "Admin@123", VAI_TRO_ADMIN)
        ql._danh_sach.append(admin_tk)
        ql.luu_du_lieu()
        print("   -> Đã tạo tài khoản 'admin' mặc định.")

        # 2. Xác thực đăng nhập
        print("\n2. Kiểm tra xác thực đăng nhập:")
        vt_admin = ql.xac_thuc("admin", "Admin@123")
        assert vt_admin == VAI_TRO_ADMIN, f"Sai vai trò admin: {vt_admin}"
        assert ql.xac_thuc("admin", "SaiMatKhau") is None, "Mật khẩu sai vẫn đăng nhập được!"
        print("   -> Xác thực admin thành công: vai_tro =", vt_admin)

        # 3. Tạo tài khoản bác sĩ hợp lệ
        print("\n3. Tạo tài khoản cho Bác sĩ (yêu cầu ma_bac_si 9 số):")
        ok, msg, tk_bs = ql.tao_tai_khoan(
            ten="bs_mai",
            mat_khau="Doctor@123",
            vai_tro=VAI_TRO_BAC_SI,
            nguoi_thuc_hien="admin",
            ma_bac_si="030222002",
        )
        assert ok, f"Tạo tài khoản bác sĩ thất bại: {msg}"
        assert tk_bs.ma_bac_si == "030222002", "Mã bác sĩ gán sai!"
        print(f"   -> [OK] {msg} (Mã BS: {tk_bs.ma_bac_si})")

        # 4. Kiểm tra ràng buộc: vai trò bác sĩ không được thiếu mã bác sĩ
        print("\n4. Kiểm tra ràng buộc khi thiếu mã bác sĩ:")
        ok_fail, msg_fail, _ = ql.tao_tai_khoan(
            ten="bs_khong_ma",
            mat_khau="Doctor@123",
            vai_tro=VAI_TRO_BAC_SI,
            nguoi_thuc_hien="admin",
            ma_bac_si="",
        )
        assert not ok_fail, "Thiếu mã bác sĩ mà vẫn tạo thành công!"
        print(f"   -> [OK] Đã chặn đúng: {msg_fail}")

        # 5. Kiểm tra ràng buộc: mã bác sĩ sai định dạng (không đủ 9 số)
        print("\n5. Kiểm tra ràng buộc mã bác sĩ sai định dạng:")
        ok_fail2, msg_fail2, _ = ql.tao_tai_khoan(
            ten="bs_sai_ma",
            mat_khau="Doctor@123",
            vai_tro=VAI_TRO_BAC_SI,
            nguoi_thuc_hien="admin",
            ma_bac_si="12345",
        )
        assert not ok_fail2, "Mã bác sĩ 5 số mà vẫn tạo thành công!"
        print(f"   -> [OK] Đã chặn đúng: {msg_fail2}")

        # 6. Kiểm tra ràng buộc: 1 bác sĩ không được cấp 2 tài khoản trùng mã
        print("\n6. Kiểm tra ràng buộc trùng mã bác sĩ:")
        ok_fail3, msg_fail3, _ = ql.tao_tai_khoan(
            ten="bs_mai_2",
            mat_khau="Doctor@123",
            vai_tro=VAI_TRO_BAC_SI,
            nguoi_thuc_hien="admin",
            ma_bac_si="030222002",  # trùng với bs_mai ở trên
        )
        assert not ok_fail3, "Trùng mã bác sĩ mà vẫn tạo thành công!"
        print(f"   -> [OK] Đã chặn đúng: {msg_fail3}")

        # 7. Kiểm tra hàm tim_theo_ma_bac_si
        print("\n7. Tra cứu tài khoản theo mã bác sĩ:")
        tk_tim = ql.tim_theo_ma_bac_si("030222002")
        assert tk_tim is not None and tk_tim.ten_dang_nhap == "bs_mai"
        print(f"   -> [OK] Tìm thấy tài khoản '{tk_tim.ten_dang_nhap}' cho mã BS '030222002'")

        # 8. Kiểm tra hàm lay_theo_vai_tro
        print("\n8. Lọc danh sách theo vai trò:")
        ds_bs = ql.lay_theo_vai_tro(VAI_TRO_BAC_SI)
        assert len(ds_bs) == 1 and ds_bs[0].ten_dang_nhap == "bs_mai"
        print(f"   -> [OK] Tìm thấy {len(ds_bs)} tài khoản vai trò bác sĩ.")

        # 9. Kiểm tra xác thực đăng nhập tài khoản bác sĩ
        print("\n9. Xác thực tài khoản bác sĩ vừa tạo:")
        vt_bs = ql.xac_thuc("bs_mai", "Doctor@123")
        assert vt_bs == VAI_TRO_BAC_SI
        print(f"   -> [OK] Đăng nhập bác sĩ thành công, vai trò trả về: '{vt_bs}'")

    print("\n" + "=" * 65)
    print("TẤT CẢ CÁC BÀI TEST QUẢN LÝ TÀI KHOẢN ĐỀU VƯỢT QUA XUẤT SẮC!")
    print("=" * 65)


if __name__ == "__main__":
    chay_kiem_thu()
