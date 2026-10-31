# Bảng số liệu cho báo cáo và slide
Tự sinh khi chạy preprocess_data → process_data → model. Mỗi bảng cũng có bản .csv cùng tên.

# Tiền xử lý (preprocess_data.ipynb)

## Từ điển dữ liệu

`tables/tu_dien_du_lieu.csv`

| cột                     | ý nghĩa                       | người bán nhập                                 | kiểu sau xử lý        |
|:------------------------|:------------------------------|:-----------------------------------------------|:----------------------|
| mileage_v2 → mileage_km | Số km đã đi                   | gõ tự do (dạng 109.366)                        | số                    |
| carorigin               | Xuất xứ                       | chọn từ danh sách (11 giá trị), không bắt buộc | phân loại             |
| condition_ad            | Tình trạng (Mới / Đã sử dụng) | chọn từ danh sách                              | phân loại             |
| veh_warranty_policy     | Chính sách bảo hành           | một giá trị duy nhất                           | bỏ                    |
| carbrand                | Hãng                          | chọn từ danh sách                              | phân loại             |
| carmodel                | Dòng xe                       | chọn từ danh sách theo hãng                    | phân loại             |
| mfdate                  | Năm sản xuất                  | chọn từ danh sách (có "trước năm 1980")        | số                    |
| gearbox                 | Hộp số                        | chọn từ danh sách (3 giá trị)                  | phân loại             |
| fuel                    | Nhiên liệu                    | chọn từ danh sách (4 giá trị)                  | phân loại             |
| cartype                 | Kiểu dáng                     | chọn từ danh sách (9 giá trị), không bắt buộc  | phân loại             |
| carseats                | Số chỗ                        | chọn từ danh sách (có "Khác"), không bắt buộc  | số                    |
| price                   | Giá rao bán (đồng)            | gõ tự do                                       | biến mục tiêu         |
| url                     | Đường dẫn tin                 | sinh tự động, chứa quận/huyện và tỉnh          | trích province rồi bỏ |

## Giá trị thiếu và cách xử lý

`tables/gia_tri_thieu.csv`

| cột       |   số thiếu |    % | cách xử lý                                                       | nơi xử lý                                       |
|:----------|-----------:|-----:|:-----------------------------------------------------------------|:------------------------------------------------|
| Xuất xứ   |       5865 | 41.5 | nhãn "Không rõ" (preprocess)                                     | preprocess_data                                 |
| Kiểu dáng |       4663 | 33.0 | mode theo dòng xe, còn lại "Không rõ" (process, học từ train)    | process_data                                    |
| Số chỗ    |       3579 | 25.3 | mode theo dòng xe → hãng (process, học từ train)                 | process_data                                    |
| Số km     |       1479 | 10.5 | xe mới = 0 (preprocess); xe cũ: trung vị theo đời + cờ (process) | preprocess_data (xe mới) + process_data (xe cũ) |
| Giá       |          1 |  0.0 | xóa dòng (không điền biến mục tiêu)                              | preprocess_data                                 |

*Tính sau khi xóa tin trùng, trước khi điền.*

## Số tin theo phân khúc giá

`tables/phan_khuc_gia.csv`

| phân khúc   |   số mẫu |    % |   gấp (so với phân khúc lớn nhất) |
|:------------|---------:|-----:|----------------------------------:|
| < 200 triệu |   2093.0 | 14.9 |                               2.8 |
| 200-500     |   5915.0 | 42.1 |                               1.0 |
| 500-1.000   |   4529.0 | 32.2 |                               1.3 |
| 1-2 tỷ      |   1071.0 |  7.6 |                               5.5 |
| > 2 tỷ      |    458.0 |  3.3 |                              12.9 |

*Tính trên dữ liệu sau tiền xử lý, trước khi lọc giá đặt cọc ở process_data.*

## Số tin còn lại qua từng bước làm sạch (preprocess)

`tables/thong_ke_lam_sach.csv`

