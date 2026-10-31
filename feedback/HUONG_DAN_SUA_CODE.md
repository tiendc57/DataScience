# Hướng dẫn sửa code: chuẩn hóa thứ tự chia dữ liệu trong pipeline ML

> Tài liệu này dành cho AI agent thực hiện việc sửa code. Đọc hết **mục 1 đến 4**
> trước khi sửa bất cứ dòng nào. Mục 4 liệt kê những thứ **không được sửa** —
> đây là phần quan trọng nhất để tránh làm hỏng những phần đang đúng.

---

## 1. Bối cảnh project

Project dự đoán **giá rao bán ô tô** (triệu đồng) từ tin đăng trên Chợ Tốt.
Bài toán hồi quy có giám sát, biến mục tiêu là `ln(giá)`, thước đo chính là MAPE.

Ba notebook:

| File | Nội dung |
|---|---|
| `crawl_data.ipynb` | Thu thập 14.835 tin từ `xe.chotot.com`, xuất `raw_data_oto.csv` |
| `preprocess_data.ipynb` | Làm sạch, điền thiếu, gộp nhãn, xuất `clean_data_oto.csv` (13.937 dòng) |
| `model.ipynb` | Chia train/test, Ridge, Random Forest (thư viện + tự cài đặt bằng NumPy), tinh chỉnh, đánh giá, xuất model |

Kết quả hiện tại trên test: Random Forest MAPE 15,5%, Ridge 18,5%, baseline 83,5%.

Project này đã khá chắc chắn. Nó có baseline, cross-validation, nhiều metric,
phân tích lỗi, permutation importance, bootstrap kiểm định, và tự cài đặt lại
Random Forest. **Mục tiêu của lần sửa này không phải viết lại project**, mà chỉ
chỉnh lại thứ tự một số bước xử lý dữ liệu.

---

## 2. Vấn đề cần sửa

Hiện `preprocess_data.ipynb` tính một số **thống kê học từ dữ liệu** trên
**toàn bộ** dataset, rồi mới xuất `clean_data_oto.csv`. Việc chia train/test
diễn ra sau đó, ở `model.ipynb`. Nghĩa là tập test đã góp phần tạo ra các tham
số tiền xử lý — đây là data leakage.

Ba chỗ cụ thể:

1. **Điền thiếu** — trung vị số km theo đời xe, mode kiểu dáng / số chỗ theo dòng xe.
2. **Gộp nhãn hiếm** — đếm tần suất hãng và dòng xe trên toàn dữ liệu để quyết định nhãn nào đủ ngưỡng giữ lại.
3. **Lọc giá trả trước / đặt cọc** — dùng trung vị **giá** (biến mục tiêu) của nhóm cùng hãng–dòng–năm trên toàn dữ liệu để quyết định xóa dòng.

Chỗ thứ 3 nghiêm trọng nhất vì nó dùng biến mục tiêu và nó **xóa dòng khỏi
tập test**.

---

## 3. Nguyên tắc phân loại

Dùng nguyên tắc này để quyết định mỗi bước thuộc giai đoạn nào. **Không áp dụng
máy móc "mọi thứ phải làm sau khi chia"** — sẽ làm phức tạp code một cách vô ích.

### 3.1. Làm TRƯỚC khi chia (không gây leakage)

Bước nào xử lý **từng dòng độc lập**, hoặc dùng **ngưỡng cứng từ kiến thức
nghiệp vụ**, thì không học gì từ dữ liệu, nên làm trước khi chia và áp dụng cho
cả hai tập:

- Ép kiểu, đổi `N/A` / `Đang cập nhật` thành `NaN`
- Xóa dòng trùng lặp (**phải** làm trước khi chia, nếu không bản sao nằm ở cả hai tập)
- Loại lỗi theo quy tắc cứng: giá < 20 triệu hoặc > 10 tỷ, giá giả dạng `123.456.789`, km > 500.000, km/năm > 100.000
- Sửa nhãn theo quy tắc cứng: `condition_ad == "Mới"` nhưng `age > 3` → `"Đã sử dụng"`
- Xóa dòng thiếu biến mục tiêu
- Điền bằng **hằng số**: km xe mới = 0, `carorigin` thiếu → `"Không rõ"`
- Tạo cờ `mileage_missing` (chỉ là `isna()` trên từng dòng)
- Trích `province` từ URL
- Biến đổi tất định biến mục tiêu: `price_log = log(price_tr)`
- Tạo `age = 2026 - mfdate`

