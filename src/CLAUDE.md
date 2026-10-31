# CLAUDE.md

Đề tài môn Khoa học dữ liệu (nhóm 2 người): **dự đoán giá bán ô tô** (triệu đồng) từ các đặc trưng của xe, dữ liệu crawl từ Chợ Tốt (`xe.chotot.com`). Sản phẩm cuối: slide, báo cáo, code demo. Yêu cầu của giảng viên (`Assignment.txt`): làm một mô hình machine learning **từ đầu đến cuối**, có metric đánh giá, kỹ thuật xử lý dữ liệu mất cân bằng; ví dụ gợi ý Random Forest, Decision Tree. Không cần mô hình quá lớn.

## Quy trình và file

Chạy theo thứ tự `preprocess_data` → `process_data` → `model` (crawl không chạy lại).

| Bước | File | Ghi chú |
|---|---|---|
| 1. Thu thập | `crawl_data.ipynb` | Sinh `raw_data_oto.csv` (14.835 dòng, 14 cột) |
| 2. Khám phá dữ liệu thô | `visualize_raw_data_2.ipynb` | Thiếu trên 13 đặc trưng theo nguồn (`figures/v01-v03`), cơ cấu kiểu dáng / số chỗ / xuất xứ (`v04`), đuôi dài hãng và dòng xe (`v05`). `visualize_raw_data.ipynb` là bản EDA cũ: hình `01-12` của nó đã bị xóa khỏi `figures/` (đã có hình mới thay), chạy lại sẽ sinh lại |
| 3. Tiền xử lý | `preprocess_data.ipynb` | **Chỉ quy tắc cứng, xử lý từng dòng**, không học tham số nào: ép kiểu, `N/A` → NaN, xóa trùng, loại giá / km vô lý theo ngưỡng nghiệp vụ, xe mới km = 0, `carorigin` → "Không rõ", `age`, `price_log`, EDA (mục 7). Xuất `preprocess_data.csv` (14.066 dòng, 14 cột), **cố ý còn NaN** ở `mileage_km` (xe cũ), `cartype`, `carseats`. Hình `p01-p10` |
| 4. Xử lý dữ liệu | `process_data.ipynb` | Chia train/test (80/20, phân tầng phân khúc giá, `random_state=42`), rồi **fit chỉ trên train**: lọc giá đặt cọc (bảng trung vị train, bỏ "Dòng khác"), `CarImputer` + `BrandModelGrouper` (`car_transformers.py`), đặc trưng Ridge, `group_key`; thí nghiệm gộp nhãn / vị trí; đối chứng điền trong fold. Xuất `train_data.csv` (11.153), `test_data.csv` (2.797), `../model/data_transformers.joblib`. Hình `m01`, `s06`, `s08`, `s10`, `s11` |
| 5. Mô hình | `model.ipynb` | Đọc `train_data.csv` / `test_data.csv`; chỉ còn one-hot / chuẩn hóa (fit trên train). Trọng tâm Random Forest: bản thư viện + bản tự cài đặt NumPy. Ridge chỉ dùng thư viện để so sánh. Mục 3 one-hot vs mã thứ tự; 8.2 permutation importance; 9 log giá + cân bằng; 10 CV chia theo nhóm; 11 xuất mô hình; 12.5 so sánh trước / sau khi sửa quy trình; **13 hình và bảng cho slide**. Hình `m05-m18` |
| 6. Mô hình đã lưu | `../model/` (cạnh `src/`) | `.joblib`, `.npz`, `metadata.json` (keep_brand / keep_model / trung vị km học từ train), `price_model.py` (nạp và dự đoán); `.pkl` tạo lại bằng `python export_pkl.py` sau mỗi lần chạy `model.ipynb` |
| Hình / bảng cho slide | `figures/slides/`, `tables/` | Hình slide PNG + PDF, chữ ≥ 12pt. Bảng CSV (utf-8-sig) + `tables/bang_bao_cao.md` (ghép từ 3 notebook qua `report_utils.py`), `so_lieu_chot.json`, `dan_y_slide.md`, `hinh_theo_buoc_pipeline.md` (bước pipeline → hình) |

`car_transformers.py`: `CarImputer`, `BrandModelGrouper` (kiểm tra bằng `python test_transformers.py`). `report_utils.py`: `SLIDE_RC`, `save_slide`, `save_table`, `update_numbers`, `vn`.

`clean_data_oto.csv` là đầu ra của phiên bản cũ (không còn notebook nào dùng). Kết quả phiên bản cũ lưu ở `tables/results_before.csv`, `tables/config_before.txt`. Hướng dẫn sửa: `../feedback/HUONG_DAN_SUA_CODE (2).md`.

`OLD/` là bản cũ, không dùng. `prompt.txt` ghi lại các yêu cầu đã giao.

## Quy ước cần giữ

