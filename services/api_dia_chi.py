import requests
import config

LIMIT_MOI_TRANG = 100


class goi_api:
    def __init__(
        self, base_url=config.API_DIA_CHI_URL, timeout=config.API_TIMEOUT_GIAY
    ):
        self.base_url = base_url
        self.timeout = timeout

    def goi_api_lay_json(self, duong_dan, tham_so=None):
        # duong dan la phan url noi ngay sau base url. vd: /new-provinces
        response = requests.get(
            f"{self.base_url}{duong_dan}",
            params=tham_so,
            # tham_so la 1 dict chua cac para truy van (phan sau dau ? tren url)
            headers={"Accept": "application/json"},
            # dat header mac dinh nhu v de bao cho sv biet minh muon nhan json
            # moi request di qua self.session deu tu mang header nay
            timeout=self.timeout,
        )
        response.raise_for_status()
        # neu sv return error code: 429 = goi qua nhieu, 500 = loi sv thi throw requests.exceptions.HTTPError
        return response.json()

    def goi_api_lay_tat_ca_trang(self, duong_dan, tham_so=None):
        ket_qua = []
        trang = 1
        while True:
            tham_so_trang = dict(tham_so or {})
            tham_so_trang["page"] = trang
            tham_so_trang["limit"] = LIMIT_MOI_TRANG
            noi_dung = self.goi_api_lay_json(duong_dan, tham_so_trang)
            du_lieu = noi_dung.get("data", [])
            # du lieu la list cac phan tu 1 trang (toi da 100)
            ket_qua.extend(du_lieu)
            # extend noi tung phan do vao ket_qua
            tong = noi_dung.get("metadata", {}).get("total", len(ket_qua))
            if not du_lieu or len(ket_qua) >= tong:
                break
            trang += 1
        return ket_qua

    def goi_api_lay_raw_data(self):
        return self.goi_api_lay_tat_ca_trang("/new-provinces")

    def goi_api_lay_phuong_xa(self, ma_tinh):
        return self.goi_api_lay_tat_ca_trang(f"/new-provinces/{ma_tinh}/wards")
