"""Dịch vụ giả theo hợp đồng hàm (docs/hop_dong_ham.md) để thử giao diện."""
import calendar
import csv
import random
from datetime import date
from types import SimpleNamespace

from models.bac_si import BacSi
from services.json_store import JsonStore
from utils.validators import la_ngay_hop_le

CHAN_DOAN = ["Cảm cúm", "Viêm họng cấp", "Viêm dạ dày", "Tăng huyết áp", "Viêm mũi dị ứng",
             "Sâu răng", "Cận thị", "Rối loạn tiêu hóa"]
THUOC = [("Paracetamol 500mg", "Viên"), ("Omeprazole 20mg", "Viên"), ("Cetirizine 10mg", "Viên"),
         ("Vitamin C 500mg", "Viên")]


def doc_ngay_vn(chuoi):
    """'15-05-1990' hoặc '15/05/1990' -> (True, date) hoặc (False, None)."""
    try:
        ngay, thang, nam = (int(p) for p in str(chuoi).strip().replace("/", "-").split("-"))
    except ValueError:
        return False, None
    if not la_ngay_hop_le(ngay, thang, nam):
        return False, None
    return True, date(nam, thang, ngay)


def _doi_ngay(gia_tri):
    return gia_tri if gia_tri is None or isinstance(gia_tri, date) else date.fromisoformat(gia_tri)


class PhieuKhamGia:
    """Cùng thuộc tính với PhieuKham trong docs/thiet_ke_lop.md."""

    def __init__(self, d):
        self.ma_phieu_kham = d["ma_phieu_kham"]
        self.ma_lich_hen = d.get("ma_lich_hen")
        self.ma_benh_nhan = d["ma_benh_nhan"]
        self.ma_bac_si = d["ma_bac_si"]
        self.ngay_kham = _doi_ngay(d["ngay_kham"])
        self.trieu_chung = d.get("trieu_chung", "")
        self.chan_doan = d.get("chan_doan", "")
        self.danh_sach_dich_vu = [dict(x) for x in d.get("danh_sach_dich_vu", [])]
        self.don_thuoc = [dict(x) for x in d.get("don_thuoc", [])]
        self.loi_dan = d.get("loi_dan", "")
        self.ngay_tai_kham = _doi_ngay(d.get("ngay_tai_kham"))
        self.trang_thai_kham = d.get("trang_thai_kham", "Dang_kham")
        self.trang_thai_thanh_toan = d.get("trang_thai_thanh_toan", "Chua_thanh_toan")

    @property
    def tong_tien(self):
        return sum(x["don_gia"] * x["so_luong"] for x in self.danh_sach_dich_vu)


class QuanLyBacSiGia:
    def __init__(self, store=None):
        self._ds = []
        for d in (store or JsonStore()).doc_file("bac_si.json"):
            try:
                self._ds.append(BacSi.from_dict(d))
            except (KeyError, ValueError):
                continue

    def lay_tat_ca(self):
        return list(self._ds)

    def tim_theo_ma(self, ma):
        return next((b for b in self._ds if b.ma_dinh_danh == ma), None)


class QuanLyLichHenGia:
    def __init__(self, store=None):
        self._ds = []
        for d in (store or JsonStore()).doc_file("lich_hen.json"):
            lich = SimpleNamespace(**d)
            lich.ngay_hen = date.fromisoformat(d["ngay_hen"])
            self._ds.append(lich)

    def lay_tat_ca(self):
        return list(self._ds)