### 3.2. Làm SAU khi chia (fit trên train, transform cả hai tập)

Bước nào **học tham số từ phân phối dữ liệu**:

- Điền thiếu bằng mean / median / mode
- Gộp nhãn hiếm theo tần suất
- Mã hóa one-hot, ordinal, chuẩn hóa
- Ngưỡng ngoại lệ học từ dữ liệu (IQR, percentile, winsorize)
- Chọn đặc trưng, PCA, target encoding
- Oversampling / undersampling (chỉ áp dụng cho train)

### 3.3. Lưu ý riêng về ngoại lệ

Với ngoại lệ phải phân biệt hai hành động, vì chúng khác nhau:

| Hành động | Áp dụng cho test? |
|---|---|
| **Cắt giá trị** (clip, winsorize) theo ngưỡng từ train | Có — đây là một phép transform |
| **Xóa dòng** theo ngưỡng học từ dữ liệu | **Không** — chỉ xóa ở train. Test phải giữ phân phối thật |
| **Xóa dòng** theo quy tắc cứng (giá trị không thể xảy ra) | Có — những dòng này không phải quan sát hợp lệ |

---

## 4. KHÔNG được sửa những phần sau

Những phần này **đang đúng**. Sửa chúng sẽ làm project xấu đi.

1. **Các quy tắc loại lỗi cứng** ở mục 5 của `preprocess_data.ipynb` (giá < 20 triệu, giá giả, km vô lý, xe "Mới" quá 3 năm tuổi). Đây là ngưỡng nghiệp vụ, không học từ dữ liệu. Giữ nguyên và vẫn áp dụng cho cả hai tập.

2. **Kiểm tra IQR trên log giá** ở mục 5 — notebook đã ghi rõ *chỉ để tham khảo, không xóa dòng*. Giữ nguyên, **không** biến nó thành bước lọc.

3. **`log(price_tr)`, `age`, `km_per_year`** — biến đổi tất định bằng công thức, không gây leakage. Không cần chuyển đi đâu. Riêng `km_per_year` phải tính **sau** khi điền km (xem việc 1).

4. **Hàm `cv_rf` ở `model.ipynb` mục 3 và `cv_mape` ở `preprocess_data.ipynb` mục 7.4** — hai hàm này **đã** fit preprocessor trong từng fold rồi. Đừng "sửa" chúng.

5. **Toàn bộ phần Random Forest tự cài đặt bằng NumPy** (`Binner`, `RegressionTreeScratch`, `RandomForestScratch`) — không đổi thuật toán, không đổi tham số.

6. **Mọi thí nghiệm hiện có**: so sánh one-hot vs ordinal, so sánh cách gộp nhãn, thí nghiệm vị trí, thí nghiệm log giá và mất cân bằng, so sánh cây vs rừng, bootstrap, permutation importance, đường khấu hao, phân tích tin đăng lại. Giữ hết. Chỉ cập nhật con số sau khi chạy lại.

7. **Việc dùng tập test** ở các mục 5.2, 5.5, 7.x, 8.2, 8.3, 10.1 — đều là báo cáo kết quả, kiểm tra tính đúng của code, hoặc diễn giải mô hình đã chốt. Không có quyết định chọn mô hình hay tham số nào dựa trên test. **Không** cần tạo thêm tập dữ liệu mới.

8. **Không thêm thuật toán mới** (XGBoost, LightGBM, neural network). Mục tiêu lần này chỉ là thứ tự xử lý dữ liệu.

9. `random_state = 42` ở mọi nơi. Không đổi, để so sánh được với kết quả cũ.

10. **Toàn bộ phần markdown giải thích** trong hai notebook. Đây là nội dung báo cáo. Chỉ sửa khi nội dung không còn đúng (xem mục 6).

---

## 5. Danh sách việc cần làm

Làm theo thứ tự. Sau mỗi việc, chạy lại notebook và xác nhận không lỗi.

