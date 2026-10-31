# Đánh giá 3 notebook Data Science / Machine Learning

## 1. Phạm vi đánh giá

Đánh giá dựa trên ba notebook người dùng cung cấp:

1.  `crawl_data.ipynb` -- Thu thập dữ liệu ô tô từ Chợ Tốt.
2.  `preprocess_data.ipynb` -- Làm sạch, xử lý dữ liệu, phân tích và
    xuất `clean_data_oto.csv`.
3.  `model.ipynb` -- Chia Train/Test, xây dựng Ridge Regression, Random
    Forest (Scikit-learn và tự cài đặt), tuning và đánh giá.

> **Nhận xét tổng quan:** Project đã có cấu trúc tương đối đầy đủ, từ
> crawl dữ liệu đến xây dựng và đánh giá mô hình. Tuy nhiên, cần xử lý
> một số nguy cơ Data Leakage, đặc biệt ở bước imputation, grouping
> category, lọc giá đặt cọc và preprocessing trước Cross-validation. Các
> vấn đề này có thể khiến kết quả đánh giá lạc quan hơn khả năng tổng
> quát hóa thực tế.

## 2. Đánh giá tổng quan

  -------------------------------------------------------------------------
  Thành phần                Đánh giá                Nhận xét
  ------------------------- ----------------------- -----------------------
  `crawl_data.ipynb`        Tốt                     Có retry, resume, chống
                                                    trùng URL và lưu dữ
                                                    liệu thô.

  `preprocess_data.ipynb`   Cần cải thiện           Có nhiều bước xử lý hợp
                                                    lý, nhưng một số thống
                                                    kê được tính trên toàn
                                                    bộ dataset trước khi
                                                    chia Train/Test.

  `model.ipynb`             Cần cải thiện           Có baseline, CV,
                                                    tuning, Random Forest
                                                    tự cài đặt và nhiều
                                                    phương pháp đánh giá;
                                                    tuy nhiên preprocessing
                                                    trước CV và việc sử
                                                    dụng Test cần được xem
                                                    xét lại.

  Evaluation &              Khá tốt                 Có nhiều metric, so
  Reproducibility                                   sánh mô hình,
                                                    bootstrap, phân tích
                                                    theo phân khúc và kiểm
                                                    tra nạp lại model.
  -------------------------------------------------------------------------

------------------------------------------------------------------------

# 3. Đánh giá `crawl_data.ipynb`

## 3.1. Thiết kế hiện tại

Notebook crawl dữ liệu từ Chợ Tốt theo hai giai đoạn:

-   Duyệt các trang danh sách để lấy URL.
-   Truy cập từng URL để lấy các thuộc tính của xe.

## 3.2. Điểm tốt

  -----------------------------------------------------------------------
  Thành phần                          Đánh giá
  ----------------------------------- -----------------------------------
  Requests + BeautifulSoup            Phù hợp với trang có HTML chứa dữ
                                      liệu cần lấy.

  Session                             Tái sử dụng kết nối.

  Retry                               Có xử lý lỗi 403, 429 và lỗi kết
                                      nối.

  Timeout                             Có giới hạn thời gian chờ.

  Resume                              Có thể tiếp tục crawl khi bị ngắt.

  Dedup URL                           Tránh crawl cùng URL nhiều lần.

  CSV                                 Ghi nối tiếp và flush sau mỗi bản
                                      ghi.

  Delay                               Có nghỉ giữa các request.
  -----------------------------------------------------------------------

## 3.3. Điểm cần cải thiện

### 3.3.1. CSS selector có thể thay đổi

Ví dụ:

``` python
soup.find_all("div", class_="crd7gu7")
```

Class có vẻ được sinh tự động và có thể thay đổi khi website cập nhật
giao diện. Khi đó crawler có thể không lấy được dữ liệu.

Nên bổ sung kiểm tra:

-   Số URL tìm được ở mỗi trang.
-   Số bản ghi thực sự lấy được.
-   Tỷ lệ thuộc tính bị thiếu.
-   Cảnh báo khi số URL bằng 0 liên tiếp.

### 3.3.2. Thiếu kiểm tra dữ liệu sau crawl

Nên kiểm tra:

-   URL có hợp lệ không.
-   Giá có phải số không.
-   Năm sản xuất có nằm trong khoảng hợp lý không.
-   Số km có đúng kiểu số không.
-   Cấu trúc HTML có thay đổi hay không.

### 3.3.3. Nên lưu metadata crawl

Ngoài các thuộc tính xe, nên lưu thêm:

-   `crawl_timestamp`
-   `source_url`
-   `http_status`
-   `crawl_batch_id`

Notebook đã lưu URL, đây là điểm tốt. Thời điểm thu thập từng bản ghi
hữu ích hơn thời điểm ghi file cuối cùng, nhất là khi crawler chạy nhiều
ngày.

------------------------------------------------------------------------

# 4. Đánh giá `preprocess_data.ipynb`

Đây là notebook cần chú ý nhất vì preprocessing ảnh hưởng trực tiếp đến
chất lượng mô hình.

## 4.1. Những bước đang làm tốt

  -----------------------------------------------------------------------
  Công việc                           Nhận xét
  ----------------------------------- -----------------------------------
  N/A → NaN                           Đúng.

  Phân biệt missing có cấu trúc và    Tốt.
  missing thực sự                     

  Giá thiếu → loại bản ghi            Hợp lý với supervised regression.

  Xe mới thiếu km → 0 km              Hợp lý theo nghiệp vụ nếu định
                                      nghĩa xe mới bảo đảm điều đó.

  Xe cũ thiếu km → đánh dấu và điền   Hợp lý.

  Phân biệt lỗi dữ liệu và outlier    Tốt.
  thật                                

  Giữ xe sang là outlier hợp lệ       Đúng về nguyên tắc.

  Log-transform giá                   Có cơ sở.

  Gộp nhãn hãng/dòng xe hiếm          Có lý do và có thí nghiệm.

  Xuất clean CSV                      Đúng hướng.
  -----------------------------------------------------------------------

Đặc biệt, cách xử lý `mileage_missing` là một ví dụ tốt về Feature
Engineering kết hợp Missing Value Handling:

``` python
df["mileage_missing"] = (
    used & df["mileage_km"].isna()
).astype(int)
```

Sau đó điền số km theo trung vị của đời xe. Feature này giúp mô hình
phân biệt số km được khai báo với số km được ước lượng.

## 4.2. Vấn đề 1: Điền Missing Values trước khi Split

**Mức độ: Cao -- cần sửa.**

Trong code:

``` python
med_by_year = df[used].groupby(
    "mfdate"
)["mileage_km"].median()

fill = df["mfdate"].map(med_by_year)

fill = fill.fillna(
    df.loc[used, "mileage_km"].median()
)
```

Median đang được tính trên toàn bộ dataset. Tương tự, hàm
`fill_by_group_mode(...)` tính Mode theo hãng và dòng xe trên toàn bộ
dataset.

Như vậy, dữ liệu Test đã tham gia vào việc tính tham số preprocessing.
Dù không dùng `price_tr` để điền các feature này, đây vẫn là leakage từ
thông tin phân phối của Test.

### Cách sửa

Quy trình đúng:

1.  Chia Train/Test.
2.  Tính Median/Mode chỉ trên Train.
3.  Dùng các thống kê học được để transform Train.
4.  Dùng chính các thống kê đó để transform Test.

Ví dụ minh họa:

