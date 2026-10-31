# Hướng dẫn sửa code: tách tiền xử lý và xử lý dữ liệu, chuẩn hóa thứ tự chia tập

> Tài liệu dành cho AI agent thực hiện việc sửa code.
>
> **Đọc hết mục 1 đến 4 trước khi sửa bất cứ dòng nào.** Mục 4 liệt kê những thứ
> **không được sửa** — đây là phần quan trọng nhất để tránh làm hỏng những phần
> đang đúng.
>
> **Phạm vi:** sửa chủ yếu ở `preprocess_data.ipynb` và một notebook mới
> `process_data.ipynb`. Phần `model.ipynb` chỉ sửa **4 chỗ mang tính kỹ thuật**
> ở phần C — không đổi thuật toán, không đổi tham số, không đổi thí nghiệm nào.
> Phần D xuất biểu đồ và bảng cho slide báo cáo.
>
> **Việc đầu tiên phải làm là việc D0** (lưu kết quả hiện tại), vì sau khi sửa
> code sẽ không lấy lại được số liệu của phiên bản cũ để so sánh.

---

## 1. Bối cảnh project

Project dự đoán **giá rao bán ô tô** (triệu đồng) từ tin đăng trên Chợ Tốt.
Bài toán hồi quy có giám sát, biến mục tiêu là `ln(giá)`, thước đo chính là MAPE.

| File hiện tại | Nội dung |
|---|---|
| `crawl_data.ipynb` | Thu thập 14.835 tin từ `xe.chotot.com`, xuất `raw_data_oto.csv` |
| `preprocess_data.ipynb` | Làm sạch, điền thiếu, gộp nhãn, xuất `clean_data_oto.csv` (13.937 dòng) |
| `model.ipynb` | Chia train/test, Ridge, Random Forest (thư viện + tự cài đặt bằng NumPy), tinh chỉnh, đánh giá, xuất model |

Kết quả hiện tại trên test: Random Forest MAPE 15,5%, Ridge 18,5%, baseline 83,5%.

Project này đã khá chắc chắn: có baseline, cross-validation, nhiều metric, phân
tích lỗi, permutation importance, bootstrap kiểm định, và tự cài đặt lại Random
Forest. **Mục tiêu lần này không phải viết lại project**, mà chỉ chỉnh thứ tự
một số bước xử lý dữ liệu và tách trách nhiệm giữa các notebook.

---

## 2. Vấn đề cần sửa

`preprocess_data.ipynb` hiện tính một số **thống kê học từ dữ liệu** trên
**toàn bộ** dataset rồi mới xuất file. Việc chia train/test diễn ra sau đó, ở
`model.ipynb`. Nghĩa là tập test đã góp phần tạo ra tham số tiền xử lý — đây là
data leakage.

Ba chỗ cụ thể:

1. **Điền thiếu** — trung vị số km theo đời xe, mode kiểu dáng / số chỗ theo dòng xe.
2. **Gộp nhãn hiếm** — đếm tần suất hãng và dòng xe trên toàn dữ liệu để quyết định nhãn nào đủ ngưỡng giữ lại.
3. **Lọc giá trả trước / đặt cọc** — dùng trung vị **giá** (biến mục tiêu) của nhóm cùng hãng–dòng–năm trên toàn dữ liệu để quyết định xóa dòng.

Chỗ thứ 3 nghiêm trọng nhất vì nó dùng biến mục tiêu và nó **xóa dòng khỏi tập test**.

---

## 3. Cấu trúc mới

Tách thành bốn notebook, mỗi notebook một trách nhiệm rõ ràng:

```
crawl_data.ipynb
  │  (không chạy lại, không sửa)
  ▼
raw_data_oto.csv
  │
  ▼
preprocess_data.ipynb        ─── TIỀN XỬ LÝ: chỉ quy tắc cứng, xử lý từng dòng
  │   ép kiểu, N/A → NaN, xóa dòng trùng,
  │   loại lỗi theo ngưỡng nghiệp vụ, xóa dòng thiếu price,
  │   điền hằng số (km xe mới = 0, carorigin = "Không rõ"),
  │   trích province, tạo age, log(price), EDA
  ▼
preprocess_data.csv          ← CÒN NaN ở mileage_km (xe cũ), cartype, carseats
  │
  ▼
process_data.ipynb  (MỚI)    ─── XỬ LÝ DỮ LIỆU: chia tập, fit trên train
  │   1. chia train/test (stratify phân khúc giá, random_state = 42)
  │   2. fit CarImputer + BrandModelGrouper trên TRAIN
  │   3. transform cả train và test bằng tham số đã học
  │   4. lọc giá đặt cọc theo bảng trung vị học từ train
  │   5. tạo đặc trưng cho Ridge (age_sq, log_km, log_km_per_year)
  │   6. cell đối chứng: so CV điền-sẵn với CV điền-trong-fold
  ▼
train_data.csv  +  test_data.csv  +  model/data_transformers.joblib
  │
  ▼
model.ipynb                  ─── MÔ HÌNH: chỉ encode, chuẩn hóa, train, đánh giá
      đọc hai file, one-hot + scaler, Ridge / RF / RF tự cài đặt,
      tinh chỉnh, đánh giá, xuất model
```

### Trách nhiệm từng file

| File | Được phép dùng | Không được làm |
|---|---|---|
| `preprocess_data.ipynb` | toàn bộ dữ liệu | mọi thống kê học từ dữ liệu (median, mode, ngưỡng tần suất) nếu kết quả đi vào file xuất |
| `process_data.ipynb` | train để fit, test chỉ transform | fit bất cứ thứ gì trên test |
| `model.ipynb` | train để fit, test chỉ để đánh giá cuối | dùng kết quả test để chọn mô hình hay tham số |

---

## 4. Nguyên tắc phân loại

Dùng nguyên tắc này để quyết định mỗi bước thuộc notebook nào. **Không áp dụng
máy móc "mọi thứ phải làm sau khi chia"** — sẽ làm phức tạp code một cách vô ích.

### 4.1. Thuộc `preprocess_data.ipynb` (không gây leakage)

Bước nào xử lý **từng dòng độc lập**, hoặc dùng **ngưỡng cứng từ kiến thức
nghiệp vụ**, thì không học gì từ dữ liệu:

- Ép kiểu, đổi `N/A` / `Đang cập nhật` thành `NaN`
- Xóa dòng trùng lặp (**phải** ở đây, nếu không bản sao nằm ở cả hai tập)
- Loại lỗi theo quy tắc cứng: giá < 20 triệu hoặc > 10 tỷ, giá giả dạng `123.456.789`, km > 500.000, km/năm > 100.000
- Sửa nhãn theo quy tắc cứng: `condition_ad == "Mới"` nhưng `age > 3` → `"Đã sử dụng"`
- Xóa dòng thiếu biến mục tiêu
- Điền bằng **hằng số**: km xe mới = 0, `carorigin` thiếu → `"Không rõ"`
- Trích `province` từ URL
- `age = 2026 - mfdate`
- `price_log = log(price_tr)` — biến đổi tất định, không có tham số nào học từ dữ liệu
- EDA (chỉ mô tả, không sinh tham số đi vào mô hình)

### 4.2. Thuộc `process_data.ipynb` (học tham số từ dữ liệu)

- Điền thiếu bằng mean / median / mode
- Gộp nhãn hiếm theo tần suất
- Ngưỡng ngoại lệ học từ dữ liệu (IQR, percentile, winsorize)
- Quy tắc lọc dùng biến mục tiêu (lọc giá đặt cọc)
- Đặc trưng phụ thuộc giá trị đã điền (`km_per_year`, `log_km`, ...)

### 4.3. Thuộc `model.ipynb`

- One-hot, ordinal encoding, chuẩn hóa
- Chọn đặc trưng, tinh chỉnh tham số, oversampling / undersampling (chỉ trên train)

### 4.4. Quy tắc chung cho mọi bước ở 4.2 và 4.3

> **`fit` trên train, `transform` mọi thứ.**

Áp dụng cho cả bốn bước: điền thiếu, gộp nhãn hiếm, mã hóa, chuẩn hóa.

**Tuyệt đối không chuẩn hóa hay mã hóa hai tập riêng biệt.** Đây là lỗi dễ mắc
nhất ở bước này, nên nói rõ:

| Lời gọi | Ý nghĩa | Dùng cho |
|---|---|---|
| `.fit_transform(tr)` | học tham số từ `tr`, rồi biến đổi `tr` | **train, một lần duy nhất** |
| `.transform(te)` | chỉ biến đổi, dùng tham số đã học | **test, và mọi dữ liệu mới** |
| `.fit_transform(te)` | học lại tham số từ test | **SAI, không bao giờ dùng** |

