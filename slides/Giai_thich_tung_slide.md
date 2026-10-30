# Giải thích chi tiết từng slide

Tài liệu đi kèm file `Bao_cao_Du_doan_gia_o_to.pptx` (35 slide), dùng để hai thành viên nắm chắc nội dung trước khi thuyết trình và trả lời câu hỏi.

**Cách dùng:** mỗi slide có bốn mục.

| Mục | Dùng để |
|---|---|
| **Mục đích** | biết slide này trả lời câu hỏi gì trong mạch bài |
| **Trên slide có gì** | đọc đúng từng hình, bảng, con số |
| **Giải thích chi tiết** | hiểu bản chất, có ví dụ |
| **Câu nói gợi ý** | câu chốt khi trình bày (khoảng 30-60 giây mỗi slide) |

Một số slide có thêm **Câu hỏi có thể gặp** kèm gợi ý trả lời. Cuối tài liệu có **bảng thuật ngữ** và **danh sách câu hỏi tổng hợp**.

Mọi con số trong tài liệu lấy từ lần chạy notebook với `random_state = 42`; chạy lại sẽ ra đúng các số này.

---

## Mạch bài trong một câu

> Thu thập 14.835 tin rao xe từ Chợ Tốt → làm sạch còn 13.937 tin → xây Random Forest (bản thư viện và bản tự viết) → so với Ridge và mốc đoán bừa → Random Forest sai trung bình 15,5%, tốt hơn Ridge 3 điểm % một cách có ý nghĩa thống kê, bản tự viết ngang bản thư viện.

---

# PHẦN 1. GIỚI THIỆU (slide 1-4)

## Slide 1 – Bìa

**Mục đích:** giới thiệu đề tài, nhóm, giảng viên.

**Trên slide có gì:** tên đề tài "Dự đoán giá ô tô cũ trên Chợ Tốt bằng Random Forest", tên sinh viên, giảng viên hướng dẫn.

**Giải thích chi tiết:** cần nói ngay từ đầu hai điều để hội đồng không hiểu nhầm:
1. Mô hình được **phân tích kỹ** là **Random Forest**, đúng yêu cầu "phân tích kỹ một mô hình" của thầy.
2. Random Forest có **hai bản**: bản dùng thư viện `scikit-learn` (làm chuẩn) và bản **tự viết bằng NumPy** (để chứng minh hiểu thuật toán). **Ridge** chỉ là mô hình phụ để so sánh, không phải trọng tâm.

**Câu nói gợi ý:** "Nhóm em xây dựng mô hình dự đoán giá rao bán ô tô trên Chợ Tốt. Mô hình chính là Random Forest, được làm hai bản, một bản dùng thư viện và một bản tự cài đặt, rồi kiểm chứng hai bản với nhau. Ridge Regression chỉ dùng làm mốc so sánh."

---

## Slide 2 – Nội dung trình bày

**Mục đích:** cho người nghe biết bài có mấy phần.

**Trên slide có gì:** 5 phần đánh số 01-05.

**Giải thích chi tiết:** thứ tự 5 phần chính là quy trình chuẩn của một dự án khoa học dữ liệu: có bài toán → có dữ liệu → làm sạch dữ liệu → xây mô hình → đánh giá. Mỗi phần tương ứng một notebook trong thư mục `src/`.

**Câu nói gợi ý:** "Bài trình bày đi theo đúng quy trình một dự án học máy từ đầu đến cuối, gồm năm phần."

---

## Slide 3 – Bài toán

**Mục đích:** nói rõ mô hình nhận gì và trả ra gì.

**Trên slide có gì:**
- Khung trái **Đầu vào**: hãng, dòng xe, năm sản xuất, số km, hộp số, nhiên liệu, kiểu dáng, số chỗ, xuất xứ, tình trạng.
- Khung xanh **Đầu ra**: giá rao bán (triệu đồng).
- Khung vàng **Yêu cầu của đề tài**: làm từ đầu đến cuối có thước đo, phân tích kỹ Random Forest, có xử lý mất cân bằng.

**Giải thích chi tiết:**
- **Vì sao là bài toán hồi quy?** Học máy có giám sát chia làm hai loại chính:
  - *Phân loại:* đầu ra là nhãn rời rạc (ví dụ "xe sang" / "xe phổ thông").
  - *Hồi quy:* đầu ra là **số liên tục** (ví dụ 487,5 triệu).
  
  Giá xe là số liên tục nên đây là **hồi quy**.
- **Vì sao chỉ dùng thông tin trong tin đăng?** Mô hình phải dùng được trong thực tế: người dùng chỉ biết những gì ghi trên tin đăng. Nếu dùng thông tin không có lúc dự đoán thì mô hình vô dụng.
- **"Giá rao bán"** khác "giá bán thật": đây là giá người bán đăng, chưa trừ phần thương lượng. Đây là một hạn chế cần nói rõ.

**Câu nói gợi ý:** "Đầu vào là những thông tin ai cũng thấy trong một tin đăng, đầu ra là giá rao bán tính bằng triệu đồng. Vì đầu ra là một con số liên tục nên đây là bài toán hồi quy có giám sát."

---

## Slide 4 – Quy trình thực hiện

**Mục đích:** cho thấy toàn cảnh 5 bước và hai nguyên tắc xuyên suốt.

**Trên slide có gì:** 5 ô nối bằng mũi tên: Thu thập (14.835 tin) → Tiền xử lý (13.937 tin) → Mô hình → Đánh giá → Triển khai. Bên dưới là hai nguyên tắc.

**Giải thích chi tiết:**

**Nguyên tắc 1 – Chống rò rỉ dữ liệu (data leakage).**
- Rò rỉ dữ liệu là khi mô hình, trong lúc học hoặc lúc chọn tham số, vô tình "nhìn thấy" thông tin của tập dùng để chấm điểm. Khi đó điểm đánh giá đẹp giả tạo.
- *Ví dụ dễ hiểu:* tập test giống **đề thi cuối kỳ**. Nếu ôn bằng chính đề thi, điểm cao nhưng không phản ánh năng lực thật.
- Cách làm trong đề tài: mọi lựa chọn (mã hóa thế nào, tham số nào, có dùng log không, cân bằng dữ liệu cách nào) đều quyết định bằng **CV hoặc OOB trên tập train**. Tập test chỉ mở ra **một lần** ở cuối.

**Nguyên tắc 2 – Tái lập (reproducibility).**
- Nhiều bước có yếu tố ngẫu nhiên: chia dữ liệu, chia fold, bootstrap của rừng, chọn đặc trưng ngẫu nhiên.
- Cố định "hạt giống" `random_state = 42` thì máy tính sinh ra đúng cùng một chuỗi số ngẫu nhiên mỗi lần chạy. Kết quả: chạy lại notebook ra **đúng cùng mô hình, cùng con số**. Chỉ thời gian huấn luyện thay đổi theo tải của máy.

**Câu nói gợi ý:** "Có hai nguyên tắc xuyên suốt. Một là tập test chỉ dùng đúng một lần để báo cáo, mọi lựa chọn đều làm trên tập train. Hai là mọi bước ngẫu nhiên đều cố định random_state bằng 42 nên kết quả tái lập được hoàn toàn."

**Câu hỏi có thể gặp:**
- *"Chạy lại có ra kết quả khác không?"* → "Không. Mọi bước ngẫu nhiên đều cố định random_state = 42, nên chạy lại ra đúng cùng số liệu; chỉ thời gian huấn luyện thay đổi."

---

# PHẦN 2. THU THẬP VÀ KHÁM PHÁ DỮ LIỆU (slide 5-9)

## Slide 5 – Crawl 14.835 tin từ Chợ Tốt

**Mục đích:** giải thích dữ liệu đến từ đâu và được lấy như thế nào.

**Trên slide có gì:**
- Dòng cam: 750 trang · 14.835 tin · 12 thuộc tính mỗi tin · thu thập ngày 25/10/2026.
- **Ảnh 1:** trang danh sách tin của Chợ Tốt (`mua-ban-oto?page=1`).
- **Ảnh 2:** trang chi tiết một tin (Mitsubishi Triton 2022) kèm công cụ DevTools của trình duyệt.
  - **Khung cam:** dòng HTML `<span itemprop="mileage_v2">44.000</span>`.
  - **Khung xanh:** mục "Số đời chủ", "Còn hạn đăng kiểm".

**Giải thích chi tiết:**

**Crawl (web scraping) là gì?** Là viết chương trình tự động mở trang web và chép lại thông tin, thay vì chép tay. Quy trình có hai tầng:
1. **Tầng danh sách (ảnh 1):** mở lần lượt 750 trang danh sách tin mới nhất. Mỗi trang có khoảng 20 tin. Chương trình lấy **đường dẫn (link)** của từng tin. Các tin "ưu tiên" lặp lại ở đầu mọi trang được bỏ trùng, nên mỗi link chỉ lấy một lần.
2. **Tầng chi tiết (ảnh 2):** mở từng link, đọc các thuộc tính của xe.

**Đọc thuộc tính bằng `itemprop` như thế nào?** Trang web được viết bằng HTML. Chợ Tốt gắn cho mỗi ô thông tin một "nhãn" ẩn tên là `itemprop`. Ví dụ ô số km được gắn `itemprop="mileage_v2"`, bên trong là giá trị `44.000` (khung cam). Chương trình chỉ cần tìm thẻ có nhãn đó là lấy được đúng giá trị, không phụ thuộc vị trí trên trang. Riêng giá đọc từ thẻ `name="price"`.

**Thu thập có trách nhiệm:**
- Nghỉ 0,5 giây giữa các tin và 1 giây giữa các trang để không làm quá tải máy chủ.
- Khi máy chủ trả mã lỗi 403 / 429 (từ chối / quá nhiều yêu cầu) thì chờ lâu hơn rồi thử lại.
- Chỉ lấy thông tin công khai, không đăng nhập, **không lấy thông tin liên hệ** người bán. Trong ảnh, tên người bán và số điện thoại đã được làm mờ.
- Có cơ chế **chạy tiếp**: nếu bị ngắt giữa chừng, chạy lại sẽ bỏ qua những link đã lấy.

**Khung xanh nói gì?** Trang tin còn có "Số đời chủ", "Còn hạn đăng kiểm", "Có phụ kiện đi kèm", nhưng code chưa lấy những mục này. Đây là các thông tin ảnh hưởng đến giá, nên được nêu ở phần **hạn chế** và **hướng phát triển** (slide 35).

**Câu nói gợi ý:** "Chương trình duyệt 750 trang danh sách để lấy link từng tin, sau đó vào từng tin đọc các thẻ HTML có thuộc tính itemprop, như khung cam là thẻ chứa số km. Tổng cộng 14.835 tin, thu thập ngày 25/10/2026. Nhóm có nghỉ giữa các yêu cầu và không lấy thông tin liên hệ của người bán."

**Câu hỏi có thể gặp:**
- *"Có vi phạm điều khoản của trang không?"* → "Nhóm chỉ lấy thông tin công khai, không đăng nhập, không lấy thông tin cá nhân, có nghỉ giữa các yêu cầu, và dữ liệu chỉ dùng cho học tập."
- *"Vì sao không lấy thêm số đời chủ?"* → "Đây là thiếu sót của bước thu thập, nhóm đã nêu ở hạn chế và hướng phát triển."

---

## Slide 6 – Từ điển dữ liệu

**Mục đích:** giới thiệu từng cột và chỉ ra cột nào dễ có lỗi.

**Trên slide có gì:** bảng 11 dòng với 4 cột: tên cột, ý nghĩa, **người bán nhập thế nào**, cách xử lý. Hai ô chữ cam "gõ tự do" ở dòng số km và giá.

**Giải thích chi tiết:**
- Cột quan trọng nhất của bảng là **"Người bán nhập"**, vì nó cho biết lỗi có thể xảy ra ở đâu:
  - **Chọn từ danh sách** (hãng, dòng xe, hộp số, nhiên liệu…): người bán chỉ bấm chọn trong menu, nên giá trị luôn viết thống nhất, không sai chính tả. Các cột này sạch.
  - **Gõ tự do** (số km, giá): người bán tự gõ số, nên có đủ loại lỗi: gõ thiếu hoặc thừa số 0, gõ km theo đơn vị nghìn, ghi tiền trả trước thay vì giá xe, gõ giá giả 123.456.789.
- Vì vậy phần tiền xử lý tập trung kiểm tra **hai cột gõ tự do**.
- Một số xử lý đáng chú ý:
  - `mfdate` (năm sản xuất) đổi thành **tuổi xe = 2026 − năm**, vì tuổi có ý nghĩa trực tiếp hơn với giá.
  - `veh_warranty_policy` (bảo hành) chỉ có một giá trị duy nhất ở mọi tin, nên không giúp phân biệt xe nào, bỏ cột.
  - `url` chứa tên tỉnh, nên trích ra cột tỉnh/thành rồi bỏ url.

**Câu nói gợi ý:** "Điểm quan trọng của bảng này là cột người bán nhập. Các cột chọn từ danh sách thì sạch, còn số km và giá là hai ô gõ tự do, cũng là hai nguồn lỗi chính mà phần tiền xử lý phải kiểm tra."

---

## Slide 7 – Cách dữ liệu được tạo ra quyết định cách xử lý

**Mục đích:** cho thấy mỗi quyết định làm sạch đều có lý do, xuất phát từ cách dữ liệu được sinh ra.

**Trên slide có gì:** bảng 7 dòng: Cơ chế → Hệ quả → Cách xử lý.

**Giải thích chi tiết từng dòng:**

| Cơ chế | Giải thích | Xử lý |
|---|---|---|
| Không tìm thấy thẻ → ghi "N/A" | Code crawl ghi chữ "N/A" khi trang không có ô đó, tức người bán bỏ trống. Đây là **thiếu thật**. | Đổi về giá trị thiếu (NaN). Đọc file với `keep_default_na=False` để tự kiểm soát việc đổi này. |
| "Đang cập nhật" ở xuất xứ | Trang tự hiện chữ này khi người bán không chọn xuất xứ. Cũng là thiếu thật. | Đổi về NaN. |
| "Khác", "Dòng khác" | Menu có sẵn mục "Khác", người bán **chủ động chọn**. Đây là **thông tin thật**, không phải thiếu. | Giữ làm nhãn. Riêng "Khác" ở số chỗ không đổi ra số được nên coi là thiếu. |
| Số km, giá là ô gõ tự do | Nguồn lỗi chính. | Luật kiểm tra ở phần 3 (slide 11-12). |
| Trang xe "Mới" không có ô km | Mọi xe mới đều thiếu km, nhưng giá trị đúng là 0. | Điền 0 km. |
| Bảo hành giống nhau ở mọi tin | Nhiều khả năng là giá trị mặc định của trang. | Bỏ cột. |
| Một lần crawl, 750 trang mới nhất | Dữ liệu là "ảnh chụp" thị trường tại một thời điểm; giá là giá rao. | Tuổi xe tính theo năm 2026; nêu ở hạn chế. |

