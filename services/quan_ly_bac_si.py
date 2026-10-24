"""Dịch vụ quản lý bác sĩ (CRUD, lọc theo chuyên khoa, tìm kiếm theo mã/tên)."""
from datetime import date, datetime
from models.bac_si import BacSi
from services.json_store import JsonStore
from utils.helpers import khop
from utils.validators import la_sdt_hop_le, la_ma_bac_si_hop_le, la_ngay_hop_le
from config import FILE_BAC_SI

_TRUONG_TIM_BS = {
    "ho_ten": "ho_ten",
    "ma": "ma_dinh_danh",
    "ma_dinh_danh": "ma_dinh_danh",
    "sdt": "sdt",
    "chuyen_khoa": "ma_chuyen_khoa",
}


class QuanLyBacSi:
    """Quản lý danh sách bác sĩ, thao tác CRUD và tìm kiếm thông tin."""

    def __init__(self, json_store=None, ten_file=FILE_BAC_SI):
        self.store = json_store or JsonStore()
        self.ten_file = ten_file
        self._danh_sach = []
        self.nap_du_lieu()

    def nap_du_lieu(self):
        """Đọc danh sách bác sĩ từ file JSON vào bộ nhớ."""
        danh_sach_raw = self.store.doc_file(self.ten_file)
        if self.store.loi_cuoi:
                    pass
        
        self._danh_sach = []
        for d in danh_sach_raw:
            try:
                self._danh_sach.append(BacSi.from_dict(d))
            except (KeyError, ValueError):
                continue

    def luu_du_lieu(self):
        """Ghi danh sách bác sĩ hiện tại ra file JSON theo cơ chế Atomic Write."""
        du_lieu_json = [bs.to_dict() for bs in self._danh_sach]
        return self.store.ghi_file(self.ten_file, du_lieu_json)

    def lay_tat_ca(self):
        """Trả về toàn bộ danh sách bác sĩ trong bộ nhớ."""
        return list(self._danh_sach)

    def tim_theo_ma(self, ma):
        """Tìm chính xác bác sĩ theo mã định danh 9 chữ số."""
        ma_clean = str(ma).strip()
        for bs in self._danh_sach:
            if bs.ma_dinh_danh == ma_clean:
                return bs
        return None

    def lay_theo_chuyen_khoa(self, ma_khoa):
        """Lấy danh sách bác sĩ thuộc một chuyên khoa cụ thể."""
        ma_khoa_clean = str(ma_khoa).strip()
        return [bs for bs in self._danh_sach if bs.ma_chuyen_khoa == ma_khoa_clean]

    def tim_kiem(self, tu_khoa="", tieu_chi="ho_ten"):
        """Tìm kiếm bác sĩ theo từ khóa và tiêu chí chỉ định."""
        thuoc_tinh = _TRUONG_TIM_BS.get(tieu_chi)
        if thuoc_tinh is None:
            return []

        if tieu_chi == "ho_ten":
            return [bs for bs in self.lay_tat_ca() if khop("ho_ten", bs.ho_ten, tu_khoa)]
        
        return [
            bs for bs in self.lay_tat_ca()
            if khop(tieu_chi, str(getattr(bs, thuoc_tinh, "")), tu_khoa)
        ]

    def _chuyen_ngay(self, val):
        """Chuyển đổi chuỗi ngày dạng DD-MM-YYYY hoặc YYYY-MM-DD sang date, kiểm tra hợp lệ."""
        if isinstance(val, date):
            return True, val, ""
        if not val or not str(val).strip():
            return False, None, "Ngày tháng không được để trống!"

        s = str(val).strip()
        for sep in ("-", "/"):
            if sep in s:
                parts = s.split(sep)
                if len(parts) == 3:
                    try:
                        if len(parts[0]) <= 2 and len(parts[2]) == 4:
                            ngay, thang, nam = int(parts[0]), int(parts[1]), int(parts[2])
                        elif len(parts[0]) == 4 and len(parts[2]) <= 2:
                            nam, thang, ngay = int(parts[0]), int(parts[1]), int(parts[2])
                        else:
                            continue

                        if not la_ngay_hop_le(ngay, thang, nam):
                            return False, None, f"Ngày không hợp lệ ({ngay:02d}/{thang:02d}/{nam})!"
                        d = date(nam, thang, ngay)
                        if d > date.today():
                            return False, None, "Ngày sinh không được ở tương lai!"
                        return True, d, ""
                    except ValueError:
                        continue

        return False, None, "Định dạng ngày phải là DD-MM-YYYY (Ví dụ: 15-05-1978)!"

    def them(self, du_lieu):
        """Thêm bác sĩ mới. Tự động kiểm tra trùng mã 9 số và SĐT."""
        ho_ten = (du_lieu.get("ho_ten") or "").strip()
        if not ho_ten:
            return False, "Họ và tên bác sĩ không được để trống!", None

        ma_dinh_danh = str(du_lieu.get("ma_dinh_danh") or "").strip()
        if not la_ma_bac_si_hop_le(ma_dinh_danh):
            return False, "Mã bác sĩ phải gồm đúng 9 chữ số!", None

        if self.tim_theo_ma(ma_dinh_danh):
            return False, f"Mã bác sĩ '{ma_dinh_danh}' đã tồn tại trong hệ thống!", None

        ok, ngay_sinh, msg = self._chuyen_ngay(du_lieu.get("ngay_sinh"))
        if not ok:
            return False, msg, None

        sdt = str(du_lieu.get("sdt") or "").strip()
        if not la_sdt_hop_le(sdt):
            return False, "Số điện thoại không hợp lệ (phải gồm 10 số, bắt đầu bằng 0)!", None

        for bs in self._danh_sach:
            if bs.sdt == sdt:
                return False, f"Số điện thoại '{sdt}' đã được sử dụng bởi bác sĩ {bs.ho_ten}!", None

        try:
            luong_cb = float(du_lieu.get("luong_cb", 0))
            if luong_cb < 0:
                raise ValueError("Lương cơ bản không được âm!")
        except (TypeError, ValueError):
            return False, "Lương cơ bản không hợp lệ!", None

        lich_lam_viec = du_lieu.get("lich_lam_viec", [])

        try:
            bs_moi = BacSi(
                ma_dinh_danh=ma_dinh_danh,
                ho_ten=ho_ten,
                dia_chi=(du_lieu.get("dia_chi") or "").strip(),
                tinh_thanh=(du_lieu.get("tinh_thanh") or "").strip(),
                xa_phuong=(du_lieu.get("xa_phuong") or "").strip(),
                gioi_tinh=du_lieu.get("gioi_tinh", "Nam"),
                ngay_sinh=ngay_sinh,
                sdt=sdt,
                lich_lam_viec=lich_lam_viec,
                luong_cb=luong_cb
            )
        except ValueError as e:
            return False, f"Dữ liệu không hợp lệ: {e}", None

        self._danh_sach.append(bs_moi)
        if self.luu_du_lieu():
            return True, f"Thêm bác sĩ '{ho_ten}' thành công!", bs_moi
        return False, f"Lỗi khi lưu dữ liệu: {self.store.loi_cuoi or 'không rõ nguyên nhân'}", None

    def sua(self, ma, du_lieu_moi):
        """Cập nhật thông tin bác sĩ có mã ma."""
        bs = self.tim_theo_ma(ma)
        if not bs:
            return False, f"Không tìm thấy bác sĩ có mã '{ma}'!"

        try:
            if "ho_ten" in du_lieu_moi:
                bs.ho_ten = du_lieu_moi["ho_ten"]
            if "ngay_sinh" in du_lieu_moi:
                ok, d, msg = self._chuyen_ngay(du_lieu_moi["ngay_sinh"])
                if not ok:
                    return False, msg
                bs._ngay_sinh = d
            if "gioi_tinh" in du_lieu_moi:
                bs.gioi_tinh = du_lieu_moi["gioi_tinh"]
            if "sdt" in du_lieu_moi:
                sdt_moi = str(du_lieu_moi["sdt"]).strip()
                for other in self._danh_sach:
                    if other.ma_dinh_danh != bs.ma_dinh_danh and other.sdt == sdt_moi:
                        return False, f"Số điện thoại '{sdt_moi}' đã thuộc về bác sĩ khác!"
                bs.sdt = sdt_moi
            if "dia_chi" in du_lieu_moi:
                bs._dia_chi = du_lieu_moi["dia_chi"]
            if "tinh_thanh" in du_lieu_moi:
                bs.tinh_thanh = du_lieu_moi["tinh_thanh"]
            if "xa_phuong" in du_lieu_moi:
                bs.xa_phuong = du_lieu_moi["xa_phuong"]
            if "lich_lam_viec" in du_lieu_moi:
                bs.lich_lam_viec = du_lieu_moi["lich_lam_viec"]
            if "luong_cb" in du_lieu_moi:
                bs.luong_cb = float(du_lieu_moi["luong_cb"])

            if self.luu_du_lieu():
                return True, f"Cập nhật thông tin bác sĩ '{bs.ho_ten}' thành công!"
            return False, f"Lỗi khi ghi dữ liệu: {self.store.loi_cuoi or 'không rõ nguyên nhân'}"
        except ValueError as e:
            return False, f"Lỗi cập nhật: {e}"

    def xoa(self, ma):
        """Xóa bác sĩ khỏi hệ thống (kiểm tra không xóa nếu đang có ràng buộc)."""
        bs = self.tim_theo_ma(ma)
        if not bs:
            return False, f"Không tìm thấy bác sĩ có mã '{ma}'!"

        self._danh_sach.remove(bs)
        if self.luu_du_lieu():
            return True, f"Đã xóa bác sĩ '{bs.ho_ten}' khỏi hệ thống!"
        return False, f"Lỗi khi cập nhật file: {self.store.loi_cuoi or 'không rõ nguyên nhân'}"