``` python
from sklearn.model_selection import train_test_split

train, test = train_test_split(
    df,
    test_size=0.2,
    random_state=42
)

med_by_year = (
    train[train["condition_ad"] == "Đã sử dụng"]
    .groupby("mfdate")["mileage_km"]
    .median()
)

global_median = train.loc[
    train["condition_ad"] == "Đã sử dụng",
    "mileage_km"
].median()

def fill_mileage(frame):
    frame = frame.copy()

    used = frame["condition_ad"] == "Đã sử dụng"
    missing = used & frame["mileage_km"].isna()

    frame["mileage_missing"] = missing.astype(int)

    fill = frame["mfdate"].map(med_by_year)
    fill = fill.fillna(global_median)

    frame.loc[missing, "mileage_km"] = fill[missing]

    new_car = (
        (frame["condition_ad"] == "Mới")
        & frame["mileage_km"].isna()
    )

    frame.loc[new_car, "mileage_km"] = 0

    return frame
```

Đây là code minh họa nguyên tắc, chưa phải bản thay thế hoàn chỉnh cho
notebook. Các phép điền khác cũng cần được triển khai tương tự.

**Lưu ý với Cross-validation:** Mỗi fold phải tự fit các thống kê từ
phần training của fold đó. Không fit một lần trên toàn bộ Train rồi dùng
chung cho tất cả fold.

## 4.3. Vấn đề 2: Gộp nhãn hiếm trước khi Split

**Mức độ: Cao -- cần sửa.**

Trong code:

``` python
BRAND_MIN, MODEL_MIN = 30, 10

def group_hierarchical(frame, brand_min, model_min):
    brand = frame["carbrand"]

    brand_grp = brand.where(
        brand.map(brand.value_counts()) >= brand_min,
        brand_other
    )

    full = brand + " " + frame["carmodel"]

    keep = (
        full.map(full.value_counts()) >= model_min
    ) & (frame["carmodel"] != "Dòng khác")

    model_grp = full.where(
        keep,
        brand_grp + " - dòng khác"
    )

    return brand_grp, model_grp
```

Số lượng mẫu của toàn bộ dataset được sử dụng để xác định nhãn nào đủ
điều kiện giữ lại.

Ví dụ:

-   Toyota Vios có 12 bản ghi Train.
-   Có thêm 3 bản ghi Test.
-   Tổng cộng 15 bản ghi.
-   Ngưỡng giữ lại là 10.

Nhãn Toyota Vios được giữ lại nhờ cả dữ liệu Test.

Cách đúng là học bảng mapping từ Train, sau đó áp dụng mapping lên Test.
Nhãn mới hoặc nhãn không đủ điều kiện nên được đưa về nhóm phù hợp đã
định nghĩa.

Điều này cũng áp dụng cho thí nghiệm ngưỡng 30/10 bằng Cross-validation
ở cell 36: nhóm nhãn được tính trước khi thực hiện các fold, nên thông
tin từ validation fold ảnh hưởng đến việc gộp nhãn.

**Khuyến nghị:** Viết `BrandModelGrouper` có hai phương thức:

-   `fit(X_train)`: học số lượng và mapping.
-   `transform(X)`: áp dụng mapping đã học.

Có thể tích hợp Transformer này vào Scikit-learn Pipeline.

## 4.4. Vấn đề 3: Loại giá đặt cọc bằng Median của toàn bộ dữ liệu

**Mức độ: Cao -- cần sửa.**

Code:

``` python
grp = df.groupby(
    ["carbrand", "carmodel", "mfdate"]
)["price_tr"]

ref = grp.transform("median")
n_grp = grp.transform("size")

deposit = (
    (n_grp >= 3)
    & (df["price_tr"] < 0.3 * ref)
)
```

Median được tính trên toàn bộ dataset, trong đó có Target của Test. Sau
đó, kết quả được dùng để quyết định loại các bản ghi.

Mục đích phát hiện giá đặt cọc là hợp lý, nhưng cách thực hiện có thể
làm phân phối Test trở nên thuận lợi hơn.

Hai hướng xử lý:

1.  Tốt nhất: phát hiện giá đặt cọc bằng thông tin độc lập với Target,
    chẳng hạn nội dung mô tả tin đăng, từ khóa trả góp hoặc đặt cọc.
2.  Nếu dùng thống kê giá: xây dựng quy tắc từ Train hoặc một nguồn tham
    chiếu độc lập, sau đó áp dụng nhất quán cho dữ liệu mới.

## 4.5. Vấn đề 4: Log giá và Feature Engineering

Code:

``` python
df["price_log"] = np.log(df["price_tr"])
```

Đây là phép biến đổi Target, không phải feature đầu vào. Bản thân phép
biến đổi bằng công thức cố định không gây Data Leakage chỉ vì thực hiện
trước Split, miễn là không sử dụng thống kê của toàn bộ Target để lựa
chọn hoặc điều chỉnh phép biến đổi.

Tương tự:

``` python
df["age"] = CURRENT_YEAR - df["mfdate"]

df["km_per_year"] = (
    df["mileage_km"] / df["age"].clip(lower=1)
)
```

Đây là các phép biến đổi xác định bằng công thức và có thể thực hiện
trước Split.

Lưu ý: `CURRENT_YEAR = 2026` cần được quản lý nhất quán khi triển khai
model trong những năm tiếp theo.

------------------------------------------------------------------------

# 5. Đánh giá `model.ipynb`

## 5.1. Điểm tốt

Notebook thực hiện nhiều thí nghiệm:

-   So sánh One-Hot Encoding và Ordinal Encoding.
-   Random Forest bằng Scikit-learn.
-   Tự cài đặt Decision Tree và Random Forest bằng NumPy.
-   So sánh Ridge Regression và Random Forest.
-   Randomized Search và Grid Search.
-   OOB Evaluation.
-   Feature Importance và Permutation Importance.
-   Phân tích Log Target và xử lý mất cân bằng.
-   Phân tích tin đăng trùng.
-   Bootstrap để so sánh model.
-   Export và kiểm tra model sau khi load lại.

Đây là cấu trúc khá tốt cho một project nghiên cứu ML.

## 5.2. Vấn đề 1: Fit Preprocessor trước Cross-validation

**Mức độ: Rất cao -- ưu tiên sửa số 1.**

Trong cell 3:

``` python
prep_tree, prep_lin = make_prep("tree"), make_prep("lin")

XT_tr = prep_tree.fit_transform(tr)
XT_te = prep_tree.transform(te)

XL_tr = prep_lin.fit_transform(tr)
XL_te = prep_lin.transform(te)
```

Bạn đã fit OneHotEncoder và StandardScaler trên toàn bộ Train.

Sau đó, ở cell 12:

``` python
rs_rf = RandomizedSearchCV(
    RandomForestRegressor(...),
    param_dist,
    cv=folds3,
    ...
)

rs_rf.fit(XT_tr, y_tr)
```

Khi CV chia Train thành nhiều fold, encoder và scaler đã biết thông tin
từ toàn bộ Train, bao gồm cả validation fold của từng vòng.

Đây là leakage trong Cross-validation.

### Cách sửa: Đưa preprocessing vào Pipeline

Ví dụ với Random Forest:

``` python
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV

rf_pipeline = Pipeline([
    ("preprocessor", make_prep("tree")),
    ("model", RandomForestRegressor(
        random_state=RANDOM_STATE,
        n_jobs=-1
    ))
])

param_dist = {
    "model__n_estimators": [300],
    "model__max_depth": [20, 30, None],
    "model__min_samples_leaf": [1, 2, 3, 5],
    "model__max_features": [0.33, 0.5, 0.8],
}

search = RandomizedSearchCV(
    rf_pipeline,
    param_distributions=param_dist,
    n_iter=12,
    cv=folds3,
    scoring="neg_root_mean_squared_error",
    random_state=RANDOM_STATE,
    n_jobs=1
)

search.fit(tr, y_tr)
```