def _sinh_phieu(store, dich_vu, hom_nay, so_bat_dau):
    """Sinh phiếu khám mẫu từ năm trước đến hôm nay để có số liệu vẽ biểu đồ."""
    rd = random.Random(2026)
    ds_bn = [d["ma_dinh_danh"] for d in store.doc_file("benh_nhan.json")]
    ds_bs = [d["ma_dinh_danh"] for d in store.doc_file("bac_si.json")]
    if not (ds_bn and ds_bs and dich_vu):
        return []
    ma_dv = list(dich_vu)
    ket_qua, ngay, dem = [], date(hom_nay.year - 1, 1, 1), 0
    while ngay <= hom_nay:
        dem += 1
        if ngay.weekday() != 6:
            so_phieu = rd.choice((0, 1, 1, 2)) + (1 if rd.random() < dem / 900 else 0)
            for _ in range(so_phieu):
                ma_bs = rd.choice(ds_bs)
                chinh = [m for m in ma_dv if dich_vu[m]["ma_chuyen_khoa"] == ma_bs[2:4]] or ma_dv[:1]
                chon = [rd.choice(chinh)]
                them = rd.choice(ma_dv)
                if rd.random() < 0.35 and them not in chon:
                    chon.append(them)
                tuoi = (hom_nay - ngay).days
                dang_kham = tuoi <= 1 and rd.random() < 0.5
                thuoc = rd.choice(THUOC)
                ket_qua.append(PhieuKhamGia({
                    "ma_phieu_kham": f"PK{so_bat_dau + len(ket_qua):03d}",
                    "ma_lich_hen": None,
                    "ma_benh_nhan": rd.choice(ds_bn),
                    "ma_bac_si": ma_bs,
                    "ngay_kham": ngay,
                    "trieu_chung": "Mệt mỏi, khó chịu",
                    "chan_doan": "" if dang_kham else rd.choice(CHAN_DOAN),
                    "danh_sach_dich_vu": [
                        {"ma_dich_vu": m, "ten_dich_vu": dich_vu[m]["ten_dich_vu"],
                         "don_gia": dich_vu[m]["don_gia"], "so_luong": 1} for m in chon],
                    "don_thuoc": [] if dang_kham else [
                        {"ten_thuoc": thuoc[0], "don_vi": thuoc[1], "so_luong": 10,
                         "cach_dung": "Uống 1 viên sau ăn"}],
                    "loi_dan": "" if dang_kham else "Nghỉ ngơi, uống nhiều nước",
                    "ngay_tai_kham": None,
                    "trang_thai_kham": "Dang_kham" if dang_kham else "Hoan_thanh",
                    "trang_thai_thanh_toan": "Da_thanh_toan" if not dang_kham and (
                        tuoi > 2 and rd.random() < 0.95 or tuoi <= 2 and rd.random() < 0.5)
                    else "Chua_thanh_toan",
                }))
        ngay = date.fromordinal(ngay.toordinal() + 1)
    for pk in ket_qua[-3:]:     # luôn có vài phiếu đang khám để thử
        pk.trang_thai_kham, pk.trang_thai_thanh_toan = "Dang_kham", "Chua_thanh_toan"
        pk.chan_doan, pk.don_thuoc, pk.loi_dan = "", [], ""
    return ket_qua


