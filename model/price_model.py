"""Nạp và dự đoán giá ô tô (triệu đồng) bằng các mô hình đã huấn luyện trong model.ipynb.

Dùng:
    from price_model import load_model, predict_price
    m = load_model("random_forest_sklearn")
    predict_price(m, df)   # df có các cột như mô tả bên dưới

Các mô hình có sẵn:
    ridge_sklearn, ridge_scratch, random_forest_sklearn, random_forest_scratch

Cột đầu vào (mỗi dòng là một xe), dùng đúng giá trị như trên Chợ Tốt:
    carbrand, carmodel      tên hãng và dòng xe ("Dòng khác" nếu không có trong danh sách)
    carorigin               xuất xứ ("Không rõ" nếu không biết)
    condition_ad            "Mới" hoặc "Đã sử dụng"
    gearbox, fuel, cartype  hộp số, nhiên liệu, kiểu dáng ("Không rõ" nếu không biết kiểu dáng)
    carseats                số chỗ
    mfdate hoặc age         năm sản xuất hoặc tuổi xe
    mileage_km              số km đã đi; xe mới = 0; để trống (None/NaN) nếu không biết

Cách dựng đặc trưng giống preprocess_data.ipynb:
    - Hãng / dòng xe hiếm hoặc chưa gặp được gộp theo cấp: dòng xe -> "<hãng> - dòng khác";
      hãng hiếm -> "Hãng cao cấp khác" / "Hãng phổ thông khác".
    - Xe đã dùng không rõ số km: điền trung vị số km của xe cùng năm sản xuất, đánh dấu mileage_missing = 1.

Lưu ý:
    - Tuổi xe tính theo năm 2026 (năm thu thập dữ liệu và huấn luyện). Giữ nguyên khi dùng ở năm sau.
    - Chợ Tốt có năm sản xuất "trước năm 1980": lúc huấn luyện được gán 1979, nên truyền 1979.
    - Giá dự đoán là exp(dự đoán log giá), tức ước lượng trung vị của giá.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

DIR = Path(__file__).resolve().parent
MODELS = ("ridge_sklearn", "ridge_scratch", "random_forest_sklearn", "random_forest_scratch")

with open(DIR / "metadata.json", encoding="utf-8") as f:
    META = json.load(f)
CURRENT_YEAR = META["current_year"]
KM_MED = {int(k): v for k, v in META["mileage_median_by_year"].items()}
LUXURY = set(META["luxury_brands"])


def make_features(df):
    """Dựng mọi đặc trưng mà hai mô hình cần từ thông tin thô của xe."""
    d = df.copy()
    if "age" not in d:
        d["age"] = CURRENT_YEAR - d["mfdate"]
    if "mfdate" not in d:
        d["mfdate"] = CURRENT_YEAR - d["age"]

    # Số km: xe mới thiếu -> 0; xe đã dùng thiếu -> trung vị theo năm sản xuất (đánh dấu mileage_missing)
    km = pd.to_numeric(d["mileage_km"], errors="coerce").astype(float)
    is_new = d["condition_ad"] == "Mới"
    if "mileage_missing" not in d:
        d["mileage_missing"] = (km.isna() & ~is_new).astype(int)
    km = km.mask(km.isna() & is_new, 0.0)
    km = km.fillna(d["mfdate"].map(KM_MED)).fillna(META["mileage_median_all"])
    d["mileage_km"] = km
    d["km_per_year"] = km / d["age"].clip(lower=1)

    # Gộp nhãn hiếm theo cấp, dùng bảng học từ dữ liệu huấn luyện
    if "carbrand_grp" not in d:
        other = np.where(d["carbrand"].isin(LUXURY), "Hãng cao cấp khác", "Hãng phổ thông khác")
        d["carbrand_grp"] = d["carbrand"].map(META["brand_group"]).fillna(pd.Series(other, index=d.index))
    if "carmodel_grp" not in d:
        full = d["carbrand"] + " " + d["carmodel"]
        d["carmodel_grp"] = full.map(META["model_group"]).fillna(d["carbrand_grp"] + " - dòng khác")

    # Biến đổi cho Ridge
    d["age_sq"] = d["age"] ** 2
    d["log_km"] = np.log1p(d["mileage_km"])
    d["log_km_per_year"] = np.log1p(d["km_per_year"])
    return d


class _ScratchRidge:
    """Ridge tự cài đặt: chỉ cần vector trọng số (phần tử đầu là hệ số tự do)."""

    def __init__(self, path):
        self.w = np.load(path)["w"]

    def predict(self, X):
        return self.w[0] + X @ self.w[1:]


class _ScratchForest:
    """Random Forest tự cài đặt (chỉ phần dự đoán): bin hóa đặc trưng rồi đi qua từng cây."""

    def __init__(self, path):
        z = np.load(path)
        offs = z["edge_offsets"]
        self.edges = [z["edges"][offs[j]:offs[j + 1]] for j in range(len(offs) - 1)]
        self.trees = [{k: z[f"t{i}_{k}"] for k in ("feature", "thr", "left", "right", "value")}
                      for i in range(int(z["n_trees"]))]

    @staticmethod
    def _predict_tree(t, Xb):
        node = np.zeros(len(Xb), dtype=np.int64)
        while True:
            f = t["feature"][node]
            active = f >= 0
            if not active.any():
                return t["value"][node]
            rows = np.where(active)[0]
            go_left = Xb[rows, f[rows]] <= t["thr"][node[rows]]
            node[rows] = np.where(go_left, t["left"][node[rows]], t["right"][node[rows]])

    def predict(self, X):
        Xb = np.empty(X.shape, dtype=np.uint8)
        for j, e in enumerate(self.edges):
            Xb[:, j] = np.searchsorted(e, X[:, j], side="left")
        return np.mean([self._predict_tree(t, Xb) for t in self.trees], axis=0)


class PriceModel:
    def __init__(self, name):
        if name not in MODELS:
            raise ValueError(f"name phải thuộc {MODELS}")
        self.name = name
        is_ridge = name.startswith("ridge")
        self.prep = joblib.load(DIR / ("preprocessor_ridge.joblib" if is_ridge else "preprocessor_rf.joblib"))
        self.columns = META["cat_features"] + (META["num_features_ridge"] if is_ridge else META["num_features_rf"])
        if name.endswith("sklearn"):
            self.est = joblib.load(DIR / f"{name}.joblib")
        elif is_ridge:
            self.est = _ScratchRidge(DIR / "ridge_scratch.npz")
        else:
            self.est = _ScratchForest(DIR / "random_forest_scratch.npz")

    def predict_log(self, df):
        return self.est.predict(self.prep.transform(make_features(df)[self.columns]))


def load_model(name="random_forest_sklearn"):
    return PriceModel(name)


def predict_price(model, df):
    """Trả về giá dự đoán (triệu đồng) cho từng dòng của df."""
    return np.exp(model.predict_log(df))


if __name__ == "__main__":
    demo = pd.DataFrame([{
        "carbrand": "Toyota", "carmodel": "Vios", "carorigin": "Việt Nam", "condition_ad": "Đã sử dụng",
        "gearbox": "Tự động", "fuel": "Xăng", "cartype": "Sedan", "carseats": 5,
        "mfdate": 2018, "mileage_km": 80000,
    }])
    for name in MODELS:
        print(f"{name:24s}: {predict_price(load_model(name), demo)[0]:,.0f} triệu")
