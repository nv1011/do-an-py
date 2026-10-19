"""Cấu hình toàn hệ thống phòng khám (Giao diện & Nghiệp vụ)"""

TIEU_DE_APP = "Quản lý phòng khám"

# Cửa sổ chính
KICH_THUOC_CUA_SO = "1150x720"
KICH_THUOC_TOI_THIEU = (950, 620)

# Font
FONT_CHUNG = ("Segoe UI", 10)
FONT_TIEU_DE = ("Segoe UI", 12, "bold")

# Màu sắc giao diện
MAU_NEN = "#f1f1f1"
MAU_NHAN_MANH = "#cfe2f3"
MAU_LOI = "#c0392b"

# Thứ tự các tab trong Notebook
DANH_SACH_TAB = ["Bệnh nhân", "Lịch hẹn", "Phiếu khám", "Thống kê"]

# Từ điển học vị bác sĩ (mã 2 số -> tên viết tắt)
HOC_VI = {
    "01": "TS",
    "02": "ThS",
    "03": "BS"
}
hoc_vi = HOC_VI  # Alias tương thích ngược

# Cấu hình khung giờ và lịch hẹn
GIO_BAT_DAU_KHAM = "07:00"
GIO_KET_THUC_KHAM = "18:00"
BUOC_THOI_LUONG_PHUT = 15  # Bội số thời lượng tối thiểu

# Định nghĩa các buổi trực của bác sĩ
CA_TRUC = {
    "SANG": ("07:30", "11:30"),
    "CHIEU": ("13:30", "17:30")
}

# Các vai trò người dùng trong hệ thống
VAI_TRO_ADMIN = "admin"
VAI_TRO_LE_TAN = "le_tan"
DANH_SACH_VAI_TRO = [VAI_TRO_ADMIN, VAI_TRO_LE_TAN]