| bước                                |   còn lại |   loại bỏ |
|:------------------------------------|----------:|----------:|
| Dữ liệu thô                         |     14835 |         0 |
| Loại tin trùng                      |     14144 |       691 |
| Loại giá thiếu, < 20 triệu, > 10 tỷ |     14080 |        64 |
| Loại giá giả 123.456.789            |     14066 |        14 |

*Bước lọc giá trả trước / đặt cọc nằm ở process_data (bảng thong_ke_xu_ly).*

## Thống kê mô tả biến số (sau tiền xử lý)

`tables/thong_ke_mo_ta.csv`

|            |   thiếu |   count |    mean |     std |   min |     25% |     50% |     75% |      max |
|:-----------|--------:|--------:|--------:|--------:|------:|--------:|--------:|--------:|---------:|
| price_tr   |     0.0 | 14066.0 |   600.1 |   659.8 |  20.0 |   280.0 |   455.0 |   680.0 |   9769.0 |
| age        |     0.0 | 14066.0 |     7.0 |     6.2 |   0.0 |     2.0 |     5.0 |    10.0 |     47.0 |
| mileage_km |   826.0 | 13240.0 | 69950.9 | 62945.4 |   0.0 | 20000.0 | 61000.0 | 99999.0 | 500000.0 |
| carseats   |  3552.0 | 10514.0 |     5.9 |     1.8 |   2.0 |     5.0 |     5.0 |     7.0 |     16.0 |

## Thống kê mô tả biến phân loại (sau tiền xử lý)

`tables/thong_ke_mo_ta_phan_loai.csv`

|              |   số giá trị |   thiếu | giá trị phổ biến nhất   |   % phổ biến nhất |
|:-------------|-------------:|--------:|:------------------------|------------------:|
| carbrand     |           69 |       0 | Toyota                  |              20.2 |
| carmodel     |          466 |       0 | Innova                  |               4.2 |
| carorigin    |           11 |       0 | Không rõ                |              41.5 |
| condition_ad |            2 |       0 | Đã sử dụng              |              91.3 |
| gearbox      |            3 |       0 | Tự động                 |              79.4 |
| fuel         |            4 |       0 | Xăng                    |              72.7 |
| cartype      |            9 |    4623 | SUV / Cross over        |              40.3 |
| province     |           63 |       0 | tp-ho-chi-minh          |              49.4 |

# Xử lý dữ liệu sau khi chia tập (process_data.ipynb)

## Chia train/test phân tầng theo phân khúc giá

`tables/chia_train_test.csv`

| phân khúc   |   train (tin) |   test (tin) |   train (%) |   test (%) |
|:------------|--------------:|-------------:|------------:|-----------:|
| < 200 triệu |        1674.0 |        419.0 |        14.9 |       14.9 |
| 200-500     |        4732.0 |       1183.0 |        42.1 |       42.0 |
| 500-1.000   |        3623.0 |        906.0 |        32.2 |       32.2 |
| 1-2 tỷ      |         857.0 |        214.0 |         7.6 |        7.6 |
| > 2 tỷ      |         366.0 |         92.0 |         3.3 |        3.3 |
| Tổng        |       11252.0 |       2814.0 |       100.0 |      100.0 |

*Số tin trước khi lọc giá trả trước / đặt cọc (mục 2).*

## Ví dụ tin nghi giá trả trước / đặt cọc

`tables/vi_du_gia_dat_coc.csv`

| hãng          | dòng xe   |   năm | tình trạng   |   giá rao (triệu) |   trung vị nhóm ở train (triệu) |
|:--------------|:----------|------:|:-------------|------------------:|--------------------------------:|
| Toyota        | Camry     |  2026 | Đã sử dụng   |               300 |                            1360 |
| Ford          | Everest   |  2026 | Đã sử dụng   |               320 |                            1310 |
| Toyota        | Fortuner  |  2026 | Mới          |               125 |                            1275 |
| Hyundai       | Santa Fe  |  2025 | Mới          |               220 |                            1079 |
| Mercedes Benz | E Class   |  2019 | Đã sử dụng   |               156 |                             899 |

