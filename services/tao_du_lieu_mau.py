import json
import os
import random
import shutil
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

from config import (
    BACKUP_DIR,
    CHUYEN_KHOA_MAX,
    CHUYEN_KHOA_MIN,
    # muon thay doi dai gioi han so lg chuyen khoa thi sua config.py
    DAU_SO,
    DEM_NAM,
    DEM_NU,
    # ten dem co san de rand
    DIA_CHI_DU_PHONG,
    DUONG,
    FILE_BAC_SI,
    FILE_BENH_NHAN,
    FILE_TINH_THANH,
    HO,
    HOC_VI_MAX,
    HOC_VI_MIN,
    LUONG_NEN,
    NAM_SINH_SOM_NHAT_BAC_SI,
    NAM_VAO_LAM_MAX,
    NAM_VAO_LAM_MIN,
    NHOM_MAU,
    SEED,
    SO_BAC_SI,
    SO_BENH_NHAN,
    SO_CA_MOI_TUAN,
    SO_NGAY_DANG_KY,
    TAT_CA_CA_LAM,
    TEN_NAM,
    TEN_NU,
    TIEN_SU,
    TRONG_SO_HO,
    TRONG_SO_NHOM_MAU,
    TUOI_TOI_THIEU_BAC_SI,
)


def bo_dau(chuoi):  # bo dau tieng viet de xu li o cac buoc sau
    chuoi = chuoi.replace("đ", "d").replace("Đ", "D")
    phan_tach = unicodedata.normalize("NFD", chuoi)
    # unicodedata.normalize(form, unistr) chuan hoa cac unistr (unicode string) ve 1 dang chuan duy nhat theo form (NFC, NFD, NFKC, NFKD)
    return "".join(c for c in phan_tach if unicodedata.category(c) != "Mn")
    # Mn: Mark, Nonspacing (dau phu khong gian) - unicode category


def doc_dia_chi_tu_file(duong_dan=FILE_TINH_THANH):
    # Lay tinh va phuong/xa tu tinh_thanh.json; loi file thi dung du lieu du phong
    try:
        with open(duong_dan, "r", encoding="utf-8") as f:
            du_lieu = json.load(f)
        phuong_xa = du_lieu["PHUONG_XA_MAU"]
        dia_chi_goc = {
            tinh: phuong_xa[tinh]
            for tinh in du_lieu["DANH_SACH_TINH"]
            if phuong_xa.get(tinh)
        }
        if not dia_chi_goc:
            raise ValueError("khong co tinh nao co phuong/xa")
        return dia_chi_goc
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as loi:
        print(f"khong doc duoc {Path(duong_dan).name} ({loi}), dung du lieu du phong")
        return DIA_CHI_DU_PHONG


def chon_dia_chi(dia_chi_goc):
    tinh = random.choice(list(dia_chi_goc))
    return {
        "dia_chi": f"{random.randint(1, 200)} {random.choice(DUONG)}",
        "tinh_thanh": tinh,
        "xa_phuong": random.choice(dia_chi_goc[tinh]),
    }


def sinh_ho_ten(gioi_tinh):
    ho = random.choices(HO, weights=TRONG_SO_HO)[0]
    # rand chon 1 phan tu ho tu list HO
    # voi trong so tuong ung trong list TRONG_SO_HO (cung do dai voi HO) de dieu chinh xac suat xuat hien cua tung ho
    # vd: Nguyen = 30/96, Tran = 11/96, Le = 10/96, ...
    # random.choices() return list nen [0] giup lay pt dau tien ra => string ho
    if gioi_tinh == "Nam":
        return f"{ho} {random.choice(DEM_NAM)} {random.choice(TEN_NAM)}"
    return f"{ho} {random.choice(DEM_NU)} {random.choice(TEN_NU)}"


def sinh_sdt(da_dung):
    # 10 so, dau so thuoc nha mang that; khong trung trong toan bo du lieu mau
    while True:
        sdt = random.choice(DAU_SO) + "".join(random.choices("0123456789", k=7))
        if sdt not in da_dung:
            da_dung.add(sdt)
            return sdt