**Ý quan trọng:** nếu để nguyên chữ "Đang cập nhật", mô hình sẽ coi nó là một **xuất xứ thật** (giống "Nhật Bản", "Thái Lan"). Đó là lý do phải đổi về thiếu.

**Câu nói gợi ý:** "Hiểu cách code crawl sinh ra dữ liệu giúp phân biệt đâu là thiếu thật, đâu là lựa chọn thật. Ví dụ N/A là người bán bỏ trống nên là thiếu, còn 'Khác' là người bán chủ động chọn nên phải giữ."

---

## Slide 8 – Dữ liệu thô: thiếu nhiều ở các cột không bắt buộc

**Mục đích:** cho thấy tình trạng dữ liệu thô trước khi làm sạch.

**Trên slide có gì:**
- **Hình trái:** biểu đồ thanh ngang, mỗi thanh là tỉ lệ % giá trị thiếu của một cột: xuất xứ 40,5%, kiểu dáng 32,9%, số chỗ 24,9%, số km 12,2%, các cột khác gần 0%.
- **Hình phải:** cơ cấu dữ liệu theo tình trạng, nhiên liệu, hộp số.
- **Ba thẻ:** 41% thiếu xuất xứ; 100% xe mới thiếu km; 67% tin ở TP.HCM và Hà Nội.

**Giải thích chi tiết:**
- **Vì sao thiếu nhiều ở xuất xứ, kiểu dáng, số chỗ?** Đây là các ô **không bắt buộc** khi đăng tin, người bán thường bỏ qua.
- **"100% xe mới thiếu km"** không phải lỗi ngẫu nhiên: trang tin xe mới không có ô số km. Loại thiếu có nguyên nhân rõ ràng như vậy gọi là **thiếu có cấu trúc**. Hiểu được điều này quyết định cách điền (slide 13).
- **Cơ cấu (hình phải):** phần lớn là xe đã sử dụng, số tự động, chạy xăng. Xe hybrid và xe bán tự động rất ít. Đây cũng là một dạng mất cân bằng ở đặc trưng.
- **67% ở TP.HCM và Hà Nội:** dữ liệu tập trung ở hai thành phố lớn.

*Ghi chú về con số:* hình trái tính trên dữ liệu thô (40,5%); slide 13 tính sau khi bỏ tin trùng nên ra 41,5%. Hai con số khác nhau một chút vì mẫu số khác nhau.

**Câu nói gợi ý:** "Dữ liệu thô thiếu nhiều ở các cột không bắt buộc như xuất xứ, kiểu dáng, số chỗ. Riêng số km thiếu ở toàn bộ xe mới, vì trang xe mới không có ô số km. Đây là thiếu có cấu trúc và sẽ được xử lý khác."

---

## Slide 9 – Tuổi xe và thương hiệu quyết định phần lớn giá

**Mục đích:** cho thấy các yếu tố nào liên quan mạnh đến giá, trước khi xây mô hình.

**Trên slide có gì:**
- **Hình trái:** đường giá trung vị theo năm sản xuất. Xe đời 2001 khoảng 73 triệu, xe đời 2026 khoảng 624 triệu.
- **Hình phải:** biểu đồ hộp giá theo 12 hãng có nhiều tin nhất.

**Giải thích chi tiết:**
- **Giá trung vị** là giá ở giữa khi xếp các xe từ rẻ đến đắt. Dùng trung vị thay trung bình vì giá có vài xe rất đắt kéo trung bình lên.
- **Hình trái** cho thấy hai điều:
  1. Xe càng mới giá càng cao (rõ ràng).
  2. Đường **cong**, không thẳng: giá tăng nhanh ở các năm gần đây. Nghĩa là xe **mất giá nhanh trong những năm đầu**. Mô hình tuyến tính đơn thuần khó học được dạng cong này.
- **Cách đọc biểu đồ hộp (hình phải):**
  - Mỗi hộp chứa **50% số xe ở giữa** của một hãng (từ 25% đến 75%).
  - Vạch giữa hộp là **trung vị**.
  - Râu hai bên là phạm vi phần lớn các xe còn lại.
  - Hộp **càng cao** thì hãng đó **càng đắt**; hộp **càng rộng** thì giá **càng đa dạng**.
- BMW, Mercedes: hộp nằm cao và rộng (đắt, nhiều phân khúc). Suzuki, Chevrolet: hộp thấp và hẹp (rẻ, tập trung).

**Câu nói gợi ý:** "Hai yếu tố liên quan rõ nhất đến giá là tuổi xe và thương hiệu. Xe mất giá nhanh trong những năm đầu nên quan hệ là đường cong. Xe sang Đức đắt và có giá đa dạng hơn hẳn xe phổ thông."

---

# PHẦN 3. TIỀN XỬ LÝ DỮ LIỆU (slide 10-15)

## Slide 10 – Chuẩn hóa giá trị giả, trích vị trí, loại tin trùng

**Mục đích:** các bước làm sạch đầu tiên, đưa dữ liệu về đúng kiểu.

**Trên slide có gì:** ba thẻ: Giá trị giả, Vị trí và cột thừa, Tin trùng.

**Giải thích chi tiết:**

**Thẻ 1 – Giá trị giả:**
- "N/A", "Đang cập nhật" → giá trị thiếu thật (lý do ở slide 7).
- Số được lưu dạng chuỗi có dấu chấm ngăn cách hàng nghìn: "109.366" → số 109366; "1.095.000.000" → 1095000000. Nếu để máy tự đọc, "79.000" sẽ bị hiểu nhầm là 79,0.
- Năm "trước năm 1980" (12 tin) → gán 1979 để vẫn dùng được như số.

**Thẻ 2 – Vị trí và cột thừa:**
- URL có dạng `mua-ban-oto-<quận>-<tỉnh>/<mã tin>.htm`, nên trích được tỉnh cho 100% số tin, 63 tỉnh/thành.
- **Không lấy quận/huyện** vì có 453 quận/huyện, trung vị chỉ 4 tin mỗi quận, 315 quận có dưới 10 tin. Quá ít mẫu để mô hình học được gì.
- Bỏ 3 cột: `no` (số thứ tự), `url` (định danh), `veh_warranty_policy` (một giá trị duy nhất).

**Thẻ 3 – Tin trùng:**
- 691 tin (4,7%) giống hệt nhau ở **mọi thuộc tính và giá**. 331 trong số đó là xe mới, thường do đại lý đăng nhiều xe cùng cấu hình.
- **Vì sao phải loại?** Nếu hai bản giống hệt nhau, một bản rơi vào train, một bản rơi vào test, thì mô hình như được **xem trước đáp án**: điểm đánh giá cao giả tạo.
- Khi so trùng **không xét tỉnh**: cùng một xe, cùng giá đăng ở hai chi nhánh vẫn là một xe.
- Kết quả: còn **14.144 tin**.

**Câu nói gợi ý:** "Bước đầu tiên đưa dữ liệu về đúng kiểu: chữ N/A thành thiếu thật, chuỗi số thành số. Tỉnh được trích từ URL, quận huyện quá thưa nên không dùng. 691 tin trùng hoàn toàn bị loại để tránh cùng một xe nằm ở cả train và test."

---

## Slide 11 – Phát hiện giá trị bất hợp lý

**Mục đích:** loại hoặc sửa các giá trị không thể xảy ra trong thực tế.

**Trên slide có gì:** bảng 6 luật (Cột, Quy tắc, Lý do, Số dòng) và dòng vàng "Giữ lại".

**Giải thích chi tiết:**

**Nguyên tắc:** phân biệt hai loại giá trị "lạ":
- **Sai dữ liệu:** không thể xảy ra (xe 5 năm tuổi chạy 10 km). → Loại hoặc sửa.
- **Ngoại lệ thật:** hiếm nhưng có thật (Mercedes G63 giá 10 tỷ). → **Giữ**, vì đó là xe thật trên thị trường.

Vì vậy không dùng cách cắt máy móc như "bỏ 1% giá cao nhất", mà dùng luật dựa trên hiểu biết thực tế.

**Từng luật:**

| Luật | Ví dụ lỗi | Vì sao |
|---|---|---|
| Giá < 20 triệu hoặc > 10 tỷ → loại (64 tin) | Gõ "45.000.000" thành "4.500.000" | Không biết giá đúng là bao nhiêu nên không sửa được, phải loại |
| Giá là dãy số liên tiếp → loại (14 tin) | 123.456.789 | Người bán gõ khi không muốn công khai giá ("liên hệ"), đây là giá giả |
| "Mới" mà hơn 3 năm tuổi → "Đã sử dụng" (6 tin) | Hyundai Tucson 2011 ghi "mới" | Xe tồn kho đại lý có thể "mới" dù đời 1-3 năm trước, nhưng 15 năm thì chắc chắn ghi sai |
| Xe đã dùng > 500.000 km → coi là thiếu (106) | 1.000.000 km | Gõ thừa số 0 |
| Xe ≥ 2 năm tuổi mà < 100 km → coi là thiếu (447) | Xe 5 năm "10 km" | Người bán gõ theo đơn vị nghìn km (10 = 10.000 km) |
| > 100.000 km/năm → coi là thiếu (25) | Xe 1 tuổi chạy 480.000 km | Xe dịch vụ chạy nhiều cũng chỉ 80.000-100.000 km/năm |

- Với **giá** sai: loại cả dòng, vì giá là đáp án, không được đoán bừa.
- Với **số km** sai: chỉ chuyển ô đó thành thiếu rồi điền lại ở bước sau (slide 13), giữ lại dòng.
- **Làm trước khi điền thiếu**, để giá trị điền không bị tính từ số liệu sai.
- Sau bước này còn **14.066 tin**.

**Dòng vàng – vẫn giữ:** giá 399.999.999 là cách định giá tâm lý ("chưa tới 400 triệu"), 888.888.888 là số đẹp; cả hai vẫn là giá thật.

**Câu nói gợi ý:** "Nhóm không cắt ngoại lệ theo phần trăm, mà dùng luật dựa trên hiểu biết thực tế. Giá sai thì loại vì không biết giá đúng; số km sai thì coi là thiếu rồi điền lại. Xe siêu sang giá cao là thật nên vẫn giữ."

---

## Slide 12 – Giá trả trước / đặt cọc

**Mục đích:** xử lý loại lỗi nguy hiểm nhất: nhãn sai nằm đúng ở biến cần dự đoán.

**Trên slide có gì:**
- Khung xanh **Quy tắc**: loại tin có giá < 30% trung vị của các xe cùng hãng, dòng, năm sản xuất (nhóm ≥ 3 xe).
- Thẻ **129 tin** bị loại, 94% có giá dưới 200 triệu.
- Bảng 5 ví dụ: Toyota Camry 2026 rao 300 triệu (trung vị nhóm 1.400 triệu), Toyota Fortuner 2026 "mới" rao 125 triệu (trung vị 1.249 triệu)…

**Giải thích chi tiết:**

**Vấn đề:** nhiều người bán ghi **số tiền trả trước** (phần còn lại trả góp) vào ô giá để tin đăng nhìn rẻ, thu hút người xem. Ví dụ Fortuner 2026 rao 125 triệu, trong khi xe cùng đời bán khoảng 1,25 tỷ.

**Vì sao nguy hiểm?** Giá là **đáp án** mô hình phải học. Nếu đáp án sai:
- Lúc học, mô hình bị dạy sai.
- Lúc chấm, mô hình đoán đúng giá xe (khoảng 1,2 tỷ) nhưng bị chấm là **sai gần 900%** vì đáp án ghi 125 triệu.

**Vì sao không dùng một ngưỡng cố định?** 100 triệu là giá hợp lý cho xe 20 năm tuổi, nhưng vô lý cho xe 1 năm tuổi. Ngưỡng 20 triệu ở slide 11 không bắt được trường hợp này.

**Giải pháp: so với chính mẫu xe đó.**
1. Gom các xe **cùng hãng, cùng dòng, cùng năm sản xuất**.
2. Tính **giá trung vị** của nhóm.
3. Nếu một tin có giá **thấp hơn 30%** trung vị nhóm thì loại.
4. Chỉ áp dụng cho nhóm có **ít nhất 3 xe**, để trung vị đủ tin cậy.

Lý do chọn 30%: không xe nào mất 70% giá so với xe cùng đời chỉ vì tình trạng hay số km.

**Có phải rò rỉ dữ liệu không?** Luật này dùng giá trên toàn bộ dữ liệu, nhưng chỉ để **loại dòng có đáp án sai** (sửa nhãn). Không có thông tin nào từ giá được đưa vào đầu vào của mô hình. Đây là bước sửa lỗi, không phải tạo đặc trưng.

Sau bước này còn **13.937 tin**.

**Câu nói gợi ý:** "Lỗi nguy hiểm nhất là giá trả trước, vì nó làm sai chính đáp án. Một ngưỡng cố định không bắt được, nên nhóm so với chính mẫu xe đó: giá dưới 30% trung vị của xe cùng hãng, dòng, năm thì loại. Có 129 tin bị loại."

**Câu hỏi có thể gặp:**
- *"Dùng giá để lọc có phải rò rỉ dữ liệu không?"* → "Không, vì đây là sửa nhãn sai: chỉ loại dòng có đáp án sai, không đưa thông tin giá vào đặc trưng. Tuy vậy khi dùng thật, mô hình vẫn sẽ gặp các tin như vậy, nhóm đã nêu ở hạn chế."
- *"Luật này có bắt hết không?"* → "Không. Nhóm có dưới 3 xe thì không áp dụng được, nên vẫn còn sót. Slide 33 cho thấy các xe bị đoán sai nặng nhất chính là những tin còn sót này."

---

## Slide 13 – Xử lý giá trị thiếu

**Mục đích:** điền giá trị thiếu theo đúng nguyên nhân thiếu.