*Trung vị nhóm cùng hãng-dòng-năm, học từ train. Giá rao < 30% trung vị thì bị loại.*

## So sánh 3 cách gộp nhãn hiếm (5-fold CV trên train)

`tables/so_sanh_gop_nhan.csv`

|                               |   số nhóm dòng xe |   Ridge - MAPE |   Ridge - MAPE < 200 triệu |   Ridge - MAPE > 2 tỷ |   Random Forest - MAPE |   Random Forest - MAPE < 200 triệu |   Random Forest - MAPE > 2 tỷ |
|:------------------------------|------------------:|---------------:|---------------------------:|----------------------:|-----------------------:|-----------------------------------:|------------------------------:|
| Cũ (50 / 30)                  |            95.000 |          0.238 |                      0.580 |                 0.479 |                  0.175 |                              0.429 |                         0.329 |
| Gộp theo cấp (50 / 30)        |           114.000 |          0.228 |                      0.543 |                 0.455 |                  0.171 |                              0.400 |                         0.325 |
| Gộp theo cấp (30 / 10) - chọn |           196.000 |          0.196 |                      0.476 |                 0.340 |                  0.166 |                              0.397 |                         0.294 |

*Ridge alpha = 0,3; Random Forest 100 cây, max_depth 30, max_features 0,33.*

## Thử thêm vị trí làm đặc trưng (5-fold CV trên train)

`tables/thu_vi_tri.csv`

|                        |   Ridge - MAPE |   Ridge - MAPE < 200 triệu |   Ridge - MAPE > 2 tỷ |   Random Forest - MAPE |   Random Forest - MAPE < 200 triệu |   Random Forest - MAPE > 2 tỷ |
|:-----------------------|---------------:|---------------------------:|----------------------:|-----------------------:|-----------------------------------:|------------------------------:|
| Không dùng vị trí      |         0.1957 |                     0.4758 |                0.3395 |                 0.1663 |                             0.3965 |                        0.2941 |
| + miền (3 nhóm)        |         0.1956 |                     0.4749 |                0.3401 |                 0.1654 |                             0.3919 |                        0.2969 |
| + tỉnh/thành (11 nhóm) |         0.1961 |                     0.4765 |                0.3404 |                 0.1658 |                             0.3949 |                        0.2979 |

## Đối chứng: điền sẵn so với điền trong từng fold (5-fold CV, Random Forest 150 cây)

`tables/doi_chung_cv.csv`

|                                       |   MAPE |   MAPE < 200 triệu |   MAPE 200-500 |   MAPE 500-1.000 |   MAPE 1-2 tỷ |   MAPE > 2 tỷ |
|:--------------------------------------|-------:|-------------------:|---------------:|-----------------:|--------------:|--------------:|
| Điền sẵn (thống kê của toàn bộ train) | 0.1681 |             0.3994 |         0.1271 |           0.1071 |        0.1703 |        0.2976 |
| Điền trong từng fold (Pipeline)       | 0.1685 |             0.3990 |         0.1274 |           0.1080 |        0.1715 |        0.2983 |
| Chênh lệch (điểm %)                   | 0.0438 |            -0.0397 |         0.0249 |           0.0835 |        0.1263 |        0.0625 |

*Hai dòng đầu là MAPE (tỉ lệ); dòng cuối là chênh lệch tính bằng điểm %.*

## Thống kê xử lý dữ liệu sau khi chia tập

`tables/thong_ke_xu_ly.csv`

