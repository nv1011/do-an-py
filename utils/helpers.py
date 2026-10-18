"""Tiện ích tìm kiếm tiếng Việt — bỏ dấu và so khớp từ khóa."""
import unicodedata


def bo_dau(chuoi: str) -> str:
    """'Nguyễn Đức' -> 'Nguyen Duc' (bỏ dấu tiếng Việt)."""
    chuoi = chuoi.replace("đ", "d").replace("Đ", "D")
    phan_tach = unicodedata.normalize("NFD", chuoi)
    return "".join(c for c in phan_tach if unicodedata.category(c) != "Mn")


def chuan_hoa(chuoi: str) -> str:
    """Bỏ dấu, viết thường, gộp khoảng trắng thừa."""
    return " ".join(bo_dau(chuoi).lower().split())


def khop_ten(ten: str, tu_khoa: str) -> bool:
    """Mỗi từ trong từ khóa phải là phần đầu của ít nhất một từ trong tên.

    VD: 'Nguyễn Văn A' khớp với 'van a' hoặc 'ngu a'.
    """
    cac_tu_khoa = chuan_hoa(tu_khoa).split()
    cac_tu_ten  = chuan_hoa(ten).split()
    return all(any(tu.startswith(tk) for tu in cac_tu_ten) for tk in cac_tu_khoa)


def khop_chuoi(gia_tri: str, tu_khoa: str) -> bool:
    """Từ khóa nằm ở bất kỳ đâu trong giá trị (dùng cho mã, SĐT, BHYT...)."""
    return chuan_hoa(tu_khoa) in chuan_hoa(gia_tri)


def khop(khoa: str, gia_tri: str, tu_khoa: str) -> bool:
    """Dispatcher tìm kiếm: 'ho_ten' so theo từ, các trường còn lại so theo chuỗi con.

    Service gọi hàm này thay vì gọi trực tiếp khop_ten / khop_chuoi.
    """
    if khoa == "ho_ten":
        return khop_ten(gia_tri, tu_khoa)
    return khop_chuoi(gia_tri, tu_khoa)