Vì sao chuẩn hóa riêng là sai: nếu train có `age` trung bình 8 và độ lệch chuẩn
4, còn test tình cờ nhiều xe đời mới hơn nên trung bình 6 và độ lệch chuẩn 3,
thì một chiếc xe 12 tuổi vào mô hình với giá trị `(12−8)/4 = 1,0` ở train nhưng
`(12−6)/3 = 2,0` ở test. Cùng một chiếc xe, hai con số khác nhau. Mô hình đã học
rằng `1,0` nghĩa là xe 12 tuổi, giờ nhận `2,0` và hiểu thành xe già hơn nhiều.

Cách nghĩ cho đúng: `mean` và `std` của scaler là **tham số học được**, giống
trọng số của Ridge. Không học lại trọng số trên test thì cũng không học lại
`mean` và `std` trên test. Thêm một lập luận: khi triển khai thật chỉ có **một**
chiếc xe cần định giá, không thể tính `mean` / `std` từ một dòng — nếu quy trình
đòi phải chuẩn hóa riêng từng tập thì nó không chạy được ngoài thực tế.

Code hiện tại ở mục 1 của `model.ipynb` **đã làm đúng** điều này
(`prep_lin.fit_transform(tr)` rồi `prep_lin.transform(te)`). Giữ nguyên, đừng
sửa thành bất cứ dạng nào khác.

### 4.4. Lưu ý riêng về ngoại lệ

Với ngoại lệ phải phân biệt hai hành động, vì chúng khác nhau:

| Hành động | Áp dụng cho test? |
|---|---|
| **Cắt giá trị** (clip, winsorize) theo ngưỡng từ train | Có — đây là một phép transform |
| **Xóa dòng** theo ngưỡng thống kê học từ dữ liệu | **Không** — chỉ xóa ở train. Test phải giữ phân phối thật |
| **Xóa dòng** theo quy tắc cứng (giá trị không thể xảy ra) | Có — những dòng này không phải quan sát hợp lệ |
| **Xóa dòng** vì **nhãn sai** (giá đặt cọc) | Có — để nhãn sai trong test thì MAPE không còn đo được chất lượng mô hình |

---

## 5. KHÔNG được sửa những phần sau

Những phần này **đang đúng**. Sửa chúng sẽ làm project xấu đi.

1. **Các quy tắc loại lỗi cứng** ở mục 5 của `preprocess_data.ipynb` (giá < 20 triệu, giá giả, km vô lý, xe "Mới" quá 3 năm tuổi). Ngưỡng nghiệp vụ, không học từ dữ liệu. Giữ nguyên vị trí, vẫn áp dụng cho toàn bộ dữ liệu.

2. **Kiểm tra IQR trên log giá** ở mục 5 — notebook đã ghi rõ *chỉ để tham khảo, không xóa dòng*. Giữ nguyên, **không** biến nó thành bước lọc.

3. **`log(price_tr)` và `age`** — biến đổi tất định bằng công thức. Giữ ở `preprocess_data.ipynb`.

4. **Hàm `cv_rf` ở `model.ipynb` mục 3 và `cv_mape` ở `preprocess_data.ipynb` mục 7.4** — hai hàm này **đã** fit preprocessor trong từng fold rồi. Đừng "sửa" chúng.

5. **Toàn bộ phần Random Forest tự cài đặt bằng NumPy** (`Binner`, `RegressionTreeScratch`, `RandomForestScratch`) — không đổi thuật toán, không đổi tham số, không bọc vào Pipeline.

6. **Cách tinh chỉnh tham số hiện tại**: `RandomizedSearchCV` cho Random Forest, `GridSearchCV` cho Ridge, OOB cho bản tự cài đặt. Giữ nguyên cả phương pháp và không gian tham số. **Không** bọc chúng vào `Pipeline` — việc điền thiếu và gộp nhãn đã xử lý xong ở `process_data.ipynb`.

7. **Mọi thí nghiệm hiện có**: so sánh one-hot vs ordinal, so sánh cách gộp nhãn, thí nghiệm vị trí, thí nghiệm log giá và mất cân bằng, so sánh cây vs rừng, bootstrap, permutation importance, đường khấu hao, phân tích tin đăng lại. Giữ hết. Chỉ cập nhật con số sau khi chạy lại.

8. **Việc dùng tập test** ở các mục 5.2, 5.5, 7.x, 8.2, 8.3, 10.1 của `model.ipynb` — đều là báo cáo kết quả, kiểm tra tính đúng của code, hoặc diễn giải mô hình đã chốt. Không có quyết định chọn mô hình hay tham số nào dựa trên test. **Không** cần tạo thêm tập dữ liệu mới.

9. **Không thêm thuật toán mới** (XGBoost, LightGBM, neural network).

10. `random_state = 42` ở mọi nơi. Không đổi, để so sánh được với kết quả cũ.

11. **Toàn bộ phần markdown giải thích** trong các notebook. Đây là nội dung báo cáo. Chỉ sửa khi nội dung không còn đúng (xem mục 8).

---

## 6. Việc cần làm

> Số mục tham chiếu theo **tiêu đề markdown** trong notebook (ví dụ "mục 6"),
> không theo chỉ số cell, vì chỉ số sẽ thay đổi khi thêm bớt cell. Định vị code
> bằng nội dung, không bằng số thứ tự.

### Việc 0 — Tạo `src/car_transformers.py`

Dùng nguyên file `car_transformers.py` kèm theo tài liệu này. File đã được test,
chứa hai class tương thích sklearn:

- **`CarImputer`** — điền thiếu. `fit` học `km_by_year_`, `km_global_`, `type_by_model_`, `seats_by_model_`, `seats_by_brand_`, `seats_global_`. `transform` tạo thêm `mileage_missing`, `age`, `km_per_year`.
- **`BrandModelGrouper`** — gộp nhãn hiếm theo cấp. `fit` học `keep_brand_`, `keep_model_`. `transform` tạo `carbrand_grp`, `carmodel_grp`. Nhãn chưa từng thấy ở train tự rơi về nhóm "khác" tương ứng (đã test: `Ferrari` → `"Hãng cao cấp khác"`, dòng xe lạ → `"<hãng> - dòng khác"`).

Chạy `python test_transformers.py` để xác nhận hai class hoạt động trước khi dùng.

**Một thay đổi nhỏ so với code cũ:** trong `CarImputer`, việc lọc bỏ `"Dòng khác"`
được làm **trước** `groupby` (`specific = X[X["carmodel"] != "Dòng khác"]`), thay
vì `transform` rồi `reindex` như hàm `fill_by_group_mode` hiện tại. Kết quả
tương đương nhưng không phụ thuộc index của frame.

---

## PHẦN A — `preprocess_data.ipynb`

### Việc A1 — Bỏ các bước học-từ-dữ-liệu

Xóa khỏi notebook (chuyển trách nhiệm sang `process_data.ipynb`):

| Vị trí | Xóa | Giữ lại |
|---|---|---|
| Mục 6 | phần điền `mileage_km` cho xe **đã dùng** bằng `med_by_year` | phần điền 0 km cho xe mới |
| Mục 6 | hàm `fill_by_group_mode` và các lời gọi cho `carseats`, `cartype` | phần `carorigin` → `"Không rõ"` (nhãn hằng) |
| Mục 6 | cell kiểm tra phân phối `cartype` trước / sau điền | — |
| Mục 7.2 | hàm `group_hierarchical`, hai cột `carbrand_grp`, `carmodel_grp`, hằng `LUXURY_BRANDS`, `BRAND_MIN`, `MODEL_MIN` | — |
| Mục 7.3 | dòng tính `km_per_year` | các dòng `astype(int)` cho `carseats`, `mfdate`, `age` — nhưng `carseats` còn `NaN` nên **bỏ** `astype(int)` của riêng cột này |

Giữ biểu đồ ở mục 6 (tỉ lệ thiếu từng cột và cách xử lý) — nó mô tả phân tích
giá trị thiếu, vẫn đúng và vẫn cần cho báo cáo. Sửa chú thích để nói rõ việc
điền được thực hiện ở `process_data.ipynb`.

### Việc A2 — Bỏ bước lọc giá đặt cọc khỏi mục 5.1

Chuyển toàn bộ cell này sang `process_data.ipynb` (việc B3). Ở
`preprocess_data.ipynb`:

- Xóa cell tính `deposit` và dòng `FUNNEL.append(("Loại giá trả trước / đặt cọc", len(df)))`.
- **Giữ nguyên** ô markdown mục 5.1 giải thích hiện tượng giá đặt cọc, nhưng thêm một câu: quy tắc này được áp dụng ở `process_data.ipynb` sau khi chia tập, dùng bảng trung vị học từ train.

