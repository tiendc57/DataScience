# Đánh giá code: Dự đoán giá ô tô cũ (Chợ Tốt)

Người đánh giá: Hùng (review cùng Claude) · Ngày: 27/10/2026
Phạm vi: toàn bộ thư mục `DataScience/` (4 notebook, 2 file CSV, `model/`, `figures/`)

**Cách kiểm tra:** đọc toàn bộ code và output trong notebook. Chạy lại Random Forest trên `clean_data_oto.csv` với đúng tham số tốt nhất trong `model.ipynb` → MAPE test = **0,198**, khớp con số 0,199 trong notebook. Các số liệu trong mục 3 được đo trên chính dữ liệu và cách chia train/test này. Riêng `price_model.py` chưa chạy, vì nạp file `.joblib`/`.pkl` tải từ ngoài về là chạy code lạ. Phần kiểm tra nạp lại mô hình dựa vào `assert` có sẵn trong notebook.

---

## 1. Tóm tắt

Bài làm **tốt, bám sát đề**, quy trình đầy đủ từ đầu đến cuối và lý do cho từng bước được viết rõ ràng. Cần sửa **3 điểm** trước khi viết báo cáo và làm slide. Lý do: hai điểm làm thay đổi con số và cách giải thích kết quả, điểm còn lại làm bài khớp đề hơn.

| # | Vấn đề | Mức độ | Ảnh hưởng |
|---|---|---|---|
| 1 | Giá trả trước / đặt cọc lẫn trong dữ liệu (nhãn sai) | **Cao** | MAPE 0,198 → 0,175 khi bỏ 22 dòng test (0,8%); phân khúc < 200 triệu: 0,566 → 0,421 |
| 2 | Tập test được dùng để chọn log giá và chọn kỹ thuật cân bằng | **Cao** | Kết luận "test không dùng để chọn mô hình" là sai |
| 3 | Thiếu Decision Tree trong bảng so sánh | Trung bình | Đề bài có nêu tên Decision Tree |
| 4 | Thí nghiệm mất cân bằng dùng mô hình khác với mô hình cuối | Trung bình | Chưa trả lời được "cân bằng có giúp gì cho Random Forest không" |
| 5 | Tin đăng lại: một xe nằm ở cả train và test | Thấp | Kết quả hơi lạc quan, MAPE lệch khoảng 2 điểm % |
| 6 | Lỗi nhỏ: trực quan hóa, đặt tên mục, crawler, kích thước file | Thấp | Thẩm mỹ, khả năng tái lập |

---

## 2. Đối chiếu với đề bài (`Assignment.txt`)

| Yêu cầu | Trạng thái | Ghi chú |
|---|---|---|
| Thu thập dữ liệu | ✅ | `crawl_data.ipynb`, 14.835 tin từ xe.chotot.com |
| Mô hình ML từ đầu đến cuối | ✅ | crawl → làm sạch → khám phá dữ liệu → mô hình → xuất mô hình |
| Có metric đánh giá | ✅ | MAE, RMSE, MAPE, MedAPE, R², ±10%/±20%, MAPE theo phân khúc, khoảng tin cậy bootstrap |
| Random Forest | ✅ | Bản sklearn và bản tự cài đặt bằng NumPy |
| Decision Tree | ⚠️ | Chỉ dùng để kiểm tra cây tự viết, chưa có trong bảng kết quả (xem mục 3.3) |
| Kỹ thuật xử lý dữ liệu mất cân bằng | ⚠️ | Có (trọng số mẫu, oversampling, undersampling) nhưng đánh giá trên test, bằng mô hình khác (xem 3.2, 3.4) |
| Slide + báo cáo + code demo | ❌ / ✅ | Chưa có slide và báo cáo. Code demo đã có (`model/price_model.py`) |

---

## 3. Vấn đề cần sửa

### 3.1 Giá trả trước / đặt cọc lẫn trong dữ liệu — mức CAO

**Hiện tượng.** `preprocess_data.ipynb` (mục 4) chỉ loại xe giá dưới 20 triệu. Vẫn còn nhiều tin mà "giá" thực ra là số tiền trả trước hoặc đặt cọc, ví dụ:

| Xe | Năm | Tình trạng | Giá trong dữ liệu |
|---|---|---|---|
| VinFast VF6 | 2026 | Mới | 50 triệu |
| VinFast VF3 | 2026 | Mới | 28 triệu |
| Mitsubishi Xpander | 2023 | Đã sử dụng | 70–89 triệu |
| Hyundai Stargazer | 2025 | Mới | 99 triệu |