|                              |   train |   test |
|:-----------------------------|--------:|-------:|
| số tin sau khi chia          |   11252 |   2814 |
| loại giá trả trước / đặt cọc |      99 |     17 |
| số tin còn lại               |   11153 |   2797 |
| km xe cũ được điền (cờ = 1)  |     653 |    161 |
| kiểu dáng điền theo dòng xe  |    3443 |    884 |
| kiểu dáng → Không rõ         |     208 |     49 |
| số chỗ được điền             |    2817 |    725 |
| nhóm hãng                    |      27 |     27 |
| nhóm dòng xe                 |     196 |    193 |

## Tóm tắt các bước xử lý (process_data)

`tables/tom_tat_xu_ly.csv`

| bước                            | tham số học từ train                                        | ảnh hưởng                                          |
|:--------------------------------|:------------------------------------------------------------|:---------------------------------------------------|
| 1. Chia train/test              | không (chỉ phân tầng theo phân khúc giá)                    | 11.252 / 2.814 tin                                 |
| 2. Lọc giá trả trước / đặt cọc  | bảng trung vị giá 931 nhóm hãng-dòng-năm                    | loại 99 tin train, 17 tin test                     |
| 3. Điền thiếu (CarImputer)      | trung vị km 45 đời xe; mode kiểu dáng / số chỗ theo dòng xe | điền km 653 / 161 xe cũ                            |
| 3. Gộp nhãn (BrandModelGrouper) | 25 hãng, 178 dòng xe đủ ngưỡng                              | 27 nhóm hãng, 196 nhóm dòng xe                     |
| 4. Đặc trưng Ridge, group_key   | không (công thức)                                           | age², log(km), log(km/năm)                         |
| 5. Thí nghiệm gộp nhãn, vị trí  | CV chỉ trên train                                           | chọn gộp theo cấp 30 / 10, không dùng vị trí       |
| 6. Đối chứng điền trong fold    | CV chỉ trên train                                           | chênh lệch MAPE 0,04 điểm %                        |
| 7. Xuất file                    |                                                             | train_data.csv 11.153 tin, test_data.csv 2.797 tin |

# Mô hình (model.ipynb)

## One-hot so với mã số thứ tự (5-fold CV trên train)

`tables/so_sanh_ma_hoa.csv`

|                                   |   số cột |   MAPE |   MAPE < 200 triệu |   MAPE 200-500 |   MAPE 500-1.000 |   MAPE 1-2 tỷ |   MAPE > 2 tỷ |
|:----------------------------------|---------:|-------:|-------------------:|---------------:|-----------------:|--------------:|--------------:|
| One-hot, max_features = 0.33      | 258.0000 | 0.1681 |             0.3994 |         0.1271 |           0.1071 |        0.1703 |        0.2976 |
| Mã số thứ tự, max_features = 0.33 |  12.0000 | 0.1904 |             0.4452 |         0.1444 |           0.1175 |        0.1911 |        0.4063 |
| Mã số thứ tự, max_features = 0.6  |  12.0000 | 0.1745 |             0.4210 |         0.1323 |           0.1074 |        0.1765 |        0.3156 |
| Mã số thứ tự, max_features = 1.0  |  12.0000 | 0.1781 |             0.4360 |         0.1358 |           0.1086 |        0.1773 |        0.3002 |

## Tham số tốt nhất (chọn trên train)

`tables/tham_so_tot_nhat.csv`

| mô hình                    | tham số tốt nhất                                                                    | cách chọn                 | điểm                  |
|:---------------------------|:------------------------------------------------------------------------------------|:--------------------------|:----------------------|
| Random Forest (thư viện)   | {'n_estimators': 300, 'min_samples_leaf': 1, 'max_features': 0.5, 'max_depth': 30}  | RandomizedSearchCV 3-fold | CV RMSE (log) 0.2745  |
| Random Forest (tự cài đặt) | {'max_depth': 30, 'min_samples_leaf': 2, 'max_features': 0.33, 'n_estimators': 100} | OOB, 30 cây mỗi cấu hình  | OOB RMSE (log) 0.2775 |
| Ridge (thư viện)           | alpha = 0.5623                                                                      | GridSearchCV 5-fold       | CV RMSE (log) 0.2994  |