**Trên slide có gì:**
- Hình: mỗi thanh là tỉ lệ thiếu của một cột, bên cạnh ghi cách xử lý:
  - Xuất xứ 41,5% → nhãn riêng "Không rõ".
  - Kiểu dáng 33,0% → giá trị phổ biến nhất theo dòng xe; còn lại "Không rõ".
  - Số chỗ 25,3% → phổ biến nhất theo dòng xe, rồi theo hãng.
  - Số km 10,5% → xe mới 0 km; xe cũ trung vị theo đời + cờ `mileage_missing`.
  - Giá 1 tin → xóa dòng.
- Ba thẻ: Thiếu có cấu trúc, Cờ mileage_missing, Không đoán bừa.

**Giải thích chi tiết:**

**Nguyên tắc chung:** trước khi điền phải hiểu **vì sao thiếu**. Cùng là "thiếu" nhưng nguyên nhân khác nhau thì cách điền khác nhau.

**Số km:**
- **Xe mới (1.235 xe):** thiếu vì trang không có ô km. Giá trị đúng là **0**. Nếu điền trung vị (khoảng 66.000 km) thì xe mới bị biến thành "xe đã chạy 66.000 km", sai hoàn toàn.
- **Xe cũ thiếu km (814 xe, 5,8%):** gồm người bán quên điền và các giá trị bị loại ở slide 11. Điền bằng **trung vị số km của xe cùng năm sản xuất** (xe đời 2018 thường chạy khác xe đời 2010). Dùng trung vị vì số km có vài giá trị rất lớn kéo trung bình lên.
- **Cờ `mileage_missing`:** cột mới, bằng 1 nếu số km là giá trị điền, 0 nếu người bán tự khai. Giúp mô hình **biết** dòng nào là ước lượng. Việc người bán không khai km cũng có thể là một tín hiệu về giá.

**Kiểu dáng và số chỗ:** gần như do **dòng xe** quyết định (Vios luôn là sedan 5 chỗ, Fortuner luôn là SUV 7 chỗ). Nên điền bằng giá trị phổ biến nhất (mode) của xe cùng hãng và dòng.
- **Kiểu dáng không lùi về hãng:** một hãng bán nhiều kiểu (Ford có Ranger bán tải, Everest SUV, Focus sedan). Lấy kiểu phổ biến nhất của Ford gán cho một xe Ford không rõ dòng là **đoán bừa**, nên ghi "Không rõ".
- **Số chỗ được lùi về hãng:** đa số xe 5 chỗ, đoán sai thường chỉ lệch 5 ↔ 7 chỗ, và mô hình còn có dòng xe để bù.

**Xuất xứ:** thiếu tới 41%, và cùng một dòng xe có thể vừa nhập khẩu vừa lắp ráp trong nước (Toyota, Ford). Không đoán được, nên tạo nhãn riêng **"Không rõ"**. Cách này giữ được 41% dữ liệu và để mô hình tự học xem "không khai xuất xứ" có liên quan đến giá không.

**Giá thiếu (1 tin):** xóa dòng. **Không bao giờ điền đáp án**, vì sẽ đưa một giá bịa vào đúng thứ cần dự đoán.

**Câu nói gợi ý:** "Mỗi cột thiếu vì một lý do khác nhau nên điền khác nhau. Xe mới thiếu km vì trang không có ô km, nên điền 0 chứ không điền trung vị. Xe cũ được điền trung vị theo đời và đánh dấu bằng cột mileage_missing. Xuất xứ thiếu quá nhiều nên giữ nhãn Không rõ, không đoán."

---

## Slide 14 – Học trên log(giá) và gộp nhãn hiếm theo cấp

**Mục đích:** hai biến đổi quan trọng: biến đổi biến mục tiêu và giảm số nhãn hiếm.

**Trên slide có gì:**
- **Hình trên trái:** phân bố giá gốc (lệch phải mạnh, skewness = 5,1).
- **Hình trên phải:** phân bố log(giá) (gần đối xứng, skewness = −0,20).
- **Ba thẻ dưới:** ba cấp gộp nhãn.
- **Thẻ xanh:** 69 hãng → 28 nhóm; 509 dòng → 214 nhóm; CV trên train: Ridge 21,9% → 18,9%, RF 16,3% → 16,1%.

**Giải thích chi tiết:**

**A. Log giá**

- **Skewness (độ lệch)** đo độ mất cân đối của phân bố. Bằng 0 là cân đối; dương lớn là có đuôi dài bên phải (vài giá trị rất lớn).
- Giá gốc có skewness 5,1: đa số xe 200-800 triệu, nhưng có đuôi dài tới 10 tỷ. Nếu mô hình học trên giá gốc, sai số của vài xe vài tỷ (sai vài trăm triệu) sẽ **lấn át** sai số của hàng nghìn xe rẻ.
- **Lấy logarit tự nhiên** `ln(giá)` co đuôi lại, phân bố thành hình chuông cân đối (skewness −0,20).
- **Ý nghĩa quan trọng nhất:** trên thang log, khoảng cách biểu thị **tỉ lệ**:
  - Xe 100 → 150 triệu (tăng 50%)
  - Xe 1 → 1,5 tỷ (tăng 50%)
  
  hai cặp này cách nhau **bằng nhau** trên thang log. Nghĩa là mô hình bị phạt theo **sai số phần trăm**, khớp với thước đo chính MAPE.
- Mô hình học `ln(giá)`, dự đoán xong dùng `exp()` để đổi về triệu đồng. **Mọi thước đo đều tính trên giá thật.**
- Lựa chọn này được kiểm chứng ở slide 32: MAPE 16,2% (log) so với 19,6% (giá gốc).

**B. Gộp nhãn hiếm theo cấp**

- **Vấn đề:** có 69 hãng và 509 dòng xe, nhiều dòng chỉ có 1-5 tin. Mô hình học quy luật từ vài mẫu là học nhiễu. Dòng xe chỉ có ở test thì mô hình không biết xử lý.
- **Cách cũ (đơn giản):** dồn mọi dòng hiếm vào một nhãn "Dòng khác". Vấn đề: nhãn này chiếm 17% dữ liệu nhưng tới 65% số xe trên 2 tỷ; một chiếc Mercedes G63 và một chiếc Kia cũ mang **cùng một nhãn**.
- **Cách mới (theo cấp):** mỗi xe lùi về nhóm **gần nhất** còn đủ mẫu:
  1. Dòng xe có ≥ 10 tin → giữ nguyên (Toyota Vios).
  2. Dòng xe hiếm → "<Hãng> - dòng khác" (một dòng Mercedes hiếm vẫn được biết là **Mercedes**).
  3. Hãng có < 30 tin → "Hãng cao cấp khác" (Bentley, Maybach…) hoặc "Hãng phổ thông khác" (Wuling…).
- Phân loại cao cấp / phổ thông dựa trên **định vị thương hiệu** (hiểu biết thị trường), **không dựa vào giá trong dữ liệu**, để không dùng đáp án khi tạo đặc trưng.
- **Ngưỡng 30 / 10** được chọn bằng **5-fold CV trên train**, so với ngưỡng cũ 50 / 30.
- **Kết quả (thẻ xanh):** Ridge cải thiện rõ (21,9% → 18,9%), vì mô hình tuyến tính chỉ có một hệ số cho mỗi nhãn, nhãn trộn xe sang với xe rẻ thì hệ số vô nghĩa. Random Forest cải thiện nhẹ (16,3% → 16,1%) vì nó tự bù được bằng các đặc trưng khác.

**Câu nói gợi ý:** "Giá lệch phải mạnh nên mô hình học trên log giá, để sai số được tính theo phần trăm. Với nhãn hiếm, thay vì dồn tất cả vào một nhãn chung, nhóm gộp theo cấp: dòng hiếm lùi về hãng, hãng hiếm lùi về nhóm cao cấp hoặc phổ thông. Ngưỡng được chọn bằng CV trên tập train."

**Câu hỏi có thể gặp:**
- *"Học trên log mà báo MAPE trên giá thật thì có mâu thuẫn không?"* → "Không. Log giúp mô hình tối ưu sai số tương đối, rất gần với MAPE. Dự đoán xong lấy exp để về giá thật rồi mới tính MAPE."
- *"Vì sao ngưỡng 30 và 10?"* → "Chọn bằng 5-fold CV trên tập train, so với các phương án khác; phương án 30/10 cho sai số thấp nhất và không làm mô hình nào kém đi."

---

## Slide 15 – Mất cân bằng theo phân khúc giá; còn 13.937 tin sạch

**Mục đích:** định lượng mất cân bằng và tổng kết phần làm sạch.

**Trên slide có gì:**
- **Hình trái:** số tin theo 5 phân khúc giá: < 200 triệu 1.972; 200-500 triệu 5.907; 500-1.000 triệu 4.529; 1-2 tỷ 1.071; > 2 tỷ 458.
- **Hình phải (phễu):** số tin qua từng bước: 14.835 → 14.144 (loại 691 trùng) → 14.080 (loại 64 giá sai) → 14.066 (loại 14 giá giả) → 13.937 (loại 129 giá trả trước).
- Hai thẻ: Xử lý mất cân bằng; File sạch chỉ chứa dữ liệu thật.

**Giải thích chi tiết:**

**Mất cân bằng trong bài toán hồi quy là gì?**
- Trong bài toán **phân loại**, mất cân bằng là một lớp có rất ít mẫu (ví dụ 1% giao dịch gian lận).
- Trong bài toán **hồi quy**, không có "lớp". Mất cân bằng thể hiện ở **mật độ dữ liệu không đều theo vùng giá**: rất nhiều xe 200 triệu - 1 tỷ, rất ít xe trên 2 tỷ.
- Phân khúc 200-500 triệu (5.907 tin) nhiều gấp **12,9 lần** phân khúc trên 2 tỷ (458 tin, chỉ 3,3%).
- **Hệ quả:** mô hình tối ưu sai số trung bình sẽ học tốt vùng đông mẫu, học kém vùng thưa, mà vùng thưa lại là xe đắt, nơi sai số tuyệt đối tốn kém nhất.
- 5 phân khúc **chỉ dùng để phân tích, chia mẫu và đánh giá**, không làm đặc trưng (vì được tạo từ giá, tức đáp án).

**Cách xử lý (thẻ trái):**
1. Chia train/test **phân tầng** theo phân khúc (slide 16).
2. Học trên **log giá** (giảm ảnh hưởng của đuôi phải).
3. Luôn báo **MAPE theo từng phân khúc**, không chỉ một con số trung bình.
4. Thử **trọng số mẫu, oversampling, undersampling** bằng CV (slide 32).

**Phễu (hình phải):** giữ lại **93,9%** dữ liệu. Mỗi bước loại đều có lý do cụ thể ở các slide trước. Các bước khác (sửa nhãn "Mới", chuyển km vô lý thành thiếu, điền thiếu, gộp nhãn) **không làm giảm số dòng**.

**File sạch chỉ chứa dữ liệu thật (thẻ phải):** không ghi mẫu nhân bản vào file `clean_data_oto.csv`. Nếu ghi, người dùng sau chia ngẫu nhiên sẽ khiến bản sao của cùng một xe nằm ở cả train lẫn test, điểm đánh giá cao giả tạo. Cân bằng (nếu dùng) chỉ làm trên phần train, sau khi đã chia.

**Câu nói gợi ý:** "Với bài toán hồi quy, mất cân bằng là mật độ dữ liệu không đều theo vùng giá: xe trên 2 tỷ chỉ 3,3%, ít hơn phân khúc đông nhất gần 13 lần. Sau làm sạch, nhóm giữ lại 13.937 tin, tức 93,9% dữ liệu thô, và không còn giá trị thiếu."

---

# PHẦN 4. MÔ HÌNH RANDOM FOREST (slide 16-25)

## Slide 16 – Thiết kế thí nghiệm

**Mục đích:** cách chia dữ liệu và chọn tham số một cách khách quan.

**Trên slide có gì:**
- Hình: tỉ lệ % mỗi phân khúc giá trong train (xanh) và test (cam) gần như bằng nhau.
- Ba bước bên phải: Train 80%, Test 20%, Hai bản Random Forest.

**Giải thích chi tiết:**

**Chia 80/20:** 11.149 tin để học (train), 2.788 tin để chấm điểm cuối (test).

**Vì sao chia phân tầng?** Xe trên 2 tỷ chỉ có 3,3%. Nếu chia ngẫu nhiên hoàn toàn, có thể tập test gần như không có xe sang; điểm đánh giá sẽ đẹp nhưng không cho biết mô hình xử lý xe sang thế nào. **Chia phân tầng** đảm bảo mỗi phân khúc có **cùng tỉ lệ** ở train và test (hình: các cặp cột xanh-cam cao bằng nhau).

**Vì sao không tách tập validation riêng?**
- Thông thường chia 3 phần: train (học), validation (chọn tham số), test (chấm cuối).
- Ở đây chỉ có khoảng 460 xe trên 2 tỷ; tách thêm một tập validation cố định thì phần xe sang trong đó quá ít, kết quả chọn tham số dễ dao động.
- Thay vào đó dùng **cross-validation (CV)**:
  1. Chia train thành 5 phần bằng nhau.
  2. Lần 1: học trên phần 2-5, chấm trên phần 1. Lần 2: học trên 1, 3-5, chấm trên phần 2… Lặp 5 lần.
  3. Lấy trung bình 5 điểm.
  
  Mọi xe trong train đều được dùng làm validation đúng một lần, nên kết quả ổn định hơn.
- Bản tự viết dùng **OOB** thay cho CV (giải thích ở slide 20), vì chạy chậm.

**Câu nói gợi ý:** "Dữ liệu chia 80/20, phân tầng theo phân khúc giá để tập test có đủ xe sang. Tham số được chọn bằng cross-validation trên tập train; tập test chỉ dùng một lần ở cuối."

**Câu hỏi có thể gặp:**
- *"Sao không dùng tập validation?"* → "Vì dữ liệu xe sang ít, CV dùng mọi phần của train làm validation nên ổn định hơn một tập validation cố định."

---

## Slide 17 – Thước đo đánh giá

**Mục đích:** giải thích từng chỉ số, chỉ số nào cần cao, cần thấp, thế nào là tốt.

**Trên slide có gì:** bảng 6 thước đo (Thước đo, Ý nghĩa, Tốt khi, Mức tham khảo) và dòng Mốc so sánh (baseline).

**Giải thích chi tiết từng thước đo:**

Ký hiệu: `p` là giá thật, `p̂` là giá dự đoán của một xe.