> Số mục tham chiếu theo tiêu đề markdown trong notebook (ví dụ "mục 6"), không
> theo chỉ số cell, vì chỉ số sẽ thay đổi khi thêm bớt cell. Định vị code bằng
> nội dung, không bằng số thứ tự.

### Việc 1 — Tạo file `src/car_transformers.py`

Dùng nguyên file `car_transformers.py` kèm theo tài liệu này. File đã được test,
chứa hai class:

- `CarImputer` — điền thiếu, học `km_by_year_`, `km_global_`, `type_by_model_`, `seats_by_model_`, `seats_by_brand_`, `seats_global_` trong `fit`. Tạo thêm `mileage_missing`, `age`, `km_per_year`.
- `BrandModelGrouper` — gộp nhãn hiếm, học `keep_brand_`, `keep_model_` trong `fit`. Tạo thêm `carbrand_grp`, `carmodel_grp`. Nhãn chưa từng thấy ở train tự rơi về nhóm "khác" tương ứng.

Hai class này tương thích sklearn `Pipeline`, nên mỗi fold cross-validation tự
fit lại.

**Lưu ý một thay đổi nhỏ so với code cũ:** trong `CarImputer`, việc lọc bỏ
`"Dòng khác"` được làm **trước** `groupby` (`specific = X[X["carmodel"] != "Dòng khác"]`),
thay vì `transform` rồi `reindex` như hàm `fill_by_group_mode` hiện tại. Kết quả
tương đương nhưng không phụ thuộc vào index của frame, nên an toàn khi chạy
trong fold.

### Việc 2 — Bỏ các bước học-từ-dữ-liệu khỏi `preprocess_data.ipynb`

Xóa khỏi notebook (chuyển trách nhiệm sang transformer):

- **Mục 6**, phần điền `mileage_km` cho xe **đã dùng** bằng `med_by_year`. **Giữ lại** phần điền 0 km cho xe mới và phần tạo cờ `mileage_missing`.
- **Mục 6**, toàn bộ hàm `fill_by_group_mode` và các lời gọi cho `carseats`, `cartype`. **Giữ lại** phần `carorigin` → `"Không rõ"` (nhãn hằng, không học gì).
- **Mục 7.2**, hàm `group_hierarchical` và hai cột `carbrand_grp`, `carmodel_grp`.
- **Mục 7.3**, dòng tính `km_per_year` (chuyển vào `CarImputer` vì phụ thuộc km đã điền).

Giữ lại biểu đồ ở mục 6 (tỉ lệ thiếu của từng cột và cách xử lý) — nó mô tả
phân tích giá trị thiếu, vẫn đúng. Sửa chú thích để nói rõ việc điền được thực
hiện ở bước mô hình.

### Việc 3 — Sửa quy tắc lọc giá đặt cọc (mục 5.1)

Có **hai lỗi** trong cell này. Sửa cả hai.

**Lỗi a — bug logic, độc lập với leakage.** Code hiện tại:

```python
grp = df.groupby(["carbrand", "carmodel", "mfdate"])["price_tr"]
```

Nhóm này gộp cả các dòng có `carmodel == "Dòng khác"`, vốn trộn nhiều xe không
liên quan, nên trung vị của nhóm đó vô nghĩa và có thể loại oan xe rẻ có thật.
Loại trừ `"Dòng khác"` khỏi quy tắc này, giống cách `CarImputer` làm.

**Lỗi b — leakage.** Trung vị giá được tính trên toàn bộ dữ liệu, trong đó có
biến mục tiêu của test. Chọn **một** trong hai hướng:

- **Hướng ưu tiên:** chuyển quy tắc này ra sau khi chia. Tính bảng trung vị nhóm **trên train**, rồi dùng bảng đó để đánh dấu dòng nghi vấn ở cả train và test. Xóa dòng bị đánh dấu ở **cả hai tập** — vì đây là **sửa lỗi nhãn**, không phải cắt ngoại lệ thống kê, và để một nhãn sai nằm trong test thì MAPE không còn đo được chất lượng mô hình.
- **Hướng đơn giản:** giữ nguyên vị trí hiện tại, nhưng thêm một ô markdown nói rõ rằng quy tắc này dùng biến mục tiêu trên toàn dữ liệu, chấp nhận vì mục đích là sửa nhãn sai, và đây là hạn chế đã biết.