## Kết quả trên tập test

`tables/ket_qua_test.csv`

|                            |   MAPE |   MedAPE |   MAE (triệu) |   RMSE (triệu) |   R2 (log) |   ±10% |   ±20% |   Thời gian fit (s) |
|:---------------------------|-------:|---------:|--------------:|---------------:|-----------:|-------:|-------:|--------------------:|
| Baseline (trung vị)        |  0.880 |    0.404 |       322.522 |        642.106 |     -0.004 |  0.141 |  0.256 |               0.001 |
| Ridge - thư viện           |  0.185 |    0.105 |       107.720 |        313.008 |      0.878 |  0.479 |  0.752 |               0.038 |
| Random Forest - thư viện   |  0.151 |    0.088 |        89.685 |        269.578 |      0.910 |  0.543 |  0.794 |               7.252 |
| Random Forest - tự cài đặt |  0.157 |    0.095 |        95.464 |        288.627 |      0.904 |  0.517 |  0.781 |              85.694 |

*MAPE, MedAPE, ±10%, ±20% là tỉ lệ; MAE, RMSE tính bằng triệu đồng; R² trên thang log.*

## MAPE theo phân khúc giá trên tập test

`tables/ket_qua_phan_khuc.csv`

|                            |   MAPE < 200 triệu |   MAPE 200-500 |   MAPE 500-1.000 |   MAPE 1-2 tỷ |   MAPE > 2 tỷ |
|:---------------------------|-------------------:|---------------:|-----------------:|--------------:|--------------:|
| Baseline (trung vị)        |              3.754 |          0.377 |            0.310 |         0.643 |         0.840 |
| Ridge - thư viện           |              0.434 |          0.140 |            0.123 |         0.166 |         0.308 |
| Random Forest - thư viện   |              0.319 |          0.120 |            0.108 |         0.160 |         0.210 |
| Random Forest - tự cài đặt |              0.329 |          0.125 |            0.112 |         0.171 |         0.234 |

## Bootstrap 1.000 lần: khoảng tin cậy 95% của MAPE và hiệu ghép cặp

`tables/khoang_tin_cay.csv`

|                                  |   MAPE 2.5% (%) |   MAPE trung vị (%) |   MAPE 97.5% (%) |   hiệu 2.5% (điểm %) |   hiệu trung vị (điểm %) |   hiệu 97.5% (điểm %) | có ý nghĩa?   |
|:---------------------------------|----------------:|--------------------:|-----------------:|---------------------:|-------------------------:|----------------------:|:--------------|
| Ridge - thư viện                 |           17.20 |               18.42 |            19.85 |               nan    |                   nan    |                nan    | nan           |
| Random Forest - thư viện         |           14.20 |               15.13 |            16.11 |               nan    |                   nan    |                nan    | nan           |
| Random Forest - tự cài đặt       |           14.80 |               15.72 |            16.74 |               nan    |                   nan    |                nan    | nan           |
| Ridge − Random Forest (thư viện) |          nan    |              nan    |           nan    |                 2.42 |                     3.30 |                  4.42 | có            |
| RF tự cài đặt − RF thư viện      |          nan    |              nan    |           nan    |                 0.34 |                     0.62 |                  0.86 | có            |

## Độ quan trọng đặc trưng: impurity (train) và permutation (test)

`tables/do_quan_trong.csv`