def sinh_so_bhyt(da_dung):
    # Theo mau nhom da nhap: 13 chu so, bat dau bang 401
    while True:
        so_bhyt = "401" + "".join(random.choices("0123456789", k=10))
        if so_bhyt not in da_dung:
            da_dung.add(so_bhyt)
            return so_bhyt


def sinh_email(ho_ten, nam_sinh, da_dung):
    cac_phan = bo_dau(ho_ten).lower().split()
    ho, ten, dem = cac_phan[0], cac_phan[-1], cac_phan[1:-1]
    kieu = [
        "".join(cac_phan),
        f"{ten}.{ho}",
        f"{''.join(dem + [ten])}{str(nam_sinh)[-2:]}",
        f"{ten}{ho[0]}{random.randint(10, 999)}",
    ]
    mien = random.choice(
        ["gmail.com", "gmail.com", "gmail.com", "yahoo.com", "outlook.com"]
    )
    phan_dau = random.choice(kieu)
    email = f"{phan_dau}@{mien}"
    while email in da_dung:
        email = f"{phan_dau}{random.randint(1, 999)}@{mien}"
    da_dung.add(email)
    return email


def sinh_tien_su(tuoi):
    if random.random() < 0.4:
        return "Không có"
    hop_le = [ten for ten, tuoi_toi_thieu in TIEN_SU if tuoi >= tuoi_toi_thieu]
    return random.choice(hop_le)


def sinh_ds_benh_nhan(so_luong, dia_chi_goc, da_dung_sdt):
    hom_nay = date.today()
    # Sap xep ngay dang ky tang dan de so thu tu trong ngay cap phat tu 000001
    ds_ngay = sorted(
        hom_nay - timedelta(days=random.randint(0, SO_NGAY_DANG_KY))
        for _ in range(so_luong)
    )
    dem_theo_ngay = {}
    da_dung_bhyt, da_dung_email = set(), set()
    ket_qua = []
    for ngay_dang_ky in ds_ngay:
        gioi_tinh = random.choice(["Nam", "Nữ"])
        ho_ten = sinh_ho_ten(gioi_tinh)
        tuoi = random.randint(1, 85)
        ngay_sinh = ngay_dang_ky - timedelta(days=tuoi * 365 + random.randint(0, 364))
        dem_theo_ngay[ngay_dang_ky] = dem_theo_ngay.get(ngay_dang_ky, 0) + 1
        # Ma benh nhan: ddmmyyyy (ngay dang ky) + 6 so thu tu trong ngay
        ma = f"{ngay_dang_ky:%d%m%Y}{dem_theo_ngay[ngay_dang_ky]:06d}"
        ket_qua.append(
            {
                "ma_dinh_danh": ma,
                "ho_ten": ho_ten,
                **chon_dia_chi(dia_chi_goc),
                "gioi_tinh": gioi_tinh,
                "ngay_sinh": ngay_sinh.isoformat(),
                "sdt": sinh_sdt(da_dung_sdt),
                "so_bhyt": sinh_so_bhyt(da_dung_bhyt),
                "email": sinh_email(ho_ten, ngay_sinh.year, da_dung_email),
                "tien_su_benh": sinh_tien_su(tuoi),
                "nhom_mau": random.choices(NHOM_MAU, weights=TRONG_SO_NHOM_MAU)[0],
                "ngay_dang_ky": ngay_dang_ky.isoformat(),
            }
        )
    return ket_qua


