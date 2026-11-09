from datetime import date, datetime
from models.phieu_kham import PhieuKham
from services.json_store import JsonStore
from config import FILE_PHIEU_KHAM, FILE_DICH_VU
from utils.validators import la_ngay_hop_le


class QuanLyPhieuKham:
    """Quản lý danh sách phiếu khám bệnh, điều phối cận lâm sàng, đơn thuốc và thanh toán."""

    def __init__(self, json_store=None, ten_file=FILE_PHIEU_KHAM, quan_ly_dich_vu=None):
        """Khởi tạo dịch vụ quản lý phiếu khám.

        Tham số:
            json_store (JsonStore | None): Bộ lưu trữ JsonStore.
            ten_file (Path | str): Đường dẫn file JSON phiếu khám.
            quan_ly_dich_vu: Danh mục dịch vụ hoặc service để lấy giá niêm yết.
        """
        self.store = json_store or JsonStore()
        self.ten_file = ten_file
        self.quan_ly_dich_vu = quan_ly_dich_vu
        self._danh_sach = []
        self._bang_dich_vu = {}
        self.nap_du_lieu()

    def nap_du_lieu(self):
        """Đọc danh sách phiếu khám và danh mục dịch vụ từ file JSON vào bộ nhớ."""
        # 1. Đọc danh mục dịch vụ để tra cứu đơn giá khi thêm dịch vụ
        raw_dv = self.store.doc_file(FILE_DICH_VU)
        self._bang_dich_vu = {d["ma_dich_vu"]: d for d in raw_dv}

        # 2. Đọc phiếu khám
        danh_sach_raw = self.store.doc_file(self.ten_file)
        self._danh_sach = []
        for d in danh_sach_raw:
            try:
                self._danh_sach.append(PhieuKham.from_dict(d))
            except (KeyError, ValueError):
                continue

    def luu_du_lieu(self):
        """Ghi danh sách phiếu khám hiện tại ra file JSON theo cơ chế Atomic Write."""
        du_lieu_json = [pk.to_dict() for pk in self._danh_sach]
        return self.store.ghi_file(self.ten_file, du_lieu_json)

    def lay_tat_ca(self):
        """Trả về toàn bộ danh sách phiếu khám bệnh."""
        return list(self._danh_sach)

    def tim_theo_ma(self, ma):
        """Tìm phiếu khám theo mã định danh (VD: 'PK001')."""
        if not ma:
            return None
        ma_clean = str(ma).strip().upper()
        for pk in self._danh_sach:
            if pk.ma_phieu_kham.upper() == ma_clean:
                return pk
        return None

    def lay_theo_benh_nhan(self, ma_bn):
        """Lấy toàn bộ lịch sử các phiếu khám của một bệnh nhân."""
        if not ma_bn:
            return []
        ma_clean = str(ma_bn).strip()
        return [pk for pk in self._danh_sach if pk.ma_benh_nhan == ma_clean]

    def lay_theo_bac_si(self, ma_bs):
        """Lấy danh sách các phiếu khám do bác sĩ phụ trách (phục vụ vai trò bác sĩ)."""
        if not ma_bs:
            return []
        ma_clean = str(ma_bs).strip()
        return [pk for pk in self._danh_sach if pk.ma_bac_si == ma_clean]

    def sinh_ma_moi(self):
        """Sinh mã phiếu khám tiếp theo tự động có dạng PK001, PK002..."""
        if not self._danh_sach:
            return "PK001"
        cac_so = []
        for pk in self._danh_sach:
            try:
                cac_so.append(int(pk.ma_phieu_kham[2:]))
            except (ValueError, IndexError):
                continue
        so_tiep = max(cac_so, default=0) + 1
        return f"PK{so_tiep:03d}"

    def lay_dich_vu(self):
        """Trả về danh sách dịch vụ y tế để giao diện chọn (danh mục niêm yết)."""
        return sorted(self._bang_dich_vu.values(), key=lambda d: d.get("ma_dich_vu", ""))

    def tao_phieu_kham(self, du_lieu):
        """Khởi tạo phiếu khám ban đầu (từ lịch hẹn hoặc khám vãng lai).

        Trạng thái ban đầu: 'Dang_kham', 'Chua_thanh_toan'.
        Quyền: admin, le_tan, bac_si.

        Tham số:
            du_lieu (dict): Gồm ma_benh_nhan, ma_bac_si, trieu_chung, [ma_lich_hen], [ngay_kham].

        Trả về:
            tuple[bool, str, PhieuKham | None]
        """
        ma_bn = str(du_lieu.get("ma_benh_nhan") or "").strip()
        ma_bs = str(du_lieu.get("ma_bac_si") or "").strip()
        trieu_chung = str(du_lieu.get("trieu_chung") or "").strip()
        ma_lh = du_lieu.get("ma_lich_hen")
        ma_lh = str(ma_lh).strip() if ma_lh else None

        if not ma_bn:
            return False, "Chưa chọn bệnh nhân!", None
        if not ma_bs:
            return False, "Chưa chọn bác sĩ!", None
        if not trieu_chung:
            return False, "Triệu chứng ban đầu không được để trống!", None

        # Kiểm tra trùng: nếu tạo từ lịch hẹn, lịch hẹn này đã có phiếu khám chưa
        if ma_lh and any(pk.ma_lich_hen == ma_lh for pk in self._danh_sach):
            return False, f"Lịch hẹn '{ma_lh}' đã được lập phiếu khám từ trước!", None

        # Xử lý ngày khám
        ngay_kham = du_lieu.get("ngay_kham") or date.today()
        if isinstance(ngay_kham, str):
            for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    ngay_kham = datetime.strptime(ngay_kham.strip(), fmt).date()
                    break
                except ValueError:
                    continue

        ma_pk = du_lieu.get("ma_phieu_kham") or self.sinh_ma_moi()

        try:
            phieu_moi = PhieuKham(
                ma_phieu_kham=ma_pk,
                ma_benh_nhan=ma_bn,
                ma_bac_si=ma_bs,
                trieu_chung=trieu_chung,
                ma_lich_hen=ma_lh,
                ngay_kham=ngay_kham,
                trang_thai_kham="Dang_kham",
                trang_thai_thanh_toan="Chua_thanh_toan",
            )
            self._danh_sach.append(phieu_moi)
            if self.luu_du_lieu():
                return True, f"Tạo phiếu khám {ma_pk} thành công!", phieu_moi
            self._danh_sach.pop()
            return False, f"Lỗi lưu file: {self.store.loi_cuoi}", None
        except ValueError as e:
            return False, str(e), None

    def them_dich_vu(self, ma_pk, ma_dv, so_luong=1):
        """Thêm dịch vụ kỹ thuật / cận lâm sàng vào phiếu khám.

        Chụp lại đơn giá niêm yết tại thời điểm thêm.
        Quyền: admin, le_tan, bac_si.

        Tham số:
            ma_pk (str): Mã phiếu khám.
            ma_dv (str): Mã dịch vụ y tế.
            so_luong (int): Số lượng chỉ định (mặc định 1).

        Trả về:
            tuple[bool, str]
        """
        pk = self.tim_theo_ma(ma_pk)
        if not pk:
            return False, f"Không tìm thấy phiếu khám '{ma_pk}'!"

        if pk.trang_thai_kham != "Dang_kham":
            return False, "Phiếu khám đã hoàn tất, không thể chỉ định thêm dịch vụ!"

        ma_dv_clean = str(ma_dv or "").strip()
        dv = self._bang_dich_vu.get(ma_dv_clean)
        if not dv:
            return False, f"Không tìm thấy dịch vụ y tế '{ma_dv_clean}'!"

        if not isinstance(so_luong, int) or so_luong <= 0:
            return False, "Số lượng chỉ định phải là số nguyên dương!"

        # Nếu dịch vụ đã có trong danh sách -> cộng dồn số lượng
        for x in pk.danh_sach_dich_vu:
            if x.get("ma_dich_vu") == ma_dv_clean:
                x["so_luong"] = int(x.get("so_luong", 1)) + so_luong
                if self.luu_du_lieu():
                    return True, f"Đã tăng thêm {so_luong} '{dv.get('ten_dich_vu')}'."
                return False, f"Lỗi lưu file: {self.store.loi_cuoi}"

        # Thêm mới vào danh sách
        pk.danh_sach_dich_vu.append({
            "ma_dich_vu": ma_dv_clean,
            "ten_dich_vu": dv.get("ten_dich_vu", ""),
            "don_gia": float(dv.get("don_gia", 0)),
            "so_luong": so_luong,
        })

        if self.luu_du_lieu():
            return True, f"Đã thêm dịch vụ '{dv.get('ten_dich_vu')}' vào phiếu khám."
        return False, f"Lỗi lưu file: {self.store.loi_cuoi}"

    def xoa_dich_vu(self, ma_pk, ma_dv):
        """Xóa dịch vụ đã chọn khỏi phiếu khám.

        Quyền: admin, le_tan, bac_si.
        """
        pk = self.tim_theo_ma(ma_pk)
        if not pk:
            return False, f"Không tìm thấy phiếu khám '{ma_pk}'!"

        if pk.trang_thai_kham != "Dang_kham":
            return False, "Phiếu khám đã hoàn tất, không thể xóa dịch vụ!"

        ma_dv_clean = str(ma_dv or "").strip()
        danh_sach_moi = [x for x in pk.danh_sach_dich_vu if x.get("ma_dich_vu") != ma_dv_clean]
        if len(danh_sach_moi) == len(pk.danh_sach_dich_vu):
            return False, f"Dịch vụ '{ma_dv_clean}' chưa có trong phiếu khám!"

        pk.danh_sach_dich_vu = danh_sach_moi
        if self.luu_du_lieu():
            return True, f"Đã bỏ dịch vụ '{ma_dv_clean}' khỏi phiếu khám."
        return False, f"Lỗi lưu file: {self.store.loi_cuoi}"

    def hoan_tat_kham(self, ma_pk, chan_doan, loi_dan, don_thuoc, ngay_tai_kham=None, nguoi_thuc_hien=None):
        """Hoàn tất quá trình khám bệnh, chẩn đoán, kê đơn thuốc và hẹn tái khám.

        Chuyển trang_thai_kham sang 'Hoan_thanh'.
        Quyền: admin, bac_si (Lễ tân không có quyền).
        Nếu là vai trò bác sĩ: chỉ được hoàn tất phiếu khám do chính mình phụ trách.

        Tham số:
            ma_pk (str): Mã phiếu khám.
            chan_doan (str): Kết luận bệnh lý (bắt buộc).
            loi_dan (str): Dặn dò dùng thuốc / sinh hoạt.
            don_thuoc (list[dict]): Danh sách thuốc [{'ten_thuoc', 'don_vi', 'so_luong', 'cach_dung'}].
            ngay_tai_kham (str | date | None): Ngày hẹn tái khám (định dạng DD-MM-YYYY hoặc YYYY-MM-DD).
            nguoi_thuc_hien (dict | str | None): Thông tin người gọi thao tác để kiểm tra quyền.

        Trả về:
            tuple[bool, str]
        """
        pk = self.tim_theo_ma(ma_pk)
        if not pk:
            return False, f"Không tìm thấy phiếu khám '{ma_pk}'!"

        if pk.trang_thai_kham == "Hoan_thanh":
            return False, "Phiếu khám này đã hoàn tất trước đó!"

        # Kiểm tra phân quyền nếu có truyền thông tin người thực hiện
        if isinstance(nguoi_thuc_hien, dict):
            vai_tro = nguoi_thuc_hien.get("vai_tro")
            ma_bs = nguoi_thuc_hien.get("ma_bac_si")
            if vai_tro == "le_tan":
                return False, "Quyền bị từ chối: Lễ tân không có quyền chẩn đoán và hoàn tất khám bệnh!"
            if vai_tro == "bac_si" and ma_bs and pk.ma_bac_si != ma_bs:
                return False, "Quyền bị từ chối: Bác sĩ chỉ được hoàn tất phiếu khám do chính mình phụ trách!"

        chan_doan_clean = str(chan_doan or "").strip()
        if not chan_doan_clean:
            return False, "Chẩn đoán bệnh không được để trống khi hoàn tất khám!"

        # Kiểm tra tính hợp lệ của đơn thuốc
        don_thuoc_chuan = []
        for t in (don_thuoc or []):
            ten = str(t.get("ten_thuoc") or "").strip()
            sl = t.get("so_luong")
            if not ten:
                return False, "Tên thuốc trong đơn không được để trống!"
            try:
                sl = int(sl)
            except (ValueError, TypeError):
                return False, f"Số lượng thuốc '{ten}' không hợp lệ!"
            if sl <= 0:
                return False, f"Số lượng thuốc '{ten}' phải là số nguyên dương!"

            don_thuoc_chuan.append({
                "ten_thuoc": ten,
                "don_vi": str(t.get("don_vi") or "").strip(),
                "so_luong": sl,
                "cach_dung": str(t.get("cach_dung") or "").strip(),
            })

        # Kiểm tra ngày tái khám nếu có
        tai_kham_date = None
        if ngay_tai_kham:
            if isinstance(ngay_tai_kham, str):
                parsed = False
                for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
                    try:
                        tai_kham_date = datetime.strptime(ngay_tai_kham.strip(), fmt).date()
                        parsed = True
                        break
                    except ValueError:
                        continue
                if not parsed:
                    return False, "Ngày tái khám không đúng định dạng (DD-MM-YYYY hoặc YYYY-MM-DD)!"
            elif isinstance(ngay_tai_kham, date):
                tai_kham_date = ngay_tai_kham

            if tai_kham_date and tai_kham_date < pk.ngay_kham:
                return False, "Ngày tái khám không thể trước ngày khám bệnh!"

        pk.chan_doan = chan_doan_clean
        pk.loi_dan = str(loi_dan or "").strip()
        pk.don_thuoc = don_thuoc_chuan
        pk.ngay_tai_kham = tai_kham_date
        pk.trang_thai_kham = "Hoan_thanh"

        if self.luu_du_lieu():
            return True, f"Đã hoàn tất ca khám cho phiếu {ma_pk}!"
        return False, f"Lỗi lưu file: {self.store.loi_cuoi}"

    def thanh_toan(self, ma_pk):
        """Xác nhận bệnh nhân đã thanh toán viện phí.

        Chuyển trang_thai_thanh_toan sang 'Da_thanh_toan'.
        Quyền: admin, le_tan (Bác sĩ không có quyền).

        Tham số:
            ma_pk (str): Mã phiếu khám.

        Trả về:
            tuple[bool, str, float]: (Thành công, Thông điệp, Tổng tiền đã thu).
        """
        pk = self.tim_theo_ma(ma_pk)
        if not pk:
            return False, f"Không tìm thấy phiếu khám '{ma_pk}'!", 0.0

        if pk.trang_thai_kham != "Hoan_thanh":
            return False, "Phiếu khám chưa hoàn tất chuyên môn, chưa thể thanh toán!", 0.0

        if pk.trang_thai_thanh_toan == "Da_thanh_toan":
            return False, f"Phiếu khám '{ma_pk}' đã được thanh toán từ trước!", 0.0

        tong_tien = pk.tong_tien
        if tong_tien <= 0:
            return False, "Phiếu khám chưa có dịch vụ nào để tính tiền thanh toán!", 0.0

        pk.trang_thai_thanh_toan = "Da_thanh_toan"
        if self.luu_du_lieu():
            return True, f"Thanh toán thành công {tong_tien:,.0f} đ cho phiếu {ma_pk}!", float(tong_tien)
        return False, f"Lỗi lưu file: {self.store.loi_cuoi}", 0.0
