"""Dịch vụ Quản lý tài khoản và Phân quyền người dùng (QuanLyTaiKhoan)."""
from datetime import date
from models.tai_khoan import TaiKhoan
from services.json_store import JsonStore
from config import DANH_SACH_VAI_TRO, VAI_TRO_ADMIN, VAI_TRO_LE_TAN, VAI_TRO_BAC_SI, FILE_TAI_KHOAN
from utils.validators import la_ma_bac_si_hop_le


class QuanLyTaiKhoan:
    """Quản lý danh sách tài khoản, xác thực bảo mật và phân quyền hệ thống.

    Hỗ trợ 3 vai trò:
        - 'admin': Quản trị viên hệ thống.
        - 'le_tan': Nhân viên lễ tân / tiếp đón.
        - 'bac_si': Bác sĩ chuyên môn (gắn liền với mã bác sĩ 9 số).
    """

    def __init__(self, json_store=None, ten_file=FILE_TAI_KHOAN, quan_ly_bac_si=None):
        """Khởi tạo dịch vụ quản lý tài khoản với bộ lưu trữ JsonStore.

        Tham số:
            json_store (JsonStore | None): Bộ lưu trữ JsonStore tùy biến hoặc mặc định.
            ten_file (Path | str): Đường dẫn tới file lưu trữ dữ liệu tài khoản JSON.
            quan_ly_bac_si (QuanLyBacSi | None): Dịch vụ quản lý bác sĩ dùng để kiểm tra tính tồn tại của bác sĩ.
        """
        self.store = json_store or JsonStore()
        self.ten_file = ten_file
        self.quan_ly_bac_si = quan_ly_bac_si
        self._danh_sach = []
        self.nap_du_lieu()

    def nap_du_lieu(self):
        """Đọc danh sách tài khoản từ file JSON vào bộ nhớ, lưu vết file hỏng nếu có."""
        danh_sach_raw = self.store.doc_file(self.ten_file)
        if self.store.loi_cuoi:
            pass

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
        """Tìm tài khoản theo tên đăng nhập (không phân biệt chữ hoa/thường).

        Tham số:
            ten (str): Tên đăng nhập cần tìm.

        Trả về:
            TaiKhoan | None: Đối tượng tài khoản tìm được hoặc None nếu không có.
        """
        if not ten:
            return None
        ten_clean = str(ten).strip().lower()
        for tk in self._danh_sach:
            if tk.ten_dang_nhap.lower() == ten_clean:
                return tk
        return None

    def tim_theo_ma_bac_si(self, ma_bac_si):
        """Tìm tài khoản được liên kết với mã bác sĩ cụ thể.

        Tham số:
            ma_bac_si (str): Mã định danh bác sĩ 9 số.

        Trả về:
            TaiKhoan | None: Đối tượng tài khoản gắn với bác sĩ này hoặc None.
        """
        if not ma_bac_si:
            return None
        ma_clean = str(ma_bac_si).strip()
        for tk in self._danh_sach:
            if tk.vai_tro == VAI_TRO_BAC_SI and tk.ma_bac_si == ma_clean:
                return tk
        return None

    def lay_theo_vai_tro(self, vai_tro):
        """Lọc danh sách các tài khoản theo vai trò cụ thể ('admin', 'le_tan', 'bac_si').

        Tham số:
            vai_tro (str): Tên vai trò cần lọc.

        Trả về:
            list[TaiKhoan]: Danh sách các tài khoản thỏa mãn.
        """
        vt_clean = str(vai_tro).strip().lower()
        return [tk for tk in self._danh_sach if tk.vai_tro == vt_clean]

    def _la_admin(self, nguoi_thuc_hien):
        """Kiểm tra người thực hiện thao tác có phải là tài khoản admin đang hoạt động hay không.

        Tham số:
            nguoi_thuc_hien (str): Tên đăng nhập của tài khoản yêu cầu thao tác.

        Trả về:
            bool: True nếu là admin đang hoạt động; False nếu không hợp lệ hoặc bị khóa.
        """
        if not nguoi_thuc_hien:
            return False
        tk = self.tim_theo_ten(nguoi_thuc_hien)
        return tk is not None and tk.trang_thai and tk.vai_tro == VAI_TRO_ADMIN

    def xac_thuc(self, ten_dang_nhap, mat_khau_nhap):
        """Xác thực đăng nhập người dùng bằng thuật toán băm mật khẩu kèm salt.

        Tham số:
            ten_dang_nhap (str): Tên tài khoản nhập vào form.
            mat_khau_nhap (str): Mật khẩu thô người dùng gõ.

        Trả về:
            str | None: Tên vai trò ('admin', 'le_tan' hoặc 'bac_si') nếu đúng; None nếu sai hoặc tài khoản bị khóa.
        """
        tk = self.tim_theo_ten(ten_dang_nhap)
        if not tk or not tk.trang_thai:
            return None
        if tk.xac_thuc(mat_khau_nhap):
            return tk.vai_tro
        return None

    def doi_mat_khau(self, ten, mk_cu, mk_moi):
        """Người dùng tự đổi mật khẩu tài khoản của mình.

        Tham số:
            ten (str): Tên tài khoản yêu cầu đổi mật khẩu.
            mk_cu (str): Mật khẩu hiện tại để xác thực.
            mk_moi (str): Mật khẩu mới mong muốn.

        Trả về:
            tuple[bool, str]: (Thành công, Thông điệp phản hồi).
        """
        tk = self.tim_theo_ten(ten)
        if not tk:
            return False, f"Không tìm thấy tài khoản '{ten}'!"

        if not tk.xac_thuc(mk_cu):
            return False, "Mật khẩu cũ không chính xác!"

        if mk_cu == mk_moi:
            return False, "Mật khẩu mới không được trùng với mật khẩu cũ!"

        try:
            tk.doi_mat_khau(mk_moi)
            if not self.luu_du_lieu():
                return False, f"Lỗi ghi file: {self.store.loi_cuoi}"
            return True, "Đổi mật khẩu thành công!"
        except ValueError as e:
            return False, str(e)

    def tao_tai_khoan(self, ten, mat_khau, vai_tro, nguoi_thuc_hien=None, ma_bac_si=None):
        """Tạo tài khoản mới trong hệ thống (Quyền hạn: Chỉ Admin).

        Khi vai trò là 'bac_si', bắt buộc phải cung cấp mã bác sĩ hợp lệ (9 chữ số)
        và chưa có tài khoản nào khác được gán cho bác sĩ đó.

        Tham số:
            ten (str): Tên đăng nhập mới (ít nhất 3 ký tự, không dấu cách).
            mat_khau (str): Mật khẩu thô khởi tạo (ít nhất 6 ký tự, có ký tự đặc biệt).
            vai_tro (str): Vai trò ('admin', 'le_tan', hoặc 'bac_si').
            nguoi_thuc_hien (str): Tên đăng nhập của admin đang thực hiện thao tác.
            ma_bac_si (str | None): Mã bác sĩ 9 số liên kết (bắt buộc đối với vai trò 'bac_si').

        Trả về:
            tuple[bool, str, TaiKhoan | None]: (Thành công, Thông điệp, Đối tượng tài khoản vừa tạo).
        """
        if not self._la_admin(nguoi_thuc_hien):
            return False, "Quyền bị từ chối: Chỉ quản trị viên mới có quyền tạo tài khoản!", None

        ten_clean = (ten or "").strip()
        if self.tim_theo_ten(ten_clean):
            return False, f"Tên đăng nhập '{ten_clean}' đã tồn tại trong hệ thống!", None

        vai_tro_clean = (vai_tro or "").strip().lower()
        if vai_tro_clean not in DANH_SACH_VAI_TRO:
            hop_le = ", ".join(DANH_SACH_VAI_TRO)
            return False, f"Vai trò không hợp lệ! Chỉ chấp nhận: {hop_le}", None

        ma_bs_clean = str(ma_bac_si).strip() if ma_bac_si is not None else None

        # Ràng buộc đối với tài khoản vai trò Bác sĩ
        if vai_tro_clean == VAI_TRO_BAC_SI:
            # Nếu chưa truyền ma_bac_si, kiểm tra xem tên đăng nhập có phải là mã bác sĩ 9 số không
            if not ma_bs_clean:
                if la_ma_bac_si_hop_le(ten_clean):
                    ma_bs_clean = ten_clean
                else:
                    return False, "Tài khoản vai trò bác sĩ bắt buộc phải cung cấp mã bác sĩ (ma_bac_si)!", None

            if not la_ma_bac_si_hop_le(ma_bs_clean):
                return False, f"Mã bác sĩ '{ma_bs_clean}' không hợp lệ (phải gồm đúng 9 chữ số)!", None

            # Kiểm tra xem bác sĩ đã được cấp tài khoản nào chưa
            tk_da_co = self.tim_theo_ma_bac_si(ma_bs_clean)
            if tk_da_co:
                return False, f"Bác sĩ có mã '{ma_bs_clean}' đã được cấp tài khoản '{tk_da_co.ten_dang_nhap}'!", None

            # Kiểm tra xem bác sĩ có tồn tại trong hệ thống hay không (nếu có QuanLyBacSi)
            if self.quan_ly_bac_si:
                bs = self.quan_ly_bac_si.tim_theo_ma(ma_bs_clean)
                if not bs:
                    return False, f"Không tìm thấy bác sĩ có mã '{ma_bs_clean}' trong danh sách bác sĩ!", None
        else:
            ma_bs_clean = None

        try:
            tai_khoan_moi = TaiKhoan.tao_moi(ten_clean, mat_khau, vai_tro_clean, ma_bac_si=ma_bs_clean)
            self._danh_sach.append(tai_khoan_moi)
            if not self.luu_du_lieu():
                self._danh_sach.pop()
                return False, f"Lỗi ghi file: {self.store.loi_cuoi}", None
            return True, f"Tạo tài khoản '{ten_clean}' thành công!", tai_khoan_moi
        except ValueError as e:
            return False, str(e), None

    def khoa_tai_khoan(self, ten, nguoi_thuc_hien=None):
        """Khóa tài khoản không cho phép đăng nhập (Quyền hạn: Chỉ Admin).

        Tham số:
            ten (str): Tên tài khoản cần khóa.
            nguoi_thuc_hien (str): Tên đăng nhập của admin đang thực hiện thao tác.

        Trả về:
            tuple[bool, str]: (Thành công, Thông điệp phản hồi).
        """
        if not self._la_admin(nguoi_thuc_hien):
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
        if not self.luu_du_lieu():
            tk.mo_khoa()  # Hoàn tác trạng thái
            return False, f"Lỗi ghi file: {self.store.loi_cuoi}"
            
        return True, f"Đã khóa tài khoản '{tk.ten_dang_nhap}' thành công!"

    def mo_khoa_tai_khoan(self, ten, nguoi_thuc_hien=None):
        """Mở khóa cho tài khoản bị vô hiệu hóa (Quyền hạn: Chỉ Admin).

        Tham số:
            ten (str): Tên tài khoản cần mở khóa.
            nguoi_thuc_hien (str): Tên đăng nhập của admin đang thực hiện thao tác.

        Trả về:
            tuple[bool, str]: (Thành công, Thông điệp phản hồi).
        """
        if not self._la_admin(nguoi_thuc_hien):
            return False, "Quyền bị từ chối: Chỉ quản trị viên mới có quyền mở khóa tài khoản!"

        tk = self.tim_theo_ten(ten)
        if not tk:
            return False, f"Không tìm thấy tài khoản '{ten}'!"

        if tk.trang_thai:
            return False, f"Tài khoản '{ten}' đang hoạt động bình thường!"

        tk.mo_khoa()
        if not self.luu_du_lieu():
            tk.khoa()  # Hoàn tác trạng thái
            return False, f"Lỗi ghi file: {self.store.loi_cuoi}"
            
        return True, f"Đã mở khóa tài khoản '{tk.ten_dang_nhap}' thành công!"

    def dat_lai_mat_khau(self, ten, mat_khau_moi, nguoi_thuc_hien=None):
        """Admin đặt lại mật khẩu cho một tài khoản mà không cần biết mật khẩu cũ.

        Tham số:
            ten (str): Tên tài khoản cần đặt lại mật khẩu.
            mat_khau_moi (str): Mật khẩu mới cần gán.
            nguoi_thuc_hien (str): Tên đăng nhập của admin đang thực hiện thao tác.

        Trả về:
            tuple[bool, str]: (Thành công, Thông điệp phản hồi).
        """
        if not self._la_admin(nguoi_thuc_hien):
            return False, "Quyền bị từ chối: Chỉ quản trị viên mới có quyền đặt lại mật khẩu!"

        tk = self.tim_theo_ten(ten)
        if not tk:
            return False, f"Không tìm thấy tài khoản '{ten}'!"

        try:
            # Lưu lại hash cũ để phòng hờ rollback nếu lỗi ghi file
            hash_cu_tam = tk.mat_khau_hash
            salt_cu_tam = tk.salt
            
            tk.doi_mat_khau(mat_khau_moi)
            if not self.luu_du_lieu():
                tk._mat_khau_hash = hash_cu_tam
                tk._salt = salt_cu_tam
                return False, f"Lỗi ghi file: {self.store.loi_cuoi}"
                
            return True, f"Đặt lại mật khẩu cho tài khoản '{tk.ten_dang_nhap}' thành công!"
        except ValueError as e:
            return False, str(e)

    def xoa_tai_khoan(self, ten, nguoi_thuc_hien=None):
        """Xóa tài khoản khỏi hệ thống (Quyền hạn: Chỉ Admin).

        Tham số:
            ten (str): Tên tài khoản cần xóa.
            nguoi_thuc_hien (str): Tên đăng nhập của admin đang thực hiện thao tác.

        Trả về:
            tuple[bool, str]: (Thành công, Thông điệp phản hồi).
        """
        if not self._la_admin(nguoi_thuc_hien):
            return False, "Quyền bị từ chối: Chỉ quản trị viên mới có quyền xóa tài khoản!"

        tk = self.tim_theo_ten(ten)
        if not tk:
            return False, f"Không tìm thấy tài khoản '{ten}'!"

        if tk.ten_dang_nhap.lower() == "admin":
            return False, "Không thể xóa tài khoản quản trị viên mặc định ('admin')!"

        if tk.ten_dang_nhap.lower() == str(nguoi_thuc_hien).lower():
            return False, "Bạn không thể tự xóa tài khoản của chính mình!"

        self._danh_sach.remove(tk)
        if not self.luu_du_lieu():
            self._danh_sach.append(tk)  # Hoàn tác nếu lưu thất bại
            return False, f"Lỗi ghi file: {self.store.loi_cuoi}"
            
        return True, f"Đã xóa tài khoản '{tk.ten_dang_nhap}' khỏi hệ thống!"
