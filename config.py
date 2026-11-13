from pathlib import Path

HOC_VI = {"01": "TS", "02": "ThS", "03": "BS"}

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

API_DIA_CHI_URL = "https://tinhthanhpho.com/api/v1"
API_TIMEOUT_GIAY = 10

TEN_UNG_DUNG = "Quan ly lich kham phong kham"
DINH_DANG_NGAY = "%d/%m/%Y"
THOI_LUONG_KHAM_MAC_DINH = 30

VAI_TRO_ADMIN = "admin"
VAI_TRO_LE_TAN = "le_tan"
VAI_TRO_BAC_SI = "bac_si"

TIEU_DE_APP = "Quản lý phòng khám"

KICH_THUOC_CUA_SO = "1150x720"
KICH_THUOC_TOI_THIEU = (950, 620)

FONT_CHUNG = ("Segoe UI", 10)
FONT_TIEU_DE = ("Segoe UI", 12, "bold")

MAU_NEN = "#f1f1f1"
MAU_NHAN_MANH = "#cfe2f3"
MAU_LOI = "#c0392b"
MAU_NEN_LOI = "#fbeceb"
MAU_CHU_PHU = "#555555"
MAU_CHU_MO = "#777777"
MAU_VIEN = "#444444"
MAU_VIEN_CHON = "#2e6bb0"

# Font phụ
FONT_DAM = ("Segoe UI", 10, "bold")
FONT_TONG_TIEN = ("Segoe UI", 12, "bold")

# Cửa sổ đăng nhập
KICH_THUOC_DANG_NHAP = "640x560"

# Thẻ lịch hẹn (AppointmentCard)
THE_RONG = 215
THE_CAO = 130

# Biểu đồ Canvas (tab Thống kê)
BIEU_DO_CAO = 230
MAU_BIEU_DO_NEN = "#fcfcfb"
MAU_BIEU_DO_CHU = "#0b0b0b"
MAU_BIEU_DO_CHU_PHU = "#52514e"
MAU_BIEU_DO_LUOI = "#e3e2df"
MAU_BIEU_DO = [
    "#2a78d6",
    "#eb6834",
    "#1baf7a",
    "#eda100",
    "#e87ba4",
    "#008300",
    "#6250d6",
    "#e34948",
]

DANH_SACH_TAB = ["Bệnh nhân", "Lịch hẹn", "Phiếu khám", "Thống kê"]

GIO_BAT_DAU_KHAM = "07:00"
GIO_KET_THUC_KHAM = "18:00"
BUOC_THOI_LUONG_PHUT = 15

CA_TRUC = {"SANG": ("07:30", "11:30"), "CHIEU": ("13:30", "17:30")}

VAI_TRO_ADMIN = "admin"
VAI_TRO_LE_TAN = "le_tan"
DANH_SACH_VAI_TRO = [VAI_TRO_ADMIN, VAI_TRO_LE_TAN]


# ---------- Dữ liệu mẫu (dùng bởi services/tao_du_lieu_mau.py) ----------
FILE_TINH_THANH = DATA_DIR / "tinh_thanh.json"

SO_BENH_NHAN = 30
SO_BAC_SI = 8
SEED = None
SO_NGAY_DANG_KY = 60
SO_CA_MOI_TUAN = 3

# Khoảng giá trị các cặp số trong mã bác sĩ: HH CC YY SSS
HOC_VI_MIN, HOC_VI_MAX = 1, 3
CHUYEN_KHOA_MIN, CHUYEN_KHOA_MAX = 1, 10
NAM_VAO_LAM_MIN, NAM_VAO_LAM_MAX = 0, 26

TUOI_TOI_THIEU_BAC_SI = 25
NAM_SINH_SOM_NHAT_BAC_SI = 1961
# Khóa trùng với HOC_VI ở đầu file: 01 = TS, 02 = ThS, 03 = BS
LUONG_NEN = {"01": 23_000_000, "02": 19_000_000, "03": 16_000_000}

