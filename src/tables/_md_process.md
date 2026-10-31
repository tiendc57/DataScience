
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