### Việc A3 — Bỏ thí nghiệm ở mục 7.4

Mục 7.4 (kiểm chứng cách gộp nhãn) và phần thử vị trí ngay sau đó phụ thuộc vào
`group_hierarchical` và vào việc chia tập, nên không còn chỗ ở notebook này.

Chuyển **nguyên vẹn** cả hai thí nghiệm sang `process_data.ipynb` (việc B5).
Không đổi logic, không đổi không gian tham số, không đổi hàm `cv_mape` — hàm này
đã fit encoder trong từng fold nên vẫn đúng.

### Việc A4 — Sửa `FINAL_COLS` và các assert ở mục 9

`FINAL_COLS` mới (bỏ `carbrand_grp`, `carmodel_grp`, `km_per_year`, `mileage_missing`):

```python
FINAL_COLS = ["carbrand", "carmodel", "carorigin", "condition_ad",
              "gearbox", "fuel", "cartype", "carseats", "mfdate", "age",
              "mileage_km", "province", "price_tr", "price_log"]
```

Assert cũ sẽ fail vì file cố tình còn `NaN`. Thay bằng:

```python
MUST_NOT_BE_NULL = ["carbrand", "carmodel", "carorigin", "condition_ad",
                    "gearbox", "fuel", "mfdate", "age", "price_tr", "price_log"]
MAY_BE_NULL = ["mileage_km", "cartype", "carseats", "province"]

assert clean[MUST_NOT_BE_NULL].isna().sum().sum() == 0, "Thiếu ở cột không được thiếu"
assert set(clean.columns[clean.isna().any()]) <= set(MAY_BE_NULL), "Có cột thiếu ngoài danh sách cho phép"
assert (clean["price_tr"] >= 20).all() and (clean["price_tr"] <= 10_000).all()
assert np.isfinite(clean["price_log"]).all()
assert not ((clean["condition_ad"] == "Mới") & (clean["age"] > 3)).any()
assert (clean.loc[clean["condition_ad"] == "Mới", "mileage_km"] == 0).all()

print("Số dòng còn thiếu theo cột:")
print(clean[MAY_BE_NULL].isna().sum())
```

Xóa assert `(clean.loc[clean["condition_ad"] == "Mới", "mileage_missing"] == 0).all()`
vì cột này không còn ở file xuất.

### Việc A5 — Đổi tên file xuất

```python
clean.to_csv("preprocess_data.csv", index=False)

check = pd.read_csv("preprocess_data.csv")
print("Đọc lại:", check.shape)
print("Thiếu theo cột:", check.isna().sum()[lambda s: s > 0].to_dict())
```

Thêm một ô markdown ngay trước cell này, giải thích **vì sao file còn giá trị
thiếu**. Đoạn này trả lời trực tiếp câu hỏi về quy trình nên viết rõ, có thể đưa
thẳng vào báo cáo:

- Các bước ở trên dùng được toàn bộ dữ liệu vì chúng xử lý từng dòng độc lập hoặc dùng ngưỡng cứng từ kiến thức thực tế, không học tham số nào từ phân phối dữ liệu.
- Điền thiếu bằng trung vị / mode và gộp nhãn theo tần suất thì khác: chúng học tham số từ dữ liệu, nên phải chờ sau khi chia train/test, fit trên train rồi áp lên test. Nếu làm ở đây, tập test sẽ góp phần tạo ra tham số tiền xử lý, và điểm đánh giá không còn là ước lượng cho dữ liệu mới.
- Vì vậy file này giữ nguyên `NaN` ở `mileage_km` (xe đã dùng), `cartype`, `carseats`.

### Việc A6 — Giữ biểu đồ phễu, cập nhật số

`FUNNEL` giờ không còn bước lọc giá đặt cọc. Biểu đồ ở cuối notebook vẫn vẽ bình
thường, chỉ bớt một thanh. Cập nhật `assert steps["còn lại"].iloc[-1] == len(clean)`
cho khớp, và sửa tiêu đề biểu đồ theo số dòng mới.

Thêm một câu trong ô markdown: bước lọc giá đặt cọc được thực hiện ở
`process_data.ipynb` và sẽ loại thêm một số dòng nữa.

### Việc A7 — Thêm mục EDA riêng

Hiện project chỉ có histogram phân phối và phân tích giá trị thiếu, nằm lẫn
trong các bước xử lý. Đây là bước **thiếu hẳn** so với quy trình chuẩn.

Thêm một mục **"EDA — Phân tích khám phá"** đặt **sau** mục 6 (xử lý giá trị
thiếu) và **trước** mục 7 (biến đổi, tạo đặc trưng), gồm tối thiểu:

1. Giá theo tuổi xe — scatter với trục y log, hoặc boxplot theo nhóm tuổi
2. Giá trung vị theo hãng — barh, top 15 hãng nhiều tin nhất
3. Giá theo số km — scatter, trục y log
4. Ma trận tương quan giữa các biến số: `age`, `mileage_km`, `carseats`, `price_log` (bỏ `km_per_year` vì chưa tạo ở bước này)
5. Phân phối giá theo `cartype` và theo `gearbox` — boxplot

Yêu cầu:

- Mỗi biểu đồ kèm 1–2 câu nhận xét. Nếu nhận xét dẫn tới một quyết định ở bước sau thì nói rõ là quyết định nào.
- Dùng đúng style đã có: hàm `save(fig, name)`, màu `BLUE` / `ORANGE`, tiêu đề `loc="left"`, tên file `p0X_*`.
- Vì `mileage_km` còn `NaN` ở bước này, dùng `.dropna()` khi vẽ và ghi rõ số dòng bị bỏ.
- Thêm một ô markdown nói rõ: EDA được phép dùng toàn bộ dữ liệu đã làm sạch vì nó chỉ để mô tả và định hướng, không sinh ra tham số nào đi vào mô hình.

---

## PHẦN B — `process_data.ipynb` (notebook mới)

Tạo notebook mới. Mở đầu bằng một ô markdown nêu mục đích: chia train/test, học
mọi tham số xử lý dữ liệu **chỉ từ train**, rồi áp lên cả hai tập và xuất ra hai
file cho bước mô hình.

### Việc B1 — Đọc dữ liệu và chia tập

```python
import sys; sys.path.insert(0, "../src")
import numpy as np, pandas as pd, joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from car_transformers import CarImputer, BrandModelGrouper

RANDOM_STATE = 42
SEG_BINS = [0, 200, 500, 1000, 2000, np.inf]
SEG_LABELS = ["< 200 triệu", "200-500", "500-1.000", "1-2 tỷ", "> 2 tỷ"]

df = pd.read_csv("preprocess_data.csv")
df["segment"] = pd.cut(df["price_tr"], bins=SEG_BINS, labels=SEG_LABELS, right=False).astype(str)

tr_raw, te_raw = train_test_split(df, test_size=0.2, stratify=df["segment"],
                                  random_state=RANDOM_STATE)
print(f"train {len(tr_raw)} | test {len(te_raw)}")
```

Thêm ô markdown giải thích **vì sao chia phân tầng theo phân khúc giá**: chia
ngẫu nhiên thông thường có thể để tập test gần như không có xe trên 2 tỷ, khiến
điểm đánh giá nhìn đẹp nhưng không phản ánh khả năng với xe sang.

Chuyển biểu đồ `m01_chia_train_test` từ `model.ipynb` sang đây (so sánh tỉ lệ
phân khúc ở train và test) — nó thuộc về bước chia tập. Giữ nguyên code và style.

### Việc B2 — Fit transformer trên train, transform cả hai tập

```python
imputer = CarImputer().fit(tr_raw)
grouper = BrandModelGrouper(brand_min=30, model_min=10).fit(tr_raw)

def apply_all(frame):
    return grouper.transform(imputer.transform(frame))

tr = apply_all(tr_raw)
te = apply_all(te_raw)
```

Thêm bảng báo cáo số dòng được điền ở mỗi cấp, cho cả train và test, để đối
chiếu với con số trong notebook cũ:

```python
report = {}
for name, before, after in [("train", tr_raw, tr), ("test", te_raw, te)]:
    report[name] = {
        "số dòng": len(after),
        "km được điền": int(after["mileage_missing"].sum()),
        "cartype → Không rõ": int((after["cartype"] == "Không rõ").sum()),
        "carseats được điền": int(before["carseats"].isna().sum()),
        "nhóm hãng": after["carbrand_grp"].nunique(),
        "nhóm dòng xe": after["carmodel_grp"].nunique(),
    }
pd.DataFrame(report).T
```