Với Ridge:

``` python
ridge_pipeline = Pipeline([
    ("preprocessor", make_prep("lin")),
    ("model", Ridge())
])

param_grid = {
    "model__alpha": np.logspace(-3, 3, 25)
}
```

Sau khi sử dụng Pipeline:

-   Mỗi fold tự fit OneHotEncoder.
-   Mỗi fold tự fit StandardScaler nếu có.
-   Validation fold chỉ được transform.
-   Model được fit lại trên toàn bộ Train sau khi tìm được tham số tốt
    nhất.

## 5.3. Vấn đề 2: Test set được sử dụng trong nhiều thí nghiệm

Trong notebook, bạn ghi Test chỉ dùng một lần để đánh giá cuối cùng. Tuy
nhiên, code có nhiều phần sử dụng Test:

  Cell     Hoạt động
  -------- -----------------------------------------------------------
  19       So sánh Decision Tree tự viết với Scikit-learn trên Test.
  24--25   So sánh một cây và cả rừng trên Test.
  28--30   Đánh giá các model trên Test.
  34--38   Phân tích dự đoán, residual và các xe sai nhiều.
  39--41   Bootstrap trên Test.
  46--47   Permutation Importance trên Test.
  49--50   Đường khấu hao, có đối chiếu các tin thật trong Test.

Không phải mọi thao tác trên đều sai:

-   Bootstrap trên Test có thể dùng để ước lượng độ bất định.
-   Residual Analysis trên Test hữu ích.
-   Permutation Importance trên Test có thể dùng để diễn giải model đã
    khóa.

Vấn đề xuất hiện khi kết quả Test được dùng để thay đổi feature, thuật
toán, hyperparameter hoặc lựa chọn model.

### Cách tổ chức tốt hơn

  Hoạt động                                Dataset
  ---------------------------------------- --------------------------
  Chọn feature, encoding, hyperparameter   Train + Cross-validation
  Chọn model                               Train + Cross-validation
  Đánh giá và phân tích cuối cùng          Test

Nếu đã dùng Test để đưa ra quyết định trong quá trình phát triển, nên
tạo một tập kiểm tra mới từ dữ liệu độc lập để có đánh giá cuối cùng
đáng tin cậy hơn.

## 5.4. Vấn đề 3: Random Split có thể đánh giá cao khả năng tổng quát hóa

Code hiện tại:

``` python
idx_tr, idx_te = train_test_split(
    df.index,
    test_size=0.2,
    stratify=df["segment"],
    random_state=RANDOM_STATE
)
```

Đây là lựa chọn hợp lý để giữ tỷ lệ các phân khúc giá.

Tuy nhiên, dữ liệu là tin đăng bán xe. Một chiếc xe có thể được đăng lại
nhiều lần với giá hơi khác nhau.

Notebook đã phát hiện vấn đề này trong mục 10:

-   14% tin trong Test có bản sao trong Train.
-   MAPE trên nhóm có bản sao thấp hơn nhóm không có bản sao.
-   StratifiedKFold cho MAPE khoảng 16,1%.
-   StratifiedGroupKFold cho MAPE khoảng 16,7%.

Nhận xét: Random Split có thể giúp model ghi nhớ những chiếc xe đã từng
nhìn thấy.

### Hai cách đánh giá nên phân biệt

**Trường hợp A: Dự đoán giá của một tin đăng bất kỳ**

Có thể sử dụng Stratified Random Split nếu mục tiêu thực sự là dự đoán
trên phân phối tin đăng tương tự.

**Trường hợp B: Dự đoán giá của những chiếc xe chưa từng xuất hiện trong
dữ liệu huấn luyện**

Nên sử dụng Group Split theo `group_key`.

Nếu muốn mô phỏng việc triển khai thực tế trên các tin đăng mới trong
tương lai, nên cân nhắc thêm Time-based Split.