Có 148 xe tuổi ≤ 5 năm mà giá dưới 150 triệu. Dùng quy tắc "giá thấp hơn 30% giá trung vị của các xe cùng hãng, dòng và năm (nhóm có ít nhất 3 xe)" thì đánh dấu được **134 dòng**, gần như toàn bộ thuộc phân khúc < 200 triệu.

**Ảnh hưởng (Random Forest, đúng cấu hình và cách chia train/test của notebook):**

| Tập đánh giá | n | MAPE | MAPE < 200 triệu |
|---|---|---|---|
| Toàn bộ test (như notebook) | 2.816 | 0,198 | 0,566 |
| Bỏ dòng nghi giá cọc | 2.794 | **0,175** | **0,421** |
| Chỉ dòng nghi giá cọc | 22 | 3,225 | 3,323 |

Chỉ 22 dòng sai nhãn mà kéo MAPE tổng tăng 2,3 điểm %. Phần kết luận của `model.ipynb` giải thích sai số lớn ở xe rẻ là do "xe đời cũ khác nhau về tình trạng". Thực tế phần lớn sai số này đến từ **nhãn sai**.

**Cách sửa.** Thêm vào cuối mục 4 của `preprocess_data.ipynb`, sau khi loại `bad_price`:

```python
# Giá rao quá thấp so với xe cùng hãng-dòng-năm: thường là tiền trả trước / đặt cọc, không phải giá xe
grp = df.groupby(["carbrand", "carmodel", "mfdate"])["price_tr"]
ref, n_grp = grp.transform("median"), grp.transform("size")
deposit = (n_grp >= 3) & (df["price_tr"] < 0.3 * ref)
print(f"Loại {deposit.sum()} tin nghi giá trả trước/đặt cọc")
df = df[~deposit].reset_index(drop=True)
```

Sau đó chạy lại `preprocess_data.ipynb` rồi `model.ipynb`, và **cập nhật mọi con số** trong phần kết luận và trong `CLAUDE.md`. Trong báo cáo nên có một đoạn ngắn về phát hiện này. Đây là một điểm cộng về hiểu dữ liệu.

> Ghi chú: quy tắc này dùng giá (biến mục tiêu) trên toàn bộ dữ liệu. Việc đó chấp nhận được vì đây là bước **sửa lỗi nhãn**, không phải tạo đặc trưng. Nên ghi rõ điều này trong báo cáo. Cách chặt chẽ hơn là crawl thêm mô tả tin đăng và lọc theo từ khóa "trả trước", "góp", "cọc".

### 3.2 Tập test đã dùng để ra quyết định — mức CAO

**Hiện tượng.** Ở mục 7.4 của `preprocess_data.ipynb`, hai lựa chọn được quyết định bằng **sai số trên tập test**:

- huấn luyện trên log giá hay giá gốc;
- dùng kỹ thuật cân bằng nào.

`model.ipynb` chia train/test giống hệt (cùng dữ liệu, cùng `stratify`, cùng `random_state=42`), nên đó chính là tập test cuối cùng. Vì vậy câu ở cuối `model.ipynb`, *"Tập test không dùng để chọn mô hình hay tham số (chỉ dùng CV/OOB trên train)"*, là **không đúng**.

**Cách sửa** (chọn một trong hai):

- **(Nên làm)** Đánh giá thí nghiệm 7.4 bằng cross-validation trên tập train. Việc cân bằng chỉ áp dụng trong phần train của từng fold:

  ```python
  from sklearn.model_selection import StratifiedKFold

  def cv_oof(log_target=True, balance=None):
      oof = np.zeros(len(yraw_tr))
      for tr_i, va_i in StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE).split(Xtr, seg_tr):
          fit_i, w = tr_i, None
          if balance == "weight":
              f = seg_tr.iloc[tr_i].value_counts(normalize=True)
              w = (1 / np.sqrt(seg_tr.iloc[tr_i].map(f).astype(float))).values
          # oversampling / undersampling: tạo fit_i từ tr_i theo cách đang làm
          m = HistGradientBoostingRegressor(max_iter=300, random_state=RANDOM_STATE)
          if log_target:
              m.fit(Xtr[fit_i], ylog_tr.values[fit_i], sample_weight=w)
              oof[va_i] = np.exp(m.predict(Xtr[va_i]))
          else:
              m.fit(Xtr[fit_i], yraw_tr.values[fit_i], sample_weight=w)
              oof[va_i] = np.clip(m.predict(Xtr[va_i]), 1, None)
      return oof   # tính MAPE tổng và theo phân khúc trên (yraw_tr, oof)
  ```

- **(Tối thiểu)** Giữ nguyên code nhưng sửa câu kết luận và ghi trong báo cáo rằng hai lựa chọn này được đưa ra dựa trên tập test.