Nếu chọn hướng ưu tiên, **phải báo trước cho người dùng** rằng MAPE sẽ thay đổi
(xem mục 7).

### Việc 4 — Chia train/test trong `preprocess_data.ipynb` và xuất hai file

Thêm vào cuối notebook, thay cho việc xuất một file `clean_data_oto.csv`:

```python
from sklearn.model_selection import train_test_split

SEG_BINS = [0, 200, 500, 1000, 2000, np.inf]
SEG_LABELS = ["< 200 triệu", "200-500", "500-1.000", "1-2 tỷ", "> 2 tỷ"]
segment = pd.cut(clean["price_tr"], bins=SEG_BINS, labels=SEG_LABELS, right=False).astype(str)

train, test = train_test_split(clean, test_size=0.2, stratify=segment,
                               random_state=RANDOM_STATE)
train.to_csv("clean_train.csv", index=False)
test.to_csv("clean_test.csv", index=False)
```

Yêu cầu:

- Dùng đúng `test_size=0.2`, `stratify` theo phân khúc giá, `random_state=42` như `model.ipynb` hiện tại, để kết quả so sánh được với lần chạy cũ.
- **Vẫn xuất thêm `clean_data_oto.csv`** (toàn bộ dữ liệu đã làm sạch) để các phần phân tích mô tả và vẽ biểu đồ trong báo cáo dùng được.
- Hai file train/test **còn giá trị thiếu** ở `mileage_km` (xe đã dùng), `cartype`, `carseats`. Đó là đúng, không phải lỗi.

### Việc 5 — Sửa các assert ở mục 9 của `preprocess_data.ipynb`

Assert hiện tại sẽ fail vì file đã cố tình còn `NaN`:

```python
assert clean.isna().sum().sum() == 0, "Còn giá trị thiếu"   # SẼ FAIL
```

Thay bằng kiểm tra theo từng cột:

```python
MUST_NOT_BE_NULL = ["price_tr", "price_log", "carbrand", "carmodel", "condition_ad", "mfdate", "age"]
MAY_BE_NULL = ["mileage_km", "cartype", "carseats"]

assert clean[MUST_NOT_BE_NULL].isna().sum().sum() == 0
assert set(clean.columns[clean.isna().any()]) <= set(MAY_BE_NULL)
assert (clean["price_tr"] >= 20).all()
assert np.isfinite(clean["price_log"]).all()
assert not ((clean["condition_ad"] == "Mới") & (clean["age"] > 3)).any()
```

Bỏ assert `(clean.loc[clean["condition_ad"] == "Mới", "mileage_missing"] == 0).all()`
nếu `mileage_missing` không còn ở file xuất, hoặc giữ nếu vẫn tạo nó ở
preprocess. Cập nhật `FINAL_COLS` cho khớp với các cột thực sự còn lại
(bỏ `carbrand_grp`, `carmodel_grp`, `km_per_year`).

### Việc 6 — Đọc hai file và dựng Pipeline trong `model.ipynb`

Thay phần đọc dữ liệu và chia tập hiện tại (mục 1) bằng:

```python
import sys; sys.path.insert(0, "../src")
from car_transformers import CarImputer, BrandModelGrouper

tr = pd.read_csv("clean_train.csv")
te = pd.read_csv("clean_test.csv")
```

Không chia lại trong `model.ipynb` nữa — việc chia đã làm ở preprocess.

Giữ nguyên định nghĩa `CAT`, `NUM_TREE`, `NUM_LIN`, `SEG_LABELS`, `group_key`,
và các biến `y_tr`, `y_te`, `p_tr`, `p_te`, `seg_tr`, `seg_te`.

Định nghĩa pipeline cho từng loại mô hình:

```python
def make_pipeline(kind, model):
    num = ("num", "passthrough", NUM_TREE) if kind == "tree" else ("num", StandardScaler(), NUM_LIN)
    return Pipeline([
        ("impute", CarImputer()),
        ("group", BrandModelGrouper(brand_min=30, model_min=10)),
        ("encode", ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore",
                                                            sparse_output=False), CAT), num])),
        ("model", model),
    ])
```