Ba cách chia này trả lời ba câu hỏi khác nhau, không nên coi một phương
pháp là đại diện cho mọi tình huống.

## 5.5. Các vấn đề khác

  -----------------------------------------------------------------------
  Vấn đề                  Nhận xét                Mức ưu tiên
  ----------------------- ----------------------- -----------------------
  Ridge GridSearchCV      Preprocessing được fit  Cao
                          trước CV.               

  RF RandomizedSearchCV   Preprocessing được fit  Cao
                          trước CV.               

  Grouping category       Dùng toàn bộ dữ liệu    Cao
                          trước CV.               

  Imputation              Dùng toàn bộ dữ liệu    Cao
                          trước Split.            

  Deposit filtering       Dùng Target toàn bộ     Cao
                          dataset.                

  Test usage              Có nhiều thí nghiệm     Cao
                          trên Test.              

  Scratch RF Binner       Quantile binning fit    Trung bình
                          toàn bộ Train trước khi 
                          đánh giá OOB.           

  Random Split            Có thể bị ảnh hưởng bởi Trung bình
                          tin đăng lại.           

  CURRENT_YEAR            Hard-code 2026.         Trung bình
  -----------------------------------------------------------------------

### OOB của Random Forest tự cài đặt

Trong class `Binner`:

``` python
self.edges_ = [
    np.unique(np.quantile(X[:, j], qs))
    for j in range(X.shape[1])
]
```

Bạn fit các ngưỡng bin trên toàn bộ Train trước khi thực hiện bootstrap
và OOB.

Do đó, những mẫu OOB vẫn ảnh hưởng đến cách phân chia bin thông qua phân
phối feature.

Đây không phải leakage từ Target, nhưng OOB không hoàn toàn độc lập đối
với bước preprocessing. Nếu muốn OOB nghiêm ngặt hơn, cần thiết kế lại
quá trình học bin hoặc dùng một tập validation độc lập.

### Kiểm chứng Decision Tree tự cài đặt

Cell 19 so sánh cây tự viết với cây Scikit-learn trên Test để kiểm chứng
thuật toán. Mục đích này hợp lý, nhưng tốt hơn nên dành một tập kiểm thử
thuật toán riêng hoặc sử dụng dữ liệu tổng hợp có kết quả kỳ vọng đã
biết.

------------------------------------------------------------------------

# 6. Pipeline đề xuất sau khi chỉnh sửa

Không cần viết lại toàn bộ project. Phần lớn code hiện tại có thể giữ
lại. Nên thay đổi cách phân chia trách nhiệm giữa
`preprocess_data.ipynb` và `model.ipynb`.

Đặc biệt, nên tách **Data Cleaning độc lập với model** và
**Model-specific Preprocessing**.

## 6.1. Pipeline mới

``` text
crawl_data.ipynb
    |
    v
raw_data_oto.csv
    |
    v
preprocess_data.ipynb — Data Cleaning
    |
    +-- Chuẩn hóa kiểu dữ liệu
    +-- Xử lý duplicate
    +-- Xử lý dữ liệu sai
    +-- Quy tắc nghiệp vụ cố định
    +-- Kiểm tra giá trị không hợp lệ
    |
    v
clean_data_oto.csv
    |
    v
model.ipynb — Data Splitting
    |
    +---------------------+
    |                     |
    v                     v
  Train                  Test
    |                     |
    v                     v
Fit Preprocessor       Transform
    |                  bằng tham số
    v                  từ Train
Train Model                |
    |                      |
    +----------+-----------+
               |
               v
        Model Evaluation
```

