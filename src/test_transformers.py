import numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from car_transformers import CarImputer, BrandModelGrouper

rng = np.random.RandomState(0)
n = 400
df = pd.DataFrame({
    "carbrand": rng.choice(["Toyota", "Ford", "Kia", "Bentley", "Wuling"], n, p=[.4, .3, .25, .025, .025]),
    "carmodel": rng.choice(["Vios", "Ranger", "Morning", "Dòng khác"], n),
    "carorigin": rng.choice(["Việt Nam", "Thái Lan", None], n),
    "condition_ad": rng.choice(["Đã sử dụng", "Mới"], n, p=[.9, .1]),
    "gearbox": rng.choice(["Tự động", "Số tay"], n),
    "fuel": rng.choice(["Xăng", "Dầu"], n),
    "cartype": rng.choice(["Sedan", "SUV", None], n),
    "carseats": rng.choice([5.0, 7.0, np.nan], n),
    "mfdate": rng.choice([2012, 2015, 2018, 2021, 2024], n),
    "mileage_km": rng.choice([20000.0, 60000.0, 120000.0, np.nan], n),
})
y = np.log(rng.uniform(200, 900, n))
tr, te, y_tr = df.iloc[:300], df.iloc[300:].copy(), y[:300]

# Nhãn chưa từng thấy ở train, mô phỏng tình huống thực tế
te.loc[te.index[0], "carbrand"] = "Ferrari"
te.loc[te.index[1], "carmodel"] = "Mẫu lạ"

imp = CarImputer().fit(tr)
grp = BrandModelGrouper().fit(tr)
o_tr = grp.transform(imp.transform(tr))
o_te = grp.transform(imp.transform(te))

for name, o in [("train", o_tr), ("test", o_te)]:
    print(f"{name}: còn thiếu = {int(o.isna().sum().sum())}, số dòng = {len(o)}, "
          f"nhóm hãng = {o['carbrand_grp'].nunique()}, nhóm dòng = {o['carmodel_grp'].nunique()}")

assert set(o_te["carbrand_grp"]) <= set(o_tr["carbrand_grp"]), "test sinh nhóm hãng lạ"
assert set(o_te["carmodel_grp"]) <= set(o_tr["carmodel_grp"]), "test sinh nhóm dòng lạ"
print("OK: test không sinh nhãn nhóm nào ngoài những nhóm đã học từ train")
print("   Ferrari (chưa thấy ở train) ->", o_te['carbrand_grp'].iloc[0], "|",
      o_te['carmodel_grp'].iloc[0])
print("   'Mẫu lạ' (chưa thấy ở train) ->", o_te['carmodel_grp'].iloc[1])

one, full = grp.transform(imp.transform(te.iloc[[5]])), o_te.iloc[[5]]
assert np.allclose(one["mileage_km"], full["mileage_km"])
assert (one["carmodel_grp"] == full["carmodel_grp"]).all()
print("OK: transform 1 dòng == transform cả tập -> không phụ thuộc chính tập test")

CAT = ["carbrand_grp", "carmodel_grp", "carorigin", "condition_ad", "gearbox", "fuel", "cartype"]
NUM = ["age", "mileage_km", "carseats", "km_per_year", "mileage_missing"]
pipe = Pipeline([
    ("impute", CarImputer()),
    ("group", BrandModelGrouper()),
    ("encode", ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
                                  ("num", "passthrough", NUM)])),
    ("model", RandomForestRegressor(50, random_state=0, n_jobs=-1)),
])
s = -cross_val_score(pipe, tr, y_tr, cv=3, scoring="neg_root_mean_squared_error")
print("OK: Pipeline chạy CV, RMSE từng fold =", np.round(s, 4))
pipe.fit(tr, y_tr)
print("OK: fit train + predict test, 3 giá trị đầu =", np.round(np.exp(pipe.predict(te))[:3], 1))