**1. MAPE – sai số phần trăm trung bình (thước đo chính). Càng THẤP càng tốt.**
- Mỗi xe tính `|p − p̂| / p`, rồi lấy trung bình.
- *Ví dụ:* xe 500 triệu đoán 550 triệu → sai 10%.
- **Vì sao là thước đo chính?** Lệch 100 triệu là nhỏ với xe 3 tỷ (3%) nhưng rất lớn với xe 150 triệu (67%). MAPE đo theo phần trăm nên công bằng giữa xe rẻ và xe đắt.
- **Mức tham khảo** (quy ước thường dùng trong dự báo, theo Lewis 1982): dưới 10% rất tốt; 10-20% tốt; 20-50% tạm được; trên 50% kém. Đây là quy ước, không phải tiêu chuẩn cứng.

**2. MedAPE – trung vị sai số phần trăm. Càng THẤP càng tốt.**
- Xếp sai số % của mọi xe từ nhỏ đến lớn, lấy giá trị ở giữa.
- Cho biết sai số của một xe **"điển hình"**, không bị vài xe sai rất nặng kéo lệch.
- Nếu MedAPE thấp hơn MAPE nhiều: đa số xe đoán tốt, chỉ một nhóm nhỏ sai nặng.

**3. MAE – sai số tuyệt đối trung bình (triệu đồng). Càng THẤP càng tốt.**
- Trung bình `|p − p̂|`. Dễ hiểu: "trung bình đoán lệch bao nhiêu tiền".
- Không có ngưỡng chung vì phụ thuộc mức giá.

**4. RMSE – căn của trung bình bình phương sai số (triệu đồng). Càng THẤP càng tốt.**
- Bình phương sai số trước khi lấy trung bình nên **phạt nặng lỗi lớn**: sai 1 tỷ bị tính nặng gấp 100 lần sai 100 triệu.
- Luôn ≥ MAE. Nếu RMSE lớn hơn MAE nhiều thì có vài lỗi rất lớn.

**5. R² (log) – hệ số xác định trên log giá. Càng CAO càng tốt.**
- Đo tỉ lệ biến động của log giá mà mô hình giải thích được.
- R² = 1: hoàn hảo; R² = 0: không hơn việc luôn đoán giá trung bình; R² < 0: còn kém hơn thế.
- Tính trên **log** vì đó là thang mô hình học; trên giá gốc, R² bị vài xe 5-10 tỷ chi phối.

**6. Lệch ≤ 10% / ≤ 20%. Càng CAO càng tốt.**
- Tỉ lệ xe có giá dự đoán nằm trong ±10% / ±20% giá thật.
- Dễ giải thích cho người dùng: "4 trên 5 xe được định giá sát trong khoảng ±20%".

**Baseline (mốc so sánh):** luôn đoán **giá trung vị của tập train** cho mọi xe, không nhìn thông tin gì. Không chỉ số nào "tốt" khi đứng một mình; luôn phải so với baseline. Mô hình phải tốt hơn hẳn baseline mới có ý nghĩa.

Ngoài ra luôn báo **MAPE theo 5 phân khúc giá**, vì một con số trung bình che mất việc mô hình kém ở hai đầu thang giá.

**Câu nói gợi ý:** "Các chỉ số sai số như MAPE, MAE, RMSE càng thấp càng tốt; R² và tỉ lệ xe đoán sát càng cao càng tốt. MAPE là thước đo chính vì tính theo phần trăm, công bằng giữa xe rẻ và xe đắt. Mọi chỉ số đều được so với baseline luôn đoán giá trung vị."

---

## Slide 18 – One-hot hay mã số thứ tự?

**Mục đích:** chọn cách đổi biến phân loại thành số cho rừng, có kiểm chứng.

**Trên slide có gì:**
- Hình hai panel: MAPE tổng và MAPE xe trên 2 tỷ của 4 phương án. Thanh cam là one-hot (16,4% và 28,9%), ba thanh xám là mã số thứ tự với `max_features` 0,33 / 0,6 / 1,0 (16,7-18,3% và 29,0-39,0%).
- Hai thẻ: "Chọn one-hot: MAPE 16,4%"; "Rừng không cần age², log, chuẩn hóa".

**Giải thích chi tiết:**

**Vì sao phải mã hóa?** Mô hình chỉ làm việc với số, nên các cột chữ như hãng, dòng xe phải đổi thành số.

**Hai cách:**

| Cách | Ví dụ | Ưu | Nhược |
|---|---|---|---|
| **One-hot** | Mỗi dòng xe một cột 0/1: cột "Toyota Vios" = 1 nếu xe là Vios, 0 nếu không. 214 dòng xe → 214 cột. Tổng 277 cột. | Không tạo thứ tự giả. Một câu hỏi "có phải Vios không?" là tách được ngay một dòng xe. | Nhiều cột. |
| **Mã số thứ tự** | Đánh số theo bảng chữ cái: Audi A4 = 0, BMW X5 = 1, … Mỗi cột phân loại thành một cột số. Tổng 12 cột. | Ít cột. | Thứ tự là **giả**: số 5 không "lớn hơn" số 4 về ý nghĩa. Xe sang và xe rẻ nằm xen kẽ. |

**Với cây, thứ tự giả gây hại thế nào?** Cây chia bằng câu hỏi "mã ≤ ngưỡng?". Nếu G-Class mang mã 87 và nằm giữa hai dòng xe rẻ mã 86 và 88, cây phải hỏi hai lần ("mã ≤ 87?" rồi "mã > 86?") mới cô lập được G-Class. Dòng xe hiếm không đủ mẫu để cây chia sâu tới đó.

**Vì sao thử nhiều mức `max_features` cho mã số?** `max_features` là tỉ lệ đặc trưng xét ở mỗi lần chia. Với 12 cột, mức 0,33 nghĩa là mỗi nút chỉ xét 4 cột, có thể không xét tuổi xe, nên kém nhất (18,3%). Thử thêm 0,6 và 1,0 để so sánh công bằng; vẫn thua one-hot.

**Kết quả:** one-hot thấp nhất ở cả MAPE tổng (16,4%) và xe trên 2 tỷ (28,9% so với 29-39%). One-hot cũng hợp với bản tự cài đặt: cột 0/1 chỉ có 2 giá trị, không mất thông tin khi chia bin (slide 22).

**Thẻ phải – vì sao rừng không cần biến đổi số?** Cây chỉ hỏi "tuổi ≤ 5?". Hỏi "tuổi² ≤ 25?" hay "log(tuổi) ≤ log 5?" cho **đúng cùng một phép chia**. Nên với cây, `age²`, `log(km)` không thêm thông tin, chỉ làm độ quan trọng bị chia đôi. Cây cũng không phụ thuộc thang đo, nên không cần chuẩn hóa.

**Câu nói gợi ý:** "Nhóm so sánh hai cách mã hóa bằng CV trên tập train. One-hot cho sai số thấp nhất, rõ nhất ở xe sang, vì một câu hỏi là tách được một dòng xe; còn mã số thứ tự xếp xe sang và xe rẻ xen kẽ theo bảng chữ cái."

---

## Slide 19 – Cây hồi quy CART

**Mục đích:** giải thích thành phần cơ bản của rừng bằng một cây thật.

**Trên slide có gì:**
- Hình: một cây độ sâu 3 học từ tập train. Ô xanh là nút (câu hỏi, số xe, giá đại diện); ô cam là lá (giá dự đoán).
- Khung xanh: công thức gain.
- Ba gạch đầu dòng: độ chệch thấp, phương sai cao, cần trung bình nhiều cây.

**Giải thích chi tiết:**

**Cây quyết định hoạt động thế nào?** Cây chia dữ liệu bằng các câu hỏi có/không, giống trò "20 câu hỏi". Mỗi câu hỏi tách xe thành hai nhóm có giá khác nhau rõ nhất.

**Đọc cây trên slide (từ trên xuống):**

```
Gốc: 11.149 xe, giá đại diện ~437 triệu
│ Câu hỏi: Tuổi xe ≤ 13,5?
├── CÓ (xe mới hơn) – 9.474 xe, ~528 triệu
│   │ Hộp số = Số sàn?
│   ├── KHÔNG (số tự động) – 8.048 xe, ~586 triệu
│   │   │ Kiểu dáng = Hatchback?
│   │   ├── KHÔNG → lá: ~617 triệu (7.487 xe)
│   │   └── CÓ    → lá: ~297 triệu (561 xe)
│   └── CÓ (số sàn) – 1.426 xe, ~291 triệu
│       │ Số chỗ ≤ 6,5?
│       ├── CÓ    → lá: ~222 triệu (743 xe)
│       └── KHÔNG → lá: ~390 triệu (683 xe)
└── KHÔNG (xe cũ hơn 13,5 năm) – 1.675 xe, ~150 triệu
    │ Hộp số = Số sàn?
    ├── KHÔNG → Tuổi ≤ 20,5? → CÓ: ~237 triệu (753 xe); KHÔNG: ~131 triệu (108 xe)
    └── CÓ    → Tuổi ≤ 20,5? → CÓ: ~121 triệu (492 xe); KHÔNG: ~73 triệu (322 xe)
```

- Câu hỏi đầu tiên **do cây tự chọn** là tuổi xe, vì đó là câu tách giá tốt nhất. Điều này khớp với kết quả độ quan trọng ở slide 30.
- Chỉ với 3 tầng, cây đã tách nhóm **~617 triệu** (xe mới hơn 13,5 năm, số tự động, không phải hatchback) khỏi nhóm **~73 triệu** (xe trên 20 năm, số sàn).
- **Giá đại diện** ở mỗi ô = `exp(trung bình log giá)` của các xe trong ô.
- Ở lá, giá dự đoán cho một xe mới là giá đại diện của lá mà xe đó rơi vào.

**Công thức gain – cây chọn câu hỏi thế nào?** Ở mỗi nút, cây thử mọi đặc trưng và mọi ngưỡng, chọn phép chia làm **giảm tổng bình phương sai số (SSE)** nhiều nhất:

```
gain = S_L² / n_L  +  S_R² / n_R  −  S² / n
```

- `n`, `S`: số xe và tổng log giá của nút.
- `n_L, S_L` và `n_R, S_R`: của nhánh trái và nhánh phải.
- Công thức này chính là mức giảm SSE khi thay "một giá chung cho cả nút" bằng "hai giá riêng cho hai nhánh". Gain lớn nghĩa là hai nhánh khác nhau rõ.

**Điểm yếu của một cây:**
- **Độ chệch thấp:** cây sâu (cây thật trong rừng sâu tới 30 tầng, hàng nghìn nút) có thể học rất khớp dữ liệu train.
- **Phương sai cao:** đổi vài mẫu là cấu trúc cây thay đổi hẳn. Nói cách khác, cây **học thuộc** dữ liệu train, dự đoán dữ liệu mới không ổn định.
- → Cần **lấy trung bình nhiều cây** (slide 20).

**Câu nói gợi ý:** "Đây là một cây thật học từ dữ liệu, giới hạn 3 tầng để dễ nhìn. Câu hỏi đầu tiên cây tự chọn là tuổi xe. Ở mỗi nút, cây chọn câu hỏi làm giảm sai số nhiều nhất theo công thức gain. Điểm yếu là một cây sâu học thuộc dữ liệu, nên cần lấy trung bình nhiều cây."

**Câu hỏi có thể gặp:**
- *"Giải thích công thức gain?"* → "Đó là mức giảm tổng bình phương sai số khi thay một giá chung của nút bằng hai giá riêng của hai nhánh. Cây chọn phép chia có gain lớn nhất."

---

## Slide 20 – Random Forest: lấy trung bình nhiều cây khác nhau

**Mục đích:** giải thích cách rừng khắc phục điểm yếu của một cây.

**Trên slide có gì:**
- Sơ đồ: Tập train → Bootstrap 1…T → Cây 1…T → Trung bình T dự đoán.
- Công thức `ŷ(x) = (1/T) Σ fₜ(x)`.
- Ba thẻ: Bootstrap, max_features, OOB.

**Giải thích chi tiết:**

**Ý tưởng chung:** nhiều cây **khác nhau** cùng dự đoán, lấy trung bình. Sai số ngẫu nhiên của từng cây triệt tiêu lẫn nhau, nên kết quả ổn định hơn hẳn một cây.

*Ví dụ dễ hiểu:* hỏi giá một chiếc xe với 300 người môi giới, mỗi người chỉ xem một phần thông tin và một phần thị trường khác nhau, rồi lấy trung bình. Kết quả đáng tin hơn hỏi một người.

**Để các cây khác nhau, rừng dùng hai nguồn ngẫu nhiên:**

**1. Bootstrap (thẻ 1).**
- Mỗi cây học trên một mẫu lấy ngẫu nhiên **có hoàn lại** từ train, cùng kích thước 11.149 xe.
- "Có hoàn lại" nghĩa là bốc xong bỏ lại vào, nên có xe được bốc 2-3 lần, có xe không được bốc lần nào.
- Kết quả: mỗi mẫu chứa khoảng **63%** số xe khác nhau.
- *Vì sao 63%?* Xác suất một xe **không** được chọn sau n lần bốc là (1 − 1/n)ⁿ ≈ e⁻¹ ≈ 0,37. Vậy khoảng 37% xe không được chọn, 63% được chọn.

**2. Chọn ngẫu nhiên đặc trưng `max_features` (thẻ 2).**
- Mỗi lần chia nút, cây chỉ được xét một **phần** đặc trưng ngẫu nhiên (ví dụ 50%).
- Nếu không có bước này, mọi cây đều chọn tuổi xe ở gốc và giống hệt nhau; lấy trung bình các cây giống nhau thì không giúp gì.

**3. Lấy trung bình:** `ŷ(x) = (1/T) Σ fₜ(x)`: dự đoán của rừng là trung bình dự đoán của T cây.

**OOB – out-of-bag (thẻ 3).**
- Khoảng 37% xe không nằm trong mẫu bootstrap của một cây, gọi là "ngoài túi" của cây đó.
- Để chấm một xe, chỉ dùng những cây **chưa thấy** xe đó. Làm vậy với mọi xe sẽ có một ước lượng sai số **khách quan** mà **không cần tập validation riêng**, và chỉ cần huấn luyện một lần.
- Đây là lý do bản tự cài đặt (chạy chậm) dùng OOB để chọn tham số.

