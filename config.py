from pathlib import Path

hoc_vi = {"01": "TS", "02": "ThS", "03": "BS"}

hoc_vi = HOC_VI  # Alias tương thích ngược

BASE_DIR = Path(__file__).resolve().parent
#  __file__: bien co san cua py = chua file path cua running file (o day la config.py)
# boc string do thanh obj path
# resolve(): bien doi thanh file path tuyet doi (remove .. and .)
# .parent: lay folder cha cua file do
DATA_DIR = BASE_DIR / "data"
# '/' tren path nghia la noi them 1 duong dan
BACKUP_DIR = BASE_DIR / "backup"

FILE_BENH_NHAN = DATA_DIR / "benh_nhan.json"
FILE_BAC_SI = DATA_DIR / "bac_si.json"
FILE_CHUYEN_KHOA = DATA_DIR / "chuyen_khoa.json"
FILE_DICH_VU = DATA_DIR / "dich_vu.json"
FILE_LICH_HEN = DATA_DIR / "lich_hen.json"
FILE_PHIEU_KHAM = DATA_DIR / "phieu_kham.json"
FILE_TAI_KHOAN = DATA_DIR / "tai_khoan.json"
FILE_DIA_CHI = DATA_DIR / "dia_chi.json"

API_DIA_CHI_URL = "https://tinhthanhpho.com/api/v1"
API_TIMEOUT_GIAY = 10

TEN_UNG_DUNG = "Quan ly lich kham phong kham"
DINH_DANG_NGAY = "%d/%m/%Y"
THOI_LUONG_KHAM_MAC_DINH = 30

VAI_TRO_ADMIN = "admin"
VAI_TRO_LE_TAN = "le_tan"

TIEU_DE_APP = "Quản lý phòng khám"

KICH_THUOC_CUA_SO = "1150x720"
KICH_THUOC_TOI_THIEU = (950, 620)

FONT_CHUNG = ("Segoe UI", 10)
FONT_TIEU_DE = ("Segoe UI", 12, "bold")

MAU_NEN = "#f1f1f1"
MAU_NHAN_MANH = "#cfe2f3"
MAU_LOI = "#c0392b"

DANH_SACH_TAB = ["Bệnh nhân", "Lịch hẹn", "Phiếu khám", "Thống kê"]

GIO_BAT_DAU_KHAM = "07:00"
GIO_KET_THUC_KHAM = "18:00"
BUOC_THOI_LUONG_PHUT = 15

CA_TRUC = {
    "SANG": ("07:30", "11:30"),
    "CHIEU": ("13:30", "17:30")
}

VAI_TRO_ADMIN = "admin"
VAI_TRO_LE_TAN = "le_tan"
DANH_SACH_VAI_TRO = [VAI_TRO_ADMIN, VAI_TRO_LE_TAN]