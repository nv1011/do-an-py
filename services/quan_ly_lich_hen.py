"""Dịch vụ quản lý lịch hẹn (CRUD, lọc theo ngày/bác sĩ, kiểm tra trùng lịch)."""
from datetime import date, datetime
from models.lich_hen import LichHen
from services.json_store import JsonStore
from utils.helpers import tim_lich_trung

FILE_LICH_HEN = "lich_hen.json"


class QuanLyLichHen:
    """Quản lý danh sách lịch hẹn, thao tác CRUD và kiểm tra xung đột thời gian."""

    def __init__(self, json_store=None, quan_ly_bac_si=None, ten_file=FILE_LICH_HEN):
        self.store = json_store or JsonStore()
        self.quan_ly_bac_si = quan_ly_bac_si
        self.ten_file = ten_file
        self._danh_sach = []
        self.nap_du_lieu()

    def nap_du_lieu(self):
        """Đọc danh sách lịch hẹn từ file JSON vào bộ nhớ RAM."""
        danh_sach_raw = self.store.doc_file(self.ten_file)
        self._danh_sach = []
        for d in danh_sach_raw:
            try:
                self._danh_sach.append(LichHen.from_dict(d))
            except (KeyError, ValueError):
                continue

    def luu_du_lieu(self):
        """Ghi danh sách lịch hẹn hiện tại ra file JSON theo cơ chế Atomic Write."""
        du_lieu_json = [lh.to_dict() for lh in self._danh_sach]
        return self.store.ghi_file(self.ten_file, du_lieu_json)

    def lay_tat_ca(self):
        """Trả về toàn bộ danh sách lịch hẹn trong bộ nhớ RAM."""
        return list(self._danh_sach)

    def tim_theo_ma(self, ma):
        """Tìm chính xác lịch hẹn theo mã định danh (VD: LH001)."""
        ma_clean = str(ma).strip()
        for lh in self._danh_sach:
            if lh.ma_lich_hen == ma_clean:
                return lh
        return None

    def sinh_ma_moi(self):
        """Sinh mã lịch hẹn tự động tiếp theo có dạng LH001, LH002..."""
        if not self._danh_sach:
            return "LH001"
        cac_so = []
        for lh in self._danh_sach:
            try:
                so = int(lh.ma_lich_hen[2:])
                cac_so.append(so)
            except ValueError:
                continue
        so_tiep = max(cac_so, default=0) + 1
        return f"LH{so_tiep:03d}"

    def loc_lich_hen(self, ngay=None, ma_bac_si=None):
        """Lọc lịch hẹn phục vụ hiển thị Treeview và Thẻ lịch hẹn theo ngày/mã bác sĩ."""
        if isinstance(ngay, str) and ngay.strip():
            for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                try:
                    ngay = datetime.strptime(ngay.strip(), fmt).date()
                    break
                except ValueError:
                    pass

        ket_qua = []
        for lh in self._danh_sach:
            if ngay and isinstance(ngay, date) and lh.ngay_hen != ngay:
                continue
            if ma_bac_si and lh.ma_bac_si != ma_bac_si:
                continue
            ket_qua.append(lh)
        return ket_qua

    def kiem_tra_trung_lich(self, ma_bac_si, ngay, gio_bat_dau, thoi_luong, ma_lich_hen_bo_qua=None):
        """Kiểm tra xung đột thời gian khám của bác sĩ (bỏ qua lịch hủy, vắng và mã lịch đang sửa)."""
        if isinstance(ngay, str):
            for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                try:
                    ngay = datetime.strptime(ngay.strip(), fmt).date()
                    break
                except ValueError:
                    pass

        danh_sach_dict = [lh.to_dict() for lh in self._danh_sach if lh.trang_thai not in ("Da_huy", "Vang")]
        lich_trung = tim_lich_trung(danh_sach_dict, ma_bac_si, str(ngay), gio_bat_dau, thoi_luong, bo_qua_ma=ma_lich_hen_bo_qua)

        if lich_trung:
            return True, f"Bác sĩ đã có lịch hẹn khác vào lúc {lich_trung.get('gio_bat_dau', '')}!"
        return False, ""

    def lay_danh_sach_bac_si_ranh(self, ngay, gio_bat_dau, thoi_luong, ma_khoa=None):
        """Lấy danh sách các bác sĩ rảnh không bị trùng lịch trong khung giờ yêu cầu."""
        if not self.quan_ly_bac_si:
            return []

        danh_sach_bs = self.quan_ly_bac_si.lay_tat_ca()
        if ma_khoa:
            danh_sach_bs = [bs for bs in danh_sach_bs if bs.ma_chuyen_khoa == ma_khoa]

        bs_ranh = []
        for bs in danh_sach_bs:
            trung, _ = self.kiem_tra_trung_lich(bs.ma_dinh_danh, ngay, gio_bat_dau, thoi_luong)
            if not trung:
                bs_ranh.append(bs)
        return bs_ranh

    def dat_lich(self, du_lieu):
        """Đặt lịch hẹn mới với các ràng buộc về ngày tương lai và trùng lịch."""
        try:
            ngay_str = du_lieu.get("ngay_hen")
            if isinstance(ngay_str, str):
                parsed_ngay = None
                for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                    try:
                        parsed_ngay = datetime.strptime(ngay_str.strip(), fmt).date()
                        break
                    except ValueError:
                        continue
                if not parsed_ngay:
                    return False, "Ngày hẹn không đúng định dạng (DD-MM-YYYY hoặc YYYY-MM-DD)!", None
                ngay_hen = parsed_ngay
            else:
                ngay_hen = ngay_str

            if ngay_hen < date.today():
                return False, "Không thể đặt lịch hẹn cho ngày ở quá khứ!", None

            trung, thong_diep_trung = self.kiem_tra_trung_lich(
                du_lieu.get("ma_bac_si"),
                ngay_hen,
                du_lieu.get("gio_bat_dau"),
                int(du_lieu.get("thoi_luong", 30))
            )
            if trung:
                return False, thong_diep_trung, None

            ma_lh = du_lieu.get("ma_lich_hen") or self.sinh_ma_moi()
            lich_hen = LichHen(
                ma_lich_hen=ma_lh,
                ma_benh_nhan=du_lieu.get("ma_benh_nhan"),
                ma_bac_si=du_lieu.get("ma_bac_si"),
                ngay_hen=ngay_hen,
                gio_bat_dau=du_lieu.get("gio_bat_dau"),
                thoi_luong=int(du_lieu.get("thoi_luong", 30)),
                trang_thai=du_lieu.get("trang_thai", "Cho_kham"),
                ly_do_kham=du_lieu.get("ly_do_kham", "")
            )

            self._danh_sach.append(lich_hen)
            if self.luu_du_lieu():
                return True, f"Đặt lịch hẹn thành công (Mã: {ma_lh})!", lich_hen
            return False, f"Lỗi khi lưu dữ liệu: {self.store.loi_cuoi or 'không rõ nguyên nhân'}", None

        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"Lỗi hệ thống: {e}", None

    def sua_lich(self, ma, du_lieu_moi):
        """Cập nhật thông tin lịch hẹn đã có."""
        lh_hien_tai = self.tim_theo_ma(ma)
        if not lh_hien_tai:
            return False, f"Không tìm thấy lịch hẹn có mã '{ma}'!"

        try:
            ma_bs = du_lieu_moi.get("ma_bac_si", lh_hien_tai.ma_bac_si)
            gio_bd = du_lieu_moi.get("gio_bat_dau", lh_hien_tai.gio_bat_dau)
            tl = int(du_lieu_moi.get("thoi_luong", lh_hien_tai.thoi_luong))
            ngay_raw = du_lieu_moi.get("ngay_hen", lh_hien_tai.ngay_hen)

            if isinstance(ngay_raw, str):
                ngay_hen = None
                for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                    try:
                        ngay_hen = datetime.strptime(ngay_raw.strip(), fmt).date()
                        break
                    except ValueError:
                        continue
                if not ngay_hen:
                    return False, "Ngày hẹn không đúng định dạng!"
            else:
                ngay_hen = ngay_raw

            trung, thong_diep = self.kiem_tra_trung_lich(ma_bs, ngay_hen, gio_bd, tl, ma_lich_hen_bo_qua=ma)
            if trung:
                return False, thong_diep

            lh_hien_tai.ma_bac_si = ma_bs
            lh_hien_tai.ngay_hen = ngay_hen
            lh_hien_tai.gio_bat_dau = gio_bd
            lh_hien_tai.thoi_luong = tl
            if "trang_thai" in du_lieu_moi:
                lh_hien_tai.trang_thai = du_lieu_moi["trang_thai"]
            if "ly_do_kham" in du_lieu_moi:
                lh_hien_tai.ly_do_kham = du_lieu_moi["ly_do_kham"]

            if self.luu_du_lieu():
                return True, "Cập nhật thông tin lịch hẹn thành công!"
            return False, f"Lỗi khi ghi dữ liệu: {self.store.loi_cuoi or 'không rõ nguyên nhân'}"

        except ValueError as e:
            return False, str(e)

    def huy_lich(self, ma, ly_do=""):
        """Chuyển trạng thái lịch hẹn sang 'Da_huy' để giải phóng khung giờ."""
        lh_tim_thay = self.tim_theo_ma(ma)
        if not lh_tim_thay:
            return False, f"Không tìm thấy lịch hẹn có mã '{ma}'!"

        lh_tim_thay.trang_thai = "Da_huy"
        if ly_do.strip():
            lh_tim_thay.ly_do_kham = f"{lh_tim_thay.ly_do_kham} (Hủy: {ly_do.strip()})".strip()

        if self.luu_du_lieu():
            return True, "Hủy lịch hẹn thành công!"
        return False, f"Lỗi khi cập nhật file: {self.store.loi_cuoi or 'không rõ nguyên nhân'}"