def sinh_ds_bac_si(so_luong, dia_chi_goc, da_dung_sdt):
    nam_hien_tai = date.today().year
    dem_theo_khoa_nam = {}
    ket_qua = []
    for _ in range(so_luong):
        hoc_vi = random.randint(HOC_VI_MIN, HOC_VI_MAX)
        chuyen_khoa = random.randint(CHUYEN_KHOA_MIN, CHUYEN_KHOA_MAX)
        nam_vao_lam = random.randint(NAM_VAO_LAM_MIN, NAM_VAO_LAM_MAX)
        # So thu tu tinh rieng cho tung cap (chuyen khoa, nam vao lam)
        khoa = (chuyen_khoa, nam_vao_lam)
        dem_theo_khoa_nam[khoa] = dem_theo_khoa_nam.get(khoa, 0) + 1
        # Ma bac si: HH (hoc vi/chuc vu) CC (chuyen khoa) YY (nam vao lam) SSS (so thu tu)
        ma_hoc_vi = f"{hoc_vi:02d}"
        ma = f"{ma_hoc_vi}{chuyen_khoa:02d}{nam_vao_lam:02d}{dem_theo_khoa_nam[khoa]:03d}"

        gioi_tinh = random.choice(["Nam", "Nữ"])
        nam_day_du = 2000 + nam_vao_lam
        # Vao lam khi du tuoi toi thieu va den nay chua qua tuoi nghi huu
        nam_sinh = random.randint(
            max(NAM_SINH_SOM_NHAT_BAC_SI, nam_day_du - 40),
            nam_day_du - TUOI_TOI_THIEU_BAC_SI,
        )
        ngay_sinh = date(nam_sinh, 1, 1) + timedelta(days=random.randint(0, 364))
        tham_nien = max(0, nam_hien_tai - nam_day_du)
        luong = (
            LUONG_NEN[ma_hoc_vi]
            + min(tham_nien, 20) * 250_000
            + random.randint(0, 4) * 500_000
        )
        vi_tri_ca = sorted(random.sample(range(len(TAT_CA_CA_LAM)), SO_CA_MOI_TUAN))

        ket_qua.append(
            {
                "ma_dinh_danh": ma,
                "ho_ten": sinh_ho_ten(gioi_tinh),
                **chon_dia_chi(dia_chi_goc),
                "gioi_tinh": gioi_tinh,
                "ngay_sinh": ngay_sinh.isoformat(),
                "sdt": sinh_sdt(da_dung_sdt),
                "lich_lam_viec": [TAT_CA_CA_LAM[i] for i in vi_tri_ca],
                "luong_cb": luong,
            }
        )
    return ket_qua


def ghi_json_an_toan(duong_dan, du_lieu):
    # Sao luu file cu vao backup/, ghi ra file tam roi doi ten de khong mat du lieu khi loi giua chung
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    if duong_dan.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        dau_thoi_gian = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(
            duong_dan,
            BACKUP_DIR / f"{duong_dan.stem}_{dau_thoi_gian}{duong_dan.suffix}",
        )
    file_tam = duong_dan.with_suffix(".json.tmp")
    with open(file_tam, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=2)
    os.replace(file_tam, duong_dan)


def tao_du_lieu_mau(so_benh_nhan=SO_BENH_NHAN, so_bac_si=SO_BAC_SI, seed=SEED):
    if seed is not None:
        random.seed(seed)
    dia_chi_goc = doc_dia_chi_tu_file()
    da_dung_sdt = set()
    ds_bac_si = sinh_ds_bac_si(so_bac_si, dia_chi_goc, da_dung_sdt)
    ds_benh_nhan = sinh_ds_benh_nhan(so_benh_nhan, dia_chi_goc, da_dung_sdt)
    ghi_json_an_toan(FILE_BAC_SI, ds_bac_si)
    ghi_json_an_toan(FILE_BENH_NHAN, ds_benh_nhan)
    print(f"da ghi {len(ds_bac_si)} bac si vao {FILE_BAC_SI}")
    print(f"da ghi {len(ds_benh_nhan)} benh nhan vao {FILE_BENH_NHAN}")
    return ds_bac_si, ds_benh_nhan


if __name__ == "__main__":
    tao_du_lieu_mau()

# muon test thi termnal -> python -m services.tao_du_lieu_mau
