"""Dịch vụ Quản lý tài khoản và Phân quyền người dùng (QuanLyTaiKhoan)."""
from datetime import date
from models.tai_khoan import TaiKhoan
from services.json_store import JsonStore
from config import DANH_SACH_VAI_TRO, VAI_TRO_ADMIN, VAI_TRO_LE_TAN

FILE_TAI_KHOAN = "tai_khoan.json"


class QuanLyTaiKhoan:
    """Quản lý danh sách tài khoản, xác thực bảo mật và phân quyền hệ thống."""

    def __init__(self, json_store=None, ten_file=FILE_TAI_KHOAN):
        """Khởi tạo dịch vụ quản lý tài khoản với bộ lưu trữ JsonStore."""
        self.store = json_store or JsonStore()
        self.ten_file = ten_file
        self._danh_sach = []
        self.nap_du_lieu()

    def nap_du_lieu(self):
        """Đọc danh sách tài khoản từ file JSON vào bộ nhớ."""
        danh_sach_raw = self.store.doc_file(self.ten_file)
        self._danh_sach = []
        for d in danh_sach_raw:
            try:
                self._danh_sach.append(TaiKhoan.from_dict(d))
            except (KeyError, ValueError):
                continue

    def luu_du_lieu(self):
        """Ghi danh sách tài khoản hiện tại ra file JSON theo cơ chế Atomic Write."""
        du_lieu_json = [tk.to_dict() for tk in self._danh_sach]
        return self.store.ghi_file(self.ten_file, du_lieu_json)

    def lay_tat_ca(self):
        """Trả về toàn bộ danh sách tài khoản trong hệ thống."""
        return list(self._danh_sach)

    def tim_theo_ten(self, ten):
        """Tìm tài khoản theo tên đăng nhập (không phân biệt chữ hoa/thường)."""
        if not ten:
            return None
        ten_clean = str(ten).strip().lower()
        for tk in self._danh_sach:
            if tk.ten_dang_nhap.lower() == ten_clean:
                return tk
        return None

    def xac_thuc(self, ten_dang_nhap, mat_khau_nhap):
        """Xác thực đăng nhập người dùng."""
        tk = self.tim_theo_ten(ten_dang_nhap)
        if not tk:
            return None
        if not tk.trang_thai:
            return None
        if tk.xac_thuc(mat_khau_nhap):
            return tk.vai_tro
        return None

    def doi_mat_khau(self, ten, mk_cu, mk_moi):
        """Người dùng tự đổi mật khẩu tài khoản của mình."""
        tk = self.tim_theo_ten(ten)
        if not tk:
            return False, f"Không tìm thấy tài khoản '{ten}'!"

        if not tk.xac_thuc(mk_cu):
            return False, "Mật khẩu cũ không chính xác!"

        if mk_cu == mk_moi:
            return False, "Mật khẩu mới không được trùng với mật khẩu cũ!"

        try:
            tk.doi_mat_khau(mk_moi)
            self.luu_du_lieu()
            return True, "Đổi mật khẩu thành công!"
        except ValueError as e:
            return False, str(e)

    def tao_tai_khoan(self, ten, mat_khau, vai_tro, nguoi_thuc_hien=VAI_TRO_ADMIN):
        """Tạo tài khoản mới trong hệ thống (Quyền hạn: Chỉ Admin)."""
        if nguoi_thuc_hien != VAI_TRO_ADMIN:
            return False, "Quyền bị từ chối: Chỉ quản trị viên (Admin) mới có quyền tạo tài khoản!", None

        ten_clean = (ten or "").strip()
        if self.tim_theo_ten(ten_clean):
            return False, f"Tên đăng nhập '{ten_clean}' đã tồn tại trong hệ thống!", None

        try:
            tai_khoan_moi = TaiKhoan.tao_moi(ten_clean, mat_khau, vai_tro)
            self._danh_sach.append(tai_khoan_moi)
            self.luu_du_lieu()
            return True, f"Tạo tài khoản '{ten_clean}' thành công!", tai_khoan_moi
        except ValueError as e:
            return False, str(e), None

    def khoa_tai_khoan(self, ten, nguoi_thuc_hien=VAI_TRO_ADMIN):
        """Khóa tài khoản không cho phép đăng nhập (Quyền hạn: Chỉ Admin)."""
        if nguoi_thuc_hien != VAI_TRO_ADMIN and nguoi_thuc_hien != "admin":
            tk_th = self.tim_theo_ten(nguoi_thuc_hien)
            if not tk_th or tk_th.vai_tro != VAI_TRO_ADMIN:
                return False, "Quyền bị từ chối: Chỉ quản trị viên mới có quyền khóa tài khoản!"

        tk = self.tim_theo_ten(ten)
        if not tk:
            return False, f"Không tìm thấy tài khoản '{ten}'!"

        if tk.ten_dang_nhap.lower() == "admin":
            return False, "Không thể khóa tài khoản quản trị viên mặc định ('admin')!"

        if tk.ten_dang_nhap.lower() == str(nguoi_thuc_hien).lower():
            return False, "Bạn không thể tự khóa tài khoản của chính mình!"

        if not tk.trang_thai:
            return False, f"Tài khoản '{ten}' hiện tại đã bị khóa từ trước!"

        tk.khoa()
        self.luu_du_lieu()
        return True, f"Đã khóa tài khoản '{tk.ten_dang_nhap}' thành công!"

    def mo_khoa_tai_khoan(self, ten, nguoi_thuc_hien=VAI_TRO_ADMIN):
        """Mở khóa cho tài khoản bị vô hiệu hóa (Quyền hạn: Chỉ Admin)."""
        if nguoi_thuc_hien != VAI_TRO_ADMIN and nguoi_thuc_hien != "admin":
            tk_th = self.tim_theo_ten(nguoi_thuc_hien)
            if not tk_th or tk_th.vai_tro != VAI_TRO_ADMIN:
                return False, "Quyền bị từ chối: Chỉ quản trị viên mới có quyền mở khóa tài khoản!"

        tk = self.tim_theo_ten(ten)
        if not tk:
            return False, f"Không tìm thấy tài khoản '{ten}'!"

        if tk.trang_thai:
            return False, f"Tài khoản '{ten}' đang hoạt động bình thường!"

        tk.mo_khoa()
        self.luu_du_lieu()
        return True, f"Đã mở khóa tài khoản '{tk.ten_dang_nhap}' thành công!"

    def dat_lai_mat_khau(self, ten, mat_khau_moi, nguoi_thuc_hien=VAI_TRO_ADMIN):
        """Admin đặt lại mật khẩu cho một tài khoản (không cần biết mật khẩu cũ)."""
        if nguoi_thuc_hien != VAI_TRO_ADMIN and nguoi_thuc_hien != "admin":
            tk_th = self.tim_theo_ten(nguoi_thuc_hien)
            if not tk_th or tk_th.vai_tro != VAI_TRO_ADMIN:
                return False, "Quyền bị từ chối: Chỉ quản trị viên mới có quyền đặt lại mật khẩu!"

        tk = self.tim_theo_ten(ten)
        if not tk:
            return False, f"Không tìm thấy tài khoản '{ten}'!"

        try:
            tk.doi_mat_khau(mat_khau_moi)
            self.luu_du_lieu()
            return True, f"Đặt lại mật khẩu cho tài khoản '{tk.ten_dang_nhap}' thành công!"
        except ValueError as e:
            return False, str(e)

    def xoa_tai_khoan(self, ten, nguoi_thuc_hien=VAI_TRO_ADMIN):
        """Xóa tài khoản khỏi hệ thống (Quyền hạn: Chỉ Admin)."""
        if nguoi_thuc_hien != VAI_TRO_ADMIN and nguoi_thuc_hien != "admin":
            tk_th = self.tim_theo_ten(nguoi_thuc_hien)
            if not tk_th or tk_th.vai_tro != VAI_TRO_ADMIN:
                return False, "Quyền bị từ chối: Chỉ quản trị viên mới có quyền xóa tài khoản!"

        tk = self.tim_theo_ten(ten)
        if not tk:
            return False, f"Không tìm thấy tài khoản '{ten}'!"

        if tk.ten_dang_nhap.lower() == "admin":
            return False, "Không thể xóa tài khoản quản trị viên mặc định ('admin')!"

        if tk.ten_dang_nhap.lower() == str(nguoi_thuc_hien).lower():
            return False, "Bạn không thể tự xóa tài khoản của chính mình!"

        self._danh_sach.remove(tk)
        self.luu_du_lieu()
        return True, f"Đã xóa tài khoản '{tk.ten_dang_nhap}' khỏi hệ thống!"