- **Làm việc trong `src/`**: các notebook đọc file bằng đường dẫn tương đối. Chạy với thư mục làm việc là `src`.
- **Ngôn ngữ**: markdown và giải thích trong notebook bằng tiếng Việt. Mỗi quyết định xử lý dữ liệu phải có lý do ghi rõ (đây là yêu cầu của báo cáo).
- **Biến mục tiêu**: `price_log` = ln(giá triệu đồng). Huấn luyện trên log, `exp()` khi dự đoán, **mọi metric tính trên giá thật**. Thước đo chính là MAPE; luôn báo cáo MAPE theo phân khúc giá (`< 200 triệu`, `200-500`, `500-1.000`, `1-2 tỷ`, `> 2 tỷ`).
- **Phân loại bước xử lý**: bước xử lý từng dòng / ngưỡng cứng / hằng số / công thức → `preprocess_data`; bước học thống kê từ dữ liệu (median, mode, tần suất, quy tắc dùng giá) → `process_data`, **fit trên train, transform mọi thứ**; mã hóa, chuẩn hóa, cân bằng → `model`. Không bao giờ `fit` / `fit_transform` trên test.
- **Không rò rỉ dữ liệu**: không dùng `price_tr`, `price_log` làm đặc trưng; tham số chỉ chọn bằng CV hoặc OOB trên train, tập test chỉ đánh giá một lần.
- **Dữ liệu xuất giữ dữ liệu thật**, không chèn mẫu nhân bản hay tổng hợp. Cân bằng dữ liệu (nếu dùng) chỉ làm trong phần train của từng fold.
- **Giá trả trước / đặt cọc:** loại tin có giá < 30% trung vị của xe cùng hãng-dòng-năm (nhóm ≥ 3 xe ở train, bỏ "Dòng khác"), bảng trung vị học từ train, áp lên cả hai tập (sửa lỗi nhãn): 99 tin train, 17 tin test.
- **Số km của xe mới = 0** (thiếu có cấu trúc), không điền trung vị. `carorigin` thiếu ~41% nên giữ nhãn "Không rõ".
- `model.ipynb` **tính lại** `km_per_year`, `age_sq`, `log_km`, `log_km_per_year` sau khi đọc CSV, đúng công thức `price_model.py`: rừng tự cài đặt rời rạc hóa theo mốc bin nên lệch 1e-16 do CSV cũng làm bài kiểm tra nạp lại mô hình (rtol 1e-9) fail.
- Mô hình tự cài đặt phải được **kiểm chứng** với bản thư viện (cùng dữ liệu, cùng tham số) trước khi dùng.
- Biểu đồ: một màu xanh chủ đạo (`#2a78d6`), cam (`#eb6834`) để nhấn, không dùng trục đôi. Hình slide: ≤ 2 panel, tiêu đề là câu kết luận, số kiểu Việt Nam.

## Chạy

```bash
cd src
python -m jupyter nbconvert --to notebook --execute <tên>.ipynb --output <tên>.ipynb --ExecutePreprocessor.timeout=-1
```

- `model.ipynb` mất khoảng 12 phút; `process_data.ipynb` khoảng 3 phút (thí nghiệm gộp nhãn + đối chứng CV); `preprocess_data.ipynb` khoảng 1 phút.
- Notebook được chạy bằng `nbconvert` chỉ ghi output vào file khi chạy xong toàn bộ; lỗi ở bất kỳ cell nào thì không lưu gì.
- Trên Windows cần chạy Python với UTF-8 (`python -X utf8`) khi in tiếng Việt ra console.
- Môi trường tham chiếu: pandas 3.0, scikit-learn 1.9, imbalanced-learn 0.14, scipy, tabulate. File `.pkl` trong `model/` cần cùng phiên bản scikit-learn khi nạp và cần `model/price_model.py` trong `sys.path`.

## Kết quả hiện tại (tập test 2.797 tin, `random_state=42`)

| Mô hình | MAPE | R² (log) | Trước khi sửa quy trình |
|---|---|---|---|
| Baseline (trung vị) | 0,880 | -0,004 | 0,835 |
| Ridge (thư viện, so sánh) | 0,185 | 0,878 | 0,185 |
| Random Forest (thư viện) | 0,151 | 0,910 | 0,155 |
| Random Forest (tự cài đặt) | 0,157 | 0,904 | 0,157 |

RF tốt hơn Ridge 3,3 điểm % (bootstrap ghép cặp, KTC 95%: 2,4-4,4); RF tự cài đặt kém thư viện 0,6 điểm % (KTC 0,34-0,86, có ý nghĩa nhưng nhỏ). Đối chứng điền sẵn vs điền trong fold: chênh 0,04 điểm % MAPE (CV). Thí nghiệm CV trên train (RF): log giá 0,166 so với giá gốc 0,200; trọng số mẫu / oversampling giữ MAPE tổng (0,167-0,169) nhưng giảm > 2 tỷ từ 0,284 xuống 0,25; undersampling 0,172. Mô hình cuối không cân bằng. RF theo phân khúc: < 200 triệu 0,32; > 2 tỷ 0,21. Khoảng 14% dòng test có bản sao trong train; trên phần còn lại MAPE RF là 0,159. Giá là **giá rao bán**, không phải giá giao dịch; dữ liệu thiếu phiên bản/trang bị xe.