Với Ridge, hai đặc trưng `age_sq`, `log_km`, `log_km_per_year` phụ thuộc vào
`age` và `mileage_km` đã điền, nên **không** tính được ở bước đọc file. Thêm một
transformer nhỏ vào pipeline của Ridge để tạo chúng sau `CarImputer`, hoặc mở
rộng `CarImputer` bằng tham số `add_linear_features=True`. Chọn cách nào cũng
được, miễn là các cột này được tạo **sau** khi điền thiếu.

### Việc 7 — Bọc hai lần tìm kiếm tham số bằng Pipeline

**Random Forest** (mục 4.2) — hiện truyền ma trận `XT_tr` đã fit sẵn:

```python
param_dist = {
    "model__n_estimators": [300],
    "model__max_depth": [20, 30, None],
    "model__min_samples_leaf": [1, 2, 3, 5],
    "model__max_features": [0.33, 0.5, 0.8],
}
rs_rf = RandomizedSearchCV(
    make_pipeline("tree", RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1)),
    param_dist, n_iter=12, cv=folds3,
    scoring="neg_root_mean_squared_error", random_state=RANDOM_STATE, n_jobs=1)
rs_rf.fit(tr, y_tr)
```

Chú ý `folds3` phải được tạo lại bằng `StratifiedKFold(3, ...).split(tr, seg_tr)`
thay vì `split(XT_tr, seg_tr)`.

**Ridge** (mục 6) — tương tự, `{"model__alpha": np.logspace(-3, 3, 25)}`.

Sau khi tìm được tham số tốt nhất, `rs_rf.best_params_` sẽ có tiền tố `model__`.
Khi dùng lại để khởi tạo `RandomForestRegressor` trực tiếp (ví dụ trong các thí
nghiệm ở mục 9), phải bỏ tiền tố:

```python
best_rf = {k.replace("model__", ""): v for k, v in rs_rf.best_params_.items()}
```

### Việc 8 — Sửa phần Random Forest tự cài đặt

Bản tự cài đặt nhận ma trận NumPy, không nhận DataFrame, nên không bọc vào
`Pipeline` được. Cách xử lý:

```python
prep_tree = make_pipeline("tree", "passthrough")[:-1]   # bỏ bước model
XT_tr = prep_tree.fit_transform(tr)
XT_te = prep_tree.transform(te)
```

Nghĩa là fit bộ tiền xử lý **một lần trên toàn bộ train**, rồi dùng ma trận đó
cho `RandomForestScratch`. Điều này chấp nhận được, nhưng phải ghi chú trong ô
markdown của mục 5.3 rằng:

- OOB của bản tự cài đặt được tính sau khi bộ tiền xử lý và `Binner` đã fit trên toàn bộ train, nên các mẫu out-of-bag vẫn ảnh hưởng tới ngưỡng bin và danh sách nhãn one-hot.
- Đây không phải leakage từ biến mục tiêu, nhưng OOB không hoàn toàn độc lập. Dùng nó để **so sánh các cấu hình với nhau**, không coi là ước lượng tổng quát hóa.

Giữ nguyên cách tinh chỉnh bằng OOB ở mục 5.3 — không chuyển sang CV, vì bản tự
viết chạy chậm.

### Việc 9 — Sửa `metadata.json` và `price_model.py` (mục 11)

Hiện các bảng tra được xây từ `df` (toàn bộ dữ liệu):

```python
"brand_group": df.groupby("carbrand")["carbrand_grp"].first().to_dict(),
"model_group": ...,
"mileage_median_by_year": {int(k): float(v) for k, v in km_med.items()},
```

Phải lấy từ transformer **đã fit trên train** thay vì từ `df`. Sau khi
`rs_rf.best_estimator_` được fit, lấy ra:

```python
imp = rs_rf.best_estimator_.named_steps["impute"]
grp = rs_rf.best_estimator_.named_steps["group"]

metadata = {
    ...
    "mileage_median_by_year": {int(k): float(v) for k, v in imp.km_by_year_.items()},
    "mileage_median_all": float(imp.km_global_),
    "keep_brand": sorted(grp.keep_brand_),
    "keep_model": sorted(grp.keep_model_),
    "brand_min": grp.brand_min,
    "model_min": grp.model_min,
    ...
}
```