### 3.3 Thêm Decision Tree vào bảng so sánh — mức TRUNG BÌNH

Đề bài nêu tên "Random Forest, Decision Tree". Hiện `DecisionTreeRegressor` chỉ xuất hiện ở mục 4B để kiểm tra cây tự viết. Nên thêm một mô hình có tinh chỉnh tham số vào mục 4 của `model.ipynb`:

```python
from sklearn.tree import DecisionTreeRegressor

gs_dt = GridSearchCV(DecisionTreeRegressor(random_state=RANDOM_STATE),
                     {"max_depth": [5, 10, 15, 20, 30, None], "min_samples_leaf": [1, 3, 5, 10, 20]},
                     cv=KFold(5, shuffle=True, random_state=RANDOM_STATE),
                     scoring="neg_root_mean_squared_error", n_jobs=-1)
gs_dt.fit(X_tr, y_tr)
t0 = time.time()
dt_lib = DecisionTreeRegressor(**gs_dt.best_params_, random_state=RANDOM_STATE).fit(X_tr, y_tr)
record("Decision Tree - thư viện", dt_lib.predict(X_te), time.time() - t0)
```

Nhớ thêm `"Decision Tree - thư viện"` vào danh sách `show` và `colors` ở mục 5. Trong báo cáo, điều này cho một câu chuyện liền mạch: **1 cây → nhiều cây (Random Forest) giảm phương sai bao nhiêu**. Cây tự viết ở mục 4B cũng có thể đưa vào bảng.

### 3.4 Thí nghiệm mất cân bằng nên làm với mô hình cuối — mức TRUNG BÌNH

Mục 7.4 dùng `HistGradientBoostingRegressor`, trong khi hai mô hình cuối là Ridge và Random Forest. Vì vậy kết luận "các kỹ thuật cân bằng không giúp" chưa chắc đúng với Random Forest. Đề nghị chuyển thí nghiệm này sang `model.ipynb`, chạy với Random Forest (`sample_weight` trong `.fit`, hoặc oversampling) và đánh giá bằng CV như ở mục 3.2. Đây là phần đề bài yêu cầu rõ, nên đáng có một mục riêng trong báo cáo.

### 3.5 Tin đăng lại — mức THẤP

Notebook đã xóa các dòng trùng hoàn toàn. Tuy vậy, cùng một xe đăng lại với mã tin khác (giá chênh nhẹ) vẫn còn:

- **15,8%** dòng test (445 dòng) có một dòng trong train giống hệt mọi đặc trưng, kể cả số km.
- Với các dòng này, nếu chỉ "tra" giá từ train thì 22,5% lệch dưới 1%. Nhiều khả năng đó là cùng một chiếc xe.
- Random Forest trên nhóm có bản sao: MedAPE 0,056. Trên nhóm không có bản sao: MedAPE 0,093, MAPE 0,202 (so với 0,198 trên toàn bộ test).

Ảnh hưởng tổng thể nhỏ. Có thể ghi vào phần **hạn chế**, hoặc chia train/test theo nhóm để mọi bản sao của một xe nằm cùng một phía:

```python
from sklearn.model_selection import StratifiedGroupKFold
FEAT_KEY = ["carbrand", "carmodel", "carorigin", "condition_ad", "gearbox", "fuel",
            "cartype", "carseats", "mfdate", "mileage_km"]
groups = d[FEAT_KEY].astype(str).agg("|".join, axis=1)
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
tr_pos, te_pos = next(sgkf.split(d, d["segment"], groups=groups))   # ~80/20, vẫn phân tầng
idx_tr, idx_te = d.index[tr_pos], d.index[te_pos]
```

### 3.6 Lỗi nhỏ

