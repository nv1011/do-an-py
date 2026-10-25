"""JsonStore: đọc/ghi file JSON an toàn cho tầng Services.

- Đọc/ghi luôn bằng `with`, mã hóa UTF-8 (đọc chịu được cả file có BOM `utf-8-sig`).
- Tự động định vị file trong thư mục `data/` nếu truyền tên file tương đối.
- File thiếu hoặc rỗng -> trả về danh sách rỗng.
- File sai định dạng JSON -> lưu bản sao file hỏng vào backup/, trả về danh sách rỗng,
  mô tả lỗi nằm ở `loi_cuoi`.
- Ghi theo kiểu nguyên tử (Atomic Write) -> ghi ra file tạm, fsync rồi đổi tên,
  file cũ không bao giờ bị ghi dở khi mất điện/tắt ngang.
- Sao lưu có dấu thời gian -> tự dọn dẹp, chỉ giữ `giu_toi_da` bản mới nhất cho mỗi file.
"""
import json
import logging
import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

_THU_MUC_GOC = Path(__file__).resolve().parent.parent
DATA_MAC_DINH = _THU_MUC_GOC / "data"
BACKUP_MAC_DINH = _THU_MUC_GOC / "backup"

log = logging.getLogger(__name__)


class JsonStore:
    def __init__(self, thu_muc_data=DATA_MAC_DINH, thu_muc_backup=BACKUP_MAC_DINH, giu_toi_da=10):
        self.thu_muc_data = Path(thu_muc_data)
        self.thu_muc_backup = Path(thu_muc_backup)
        self.giu_toi_da = giu_toi_da
        # Mô tả lỗi/cảnh báo của lần gọi gần nhất; chuỗi rỗng nghĩa là mọi thứ ổn.
        self.loi_cuoi = ""

        self.thu_muc_data.mkdir(parents=True, exist_ok=True)
        self.thu_muc_backup.mkdir(parents=True, exist_ok=True)

    def _chuan_hoa_duong_dan(self, duong_dan):
        """Nếu chỉ truyền tên file (VD: 'benh_nhan.json'), tự động gắn vào thư mục data."""
        p = Path(duong_dan)
        if not p.is_absolute() and p.parent == Path("."):
            if not p.suffix:
                p = p.with_suffix(".json")
            return self.thu_muc_data / p
        return p

    # ------------------------------------------------------------------ đọc
    def doc_file(self, duong_dan):
        """Đọc file JSON, luôn trả về list[dict]. Không bao giờ ném lỗi ra ngoài."""
        duong_dan = self._chuan_hoa_duong_dan(duong_dan)
        self.loi_cuoi = ""
        try:
            with open(duong_dan, "r", encoding="utf-8-sig") as f:
                noi_dung = f.read()
        except FileNotFoundError:
            return []
        except UnicodeDecodeError:
            return self._xu_ly_file_hong(duong_dan, "không phải mã hóa UTF-8")
        except OSError as e:
            self._ghi_loi(f"Không đọc được {duong_dan.name}: {e}")
            return []

        if not noi_dung.strip():
            return []

        try:
            du_lieu = json.loads(noi_dung)
        except json.JSONDecodeError as e:
            return self._xu_ly_file_hong(
                duong_dan, f"sai định dạng JSON (dòng {e.lineno}, cột {e.colno})")

        if not isinstance(du_lieu, list) or not all(isinstance(p, dict) for p in du_lieu):
            return self._xu_ly_file_hong(duong_dan, "phải là một danh sách các đối tượng")
        return du_lieu

    def doc(self, duong_dan, mac_dinh=None):
        """Bí danh tương thích ngược cho doc_file."""
        kq = self.doc_file(duong_dan)
        return kq if kq else (mac_dinh if mac_dinh is not None else [])

    # ------------------------------------------------------------------ ghi
    def ghi_file(self, duong_dan, du_lieu):
        """Ghi list[dict] ra file theo kiểu nguyên tử. Trả về True/False, lý do ở `loi_cuoi`."""
        duong_dan = self._chuan_hoa_duong_dan(duong_dan)
        self.loi_cuoi = ""
        if not isinstance(du_lieu, list):
            self._ghi_loi(f"Dữ liệu ghi vào {duong_dan.name} phải là một danh sách")
            return False

        file_tam = None
        try:
            duong_dan.parent.mkdir(parents=True, exist_ok=True)
            fd, file_tam = tempfile.mkstemp(
                dir=duong_dan.parent, prefix=duong_dan.stem + "_", suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(du_lieu, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(file_tam, duong_dan)       # đổi tên nguyên tử, ghi đè file cũ
            return True
        except (OSError, TypeError, ValueError) as e:
            self._ghi_loi(f"Không ghi được {duong_dan.name}: {e}")
            if file_tam and os.path.exists(file_tam):
                try:
                    os.remove(file_tam)
                except OSError:
                    pass
            return False

    def ghi(self, duong_dan, du_lieu):
        """Bí danh tương thích ngược cho ghi_file."""
        return self.ghi_file(duong_dan, du_lieu)

    # -------------------------------------------------------------- sao lưu
    def sao_luu(self, duong_dan_nguon, thu_muc_backup=None) -> str | None:
        """Chép file vào backup/ kèm dấu thời gian. Trả về đường dẫn bản sao, hoặc None."""
        nguon = self._chuan_hoa_duong_dan(duong_dan_nguon)
        thu_muc = Path(thu_muc_backup) if thu_muc_backup else self.thu_muc_backup
        self.loi_cuoi = ""
        if not nguon.is_file():
            return None
        try:
            thu_muc.mkdir(parents=True, exist_ok=True)
            dich = thu_muc / f"{nguon.stem}_{self._dau_thoi_gian()}{nguon.suffix}"
            shutil.copy2(nguon, dich)
        except OSError as e:
            self._ghi_loi(f"Không sao lưu được {nguon.name}: {e}")
            return None
        self._don_ban_sao_cu(nguon, thu_muc)
        return str(dich)

    # ------------------------------------------------------------- nội bộ
    @staticmethod
    def _dau_thoi_gian():
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    def _ghi_loi(self, thong_diep):
        self.loi_cuoi = thong_diep
        log.error(thong_diep)

    def _xu_ly_file_hong(self, duong_dan, ly_do):
        """Giữ lại bản sao file hỏng để không mất dấu vết, rồi coi như danh sách rỗng."""
        thong_diep = f"File {duong_dan.name} {ly_do}."
        try:
            self.thu_muc_backup.mkdir(parents=True, exist_ok=True)
            ban_sao = self.thu_muc_backup / (
                f"{duong_dan.stem}_HONG_{self._dau_thoi_gian()}{duong_dan.suffix}")
            shutil.copy2(duong_dan, ban_sao)
            thong_diep += f" Đã lưu bản sao tại {ban_sao.name}, tạm dùng danh sách rỗng."
        except OSError as e:
            thong_diep += f" Không lưu được bản sao ({e}), tạm dùng danh sách rỗng."
        self._ghi_loi(thong_diep)
        return []

    def _don_ban_sao_cu(self, nguon, thu_muc):
        """Chỉ giữ `giu_toi_da` bản sao mới nhất của file nguồn (không đụng tới bản *_HONG_*)."""
        mau = re.compile(
            rf"^{re.escape(nguon.stem)}_\d{{8}}_\d{{6}}_\d{{6}}{re.escape(nguon.suffix)}$")
        try:
            cac_ban = sorted(p for p in thu_muc.iterdir() if p.is_file() and mau.match(p.name))
            for cu in cac_ban[:-self.giu_toi_da] if self.giu_toi_da > 0 else cac_ban:
                try:
                    cu.unlink()
                except OSError:
                    pass
        except OSError:
            pass
