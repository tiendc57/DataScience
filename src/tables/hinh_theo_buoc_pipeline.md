# Hình minh họa cho từng bước của pipeline

Mỗi bước xử lý cần một hình trả lời câu hỏi **"vì sao làm vậy"** (vấn đề trong dữ liệu) hoặc **"làm xong thì sao"** (kết quả / kiểm chứng). Bản cho slide nằm ở `figures/slides/` (PNG + PDF, chữ ≥ 12pt, tối đa 2 panel); bản cho báo cáo ở `figures/`.

| # | Bước pipeline | Câu hỏi slide cần trả lời | Hình (figures/slides/) | Bảng (tables/) | Notebook |
|---|---|---|---|---|---|
| 1 | Bài toán, nguồn dữ liệu | Dữ liệu là gì, lấy từ đâu, cột nào người bán gõ tự do? | ảnh chụp trang Chợ Tốt (`image/`) | `tu_dien_du_lieu.csv` | crawl, preprocess |
| 2 | Khám phá dữ liệu thô: thiếu | Thiếu ở đâu, bao nhiêu, có ngẫu nhiên không? | `figures/v01_thieu_moi_dac_trung`, `figures/v03_thieu_theo_tinh_trang` (`v02` ma trận nếu cần) | | visualize_raw_data_2 |
| 3 | Khám phá dữ liệu thô: cơ cấu, nhãn hiếm | Đặc trưng lệch thế nào, bao nhiêu nhãn hiếm? | `figures/v04_co_cau_kieu_dang_so_cho_xuat_xu`, `figures/v05_duoi_dai_hang_dong` | | visualize_raw_data_2 |
| 4 | Làm sạch bằng quy tắc cứng | Giá / km nào là vô lý, ngưỡng lấy từ đâu? | `p10_gia_tri_bat_hop_ly` | | preprocess |
| 5 | Kết quả làm sạch | Còn lại bao nhiêu tin sau mỗi bước? | `p01_pheu_lam_sach` | `thong_ke_lam_sach.csv` | preprocess |
| 6 | Phân tích và cách xử lý giá trị thiếu | Mỗi cột thiếu bao nhiêu, xử lý thế nào, ở đâu? | `p02_thieu_va_cach_xu_ly` | `gia_tri_thieu.csv` | preprocess |
| 7 | EDA | Giá phụ thuộc vào gì? Quan hệ có tuyến tính không? | `s01_eda_gia_theo_tuoi`, `s02_eda_gia_theo_hang`, `s03_eda_gia_theo_km`, `s04_eda_tuong_quan`, `s05_eda_gia_theo_kieu_dang` | `thong_ke_mo_ta*.csv` | preprocess |
| 8 | Biến đổi biến mục tiêu | Vì sao học trên log(giá)? | `p03_gia_va_log_gia` | | preprocess |
| 9 | Mất cân bằng | Phân khúc nào hiếm, hệ quả gì? | `p04_phan_khuc_gia` | `phan_khuc_gia.csv` | preprocess |
| 10 | **Quy trình chống rò rỉ dữ liệu** | Bước nào làm trước / sau khi chia tập? | `s06_so_do_quy_trinh` | `so_do_quy_trinh.txt` | process |
| 11 | Chia train/test phân tầng | Test có đủ xe ở mọi phân khúc không? | `m01_chia_train_test` | `chia_train_test.csv` | process |
| 12 | Lọc nhãn sai (giá đặt cọc) | Nhãn sai trông thế nào, lọc bằng gì? | `s08_gia_dat_coc` | `vi_du_gia_dat_coc.csv` | process |
| 13 | Điền thiếu (fit trên train) | Điền có làm méo phân phối không? | `s10_truoc_sau_dien_thieu` | `thong_ke_xu_ly.csv` | process |
| 14 | Gộp nhãn hiếm | Gộp thế nào, ngưỡng chọn bằng gì? | `s11_gop_nhan` (kèm `v05` ở bước 3) | `so_sanh_gop_nhan.csv`, `thu_vi_tri.csv` | process |
| 15 | Đối chứng điền trong fold | Điền sẵn có làm CV lạc quan không? | (bảng là đủ) | `doi_chung_cv.csv` | process |
| 16 | Mã hóa đặc trưng | One-hot hay mã thứ tự? | `m16_ma_hoa` | `so_sanh_ma_hoa.csv` | model |
| 17 | Mô hình: lý thuyết | Một cây quyết định thế nào? | `m17_cay_minh_hoa` | | model |
| 18 | Mô hình: rừng, tự cài đặt | Vì sao nhiều cây tốt hơn, bản tự viết có đúng không? | `m18_cay_vs_rung`, `m05_rf_so_cay` (báo cáo thêm `figures/m11_tu_cai_dat_vs_thu_vien`) | `tham_so_tot_nhat.csv` | model |
| 19 | Đánh giá trên test | Mô hình nào tốt nhất, tốt đến đâu? | `s09_bang_ket_qua`, `m06_so_sanh_tong`, `m08_du_doan_vs_thuc_te` | `ket_qua_test.csv` | model |
| 20 | Đánh giá theo phân khúc | Mô hình kém ở đâu? | `m07_mape_phan_khuc` | `ket_qua_phan_khuc.csv` | model |
| 21 | Kiểm định thống kê | Chênh lệch có ý nghĩa không? | `m10_khoang_tin_cay` | `khoang_tin_cay.csv` | model |
| 22 | Xử lý mất cân bằng | Log giá, trọng số mẫu, over/undersampling giúp gì? | `m14_log_va_mat_can_bang` | `thi_nghiem_can_bang.csv` | model |
| 23 | Diễn giải | Đặc trưng nào quyết định giá, mô hình học được gì? | `m12_do_quan_trong`, `m13_duong_khau_hao` | `do_quan_trong.csv` | model |
| 24 | Phân tích lỗi, hạn chế | Sai nhiều nhất ở đâu, vì sao? | (bảng) | `xe_doan_sai_nhat.csv`, `tin_dang_lai.csv` | model |
| 25 | Trước / sau khi sửa quy trình | Sửa quy trình làm kết quả thay đổi thế nào? | `s07_truoc_sau` | `so_sanh_truoc_sau.csv` | model |

Các con số lẻ cho slide mở đầu / kết luận: `so_lieu_chot.json`. Dàn ý gọn 24 slide: `dan_y_slide.md`.