| File | Vấn đề | Đề xuất |
|---|---|---|
| `visualize_raw_data.ipynb` | `na_values=["N/A", "Đang cập nhật", "Khác"]` áp cho **mọi cột**, nên nhãn "Khác" ở `carmodel` cũng thành thiếu. Không khớp với cách `preprocess_data.ipynb` xử lý. | Chỉ áp "Khác" cho `carseats` |
| `visualize_raw_data.ipynb` | Thống kê trên dữ liệu thô vẫn còn giá 0,36 triệu và 40 tỷ | Ghi rõ "dữ liệu thô", hoặc vẽ thêm vài biểu đồ từ `clean_data_oto.csv` cho báo cáo |
| `visualize_raw_data.ipynb` | Matplotlib báo `vert=` sắp bị bỏ | Đổi sang `orientation="horizontal"` |
| `preprocess_data.ipynb` | Hai mục cùng đánh số "3." | Đánh số lại |
| `crawl_data.ipynb` | Tìm tin bằng class CSS `crd7gu7`, là tên sinh tự động nên dễ hỏng khi web đổi giao diện | Ghi **ngày crawl** vào báo cáo. Nhắc tới việc tuân thủ robots.txt / điều khoản sử dụng và tốc độ crawl (đã có `sleep`) |
| `crawl_data.ipynb` | Cell 0 (thử 5 trang) là bản nháp | Xóa, hoặc ghi chú "thử nghiệm" |
| `model/` | `random_forest_sklearn.pkl` 236 MB trùng chức năng với `.joblib` 57 MB. Cả thư mục khoảng 130 MB khi nén | Nộp một định dạng thôi, hoặc chỉ nộp code + hướng dẫn huấn luyện lại |
| `model.ipynb` | Dùng `exp(dự đoán log)` sẽ ra **trung vị** của giá chứ không phải trung bình (hơi thấp hơn) | Không cần sửa (hợp với MAPE), nhưng nên nêu trong báo cáo |
| `price_model.py` | `CURRENT_YEAR = 2026` cố định; không xử lý `mfdate = "trước năm 1980"` | Ghi chú trong docstring là đủ |

---

## 4. Điểm mạnh (nên giữ và nêu trong báo cáo)

- **Tiền xử lý có lý do rõ ràng:** xe mới thiếu km thì điền 0 (thiếu có cấu trúc); km bất hợp lý thì chuyển thành thiếu rồi mới điền; `cartype`/`carseats` điền theo mode của hãng + dòng xe; `carorigin` thiếu 41% thì gán "Không rõ" thay vì đoán; giữ xe sang thật thay vì cắt ngoại lệ.
- **Có kiểm tra chống rò rỉ dữ liệu:** bộ mã hóa fit chỉ trên train; tinh chỉnh tham số bằng CV/OOB; đã tự ghi chú rủi ro rò rỉ khi điền thiếu trên toàn bộ dữ liệu.
- **Đánh giá kỹ:** nhiều metric, MAPE theo phân khúc, khoảng tin cậy bootstrap, biểu đồ phần dư.
- **Tự cài đặt có kiểm chứng:** Ridge nghiệm đóng trùng sklearn đến cỡ 1e-10; Gradient Descent có Nesterov hội tụ về nghiệm đóng; Random Forest tự viết (chia nút bằng histogram, OOB) cho MAPE 0,206 so với 0,199 của sklearn.
- **Xuất mô hình dùng lại được:** `price_model.py` + `metadata.json`, có `assert` so khớp dự đoán sau khi nạp lại.

---

## 5. Kết quả hiện tại (trước khi sửa, tập test, `random_state=42`)

| Mô hình | MAPE | MedAPE | R² (log) | ±20% |
|---|---|---|---|---|
| Baseline (trung vị) | 0,894 | 0,409 | −0,005 | 25% |
| Ridge (sklearn / tự viết) | 0,269 | 0,127 | 0,791 | 68% |
| Random Forest (sklearn) | **0,199** | **0,088** | **0,856** | **77%** |
| Random Forest (tự viết) | 0,206 | 0,091 | 0,850 | 77% |

Các số này **sẽ thay đổi** sau khi sửa mục 3.1. Dự kiến MAPE của Random Forest còn khoảng 0,17–0,18.

---

## 6. Về việc dùng AI

`prompt.txt` và `CLAUDE.md` cho thấy code được viết với trợ lý AI. Cần:

1. Xem quy định của môn về việc dùng AI và **ghi rõ trong báo cáo** nếu môn yêu cầu.
2. Đảm bảo **cả hai thành viên** tự giải thích được các phần dễ bị hỏi khi bảo vệ: vì sao dùng log giá; công thức gain khi tách nút; cách chia nút bằng histogram; OOB là gì; Nesterov momentum và vì sao bước học là 1/L; vì sao đổi `alpha` theo `n` khi so với sklearn; ý nghĩa MAPE so với R².

---

## 7. Việc cần làm tiếp (theo thứ tự)

- [ ] Thêm bộ lọc giá trả trước / đặt cọc (3.1) → chạy lại `preprocess_data.ipynb`
- [ ] Chuyển thí nghiệm log giá + cân bằng sang CV trên train, dùng Random Forest (3.2, 3.4)
- [ ] Thêm Decision Tree vào bảng so sánh (3.3)
- [ ] Chạy lại `model.ipynb`, cập nhật kết luận và các con số trong `CLAUDE.md`
- [ ] Sửa các lỗi nhỏ (3.6), ghi tin đăng lại vào phần hạn chế (3.5)
- [ ] Viết báo cáo + slide, dùng ảnh trong `figures/` và các bảng kết quả mới