## 6.2. Phân chia trách nhiệm giữa các notebook

  -------------------------------------------------------------------------
  Notebook                  Giữ nguyên              Thay đổi
  ------------------------- ----------------------- -----------------------
  `crawl_data.ipynb`        Crawl, retry, resume,   Thêm validation và
                            CSV                     metadata.

  `preprocess_data.ipynb`   Cleaning, kiểm tra bất  Chuyển imputation và
                            thường, EDA             grouping phụ thuộc
                                                    thống kê sang model.

  `model.ipynb`             Ridge, RF, Scratch RF,  Chia tập trước,
                            metrics                 Pipeline, CV đúng cách.

  `model.ipynb`             Export model            Lưu cả preprocessing và
                                                    mapping.
  -------------------------------------------------------------------------

## 6.3. Clean CSV nên chứa gì?

Nên:

-   Giữ các giá trị thiếu chưa thể xử lý bằng quy tắc cố định.
-   Giữ dữ liệu gốc để đối chiếu.
-   Giữ cột đánh dấu dữ liệu đã bị sửa hoặc ước lượng.
-   Không thực hiện One-Hot Encoding.
-   Không Standardization.
-   Không tính Median/Mode từ toàn bộ dataset.
-   Không gộp category dựa trên tần suất toàn bộ dataset.

Có thể tạo thêm các cột:

``` text
mileage_km_original
mileage_missing
condition_corrected
price_tr
source_url
```

Nhờ đó có thể kiểm tra nguồn gốc từng giá trị và giải thích cách xử lý
trong báo cáo.

------------------------------------------------------------------------

# 7. Thứ tự ưu tiên sửa code

## 7.1. Ưu tiên rất cao

1.  **Chuyển Imputation sang sau Split:** không dùng Median/Mode của
    Test.
2.  **Chuyển Grouping sang Transformer:** học mapping hãng/dòng xe từ
    Train.
3.  **Sửa Deposit Filtering:** không dùng Target của Test để quyết định
    loại mẫu.
4.  **Đưa Preprocessor vào Pipeline:** đảm bảo từng CV fold tự fit
    preprocessing.
5.  **Kiểm soát việc sử dụng Test:** chỉ dùng Test cho đánh giá cuối
    cùng.

## 7.2. Ưu tiên tiếp theo

-   Thử Group-based Train/Test Split.
-   Thử Time-based Split nếu mục tiêu là dự đoán giá tin đăng trong
    tương lai.
-   Cải thiện OOB của Random Forest tự cài đặt.
-   Thêm kiểm tra dữ liệu sau crawl.
-   Chuẩn hóa cấu hình và phiên bản model.

------------------------------------------------------------------------

# 8. Kết luận

Project đã vượt qua mức một bài thực hành ML cơ bản.

Điểm mạnh:

-   Có tư duy thực nghiệm, không chỉ xây dựng model.
-   Có so sánh thuật toán.
-   Có tự cài đặt Random Forest.
-   Có phân tích feature, dữ liệu bất thường và tin đăng trùng.
-   Có nhiều phương pháp đánh giá và kiểm tra model sau khi lưu.

Tuy nhiên, cần phân biệt:

-   **Model chạy được và có kết quả tốt:** đã làm được.
-   **Quy trình thực nghiệm đảm bảo kết quả không bị leakage:** vẫn cần
    chỉnh sửa.

Đặc biệt, kết quả MAPE 15,5% của Random Forest hiện tại nên được xem là
kết quả tham khảo trên cách chia ngẫu nhiên hiện tại, chưa nên coi là
kết quả tổng quát hóa cuối cùng trước khi xử lý các vấn đề leakage.

## Khuyến nghị cuối cùng

Không cần vội thử thêm XGBoost, LightGBM hay Neural Network.

Hãy sửa Data Leakage và thiết kế lại Cross-validation trước, sau đó chạy
lại Ridge và Random Forest trên cùng điều kiện. Khi đó mới có thể đánh
giá chính xác mức cải thiện đến từ thuật toán hay từ cách xử lý dữ liệu.

Đây là hướng nâng cấp project thành một pipeline Data Science có khả
năng tái lập và đủ chặt chẽ để trình bày trong báo cáo nghiên cứu.
