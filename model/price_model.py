"""Nạp và dự đoán giá ô tô (triệu đồng) bằng các mô hình đã huấn luyện trong model.ipynb.

Dùng:
    from price_model import load_model, predict_price
    m = load_model("random_forest_sklearn")
    predict_price(m, df)   # df có các cột như mô tả bên dưới

Các mô hình có sẵn:
    ridge_sklearn, ridge_scratch, random_forest_sklearn, random_forest_scratch

Cột đầu vào (mỗi dòng là một xe):
    carbrand, carmodel   (tên hãng và dòng xe như trên Chợ Tốt; hoặc truyền trực tiếp carbrand_grp, carmodel_grp)
    carorigin, condition_ad, gearbox, fuel, cartype, carseats
    mfdate hoặc age       (năm sản xuất hoặc tuổi xe)
    mileage_km            (số km đã đi; xe mới = 0)

Lưu ý:
    - Tuổi xe tính theo CURRENT_YEAR = 2026 (năm thu thập dữ liệu, cũng là năm dùng khi huấn luyện).
      Giữ nguyên giá trị này khi dùng ở năm sau, vì mô hình học giá theo mốc 2026.
    - mfdate phải là số. Trên Chợ Tốt có giá trị "trước năm 1980": lúc huấn luyện được gán 1979, nên truyền 1979.
    - Giá dự đoán là exp(dự đoán log giá), tức ước lượng trung vị của giá, hơi thấp hơn trung bình.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

DIR = Path(__file__).resolve().parent
CURRENT_YEAR = 2026
MODELS = ("ridge_sklearn", "ridge_scratch", "random_forest_sklearn", "random_forest_scratch")

with open(DIR / "metadata.json", encoding="utf-8") as f:
    META = json.load(f)


def make_features(df):
    """Dựng các đặc trưng đúng như lúc huấn luyện (xem model.ipynb mục 1.1)."""
    d = df.copy()
    if "age" not in d:
        d["age"] = CURRENT_YEAR - d["mfdate"]
    if "km_per_year" not in d:
        d["km_per_year"] = d["mileage_km"] / d["age"].clip(lower=1)
    if "carbrand_grp" not in d:
        d["carbrand_grp"] = d["carbrand"].where(d["carbrand"].isin(META["brands"]), "Hãng khác")
    if "carmodel_grp" not in d:
        full = d["carbrand"] + " " + d["carmodel"]
        d["carmodel_grp"] = full.where(full.isin(META["models"]), "Dòng khác")
    d["age_sq"] = d["age"] ** 2
    d["log_km"] = np.log1p(d["mileage_km"])
    d["log_km_per_year"] = np.log1p(d["km_per_year"])
    return d[META["cat_features"] + META["num_features"]]


class _ScratchRidge:
    """Ridge tự cài đặt: chỉ cần vector trọng số (phần tử đầu là bias)."""

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

    def _predict_tree(self, t, Xb):
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
        self.prep = joblib.load(DIR / "preprocessor.joblib")
        if name == "ridge_sklearn":
            self.est = joblib.load(DIR / "ridge_sklearn.joblib")
        elif name == "random_forest_sklearn":
            self.est = joblib.load(DIR / "random_forest_sklearn.joblib")
        elif name == "ridge_scratch":
            self.est = _ScratchRidge(DIR / "ridge_scratch.npz")
        else:
            self.est = _ScratchForest(DIR / "random_forest_scratch.npz")

    def predict_log(self, df):
        return self.est.predict(self.prep.transform(make_features(df)))


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