|                    |   impurity - thư viện (%) |   impurity - tự cài đặt (%) |   permutation: tăng MAPE (điểm %) |   permutation: độ lệch chuẩn |
|:-------------------|--------------------------:|----------------------------:|----------------------------------:|-----------------------------:|
| Tuổi xe            |                      30.7 |                        28.7 |                              45.2 |                          0.8 |
| Hãng               |                      16.4 |                        16.1 |                              21.5 |                          0.7 |
| Kiểu dáng          |                       7.3 |                         7.8 |                              11.5 |                          0.2 |
| Hộp số             |                      17.0 |                        16.0 |                              10.7 |                          0.4 |
| Dòng xe            |                      12.9 |                        13.9 |                               8.2 |                          0.1 |
| Nhiên liệu         |                       3.0 |                         3.0 |                               5.7 |                          0.2 |
| Số chỗ             |                       3.0 |                         2.8 |                               5.5 |                          0.2 |
| Số km              |                       5.6 |                         7.0 |                               4.0 |                          0.2 |
| Số km / năm        |                       2.6 |                         2.5 |                               0.6 |                          0.1 |
| Xuất xứ            |                       1.3 |                         1.6 |                               0.3 |                          0.1 |
| Tình trạng         |                       0.1 |                         0.2 |                               0.0 |                          0.0 |
| Km là giá trị điền |                       0.2 |                         0.2 |                              -0.0 |                          0.0 |

## 10 xe Random Forest đoán sai nhiều nhất (tập test)

`tables/xe_doan_sai_nhat.csv`

| hãng          | dòng xe   |   năm | tình trạng   |   số km |   giá rao (triệu) |   dự đoán (triệu) |   lệch (%) | nhận xét                                                                   |
|:--------------|:----------|------:|:-------------|--------:|------------------:|------------------:|-----------:|:---------------------------------------------------------------------------|
| Mercedes Benz | AMG       |  2005 | Đã sử dụng   |  200000 |                30 |               236 |        687 | giá rao cực thấp: có thể giá cọc, xe hư hỏng hoặc nhập thiếu số            |
| Daewoo        | Matiz     |  2016 | Đã sử dụng   |  300000 |                23 |               134 |        484 | giá rao cực thấp: có thể giá cọc, xe hư hỏng hoặc nhập thiếu số            |
| Geely         | Dòng khác |  2026 | Mới          |       0 |               114 |               604 |        430 | xe đời mới, giá rao rất thấp: nghi giá trả trước / đặt cọc lọt lưới        |
| Hyundai       | Accent    |  2026 | Mới          |       0 |                90 |               465 |        417 | xe đời mới, giá rao rất thấp: nghi giá trả trước / đặt cọc lọt lưới        |
| MINI          | Cooper    |  2025 | Đã sử dụng   |   91000 |               199 |               751 |        278 | xe đời mới, giá rao rất thấp: nghi giá trả trước / đặt cọc lọt lưới        |
| GAC           | M8        |  2025 | Mới          |       0 |               168 |               621 |        270 | xe đời mới, giá rao rất thấp: nghi giá trả trước / đặt cọc lọt lưới        |
| Hãng khác     | Dòng khác |  2008 | Đã sử dụng   |  200000 |                35 |               108 |        209 | giá rao cực thấp: có thể giá cọc, xe hư hỏng hoặc nhập thiếu số            |
| VinFast       | Dòng khác |  2025 | Đã sử dụng   |       2 |               200 |               590 |        195 | xe đời mới, giá rao rất thấp: nghi giá trả trước / đặt cọc lọt lưới        |
| Mercedes Benz | GLA Class |  2015 | Đã sử dụng   |  100000 |               418 |              1200 |        187 | dòng xe hiếm bị gộp '- dòng khác': mô hình chỉ biết mức giá chung của hãng |
| Toyota        | Corolla   |  1994 | Đã sử dụng   |  158708 |                25 |                70 |        180 | giá rao cực thấp: có thể giá cọc, xe hư hỏng hoặc nhập thiếu số            |

*Cột nhận xét gán theo quy tắc đơn giản để gợi ý nguyên nhân, cần đọc tin gốc để chắc chắn.*

## Log giá và 3 kỹ thuật cân bằng (5-fold CV trên train, Random Forest)

`tables/thi_nghiem_can_bang.csv`