Sửa `price_model.py` để dựng `carbrand_grp` / `carmodel_grp` từ `keep_brand`,
`keep_model` và danh sách `luxury_brands` theo đúng logic của
`BrandModelGrouper`, thay vì tra bảng mapping cứng. Cách này xử lý được cả nhãn
chưa từng thấy.

Giữ nguyên bài kiểm tra ở cuối mục 11 (nạp lại model, dự đoán phải trùng khớp
với notebook). Nó phải vẫn pass.

### Việc 10 — Thêm mục EDA riêng vào `preprocess_data.ipynb`

Hiện project chỉ có histogram phân phối và phân tích giá trị thiếu, nằm lẫn
trong các bước xử lý. Thêm một mục EDA độc lập (đặt sau mục làm sạch, trước
feature engineering), gồm tối thiểu:

- Giá theo tuổi xe (scatter hoặc boxplot theo nhóm tuổi)
- Giá trung vị theo hãng (top 15 hãng nhiều tin nhất)
- Giá theo số km
- Ma trận tương quan giữa các biến số (`age`, `mileage_km`, `km_per_year`, `carseats`, `price_log`)
- Phân phối giá theo `cartype` và `gearbox`

Mỗi biểu đồ kèm 1–2 câu nhận xét, và nếu nhận xét đó dẫn tới một quyết định ở
bước sau thì nói rõ. Dùng cùng style biểu đồ đã có (hàm `save`, màu `BLUE` /
`ORANGE`, tiêu đề `loc="left"`).

EDA được phép dùng **toàn bộ** dữ liệu đã làm sạch, vì nó chỉ để mô tả và định
hướng, không sinh ra tham số nào đi vào mô hình. Nói rõ điều này trong một ô
markdown.

### Việc 11 — Thêm learning curve (mục 7 của `model.ipynb`)

Thêm `sklearn.model_selection.learning_curve` cho Random Forest với tham số tốt
nhất, chạy trên train với 5-fold CV, trục x là số mẫu train. Vẽ hai đường
train score và validation score, kèm nhận xét chẩn đoán bias / variance và nhận
xét về việc thêm dữ liệu có khả năng giúp gì không.

---

## 6. Cập nhật phần văn bản

Sau khi sửa code và chạy lại, **mọi con số trong các ô markdown đều phải cập
nhật**. Những chỗ chứa số liệu cần soát:

| Vị trí | Nội dung cần soát |
|---|---|
| `preprocess_data.ipynb` mục 7.4 | kết quả so sánh 3 phương án gộp nhãn |
| `preprocess_data.ipynb` mục 7.4 (vị trí) | kết luận về miền / tỉnh thành |
| `preprocess_data.ipynb` bảng tóm tắt cuối | các bước và kết quả |
| `model.ipynb` mục 3 | kết luận one-hot vs mã số thứ tự |
| `model.ipynb` mục 7.x | toàn bộ bảng kết quả test, MAPE theo phân khúc |
| `model.ipynb` mục 7.3 | khoảng tin cậy bootstrap, kết luận có ý nghĩa thống kê hay không |
| `model.ipynb` mục 8.2 | thứ hạng permutation importance |
| `model.ipynb` mục 9.1 | kết luận log giá và các kỹ thuật cân bằng |
| `model.ipynb` mục 10 | tỉ lệ tin có bản sao, chênh lệch StratifiedKFold vs StratifiedGroupKFold |
| `model.ipynb` mục 12 | bảng kết quả tổng và kết luận |

Thêm vào `preprocess_data.ipynb` một ô markdown mới, đặt ngay trước bước chia
train/test, giải thích:

- Vì sao các bước làm sạch ở trên làm được trước khi chia (quy tắc cứng, xử lý từng dòng).
- Vì sao điền thiếu và gộp nhãn phải chuyển sang sau khi chia.
- Vì sao `clean_train.csv` và `clean_test.csv` vẫn còn giá trị thiếu.

Đoạn này là phần trả lời trực tiếp cho câu hỏi về quy trình, nên viết rõ ràng,
có thể đưa thẳng vào báo cáo.