class QuanLyPhieuKhamGia:
    """Giống hợp đồng QuanLyPhieuKham; thêm lay_dich_vu() (cần hỏi A)."""

    def __init__(self, store=None, hom_nay=None, sinh_them=True):
        store = store or JsonStore()
        self.hom_nay = hom_nay or date.today()
        self._dich_vu = {d["ma_dich_vu"]: d for d in store.doc_file("dich_vu.json")}
        self._ds = [PhieuKhamGia(d) for d in store.doc_file("phieu_kham.json")]
        if sinh_them:
            self._ds += _sinh_phieu(store, self._dich_vu, self.hom_nay, self._so_tiep_theo())

    def _so_tiep_theo(self):
        return max((int(p.ma_phieu_kham[2:]) for p in self._ds), default=0) + 1

    def lay_tat_ca(self):
        return list(self._ds)

    def lay_dich_vu(self):
        return sorted(self._dich_vu.values(), key=lambda d: d["ma_dich_vu"])

    def tim_theo_ma(self, ma):
        return next((p for p in self._ds if p.ma_phieu_kham == ma), None)

    def lay_theo_benh_nhan(self, ma_bn):
        return [p for p in self._ds if p.ma_benh_nhan == ma_bn]

    def sinh_ma_moi(self):
        return f"PK{self._so_tiep_theo():03d}"

    def tao_phieu_kham(self, du_lieu):
        ma_bn, ma_bs = du_lieu.get("ma_benh_nhan"), du_lieu.get("ma_bac_si")
        ma_lh = du_lieu.get("ma_lich_hen") or None
        trieu_chung = (du_lieu.get("trieu_chung") or "").strip()
        if not ma_bn:
            return False, "Chưa chọn bệnh nhân!", None
        if not ma_bs:
            return False, "Chưa chọn bác sĩ!", None
        if not trieu_chung:
            return False, "Triệu chứng không được để trống!", None
        if ma_lh and any(p.ma_lich_hen == ma_lh for p in self._ds):
            return False, f"Lịch hẹn '{ma_lh}' đã có phiếu khám!", None
        pk = PhieuKhamGia({
            "ma_phieu_kham": self.sinh_ma_moi(), "ma_lich_hen": ma_lh, "ma_benh_nhan": ma_bn,
            "ma_bac_si": ma_bs, "ngay_kham": self.hom_nay, "trieu_chung": trieu_chung})
        self._ds.append(pk)
        return True, f"Đã tạo phiếu khám {pk.ma_phieu_kham}!", pk

    def _phieu_dang_kham(self, ma_pk):
        pk = self.tim_theo_ma(ma_pk)
        if not pk:
            return None, f"Không tìm thấy phiếu khám '{ma_pk}'!"
        if pk.trang_thai_kham != "Dang_kham":
            return None, "Phiếu đã hoàn tất khám, không sửa được!"
        return pk, ""

    def them_dich_vu(self, ma_pk, ma_dv, so_luong=1):
        pk, loi = self._phieu_dang_kham(ma_pk)
        if not pk:
            return False, loi
        dv = self._dich_vu.get(ma_dv)
        if not dv:
            return False, f"Không tìm thấy dịch vụ '{ma_dv}'!"
        if not isinstance(so_luong, int) or so_luong <= 0:
            return False, "Số lượng phải là số nguyên dương!"
        for x in pk.danh_sach_dich_vu:
            if x["ma_dich_vu"] == ma_dv:
                x["so_luong"] += so_luong
                return True, f"Đã cộng thêm {so_luong} '{dv['ten_dich_vu']}'."
        pk.danh_sach_dich_vu.append({"ma_dich_vu": ma_dv, "ten_dich_vu": dv["ten_dich_vu"],
                                     "don_gia": dv["don_gia"], "so_luong": so_luong})
        return True, f"Đã thêm dịch vụ '{dv['ten_dich_vu']}'."

    def xoa_dich_vu(self, ma_pk, ma_dv):
        pk, loi = self._phieu_dang_kham(ma_pk)
        if not pk:
            return False, loi
        for x in pk.danh_sach_dich_vu:
            if x["ma_dich_vu"] == ma_dv:
                pk.danh_sach_dich_vu.remove(x)
                return True, f"Đã bỏ dịch vụ '{x['ten_dich_vu']}'."
        return False, "Dịch vụ này chưa có trong phiếu!"

    def hoan_tat_kham(self, ma_pk, chan_doan, loi_dan, don_thuoc, ngay_tai_kham=None):
        pk, loi = self._phieu_dang_kham(ma_pk)
        if not pk:
            return False, loi
        chan_doan = (chan_doan or "").strip()
        if not chan_doan:
            return False, "Chẩn đoán không được để trống khi hoàn tất khám!"
        thuoc = []
        for t in don_thuoc or []:
            ten, sl = (t.get("ten_thuoc") or "").strip(), t.get("so_luong")
            if not ten:
                return False, "Tên thuốc không được để trống!"
            if not isinstance(sl, int) or sl <= 0:
                return False, f"Số lượng thuốc '{ten}' phải là số nguyên dương!"
            thuoc.append({"ten_thuoc": ten, "don_vi": (t.get("don_vi") or "").strip(),
                          "so_luong": sl, "cach_dung": (t.get("cach_dung") or "").strip()})
        tai_kham = None
        if ngay_tai_kham:
            ok, tai_kham = doc_ngay_vn(ngay_tai_kham)
            if not ok:
                return False, "Ngày tái khám không hợp lệ!"
            if tai_kham < pk.ngay_kham:
                return False, "Ngày tái khám không được trước ngày khám!"
        pk.chan_doan, pk.loi_dan = chan_doan, (loi_dan or "").strip()
        pk.don_thuoc, pk.ngay_tai_kham = thuoc, tai_kham
        pk.trang_thai_kham = "Hoan_thanh"
        return True, f"Đã hoàn tất khám phiếu {ma_pk}!"

    def thanh_toan(self, ma_pk):
        pk = self.tim_theo_ma(ma_pk)
        if not pk:
            return False, f"Không tìm thấy phiếu khám '{ma_pk}'!", 0.0
        if pk.trang_thai_kham != "Hoan_thanh":
            return False, "Phải hoàn tất khám trước khi thanh toán!", 0.0
        if pk.trang_thai_thanh_toan == "Da_thanh_toan":
            return False, "Phiếu này đã thanh toán!", 0.0
        if pk.tong_tien <= 0:
            return False, "Phiếu chưa có dịch vụ nào để thanh toán!", 0.0
        pk.trang_thai_thanh_toan = "Da_thanh_toan"
        return True, f"Đã thu {pk.tong_tien:,.0f} đ cho phiếu {ma_pk}!".replace(",", "."), float(pk.tong_tien)