**Câu nói gợi ý:** "Random Forest huấn luyện nhiều cây, mỗi cây trên một mẫu bootstrap khác nhau và mỗi lần chia chỉ xét một phần đặc trưng ngẫu nhiên, rồi lấy trung bình. Trung bình nhiều cây ít giống nhau có phương sai nhỏ hơn hẳn một cây. Khoảng 37% xe không được mỗi cây thấy, gọi là out-of-bag, dùng để ước lượng sai số mà không cần tập riêng."

**Câu hỏi có thể gặp:**
- *"Vì sao khoảng 37% mẫu nằm ngoài bootstrap?"* → "Xác suất một mẫu không được chọn sau n lần bốc có hoàn lại là (1 − 1/n)ⁿ, tiến tới e⁻¹ ≈ 0,37 khi n lớn."
- *"OOB là gì, dùng để làm gì?"* → "Là các mẫu không nằm trong bootstrap của một cây. Dự đoán chúng bằng những cây chưa thấy chúng cho ước lượng sai số khách quan, thay cho tập validation."

---

## Slide 21 – Random Forest thư viện: tinh chỉnh bằng CV

**Mục đích:** cách chọn tham số cho bản thư viện và kết quả.

**Trên slide có gì:**
- Bảng 5 cấu hình tốt nhất (300 cây); dòng cam là cấu hình chọn: `min_samples_leaf = 1`, `max_features = 0,5`, `max_depth = 30`, CV RMSE (log) = 0,2692.
- Ba thẻ: OOB R² 0,896; huấn luyện 9 giây; 12 cấu hình / 3-fold.

**Giải thích chi tiết:**

**Siêu tham số** là các "nút vặn" phải chọn trước khi huấn luyện:

| Tham số | Ý nghĩa | Ảnh hưởng |
|---|---|---|
| `n_estimators` | số cây | nhiều hơn thì ổn định hơn, đến một mức thì bão hòa |
| `max_depth` | độ sâu tối đa | sâu hơn thì học chi tiết hơn |
| `min_samples_leaf` | số xe tối thiểu ở mỗi lá | lớn hơn thì cây "mượt" hơn, ít học thuộc hơn |
| `max_features` | tỉ lệ đặc trưng xét mỗi lần chia | nhỏ hơn thì các cây đa dạng hơn |

**Cách tìm:** **RandomizedSearchCV** thử ngẫu nhiên 12 cấu hình trong không gian (`max_depth` ∈ {20, 30, không giới hạn}, `min_samples_leaf` ∈ {1, 2, 3, 5}, `max_features` ∈ {0,33; 0,5; 0,8}), mỗi cấu hình chấm bằng **3-fold CV phân tầng**. Thử ngẫu nhiên rẻ hơn thử hết mọi tổ hợp mà thường tìm được cấu hình gần tốt nhất.

**Cách đọc bảng:** CV RMSE (log) là sai số trên thang log khi CV, **càng nhỏ càng tốt**. Sai số trên thang log tương đương sai số tương đối, nên nhất quán với MAPE.

**Nhận xét:** các cấu hình tốt đều có **cây sâu (30) và lá nhỏ (1-2)**. Dữ liệu có nhiều tổ hợp hãng-dòng-đời xe riêng biệt, nên mỗi cây cần đủ phức tạp để học từng nhóm; việc lấy trung bình 300 cây đã kiểm soát phương sai.

**Các thẻ:**
- **OOB R² = 0,896:** mô hình giải thích khoảng 90% biến động của log giá, đo trên các xe "ngoài túi".
- **9 giây:** thư viện viết bằng C/Cython và chạy song song nhiều lõi CPU nên rất nhanh.

**Câu nói gợi ý:** "Bản thư viện được tinh chỉnh bằng RandomizedSearchCV với 12 cấu hình và 3-fold CV phân tầng. Cấu hình tốt nhất là 300 cây, độ sâu 30, lá tối thiểu 1 mẫu, xét 50% đặc trưng mỗi lần chia; OOB R² đạt 0,896."

---

## Slide 22 – Random Forest tự cài đặt bằng NumPy

**Mục đích:** giải thích cấu trúc code tự viết và kỹ thuật tăng tốc.

**Trên slide có gì:**
- Ba lớp đánh số: `Binner`, `RegressionTreeScratch`, `RandomForestScratch`.
- Bốn bước bên phải: Đếm theo bin → Cộng dồn → Tính gain → Chọn max.
- Thẻ xanh: cột one-hot không mất thông tin; cột số mất rất ít độ chi tiết.

**Giải thích chi tiết:**

**Ba lớp:**
1. **`Binner`:** chia mỗi đặc trưng thành tối đa **32 "ngăn" (bin)** theo phân vị, chỉ làm **một lần** trên tập train. Ví dụ tuổi xe 0-47 năm được chia thành các ngăn sao cho mỗi ngăn có số xe gần bằng nhau.
2. **`RegressionTreeScratch`:** cây CART, tìm phép chia tốt nhất bằng công thức gain. Cây được dựng bằng **ngăn xếp** (stack) thay vì đệ quy, để không bị giới hạn độ sâu đệ quy của Python.
3. **`RandomForestScratch`:** bootstrap, chọn ngẫu nhiên đặc trưng, lấy trung bình; tính thêm OOB và độ quan trọng đặc trưng.

**Vấn đề tốc độ:** cách cơ bản là ở mỗi nút, với mỗi đặc trưng, sắp xếp các xe rồi thử từng ngưỡng. Với 11.149 xe, 277 cột, hàng nghìn nút và 100 cây, viết bằng Python thuần thì **rất chậm**.

**Kỹ thuật histogram (bốn bước bên phải):** đây cũng là kỹ thuật của thư viện LightGBM và HistGradientBoosting.
1. **Đếm theo bin:** dùng `np.bincount` đếm số xe và tổng log giá trong mỗi ngăn. Chỉ một lệnh cho mọi đặc trưng.
2. **Cộng dồn:** dùng `np.cumsum`. Phần tử thứ b của tổng cộng dồn chính là "số xe và tổng log giá của nhánh trái nếu chia ở ngưỡng b". Vậy có ngay nhánh trái của **mọi ngưỡng**; nhánh phải = tổng − nhánh trái.
3. **Tính gain:** thay vào công thức gain cho mọi (đặc trưng, ngưỡng) cùng lúc bằng phép toán ma trận.
4. **Chọn max:** lấy phép chia có gain lớn nhất.

Thay vì thử từng ngưỡng bằng vòng lặp Python, tất cả được tính bằng vài phép toán NumPy, nhanh hơn nhiều.

**Có mất thông tin không?**
- Cột one-hot chỉ có 2 giá trị (0/1), nằm gọn trong 2 ngăn → **không mất gì**.
- Cột số (tuổi, km) bị gom vào 32 ngăn → mất một chút độ chi tiết, nhưng rất ít. Đây là một nguyên nhân khiến bản tự viết lệch nhẹ so với thư viện.

**Độ quan trọng đặc trưng:** tổng gain mà đặc trưng mang lại ở mọi nút của mọi cây, chuẩn hóa về tổng 1. Cùng định nghĩa với `scikit-learn`.

**Câu nói gợi ý:** "Bản tự cài đặt gồm ba lớp. Để chạy đủ nhanh bằng Python, nhóm dùng kỹ thuật histogram như LightGBM: chia mỗi đặc trưng thành 32 ngăn một lần, rồi ở mỗi nút chỉ cần đếm bằng bincount và cộng dồn bằng cumsum là có gain của mọi ngưỡng cùng lúc."

**Câu hỏi có thể gặp:**
- *"Vì sao chia 32 bin không mất nhiều thông tin?"* → "Cột one-hot chỉ có 2 giá trị nên không mất gì. Cột số chia theo phân vị nên mỗi ngăn có số xe gần bằng nhau; các ngưỡng tốt nhất thường vẫn nằm gần ranh giới ngăn. Kết quả kiểm chứng ở slide 23 cho thấy chênh lệch rất nhỏ."

---

## Slide 23 – Kiểm chứng: một cây và cả rừng trùng khớp thư viện

**Mục đích:** chứng minh code tự viết đúng.

**Trên slide có gì:**
- **Bảng trái (một cây, lá ≥ 5 mẫu):** số nút 3.481 / 3.429; R² train 0,929 / 0,927; R² test 0,842 / 0,851; MAPE test 19,6% / 18,6% (thư viện / tự cài đặt).
- **Hình phải:** dự đoán của hai bản rừng trên từng xe test (biểu đồ chấm) và phân bố độ lệch (histogram).
- Hai thẻ: 1,7% (độ lệch trung vị); 83% (số xe lệch không quá 5%).

**Giải thích chi tiết:**

**Bước 1 – Kiểm chứng một cây.** Dựng một cây bằng code tự viết và một cây bằng `DecisionTreeRegressor` của thư viện, **cùng tham số** (lá ít nhất 5 mẫu, không giới hạn độ sâu, xét mọi đặc trưng). So sánh:
- Số nút gần bằng nhau (3.429 so với 3.481).
- R² và MAPE gần bằng nhau.

→ Lớp cây tự viết **đúng**.

Bảng còn cho thấy một điều quan trọng: **R² train 0,93 nhưng R² test chỉ 0,84-0,85**. Một cây khớp dữ liệu train tốt hơn hẳn dữ liệu mới, đó là dấu hiệu **học thuộc (phương sai cao)**, đúng như lý thuyết ở slide 19.

**Bước 2 – Kiểm chứng cả rừng trên từng xe.**
- Không chỉ so con số trung bình (MAPE), mà so **dự đoán trên từng xe** trong tập test.
- **Biểu đồ chấm:** mỗi chấm là một xe; trục ngang là giá bản thư viện đoán, trục dọc là giá bản tự viết đoán. Nếu hai bản đoán giống nhau, chấm nằm trên đường chéo. Các chấm bám sát đường chéo.
- **Histogram:** phân bố độ lệch giữa hai bản; phần lớn dồn sát 0.
- **1,7%:** độ lệch trung vị; **83%** số xe lệch không quá 5%.

**Vì sao vẫn lệch một chút?** Ba nguyên nhân:
1. Bản tự viết chia đặc trưng thành 32 bin.
2. Bản tự viết dùng 100 cây, bản thư viện 300 cây.
3. Hai bản tinh chỉnh bằng cách khác nhau (OOB và CV) nên tham số hơi khác (`min_samples_leaf` 2 so với 1).

*Lưu ý:* tập test ở đây chỉ dùng để **kiểm tra tính đúng của code**, không dùng để chọn tham số.

**Câu nói gợi ý:** "Nhóm kiểm chứng ở hai mức. Một cây tự viết có số nút và R² gần như bằng cây của thư viện. Cả rừng thì dự đoán trên từng xe lệch trung vị 1,7%, 83% số xe lệch không quá 5%."

---

## Slide 24 – Từ một cây đến một rừng

**Mục đích:** cho thấy trực quan lợi ích của việc lấy trung bình nhiều cây.

**Trên slide có gì:**
- **Hình trái:** OOB RMSE của rừng tự viết khi số cây tăng từ 1 đến 100.
- **Hình phải:** MAPE và R² trên test của một cây và cả rừng (hai bản).
- Ba thẻ: 0,346 → 0,263; 0,892; 19% → 15,5%.

**Giải thích chi tiết:**

**Tinh chỉnh bản tự viết bằng OOB:** thay vì CV (phải huấn luyện 3-5 lần mỗi cấu hình), bản tự viết dùng OOB: mỗi cấu hình chỉ huấn luyện **một lần** với 30 cây. Thử 6 cấu hình, chọn được độ sâu 30, lá tối thiểu 2, xét 50% đặc trưng. Sau đó huấn luyện 100 cây, mất khoảng 2,4 phút.

**Đọc hình trái:**
- Với 1 cây, OOB RMSE = 0,346.
- Sai số **giảm rất nhanh** trong khoảng 20 cây đầu, rồi **đi ngang (bão hòa)** quanh 0,263 khi đủ 100 cây.
- Nghĩa là: thêm cây giúp nhiều lúc đầu; sau một mức, thêm cây chỉ tốn thời gian mà không cải thiện.

**Đọc hình phải (trên test):**
- MAPE: một cây khoảng 19% (19,6% thư viện, 18,6% tự viết) → cả rừng 15,5-15,7%.
- R²: một cây khoảng 0,84-0,85 → cả rừng 0,887-0,891.
- Bản tự viết (màu nhạt) đi **đúng xu hướng** của bản thư viện (màu đậm) ở cả hai mức.

*Lưu ý trục:* trục R² bắt đầu từ 0,80 để thấy rõ chênh lệch; chênh lệch thật giữa một cây và rừng là khoảng 0,04-0,05.

**OOB R² = 0,892** của bản tự viết, rất sát 0,896 của bản thư viện.

**Câu nói gợi ý:** "Khi tăng số cây, sai số giảm rất nhanh trong vài chục cây đầu rồi bão hòa. Trên tập test, một cây sai khoảng 19%, cả rừng chỉ còn 15,5%. Đây là bằng chứng trực quan cho lợi ích của việc lấy trung bình nhiều cây."

---

## Slide 25 – Ridge Regression: mốc so sánh tuyến tính

**Mục đích:** giới thiệu mô hình so sánh và lý do chọn nó.

**Trên slide có gì:**
- Khung hàm mất mát: `J(w) = (1/2n) Σ (yᵢ − ŷᵢ)² + (α/2) Σ wⱼ²`.
- Ba gạch đầu dòng: tổ hợp tuyến tính; phạt L2; α = 0,56.
- Hai thẻ: Vì sao chọn Ridge làm mốc; Ridge khác rừng ở đặc trưng số.

**Giải thích chi tiết:**

**Ridge là gì?** Hồi quy tuyến tính: dự đoán = hằng số + tổng (trọng số × đặc trưng). Ví dụ: log giá = w₀ + w₁·tuổi + w₂·(là Toyota) + … Mỗi đặc trưng đóng góp một lượng cố định, **cộng lại** với nhau.

**Hàm mất mát gồm hai phần:**
1. **Sai số dự đoán** `(1/2n) Σ (yᵢ − ŷᵢ)²`: như hồi quy tuyến tính thường.
2. **Khoản phạt L2** `(α/2) Σ wⱼ²`: phạt trọng số lớn.

**Vì sao cần phạt?** Sau one-hot có khoảng 278 cột, nhiều cột **tương quan mạnh** (hãng Toyota và dòng Toyota Vios luôn đi cùng nhau). Không có phạt, các trọng số có thể phình to và triệt tiêu lẫn nhau (ví dụ +1000 và −999), mô hình rất nhạy với nhiễu. Khoản phạt kéo trọng số về gần 0, mô hình ổn định hơn.

