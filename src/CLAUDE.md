# CLAUDE.md

Đề tài môn Khoa học dữ liệu (nhóm 2 người): **dự đoán giá bán ô tô** (triệu đồng) từ các đặc trưng của xe, dữ liệu crawl từ Chợ Tốt (`xe.chotot.com`). Sản phẩm cuối: slide, báo cáo, code demo. Yêu cầu của giảng viên (`Assignment.txt`): làm một mô hình machine learning **từ đầu đến cuối**, có metric đánh giá, kỹ thuật xử lý dữ liệu mất cân bằng; ví dụ gợi ý Random Forest, Decision Tree. Không cần mô hình quá lớn.

## Quy trình và file

| Bước | File | Ghi chú |
|---|---|---|
| 1. Thu thập | `crawl_data.ipynb` | Sinh `raw_data_oto.csv` (~14.8k dòng, 14 cột) |
| 2. Khám phá | `visualize_raw_data.ipynb`, `figures/` | Biểu đồ cho báo cáo (PNG 200 dpi) |
| 3. Tiền xử lý | `preprocess_data.ipynb` | `raw_data_oto.csv` → `clean_data_oto.csv` (13.937 dòng, 17 cột; nhãn hiếm gộp theo cấp dòng → hãng → nhóm hãng cao cấp/phổ thông, có cột `mileage_missing`; `province` chỉ dùng trong notebook, không xuất vì không giúp dự đoán); `clean_data.ipynb` là bản cũ theo hướng phân loại `fuel` |
| 4. Mô hình | `model.ipynb` | Trọng tâm là Random Forest: bản thư viện + bản tự cài đặt NumPy (cây đơn chỉ là thành phần kiểm chứng). Ridge chỉ dùng thư viện để so sánh (không tự cài đặt). RF dùng one-hot + số gốc (mục 3 kiểm chứng one-hot tốt hơn mã số thứ tự bằng CV); Ridge dùng `age²`, `log(km)` + chuẩn hóa. Có permutation importance (mục 8.2), thí nghiệm log giá + cân bằng (mục 9), CV chia theo nhóm cho tin đăng lại (mục 10). Biểu đồ lưu ở `figures/m01`, `m05-m15` |
| 5. Mô hình đã lưu | `../model/` (cạnh `src/`) | `.joblib`, `.npz`, `metadata.json`, `price_model.py` (nạp và dự đoán); `.pkl` tạo lại bằng `python export_pkl.py` sau mỗi lần chạy `model.ipynb` |

`feeback/DANH_GIA_CODE.md` (ngoài `src/`) là bài đánh giá code ngày 27/10/2026; các mục 3.1-3.6 đã được sửa.

`OLD/` là bản cũ, không dùng. `prompt.txt` ghi lại các yêu cầu đã giao.

## Quy ước cần giữ

- **Làm việc trong `src/`**: các notebook đọc file bằng đường dẫn tương đối (`raw_data_oto.csv`, `clean_data_oto.csv`). Chạy với thư mục làm việc là `src`.
- **Ngôn ngữ**: markdown và giải thích trong notebook bằng tiếng Việt. Mỗi quyết định xử lý dữ liệu phải có lý do ghi rõ (đây là yêu cầu của báo cáo).
- **Biến mục tiêu**: `price_log` = ln(giá triệu đồng). Huấn luyện trên log, `exp()` khi dự đoán, **mọi metric tính trên giá thật**. Thước đo chính là MAPE; luôn báo cáo MAPE theo phân khúc giá (`< 200 triệu`, `200-500`, `500-1.000`, `1-2 tỷ`, `> 2 tỷ`).
- **Không rò rỉ dữ liệu**: không dùng `price_tr`, `price_log` làm đặc trưng; chia train/test (80/20, phân tầng theo phân khúc giá, `random_state=42`) trước khi tinh chỉnh; tham số chỉ chọn bằng CV hoặc OOB trên train, tập test chỉ đánh giá một lần.
- **`clean_data_oto.csv` giữ dữ liệu thật**, không chèn mẫu nhân bản hay tổng hợp. Cân bằng dữ liệu (nếu dùng) chỉ làm trên tập train sau khi chia.
- **Giá trả trước / đặt cọc:** loại tin có giá < 30% trung vị của xe cùng hãng-dòng-năm (nhóm ≥ 3 xe), 134 tin. Đây là sửa lỗi nhãn, không phải tạo đặc trưng.
- **Mọi quyết định** (log giá, kỹ thuật cân bằng, tham số) chỉ dựa trên CV/OOB trên train; `preprocess_data.ipynb` không còn đánh giá gì trên tập test.
- **Số km của xe mới = 0** (thiếu có cấu trúc), không điền trung vị. `carorigin` thiếu ~41% nên giữ nhãn "Không rõ".
- Mô hình tự cài đặt phải được **kiểm chứng** với bản thư viện (cùng dữ liệu, cùng tham số) trước khi dùng.
- Biểu đồ: một màu xanh chủ đạo (`#2a78d6`), cam (`#eb6834`) để nhấn, không dùng trục đôi.

## Chạy

```bash
cd src
python -m jupyter nbconvert --to notebook --execute <tên>.ipynb --output <tên>.ipynb --ExecutePreprocessor.timeout=-1
```

- `model.ipynb` mất khoảng 12 phút (rừng cây tự cài đặt chạy Python thuần khoảng 5 phút cả tinh chỉnh; thí nghiệm CV mục 7 khoảng 2,5 phút). `preprocess_data.ipynb` khoảng 2 phút (mục 7.4 có CV kiểm chứng cách gộp nhãn). Notebook khác chỉ vài chục giây.
- Notebook được chạy bằng `nbconvert` chỉ ghi output vào file khi chạy xong toàn bộ; lỗi ở bất kỳ cell nào thì không lưu gì.
- Trên Windows cần chạy Python với UTF-8 (`python -X utf8`) khi in tiếng Việt ra console.
- Môi trường tham chiếu: pandas 3.0, scikit-learn 1.9, imbalanced-learn 0.14, scipy. File `.pkl` trong `model/` cần cùng phiên bản scikit-learn khi nạp và cần `model/price_model.py` trong `sys.path`.

## Kết quả hiện tại (tập test, `random_state=42`)

| Mô hình | MAPE | R² (log) |
|---|---|---|
| Baseline (trung vị) | 0,835 | -0,003 |
| Ridge (thư viện, so sánh) | 0,185 | 0,873 |
| Random Forest (thư viện) | 0,155 | 0,891 |
| Random Forest (tự cài đặt) | 0,157 | 0,887 |

RF tốt hơn Ridge 3,0 điểm % (bootstrap ghép cặp, KTC 95%: 2,1-4,0); RF tự cài đặt và thư viện không khác nhau có ý nghĩa. Thí nghiệm CV trên train (RF): log giá MAPE 0,162 so với giá gốc 0,196; trọng số mẫu / oversampling giữ MAPE tổng (0,161-0,163) nhưng giảm > 2 tỷ từ 0,274 xuống 0,24; undersampling 0,168. Mô hình cuối không cân bằng (oversampling là lựa chọn nếu ưu tiên xe sang). RF theo phân khúc: < 200 triệu 0,35; > 2 tỷ 0,27. Khoảng 14% dòng test có bản sao (tin đăng lại) trong train; trên phần còn lại MAPE RF là 0,162. Giá là **giá rao bán**, không phải giá giao dịch; dữ liệu thiếu phiên bản/trang bị xe.