class ThongKeGia:
    """Giống hợp đồng ThongKe; lượt khám: phiếu Hoan_thanh, doanh thu: phiếu Da_thanh_toan."""

    def __init__(self, ql_phieu, ql_bac_si=None, store=None):
        store = store or JsonStore()
        self.ql_phieu = ql_phieu
        self.ql_bac_si = ql_bac_si or QuanLyBacSiGia(store)
        self._ten_khoa = {d["ma_chuyen_khoa"]: d["ten_chuyen_khoa"]
                          for d in store.doc_file("chuyen_khoa.json")}

    def _ten_bac_si(self, ma):
        bs = self.ql_bac_si.tim_theo_ma(ma)
        return f"{bs.hoc_vi}. {bs.ho_ten}" if bs else ma

    def _ten_khoa_cua(self, ma_bs):
        return self._ten_khoa.get(ma_bs[2:4], "Khác")

    def _loc(self, tu_ngay, den_ngay, **dieu_kien):
        return [p for p in self.ql_phieu.lay_tat_ca() if tu_ngay <= p.ngay_kham <= den_ngay
                and all(getattr(p, k) == v for k, v in dieu_kien.items())]

    def thong_ke_theo_ngay(self, nam, thang):
        so_ngay = calendar.monthrange(nam, thang)[1]
        ket_qua = {n: {"luot_kham": 0, "doanh_thu": 0.0} for n in range(1, so_ngay + 1)}
        for p in self._loc(date(nam, thang, 1), date(nam, thang, so_ngay), trang_thai_kham="Hoan_thanh"):
            ket_qua[p.ngay_kham.day]["luot_kham"] += 1
        for p in self._loc(date(nam, thang, 1), date(nam, thang, so_ngay), trang_thai_thanh_toan="Da_thanh_toan"):
            ket_qua[p.ngay_kham.day]["doanh_thu"] += p.tong_tien
        return ket_qua

    def thong_ke_theo_thang(self, nam):
        ket_qua = {t: {"luot_kham": 0, "doanh_thu": 0.0} for t in range(1, 13)}
        dau, cuoi = date(nam, 1, 1), date(nam, 12, 31)
        for p in self._loc(dau, cuoi, trang_thai_kham="Hoan_thanh"):
            ket_qua[p.ngay_kham.month]["luot_kham"] += 1
        for p in self._loc(dau, cuoi, trang_thai_thanh_toan="Da_thanh_toan"):
            ket_qua[p.ngay_kham.month]["doanh_thu"] += p.tong_tien
        return ket_qua

    def thong_ke_doanh_thu_theo_thang(self, nam):
        return {t: v["doanh_thu"] for t, v in self.thong_ke_theo_thang(nam).items()}

    def thong_ke_luot_kham_theo_bac_si(self, tu_ngay, den_ngay):
        dem = {self._ten_bac_si(b.ma_dinh_danh): 0 for b in self.ql_bac_si.lay_tat_ca()}
        for p in self._loc(tu_ngay, den_ngay, trang_thai_kham="Hoan_thanh"):
            ten = self._ten_bac_si(p.ma_bac_si)
            dem[ten] = dem.get(ten, 0) + 1
        return dict(sorted(dem.items(), key=lambda kv: -kv[1]))

    def thong_ke_co_cau_chuyen_khoa(self, tu_ngay, den_ngay):
        dem = {}
        for p in self._loc(tu_ngay, den_ngay, trang_thai_kham="Hoan_thanh"):
            ten = self._ten_khoa_cua(p.ma_bac_si)
            dem[ten] = dem.get(ten, 0) + 1
        return dict(sorted(dem.items(), key=lambda kv: -kv[1]))

    def xuat_bao_cao_csv(self, duong_dan, tu_ngay, den_ngay):
        if tu_ngay > den_ngay:
            return False, "Khoảng ngày không hợp lệ!"
        ds = sorted(self._loc(tu_ngay, den_ngay), key=lambda p: (p.ngay_kham, p.ma_phieu_kham))
        luot = sum(1 for p in ds if p.trang_thai_kham == "Hoan_thanh")
        thu = sum(p.tong_tien for p in ds if p.trang_thai_thanh_toan == "Da_thanh_toan")
        try:
            with open(duong_dan, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["Mã phiếu", "Ngày khám", "Mã bệnh nhân", "Bác sĩ", "Chuyên khoa",
                            "Trạng thái khám", "Thanh toán", "Tổng tiền"])
                for p in ds:
                    w.writerow([p.ma_phieu_kham, p.ngay_kham.strftime("%d/%m/%Y"), p.ma_benh_nhan,
                                self._ten_bac_si(p.ma_bac_si), self._ten_khoa_cua(p.ma_bac_si),
                                p.trang_thai_kham, p.trang_thai_thanh_toan, int(p.tong_tien)])
                w.writerow([])
                w.writerow(["Tổng lượt khám", luot])
                w.writerow(["Tổng doanh thu", int(thu)])
        except OSError as e:
            return False, f"Không ghi được file: {e}"
        return True, f"Đã xuất {len(ds)} phiếu khám ra file {duong_dan}"