|                         |   cỡ train mỗi fold |   MAPE |   MedAPE |   MAE (triệu) |   MAPE < 200 triệu |   MAPE 200-500 |   MAPE 500-1.000 |   MAPE 1-2 tỷ |   MAPE > 2 tỷ |
|:------------------------|--------------------:|-------:|---------:|--------------:|-------------------:|---------------:|-----------------:|--------------:|--------------:|
| Giá gốc                 |            8922.000 |  0.200 |    0.096 |       103.357 |              0.540 |          0.154 |            0.117 |         0.171 |         0.228 |
| Log giá                 |            8922.000 |  0.166 |    0.090 |       102.424 |              0.397 |          0.126 |            0.107 |         0.169 |         0.284 |
| Log giá + trọng số mẫu  |            8922.000 |  0.169 |    0.089 |        99.699 |              0.389 |          0.134 |            0.112 |         0.159 |         0.253 |
| Log giá + Oversampling  |            9834.000 |  0.167 |    0.087 |        98.556 |              0.403 |          0.127 |            0.109 |         0.165 |         0.250 |
| Log giá + Undersampling |            6927.000 |  0.172 |    0.095 |       104.077 |              0.388 |          0.141 |            0.110 |         0.164 |         0.277 |

## Tin đăng lại: MAPE theo nhóm có / không có bản sao (test) và CV chia theo nhóm (train)

`tables/tin_dang_lai.csv`

|                                       |   số tin |   % test |   MAPE Ridge (thư viện) |   MAPE RF (thư viện) |   MAPE RF (tự cài đặt) |    MAPE |   MAPE < 200 triệu |   MAPE 200-500 |   MAPE 500-1.000 |   MAPE 1-2 tỷ |   MAPE > 2 tỷ |
|:--------------------------------------|---------:|---------:|------------------------:|---------------------:|-----------------------:|--------:|-------------------:|---------------:|-----------------:|--------------:|--------------:|
| có bản sao trong train                |  400.000 |   14.301 |                   0.128 |                0.101 |                  0.103 | nan     |            nan     |        nan     |          nan     |       nan     |       nan     |
| trong đó xe đã dùng                   |  262.000 |    9.367 |                   0.118 |                0.102 |                  0.105 | nan     |            nan     |        nan     |          nan     |       nan     |       nan     |
| không có bản sao                      | 2397.000 |   85.699 |                   0.194 |                0.159 |                  0.166 | nan     |            nan     |        nan     |          nan     |       nan     |       nan     |
| toàn bộ test                          | 2797.000 |  100.000 |                   0.185 |                0.151 |                  0.157 | nan     |            nan     |        nan     |          nan     |       nan     |       nan     |
| Chia ngẫu nhiên (StratifiedKFold)     |  nan     |  nan     |                 nan     |              nan     |                nan     |   0.166 |              0.397 |          0.126 |            0.107 |         0.169 |         0.284 |
| Chia theo nhóm (StratifiedGroupKFold) |  nan     |  nan     |                 nan     |              nan     |                nan     |   0.170 |              0.411 |          0.126 |            0.108 |         0.171 |         0.296 |

## Kết quả trên test trước / sau khi sửa quy trình

`tables/so_sanh_truoc_sau.csv`

