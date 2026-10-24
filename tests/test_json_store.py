"""Kiểm thử JsonStore. Chạy từ thư mục gốc dự án:  py -m tests.test_json_store

Phần 1 chạy trong thư mục tạm, không đụng tới dữ liệu thật.
Phần 2 chỉ ĐỌC data/benh_nhan.json (ghi thử ra thư mục tạm), không sửa file thật.
"""
import tempfile
from datetime import date
from pathlib import Path

from services.json_store import JsonStore

THU_MUC_GOC = Path(__file__).resolve().parent.parent


def kiem_thu_thu_muc_tam():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        backup = tmp / "backup"
        store = JsonStore(thu_muc_backup=backup, giu_toi_da=3)
        f = tmp / "data" / "thu.json"

        # 1. File thiếu: trả về [], không báo lỗi, không tự tạo file
        assert store.doc_file(f) == [] and store.loi_cuoi == ""
        assert not f.exists()
        print("1. file thiếu                -> []            OK")

        # 2. File rỗng (0 byte, và chỉ có khoảng trắng): trả về []
        f.parent.mkdir(parents=True)
        f.write_text("", encoding="utf-8")
        assert store.doc_file(f) == [] and store.loi_cuoi == ""
        f.write_text("  \n ", encoding="utf-8")
        assert store.doc_file(f) == [] and store.loi_cuoi == ""
        print("2. file rỗng                 -> []            OK")

        # 3. Sai định dạng: trả về [], có thông báo, giữ bản sao file hỏng
        f.write_text('[{"ho_ten": "An"', encoding="utf-8")
        assert store.doc_file(f) == [] and "sai định dạng" in store.loi_cuoi
        assert any("_HONG_" in p.name for p in backup.iterdir())
        f.write_text('{"a": 1}', encoding="utf-8")              # JSON đúng nhưng không phải list
        assert store.doc_file(f) == [] and store.loi_cuoi != ""
        f.write_bytes("[]".encode("utf-16"))                    # sai mã hóa
        assert store.doc_file(f) == [] and "UTF-8" in store.loi_cuoi
        print("3. file sai định dạng        -> [] + bản sao  OK")

        # 4. Ghi rồi đọc lại, giữ nguyên tiếng Việt (không bị \uXXXX)
        du_lieu = [{"ho_ten": "Nguyễn Văn An", "so": 1}]
        assert store.ghi_file(f, du_lieu) is True and store.loi_cuoi == ""
        assert store.doc_file(f) == du_lieu
        assert "Nguyễn Văn An" in f.read_text(encoding="utf-8")
        print("4. ghi rồi đọc lại           -> khớp          OK")

        # 5. Đọc được file có BOM (Notepad hay thêm)
        f.write_text('\ufeff[{"a": 1}]', encoding="utf-8")
        assert store.doc_file(f) == [{"a": 1}]
        store.ghi_file(f, du_lieu)
        print("5. file có BOM               -> đọc được     OK")

        # 6. Ghi lỗi (date không tuần tự hóa được): file cũ còn nguyên, không sót file tạm
        assert store.ghi_file(f, [{"ngay": date(2026, 10, 18)}]) is False
        assert store.loi_cuoi != ""
        assert store.doc_file(f) == du_lieu
        assert not list(f.parent.glob("*.tmp"))
        assert store.ghi_file(f, {"khong_phai": "list"}) is False
        print("6. ghi lỗi                   -> file cũ còn   OK")

        # 7. Ghi vào thư mục chưa có: tự tạo thư mục
        sau = tmp / "moi" / "tao" / "ra.json"
        assert store.ghi_file(sau, []) is True and sau.exists()
        print("7. thư mục chưa có           -> tự tạo        OK")

        # 8. Sao lưu: có dấu thời gian, chỉ giữ tối đa 3 bản mới nhất, file thiếu trả None
        for _ in range(5):
            assert store.sao_luu(f) is not None
        cac_ban = [p for p in backup.iterdir() if p.name.startswith("thu_2")]
        assert len(cac_ban) == 3, cac_ban
        assert any("_HONG_" in p.name for p in backup.iterdir())    # bản hỏng không bị dọn
        assert store.sao_luu(tmp / "khong_co.json") is None
        print("8. sao lưu                   -> giữ 3 bản     OK")


def kiem_thu_voi_du_lieu_that():
    nguon = THU_MUC_GOC / "data" / "benh_nhan.json"
    if not nguon.exists():
        print("9. bỏ qua: chưa có data/benh_nhan.json")
        return
    from models.benh_nhan import BenhNhan

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        store = JsonStore(thu_muc_backup=tmp / "backup")

        ds = store.doc_file(nguon)
        assert store.loi_cuoi == "", store.loi_cuoi
        print(f"9. đọc data/benh_nhan.json   -> {len(ds)} bản ghi  OK")

        benh_nhan = [BenhNhan.from_dict(d) for d in ds]          # lỗi ở đây = JSON mẫu lệch schema
        du_lieu_ra = [b.to_dict() for b in benh_nhan]

        ban_sao = tmp / "benh_nhan_copy.json"
        assert store.ghi_file(ban_sao, du_lieu_ra)
        doc_lai = [BenhNhan.from_dict(d).to_dict() for d in store.doc_file(ban_sao)]
        assert doc_lai == du_lieu_ra
        print("10. ghi bản sao và đọc lại   -> khớp          OK")


if __name__ == "__main__":
    kiem_thu_thu_muc_tam()
    kiem_thu_voi_du_lieu_that()
    print("OK")