**α (alpha)** là độ mạnh của khoản phạt: quá nhỏ thì gần như không phạt (dễ học thuộc); quá lớn thì trọng số bị ép về 0 (học quá kém). α = 0,56 được chọn bằng 5-fold CV trên 25 giá trị từ 0,001 đến 1000.

**Vì sao chọn Ridge làm mốc (thẻ xanh)?**
- Ridge là **mô hình tuyến tính tốt nhất có thể** trên cùng dữ liệu: đã được thêm `age²`, `log(km)` để biểu diễn khấu hao cong, và đã được tinh chỉnh bằng CV như rừng.
- Cùng tập train/test, cùng thước đo → **so sánh công bằng**.
- Chênh lệch giữa Ridge và Random Forest trả lời câu hỏi: "Quan hệ **phi tuyến** và **tương tác** giữa các đặc trưng đóng góp bao nhiêu vào độ chính xác?"

**Ridge khác rừng ở đặc trưng số (thẻ nhạt):** Ridge chỉ cộng các hiệu ứng tuyến tính, nhưng xe mất giá **nhanh những năm đầu rồi chậm lại** (đường cong). Thêm `age²` và `log(km)` giúp biến đường cong thành gần tuyến tính để Ridge học được. Ridge cũng cần **chuẩn hóa** (StandardScaler) để khoản phạt công bằng giữa các đặc trưng có thang đo khác nhau (tuổi 0-47, km 0-500.000).

**Câu nói gợi ý:** "Ridge chỉ là mô hình so sánh, dùng bản thư viện. Đây là mô hình tuyến tính tốt nhất có thể trên cùng dữ liệu, cũng được tinh chỉnh bằng CV, nên so sánh là công bằng. Phần Random Forest tốt hơn Ridge chính là đóng góp của quan hệ phi tuyến và tương tác."

**Câu hỏi có thể gặp:**
- *"Sao không so với XGBoost hay Gradient Boosting?"* → "Đề yêu cầu phân tích kỹ một mô hình. Ridge đủ để trả lời câu hỏi phi tuyến giúp bao nhiêu. Gradient Boosting là hướng phát triển, có thể dùng lại lớp cây đã tự cài đặt."

---

# PHẦN 5. KẾT QUẢ VÀ KẾT LUẬN (slide 26-35)

## Slide 26 – Kết quả tổng thể trên tập test

**Mục đích:** con số chính của đề tài.

**Trên slide có gì:**
- Ba ô lớn: Baseline 83,5%; Ridge 18,5%; Random Forest 15,5%.
- Bảng đầy đủ 4 mô hình với 7 chỉ số và thời gian huấn luyện.

| Mô hình | MAPE | MedAPE | MAE (triệu) | RMSE (triệu) | R² (log) | ≤ 20% | Huấn luyện |
|---|---|---|---|---|---|---|---|
| Baseline | 83,5% | 40,0% | 337 | 724 | 0,00 | 26% | – |
| Ridge | 18,5% | 10,7% | 120 | 411 | 0,873 | 75% | 0,04 giây |
| **RF thư viện** | **15,5%** | **9,0%** | **102** | **372** | **0,891** | **80%** | 9 giây |
| RF tự cài đặt | 15,7% | 9,0% | 106 | 388 | 0,887 | 80% | 143 giây |

**Giải thích chi tiết:**

Đây là lần **duy nhất** tập test (2.788 tin) được dùng để đánh giá.

**Đọc từng chỉ số của Random Forest:**
- **MAPE 15,5%:** trung bình mỗi xe bị đoán lệch 15,5%. Theo thang tham khảo, 10-20% là **mức tốt**. Giảm từ 83,5% của baseline.
- **MedAPE 9,0%:** một xe "điển hình" chỉ lệch 9%. Thấp hơn MAPE nhiều, nghĩa là **đa số xe đoán tốt**, chỉ một nhóm nhỏ bị sai rất nặng kéo trung bình lên (chủ yếu xe rất rẻ và xe sang, xem slide 27, 33).
- **MAE 102 triệu:** trung bình lệch khoảng 102 triệu đồng.
- **RMSE 372 triệu, gấp khoảng 3,6 lần MAE:** vì RMSE phóng đại lỗi lớn, tỉ lệ này cho thấy có **một số xe bị đoán sai hàng tỷ đồng**, chủ yếu là xe sang.
- **R² (log) 0,891:** mô hình giải thích khoảng 89% biến động của log giá. 11% còn lại đến từ những gì dữ liệu không có: phiên bản, trang bị, tình trạng thực tế, thương lượng.
- **Lệch ≤ 20%: 80%:** **4 trên 5 xe** được định giá sát trong khoảng ±20%.

**Vì sao baseline đoán bừa vẫn đúng 26% (≤ 20%)?** Baseline luôn đoán khoảng 437 triệu (trung vị); nhiều xe có giá quanh mức này nên trúng ngẫu nhiên. Đây là lý do chỉ số này phải đọc cạnh baseline.

**Hai bản Random Forest gần như trùng nhau.** Khác biệt lớn nhất là **thời gian**: 143 giây (Python, một lõi) so với 9 giây (C/Cython, nhiều lõi).

**Câu nói gợi ý:** "Random Forest đạt MAPE 15,5%, tức mức tốt theo thang tham khảo, giảm từ 83,5% của baseline và tốt hơn Ridge 3 điểm %. Bốn trên năm xe được định giá lệch không quá 20%. MedAPE chỉ 9% cho thấy đa số xe được đoán tốt; một nhóm nhỏ xe sai nặng kéo trung bình lên."

---

## Slide 27 – Sai số theo phân khúc giá

**Mục đích:** xem mô hình tốt và kém ở đâu, thay vì chỉ một con số trung bình.

**Trên slide có gì:**
- Hình: MAPE của Ridge, RF thư viện, RF tự cài đặt ở 5 phân khúc (số tin test ghi dưới mỗi phân khúc).
- Ba thẻ: ~11%, 35%, 27%.

| Phân khúc | % dữ liệu | Ridge | RF thư viện | RF tự cài đặt |
|---|---|---|---|---|
| < 200 triệu | 14% | 43,0% | 34,7% | 35,6% |
| 200-500 triệu | 42% | 13,9% | 11,7% | 11,6% |
| 500-1.000 triệu | 33% | 12,6% | 10,9% | 10,8% |
| 1-2 tỷ | 8% | 16,7% | 15,7% | 15,8% |
| > 2 tỷ | 3% | 34,3% | 27,0% | 30,4% |

**Giải thích chi tiết:**

**Phân khúc giữa (200 triệu - 1 tỷ, khoảng 75% thị trường): sai khoảng 11%.** Đủ tốt để tham khảo giá.

**Xe dưới 200 triệu: sai 35%.** Ba lý do:
1. Giá thấp nên chênh vài chục triệu (do tình trạng thực tế, thương lượng) đã là phần trăm lớn. Xe 100 triệu đoán 135 triệu là sai 35%.
2. Xe đời cũ rất khác nhau về tình trạng (đâm đụng, ngập nước, bảo dưỡng) mà dữ liệu không có.
3. Vẫn còn sót tin ghi giá trả trước (slide 33).

**Xe trên 2 tỷ: sai 27%.** Chỉ 3% dữ liệu, và giá xe sang phụ thuộc nhiều vào **phiên bản, trang bị** (cùng là Mercedes S-Class nhưng S450 và S680 chênh vài tỷ), mà dữ liệu không có.

**Random Forest tốt hơn Ridge ở mọi phân khúc.** Bản tự viết lệch nhiều nhất ở xe trên 2 tỷ (30,4% so với 27,0%), nơi ít mẫu nên việc chia 32 bin và lá lớn hơn ảnh hưởng nhiều hơn.

**Câu nói gợi ý:** "Mô hình tốt ở phân khúc giữa, chiếm 75% thị trường, sai khoảng 11%. Hai đầu thang giá khó hơn: xe rẻ vì giá thấp nên lệch ít đã là phần trăm lớn, xe sang vì ít dữ liệu và thiếu thông tin phiên bản."

---

## Slide 28 – Dự đoán so với giá thật

**Mục đích:** nhìn trực quan chất lượng dự đoán trên từng xe.

**Trên slide có gì:** hai biểu đồ chấm (Ridge xanh, RF cam) và 4 gạch đầu dòng.

**Giải thích chi tiết:**

**Cách đọc biểu đồ:**
- Mỗi chấm là **một xe** trong tập test.
- Trục ngang: **giá thật**; trục dọc: **giá dự đoán**.
- **Đường chéo đen:** dự đoán đúng hoàn toàn (giá đoán = giá thật).
- **Vùng xám:** ±20% quanh đường chéo.
- Hai trục dùng **thang log** để thấy được cả xe 50 triệu lẫn xe 10 tỷ. Trên thang log, khoảng cách từ chấm tới đường chéo chính là **sai số phần trăm**.

**Nhận xét:**
- Chấm của RF **tụ sát** đường chéo hơn Ridge.
- Chấm phân bố **đều hai bên** đường chéo, không lệch hẳn về một phía. Nghĩa là mô hình **không đoán lệch hệ thống** (không có xu hướng luôn đoán cao hay luôn đoán thấp).
- Các chấm xa đường chéo nhất nằm ở **hai đầu**: xe rất rẻ và xe sang.

**Ghi chú:** giá dự đoán = `exp(dự đoán log giá)`. Về mặt thống kê, đây là ước lượng **trung vị** của giá, hơi thấp hơn giá trung bình một chút. Điều này phù hợp với MAPE nên nhóm không hiệu chỉnh.

**Câu nói gợi ý:** "Mỗi chấm là một xe; chấm càng sát đường chéo thì đoán càng đúng. Random Forest tụ sát đường chéo hơn Ridge, và các chấm phân bố đều hai bên nên mô hình không đoán lệch hệ thống."

---

## Slide 29 – Chênh lệch có ý nghĩa thống kê không? (Bootstrap)

**Mục đích:** chứng minh RF tốt hơn Ridge là thật, không phải do may mắn.

**Trên slide có gì:**
- Hình: MAPE của 3 mô hình kèm khoảng tin cậy 95% (đường ngang): Ridge 18,5% (17,0-20,3), RF thư viện 15,4% (14,2-17,5), RF tự cài đặt 15,6% (14,4-17,6).
- Thẻ xanh: RF tốt hơn Ridge 3,0 điểm %, KTC 95% 2,1 → 4,0, không chứa 0 → có ý nghĩa.
- Thẻ nhạt: RF tự cài đặt − thư viện 0,19 điểm %, KTC 95% −0,04 → 0,46, chứa 0 → ngang nhau.
- Thẻ vàng: quy tắc đọc.

**Giải thích chi tiết:**

**Vấn đề:** MAPE 15,5% được đo trên 2.788 xe cụ thể. Nếu tình cờ lấy 2.788 xe khác, con số có thể là 15,1% hay 16,0%. Vậy RF hơn Ridge 3 điểm % là **thật**, hay chỉ do tập test này tình cờ có lợi cho RF?

**Khoảng tin cậy 95%** là khoảng mà chỉ số sẽ rơi vào trong 95% số lần nếu ta đánh giá lại trên nhiều tập dữ liệu khác nhau.

**Cách tính bằng bootstrap:**
1. Từ 2.788 xe test, bốc ngẫu nhiên 2.788 xe **có hoàn lại**, được một "tập test giả".
2. Tính MAPE trên tập giả này.
3. Lặp lại **1.000 lần**, được 1.000 giá trị MAPE.
4. Xếp 1.000 giá trị từ nhỏ đến lớn, bỏ 2,5% thấp nhất và 2,5% cao nhất. Khoảng còn lại là **khoảng tin cậy 95%**.

**Đọc hình:** chấm là MAPE, đường ngang là khoảng tin cậy. Khoảng của Ridge và RF chồng nhau một chút (17,0-20,3 và 14,2-17,5).

**Vì sao không kết luận từ việc hai khoảng chồng nhau?** Cách nhìn hai khoảng riêng rẽ **quá khắt khe**, vì nó bỏ qua việc hai mô hình được chấm trên **cùng các xe**. Một xe khó thì cả hai mô hình cùng sai nhiều; một xe dễ thì cả hai cùng đúng.

**Bootstrap ghép cặp (cách đúng):** trong **mỗi** lần bốc, tính **hiệu MAPE** của hai mô hình **trên cùng các xe đó**. Lặp 1.000 lần, được khoảng tin cậy 95% của **hiệu**.

**Quy tắc đọc:**
- Khoảng của hiệu **không chứa 0** → chênh lệch **có ý nghĩa thống kê** (là thật).
- Khoảng của hiệu **chứa 0** → chênh lệch có thể chỉ là ngẫu nhiên.

**Kết quả:**
- **Ridge − RF:** khoảng 2,1 đến 4,0 điểm %, nằm hoàn toàn trên 0 → **RF tốt hơn Ridge thật sự**, khoảng 3 điểm %.
- **RF tự viết − RF thư viện:** khoảng −0,04 đến 0,46, **chứa 0** → hai bản **không khác nhau có ý nghĩa**.

**Câu nói gợi ý:** "Để biết chênh lệch là thật hay do may mắn, nhóm dùng bootstrap ghép cặp: bốc lại tập test 1.000 lần, mỗi lần tính hiệu MAPE của hai mô hình trên cùng các xe. Hiệu giữa Ridge và Random Forest nằm trong khoảng 2,1 đến 4,0 điểm %, không chứa 0, nên Random Forest tốt hơn thật. Hiệu giữa hai bản Random Forest chứa 0, nên hai bản ngang nhau."

**Câu hỏi có thể gặp:**
- *"Bootstrap ghép cặp khác gì nhìn hai khoảng tin cậy chồng nhau?"* → "Bootstrap ghép cặp tính hiệu trên cùng các xe nên loại được phần biến động chung (xe khó thì cả hai cùng sai). Nhìn hai khoảng chồng nhau bỏ qua điều này nên quá khắt khe."
- *"Khoảng tin cậy 95% nghĩa là gì?"* → "Nếu đánh giá lại trên nhiều tập dữ liệu khác, chỉ số sẽ rơi vào khoảng này trong khoảng 95% số lần."

---

## Slide 30 – Đặc trưng nào quyết định giá? Hai cách đo

