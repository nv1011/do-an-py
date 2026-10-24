import time
from pathlib import Path

import orjson
import requests

from services.api_dia_chi import goi_api

JSON_FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "tinh_thanh.json"
TEN_RUT_GON = {"Hồ Chí Minh": "TP.HCM"}
SO_LAN_THU = 3
GIAY_CHO_KHI_BI_GIOI_HAN = 20


class quan_li_dia_chi:
    def __init__(self, api=None, json_file_path=JSON_FILE_PATH):
        self.api = api or goi_api()
        self.json_file_path = Path(json_file_path)
        self.danh_sach_tinh = []
        self.phuong_xa = {}

    @staticmethod
    def ten_hien_thi(ten_tinh):
        return TEN_RUT_GON.get(ten_tinh, ten_tinh)

    @staticmethod
    def ten_phuong_xa(phuong_xa):
        return f"{phuong_xa['type']} {phuong_xa['name']}"

    def goi_co_thu_lai(self, ham, *doi_so):
        for lan in range(1, SO_LAN_THU + 1):
            try:
                return ham(*doi_so)
            except requests.exceptions.HTTPError as loi:
                bi_gioi_han = (
                    loi.response is not None and loi.response.status_code == 429
                )
                if not bi_gioi_han or lan == SO_LAN_THU:
                    raise
                print(
                    f"bi gioi han so request, cho {GIAY_CHO_KHI_BI_GIOI_HAN}s roi thu lai ({lan}/{SO_LAN_THU})"
                )
                time.sleep(GIAY_CHO_KHI_BI_GIOI_HAN)

    def tai_tat_ca(self):
        raw_data = self.goi_co_thu_lai(self.api.goi_api_lay_raw_data)
        self.danh_sach_tinh = []
        self.phuong_xa = {}
        for stt, tinh in enumerate(raw_data, start=1):
            ds_phuong_xa = self.goi_co_thu_lai(
                self.api.goi_api_lay_phuong_xa, tinh["code"]
            )
            tong_du_kien = tinh.get("ward_count")
            if tong_du_kien is not None and tong_du_kien != len(ds_phuong_xa):
                print(
                    f"canh bao: {tinh['name']} can {tong_du_kien} phuong/xa nhung lay duoc {len(ds_phuong_xa)}"
                )
            ten_ra = self.ten_hien_thi(tinh["name"])
            self.danh_sach_tinh.append(ten_ra)
            self.phuong_xa[ten_ra] = [self.ten_phuong_xa(p) for p in ds_phuong_xa]
            print(f"[{stt}/{len(raw_data)}] {ten_ra}: {len(ds_phuong_xa)} phuong/xa")

    def lay_danh_sach_tinh(self):
        return list(self.danh_sach_tinh)

    def lay_phuong_xa(self, ten_tinh):
        return list(self.phuong_xa.get(ten_tinh, []))

    def dem_phuong_xa(self):
        return sum(len(ds) for ds in self.phuong_xa.values())

    def luu_json(self):
        self.json_file_path.parent.mkdir(parents=True, exist_ok=True)
        du_lieu = {
            "DANH_SACH_TINH": self.danh_sach_tinh,
            "PHUONG_XA_MAU": self.phuong_xa,
        }
        with open(self.json_file_path, "wb") as f:
            f.write(orjson.dumps(du_lieu, option=orjson.OPT_INDENT_2))

    def doc_json(self):
        with open(self.json_file_path, "rb") as f:
            du_lieu = orjson.loads(f.read())
        self.danh_sach_tinh = du_lieu["DANH_SACH_TINH"]
        self.phuong_xa = du_lieu["PHUONG_XA_MAU"]


if __name__ == "__main__":
    ql = quan_li_dia_chi()
    ql.tai_tat_ca()
    ql.luu_json()
    print(
        f"da ghi {len(ql.danh_sach_tinh)} tinh, {ql.dem_phuong_xa()} phuong/xa vao {ql.json_file_path}"
    )
