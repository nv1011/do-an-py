"""Dịch vụ quản lý bệnh nhân (CRUD, tìm kiếm đa tiêu chí không dấu, kiểm tra hợp lệ)."""
from datetime import date, datetime
from models.benh_nhan import BenhNhan
from services.json_store import JsonStore
from utils.helpers import khop
from utils.validators import la_ngay_hop_le, la_sdt_hop_le, la_ma_bhyt_hop_le, la_email_hop_le

# Ánh xạ mã tiêu chí sang tên thuộc tính của đối tượng BenhNhan
_TRUONG_TIM = {
    "ho_ten": "ho_ten",
    "bhyt": "so_bhyt",
    "so_bhyt": "so_bhyt",
    "sdt": "sdt",
    "ma": "ma_dinh_danh",
    "ma_dinh_danh": "ma_dinh_danh",
}


class QuanLyBenhNhan:
    """Quản lý danh sách bệnh nhân, thao tác CRUD và tìm kiếm gần đúng."""

    def __init__(self, json_store = None, ten_file = "benh_nhan.json"):
        self.store = json_store or JsonStore()
        self.ten_file = ten_file
        self._danh_sach: list[BenhNhan] = []
        self.nap_du_lieu()

    def nap_du_lieu(self):
        """Đọc danh sách bệnh nhân từ file JSON vào bộ nhớ."""
        danh_sach_raw = self.store.doc_file(self.ten_file)
        self._danh_sach = []
        for d in danh_sach_raw:
            try:
                self._danh_sach.append(BenhNhan.from_dict(d))
            except (KeyError, ValueError):
                continue

    def luu_du_lieu(self):
        """Ghi danh sách bệnh nhân hiện tại ra file JSON theo cơ chế Atomic Write."""
        du_lieu_json = [bn.to_dict() for bn in self._danh_sach]
        return self.store.ghi_file(self.ten_file, du_lieu_json)

    def lay_tat_ca(self):
        """Trả về toàn bộ danh sách bệnh nhân."""
        return list(self._danh_sach)

    def tim_theo_ma(self, ma):
        """Tìm chính xác bệnh nhân theo mã định danh 14 chữ số."""
        ma_clean = str(ma).strip()
        for bn in self._danh_sach:
            if bn.ma_dinh_danh == ma_clean:
                return bn
        return None

    def tim_kiem_ket_hop(
        self,
        ho_ten: str = "",
        so_bhyt: str = "",
        sdt: str = "",
        ma: str = "",
    ):
        """Tìm kiếm kết hợp đa tiêu chí (ít nhất 2 tiêu chí chính: họ tên và số BHYT).

        - Tiêu chí chính: 'ho_ten' và 'so_bhyt'
        - Tiêu chí mở rộng: 'sdt' và 'ma'
        Chỉ trả về các bệnh nhân thỏa mãn TẤT CẢ các tiêu chí được truyền vào (điều kiện AND).
        Tiêu chí nào để trống ("") sẽ tự động bỏ qua.
        """
        ket_qua = self.lay_tat_ca()

        if ho_ten and ho_ten.strip():
            ket_qua = [bn for bn in ket_qua if khop("ho_ten", bn.ho_ten, ho_ten)]

        if so_bhyt and so_bhyt.strip():
            ket_qua = [bn for bn in ket_qua if khop("so_bhyt", bn.so_bhyt, so_bhyt)]

        if sdt and sdt.strip():
            ket_qua = [bn for bn in ket_qua if khop("sdt", bn.sdt, sdt)]

        if ma and ma.strip():
            ket_qua = [bn for bn in ket_qua if khop("ma", bn.ma_dinh_danh, ma)]

        return ket_qua

    def tim_kiem(
        self,
        tu_khoa: str = "",
        tieu_chi: str = "ho_ten",
        ho_ten: str = None,
        so_bhyt: str = None,
        **tieu_chi_khac,
    ):
        """Tìm kiếm bệnh nhân không dấu tiếng Việt.

        Hỗ trợ 2 chế độ gọi:
        1. Đa tiêu chí (kết hợp Họ tên & Số BHYT):
           VD: tim_kiem(ho_ten="An", so_bhyt="4010")
        2. Đơn tiêu chí (tương thích giao diện UI Combobox):
           VD: tim_kiem("van an", tieu_chi="ho_ten")
               tim_kiem("4010123456789", tieu_chi="bhyt")
               tim_kiem("0912345678", tieu_chi="sdt")
               tim_kiem("12102026", tieu_chi="ma")
           Từ khóa rỗng ("") sẽ trả về toàn bộ danh sách.
        """
        # Nếu truyền theo dạng đa tiêu chí (keyword arguments)
        if ho_ten is not None or so_bhyt is not None or tieu_chi_khac:
            return self.tim_kiem_ket_hop(
                ho_ten=ho_ten or "",
                so_bhyt=so_bhyt or "",
                sdt=tieu_chi_khac.get("sdt", ""),
                ma=tieu_chi_khac.get("ma", ""),
            )

        # Chế độ đơn tiêu chí theo hợp đồng hàm
        thuoc_tinh = _TRUONG_TIM.get(tieu_chi)
        if thuoc_tinh is None:
            return []

        return [
            bn for bn in self.lay_tat_ca()
            if khop(tieu_chi, getattr(bn, thuoc_tinh, ""), tu_khoa)
        ]

    def _chuyen_ngay(self, val):
        """Chuyển đổi chuỗi ngày dạng DD-MM-YYYY hoặc YYYY-MM-DD sang date, kiểm tra năm nhuận."""
        if isinstance(val, date):
            return True, val, ""
        if not val or not str(val).strip():
            return False, None, "Ngày tháng không được để trống!"

        s = str(val).strip()
        # Thử chuẩn Việt Nam DD-MM-YYYY hoặc DD/MM/YYYY
        for sep in ("-", "/"):
            if sep in s:
                parts = s.split(sep)
                if len(parts) == 3:
                    try:
                        # Kiểm tra định dạng DD-MM-YYYY
                        if len(parts[0]) <= 2 and len(parts[2]) == 4:
                            ngay, thang, nam = int(parts[0]), int(parts[1]), int(parts[2])
                        # Kiểm tra định dạng YYYY-MM-DD
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

        return False, None, "Định dạng ngày phải là DD-MM-YYYY (Ví dụ: 15-05-1990)!"

    def sinh_ma_moi(self, ngay_dang_ky = None):
        """Sinh mã bệnh nhân 14 số tự động: DDMMYYYY + 6 số thứ tự trong ngày."""
        ngay = ngay_dang_ky or date.today()
        tien_to = ngay.strftime("%d%m%Y")

        stt_max = 0
        for bn in self._danh_sach:
            if bn.ma_dinh_danh.startswith(tien_to):
                try:
                    stt = int(bn.ma_dinh_danh[8:])
                    if stt > stt_max:
                        stt_max = stt
                except ValueError:
                    pass

        stt_moi = stt_max + 1
        return f"{tien_to}{stt_moi:06d}"

    def them(self, du_lieu):
        """Thêm bệnh nhân mới từ từ điển dữ liệu form.

        Tự động kiểm tra trùng mã, trùng SĐT, định dạng ngày sinh DD-MM-YYYY.
        """
        ho_ten = (du_lieu.get("ho_ten") or "").strip()
        if not ho_ten:
            return False, "Họ và tên không được để trống!", None

        ok, ngay_sinh, msg = self._chuyen_ngay(du_lieu.get("ngay_sinh"))
        if not ok:
            return False, msg, None

        sdt = str(du_lieu.get("sdt") or "").strip()
        if not la_sdt_hop_le(sdt):
            return False, "Số điện thoại không hợp lệ (phải gồm 10 số, bắt đầu bằng 0)!", None

        for bn in self._danh_sach:
            if bn.sdt == sdt:
                return False, f"Số điện thoại '{sdt}' đã được đăng ký bởi bệnh nhân {bn.ho_ten}!", None

        so_bhyt = (du_lieu.get("so_bhyt") or "Không có").strip()
        if not la_ma_bhyt_hop_le(so_bhyt):
            return False, "Số thẻ BHYT không hợp lệ (phải gồm đúng 13 chữ số hoặc 'Không có')!", None

        email = (du_lieu.get("email") or "").strip()
        if email and not la_email_hop_le(email):
            return False, "Địa chỉ email không hợp lệ!", None

        ma_dinh_danh = du_lieu.get("ma_dinh_danh")
        if not ma_dinh_danh:
            ma_dinh_danh = self.sinh_ma_moi()
        else:
            ma_dinh_danh = str(ma_dinh_danh).strip()
            if self.tim_theo_ma(ma_dinh_danh):
                return False, f"Mã bệnh nhân '{ma_dinh_danh}' đã tồn tại trong hệ thống!", None

        try:
            bn_moi = BenhNhan(
                ma_dinh_danh=ma_dinh_danh,
                ho_ten=ho_ten,
                dia_chi=(du_lieu.get("dia_chi") or "").strip(),
                tinh_thanh=(du_lieu.get("tinh_thanh") or "").strip(),
                xa_phuong=(du_lieu.get("xa_phuong") or "").strip(),
                gioi_tinh=du_lieu.get("gioi_tinh", "Nam"),
                ngay_sinh=ngay_sinh,
                sdt=sdt,
                so_bhyt=so_bhyt,
                tien_su_benh=(du_lieu.get("tien_su_benh") or "Không có").strip(),
                nhom_mau=du_lieu.get("nhom_mau", "Chưa rõ"),
                email=email,
            )
        except ValueError as e:
            return False, f"Dữ liệu không hợp lệ: {e}", None

        self._danh_sach.append(bn_moi)
        if self.luu_du_lieu():
            return True, f"Thêm bệnh nhân '{ho_ten}' thành công (Mã: {ma_dinh_danh})!", bn_moi
        return False, f"Lỗi khi lưu dữ liệu: {self.store.loi_cuoi or 'không rõ nguyên nhân'}", None

    def sua(self, ma, du_lieu_moi):
        """Cập nhật thông tin bệnh nhân có mã ma. Quyền: Chỉ admin."""
        bn = self.tim_theo_ma(ma)
        if not bn:
            return False, f"Không tìm thấy bệnh nhân có mã '{ma}'!"

        try:
            if "ho_ten" in du_lieu_moi:
                bn.ho_ten = du_lieu_moi["ho_ten"]
            if "ngay_sinh" in du_lieu_moi:
                ok, d, msg = self._chuyen_ngay(du_lieu_moi["ngay_sinh"])
                if not ok:
                    return False, msg
                bn._ngay_sinh = d
            if "gioi_tinh" in du_lieu_moi:
                bn.gioi_tinh = du_lieu_moi["gioi_tinh"]
            if "sdt" in du_lieu_moi:
                sdt_moi = str(du_lieu_moi["sdt"]).strip()
                # Kiểm tra trùng SĐT với người khác
                for other in self._danh_sach:
                    if other.ma_dinh_danh != bn.ma_dinh_danh and other.sdt == sdt_moi:
                        return False, f"Số điện thoại '{sdt_moi}' đã thuộc về bệnh nhân khác!"
                bn.sdt = sdt_moi
            if "dia_chi" in du_lieu_moi:
                bn._dia_chi = du_lieu_moi["dia_chi"]
            if "tinh_thanh" in du_lieu_moi:
                bn.tinh_thanh = du_lieu_moi["tinh_thanh"]
            if "xa_phuong" in du_lieu_moi:
                bn.xa_phuong = du_lieu_moi["xa_phuong"]
            if "so_bhyt" in du_lieu_moi:
                bn.so_bhyt = du_lieu_moi["so_bhyt"]
            if "tien_su_benh" in du_lieu_moi:
                bn.tien_su_benh = du_lieu_moi["tien_su_benh"]
            if "nhom_mau" in du_lieu_moi:
                bn.nhom_mau = du_lieu_moi["nhom_mau"]
            if "email" in du_lieu_moi:
                bn.email = du_lieu_moi["email"]

            if self.luu_du_lieu():
                return True, f"Cập nhật thông tin bệnh nhân '{bn.ho_ten}' thành công!"
            return False, f"Lỗi khi ghi dữ liệu: {self.store.loi_cuoi or 'không rõ nguyên nhân'}"
        except ValueError as e:
            return False, f"Lỗi cập nhật: {e}"

    def xoa(self, ma):
        """Xóa bệnh nhân khỏi hệ thống. Quyền: Chỉ admin."""
        bn = self.tim_theo_ma(ma)
        if not bn:
            return False, f"Không tìm thấy bệnh nhân có mã '{ma}'!"

        self._danh_sach.remove(bn)
        if self.luu_du_lieu():
            return True, f"Đã xóa bệnh nhân '{bn.ho_ten}' khỏi hệ thống!"
        return False, f"Lỗi khi cập nhật file: {self.store.loi_cuoi or 'không rõ nguyên nhân'}"