|                            |   MAPE (trước) |   MAPE (sau) |   MAPE (chênh lệch) |   R2_log (trước) |   R2_log (sau) |   R2_log (chênh lệch) |   pct_20 (trước) |   pct_20 (sau) |   pct_20 (chênh lệch) |   MAPE < 200 triệu (trước) |   MAPE < 200 triệu (sau) |   MAPE < 200 triệu (chênh lệch) |   MAPE 200-500 (trước) |   MAPE 200-500 (sau) |   MAPE 200-500 (chênh lệch) |   MAPE 500-1.000 (trước) |   MAPE 500-1.000 (sau) |   MAPE 500-1.000 (chênh lệch) |   MAPE 1-2 tỷ (trước) |   MAPE 1-2 tỷ (sau) |   MAPE 1-2 tỷ (chênh lệch) |   MAPE > 2 tỷ (trước) |   MAPE > 2 tỷ (sau) |   MAPE > 2 tỷ (chênh lệch) |
|:---------------------------|---------------:|-------------:|--------------------:|-----------------:|---------------:|----------------------:|-----------------:|---------------:|----------------------:|---------------------------:|-------------------------:|--------------------------------:|-----------------------:|---------------------:|----------------------------:|-------------------------:|-----------------------:|------------------------------:|----------------------:|--------------------:|---------------------------:|----------------------:|--------------------:|---------------------------:|
| Baseline (trung vị)        |          0.835 |        0.880 |               0.045 |           -0.003 |         -0.004 |                -0.001 |            0.256 |          0.256 |                -0.000 |                      3.498 |                    3.754 |                           0.256 |                  0.385 |                0.377 |                      -0.008 |                    0.307 |                  0.310 |                         0.003 |                 0.641 |               0.643 |                      0.002 |                 0.854 |               0.840 |                     -0.014 |
| Ridge - thư viện           |          0.185 |        0.185 |              -0.000 |            0.873 |          0.878 |                 0.005 |            0.750 |          0.752 |                 0.002 |                      0.430 |                    0.434 |                           0.004 |                  0.139 |                0.140 |                       0.001 |                    0.126 |                  0.123 |                        -0.003 |                 0.167 |               0.166 |                     -0.001 |                 0.343 |               0.308 |                     -0.035 |
| Random Forest - thư viện   |          0.155 |        0.151 |              -0.004 |            0.891 |          0.910 |                 0.019 |            0.801 |          0.794 |                -0.007 |                      0.347 |                    0.319 |                          -0.028 |                  0.117 |                0.120 |                       0.003 |                    0.109 |                  0.108 |                        -0.001 |                 0.157 |               0.160 |                      0.003 |                 0.270 |               0.210 |                     -0.060 |
| Random Forest - tự cài đặt |          0.157 |        0.157 |               0.000 |            0.887 |          0.904 |                 0.017 |            0.796 |          0.781 |                -0.015 |                      0.356 |                    0.329 |                          -0.027 |                  0.116 |                0.125 |                       0.009 |                    0.108 |                  0.112 |                         0.004 |                 0.158 |               0.171 |                      0.013 |                 0.304 |               0.234 |                     -0.070 |

*Trước: tiền xử lý học trên toàn bộ dữ liệu, lọc giá đặt cọc trên toàn bộ dữ liệu. Sau: chia tập trước, mọi tham số học từ train.*

## Kết quả phiên bản cũ (lưu trước khi sửa code)

`tables/results_before.csv`

| model                      |   MAPE |   MedAPE |     MAE |    RMSE |   R2_log |   pct_10 |   pct_20 |   MAPE < 200 triệu |   MAPE 200-500 |   MAPE 500-1.000 |   MAPE 1-2 tỷ |   MAPE > 2 tỷ |
|:---------------------------|-------:|---------:|--------:|--------:|---------:|---------:|---------:|-------------------:|---------------:|-----------------:|--------------:|--------------:|
| Baseline (trung vị)        |  0.835 |    0.400 | 336.968 | 723.755 |   -0.003 |    0.137 |    0.256 |              3.498 |          0.385 |            0.307 |         0.641 |         0.854 |
| Ridge - thư viện           |  0.185 |    0.107 | 119.564 | 411.409 |    0.873 |    0.475 |    0.750 |              0.430 |          0.139 |            0.126 |         0.167 |         0.343 |
| Random Forest - thư viện   |  0.155 |    0.090 | 102.137 | 372.406 |    0.891 |    0.539 |    0.801 |              0.347 |          0.117 |            0.109 |         0.157 |         0.270 |
| Random Forest - tự cài đặt |  0.157 |    0.090 | 106.029 | 388.394 |    0.887 |    0.546 |    0.796 |              0.356 |          0.116 |            0.108 |         0.158 |         0.304 |