Thêm ô markdown giải thích: `transform` của test dùng **nguyên** các thống kê đã
học từ train, nên số nhóm ở test có thể ít hơn train, và nhãn chưa từng thấy ở
train sẽ rơi về nhóm "khác" tương ứng. Đó là hành vi đúng.

**Kiểm tra bắt buộc** — thêm assert:

```python
assert set(te["carbrand_grp"]) <= set(tr["carbrand_grp"]), "test sinh nhóm hãng lạ"
assert set(te["carmodel_grp"]) <= set(tr["carmodel_grp"]), "test sinh nhóm dòng xe lạ"
assert tr[["mileage_km", "cartype", "carseats"]].isna().sum().sum() == 0
assert te[["mileage_km", "cartype", "carseats"]].isna().sum().sum() == 0
```

### Việc B3 — Lọc giá đặt cọc, bảng trung vị học từ train

Chuyển cell mục 5.1 từ `preprocess_data.ipynb` sang đây, **sửa hai lỗi**:

**Lỗi a — bug logic, độc lập với leakage.** Code cũ:

```python
grp = df.groupby(["carbrand", "carmodel", "mfdate"])["price_tr"]
```

Nhóm này gộp cả các dòng có `carmodel == "Dòng khác"`, vốn trộn nhiều xe không
liên quan, nên trung vị của nhóm đó vô nghĩa và có thể loại oan xe rẻ có thật.
Phải loại trừ `"Dòng khác"`.

**Lỗi b — leakage.** Trung vị phải học từ train, rồi áp lên cả hai tập.

```python
# Bảng tham chiếu học TỪ TRAIN
ref_src = tr[tr["carmodel"] != "Dòng khác"]
g = ref_src.groupby(["carbrand", "carmodel", "mfdate"])["price_tr"]
ref_median = g.median()
ref_size = g.size()
valid_groups = ref_size[ref_size >= 3].index          # nhóm đủ 3 xe mới tin được

def mark_deposit(frame):
    key = pd.MultiIndex.from_frame(frame[["carbrand", "carmodel", "mfdate"]])
    med = pd.Series(ref_median.reindex(key).values, index=frame.index)
    ok = pd.Series(key.isin(valid_groups), index=frame.index)
    return ok & med.notna() & (frame["price_tr"] < 0.3 * med)

for name in ["train", "test"]:
    pass   # xem bên dưới

dep_tr, dep_te = mark_deposit(tr), mark_deposit(te)
print(f"Loại nghi giá trả trước/đặt cọc: train {dep_tr.sum()}, test {dep_te.sum()}")
tr, te = tr[~dep_tr].reset_index(drop=True), te[~dep_te].reset_index(drop=True)
```

Xóa dòng bị đánh dấu ở **cả hai tập** — vì đây là **sửa lỗi nhãn**, không phải
cắt ngoại lệ thống kê. Để một nhãn sai nằm trong test thì MAPE không còn đo được
chất lượng mô hình.

Thêm ô markdown ghi rõ:

- Bảng trung vị chỉ học từ train, nên quy tắc này không dùng biến mục tiêu của test để quyết định gì.
- Một số tin ở test có nhóm tham chiếu không tồn tại trong train (dòng xe hiếm) thì không bị đánh dấu — đây là hạn chế đã biết, và số tin đó nên được báo cáo.
- So với cách cũ (trung vị trên toàn dữ liệu), số dòng bị loại sẽ **ít hơn**, nên tập test khó hơn và MAPE sẽ tăng. Xem mục 9.

### Việc B4 — Tạo đặc trưng cho Ridge

Ba cột này phụ thuộc giá trị đã điền nên phải tính ở đây, không tính ở
`preprocess_data.ipynb`:

```python
for frame in (tr, te):
    frame["age_sq"] = frame["age"] ** 2
    frame["log_km"] = np.log1p(frame["mileage_km"])
    frame["log_km_per_year"] = np.log1p(frame["km_per_year"])
```

Thêm ô markdown: các biến đổi phi tuyến này chỉ cần cho **mô hình tuyến tính**
(Ridge), để quan hệ cong trở nên gần tuyến tính. Mô hình cây không bị ảnh hưởng
bởi biến đổi đơn điệu nên không dùng chúng — nội dung này đã có ở mục 7.3 của
`preprocess_data.ipynb`, chuyển sang đây.

Cũng tạo lại `group_key` ở đây (dùng cho phân tích tin đăng lại ở mục 10 của
`model.ipynb`):

```python
FEAT_KEY = ["carbrand", "carmodel", "carorigin", "condition_ad", "gearbox",
            "fuel", "cartype", "carseats", "mfdate", "mileage_km"]
for frame in (tr, te):
    frame["group_key"] = frame[FEAT_KEY].astype(str).agg("|".join, axis=1)
```

**Lưu ý cần ghi vào markdown:** `mileage_km` trong khóa này giờ gồm cả giá trị
đã điền, nên hai xe khác nhau cùng được điền bằng trung vị của một đời xe sẽ
trông như "bản sao". Vì vậy con số 14% ở mục 10 của `model.ipynb` là **giới hạn
trên**. Cách chặt hơn là loại các dòng có `mileage_missing == 1` khỏi phép đếm
bản sao — nếu làm, báo cáo cả hai con số.

### Việc B5 — Chuyển hai thí nghiệm từ mục 7.4 sang

Chuyển **nguyên vẹn** hai thí nghiệm từ `preprocess_data.ipynb`:

1. So sánh 3 phương án gộp nhãn (cũ 50/30, theo cấp 50/30, theo cấp 30/10)
2. Thử thêm vị trí (miền, tỉnh/thành) làm đặc trưng

Sửa duy nhất một điểm: thay vì gọi `group_hierarchical(df, ...)` trên toàn bộ
dữ liệu, dùng `BrandModelGrouper(brand_min, model_min).fit(tr_raw).transform(...)`
để mỗi phương án cũng học ngưỡng từ train. Hàm `cv_mape` giữ nguyên — nó đã fit
encoder trong từng fold.

Viết thêm hàm `old_grouping` dưới dạng một grouper tương đương để so sánh công
bằng (một nhãn `"Dòng khác"` / `"Hãng khác"` chung, ngưỡng 50/30).

Giữ nguyên kết luận cấu trúc của hai thí nghiệm, chỉ cập nhật số.

### Việc B6 — Cell đối chứng: điền sẵn so với điền trong fold

Đây là cell **quan trọng nhất về mặt lập luận** của notebook này. Nó biến hạn chế
còn lại của cấu trúc 3 file thành một thí nghiệm có số liệu.

Vấn đề: `train_data.csv` chứa giá trị đã điền bằng thống kê của **toàn bộ** train.
Khi `model.ipynb` chia train thành 5 fold để tinh chỉnh, phần validation của mỗi
fold đã góp phần tạo ra giá trị điền của chính nó. Mức độ nhỏ vì các thống kê
chỉ dùng đặc trưng, không dùng giá — nhưng cần chứng minh bằng số.

```python
from sklearn.model_selection import StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

CAT = ["carbrand_grp", "carmodel_grp", "carorigin", "condition_ad", "gearbox", "fuel", "cartype"]
NUM = ["age", "mileage_km", "carseats", "km_per_year", "mileage_missing"]
PROBE = dict(n_estimators=150, max_depth=30, max_features=0.33, random_state=RANDOM_STATE, n_jobs=-1)

def encoder():
    return ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT),
                              ("num", "passthrough", NUM)])

def cv_mape_oof(frame_fitted, frame_raw, impute_in_fold):
    """MAPE out-of-fold. impute_in_fold = True thì CarImputer + Grouper fit lại mỗi fold."""
    seg = frame_fitted["segment"].values
    y = frame_fitted["price_log"].values
    p = frame_fitted["price_tr"].values
    oof = np.zeros(len(y))
    for a, b in StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE).split(frame_fitted, seg):
        if impute_in_fold:
            pipe = Pipeline([("impute", CarImputer()), ("group", BrandModelGrouper(30, 10)),
                             ("encode", encoder()), ("model", RandomForestRegressor(**PROBE))])
            pipe.fit(frame_raw.iloc[a], y[a])
            oof[b] = np.exp(pipe.predict(frame_raw.iloc[b]))
        else:
            pipe = Pipeline([("encode", encoder()), ("model", RandomForestRegressor(**PROBE))])
            pipe.fit(frame_fitted.iloc[a], y[a])
            oof[b] = np.exp(pipe.predict(frame_fitted.iloc[b]))
    ape = np.abs(oof - p) / p
    return {"MAPE": ape.mean(),
            **{f"MAPE {s}": ape[seg == s].mean() for s in SEG_LABELS}}
```