**Mục đích:** diễn giải mô hình: yếu tố nào ảnh hưởng giá nhiều nhất.

**Trên slide có gì:**
- **Panel trái (xám) – Impurity:** % tổng mức giảm sai số khi học (train).
- **Panel phải (cam) – Permutation:** MAPE tăng thêm (điểm %) khi xáo trộn đặc trưng trên tập test.
- Ba thẻ: Tuổi xe đứng đầu; Hộp số hạng 2 → 4; Hãng hạng 3 → 2.

| Đặc trưng | Impurity (%) | Permutation (MAPE tăng, điểm %) | Hạng (impurity → permutation) |
|---|---|---|---|
| Tuổi xe | 31,0 | 43,2 | 1 → 1 |
| Hãng | 15,8 | 19,7 | 3 → 2 |
| Kiểu dáng | 7,4 | 11,3 | 5 → 3 |
| Hộp số | 17,7 | 11,0 | 2 → 4 |
| Dòng xe | 12,8 | 8,8 | 4 → 5 |
| Nhiên liệu | 3,1 | 5,5 | 7 → 6 |
| Số chỗ | 2,7 | 4,6 | 8 → 7 |
| Số km | 5,4 | 3,7 | 6 → 8 |
| Số km/năm, xuất xứ, tình trạng, cờ km điền | ≤ 2,5 | ≤ 0,6 | cuối |

**Giải thích chi tiết:**

**Cách 1 – Impurity (mức giảm sai số):**
- Cộng gain mà mỗi đặc trưng mang lại ở mọi nút của mọi cây khi học. Đặc trưng nào được dùng để chia nhiều và chia hiệu quả thì quan trọng.
- Với cột phân loại bị one-hot thành nhiều cột (hãng thành 28 cột), cộng độ quan trọng của mọi cột thuộc cùng đặc trưng gốc.
- **Điểm yếu:**
  - Tính trên **train**, kể cả những phép chia chỉ học thuộc nhiễu.
  - **Bị lệch khi đặc trưng tương quan:** nếu hai đặc trưng mang trùng thông tin, cây chọn cái nào để chia phần nhiều là ngẫu nhiên, và độ quan trọng bị chia theo cách đó (Strobl và cộng sự, 2007).

**Cách 2 – Permutation importance (xáo trộn):**
- Ý tưởng: "nếu thông tin này bị phá hỏng thì mô hình kém đi bao nhiêu?"
- Cách làm: lấy tập test, **xáo trộn ngẫu nhiên** một cột (ví dụ cột tuổi xe), giữ nguyên các cột khác, rồi dự đoán lại và xem **MAPE tăng bao nhiêu**. Lặp 5 lần lấy trung bình.
- Xáo trộn phá vỡ quan hệ giữa cột đó và giá nhưng giữ nguyên phân phối của cột.
- Đo trên **đặc trưng gốc** (xáo trộn cả cột dòng xe rồi mới mã hóa), nên không phải cộng các cột one-hot.
- Đo trên **tập test**, theo đúng thước đo chính (MAPE).

**Kết luận:**
1. **Tuổi xe** quan trọng nhất ở cả hai cách: xáo trộn tuổi xe làm MAPE tăng **43 điểm %**. Khấu hao là yếu tố lớn nhất quyết định giá xe cũ.
2. **Hộp số tụt từ hạng 2 xuống hạng 4.** Xe số sàn thường là xe đời cũ, nên hộp số và tuổi xe mang **trùng thông tin**. Impurity "chia điểm" cho hộp số vì cây hay dùng nó để chia, nhưng khi xáo trộn hộp số, tuổi xe vẫn giữ được phần thông tin chung đó, nên MAPE không tăng nhiều.
3. **Hãng lên hạng 2:** mức giá chung của thương hiệu là thông tin mà đặc trưng khác không thay thế được. Dòng xe xếp sau hãng vì một phần thông tin của nó đã có trong hãng, kiểu dáng, số chỗ.
4. **Tình trạng (mới/cũ), cờ km điền, xuất xứ** gần như bằng 0: tình trạng mới/cũ đã nằm trong tuổi = 0 và km = 0.

**Lưu ý khi diễn giải:** độ quan trọng đo mức **đóng góp vào dự đoán**, không phải **tác động nhân quả**. Hộp số sàn không "làm" xe rẻ; nó chỉ là dấu hiệu của xe cũ, phân khúc thấp. Ngoài ra, xáo trộn từng cột độc lập có thể tạo tổ hợp không thực tế (xe 0 tuổi chạy 200.000 km), nên con số dùng để **xếp hạng**.

**Câu nói gợi ý:** "Nhóm đo độ quan trọng bằng hai cách. Tuổi xe đứng đầu ở cả hai. Đáng chú ý là hộp số đứng thứ hai theo impurity nhưng tụt xuống thứ tư theo permutation, vì xe số sàn thường là xe cũ, nên thông tin của hộp số phần lớn đã có trong tuổi xe."

**Câu hỏi có thể gặp:**
- *"Vì sao hộp số quan trọng vậy?"* → "Theo impurity thì cao, nhưng permutation cho thấy phần lớn là thông tin trùng với tuổi xe. Đây là lý do nhóm kiểm tra lại bằng permutation importance."

---

## Slide 31 – Đường khấu hao

**Mục đích:** cho thấy cụ thể RF học được điều gì mà Ridge không học được.

**Trên slide có gì:** ba biểu đồ cho Toyota Vios, Ford Ranger, Mercedes C-Class: giá dự đoán theo tuổi xe của Ridge (xanh) và RF (cam), cùng các chấm xám là tin thật.

**Giải thích chi tiết:**

**Cách làm:** giữ nguyên mọi thuộc tính của một mẫu xe (lắp ráp trong nước, số tự động, 5 chỗ), chỉ thay đổi tuổi xe từ 0 đến 15 năm, giả định chạy 15.000 km mỗi năm (tuổi 0 là xe mới, 0 km). Rồi xem hai mô hình dự đoán giá bao nhiêu.

**Ridge (xanh):** ba đường có **cùng một hình dạng**, chỉ dịch lên xuống theo mức giá của dòng xe. Lý do: Ridge cộng các hiệu ứng; trên thang log, nó giả định **mọi xe mất giá cùng một tỉ lệ % mỗi năm**, dù là Vios hay Mercedes.

**Random Forest (cam):**
- Đường dạng **bậc thang** (vì cây chia tuổi xe theo ngưỡng).
- Quan trọng hơn: **hình dạng khác nhau giữa các dòng xe**. Mercedes C-Class mất giá **rất nhanh** trong 3-4 năm đầu (từ khoảng 1,7 tỷ xuống khoảng 1 tỷ), còn Vios và Ranger mất giá chậm và đều hơn.

**Đây là "tương tác":** tác động của tuổi xe lên giá **phụ thuộc vào** dòng xe. Mô hình cộng tuyến tính như Ridge không biểu diễn được điều này; cây thì làm được tự nhiên, vì nó có thể hỏi "là Mercedes?" rồi mới hỏi "tuổi ≤ 3?".

**Chấm xám:** tin thật của cùng dòng xe ở mọi phiên bản, mọi số km. Chúng phân tán rộng theo chiều dọc: cùng tuổi nhưng giá chênh nhiều. Đó là phần giá mà dữ liệu không giải thích được (phiên bản, trang bị, tình trạng).

**Câu nói gợi ý:** "Khi chỉ thay đổi tuổi xe, Ridge cho mọi dòng xe cùng một dạng đường khấu hao. Random Forest học được rằng Mercedes mất giá rất nhanh trong 3-4 năm đầu, khác hẳn Vios. Đây là tương tác giữa dòng xe và tuổi xe, và là lý do Random Forest chính xác hơn 3 điểm %."

---

## Slide 32 – Thí nghiệm log giá và xử lý mất cân bằng

**Mục đích:** kiểm chứng hai quyết định quan trọng bằng số liệu: dùng log giá, và có nên cân bằng dữ liệu không.

**Trên slide có gì:**
- **Panel trái:** MAPE tổng (CV trên train) của 5 phương án.
- **Panel phải:** MAPE theo 5 phân khúc của 5 phương án.
- Ba thẻ: Log giá; Oversampling; Undersampling.

| Phương án | Cỡ train mỗi fold | MAPE | < 200 tr | 200-500 | > 2 tỷ |
|---|---|---|---|---|---|
| Giá gốc | 8.919 | 19,6% | 51,3% | 15,8% | 22,5% |
| **Log giá (chọn)** | 8.919 | **16,2%** | 35,7% | 12,8% | 27,4% |
| Log + trọng số mẫu | 8.919 | 16,3% | 34,9% | 13,6% | 24,1% |
| Log + Oversampling | 9.830 | 16,1% | 36,0% | 12,8% | 24,5% |
| Log + Undersampling | 6.925 | 16,8% | 35,5% | 14,3% | 26,7% |

**Giải thích chi tiết:**

**Cách đánh giá:** 5-fold CV phân tầng **chỉ trên tập train**. Việc cân bằng chỉ áp dụng cho **phần train của từng fold**; phần validation **giữ nguyên phân phối thật** (vì ngoài đời dữ liệu cũng mất cân bằng như vậy).

**Vì sao dùng CV chứ không dùng OOB?** Khi oversampling, bản sao của một xe có thể nằm trong bootstrap của một cây, còn bản gốc là mẫu "ngoài túi" của chính cây đó. OOB sẽ chấm trên xe mà cây **đã thấy** (qua bản sao), cho điểm đẹp giả tạo. CV tách validation **trước** khi nhân bản nên không gặp vấn đề này.

**Thí nghiệm 1 – Log giá:**
- MAPE giảm từ **19,6% xuống 16,2%**. Cải thiện mạnh nhất ở xe dưới 200 triệu (51% → 36%).
- Lý do: học trên giá gốc thì sai số bình phương bị xe đắt chi phối (sai 500 triệu ở xe 5 tỷ "nặng" hơn nhiều so với sai 50 triệu ở xe 100 triệu), nên mô hình bỏ qua sai số tương đối ở xe rẻ.
- Đổi lại, giá gốc tốt hơn ở xe trên 2 tỷ (22,5% so với 27,4%), cũng vì lý do đó.
- Với thước đo chính là MAPE, **chọn log giá**.

**Thí nghiệm 2 – Ba kỹ thuật cân bằng:**

| Kỹ thuật | Cách làm | Kết quả |
|---|---|---|
| **Trọng số mẫu** | Xe ở phân khúc hiếm được tính "nặng" hơn khi học: trọng số = 1/√(tần suất phân khúc) | MAPE tổng giữ nguyên (16,3%); xe > 2 tỷ giảm 27,4% → 24,1%; nhưng phân khúc 200-500 triệu tăng 12,8% → 13,6% |
| **Random Oversampling** | Nhân bản ngẫu nhiên xe ở phân khúc hiếm đến ít nhất 25% quy mô phân khúc lớn nhất | MAPE tổng 16,1%; xe > 2 tỷ giảm còn 24,5%; các phân khúc khác gần như không đổi |
| **Random Undersampling** | Bỏ bớt xe ở phân khúc đông, mỗi phân khúc giữ tối đa 8 lần phân khúc hiếm nhất | Bỏ khoảng 22% dữ liệu; MAPE tổng tăng lên 16,8%; gần như không giúp xe sang |

**Nhận xét:**
- Cân bằng **không thay đổi MAPE tổng**, nhưng **giúp phân khúc hiếm** khoảng 3 điểm %, vì mô hình "nhìn thấy" xe sang nhiều hơn khi học.
- Undersampling kém vì **bỏ dữ liệu thật thì mất thông tin**.
- **Giới hạn:** dù cân bằng, xe trên 2 tỷ vẫn sai gấp đôi phân khúc giữa. Nguyên nhân chính là **thiếu thông tin** (phiên bản, trang bị), không chỉ do ít mẫu. Nhân bản dữ liệu không tạo ra thông tin mới.

**Quyết định:** mô hình cuối **học trên log giá, không cân bằng**, vì thước đo chính không đổi và mô hình đơn giản hơn. Nếu ứng dụng **ưu tiên định giá xe sang**, nên dùng **oversampling** (chỉ trên tập train).

**Câu nói gợi ý:** "Hai quyết định được kiểm chứng bằng CV trên train. Log giá giảm MAPE từ 19,6% xuống 16,2%. Trọng số mẫu và oversampling không đổi MAPE tổng nhưng giảm sai số xe sang khoảng 3 điểm %; undersampling bỏ dữ liệu nên kém hơn. Mô hình cuối dùng log giá, không cân bằng."

**Câu hỏi có thể gặp:**
- *"Vì sao oversampling không giúp nhiều cho xe trên 2 tỷ?"* → "Nhân bản chỉ lặp lại thông tin đã có. Sai số xe sang chủ yếu do thiếu thông tin phiên bản, trang bị, nên nhân bản không giải quyết được."
- *"Vì sao không cân bằng trước khi chia train/test?"* → "Vì bản sao của cùng một xe có thể nằm ở cả train và validation, làm điểm cao giả tạo. Cân bằng chỉ làm trong phần train của từng fold."

---

## Slide 33 – Hai nguồn sai lệch: tin đăng lại và nhãn sai còn sót

**Mục đích:** nêu trung thực các yếu tố làm con số đánh giá lệch, theo hai chiều.

**Trên slide có gì:**
- **Bảng trái:** MAPE (CV) khi chia ngẫu nhiên 16,1% và khi chia theo nhóm 16,7%.
- **Thẻ xanh:** Ước lượng thận trọng 16-16,5%; 14% tin test có bản sao trong train.
- **Bảng phải:** 5 xe bị đoán sai nhiều nhất.

**Giải thích chi tiết:**

**A. Tin đăng lại → con số hơi LẠC QUAN.**
- Đã loại tin trùng **hoàn toàn** ở slide 10, nhưng cùng một xe có thể được **đăng lại với giá chênh nhẹ**, nên vẫn còn hai dòng gần giống nhau.
- Khi chia ngẫu nhiên, một bản rơi vào train, bản kia vào test. Random Forest với lá nhỏ chỉ cần "nhớ" giá của chính xe đó là đoán đúng.
- **Kiểm tra trên test:** 391 tin test (14%) có một tin train **giống hệt mọi đặc trưng kể cả số km**. Trên nhóm này RF sai 10,9%; trên nhóm còn lại sai 16,2%.
- **Kiểm tra bằng CV chia theo nhóm (`StratifiedGroupKFold`):** mọi tin giống hệt nhau về đặc trưng luôn nằm **cùng một phía** (cùng train hoặc cùng validation). MAPE tăng từ **16,1% lên 16,7%** (+0,5 điểm %), rõ nhất ở xe dưới 200 triệu (35,7% → 38,0%).
- **Kết luận:** mức lạc quan **có nhưng nhỏ**, không đổi kết luận nào. Ước lượng thận trọng cho một xe hoàn toàn mới: **16-16,5%**.