---

## 7. Kỳ vọng về số liệu sau khi sửa

**Quan trọng — đọc trước khi báo cáo kết quả.**

Sau khi sửa, MAPE trên test **có thể tăng lên**, và điều đó là **bình thường**,
không phải dấu hiệu code sai. Lý do:

1. Nếu làm theo hướng ưu tiên ở việc 3, quy tắc lọc giá đặt cọc chỉ còn học từ train, nên một số tin rao **giá trả trước** trước đây bị xóa khỏi test giờ sẽ được giữ lại. Mục 7.2 của notebook đã chứng minh những tin này chiếm phần lớn trong 10 xe bị đoán sai nặng nhất. Test khó hơn, nên MAPE tăng.
2. Điền thiếu và gộp nhãn giờ chỉ dùng thống kê của train, nên bớt đi phần lạc quan.

Mức thay đổi dự kiến: MAPE của Random Forest đi từ 15,5% lên khoảng
**16–18%**, tùy hướng xử lý ở việc 3. Thứ hạng giữa các mô hình
(Random Forest < Ridge < baseline) **không nên đổi**. Nếu thứ hạng đổi, hoặc
MAPE nhảy lên trên 25%, thì có lỗi trong code — dừng lại và kiểm tra.

Khi báo cáo, nói rõ với người dùng:

- Con số cũ và con số mới.
- Con số mới cao hơn vì tập test khó hơn và quy trình chặt hơn, **không** vì mô hình kém đi.
- Nếu muốn so sánh công bằng với con số cũ, chạy thêm một lần với cấu hình cũ và đặt hai kết quả cạnh nhau.

---

## 8. Tiêu chí hoàn thành

Chỉ báo cáo xong khi tất cả các điểm sau đều đạt:

- [ ] Cả ba notebook chạy lại **từ đầu đến cuối** không lỗi, theo thứ tự `crawl` (bỏ qua, không chạy lại) → `preprocess` → `model`.
- [ ] `preprocess_data.ipynb` xuất ba file: `clean_data_oto.csv`, `clean_train.csv`, `clean_test.csv`.
- [ ] Không còn chỗ nào trong `preprocess_data.ipynb` tính `median`, `mode` hoặc `value_counts()` ngưỡng trên toàn bộ dữ liệu rồi đưa kết quả vào file xuất.
- [ ] `grep` trong `model.ipynb` không còn `prep.fit_transform(tr)` nằm trước một lệnh `GridSearchCV` / `RandomizedSearchCV` nào (trừ trường hợp bản tự cài đặt ở việc 8, đã ghi chú).
- [ ] Bài kiểm tra nạp lại model ở cuối mục 11 vẫn pass với `rtol=1e-9`.
- [ ] Mọi con số trong markdown khớp với output thực tế của lần chạy cuối.
- [ ] Mục EDA mới có ít nhất 5 biểu đồ, mỗi biểu đồ có nhận xét.
- [ ] Có learning curve.
- [ ] Không có thuật toán mới nào được thêm vào.
- [ ] `random_state = 42` ở mọi nơi.

Cuối cùng, viết một bảng ngắn so sánh **trước / sau** cho các chỉ số chính
(MAPE tổng, MAPE từng phân khúc, R² log, ±20%) của Ridge và Random Forest, kèm
một đoạn giải thích chênh lệch đến từ đâu.

---

## 9. Thứ tự ưu tiên nếu không làm hết

Nếu bị giới hạn thời gian, làm theo thứ tự này. Mỗi mức đều để lại project ở
trạng thái chạy được.

1. Việc 1, 2, 4, 5, 6 — chuyển điền thiếu và gộp nhãn sang sau khi chia. Đây là phần cốt lõi.
2. Việc 3 lỗi a — sửa bug `"Dòng khác"` trong quy tắc lọc giá đặt cọc. Rẻ và sửa một lỗi logic thật.
3. Việc 10 — thêm mục EDA. Đây là bước thiếu hẳn so với quy trình chuẩn.
4. Việc 7, 9 — bọc Pipeline cho tìm kiếm tham số, sửa metadata.
5. Việc 3 lỗi b, việc 8, việc 11 — phần còn lại.