Gọi hai lần trên **cùng tập train** và đặt kết quả cạnh nhau. `frame_raw` là
`tr_raw` đã lọc bỏ cùng những dòng đặt cọc như `tr`, để hai phương án chạy trên
đúng cùng số dòng — phải đảm bảo điều này, nếu không so sánh vô nghĩa.

Viết ô markdown kết luận:

- Nếu chênh lệch MAPE nhỏ (dự kiến dưới 0,5 điểm phần trăm), cấu trúc điền sẵn không bóp méo kết luận nào, và ước lượng CV ở `model.ipynb` dùng được.
- Nếu chênh lệch lớn hơn, phải chuyển `CarImputer` và `BrandModelGrouper` vào `Pipeline` trong `model.ipynb`. **Báo cho người dùng** trước khi làm việc này, vì nó thay đổi nhiều ở notebook mô hình.
- Nói rõ ranh giới train/test luôn được giữ nghiêm ngặt trong cả hai phương án; chênh lệch ở đây chỉ liên quan tới ranh giới giữa các fold bên trong train.

### Việc B7 — Xuất file

```python
MODEL_DIR = Path("../model"); MODEL_DIR.mkdir(exist_ok=True)

tr.to_csv("train_data.csv", index=False)
te.to_csv("test_data.csv", index=False)
joblib.dump({"imputer": imputer, "grouper": grouper, "random_state": RANDOM_STATE,
             "seg_bins": SEG_BINS, "seg_labels": SEG_LABELS},
            MODEL_DIR / "data_transformers.joblib", compress=3)

for name, f in [("train_data.csv", tr), ("test_data.csv", te)]:
    back = pd.read_csv(name)
    print(f"{name}: {back.shape}, thiếu = {int(back.isna().sum().sum())}")
    assert len(back) == len(f)
```

**Phải lưu `data_transformers.joblib`.** Hai file CSV chỉ chứa *kết quả* điền,
không chứa *tham số* điền. Nhưng `price_model.py` cần các tham số đó để định giá
một chiếc xe mới. Nếu bỏ qua, sẽ không dựng lại được đặc trưng cho dữ liệu mới,
hoặc buộc phải tính lại thống kê từ `train_data.csv` đã điền — lúc đó trung vị
bị méo vì chính các giá trị điền được tính vào.

Cột phải có trong cả hai file: toàn bộ `FINAL_COLS` của preprocess, cộng thêm
`mileage_missing`, `km_per_year`, `carbrand_grp`, `carmodel_grp`, `age_sq`,
`log_km`, `log_km_per_year`, `segment`, `group_key`.

### Việc B8 — Thêm phần tóm tắt

Bảng cuối notebook: mỗi bước đã làm, học tham số gì từ train, ảnh hưởng mấy
dòng. Đây là phần đưa vào báo cáo để chứng minh thứ tự xử lý đúng.

---

## PHẦN C — `model.ipynb` (chỉ 4 chỗ)

> Giữ nguyên toàn bộ phần còn lại: thuật toán, tham số, thí nghiệm, biểu đồ,
> markdown. Bốn sửa đổi dưới đây đều mang tính kỹ thuật.

### Việc C1 — Đổi phần đọc dữ liệu, bỏ việc chia tập

Trong mục 1, thay cell đọc `clean_data_oto.csv` và cell `train_test_split` bằng:

```python
tr = pd.read_csv("train_data.csv")
te = pd.read_csv("test_data.csv")

tr["carseats"] = tr["carseats"].astype(int)       # CSV đọc lại thành float
te["carseats"] = te["carseats"].astype(int)
```

**Xóa** các dòng sau vì giá trị đã có trong file:

- `df = pd.read_csv("clean_data_oto.csv")` và `df["price_log"] = np.log(df["price_tr"])`
- `df["km_per_year"] = ...`
- `df["age_sq"]`, `df["log_km"]`, `df["log_km_per_year"]`
- `df["segment"] = pd.cut(...)`
- `df["group_key"] = ...` và `FEAT_KEY`
- `idx_tr, idx_te = train_test_split(...)` và `tr, te = df.loc[idx_tr], df.loc[idx_te]`

**Giữ nguyên:** `CAT`, `NUM_TREE`, `NUM_LIN`, `SEG_BINS`, `SEG_LABELS`,
`make_prep`, `prep_tree`, `prep_lin`, `XT_tr`, `XT_te`, `XL_tr`, `XL_te`,
`names_tree`, `y_tr`, `y_te`, `p_tr`, `p_te`, `seg_tr`, `seg_te`.

Lấy `seg_tr`, `seg_te` từ cột `segment` trong file thay vì tính lại.

Nếu một số cell sau còn tham chiếu `df` (ví dụ biểu đồ đường khấu hao ở mục 8.3
dùng `df` để vẽ điểm xám), thay bằng `pd.concat([tr, te])` và ghi chú trong
markdown rằng điểm tham chiếu lấy từ toàn bộ dữ liệu, chỉ để minh họa.

### Việc C2 — Chuyển biểu đồ chia train/test sang `process_data.ipynb`

Xóa cell vẽ `m01_chia_train_test` ở mục 1 (đã chuyển sang việc B1). Sửa ô
markdown mục 1 để trỏ sang `process_data.ipynb` cho phần chia tập.

### Việc C3 — Sửa `metadata.json` ở mục 11

Thay các bảng tra xây từ `df` bằng tham số lấy từ transformer đã fit trên train:

```python
bundle = joblib.load(MODEL_DIR / "data_transformers.joblib")
imputer, grouper = bundle["imputer"], bundle["grouper"]

metadata = {
    # ... giữ nguyên các khóa khác ...
    "mileage_median_by_year": {int(k): float(v) for k, v in imputer.km_by_year_.items()},
    "mileage_median_all": float(imputer.km_global_),
    "keep_brand": sorted(grouper.keep_brand_),
    "keep_model": sorted(grouper.keep_model_),
    "brand_min": grouper.brand_min,
    "model_min": grouper.model_min,
    "luxury_brands": sorted(grouper._luxury()),
}
```

**Xóa** các khóa `brand_group` và `model_group` (bảng mapping cứng xây từ `df`).

Sửa `price_model.py`: dựng `carbrand_grp` / `carmodel_grp` từ `keep_brand`,
`keep_model` và `luxury_brands` theo đúng logic `BrandModelGrouper.transform`,
thay vì tra bảng mapping. Cách này xử lý được cả nhãn chưa từng thấy.

Giữ nguyên bài kiểm tra ở cuối mục 11 (nạp lại model, dự đoán phải trùng khớp
với notebook, `rtol=1e-9`). Nó **phải vẫn pass**.

### Việc C4 — Thêm ghi chú về OOB của bản tự cài đặt

Thêm vào ô markdown mục 5.3 hai câu:

- OOB của bản tự cài đặt được tính sau khi bộ one-hot và `Binner` đã fit trên toàn bộ train, nên các mẫu out-of-bag vẫn ảnh hưởng tới ngưỡng bin và danh sách nhãn.
- Đây không phải leakage từ biến mục tiêu, nhưng OOB không hoàn toàn độc lập. Dùng nó để **so sánh các cấu hình với nhau**, không coi là ước lượng tổng quát hóa.

Không đổi code, không chuyển sang CV — bản tự viết chạy chậm nên OOB là lựa chọn
hợp lý.

---

## PHẦN D — Biểu đồ và bảng cho slide báo cáo

Mục tiêu: sau khi chạy xong, có sẵn một thư mục hình và bảng để chèn thẳng vào
slide, không phải chụp lại màn hình notebook.

### Việc D0 — Lưu kết quả HIỆN TẠI trước khi sửa bất cứ gì

**Làm việc này đầu tiên, trước cả việc 0.** Cần số liệu của phiên bản cũ để vẽ
biểu đồ so sánh trước / sau.

Đọc output đã lưu trong `model.ipynb` hiện tại (các bảng ở mục 7 và 12), ghi ra:

```
tables/results_before.csv
```

với các cột: `model`, `MAPE`, `MedAPE`, `MAE`, `RMSE`, `R2_log`, `pct_10`,
`pct_20`, và MAPE từng phân khúc. Ba dòng: Ridge, RF thư viện, RF tự cài đặt.
Nếu notebook không còn output, chạy lại phiên bản hiện tại **một lần** rồi lưu,
trước khi bắt đầu sửa.

Ghi kèm một file `tables/config_before.txt` nêu: số dòng train/test, tham số tốt
nhất, và việc lọc giá đặt cọc được áp dụng trên toàn bộ dữ liệu.

### Việc D1 — Thiết lập style cho hình dùng trong slide

