
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
