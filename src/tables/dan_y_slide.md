# Dàn ý slide đề xuất

| # | Slide | Hình / bảng | Thông điệp chính |
|---|---|---|---|
| 1 | Bài toán và mục tiêu | `tables/so_lieu_chot.json` | Dự đoán giá rao ô tô cũ từ thông tin tin đăng; thước đo chính là MAPE. |
| 2 | Nguồn dữ liệu và cách thu thập | `tu_dien_du_lieu.csv` | 14.835 tin crawl từ Chợ Tốt; số km và giá là ô gõ tự do nên là nguồn lỗi chính. |
| 3 | Làm sạch dữ liệu | `p01_pheu_lam_sach` | Quy tắc cứng, xử lý từng dòng: bỏ tin trùng, giá vô lý, giá giả. |
| 4 | Giá trị thiếu và cách xử lý | `p02_thieu_va_cach_xu_ly` | Mỗi cột xử lý theo nguyên nhân thiếu; điền bằng thống kê của train. |
| 5 | Vấn đề giá trả trước / đặt cọc | `s08_gia_dat_coc + vi_du_gia_dat_coc.csv` | Xe đời mới giá rất thấp là nhãn sai; lọc bằng bảng trung vị học từ train. |
| 6 | EDA: giá theo tuổi xe | `s01_eda_gia_theo_tuoi` | Giá giảm đều theo tuổi xe trên thang log. |
| 7 | EDA: giá theo hãng | `s02_eda_gia_theo_hang` | Thương hiệu tạo chênh lệch giá gấp nhiều lần. |
| 8 | EDA: tương quan giữa các biến | `s04_eda_tuong_quan` | Tuổi xe tương quan mạnh nhất; tuổi và km trùng thông tin. |
| 9 | Vì sao dùng log giá | `p03_gia_va_log_gia` | Log đưa giá về gần đối xứng, sai số tính theo phần trăm. |
| 10 | Mất cân bằng theo phân khúc | `p04_phan_khuc_gia` | Xe trên 2 tỷ chỉ khoảng 3%: chia phân tầng, báo MAPE theo phân khúc. |
| 11 | Quy trình xử lý và chia tập | `s06_so_do_quy_trinh` | Chia tập trước; tham số chỉ đi một chiều từ train sang test. |
| 12 | Chia phân tầng train/test | `m01_chia_train_test` | Mỗi phân khúc giá có cùng tỉ lệ ở train và test. |
| 13 | Gộp nhãn hiếm: chọn bằng số liệu | `so_sanh_gop_nhan.csv` | Gộp theo cấp dòng → hãng → nhóm hãng, ngưỡng 30/10 chọn bằng CV. |
| 14 | Chọn cách mã hóa | `m16_ma_hoa` | One-hot tốt hơn mã số thứ tự. |
| 15 | Random Forest hoạt động thế nào | `m17_cay_minh_hoa` | Cây hỏi các câu có / không; rừng lấy trung bình nhiều cây. |
| 16 | Một cây so với cả rừng | `m18_cay_vs_rung, m05_rf_so_cay` | Lấy trung bình nhiều cây giảm sai số rõ rệt. |
| 17 | Kết quả trên tập test | `s09_bang_ket_qua, m06_so_sanh_tong` | Random Forest tốt nhất. |
| 18 | Sai số theo phân khúc giá | `m07_mape_phan_khuc` | Tốt ở phân khúc giữa, kém ở hai đầu thang giá. |
| 19 | Dự đoán so với giá thật | `m08_du_doan_vs_thuc_te` | Dự đoán bám sát đường chéo. |
| 20 | Chênh lệch có ý nghĩa thống kê không | `m10_khoang_tin_cay` | Bootstrap ghép cặp: RF tốt hơn Ridge có ý nghĩa. |
| 21 | Đặc trưng nào quyết định giá | `m12_do_quan_trong` | Tuổi xe quan trọng nhất theo cả hai cách đo. |
| 22 | Mô hình học được gì về khấu hao | `m13_duong_khau_hao` | Mỗi dòng xe khấu hao theo cách riêng. |
| 23 | Trước / sau khi sửa quy trình | `s07_truoc_sau, so_sanh_truoc_sau.csv` | Quy trình chặt hơn, đánh giá trung thực hơn. |
| 24 | Hạn chế và hướng phát triển | `tin_dang_lai.csv` | Tin đăng lại, nhãn sai còn sót, thiếu phiên bản xe. |

Slide 11 và 23 thể hiện phần việc sửa quy trình, nên để riêng, không gộp.
Hình cho slide ở `figures/slides/` (PNG + PDF); bảng ở `tables/` (CSV) và `tables/bang_bao_cao.md`.