Thêm vào đầu mỗi notebook một khối cấu hình riêng cho hình slide. Hình trong
notebook giữ nguyên như hiện tại; hình cho slide lưu thêm một bản ở thư mục khác
với chữ to hơn.

```python
from pathlib import Path
import matplotlib.pyplot as plt

SLIDE_DIR = Path("figures/slides"); SLIDE_DIR.mkdir(parents=True, exist_ok=True)

SLIDE_RC = {                       # chữ to, đọc được khi chiếu
    "figure.figsize": (10, 5.6),   # tỉ lệ 16:9 cho vùng nội dung slide
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "font.size": 13,
    "axes.titlesize": 15,
    "axes.labelsize": 13,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
}

def save_slide(fig, name):
    """Lưu bản dùng cho slide: PNG để chèn, PDF để in nét."""
    fig.savefig(SLIDE_DIR / f"{name}.png", dpi=200, bbox_inches="tight", facecolor="white")
    fig.savefig(SLIDE_DIR / f"{name}.pdf", bbox_inches="tight", facecolor="white")
```

Dùng `with plt.rc_context(SLIDE_RC):` quanh phần vẽ, để không ảnh hưởng các hình
khác trong notebook.

Yêu cầu bắt buộc với mọi hình trong `figures/slides/`:

- **Không hình nào có chữ nhỏ hơn 12pt.** Nhãn trục, số trên cột, chú giải đều phải đọc được khi chiếu.
- **Tối đa 2 panel mỗi hình.** Các hình hiện tại có 3 panel (ví dụ `p03`, `m13` với 3 subplot) phải tách thành nhiều hình riêng hoặc giảm còn 2 panel cho bản slide.
- **Tiêu đề nằm trong hình**, dạng một câu kết luận chứ không phải tên biến. Ví dụ dùng "Random Forest định giá sát hơn Ridge ở mọi phân khúc" thay cho "MAPE theo phân khúc". Nếu bạn muốn đặt tiêu đề trên slide thì vẫn giữ tiêu đề trong hình, người dùng tự xóa sau.
- **Số theo định dạng Việt Nam**: dấu phẩy thập phân, dấu chấm hàng nghìn. Hàm `vn()` đã có trong `model.ipynb`, dùng lại.
- **Kiểm tra dấu tiếng Việt.** Font mặc định DejaVu Sans hiển thị được dấu. Sau khi lưu, mở một file PNG kiểm tra; nếu thấy ô vuông thay cho chữ có dấu thì đổi `plt.rcParams["font.family"]` sang font khác có hỗ trợ và ghi lại trong báo cáo.

### Việc D2 — Dùng lại các hình đã có, lưu thêm bản slide

Những hình này đã có và đủ tốt. Chỉ cần bọc trong `rc_context(SLIDE_RC)` và gọi
thêm `save_slide(...)`. **Không đổi nội dung.**

| Hình | Notebook | Dùng cho slide |
|---|---|---|
| `p01_pheu_lam_sach` | preprocess | Làm sạch dữ liệu: còn lại bao nhiêu tin |
| `p02_thieu_va_cach_xu_ly` | preprocess | Giá trị thiếu và cách xử lý từng cột |
| `p03_gia_va_log_gia` | preprocess | Vì sao dùng log giá |
| `p04_phan_khuc_gia` | preprocess | Mất cân bằng theo phân khúc giá |
| `m01_chia_train_test` | process (sau việc B1) | Chia phân tầng train/test |
| cây minh họa độ sâu 3 | model mục 4.3 | Random Forest hoạt động thế nào |
| `m05_rf_so_cay` | model | Vì sao nhiều cây tốt hơn một cây |
| `m06_so_sanh_tong` | model | Kết quả tổng: MAPE và tỉ lệ định giá sát |
| `m07_mape_phan_khuc` | model | Sai số theo phân khúc giá |
| `m08_du_doan_vs_thuc_te` | model | Dự đoán so với giá thật |
| `m10_khoang_tin_cay` | model | Chênh lệch giữa các mô hình có ý nghĩa không |
| `m12_do_quan_trong` | model | Đặc trưng nào quyết định giá |
| `m13_duong_khau_hao` | model | Mô hình học được gì về khấu hao (giảm còn 2 mẫu xe) |
| `m14_log_va_mat_can_bang` | model | Thí nghiệm log giá và cân bằng |
| `m16_ma_hoa` | model | Chọn cách mã hóa bằng số liệu |
| `m18_cay_vs_rung` | model | Một cây so với cả rừng |

Cây minh họa ở mục 4.3 của `model.ipynb` hiện có `figsize=(16, 6.5)` — tỉ lệ này
quá rộng cho slide 16:9. Với bản slide, giảm còn độ sâu 2 (hoặc giữ độ sâu 3
nhưng bỏ hàng lá cuối) và dùng `figsize=(11, 5.5)`.

### Việc D3 — Hình mới cần vẽ

#### D3.1 — EDA (5 hình, từ việc A7)

Năm hình EDA ở việc A7 đều cần bản slide. Mỗi hình một thông điệp, một panel.
Đặt tên `s01_eda_gia_theo_tuoi`, `s02_eda_gia_theo_hang`, `s03_eda_gia_theo_km`,
`s04_eda_tuong_quan`, `s05_eda_gia_theo_kieu_dang`.

Với hình giá theo tuổi và giá theo km, dùng `alpha=0.25`, `s=8`, trục y thang log,
và vẽ thêm **đường trung vị theo nhóm** (ví dụ trung vị giá theo từng tuổi) bằng
màu `ORANGE` lw=2.5 để mắt thấy được xu hướng giữa đám điểm.

#### D3.2 — Sơ đồ quy trình xử lý dữ liệu

Hình quan trọng nhất của bài báo cáo lần này, vì nó là nội dung chính của việc
sửa code. Nội dung cần thể hiện:

```
raw_data_oto.csv
      ↓   làm sạch bằng quy tắc cứng, xử lý từng dòng
preprocess_data.csv          (còn giá trị thiếu)
      ↓   CHIA TRAIN / TEST  ← vạch phân cách, đánh dấu rõ
   train          test
      ↓             ↓
  fit tham số → transform     (điền thiếu, gộp nhãn, lọc nhãn sai)
      ↓             ↓
train_data.csv  test_data.csv
      ↓             ↓
   huấn luyện    đánh giá một lần
```

Điểm phải nhấn: **vạch chia train/test**, và mũi tên chỉ rõ tham số đi **một
chiều** từ train sang test, không có mũi tên ngược.

Khuyến nghị: vẽ sơ đồ này **trực tiếp trong công cụ làm slide** bằng khối hình
và mũi tên, sẽ gọn và dễ sửa hơn matplotlib. Nếu vẽ bằng matplotlib thì dùng
`ax.add_patch(FancyBboxPatch(...))` cho các khối và `ax.annotate` với
`arrowprops` cho mũi tên, tắt trục bằng `ax.axis("off")`, lưu tên
`s06_so_do_quy_trinh`.

Trong cả hai trường hợp, xuất kèm một file `tables/so_do_quy_trinh.txt` chứa
phiên bản text ở trên, để người dùng dựng lại được sơ đồ.

#### D3.3 — So sánh trước / sau khi sửa quy trình

Hai panel cạnh nhau, dùng `tables/results_before.csv` và kết quả mới:

- **Panel trái:** MAPE tổng của Ridge và Random Forest, mỗi mô hình hai cột (trước / sau). Màu nhạt cho "trước", màu đậm cho "sau".
- **Panel phải:** MAPE theo 5 phân khúc của riêng Random Forest, hai cột mỗi phân khúc.

Tiêu đề phải nói rõ bản chất, ví dụ: "Sau khi sửa quy trình, sai số báo cáo tăng
vì tập test khó hơn, không vì mô hình kém đi". Lưu tên `s07_truoc_sau`.

Thêm chú thích trong hình (dùng `ax.text` cỡ 11pt) nêu hai nguyên nhân: tập test
giữ lại các tin giá trả trước, và thống kê tiền xử lý chỉ học từ train.

#### D3.4 — Minh họa vấn đề giá trả trước / đặt cọc

Đây là phát hiện thú vị nhất của project, nên có một slide riêng. Scatter giá
theo tuổi xe, tô đỏ các tin bị quy tắc ở việc B3 đánh dấu, phần còn lại màu xám
nhạt. Thấy ngay một dải điểm đỏ nằm ở vùng xe đời mới nhưng giá rất thấp.

Kèm bảng 5 ví dụ cụ thể (hãng, dòng xe, năm, giá rao, trung vị nhóm) xuất ra
`tables/vi_du_gia_dat_coc.csv`. Lưu hình tên `s08_gia_dat_coc`.

