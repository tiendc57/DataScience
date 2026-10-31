"""Hai transformer cho bài toán dự đoán giá ô tô.

Cả hai học tham số trong `fit` (chỉ từ dữ liệu train) và chỉ áp dụng trong
`transform`, nên đặt được vào sklearn Pipeline: mỗi fold của cross-validation
tự fit lại, không rò rỉ thông tin từ phần validation.
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

CURRENT_YEAR = 2026

LUXURY_BRANDS = {
    "Bentley", "Rolls Royce", "Maybach", "Aston Martin", "Ferrari", "Lamborghini",
    "McLaren", "Maserati", "Cadillac", "Lincoln", "Hummer", "Jaguar", "Infiniti",
    "Acura", "Volvo", "Alfa Romeo", "MINI", "Jeep", "Genesis", "Lotus",
}


def _mode(s):
    s = s.dropna()
    return s.mode().iat[0] if len(s) else np.nan


class CarImputer(BaseEstimator, TransformerMixin):
    """Điền giá trị thiếu. Thống kê (trung vị, mode) học từ train.

    Tạo thêm: mileage_missing, age, km_per_year.
    """

    def fit(self, X, y=None):
        used = X["condition_ad"] == "Đã sử dụng"
        km = X[used & X["mileage_km"].notna()]
        self.km_by_year_ = km.groupby("mfdate")["mileage_km"].median()
        self.km_global_ = km["mileage_km"].median()

        specific = X[X["carmodel"] != "Dòng khác"]
        self.type_by_model_ = specific.groupby(["carbrand", "carmodel"])["cartype"].agg(_mode)
        self.seats_by_model_ = specific.groupby(["carbrand", "carmodel"])["carseats"].agg(_mode)
        self.seats_by_brand_ = X.groupby("carbrand")["carseats"].agg(_mode)
        self.seats_global_ = _mode(X["carseats"])
        return self

    def transform(self, X):
        X = X.copy()
        used = X["condition_ad"] == "Đã sử dụng"

        # Cờ đánh dấu: tính trên từng dòng, không học gì từ train
        X["mileage_missing"] = (used & X["mileage_km"].isna()).astype(int)

        # Xe mới -> 0 km (quy tắc nghiệp vụ, không phải thống kê)
        X.loc[~used & X["mileage_km"].isna(), "mileage_km"] = 0.0

        # Xe đã dùng -> trung vị số km theo đời xe, học từ train
        m = (used & X["mileage_km"].isna()).values
        if m.any():
            X.loc[m, "mileage_km"] = (X.loc[m, "mfdate"].map(self.km_by_year_)
                                      .fillna(self.km_global_).values)

        key = pd.MultiIndex.from_frame(X[["carbrand", "carmodel"]])

        # Kiểu dáng: mode theo dòng xe; không suy ra được -> "Không rõ"
        m = X["cartype"].isna().values
        if m.any():
            X.loc[m, "cartype"] = self.type_by_model_.reindex(key[m]).values
        X["cartype"] = X["cartype"].fillna("Không rõ")

        # Số chỗ: mode theo dòng xe -> theo hãng -> toàn cục
        m = X["carseats"].isna().values
        if m.any():
            X.loc[m, "carseats"] = self.seats_by_model_.reindex(key[m]).values
        m = X["carseats"].isna().values
        if m.any():
            X.loc[m, "carseats"] = X.loc[m, "carbrand"].map(self.seats_by_brand_).values
        X["carseats"] = X["carseats"].fillna(self.seats_global_)

        # Nhãn hằng, không học từ dữ liệu
        X["carorigin"] = X["carorigin"].fillna("Không rõ")

        # Phải tính SAU khi điền km, nếu không sẽ mang NaN sang
        X["age"] = CURRENT_YEAR - X["mfdate"]
        X["km_per_year"] = X["mileage_km"] / X["age"].clip(lower=1)
        return X


class BrandModelGrouper(BaseEstimator, TransformerMixin):
    """Gộp nhãn hãng / dòng xe hiếm theo cấp. Tần suất đếm trên train.

    Tạo thêm: carbrand_grp, carmodel_grp.
    Nhãn chưa từng thấy ở train tự động rơi về nhóm "khác" tương ứng.
    """

    def __init__(self, brand_min=30, model_min=10, luxury_brands=None):
        self.brand_min = brand_min
        self.model_min = model_min
        self.luxury_brands = luxury_brands

    def _luxury(self):
        return LUXURY_BRANDS if self.luxury_brands is None else set(self.luxury_brands)

    def fit(self, X, y=None):
        vc_b = X["carbrand"].value_counts()
        self.keep_brand_ = set(vc_b[vc_b >= self.brand_min].index)
        full = X["carbrand"] + " " + X["carmodel"]
        vc_f = full.value_counts()
        self.keep_model_ = set(vc_f[vc_f >= self.model_min].index)
        return self

    def transform(self, X):
        X = X.copy()
        b = X["carbrand"]
        other = np.where(b.isin(self._luxury()), "Hãng cao cấp khác", "Hãng phổ thông khác")
        brand_grp = pd.Series(np.where(b.isin(self.keep_brand_), b, other), index=X.index)

        full = b + " " + X["carmodel"]
        keep = full.isin(self.keep_model_) & (X["carmodel"] != "Dòng khác")

        X["carbrand_grp"] = brand_grp
        X["carmodel_grp"] = full.where(keep, brand_grp + " - dòng khác")
        return X