HO = [
    "Nguyễn",
    "Trần",
    "Lê",
    "Phạm",
    "Hoàng",
    "Huỳnh",
    "Phan",
    "Vũ",
    "Võ",
    "Đặng",
    "Bùi",
    "Đỗ",
    "Hồ",
    "Ngô",
    "Dương",
    "Lý",
]
TRONG_SO_HO = [30, 11, 10, 7, 5, 5, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2]
DEM_NAM = ["Văn", "Đức", "Minh", "Quang", "Quốc", "Anh", "Hữu", "Thanh", "Gia", "Xuân"]
DEM_NU = ["Thị", "Thị", "Thị", "Ngọc", "Thu", "Mỹ", "Thanh", "Hồng", "Kim", "Phương"]
TEN_NAM = [
    "An",
    "Bình",
    "Dũng",
    "Huy",
    "Khoa",
    "Long",
    "Nam",
    "Phúc",
    "Quân",
    "Sơn",
    "Thành",
    "Tuấn",
    "Vinh",
    "Hải",
    "Khải",
    "Hiếu",
    "Đạt",
    "Minh",
]
TEN_NU = [
    "Anh",
    "Châu",
    "Hà",
    "Linh",
    "Mai",
    "Ngân",
    "Lan",
    "Phương",
    "Trang",
    "Thảo",
    "Hương",
    "Yến",
    "Vy",
    "Oanh",
    "Nhung",
    "Diệp",
    "Hạnh",
    "Quỳnh",
]

DUONG = [
    "Lê Lợi",
    "Nguyễn Huệ",
    "Hai Bà Trưng",
    "Trần Hưng Đạo",
    "Lý Thường Kiệt",
    "Phan Chu Trinh",
    "Hùng Vương",
    "Nguyễn Trãi",
    "Điện Biên Phủ",
    "Cách Mạng Tháng 8",
    "Nguyễn Văn Linh",
    "Lạch Tray",
    "Kim Mã",
    "Cầu Giấy",
    "Nguyễn Tri Phương",
    "Trần Phú",
    "Hoàng Diệu",
    "Quang Trung",
    "Lê Duẩn",
]

DAU_SO = [
    "032",
    "033",
    "034",
    "035",
    "036",
    "037",
    "038",
    "039",
    "056",
    "058",
    "059",
    "070",
    "076",
    "077",
    "078",
    "079",
    "081",
    "082",
    "083",
    "084",
    "085",
    "086",
    "088",
    "089",
    "090",
    "091",
    "092",
    "093",
    "094",
    "096",
    "097",
    "098",
    "099",
]

# (tên bệnh, tuổi tối thiểu để có thể mắc)
TIEN_SU = [
    ("Viêm loét dạ dày", 18),
    ("Tăng huyết áp nhẹ", 40),
    ("Dị ứng hải sản", 0),
    ("Viêm xoang mãn tính", 10),
    ("Tiểu đường tuýp 2", 40),
    ("Hen suyễn", 0),
    ("Viêm da cơ địa", 0),
    ("Đau thắt lưng", 25),
    ("Rối loạn mỡ máu", 40),
]

NHOM_MAU = ["O", "A", "B", "AB"]
TRONG_SO_NHOM_MAU = [40, 27, 25, 8]

# Tên ca lấy từ CA_TRUC để không khai báo lại: T2_SANG, T2_CHIEU, T3_SANG, ...
TAT_CA_CA_LAM = [f"T{thu}_{ca}" for thu in range(2, 8) for ca in CA_TRUC]

# Dùng khi data/tinh_thanh.json bị xóa hoặc hỏng
DIA_CHI_DU_PHONG = {
    "Hà Nội": ["Phường Hoàn Kiếm", "Phường Ba Đình", "Phường Cầu Giấy"],
    "Đà Nẵng": ["Phường Hải Châu", "Phường Thanh Khê", "Phường Sơn Trà"],
    "TP.HCM": ["Phường Bến Thành", "Phường Sài Gòn", "Phường Tân Định"],
}
