"""Danh sách tỉnh/thành và phường/xã cho form."""

TINH_MAU = ["Hà Nội", "Đà Nẵng", "TP.HCM", "Hải Phòng", "Cần Thơ"]
XA_MAU = {
    "Hà Nội": ["Phường Hoàn Kiếm", "Phường Ba Đình", "Phường Cầu Giấy"],
    "Đà Nẵng": ["Phường Hải Châu", "Phường Thanh Khê", "Phường Sơn Trà"],
    "TP.HCM": ["Phường Bến Nghé", "Phường Bến Thành", "Phường Võ Thị Sáu"],
    "Hải Phòng": ["Phường Hồng Bàng", "Phường Ngô Quyền", "Phường Lê Chân"],
    "Cần Thơ": ["Phường Ninh Kiều", "Phường Cái Khế", "Phường An Hòa"],
}


class DiaChi:
    """Đọc tỉnh và phường/xã đã lưu sẵn trong data/tinh_thanh.json (lớp của C); lỗi thì dùng danh sách mẫu."""

    def __init__(self, ql=None):
        self.loi = ""
        self.dung_mau = False
        try:
            if ql is None:
                from services.quan_ly_dia_chi import quan_li_dia_chi
                ql = quan_li_dia_chi()
                ql.doc_json()
            self.ql = ql
            if not ql.lay_danh_sach_tinh():
                raise ValueError("file tinh_thanh.json không có tỉnh nào")
        except Exception as e:       # thiếu file, thiếu thư viện, v.v.
            self.ql, self.dung_mau, self.loi = None, True, f"{type(e).__name__}: {e}"

    def lay_danh_sach_tinh(self):
        return list(TINH_MAU) if self.dung_mau else self.ql.lay_danh_sach_tinh()

    def lay_danh_sach_xa(self, ten_tinh):
        if self.dung_mau:
            return list(XA_MAU.get(ten_tinh, []))
        return self.ql.lay_phuong_xa(ten_tinh)
