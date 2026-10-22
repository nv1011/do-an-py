hoc_vi = { "01": "TS", "02": "ThS", "03": "BS" }

from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent
#  __file__: bien co san cua py = chua file path cua running file (o day la config.py)
# boc string do thanh obj path
# resolve(): bien doi thanh file path tuyet doi (remove .. and .)
# .parent: lay folder cha cua file do
DATA_DIR=BASE_DIR/"data"
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

API_DIA_CHI_URL = "https://provinces.open-api.vn/api/"
API_TIMEOUT_GIAY = 10

TEN_UNG_DUNG = "Quan ly lich kham phong kham"
DINH_DANG_NGAY = "%d/%m/%Y"
THOI_LUONG_KHAM_MAC_DINH = 30

VAI_TRO_ADMIN = "admin"
VAI_TRO_LE_TAN = "le_tan"