**B. Nhãn sai còn sót → con số hơi BI QUAN.**

| Xe | Tình trạng | Giá rao (triệu) | Dự đoán (triệu) |
|---|---|---|---|
| Hyundai Starex 2023 | Đã dùng | 35 | 655 |
| Toyota 4 Runner 2025 | Đã dùng | 115 | 819 |
| Hyundai Accent 2026 | Mới | 90 | 464 |
| Mitsubishi Xforce 2025 | Đã dùng | 170 | 612 |
| Ford Ranger 2024 | Đã dùng | 225 | 616 |

- Các xe này đều **đời 2023-2026** nhưng rao chỉ 35-225 triệu. Một chiếc Accent 2026 **mới** không thể giá 90 triệu. Gần như chắc chắn đây là **giá trả trước** lọt qua luật lọc ở slide 12 (vì nhóm hãng-dòng-năm có dưới 3 xe nên không áp dụng được).
- **Mô hình đoán 460-650 triệu mới là hợp lý**; chính nhãn sai.
- Những tin này làm MAPE, nhất là phân khúc dưới 200 triệu, bị **đội lên**. Sai số thật của mô hình trên tin có giá đúng thấp hơn con số báo cáo.

**Câu nói gợi ý:** "Có hai yếu tố làm lệch con số theo hai chiều. Tin đăng lại làm điểm hơi lạc quan: chia theo nhóm thì MAPE tăng 0,5 điểm %, ước lượng thận trọng là 16-16,5%. Ngược lại, nhiều xe bị đoán sai nặng nhất thực ra là tin ghi giá trả trước còn sót, ở đó mô hình đoán hợp lý hơn giá rao."

---

## Slide 34 – Lưu mô hình và dự đoán từ thông tin thô

**Mục đích:** cho thấy mô hình dùng được trong thực tế, không chỉ trong notebook.

**Trên slide có gì:**
- **Bảng trái:** các file đã lưu trong thư mục `model/`.
- **Bảng phải:** ví dụ dự đoán: Toyota Vios 2018, 80.000 km → RF thư viện 303, RF tự cài đặt 303, Ridge 281 triệu; Ford Ranger 2021 không rõ km → 515 / 536 / 596 triệu.
- Thẻ vàng: cách xử lý km không rõ và dòng xe chưa gặp.

**Giải thích chi tiết:**

**Các file:**

| File | Nội dung |
|---|---|
| `random_forest_sklearn.joblib` | Rừng thư viện 300 cây đã huấn luyện |
| `random_forest_scratch.npz` | Các cây và ngưỡng bin của rừng tự viết, lưu dạng mảng NumPy (không phụ thuộc code trong notebook) |
| `preprocessor_rf.joblib` | Bộ mã hóa one-hot đã học trên train |
| `metadata.json` | Bảng gộp nhãn hãng/dòng, trung vị km theo năm, tham số, metric |
| `price_model.py` | Hàm `load_model()` và `predict_price()` |

**`predict_price` hoạt động thế nào?** Người dùng chỉ cần đưa **thông tin thô** như trên tin đăng (hãng "Toyota", dòng "Vios", năm 2018, 80.000 km…). Hàm tự làm lại các bước như lúc huấn luyện:
- Tính tuổi xe, km/năm.
- **Xe đã dùng không rõ km:** điền trung vị km theo năm sản xuất, đánh dấu `mileage_missing = 1` (như Ford Ranger trong ví dụ).
- **Dòng xe chưa gặp:** lùi về "<hãng> - dòng khác"; hãng chưa gặp lùi về nhóm cao cấp / phổ thông.
- Mã hóa one-hot rồi dự đoán, lấy `exp()` ra triệu đồng.

**Kiểm tra:** nạp lại mô hình và dự đoán trên tập test cho kết quả **trùng với notebook** đến khoảng 10⁻¹¹ triệu đồng, tức giống hệt.

**Câu nói gợi ý:** "Mô hình được lưu thành file. Hàm predict_price nhận thông tin thô của xe như trên tin đăng và tự làm lại các bước xử lý như lúc huấn luyện. Ví dụ Toyota Vios 2018 chạy 80.000 km được định giá khoảng 303 triệu."

---

## Slide 35 – Kết luận, hạn chế và hướng phát triển

**Mục đích:** tóm tắt và kết thúc.

**Trên slide có gì:**
- Ba ô: 15,5% (MAPE RF, 80% xe lệch ≤ 20%); +3 điểm % (tốt hơn Ridge, có ý nghĩa thống kê); ≈ thư viện (rừng tự cài đặt 15,7%, kiểm chứng ở mức cây và rừng).
- Khung Hạn chế và khung Hướng phát triển.
- Lời cảm ơn.

**Giải thích chi tiết:**

**Kết quả chính:**
1. Hoàn thành quy trình **từ đầu đến cuối**: thu thập 14.835 tin → làm sạch còn 13.937 → huấn luyện, đánh giá, diễn giải → đóng gói mô hình.
2. **Random Forest** đạt **MAPE 15,5%**, MedAPE 9%, R² 0,891, 80% xe lệch không quá 20%.
3. **Tốt hơn Ridge 3 điểm %, có ý nghĩa thống kê.** Phần chênh là đóng góp của quan hệ phi tuyến và tương tác.
4. **Bản tự cài đặt** được kiểm chứng ở mức một cây và cả rừng, MAPE 15,7%, không khác bản thư viện có ý nghĩa.
5. Mọi quyết định (mã hóa, tham số, log giá, cân bằng) đều kiểm chứng bằng CV/OOB trên train.

**Hạn chế (nói thẳng, không né):**
- **Giá rao bán, không phải giá giao dịch:** luôn có phần thương lượng mà mô hình không biết.
- **Thiếu thông tin quan trọng:** phiên bản xe, số đời chủ, hạn đăng kiểm (có trên trang nhưng chưa lấy, slide 5). Đây là nguyên nhân chính của sai số cao ở xe sang.
- **Còn sót giá trả trước** (slide 33) và **có tin đăng lại** (ước lượng thận trọng 16-16,5%).
- **Mẫu dữ liệu:** chỉ 750 trang mới nhất tại tháng 10/2026; xe trên 10 tỷ đã bị loại nên mô hình không áp dụng cho siêu xe.

**Hướng phát triển:**
- Crawl thêm **tiêu đề, mô tả tin**: trích phiên bản xe, lọc giá trả trước theo từ khóa ("trả trước", "góp", "vay", "cọc").
- Dùng **chia train/test theo nhóm** làm cách đánh giá chính.
- Thử **Gradient Boosting**, có thể dùng lại lớp cây đã tự cài đặt.
- Làm **giao diện web** cho người dùng nhập thông tin xe và nhận giá tham khảo.

**Câu nói gợi ý:** "Tóm lại, Random Forest dự đoán giá rao với sai số trung bình 15,5%, tốt hơn Ridge 3 điểm % một cách có ý nghĩa thống kê, và bản tự cài đặt cho kết quả tương đương thư viện. Hạn chế chính là dữ liệu thiếu phiên bản xe và còn sót giá trả trước; hướng phát triển là thu thập thêm tiêu đề và mô tả tin. Nhóm em xin cảm ơn thầy cô đã lắng nghe."

---

# PHỤ LỤC

## A. Bảng thuật ngữ

| Thuật ngữ | Giải thích ngắn |
|---|---|
| **Hồi quy** | Bài toán dự đoán một con số liên tục (giá) |
| **Train / Test** | Tập để học / tập để chấm điểm cuối, chỉ dùng một lần |
| **Rò rỉ dữ liệu** | Mô hình vô tình thấy thông tin của tập chấm điểm, làm điểm đẹp giả tạo |
| **Cross-validation (CV)** | Chia train thành K phần, lần lượt lấy mỗi phần làm validation, lấy trung bình |
| **Chia phân tầng** | Chia sao cho mỗi nhóm (phân khúc giá) có cùng tỉ lệ ở các tập |
| **Bootstrap** | Lấy mẫu ngẫu nhiên có hoàn lại, cùng kích thước tập gốc |
| **OOB (out-of-bag)** | Khoảng 37% mẫu không nằm trong bootstrap của một cây; dùng để ước lượng sai số |
| **CART** | Thuật toán cây chia dữ liệu bằng câu hỏi có/không, chọn phép chia giảm sai số nhiều nhất |
| **Gain** | Mức giảm tổng bình phương sai số khi chia một nút |
| **Phương sai cao** | Mô hình thay đổi nhiều khi dữ liệu thay đổi ít; dấu hiệu học thuộc |
| **Siêu tham số** | Tham số chọn trước khi huấn luyện (số cây, độ sâu…) |
| **One-hot** | Mỗi nhãn phân loại thành một cột 0/1 |
| **Histogram (trong cây)** | Gom giá trị vào các ngăn để tìm ngưỡng chia nhanh |
| **Log giá** | ln(giá); làm sai số tính theo phần trăm |
| **Skewness** | Độ lệch của phân bố; 0 là cân đối |
| **Thiếu có cấu trúc** | Giá trị thiếu có nguyên nhân rõ (xe mới không có ô km) |
| **Mất cân bằng (hồi quy)** | Mật độ dữ liệu không đều theo vùng giá |
| **Oversampling / Undersampling** | Nhân bản mẫu hiếm / bỏ bớt mẫu đông |
| **Trọng số mẫu** | Cho mẫu hiếm "nặng" hơn khi học |
| **MAPE / MedAPE** | Trung bình / trung vị sai số phần trăm |
| **MAE / RMSE** | Sai số tuyệt đối trung bình / căn trung bình bình phương sai số |
| **R²** | Tỉ lệ biến động được mô hình giải thích |
| **Baseline** | Mô hình mốc luôn đoán giá trung vị |
| **Khoảng tin cậy 95%** | Khoảng mà chỉ số rơi vào 95% số lần nếu đánh giá lại trên dữ liệu khác |
| **Bootstrap ghép cặp** | Tính hiệu hai mô hình trên cùng các mẫu bốc lại, để kiểm định chênh lệch |
| **Impurity importance** | Độ quan trọng tính bằng tổng gain khi học |
| **Permutation importance** | Độ quan trọng tính bằng mức tăng sai số khi xáo trộn đặc trưng |
| **Tương tác** | Tác động của một đặc trưng phụ thuộc vào đặc trưng khác (khấu hao phụ thuộc dòng xe) |
| **Ridge** | Hồi quy tuyến tính có phạt L2 trên trọng số |

## B. Câu hỏi thường gặp và gợi ý trả lời

1. **Vì sao học trên log giá mà vẫn báo MAPE trên giá thật?**
   Log làm mô hình tối ưu sai số tương đối, rất gần với MAPE. Dự đoán xong lấy `exp()` về giá thật rồi mới tính MAPE, để con số dễ hiểu với người dùng. Thí nghiệm cho thấy log giảm MAPE từ 19,6% xuống 16,2%.

2. **Công thức gain là gì? Vì sao chia 32 bin không mất nhiều thông tin?**
   Gain = S_L²/n_L + S_R²/n_R − S²/n, là mức giảm tổng bình phương sai số khi chia nút. Chia 32 bin: cột one-hot chỉ có 2 giá trị nên không mất gì; cột số chia theo phân vị nên mất rất ít. Kiểm chứng: cây tự viết có số nút và R² gần bằng cây thư viện.

3. **OOB là gì, vì sao khoảng 37% mẫu nằm ngoài bootstrap?**
   OOB là các mẫu không được chọn vào bootstrap của một cây. Xác suất một mẫu không được chọn sau n lần bốc có hoàn lại là (1 − 1/n)ⁿ ≈ e⁻¹ ≈ 0,37.

4. **Bootstrap ghép cặp khác gì nhìn hai khoảng tin cậy chồng nhau?**
   Ghép cặp tính hiệu hai mô hình trên cùng các xe, loại được biến động chung (xe khó thì cả hai cùng sai). Nhìn hai khoảng riêng bỏ qua điều này nên quá khắt khe.

5. **Vì sao oversampling không giúp nhiều cho xe trên 2 tỷ?**
   Nhân bản không tạo thông tin mới. Sai số xe sang chủ yếu do thiếu phiên bản, trang bị.

6. **Vì sao không dùng tập validation riêng?**
   Xe sang ít; CV dùng mọi phần của train làm validation nên ổn định hơn.

7. **Vì sao chọn Random Forest?**
   Bắt được quan hệ phi tuyến và tương tác (slide 31), không cần biến đổi đặc trưng số hay chuẩn hóa, có OOB và độ quan trọng đặc trưng để diễn giải, và cho kết quả tốt hơn Ridge có ý nghĩa thống kê.

8. **Vì sao không so với XGBoost / Gradient Boosting?**
   Đề yêu cầu phân tích kỹ một mô hình; Ridge đủ để trả lời câu hỏi phi tuyến giúp bao nhiêu. Gradient Boosting là hướng phát triển.

9. **Dùng giá để lọc giá trả trước có phải rò rỉ dữ liệu không?**
   Không, vì chỉ loại dòng có đáp án sai (sửa nhãn), không đưa giá vào đặc trưng. Nhóm nêu rõ hệ quả: khi dùng thật, mô hình vẫn gặp các tin như vậy.

10. **Kết quả có tái lập được không?**
    Có. Mọi bước ngẫu nhiên cố định `random_state = 42`; chạy lại ra đúng cùng con số.

11. **Mô hình tốt chưa?**
    MAPE 15,5% nằm trong mức tốt (10-20%), giảm từ 83,5% của baseline; R² 0,89; 80% xe lệch không quá 20%. Sai số tập trung ở hai đầu thang giá, do dữ liệu thiếu phiên bản và tình trạng xe.

12. **Vì sao hộp số lại quan trọng?**
    Theo impurity thì đứng thứ 2, nhưng permutation cho thấy chỉ đứng thứ 4: phần lớn thông tin của hộp số trùng với tuổi xe (xe số sàn thường là xe cũ). Độ quan trọng đo đóng góp vào dự đoán, không phải tác động nhân quả.