#### D3.5 — Bảng kết quả chính dưới dạng hình

Một số công cụ slide khó định dạng bảng cho đẹp. Xuất thêm bảng kết quả cuối
dạng hình, dùng `ax.table` hoặc vẽ thủ công bằng `ax.text`:

- Dòng: Baseline, Ridge, RF thư viện, RF tự cài đặt
- Cột: MAPE, MedAPE, R² (log), ±20%, thời gian huấn luyện
- Tô đậm dòng Random Forest thư viện

Lưu tên `s09_bang_ket_qua`. **Vẫn xuất bản CSV** ở việc D4 để người dùng chọn
dùng bảng gốc nếu muốn.

### Việc D4 — Xuất bảng ra CSV và Markdown

Tạo thư mục `tables/`. Mỗi bảng xuất **hai** bản: `.csv` để mở bằng Excel, và
một file `tables/bang_bao_cao.md` gộp tất cả dưới dạng bảng Markdown để dán
thẳng vào slide hoặc Word.

| File | Nội dung | Nguồn |
|---|---|---|
| `tu_dien_du_lieu.csv` | 12 thuộc tính: tên cột, ý nghĩa, kiểu, cách người bán nhập | preprocess mục 0 |
| `thong_ke_lam_sach.csv` | từng bước loại dòng, số dòng loại, số còn lại | preprocess `FUNNEL` |
| `gia_tri_thieu.csv` | mỗi cột: số thiếu, %, cách xử lý, nơi xử lý | preprocess mục 4 + 6 |
| `thong_ke_mo_ta.csv` | describe() của các biến số và phân phối các biến phân loại | preprocess mục 9 |
| `phan_khuc_gia.csv` | 5 phân khúc: số mẫu, %, tỉ lệ so với phân khúc lớn nhất | preprocess mục 8 |
| `chia_train_test.csv` | số tin và tỉ lệ từng phân khúc ở train và test | process việc B1 |
| `thong_ke_xu_ly.csv` | số dòng được điền mỗi cấp, số nhóm nhãn, số dòng bị lọc | process việc B2 + B3 |
| `doi_chung_cv.csv` | kết quả cell đối chứng ở việc B6 | process việc B6 |
| `so_sanh_gop_nhan.csv` | 3 phương án gộp nhãn × 2 mô hình | process việc B5 |
| `so_sanh_ma_hoa.csv` | one-hot vs mã số thứ tự | model mục 3 |
| `tham_so_tot_nhat.csv` | tham số tốt nhất của RF và Ridge, điểm CV | model mục 4.2, 5.3, 6 |
| `ket_qua_test.csv` | bảng metric chính của 4 mô hình | model mục 7 |
| `ket_qua_phan_khuc.csv` | MAPE từng phân khúc × từng mô hình | model mục 7 |
| `khoang_tin_cay.csv` | bootstrap: khoảng tin cậy và hiệu ghép cặp | model mục 7.3 |
| `do_quan_trong.csv` | impurity và permutation importance cạnh nhau | model mục 8 |
| `xe_doan_sai_nhat.csv` | 10 xe sai nhiều nhất, kèm nhận xét nguyên nhân | model mục 7.2 |
| `thi_nghiem_can_bang.csv` | log giá và 3 kỹ thuật cân bằng | model mục 9 |
| `tin_dang_lai.csv` | MAPE theo nhóm có / không có bản sao, và CV chia theo nhóm | model mục 10 |
| `results_before.csv` | kết quả phiên bản cũ | việc D0 |
| `so_sanh_truoc_sau.csv` | trước / sau, kèm cột chênh lệch | tổng hợp |

Viết một hàm dùng chung:

```python
TABLE_DIR = Path("tables"); TABLE_DIR.mkdir(exist_ok=True)

def save_table(df, name, title, note=""):
    """Lưu CSV và nối vào tables/bang_bao_cao.md."""
    df.to_csv(TABLE_DIR / f"{name}.csv", encoding="utf-8-sig")
    with open(TABLE_DIR / "bang_bao_cao.md", "a", encoding="utf-8") as f:
        f.write(f"\n\n## {title}\n\n{df.to_markdown()}\n")
        if note:
            f.write(f"\n*{note}*\n")
```

Dùng `encoding="utf-8-sig"` để Excel mở không lỗi chữ có dấu. Xóa
`bang_bao_cao.md` ở đầu mỗi lần chạy để không bị nối trùng.

### Việc D5 — File số liệu chốt

Nhiều slide cần một vài con số lẻ (slide mở đầu, slide kết luận). Xuất
`tables/so_lieu_chot.json` để không phải tra lại trong notebook:

```python
so_lieu = {
    "so_tin_tho": len(raw),
    "so_tin_sach": len(clean),
    "ti_le_giu": len(clean) / len(raw),
    "ngay_crawl": "25/10/2026",
    "so_dac_trung": len(CAT) + len(NUM_TREE),
    "so_hang": ..., "so_dong_xe": ...,
    "train": len(tr), "test": len(te),
    "mape_rf": ..., "mape_ridge": ..., "mape_baseline": ...,
    "pct_20_rf": ..., "r2_log_rf": ...,
    "mape_rf_truoc_khi_sua": 0.155,
    "dac_trung_quan_trong_nhat": "Tuổi xe",
}
```

### Việc D6 — Thứ tự slide đề xuất

Viết ra `tables/dan_y_slide.md`, mỗi dòng gồm: số slide, tiêu đề, hình hoặc bảng
dùng, và một câu thông điệp chính. Đề xuất:

| # | Slide | Hình / bảng |
|---|---|---|
| 1 | Bài toán và mục tiêu | `so_lieu_chot.json` |
| 2 | Nguồn dữ liệu và cách thu thập | `tu_dien_du_lieu.csv` |
| 3 | Làm sạch dữ liệu | `p01_pheu_lam_sach` |
| 4 | Giá trị thiếu và cách xử lý | `p02_thieu_va_cach_xu_ly` |
| 5 | Vấn đề giá trả trước / đặt cọc | `s08_gia_dat_coc` |
| 6 | EDA: giá theo tuổi xe | `s01_eda_gia_theo_tuoi` |
| 7 | EDA: giá theo hãng | `s02_eda_gia_theo_hang` |
| 8 | EDA: tương quan giữa các biến | `s04_eda_tuong_quan` |
| 9 | Vì sao dùng log giá | `p03_gia_va_log_gia` |
| 10 | Mất cân bằng theo phân khúc | `p04_phan_khuc_gia` |
| 11 | **Quy trình xử lý và chia tập** | `s06_so_do_quy_trinh` |
| 12 | Chia phân tầng train/test | `m01_chia_train_test` |
| 13 | Gộp nhãn hiếm: chọn bằng số liệu | `so_sanh_gop_nhan.csv` |
| 14 | Chọn cách mã hóa | `m16_ma_hoa` |
| 15 | Random Forest hoạt động thế nào | cây minh họa |
| 16 | Một cây so với cả rừng | `m18_cay_vs_rung`, `m05_rf_so_cay` |
| 17 | Kết quả trên tập test | `s09_bang_ket_qua`, `m06_so_sanh_tong` |
| 18 | Sai số theo phân khúc giá | `m07_mape_phan_khuc` |
| 19 | Dự đoán so với giá thật | `m08_du_doan_vs_thuc_te` |
| 20 | Chênh lệch có ý nghĩa thống kê không | `m10_khoang_tin_cay` |
| 21 | Đặc trưng nào quyết định giá | `m12_do_quan_trong` |
| 22 | Mô hình học được gì về khấu hao | `m13_duong_khau_hao` |
| 23 | Trước / sau khi sửa quy trình | `s07_truoc_sau` |
| 24 | Hạn chế và hướng phát triển | `tin_dang_lai.csv` |

Slide 11 và 23 là hai slide thể hiện phần việc lần này, nên để nguyên, đừng gộp.

---

## 7. Tùy chọn, làm sau cùng nếu còn thời gian

Chỉ làm khi mọi việc ở phần A, B, C đã xong và notebook chạy sạch.

**Learning curve** — thêm vào mục 7 của `model.ipynb`:
`sklearn.model_selection.learning_curve` cho Random Forest với tham số tốt nhất,
5-fold CV trên train, trục x là số mẫu train. Vẽ hai đường train / validation,
kèm nhận xét chẩn đoán bias–variance và việc thêm dữ liệu có khả năng giúp gì.

---

## 8. Cập nhật phần văn bản

Sau khi sửa code và chạy lại, **mọi con số trong các ô markdown đều phải cập
nhật**. Những chỗ cần soát:

| Vị trí | Nội dung |
|---|---|
| `preprocess_data.ipynb` bảng tóm tắt cuối | các bước và kết quả, bỏ bước đặt cọc |
| `preprocess_data.ipynb` biểu đồ phễu | số dòng còn lại từng bước |
| `process_data.ipynb` | toàn bộ, vì là notebook mới |
| `model.ipynb` mục 3 | kết luận one-hot vs mã số thứ tự |
| `model.ipynb` mục 4.2, 5.3 | tham số tốt nhất tìm được |
| `model.ipynb` mục 7.x | bảng kết quả test, MAPE theo phân khúc |
| `model.ipynb` mục 7.2 | danh sách 10 xe đoán sai nhất và nhận xét về nguyên nhân |
| `model.ipynb` mục 7.3 | khoảng tin cậy bootstrap, kết luận ý nghĩa thống kê |
| `model.ipynb` mục 8.1, 8.2 | độ quan trọng đặc trưng và thứ hạng permutation |
| `model.ipynb` mục 9.1 | kết luận log giá và các kỹ thuật cân bằng |
| `model.ipynb` mục 10 | tỉ lệ tin có bản sao, chênh lệch hai cách chia fold |
| `model.ipynb` mục 12 | bảng kết quả tổng và kết luận |

Riêng mục 7.2 của `model.ipynb` cần xem lại nội dung, không chỉ số: nhận xét
hiện tại nói rằng sai số lớn nhất đến từ giá trả trước lọt lưới. Sau khi sửa
việc B3, số tin như vậy trong test sẽ **nhiều hơn**, nên nhận xét vẫn đúng và
càng rõ. Cập nhật ví dụ cụ thể theo output mới.

---

## 9. Kỳ vọng về số liệu sau khi sửa

**Quan trọng — đọc trước khi báo cáo kết quả.**

Sau khi sửa, MAPE trên test **sẽ tăng lên**, và đó là **bình thường**, không phải
dấu hiệu code sai. Hai lý do:

1. **Chính:** quy tắc lọc giá đặt cọc giờ chỉ học từ train, nên nhiều tin rao **giá trả trước** trước đây bị xóa khỏi test giờ được giữ lại. Mục 7.2 của notebook đã chứng minh những tin này chiếm phần lớn trong 10 xe bị đoán sai nặng nhất. Test khó hơn, nên MAPE tăng.
2. **Phụ:** điền thiếu và gộp nhãn giờ chỉ dùng thống kê của train, bớt phần lạc quan.

Mức thay đổi dự kiến: Random Forest từ 15,5% lên khoảng **16–19%**, tăng mạnh
nhất ở phân khúc `< 200 triệu`. Những điều **không nên đổi**:

- Thứ hạng: Random Forest tốt hơn Ridge, cả hai tốt hơn baseline rất nhiều.
- Random Forest tự cài đặt vẫn xấp xỉ bản thư viện (chênh lệch MAPE dưới 1 điểm %).
- Kết luận log giá tốt hơn giá gốc theo MAPE.
- Tuổi xe vẫn là đặc trưng quan trọng nhất.

Nếu thứ hạng đổi, hoặc MAPE vượt 25%, hoặc bài kiểm tra nạp lại model ở mục 11
fail — **dừng lại và kiểm tra code**, đừng điều chỉnh tham số để con số đẹp
trở lại. Tinh chỉnh tham số dựa trên kết quả test chính là lỗi mà toàn bộ việc
sửa này nhằm loại bỏ.

Khi báo cáo cho người dùng, nói rõ:

- Con số cũ và con số mới, đặt cạnh nhau.
- Con số mới cao hơn vì **tập test khó hơn và quy trình chặt hơn**, không vì mô hình kém đi.
- Kết quả của cell đối chứng ở việc B6.

---

## 10. Tiêu chí hoàn thành

Chỉ báo cáo xong khi tất cả các điểm sau đều đạt:

- [ ] Bốn notebook chạy lại từ đầu đến cuối không lỗi, theo thứ tự `crawl` (bỏ qua) → `preprocess_data` → `process_data` → `model`.
- [ ] `preprocess_data.ipynb` xuất `preprocess_data.csv`, file này **còn `NaN`** ở đúng ba cột `mileage_km`, `cartype`, `carseats`.
- [ ] Không còn chỗ nào trong `preprocess_data.ipynb` tính `median`, `mode`, hoặc ngưỡng `value_counts()` mà kết quả đi vào file xuất.
- [ ] `process_data.ipynb` xuất `train_data.csv`, `test_data.csv`, `model/data_transformers.joblib`.
- [ ] Hai file train/test không còn `NaN` ở các cột đặc trưng.
- [ ] Mọi `fit` trong `process_data.ipynb` chỉ nhận dữ liệu train. Kiểm tra bằng cách `grep` các lời gọi `.fit(` và xác nhận đối số không phải `te`, `te_raw` hay `df`.
- [ ] Trong `model.ipynb`, `grep` toàn bộ `fit_transform` và xác nhận **không có** lời gọi nào nhận `te` (phải là `prep.fit_transform(tr)` rồi `prep.transform(te)`). Không tập nào được chuẩn hóa hay mã hóa riêng.
- [ ] Trong `model.ipynb`, mọi lời gọi `.fit(` cho scaler và encoder đều nhận dữ liệu train hoặc phần train của một fold, không nhận `te` và không nhận toàn bộ dữ liệu.
- [ ] Assert nhãn nhóm của test là tập con của train — pass.
- [ ] Cell đối chứng ở việc B6 chạy được và có kết luận bằng số.
- [ ] `model.ipynb` chỉ thay đổi ở 4 chỗ của phần C. Không thêm thuật toán, không đổi tham số tìm kiếm, không đổi `random_state`.
- [ ] Bài kiểm tra nạp lại model ở cuối mục 11 pass với `rtol=1e-9`.
- [ ] Mục EDA mới có ít nhất 5 biểu đồ, mỗi biểu đồ có nhận xét.
- [ ] Mọi con số trong markdown khớp với output thực tế của lần chạy cuối.
- [ ] `tables/results_before.csv` được lưu **trước** khi sửa code (việc D0).
- [ ] Thư mục `figures/slides/` có đủ các hình ở việc D2 và D3, mỗi hình hai bản PNG và PDF.
- [ ] Mở ngẫu nhiên 3 file PNG trong `figures/slides/` kiểm tra: chữ tiếng Việt hiện đúng dấu, không có chữ nhỏ hơn 12pt, không bị cắt mất nhãn.
- [ ] Thư mục `tables/` có đủ các file ở việc D4, cộng `so_lieu_chot.json` và `dan_y_slide.md`.
- [ ] `tables/bang_bao_cao.md` mở được, các bảng không bị trùng lặp do nối nhiều lần.

Cuối cùng, viết một bảng so sánh **trước / sau** cho Ridge và Random Forest
(MAPE tổng, MAPE từng phân khúc, R² log, ±20%), kèm một đoạn giải thích chênh
lệch đến từ đâu, tách riêng phần do tập test thay đổi và phần do thống kê chỉ
học từ train.

---

## 11. Thứ tự ưu tiên nếu không làm hết

Mỗi mức để lại project ở trạng thái chạy được.

0. **Việc D0** — lưu kết quả hiện tại. Làm trước tiên, không bỏ qua: sau khi đã sửa code thì không lấy lại được số liệu cũ.
1. **Việc 0, A1, A4, A5, B1, B2, B7, C1** — chuyển điền thiếu và gộp nhãn sang sau khi chia. Đây là phần cốt lõi, và sau mức này project đã chạy được end-to-end.
2. **Việc B3 lỗi a** — sửa bug `"Dòng khác"` trong quy tắc lọc giá đặt cọc. Rẻ, và sửa một lỗi logic thật.
3. **Việc A7** — thêm mục EDA. Bước thiếu hẳn so với quy trình chuẩn.
4. **Việc B3 lỗi b, A2, A6** — chuyển quy tắc lọc đặt cọc sang sau khi chia.
5. **Việc D1, D2, D4** — style slide, lưu lại các hình đã có, xuất bảng. Rẻ và dùng được ngay cho báo cáo.
6. **Việc B6** — cell đối chứng. Đây là phần làm cho cấu trúc bảo vệ được trong báo cáo.
7. **Việc D3.2, D3.3** — sơ đồ quy trình và hình trước / sau. Hai hình thể hiện trực tiếp phần việc lần này.
8. **Việc A3, B4, B5, B8, C2, C3, C4** — phần còn lại của code.
9. **Việc D3.1, D3.4, D3.5, D5, D6** — các hình và file phụ trợ còn lại cho slide.
10. **Mục 7** — learning curve.
