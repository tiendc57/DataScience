"""Dựng báo cáo Word cho đề tài dự đoán giá ô tô.

Chạy: python build_report.py   (thư mục làm việc bất kỳ)
Số liệu lấy từ output đã lưu của src/preprocess_data.ipynb và src/model.ipynb, không chạy lại notebook.
Sau khi tạo file, mở bằng Word và cập nhật mục lục (chuột phải > Update Field) nếu mục lục trống.
"""
import re
import sys
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from latex2mathml.converter import convert as latex_to_mathml
from lxml import etree

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "src" / "figures"
LOGO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "logo_dut.jpeg"
OUT = ROOT / "report" / "Bao_cao_Du_doan_gia_o_to.docx"
XSL = Path(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL")

BLUE = RGBColor(0x07, 0x52, 0x89)
FONT = "Times New Roman"

doc = Document()

# ------------------------------------------------------------------ styles
st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(13)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
pf = st.paragraph_format
pf.line_spacing = 1.3
pf.space_after = Pt(6)
pf.space_before = Pt(0)

for name, size, align in [("Heading 1", 15, WD_ALIGN_PARAGRAPH.CENTER),
                          ("Heading 2", 13.5, WD_ALIGN_PARAGRAPH.LEFT),
                          ("Heading 3", 13, WD_ALIGN_PARAGRAPH.LEFT)]:
    h = doc.styles[name]
    h.font.name = FONT
    h.font.size = Pt(size)
    h.font.bold = True
    h.font.italic = name == "Heading 3"
    h.font.color.rgb = BLUE if name != "Heading 3" else RGBColor(0, 0, 0)
    rpr = h.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), FONT)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    h.paragraph_format.alignment = align
    h.paragraph_format.space_before = Pt(18 if name == "Heading 1" else 12)
    h.paragraph_format.space_after = Pt(12 if name == "Heading 1" else 6)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.line_spacing = 1.15

from docx.enum.style import WD_STYLE_TYPE
for name in ("Chú thích hình", "Chú thích bảng"):
    s = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    s.base_style = st
    s.font.size = Pt(12)
    s.font.italic = True
    s.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s.paragraph_format.space_before = Pt(4)
    s.paragraph_format.space_after = Pt(10)
    if name == "Chú thích bảng":
        s.paragraph_format.keep_with_next = True
        s.paragraph_format.space_before = Pt(8)
        s.paragraph_format.space_after = Pt(4)

# ------------------------------------------------------------------ page
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin, sec.right_margin = Cm(3), Cm(2)
sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)

INLINE = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")


def add_runs(p, text, size=None, color=None, bold=None):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**"):
            add_runs(p, part[2:-2], size, color, True)   # cho phép `code` nằm trong **đậm**
            continue
        if part.startswith("`"):
            r = p.add_run(part[1:-1]); r.font.name = "Consolas"; r.font.size = Pt((size or 13) - 1.5)
        elif part.startswith("*") and len(part) > 2:
            r = p.add_run(part[1:-1]); r.italic = True
        else:
            r = p.add_run(part)
        if size and not part.startswith("`"):
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = color
        if bold:
            r.bold = True
    return p


def para(text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True, **kw):
    p = doc.add_paragraph()
    p.alignment = align
    if indent:
        p.paragraph_format.first_line_indent = Cm(1)
    return add_runs(p, text, **kw)


def bullet(text, level=0):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(3)
    return add_runs(p, text)


def numbered(items):
    for k, t in enumerate(items, 1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(1)
        p.paragraph_format.first_line_indent = Cm(-0.6)
        p.paragraph_format.space_after = Pt(3)
        add_runs(p, f"{k}. " + t)


def h1(t):
    doc.add_heading(t, level=1)


def h2(t):
    doc.add_heading(t, level=2)


def h3(t):
    doc.add_heading(t, level=3)


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def set_cell_margins(table, top=50, bottom=50, left=90, right=90):
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for k, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        e = OxmlElement(f"w:{k}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa"); mar.append(e)
    tblPr.append(mar)


TAB_N = {}
FIG_N = {}
CHAPTER = [0]


def caption_table(text):
    c = CHAPTER[0]
    TAB_N[c] = TAB_N.get(c, 0) + 1
    p = doc.add_paragraph(style="Chú thích bảng")
    r = p.add_run(f"Bảng {c}.{TAB_N[c]}. "); r.bold = True; r.italic = False
    p.add_run(text)


def table(headers, rows, widths, caption=None, bold_rows=(), align=None, font=11.5):
    if caption:
        caption_table(caption)
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_cell_margins(t)
    align = align or ["l"] + ["c"] * (len(headers) - 1)
    amap = {"l": WD_ALIGN_PARAGRAPH.LEFT, "c": WD_ALIGN_PARAGRAPH.CENTER, "r": WD_ALIGN_PARAGRAPH.RIGHT}
    for i, row in enumerate([headers] + rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else amap[align[j]]
            add_runs(p, str(val), size=font, bold=(i == 0 or (i - 1) in bold_rows) or None,
                     color=RGBColor(255, 255, 255) if i == 0 else None)
            if i == 0:
                shade(cell, "075289")
            elif (i - 1) in bold_rows:
                shade(cell, "FFF6CC")
            elif i % 2 == 0:
                shade(cell, "EAF2FA")
    # lặp tiêu đề khi sang trang
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    for col, w in zip(t.columns, widths):
        col.width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def figure(name, width_cm, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(str(FIG / name), width=Cm(width_cm))
    c = CHAPTER[0]
    FIG_N[c] = FIG_N.get(c, 0) + 1
    cp = doc.add_paragraph(style="Chú thích hình")
    r = cp.add_run(f"Hình {c}.{FIG_N[c]}. "); r.bold = True; r.italic = False
    cp.add_run(text)


_xslt = etree.XSLT(etree.parse(str(XSL)))


def equation(latex):
    mml = etree.fromstring(latex_to_mathml(latex).encode())
    omml = _xslt(mml).getroot()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p._p.append(parse_xml(etree.tostring(omml)))


def field(p, instr, placeholder="Nhấn chuột phải, chọn Update Field để cập nhật."):
    def fc(t):
        r = OxmlElement("w:r"); e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t); r.append(e); return r
    p._p.append(fc("begin"))
    r = OxmlElement("w:r"); it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
    r.append(it); p._p.append(r)
    p._p.append(fc("separate"))
    r = OxmlElement("w:r"); tt = OxmlElement("w:t"); tt.text = placeholder; r.append(tt); p._p.append(r)
    p._p.append(fc("end"))


def chapter(n, title):
    CHAPTER[0] = n
    page_break()
    h1(f"CHƯƠNG {n}. {title}")


def front_heading(t):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run(t); r.bold = True; r.font.size = Pt(15); r.font.color.rgb = BLUE


# ================================================================== BÌA
def cover_line(text, size, bold=False, after=0, color=None, italic=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text); r.bold = bold; r.italic = italic; r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color
    return p


cover_line("ĐẠI HỌC ĐÀ NẴNG", 14, True)
cover_line("TRƯỜNG ĐẠI HỌC BÁCH KHOA", 14, True)
cover_line("KHOA <TÊN KHOA>", 14, True, after=4)
cover_line("─────── ✦ ───────", 12, after=24)
if LOGO and LOGO.exists():
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(30)
    p.add_run().add_picture(str(LOGO), width=Cm(3.6))
cover_line("BÁO CÁO ĐỀ TÀI", 16, True, after=4)
cover_line("MÔN KHOA HỌC DỮ LIỆU", 16, True, after=30)
cover_line("DỰ ĐOÁN GIÁ Ô TÔ TRÊN CHỢ TỐT", 22, True, color=BLUE, after=4)
cover_line("BẰNG RIDGE REGRESSION VÀ RANDOM FOREST", 18, True, color=BLUE, after=60)

info = doc.add_table(rows=4, cols=2)
info.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, (k, v) in enumerate([("Giảng viên hướng dẫn:", "<Tên giảng viên>"),
                            ("Sinh viên thực hiện:", "<Họ tên SV 1> – <MSSV>"),
                            ("", "<Họ tên SV 2> – <MSSV>"),
                            ("Lớp học phần:", "<Mã lớp>")]):
    for j, (val, w) in enumerate([(k, 6), (v, 7.5)]):
        c = info.cell(i, j); c.width = Cm(w)
        pp = c.paragraphs[0]; pp.paragraph_format.space_after = Pt(2)
        r = pp.add_run(val); r.font.size = Pt(14); r.bold = j == 0
for _ in range(5):
    doc.add_paragraph()
cover_line("Đà Nẵng, tháng 10 năm 2026", 14, italic=True)

# khung trang bìa
sectPr = doc.sections[0]._sectPr
pgb = parse_xml(
    '<w:pgBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:offsetFrom="page">'
    + "".join(f'<w:{s} w:val="thinThickSmallGap" w:sz="24" w:space="24" w:color="075289"/>'
              for s in ("top", "left", "bottom", "right")) + "</w:pgBorders>")
sectPr.append(pgb)

# sang section mới (không khung, có số trang)
new = doc.add_section(WD_SECTION.NEW_PAGE)
new_pr = new._sectPr
for e in new_pr.findall(qn("w:pgBorders")):
    new_pr.remove(e)
new.footer.is_linked_to_previous = False
fp = new.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
field(fp, "PAGE", "1")
pg = OxmlElement("w:pgNumType"); pg.set(qn("w:start"), "1"); new_pr.append(pg)
doc.sections[0].footer.is_linked_to_previous = False

# ================================================================== MỤC LỤC
front_heading("MỤC LỤC")
field(doc.add_paragraph(), 'TOC \\o "1-3" \\h \\z \\u')
page_break()
front_heading("DANH MỤC HÌNH")
field(doc.add_paragraph(), 'TOC \\h \\z \\t "Chú thích hình,1"')
page_break()
front_heading("DANH MỤC BẢNG")
field(doc.add_paragraph(), 'TOC \\h \\z \\t "Chú thích bảng,1"')
page_break()
front_heading("DANH MỤC TỪ VIẾT TẮT VÀ THUẬT NGỮ")
CHAPTER[0] = 0
table(["Từ viết tắt", "Tiếng Anh", "Ý nghĩa"], [
    ["MAPE", "Mean Absolute Percentage Error", "Sai số phần trăm tuyệt đối trung bình (thước đo chính)"],
    ["MedAPE", "Median Absolute Percentage Error", "Trung vị sai số phần trăm tuyệt đối"],
    ["MAE", "Mean Absolute Error", "Sai số tuyệt đối trung bình (triệu đồng)"],
    ["RMSE", "Root Mean Squared Error", "Căn bậc hai sai số bình phương trung bình"],
    ["R²", "Coefficient of determination", "Hệ số xác định"],
    ["CV", "Cross-validation", "Kiểm định chéo (K-fold)"],
    ["OOB", "Out-of-bag", "Các mẫu không được chọn vào mẫu bootstrap của một cây"],
    ["CART", "Classification and Regression Tree", "Cây phân loại và hồi quy"],
    ["RF", "Random Forest", "Rừng ngẫu nhiên"],
    ["SSE", "Sum of Squared Errors", "Tổng bình phương sai số"],
    ["KTC", "Confidence interval", "Khoảng tin cậy"],
    ["EDA", "Exploratory Data Analysis", "Phân tích khám phá dữ liệu"],
], [2.6, 5.8, 7.6], align=["l", "l", "l"])

# ================================================================== CHƯƠNG 1
chapter(1, "GIỚI THIỆU ĐỀ TÀI")
h2("1.1. Bối cảnh")
para("Thị trường ô tô cũ ở Việt Nam ngày càng sôi động, và phần lớn giao dịch bắt đầu từ các trang rao vặt trực tuyến như Chợ Tốt (`xe.chotot.com`). Người bán thường tự đặt giá theo cảm tính hoặc tham khảo vài tin tương tự, còn người mua khó biết một mức giá rao là hợp lý hay không. Một mô hình ước lượng giá từ các thông tin cơ bản của xe (hãng, dòng xe, năm sản xuất, số km, hộp số, nhiên liệu, kiểu dáng...) giúp cả hai phía có một mốc tham chiếu khách quan.")
para("Đề tài được thực hiện theo yêu cầu của môn Khoa học dữ liệu: xây dựng **một mô hình học máy từ đầu đến cuối**, từ thu thập dữ liệu, tiền xử lý, huấn luyện đến đánh giá bằng các thước đo phù hợp, có áp dụng **kỹ thuật xử lý dữ liệu mất cân bằng**. Các mô hình phải được **tự cài đặt** thuật toán, không chỉ gọi thư viện.")

h2("1.2. Phát biểu bài toán")
para("Đây là bài toán **hồi quy có giám sát**:")
bullet("**Đầu vào:** các thuộc tính của một tin rao bán ô tô: hãng, dòng xe, xuất xứ, tình trạng (mới / đã sử dụng), hộp số, nhiên liệu, kiểu dáng, số chỗ, năm sản xuất, số km đã đi.")
bullet("**Đầu ra:** giá rao bán dự đoán (triệu đồng).")
bullet("**Dữ liệu:** 14.835 tin rao bán ô tô thu thập từ Chợ Tốt ngày 25/10/2026; sau tiền xử lý còn 13.937 tin.")
bullet("**Thước đo chính:** MAPE (sai số phần trăm trung bình), báo cáo kèm theo từng phân khúc giá.")

h2("1.3. Mục tiêu và phạm vi")
numbered([
    "Thu thập dữ liệu tin rao bán ô tô từ Chợ Tốt bằng web scraping.",
    "Làm sạch dữ liệu: xử lý giá trị thiếu, giá trị bất hợp lý, giá giả, giá trả trước, tin trùng; gộp nhãn hiếm; tạo đặc trưng.",
    "Xây dựng hai mô hình học máy cổ điển: **Ridge Regression** (tuyến tính) và **Random Forest** (phi tuyến). Mỗi mô hình có hai bản: dùng thư viện `scikit-learn` và **tự cài đặt bằng NumPy**, rồi kiểm chứng hai bản cho kết quả tương đương.",
    "Đánh giá bằng nhiều thước đo, kiểm định ý nghĩa thống kê của chênh lệch giữa các mô hình.",
    "Thử nghiệm các kỹ thuật xử lý mất cân bằng (trọng số mẫu, oversampling, undersampling) và đánh giá tác động.",
    "Diễn giải mô hình: yếu tố nào quyết định giá xe, xe mất giá theo tuổi như thế nào.",
])
para("**Phạm vi:** giá trong dữ liệu là **giá rao bán**, không phải giá giao dịch thực tế. Dữ liệu là ảnh chụp thị trường tại một thời điểm, không xét biến động giá theo thời gian.")

h2("1.4. Quy trình thực hiện")
para("Đề tài đi theo quy trình chuẩn của một dự án khoa học dữ liệu, mỗi bước tương ứng với một notebook:")
table(["Bước", "Nội dung", "File", "Kết quả"], [
    ["1. Thu thập", "Crawl 750 trang danh sách tin, đọc thuộc tính từng tin", "`crawl_data.ipynb`", "`raw_data_oto.csv` (14.835 dòng, 14 cột)"],
    ["2. Khám phá", "Biểu đồ phân bố, tương quan, giá trị thiếu", "`visualize_raw_data.ipynb`", "Biểu đồ trong `figures/`"],
    ["3. Tiền xử lý", "Làm sạch, điền thiếu, gộp nhãn hiếm, tạo đặc trưng", "`preprocess_data.ipynb`", "`clean_data_oto.csv` (13.937 dòng, 18 cột)"],
    ["4. Mô hình", "Ridge và Random Forest (thư viện + tự cài đặt), đánh giá, thí nghiệm", "`model.ipynb`", "Mô hình đã lưu trong `model/`"],
    ["5. Triển khai", "Nạp mô hình, dự đoán từ thông tin thô của xe", "`model/price_model.py`", "Hàm `predict_price()`"],
], [2.4, 5.6, 4.0, 4.0], caption="Các bước thực hiện đề tài", align=["l", "l", "l", "l"])

h2("1.5. Công cụ sử dụng")
bullet("**Ngôn ngữ:** Python 3, môi trường Jupyter Notebook.")
bullet("**Thu thập dữ liệu:** `requests`, `BeautifulSoup`.")
bullet("**Xử lý và trực quan hóa:** `pandas` 3.0, `NumPy`, `matplotlib`.")
bullet("**Học máy:** `scikit-learn` 1.9 (bản thư viện, dùng làm chuẩn đối chiếu); `NumPy` (bản tự cài đặt); `joblib` để lưu mô hình.")

# ================================================================== CHƯƠNG 2
chapter(2, "THU THẬP DỮ LIỆU")
h2("2.1. Nguồn dữ liệu và phương pháp thu thập")
para("Dữ liệu được thu thập từ chuyên mục mua bán ô tô của Chợ Tốt (`https://xe.chotot.com/mua-ban-oto`) bằng notebook `crawl_data.ipynb`, hoàn tất ngày **25/10/2026**. Quy trình gồm hai tầng:")
numbered([
    "**Duyệt trang danh sách:** lần lượt truy cập 750 trang danh sách tin mới nhất (`?page=1` đến `?page=750`), lấy đường dẫn của từng tin.",
    "**Đọc trang chi tiết:** với mỗi tin, tải trang và đọc các thẻ HTML có thuộc tính `itemprop` tương ứng với từng thuộc tính của xe (riêng giá đọc từ thẻ `name=\"price\"`). Kết quả được ghi nối tiếp vào `raw_data_oto.csv`.",
])
para("Code có cơ chế **chạy tiếp**: các URL đã có trong file được bỏ qua, nên nếu bị ngắt giữa chừng chỉ cần chạy lại. Các tin \"ưu tiên\" lặp lại ở đầu mọi trang cũng chỉ được ghi một lần. Kết quả là **14.835 tin** với 14 cột (số thứ tự, URL và 12 thuộc tính).")

h2("2.2. Thu thập có trách nhiệm")
bullet("Chỉ lấy thông tin công khai trên trang tin rao, không đăng nhập, không lấy thông tin liên hệ của người bán; dữ liệu chỉ dùng cho mục đích học tập.")
bullet("Nghỉ giữa các yêu cầu (0,5 giây giữa các tin, 1 giây giữa các trang) và tự lùi thời gian khi máy chủ trả về mã 403/429, để không gây tải cho máy chủ.")
bullet("Hạn chế kỹ thuật: danh sách tin được tìm bằng một class CSS sinh tự động; khi trang đổi giao diện cần sửa lại bộ chọn.")

h2("2.3. Từ điển dữ liệu")
para("Bảng 2.1 mô tả các cột thu được. Cột *\"Người bán nhập thế nào\"* rất quan trọng cho bước tiền xử lý: cột **chọn từ danh sách** có tập giá trị cố định, viết thống nhất; còn cột **gõ tự do** (số km, giá) là nguồn lỗi nhập liệu chính.")
table(["Cột", "Ý nghĩa", "Người bán nhập", "Sau xử lý"], [
    ["`mileage_v2`", "Số km đã đi", "**gõ tự do** (dạng 109.366)", "số (`mileage_km`)"],
    ["`carorigin`", "Xuất xứ", "chọn từ danh sách, không bắt buộc", "phân loại"],
    ["`condition_ad`", "Tình trạng (Mới / Đã sử dụng)", "chọn từ danh sách", "phân loại"],
    ["`veh_warranty_policy`", "Chính sách bảo hành", "(một giá trị duy nhất)", "bỏ"],
    ["`carbrand`", "Hãng xe", "chọn từ danh sách", "phân loại"],
    ["`carmodel`", "Dòng xe", "chọn theo hãng", "phân loại"],
    ["`mfdate`", "Năm sản xuất", "chọn (có mục \"trước năm 1980\")", "số"],
    ["`gearbox`", "Hộp số", "chọn (3 giá trị)", "phân loại"],
    ["`fuel`", "Nhiên liệu", "chọn (4 giá trị)", "phân loại"],
    ["`cartype`", "Kiểu dáng", "chọn (9 giá trị), không bắt buộc", "phân loại"],
    ["`carseats`", "Số chỗ ngồi", "chọn (có mục \"Khác\"), không bắt buộc", "số"],
    ["`price`", "Giá rao bán (đồng)", "**gõ tự do**", "biến mục tiêu"],
    ["`url`", "Đường dẫn tin", "sinh tự động, chứa quận/huyện và tỉnh", "trích `province`, rồi bỏ"],
], [3.6, 4.2, 5.0, 3.2], caption="Từ điển dữ liệu thô", align=["l", "l", "l", "l"])

h2("2.4. Cơ chế thu thập và hệ quả cho tiền xử lý")
para("Hiểu **cách dữ liệu được tạo ra** giúp biết mỗi loại lỗi đến từ đâu và nên xử lý thế nào:")
table(["Cơ chế", "Hệ quả", "Cách xử lý"], [
    ["Không tìm thấy thẻ của một thuộc tính → ghi chuỗi `\"N/A\"`", "`N/A` là thiếu thật; pandas mặc định tự đổi thành NaN, làm mất dấu vết", "Đọc với `keep_default_na=False`, rồi tự đổi về NaN"],
    ["Trang hiển thị `\"Đang cập nhật\"` khi người bán không chọn xuất xứ", "Cũng là thiếu thật", "Đổi về NaN"],
    ["Danh sách có sẵn mục `\"Khác\"`, `\"Dòng khác\"`, `\"Nước khác\"`", "Là lựa chọn thật của người bán", "Giữ làm nhãn (trừ `carseats = \"Khác\"`)"],
    ["Số km và giá là ô gõ tự do", "Gõ thiếu/thừa số 0, ghi tiền trả trước, giá giả 123.456.789", "Quy tắc kiểm tra ở mục 3.4, 3.5"],
    ["Xe \"Mới\" không có ô số km", "Số km thiếu ở mọi xe mới", "Điền 0 km"],
    ["Bỏ qua URL đã gặp", "Mỗi dòng là một tin khác nhau; dòng trùng nội dung là tin đăng lại", "Loại trùng theo nội dung"],
    ["URL dạng `mua-ban-oto-<quận>-<tỉnh>/<mã>.htm`", "Có thông tin vị trí", "Trích tỉnh/thành"],
    ["Một lần thu thập, 750 trang mới nhất", "Ảnh chụp thị trường tại một thời điểm; giá là giá rao", "Tuổi xe tính theo năm 2026"],
], [5.0, 5.6, 5.4], caption="Cơ chế thu thập dữ liệu và cách xử lý tương ứng", align=["l", "l", "l"], font=11)

# ================================================================== CHƯƠNG 3
chapter(3, "KHÁM PHÁ VÀ TIỀN XỬ LÝ DỮ LIỆU")
para("Chương này trình bày các bước biến dữ liệu thô thành tập dữ liệu sạch cho mô hình (notebook `preprocess_data.ipynb`). Mỗi quyết định đều kèm lý do, và đều xuất phát từ việc **giá là biến cần dự đoán**.")

h2("3.1. Khám phá dữ liệu ban đầu")
para("Dữ liệu thô có 14.835 dòng và 14 cột. Thị trường tập trung vào các hãng phổ thông: Toyota chiếm khoảng 20% số tin, tiếp theo là Ford, VinFast, Kia, Hyundai (Hình 3.1).")
figure("03_top_hang.png", 12.5, "Mười hãng xe có nhiều tin đăng nhất (dữ liệu thô)")
para("Giá rao **lệch phải rất mạnh** (độ lệch skewness = 5,08): đa số xe có giá 200-800 triệu, nhưng có một đuôi dài các xe vài tỷ đến hàng chục tỷ đồng (Hình 3.2). Đặc điểm này ảnh hưởng trực tiếp đến cách chọn biến mục tiêu (mục 3.7).")
figure("04_phan_bo_gia.png", 13, "Phân bố giá rao bán trên thang gốc và thang log")
para("Hai yếu tố có quan hệ rõ nhất với giá là **năm sản xuất** và **số km**: xe càng mới giá càng cao, xe chạy càng nhiều km giá càng thấp, và quan hệ không tuyến tính (xe mất giá nhanh trong những năm đầu). Giá cũng chênh lệch lớn giữa các hãng.")
figure("08_gia_theo_nam.png", 13, "Giá rao theo năm sản xuất")
figure("05_gia_theo_hang.png", 13, "Phân bố giá theo hãng xe")
figure("09_km_gia.png", 11.5, "Quan hệ giữa số km đã đi và giá (mật độ tin đăng)")

h2("3.2. Chuẩn hóa kiểu dữ liệu và giá trị giả")
para("Bảng 3.1 thống kê các giá trị \"giả\" trong dữ liệu thô, tức các chuỗi không phải giá trị thật của thuộc tính:")
table(["Cột", "`N/A` (không có thẻ)", "`Đang cập nhật`", "`Khác`", "Số giá trị khác nhau"], [
    ["mileage_v2", "1.811", "0", "0", "1.995"],
    ["carorigin", "0", "6.012", "0", "11"],
    ["veh_warranty_policy", "0", "0", "0", "1"],
    ["cartype", "4.883", "0", "0", "10"],
    ["carseats", "3.028", "0", "659", "12"],
    ["price", "1", "0", "0", "1.433"],
], [4.0, 3.2, 3.0, 2.0, 3.8], caption="Các giá trị giả trong dữ liệu thô")
bullet("`N/A` và `Đang cập nhật` đều là người đăng **không điền thông tin**, nên được đổi thành giá trị thiếu (NaN). Nếu để nguyên, mô hình sẽ coi \"Đang cập nhật\" là một xuất xứ thật.")
bullet("`Khác` trong `carseats` không đổi ra số được nên coi là thiếu; còn `Dòng khác`, `Kiểu dáng khác` là nhãn có nghĩa nên giữ nguyên.")
bullet("`price`, `mileage_v2`, `carseats` dạng chuỗi `1.095.000.000` được bỏ dấu chấm rồi ép sang số; giá đổi sang đơn vị triệu đồng (`price_tr`).")
bullet("`mfdate = \"trước năm 1980\"` (12 dòng) được gán 1979.")

h2("3.3. Trích vị trí, loại cột thừa và tin trùng")
para("**Vị trí từ URL.** Mọi URL có dạng `mua-ban-oto-<quận/huyện>-<tỉnh>/<mã tin>.htm`. So khớp phần cuối với danh sách 63 tỉnh/thành để lấy cột `province` (giữ dạng slug của Chợ Tốt như `tp-ho-chi-minh`, `ha-noi`). Trích được tỉnh cho 100% số tin. Không tách quận/huyện vì có 453 quận/huyện, trung vị chỉ 4 tin mỗi quận, 315 quận dưới 10 tin: dữ liệu quá thưa. Ngay cả ở mức tỉnh, TP.HCM và Hà Nội đã chiếm 67% số tin, 28 tỉnh có dưới 30 tin.")
para("**Cột loại bỏ:** `no` và `url` là định danh, không mang thông tin dự đoán; `veh_warranty_policy` chỉ có một giá trị duy nhất (\"Bảo hành hãng\") ở mọi dòng.")
para("**Tin trùng:** 691 dòng (4,7%) giống hệt nhau ở mọi thuộc tính và giá (331 trong số đó là xe mới, thường do đại lý đăng nhiều xe cùng cấu hình). Giữ lại sẽ làm lệch phân phối, và khi chia train/test thì cùng một xe có thể nằm ở cả hai phía, làm điểm đánh giá cao ảo. Chỉ giữ một bản, còn lại **14.144 dòng**.")

h2("3.4. Giá trị bất hợp lý")
para("Bước này làm **trước** khi điền thiếu, để không điền dựa trên số liệu sai. Phân biệt hai loại: **sai dữ liệu** (nhập nhầm, không thể xảy ra) thì loại hoặc sửa; **ngoại lệ thật** (xe siêu sang giá chục tỷ) thì giữ, vì đó là xe có thật.")
table(["Cột", "Quy tắc", "Lý do", "Số dòng"], [
    ["Giá", "Loại nếu < 20 triệu hoặc > 10 tỷ", "Gõ thiếu/thừa số 0; không biết giá đúng nên loại", "64"],
    ["Giá", "Loại giá là dãy số liên tiếp (123.456.789...)", "Giá giả khi người bán không muốn công khai giá", "14"],
    ["Tình trạng", "\"Mới\" nhưng hơn 3 năm tuổi → \"Đã sử dụng\"", "Ghi sai tình trạng (ví dụ Tucson 2011 \"mới\")", "6 (sửa)"],
    ["Số km", "Xe đã dùng > 500.000 km → thiếu", "Nhập thừa số 0", "106"],
    ["Số km", "Xe ≥ 2 năm tuổi mà < 100 km → thiếu", "Nhập theo đơn vị nghìn km", "447"],
    ["Số km", "> 100.000 km/năm → thiếu", "Bất khả thi với xe dân dụng", "25"],
], [2.2, 5.4, 6.4, 2.0], caption="Quy tắc phát hiện giá trị bất hợp lý", align=["l", "l", "l", "c"], font=11)
para("Các giá như 399.999.999 hay 888.888.888 vẫn được **giữ**, vì đó là cách định giá tâm lý hoặc chọn số đẹp, vẫn là giá thật. Sau bước này còn **14.066 dòng** (loại 78 dòng); 578 giá trị số km bất hợp lý được chuyển thành thiếu để điền lại ở mục 3.6.")

h2("3.5. Giá trả trước / đặt cọc")
para("Ngưỡng 20 triệu chỉ bắt được lỗi gõ thiếu số. Vẫn còn những tin mà \"giá\" thực ra là **số tiền trả trước hoặc đặt cọc**, ví dụ xe đời 2025-2026 còn mới mà giá chỉ 30-100 triệu. Một ngưỡng tuyệt đối không bắt được trường hợp này, vì 100 triệu hợp lý với xe 20 năm tuổi nhưng vô lý với xe 1 năm tuổi.")
para("**Quy tắc:** loại tin có giá **thấp hơn 30% giá trung vị của các xe cùng hãng, dòng và năm sản xuất** (chỉ xét nhóm có ít nhất 3 xe). Không xe nào mất 70% giá so với xe cùng đời chỉ vì tình trạng hay số km. Kết quả: loại **129 tin**, 94% trong số đó có giá dưới 200 triệu; còn lại **13.937 dòng**.")
table(["Xe", "Năm", "Tình trạng", "Giá rao (triệu)", "Trung vị nhóm (triệu)"], [
    ["Toyota Camry", "2026", "Đã sử dụng", "300", "1.400"],
    ["Ford Everest", "2026", "Đã sử dụng", "320", "1.325"],
    ["Toyota Fortuner", "2026", "Mới", "125", "1.249"],
    ["Hyundai Santa Fe", "2025", "Mới", "220", "959"],
    ["Mercedes Benz E Class", "2019", "Đã sử dụng", "156", "889"],
], [5.0, 1.6, 3.0, 3.0, 3.4], caption="Ví dụ tin bị loại vì nghi ghi giá trả trước / đặt cọc")
para("Đây là bước **sửa lỗi nhãn**: quy tắc dùng giá trên toàn bộ dữ liệu nhưng chỉ để loại dòng có đáp án sai, không đưa thông tin giá vào đặc trưng nên không gây rò rỉ dữ liệu vào đầu vào của mô hình.")
para("**Ngoại lệ theo IQR** của log giá còn 696 dòng (5,0%), chủ yếu là xe sang thật (Mercedes, Lexus, Bentley, Range Rover...) hoặc xe cổ rất rẻ. Đây là thông tin thật của thị trường nên **giữ nguyên**; ảnh hưởng của chúng được giảm bằng biến đổi log.")

h2("3.6. Xử lý giá trị thiếu")
para("Trước khi điền cần hiểu **vì sao thiếu**, vì cách điền phụ thuộc cơ chế thiếu.")
figure("01_missing.png", 12, "Tỉ lệ giá trị thiếu theo cột (dữ liệu thô)")
table(["Cột", "Cơ chế thiếu", "Cách xử lý"], [
    ["`mileage_km`", "**Toàn bộ** 1.235 xe mới thiếu km (trang tin xe mới không có ô số km); chỉ 244 xe đã dùng thiếu thật, cộng 578 giá trị bất hợp lý", "Xe mới: **0 km**. Xe đã dùng: trung vị theo năm sản xuất (814 xe, 5,8%), đánh dấu `mileage_missing = 1`"],
    ["`carorigin`", "Thiếu ~41%; một mẫu xe có thể vừa nhập khẩu vừa lắp ráp", "Nhãn riêng **\"Không rõ\"** (5.787 dòng)"],
    ["`cartype`", "Thiếu ~33%; kiểu dáng gần như do dòng xe quyết định", "Mode theo hãng + dòng xe (4.336); còn lại \"Không rõ\" (243)"],
    ["`carseats`", "Thiếu ~25%; số chỗ do dòng xe quyết định", "Mode theo dòng xe (3.352) → theo hãng (183) → mode chung (4)"],
    ["`price`", "1 dòng", "**Xóa** (không bịa biến mục tiêu)"],
], [2.6, 6.8, 6.6], caption="Cơ chế thiếu và cách điền cho từng cột", align=["l", "l", "l"], font=11)
para("**Vì sao không điền trung vị số km cho xe mới?** Điền trung vị sẽ biến xe mới thành \"xe đã chạy 66.000 km\", sai lệch nghiêm trọng. Đây là thiếu **có cấu trúc** (không đo vì không có ý nghĩa), giá trị đúng là 0.")
para("**Cột đánh dấu `mileage_missing`:** giá trị điền cho xe đã dùng chỉ là \"đoán trung bình\". Cột này cho mô hình biết dòng nào là ước lượng để tự học mức độ tin cậy; việc người bán không khai số km cũng có thể là một tín hiệu về giá.")
para("**Vì sao `cartype` không lùi về cấp hãng còn `carseats` thì có?** Trong một dòng xe, kiểu dáng gần như cố định; nhưng một hãng bán đủ loại (Ford có Ranger bán tải, Everest SUV, Focus sedan), nên gán kiểu dáng phổ biến của hãng là đoán mò. Số chỗ thì đa số là 5, đoán sai theo hãng thường chỉ lệch 5 ↔ 7 chỗ.")

h2("3.7. Biến đổi log cho giá")
para("Giá lệch phải mạnh khiến mô hình hồi quy bị kéo bởi vài xe rất đắt. Lấy logarit đưa phân phối về gần đối xứng (độ lệch giảm từ **5,08 xuống −0,20**) và biến chênh lệch tuyệt đối thành chênh lệch **tương đối**: xe 100 → 150 triệu và xe 1 → 1,5 tỷ đều là tăng 50%, khớp với cách người mua nghĩ về giá và với thước đo MAPE.")
equation(r"y = \ln(p)")
equation(r"\hat{p} = e^{\hat{y}}")
para("Với p là giá (triệu đồng), mô hình học `price_log`, dự đoán xong dùng `exp()` để đổi về triệu đồng; **mọi thước đo đều tính trên giá thật**. Lựa chọn này được kiểm chứng bằng thí nghiệm ở mục 5.7.")

h2("3.8. Gộp nhãn hiếm theo cấp")
para("Dữ liệu có 69 hãng và 509 tổ hợp hãng + dòng xe, nhiều nhãn chỉ có 1-5 tin. One-hot nguyên vẹn sinh hàng trăm cột thưa, mô hình học quy luật từ vài mẫu là học nhiễu. Cách gộp đơn giản (mọi dòng hiếm thành một nhãn `\"Dòng khác\"`) có vấn đề: nhãn này chiếm 17% dữ liệu nhưng tới **65% số xe trên 2 tỷ**, một chiếc Mercedes G63 và một chiếc Kia đời cũ mang cùng nhãn.")
para("Đề tài dùng cách **gộp theo cấp**: mỗi xe lùi về nhóm gần nhất còn đủ mẫu.")
table(["Cấp", "Quy tắc", "Ví dụ"], [
    ["Dòng xe", "Giữ `Hãng + Dòng` nếu có ≥ 10 tin", "Toyota Vios"],
    ["→ Hãng", "Dòng hiếm → `\"<Hãng> - dòng khác\"`", "Mercedes Benz - dòng khác"],
    ["Hãng", "Giữ hãng nếu có ≥ 30 tin", "Volvo, Subaru"],
    ["→ Nhóm hãng", "Hãng hiếm → `\"Hãng cao cấp khác\"` / `\"Hãng phổ thông khác\"`", "Bentley → cao cấp; Wuling → phổ thông"],
], [3.0, 7.6, 5.4], caption="Quy tắc gộp nhãn hiếm theo cấp", align=["l", "l", "l"])
para("Nhóm cao cấp / phổ thông được phân theo **định vị thương hiệu** (hiểu biết thị trường), **không** dựa vào giá trong dữ liệu, để không dùng biến mục tiêu khi tạo đặc trưng. Kết quả: 69 hãng → **28 nhóm**, 509 dòng → **214 nhóm**; 8,9% số xe mang nhãn \"... - dòng khác\". Nhóm \"Hãng cao cấp khác\" có 93 tin từ 13 hãng (giá trung vị 1 tỷ), \"Hãng phổ thông khác\" có 188 tin từ 30 hãng (giá trung vị 390 triệu).")
para("Cách gộp và ngưỡng được **chọn bằng 5-fold CV chỉ trên tập train** (Bảng 3.6). Gộp theo cấp cải thiện rõ Ridge (MAPE 21,9% → 18,9%; xe > 2 tỷ 43,0% → 32,2%) vì mô hình tuyến tính chỉ có một hệ số cho mỗi nhãn. Random Forest được lợi ít hơn vì tự bù thông tin bằng các đặc trưng khác. Không phương án nào làm mô hình xấu đi.")
table(["Phương án", "Ridge: MAPE", "< 200 tr", "> 2 tỷ", "RF: MAPE", "< 200 tr", "> 2 tỷ"], [
    ["Một nhãn chung (50 / 30)", "0,219", "0,522", "0,430", "0,163", "0,374", "0,292"],
    ["Gộp theo cấp (50 / 30)", "0,206", "0,474", "0,392", "0,163", "0,361", "0,278"],
    ["Gộp theo cấp (30 / 10) – chọn", "0,189", "0,449", "0,322", "0,161", "0,359", "0,287"],
], [5.0, 1.9, 1.8, 1.8, 1.9, 1.8, 1.8], caption="So sánh các cách gộp nhãn (5-fold CV trên train, MAPE)", bold_rows=(2,), font=11)

h2("3.9. Tạo đặc trưng")
bullet("`age` = 2026 − năm sản xuất: tuổi xe có ý nghĩa trực tiếp hơn năm tuyệt đối.")
bullet("`km_per_year` = km / max(tuổi, 1): xe 5 năm đi 150.000 km (nhiều khả năng chạy dịch vụ) khác hẳn xe 5 năm đi 50.000 km.")
bullet("`mileage_missing`: 1 nếu số km là giá trị điền.")
bullet("`province`: tỉnh/thành của tin đăng.")
para("**Vị trí có giúp dự đoán không?** Thử thêm miền (3 nhóm) hoặc tỉnh/thành (15 nhóm, tỉnh dưới 100 tin gộp theo miền) bằng cùng cách CV: MAPE chỉ chênh ở chữ số thứ ba (Ridge 0,1895 / 0,1894 / 0,1897; Random Forest 0,1610 / 0,1604 / 0,1611), nhỏ hơn mức dao động giữa các lần chia fold. Giá rao chủ yếu do bản thân chiếc xe quyết định; chênh lệch giá giữa các miền chủ yếu do **cơ cấu xe khác nhau**, mà mô hình đã thấy qua các đặc trưng khác. Vì vậy `province` được giữ trong file để mô tả dữ liệu nhưng **không đưa vào mô hình**.")

h2("3.10. Dữ liệu mất cân bằng")
para("Biến mục tiêu là số liên tục nên không có \"lớp thiểu số\" như bài toán phân loại. Mất cân bằng ở đây thể hiện ở **mật độ dữ liệu không đều theo vùng giá**: phần lớn xe ở phân khúc phổ thông, xe sang vài tỷ rất ít. Mô hình tối ưu sai số trung bình sẽ học tốt vùng đông mẫu và kém ở vùng hiếm. Để định lượng, giá được chia thành 5 phân khúc (chỉ dùng để phân tích, chia mẫu và đánh giá, không làm đặc trưng):")
table(["Phân khúc", "Số tin", "Tỉ lệ", "Ít hơn phân khúc lớn nhất"], [
    ["< 200 triệu", "1.972", "14,1%", "3,0 lần"],
    ["200-500 triệu", "5.907", "42,4%", "1,0 lần"],
    ["500-1.000 triệu", "4.529", "32,5%", "1,3 lần"],
    ["1-2 tỷ", "1.071", "7,7%", "5,5 lần"],
    ["> 2 tỷ", "458", "3,3%", "12,9 lần"],
], [4.0, 3.0, 3.0, 5.0], caption="Phân bố dữ liệu theo phân khúc giá")
para("Phân khúc > 2 tỷ ít hơn phân khúc lớn nhất gần 13 lần: mất cân bằng thật sự. Các đặc trưng cũng lệch: xe mới chỉ 8,5%, Hybrid 2,2%, hộp số bán tự động 0,7%. Các biện pháp áp dụng:")
bullet("**Chia train/test phân tầng theo phân khúc giá**, để tập test có đủ xe ở mọi phân khúc.")
bullet("**Học trên log giá**, giảm ảnh hưởng của đuôi phải.")
bullet("**Báo cáo MAPE theo từng phân khúc**, không chỉ một con số trung bình.")
bullet("**Thử trọng số mẫu, Random Oversampling, Random Undersampling** bằng CV trên tập train (mục 4.5 và 5.7).")
para("File `clean_data_oto.csv` **chỉ chứa dữ liệu thật**: nếu ghi mẫu nhân bản vào file, người dùng sau chia ngẫu nhiên sẽ khiến bản sao của cùng một xe nằm ở cả train lẫn test.")

h2("3.11. Tổng kết tiền xử lý")
table(["Bước", "Số dòng còn lại", "Thay đổi"], [
    ["Dữ liệu thô", "14.835", ""],
    ["Loại tin trùng nội dung", "14.144", "−691"],
    ["Loại giá thiếu / < 20 triệu / > 10 tỷ / giá giả", "14.066", "−78"],
    ["Loại giá trả trước / đặt cọc", "13.937", "−129"],
    ["**Dữ liệu sạch** (giữ 93,9%)", "**13.937**", "18 cột, không còn giá trị thiếu"],
], [8.0, 3.5, 4.5], caption="Số dòng qua từng bước tiền xử lý", bold_rows=(4,))
para("File `clean_data_oto.csv` gồm 18 cột: `carbrand`, `carbrand_grp`, `carmodel`, `carmodel_grp`, `carorigin`, `condition_ad`, `gearbox`, `fuel`, `cartype`, `carseats`, `mfdate`, `age`, `mileage_km`, `mileage_missing`, `km_per_year`, `province`, `price_tr`, `price_log`. Cột gốc `carbrand`, `carmodel` được giữ để tra cứu; mô hình dùng cột đã gộp `*_grp`.")

# ================================================================== CHƯƠNG 4
chapter(4, "XÂY DỰNG MÔ HÌNH")
h2("4.1. Thiết kế thí nghiệm")
h3("4.1.1. Chia dữ liệu")
para("Dữ liệu được chia **80% train (11.149 tin) / 20% test (2.788 tin)**, phân tầng theo phân khúc giá, `random_state = 42`. Không tách tập validation riêng: tham số được chọn bằng **5-fold cross-validation** (hoặc **OOB** với Random Forest) **trên tập train**, ổn định hơn một tập validation cố định khi xe trên 2 tỷ chỉ có khoảng 460 tin. Tập test chỉ dùng **một lần** để báo cáo kết quả cuối.")
figure("m01_chia_train_test.png", 13, "Chia train/test phân tầng: tỉ lệ các phân khúc giá như nhau ở hai tập")
h3("4.1.2. Đặc trưng cho từng mô hình")
para("Hai mô hình dùng chung đặc trưng phân loại (one-hot), nhưng đặc trưng số được biến đổi theo bản chất mô hình:")
table(["Nhóm", "Đặc trưng", "Ridge", "Random Forest"], [
    ["Phân loại (one-hot)", "hãng, dòng xe (đã gộp), xuất xứ, tình trạng, hộp số, nhiên liệu, kiểu dáng", "✓", "✓"],
    ["Tuổi xe", "`age`", "`age`, `age²`", "`age`"],
    ["Số km", "`mileage_km`, `km_per_year`", "`log(1+km)`, `log(1+km/năm)`", "giữ nguyên"],
    ["Khác", "`carseats`, `mileage_missing`", "✓ (chuẩn hóa)", "✓"],
    ["Số cột sau mã hóa", "", "278", "277"],
], [3.4, 5.6, 3.8, 3.2], caption="Đặc trưng đầu vào của hai mô hình", align=["l", "l", "c", "c"], font=11)
bullet("**Ridge cần `age²` và `log`** vì nó chỉ cộng các hiệu ứng tuyến tính, trong khi xe mất giá nhanh những năm đầu rồi chậm lại, và 10.000 km đầu \"đắt\" hơn 10.000 km sau.")
bullet("**Random Forest không cần**, vì cây chỉ so sánh ngưỡng nên mọi biến đổi đơn điệu cho cùng kết quả; thêm `age²` chỉ làm độ quan trọng đặc trưng bị chia đôi.")
bullet("**StandardScaler** chỉ cho Ridge, để khoản phạt L2 công bằng giữa các đặc trưng. Bộ mã hóa và chuẩn hóa **fit trên train** rồi áp lên test.")
bullet("**Không dùng:** `price_tr`, `price_log` (đáp án), `mfdate` (trùng `age`), `province` (không giúp dự đoán, mục 3.9).")

h2("4.2. Thước đo đánh giá")
para("Tất cả thước đo tính trên **giá thật (triệu đồng)**, sau khi đổi dự đoán log về giá bằng `exp()`:")
equation(r"\mathrm{MAPE} = \frac{1}{n}\sum_{i=1}^{n}\frac{|p_i - \hat{p}_i|}{p_i}")
equation(r"\mathrm{MAE} = \frac{1}{n}\sum_{i=1}^{n}|p_i - \hat{p}_i|")
equation(r"\mathrm{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(p_i - \hat{p}_i)^2}")
para("trong đó pᵢ là giá thật và p̂ᵢ là giá dự đoán của xe thứ i (triệu đồng).", indent=False)
table(["Thước đo", "Ý nghĩa", "Vì sao dùng"], [
    ["**MAPE**", "Sai số phần trăm trung bình", "**Thước đo chính**: lệch 100 triệu là nhỏ với xe 3 tỷ nhưng rất lớn với xe 150 triệu"],
    ["MedAPE", "Trung vị sai số phần trăm", "Sai số \"điển hình\", không bị vài tin sai nặng kéo lệch"],
    ["MAE", "Sai số tuyệt đối trung bình (triệu)", "Dễ hiểu: trung bình đoán lệch bao nhiêu tiền"],
    ["RMSE", "Căn trung bình bình phương sai số (triệu)", "Phạt nặng lỗi lớn (thường ở xe sang)"],
    ["R² (log)", "Tỉ lệ biến thiên của log giá được giải thích", "Đo trên đúng thang mô hình học"],
    ["±10% / ±20%", "Tỉ lệ tin đoán lệch không quá 10% / 20%", "Diễn giải cho người dùng"],
], [2.8, 5.6, 7.6], caption="Các thước đo đánh giá", align=["l", "l", "l"], font=11)
para("Ngoài ra luôn báo **MAPE theo từng phân khúc giá**. Mô hình mốc (**baseline**) luôn đoán giá trung vị của tập train; mô hình nào cũng phải tốt hơn hẳn mức này mới có ý nghĩa.")

h2("4.3. Mô hình 1: Ridge Regression")
h3("4.3.1. Cơ sở lý thuyết")
para("Ridge dự đoán log giá bằng tổ hợp tuyến tính của các đặc trưng, và tìm trọng số bằng cách tối thiểu hóa sai số bình phương **cộng một khoản phạt L2**:")
equation(r"\hat y = w_0 + \sum_{j=1}^{p} w_j x_j")
equation(r"J(w) = \frac{1}{2n}\sum_{i=1}^{n}(y_i - \hat y_i)^2 + \frac{\alpha}{2}\sum_{j=1}^{p} w_j^2")
para("Hệ số tự do `w₀` không bị phạt. **Vì sao cần khoản phạt:** sau one-hot có khoảng 270 cột, nhiều cột tương quan mạnh (hãng Toyota và dòng Toyota Vios luôn đi cùng nhau). Không có phạt, các hệ số có thể phình to và triệt tiêu lẫn nhau, mô hình nhạy với nhiễu. Siêu tham số α quá nhỏ thì dễ overfit, quá lớn thì các hệ số bị ép về 0 (underfit).")
para("**Diễn giải hệ số:** vì mô hình dự đoán log giá, tăng xⱼ thêm 1 đơn vị thì giá nhân với exp(wⱼ), tức thay đổi khoảng (exp(wⱼ) − 1) × 100%.")
h3("4.3.2. Bản thư viện")
para("Dùng `sklearn.linear_model.Ridge`, tinh chỉnh α trên lưới 25 giá trị từ 10⁻³ đến 10³ bằng **GridSearchCV + 5-fold CV** (thước đo RMSE trên log giá). Kết quả: **α = 0,5623**, CV RMSE (log) = 0,2879, mất 8,9 giây.")
figure("m02_ridge_chon_alpha.png", 12, "Chọn α cho Ridge bằng 5-fold cross-validation")
h3("4.3.3. Bản tự cài đặt bằng NumPy")
para("Lớp `RidgeScratch` tìm `w` bằng hai cách, đều tự viết:")
para("**(1) Nghiệm đóng (normal equation).** Đạo hàm J(w) theo w và cho bằng 0, được hệ phương trình tuyến tính, giải trực tiếp bằng `np.linalg.solve` (không nghịch đảo ma trận để ổn định số):", indent=False)
equation(r"\left(\frac{1}{n}A^{T}A + \alpha I'\right)w = \frac{1}{n}A^{T}y")
para("trong đó A là ma trận đặc trưng thêm cột 1 (cho w₀), I' là ma trận đơn vị nhưng phần tử ứng với w₀ bằng 0.", indent=False)
para("**(2) Gradient Descent có momentum Nesterov.** Bắt đầu từ w = 0, lặp lại bước ngược hướng gradient tại điểm \"nhìn trước\" v:", indent=False)
equation(r"\nabla J(v) = \frac{1}{n}A^{T}(Av - y) + \alpha I' v")
equation(r"w_{t+1} = v_t - \eta \nabla J(v_t)")
equation(r"v_{t+1} = w_{t+1} + \frac{t-1}{t+2}(w_{t+1} - w_t)")
para("Bước học η = 1/L với L là trị riêng lớn nhất của ma trận Hessian, đảm bảo hội tụ. Cách này dùng để minh họa quá trình tối ưu và kiểm chứng chéo với nghiệm đóng.")
para("**Chọn α** bằng **K-fold CV tự viết** (xáo trộn chỉ số rồi chia thành K phần). Lưu ý: `sklearn` tối thiểu hóa ‖y − Aw‖² + α‖w‖² (không chia n), còn bản tự viết chia n, nên hai mô hình là một khi α(tự viết) = α(sklearn) / n. K-fold tự viết chọn đúng **α = 0,5623**, cùng CV RMSE 0,2879.")
h3("4.3.4. Kiểm chứng")
table(["Kiểm tra", "Kết quả"], [
    ["Nghiệm đóng so với `sklearn` (cùng α): lệch hệ số lớn nhất", "2,8 × 10⁻¹¹"],
    ["Gradient descent (5.000 vòng, 17,1 giây): J − J*", "3,6 × 10⁻⁷"],
    ["Gradient descent: lệch dự đoán log giá lớn nhất trên test", "2,1 × 10⁻³"],
    ["MAPE test: thư viện / nghiệm đóng / GD", "0,1847 / 0,1847 / 0,1847"],
], [11.0, 5.0], caption="Kiểm chứng Ridge tự cài đặt với bản thư viện", align=["l", "c"])
para("Hệ số của nghiệm đóng trùng `sklearn` đến sai số làm tròn của máy tính, gradient descent hội tụ về cùng nghiệm. Vậy bản tự cài đặt **đúng**.")
figure("m03_ridge_kiem_chung.png", 15.5, "Kiểm chứng Ridge: đường CV tự viết trùng thư viện và quá trình hội tụ của gradient descent")

h2("4.4. Mô hình 2: Random Forest")
h3("4.4.1. Cơ sở lý thuyết")
para("**Thành phần: cây hồi quy CART.** Cây chia dữ liệu bằng các câu hỏi có/không, ví dụ \"tuổi xe ≤ 5?\", \"dòng xe là Toyota Vios?\". Tại mỗi nút, thuật toán thử các đặc trưng và ngưỡng, chọn phép chia làm **giảm tổng bình phương sai số (SSE)** nhiều nhất. Với nút có n mẫu, tổng nhãn S, chia thành trái (n_L, S_L) và phải (n_R, S_R), mức giảm SSE là:")
equation(r"\text{gain} = \frac{S_L^2}{n_L} + \frac{S_R^2}{n_R} - \frac{S^2}{n}")
para("Lặp lại đến khi đạt độ sâu tối đa hoặc nút quá ít mẫu; giá trị dự đoán ở lá là trung bình log giá của các xe trong lá. Cây sâu học thuộc dữ liệu train (độ chệch thấp) nhưng **phương sai cao**: đổi vài mẫu là cấu trúc cây thay đổi hẳn.")
para("**Random Forest** giảm phương sai bằng cách lấy trung bình nhiều cây khác nhau:")
numbered([
    "**Bootstrap:** mỗi cây học trên một mẫu lấy ngẫu nhiên **có hoàn lại** từ train (khoảng 63% mẫu khác nhau).",
    "**Chọn ngẫu nhiên đặc trưng:** mỗi lần chia nút chỉ xét một tỉ lệ `max_features` đặc trưng, để các cây ít giống nhau.",
    "**Lấy trung bình** dự đoán của tất cả các cây.",
])
equation(r"\hat y(x) = \frac{1}{T}\sum_{t=1}^{T} f_t(x)")
para("**Out-of-bag (OOB):** khoảng 37% mẫu không được chọn vào bootstrap của mỗi cây. Dự đoán các mẫu này bằng những cây \"chưa thấy\" chúng cho ra một ước lượng sai số khách quan mà không cần tập validation riêng.")
table(["Siêu tham số", "Tác dụng"], [
    ["`n_estimators`", "Số cây; nhiều hơn thì ổn định hơn, đến một mức thì bão hòa"],
    ["`max_depth`", "Độ sâu tối đa của cây"],
    ["`min_samples_leaf`", "Số mẫu tối thiểu ở mỗi lá; lớn hơn thì cây \"mượt\" hơn"],
    ["`max_features`", "Tỉ lệ đặc trưng xét ở mỗi lần chia; nhỏ hơn thì các cây đa dạng hơn"],
], [4.0, 12.0], caption="Siêu tham số của Random Forest", align=["l", "l"])
h3("4.4.2. Bản thư viện")
para("Dùng `RandomForestRegressor`, tinh chỉnh bằng **RandomizedSearchCV** (15 cấu hình ngẫu nhiên) + **3-fold CV** trên train, mất 156 giây. Cấu hình tốt nhất: **300 cây, `max_depth` = 30, `min_samples_leaf` = 1, `max_features` = 0,5**; CV RMSE (log) = 0,2741; OOB R² (log) = 0,8956; huấn luyện 7,9 giây.")
table(["n_estimators", "min_samples_leaf", "max_features", "max_depth", "CV RMSE (log)"], [
    ["300", "1", "0,50", "30", "0,2741"],
    ["300", "1", "0,33", "30", "0,2747"],
    ["300", "2", "0,50", "30", "0,2819"],
    ["300", "2", "0,80", "30", "0,2827"],
    ["300", "2", "0,33", "30", "0,2839"],
], [3.0, 3.4, 3.0, 2.8, 3.4], caption="Năm cấu hình Random Forest tốt nhất (thư viện)", bold_rows=(0,), align=["c"] * 5)
para("Các cấu hình tốt đều có cây sâu và lá nhỏ: dữ liệu có nhiều tổ hợp hãng-dòng-đời xe riêng biệt nên mô hình cần đủ độ phức tạp để học từng nhóm.")
h3("4.4.3. Bản tự cài đặt bằng NumPy")
table(["Lớp", "Nhiệm vụ"], [
    ["`Binner`", "Rời rạc hóa mỗi đặc trưng thành tối đa 32 bin theo phân vị (fit trên train)"],
    ["`RegressionTreeScratch`", "Cây hồi quy CART: tìm phép chia tốt nhất theo công thức gain"],
    ["`RandomForestScratch`", "Bootstrap + chọn ngẫu nhiên đặc trưng + lấy trung bình; tính OOB và độ quan trọng đặc trưng"],
], [5.0, 11.0], caption="Các lớp của Random Forest tự cài đặt", align=["l", "l"])
para("**Tăng tốc bằng histogram.** Cách cơ bản phải sắp xếp từng cột ở mỗi nút để thử mọi ngưỡng, rất chậm khi viết bằng Python. Thay vào đó, mỗi đặc trưng được chia sẵn thành tối đa 32 bin **một lần** (kỹ thuật của LightGBM / HistGradientBoosting). Tại mỗi nút chỉ cần đếm số mẫu và tổng nhãn trong từng bin (`np.bincount`), rồi cộng dồn (`np.cumsum`) là có gain của **mọi ngưỡng cùng lúc**. Cột one-hot chỉ có 2 giá trị nên không mất thông tin; cột số mất rất ít độ chi tiết.")
para("**Độ quan trọng đặc trưng** = tổng gain mà đặc trưng mang lại ở mọi nút của mọi cây, chuẩn hóa về tổng bằng 1 (cùng định nghĩa với `sklearn`).")
h3("4.4.4. Kiểm chứng thành phần: một cây")
para("Trước khi dựng rừng, so sánh **một cây** tự viết (xét mọi đặc trưng ở mỗi nút) với `DecisionTreeRegressor` khi dùng **cùng tham số**:")
table(["Mô hình", "Số nút", "R² (log) train", "R² (log) test", "MAPE test", "Thời gian"], [
    ["Một cây – thư viện", "3.481", "0,929", "0,842", "19,6%", "0,3 s"],
    ["Một cây – tự cài đặt", "3.429", "0,927", "0,851", "18,6%", "1,6 s"],
], [4.4, 1.9, 2.4, 2.4, 2.2, 2.0], caption="Kiểm chứng cây hồi quy tự cài đặt")
para("Hai cây có số nút và R² gần như nhau, nên **lớp cây tự viết đúng**. Khoảng cách lớn giữa R² train (0,93) và R² test (0,84-0,85) chính là **phương sai cao** mà Random Forest khắc phục. Bảng này dùng tập test chỉ để kiểm tra tính đúng của code, không dùng để chọn tham số.")
h3("4.4.5. Tinh chỉnh bằng OOB và chọn số cây")
para("Bản tự viết chậm hơn thư viện nhiều, nên thay vì CV (huấn luyện 3-5 lần mỗi cấu hình), dùng **OOB RMSE**: mỗi cấu hình chỉ huấn luyện một lần với 30 cây. Thử 6 cấu hình trong cùng không gian tham số, mất 151 giây.")
table(["max_depth", "min_samples_leaf", "max_features", "OOB RMSE (log)", "OOB R²", "Thời gian (s)"], [
    ["30", "2", "0,50", "0,2704", "0,886", "36"],
    ["30", "2", "0,33", "0,2741", "0,883", "28"],
    ["30", "3", "0,33", "0,2779", "0,879", "21"],
    ["20", "1", "0,33", "0,2938", "0,865", "24"],
    ["20", "2", "0,33", "0,2946", "0,864", "19"],
    ["20", "3", "0,50", "0,2972", "0,862", "23"],
], [2.4, 3.0, 2.6, 3.0, 2.2, 2.8], caption="Tinh chỉnh Random Forest tự cài đặt bằng OOB (30 cây)", bold_rows=(0,), align=["c"] * 6)
para("Với cấu hình tốt nhất, huấn luyện **100 cây** mất 152 giây, OOB R² (log) = **0,8916** (bản thư viện 0,8956). Hình 4.4 cho thấy trực quan vì sao \"rừng\" tốt hơn \"cây\": sai số giảm rất nhanh trong vài chục cây đầu rồi bão hòa.")
figure("m05_rf_so_cay.png", 12.5, "OOB RMSE của rừng tự cài đặt theo số cây")

h2("4.5. Kỹ thuật xử lý mất cân bằng")
para("Ba kỹ thuật được thử trên chính mô hình cuối (Random Forest), so với huấn luyện bình thường:")
table(["Kỹ thuật", "Cách làm (chỉ trong phần train của mỗi fold)"], [
    ["Không cân bằng", "Huấn luyện bình thường"],
    ["**Trọng số mẫu**", "Mẫu ở phân khúc hiếm có trọng số lớn hơn: 1/√(tần suất phân khúc), chuẩn hóa về trung bình 1"],
    ["**Random Oversampling**", "Nhân bản ngẫu nhiên mẫu của phân khúc hiếm đến tối thiểu 25% quy mô phân khúc lớn nhất"],
    ["**Random Undersampling**", "Bỏ bớt mẫu ở phân khúc đông, mỗi phân khúc giữ tối đa 8 lần số mẫu của phân khúc hiếm nhất"],
], [4.6, 11.4], caption="Các kỹ thuật xử lý mất cân bằng được thử nghiệm", align=["l", "l"])
para("**Cách đánh giá:** 5-fold CV phân tầng theo phân khúc giá **chỉ trên tập train**. Việc cân bằng chỉ áp dụng cho phần train của từng fold; phần validation **giữ nguyên phân phối thật**. Cân bằng trước khi chia sẽ làm bản sao của cùng một xe nằm ở cả hai phía và cho điểm cao giả tạo. Thí nghiệm cũng so sánh học trên giá gốc với học trên log giá. Tập test không được dùng ở bước này.")

# ================================================================== CHƯƠNG 5
chapter(5, "KẾT QUẢ VÀ ĐÁNH GIÁ")
h2("5.1. Kết quả tổng thể trên tập test")
para("Đây là lần **duy nhất** tập test được dùng. Mọi mô hình học trên cùng tập train (11.149 tin) và được đánh giá trên cùng 2.788 tin test.")
table(["Mô hình", "MAPE", "MedAPE", "MAE (tr)", "RMSE (tr)", "R² (log)", "±10%", "±20%", "Fit (s)"], [
    ["Baseline (trung vị)", "83,5%", "40,0%", "337", "724", "0,00", "14%", "26%", "0,001"],
    ["Ridge – thư viện", "18,5%", "10,7%", "120", "411", "0,873", "48%", "75%", "0,04"],
    ["Ridge – tự cài đặt (nghiệm đóng)", "18,5%", "10,7%", "120", "411", "0,873", "48%", "75%", "0,02"],
    ["Ridge – tự cài đặt (GD)", "18,5%", "10,7%", "120", "411", "0,873", "48%", "75%", "17,1"],
    ["**Random Forest – thư viện**", "**15,5%**", "**9,0%**", "**102**", "**372**", "**0,891**", "54%", "**80%**", "7,9"],
    ["Random Forest – tự cài đặt", "15,7%", "9,0%", "106", "388", "0,887", "55%", "80%", "151,7"],
], [4.6, 1.5, 1.6, 1.4, 1.5, 1.5, 1.2, 1.2, 1.5], caption="Kết quả trên tập test", bold_rows=(4,), font=10.5)
figure("m06_so_sanh_tong.png", 16, "So sánh MAPE và tỉ lệ xe được định giá sát giữa các mô hình")
bullet("**Cả hai mô hình vượt xa mốc so sánh:** baseline sai trung bình 83,5%; Ridge giảm còn 18,5%, Random Forest còn 15,5%.")
bullet("Với Random Forest, **4 trên 5 xe** được định giá lệch không quá 20%, hơn một nửa lệch không quá 10%, sai số điển hình (MedAPE) khoảng 9%.")
bullet("Bản tự cài đặt cho kết quả gần như trùng bản thư viện; khác biệt lớn nhất là thời gian huấn luyện.")

h2("5.2. Sai số theo phân khúc giá")
table(["Phân khúc", "% dữ liệu", "Baseline", "Ridge", "Random Forest (TV)", "Random Forest (TCĐ)"], [
    ["< 200 triệu", "14%", "349,8%", "43,0%", "34,7%", "35,6%"],
    ["200-500 triệu", "42%", "38,5%", "13,9%", "11,7%", "11,6%"],
    ["500-1.000 triệu", "33%", "30,7%", "12,6%", "10,9%", "10,8%"],
    ["1-2 tỷ", "8%", "64,1%", "16,7%", "15,7%", "15,8%"],
    ["> 2 tỷ", "3%", "85,4%", "34,3%", "27,0%", "30,4%"],
], [3.2, 2.0, 2.2, 2.2, 3.2, 3.2], caption="MAPE theo phân khúc giá trên tập test (TV: thư viện, TCĐ: tự cài đặt)")
figure("m07_mape_phan_khuc.png", 15, "MAPE theo phân khúc giá")
bullet("**Phân khúc giữa (200 triệu - 1 tỷ, khoảng 75% thị trường):** sai số khoảng 11%, đủ tốt để tham khảo giá.")
bullet("**Xe dưới 200 triệu:** sai số phần trăm cao vì giá thấp: chênh vài chục triệu (tình trạng thực tế, thương lượng) đã là phần trăm lớn; xe đời cũ rất khác nhau về tình trạng mà dữ liệu không có; có thể vẫn còn tin ghi tiền trả trước chưa bị bắt.")
bullet("**Xe trên 2 tỷ:** chỉ 3% dữ liệu và thiếu thông tin quyết định giá xe sang (phiên bản, trang bị).")
bullet("Random Forest tốt hơn Ridge ở **mọi phân khúc**.")

h2("5.3. Dự đoán so với giá thật và phần dư")
para("Trên Hình 5.3, mỗi điểm là một xe trong tập test; trục dùng thang log nên khoảng cách tới đường chéo chính là sai số phần trăm. Phần dư của cả hai mô hình đối xứng quanh 0 (không lệch hệ thống), Random Forest có phân bố hẹp hơn (độ lệch chuẩn 0,26 so với 0,28). Biểu đồ hộp cho thấy sai số tăng ở hai đầu thang giá, rõ nhất ở xe trên 2 tỷ.")
figure("m08_du_doan_vs_thuc_te.png", 16, "Giá dự đoán so với giá thật trên tập test (thang log)")
figure("m09_phan_du.png", 16, "Phân bố phần dư và sai số tuyệt đối theo phân khúc")

h2("5.4. Kiểm định ý nghĩa thống kê bằng bootstrap")
para("Tập test hữu hạn nên MAPE chỉ là một ước lượng. **Bootstrap** lấy mẫu lại tập test có hoàn lại 1.000 lần, mỗi lần tính lại MAPE, để có khoảng tin cậy 95%. Để so sánh hai mô hình, dùng **bootstrap ghép cặp**: trong mỗi lần lấy mẫu, tính **hiệu MAPE của hai mô hình trên cùng các xe**. Nếu khoảng tin cậy 95% của hiệu không chứa 0 thì chênh lệch có ý nghĩa thống kê.")
table(["So sánh", "2,5%", "Trung vị", "97,5%", "Có ý nghĩa?"], [
    ["Ridge − Random Forest (thư viện)", "2,08", "2,97", "3,97", "**Có**"],
    ["RF tự cài đặt − RF thư viện", "−0,04", "0,19", "0,46", "Không (chứa 0)"],
    ["Ridge tự cài đặt − Ridge thư viện", "0,00", "0,00", "0,00", "Không (cùng nghiệm)"],
], [6.2, 1.8, 2.0, 1.8, 4.2], caption="Hiệu MAPE giữa các mô hình (điểm %), bootstrap ghép cặp")
figure("m10_khoang_tin_cay.png", 13.5, "Khoảng tin cậy 95% của MAPE và của hiệu MAPE")
para("**Random Forest tốt hơn Ridge có ý nghĩa thống kê** (khoảng 3 điểm %, KTC 95%: 2,1-4,0). **Bản tự cài đặt và bản thư viện không khác nhau có ý nghĩa.**")

h2("5.5. Bản tự cài đặt so với bản thư viện")
para("Nếu hai bản cài đặt cùng một thuật toán, dự đoán của chúng phải gần như trùng nhau trên **từng xe**, không chỉ ở con số trung bình. Hình 5.6 cho thấy dự đoán của Ridge trùng tuyệt đối; với Random Forest, các điểm bám sát đường chéo với độ lệch trung vị 1,7%. Chênh lệch nhỏ của Random Forest đến từ việc chia đặc trưng thành 32 bin, rừng tự viết dùng 100 cây thay vì 300, và chuỗi số ngẫu nhiên khác nhau.")
figure("m11_tu_cai_dat_vs_thu_vien.png", 15, "Dự đoán của bản tự cài đặt so với bản thư viện trên từng xe trong tập test")
table(["Tiêu chí", "Ridge", "Random Forest"], [
    ["MAPE test (thư viện / tự cài đặt)", "18,5% / 18,5%", "15,5% / 15,7%"],
    ["Kiểm chứng", "Hệ số lệch ~10⁻¹¹; GD hội tụ cùng nghiệm", "OOB R² 0,892 so với 0,896; cùng thứ hạng đặc trưng"],
    ["Thời gian huấn luyện", "0,02 s (nghiệm đóng), 17 s (GD) so với 0,04 s", "152 s (100 cây) so với 7,9 s (300 cây)"],
], [5.0, 5.5, 5.5], caption="Tóm tắt so sánh bản tự cài đặt và bản thư viện", align=["l", "l", "l"], font=11)
para("Chi phí tính toán là khác biệt lớn nhất: thư viện viết bằng C/Cython và chạy song song nhiều lõi. Đây là lý do thực tế để dùng thư viện khi triển khai, còn bản tự cài đặt có giá trị để hiểu thuật toán.")

h2("5.6. Diễn giải mô hình")
h3("5.6.1. Hệ số của Ridge")
para("Mỗi hệ số của cột one-hot cho biết thuộc tính đó làm giá cao hơn hay thấp hơn bao nhiêu % so với mức chung, khi giữ nguyên các đặc trưng khác. Vì mô hình có **cả** cột hãng **và** cột dòng xe, hệ số của một dòng xe là phần **chênh thêm so với mức chung của hãng đó**. Ví dụ hệ số âm của `Hãng: VinFast` nghĩa là xe VinFast có giá thấp hơn mức chung của các xe cùng tuổi, cùng số km (nhiều khả năng do xe điện mất giá nhanh trên thị trường xe cũ).")
figure("m04_ridge_he_so.png", 14, "Các hệ số Ridge ảnh hưởng mạnh nhất")
para("Hệ số của các đặc trưng số (đã chuẩn hóa): `age` −0,987, `age²` +0,295, `log_km` +0,705, `log_km_per_year` −0,621, `carseats` +0,031, `mileage_missing` −0,008. Các hệ số này khó đọc riêng lẻ vì `age` và `age²` (hay km và km/năm) cùng mô tả một hiện tượng; cách đọc đúng là xem đường khấu hao (mục 5.6.3).")
h3("5.6.2. Độ quan trọng đặc trưng của Random Forest")
para("Một đặc trưng phân loại bị one-hot thành nhiều cột, nên độ quan trọng của mọi cột thuộc cùng một đặc trưng gốc được cộng lại:")
table(["Đặc trưng", "Thư viện (%)", "Tự cài đặt (%)"], [
    ["Tuổi xe", "31,0", "31,7"], ["Hộp số", "17,7", "17,7"], ["Hãng", "15,8", "16,3"],
    ["Dòng xe", "12,8", "12,7"], ["Kiểu dáng", "7,4", "7,4"], ["Số km", "5,4", "4,7"],
    ["Nhiên liệu", "3,1", "3,2"], ["Số chỗ", "2,7", "2,8"], ["Số km / năm", "2,5", "2,0"],
    ["Xuất xứ", "1,3", "1,3"], ["Km là giá trị điền", "0,2", "0,1"], ["Tình trạng", "0,1", "0,1"],
], [6.0, 4.0, 4.0], caption="Độ quan trọng đặc trưng của Random Forest (gộp theo đặc trưng gốc)")
figure("m12_do_quan_trong.png", 13, "Độ quan trọng đặc trưng: bản thư viện và bản tự cài đặt")
bullet("**Tuổi xe** quan trọng nhất (khoảng 1/3 tổng): khấu hao là yếu tố lớn nhất quyết định giá xe cũ.")
bullet("**Hãng và dòng xe** cộng lại gần ngang tuổi xe: hai xe cùng tuổi nhưng khác dòng có thể chênh nhau hàng chục lần.")
bullet("**Hộp số** đứng thứ hai, cao hơn trực giác. Nhiều khả năng đây là **đại diện gián tiếp**: xe số sàn thường là xe đời cũ, xe tải nhẹ, phân khúc thấp, nên câu hỏi \"số sàn hay tự động?\" tách nhanh nhóm xe rẻ khỏi nhóm xe đắt. Độ quan trọng đo mức đóng góp vào việc chia dữ liệu, không phải tác động nhân quả.")
bullet("**Tình trạng** gần như bằng 0 vì thông tin đã nằm trong `tuổi = 0` và `số km = 0`.")
bullet("Hai bản cài đặt cho **cùng thứ hạng** và gần như cùng tỉ lệ, thêm một bằng chứng rừng tự viết hoạt động đúng.")
h3("5.6.3. Đường khấu hao")
para("Lấy ba mẫu xe phổ biến ở ba phân khúc, cố định mọi thuộc tính, chỉ thay đổi tuổi xe (giả định chạy 15.000 km/năm; tuổi 0 là xe mới, 0 km), rồi xem hai mô hình dự đoán giá:")
figure("m13_duong_khau_hao.png", 16, "Giá dự đoán theo tuổi xe của ba mẫu xe ở ba phân khúc")
bullet("**Ridge** cho đường khấu hao trơn và **cùng một hình dạng** cho mọi mẫu xe (chỉ dịch lên xuống), vì mô hình tuyến tính trên log giá giả định mọi xe mất giá cùng một tỉ lệ % mỗi năm.")
bullet("**Random Forest** cho đường bậc thang với **hình dạng khác nhau giữa các dòng xe**: xe sang (Mercedes C Class) mất giá rất nhanh trong 3-4 năm đầu, khác hẳn xe phổ thông. Đây chính là **tương tác** giữa dòng xe và tuổi xe mà Ridge không biểu diễn được, và là lý do Random Forest chính xác hơn.")
bullet("Các điểm xám là tin thật của cùng dòng xe; độ phân tán dọc lớn cho thấy phần giá mà dữ liệu không giải thích được (phiên bản, trang bị, tình trạng thực tế).")

h2("5.7. Thí nghiệm log giá và xử lý mất cân bằng")
table(["Phương án", "Cỡ train/fold", "MAPE", "MedAPE", "< 200 tr", "200-500", "500-1.000", "1-2 tỷ", "> 2 tỷ"], [
    ["Giá gốc", "8.919", "19,6%", "9,7%", "51,3%", "15,8%", "11,5%", "15,6%", "22,5%"],
    ["**Log giá** (chọn)", "8.919", "16,2%", "9,1%", "35,7%", "12,8%", "10,8%", "16,5%", "27,4%"],
    ["Log + trọng số mẫu", "8.919", "16,3%", "8,8%", "34,9%", "13,6%", "11,2%", "15,3%", "24,1%"],
    ["Log + Oversampling", "9.830", "16,1%", "8,7%", "36,0%", "12,8%", "11,0%", "16,3%", "24,5%"],
    ["Log + Undersampling", "6.925", "16,8%", "9,5%", "35,5%", "14,3%", "11,0%", "16,0%", "26,7%"],
], [3.8, 1.8, 1.4, 1.5, 1.5, 1.5, 1.6, 1.4, 1.4], caption="Thí nghiệm trên Random Forest (5-fold CV trên tập train)", bold_rows=(1,), font=10.5)
figure("m14_log_va_mat_can_bang.png", 16, "MAPE theo phân khúc của các phương án (CV trên train)")
para("**Log giá tốt hơn rõ rệt.** MAPE tổng giảm từ 19,6% xuống 16,2%; phân khúc dưới 200 triệu cải thiện mạnh nhất (51% → 36%). Học trên giá gốc thì sai số bình phương bị xe đắt chi phối, nên mô hình bỏ qua sai số tương đối ở xe rẻ. Đổi lại, giá gốc tốt hơn ở xe trên 2 tỷ (22,5% so với 27,4%), cũng vì lý do đó.")
para("**Các kỹ thuật cân bằng không thay đổi MAPE tổng, nhưng giúp phân khúc hiếm:**")
bullet("MAPE tổng của ba kỹ thuật nằm trong khoảng 16,1-16,8%, so với 16,2% khi không cân bằng, trong mức dao động của CV.")
bullet("**Oversampling** và **trọng số mẫu** giảm sai số ở xe trên 2 tỷ khoảng 3 điểm % (27,4% → 24-25%). Trọng số mẫu phải đổi lại bằng sai số cao hơn ở phân khúc 200-500 triệu (12,8% → 13,6%); oversampling gần như không làm phân khúc nào kém đi.")
bullet("**Undersampling** bỏ khoảng 22% dữ liệu train, MAPE tổng tăng lên 16,8% và gần như không giúp xe sang: bỏ dữ liệu thật thì mất thông tin.")
bullet("Dù đã cân bằng, sai số ở xe trên 2 tỷ vẫn cao hơn gấp đôi phân khúc giữa: nguyên nhân chủ yếu là **thiếu thông tin** (phiên bản, trang bị), không chỉ do ít mẫu. Nhân bản dữ liệu không tạo thêm thông tin mới.")
para("**Quyết định:** mô hình cuối **học trên log giá, không dùng kỹ thuật cân bằng**, vì thước đo chính không đổi và mô hình đơn giản hơn. Nếu ứng dụng ưu tiên định giá xe sang, nên dùng **Random Oversampling** (chỉ trên tập train).")

h2("5.8. Ảnh hưởng của tin đăng lại")
para("Bước tiền xử lý đã xóa các tin trùng hoàn toàn, nhưng cùng một chiếc xe có thể được **đăng lại với giá chênh nhẹ**. Khi chia ngẫu nhiên, một bản rơi vào train và bản kia vào test; Random Forest với lá nhỏ chỉ cần \"nhớ\" giá là đoán đúng. Kiểm tra: tin test nào có một tin train **giống hệt mọi đặc trưng, kể cả số km**?")
table(["Nhóm tin test", "Số tin", "% test", "MAPE Ridge", "MAPE RF"], [
    ["Có bản sao trong train", "391", "14,0%", "14,0%", "10,9%"],
    ["   trong đó xe đã dùng", "247", "8,9%", "14,0%", "10,5%"],
    ["Không có bản sao", "2.397", "86,0%", "19,2%", "16,2%"],
    ["Toàn bộ test", "2.788", "100%", "18,5%", "15,5%"],
], [5.6, 2.2, 2.2, 2.8, 2.8], caption="Sai số trên nhóm tin có và không có bản sao trong tập train")
para("MAPE trên nhóm **không có bản sao** (RF 16,2%) là ước lượng thận trọng hơn cho một chiếc xe hoàn toàn mới với mô hình; con số 15,5% hơi lạc quan. Cách chặt chẽ hơn là chia train/test theo nhóm (`StratifiedGroupKFold`) để mọi bản đăng của một xe nằm cùng một phía.")

h2("5.9. Lưu và sử dụng mô hình")
para("Các mô hình đã huấn luyện được lưu trong thư mục `model/` để dùng lại mà không phải huấn luyện lại:")
table(["File", "Nội dung"], [
    ["`preprocessor_ridge.joblib`, `preprocessor_rf.joblib`", "Bộ mã hóa one-hot + chuẩn hóa của từng mô hình (fit trên train)"],
    ["`ridge_sklearn.joblib`, `random_forest_sklearn.joblib`", "Mô hình thư viện"],
    ["`ridge_scratch.npz`, `random_forest_scratch.npz`", "Trọng số Ridge tự cài đặt; các cây và ngưỡng bin của rừng tự cài đặt (mảng NumPy)"],
    ["`metadata.json`", "Danh sách đặc trưng, bảng gộp nhãn, trung vị số km theo năm, tham số tốt nhất, metric"],
    ["`price_model.py`", "Hàm `load_model` / `predict_price`: nhận thông tin thô của xe, tự dựng đặc trưng như lúc huấn luyện"],
], [7.0, 9.0], caption="Các file mô hình đã lưu", align=["l", "l"], font=11)
para("Khi nạp lại bằng `price_model.py` và truyền thông tin thô của các xe test, dự đoán trùng với notebook (lệch lớn nhất 1,6 × 10⁻¹¹ triệu). Ví dụ dự đoán:")
table(["Xe", "Ridge (TV)", "Ridge (TCĐ)", "RF (TV)", "RF (TCĐ)"], [
    ["Toyota Vios 2018, 80.000 km", "281", "281", "303", "303"],
    ["Ford Ranger 2021, không rõ số km", "596", "596", "515", "536"],
], [5.6, 2.6, 2.6, 2.6, 2.6], caption="Ví dụ dự đoán giá (triệu đồng)")

# ================================================================== CHƯƠNG 6
chapter(6, "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
h2("6.1. Kết quả đạt được")
bullet("Xây dựng hoàn chỉnh quy trình học máy từ đầu đến cuối: thu thập **14.835 tin** từ Chợ Tốt, tiền xử lý còn **13.937 tin** sạch, huấn luyện, đánh giá, diễn giải và đóng gói mô hình để sử dụng.")
bullet("Tiền xử lý dựa trên hiểu biết về cách dữ liệu được tạo ra: phát hiện giá giả, giá trả trước/đặt cọc, xe \"mới\" ghi sai, số km nhập sai đơn vị; điền thiếu theo cơ chế thiếu; gộp nhãn hiếm theo cấp với ngưỡng chọn bằng CV.")
bullet("**Random Forest** là mô hình tốt nhất: MAPE **15,5%**, MedAPE 9,0%, R² (log) 0,891, **80% xe** được định giá lệch không quá 20%. **Ridge** đạt MAPE 18,5%. Chênh lệch khoảng 3 điểm % **có ý nghĩa thống kê** (KTC 95%: 2,1-4,0), và là phần đóng góp của quan hệ phi tuyến và tương tác giữa các đặc trưng.")
bullet("Cả hai mô hình được **tự cài đặt bằng NumPy** và kiểm chứng với `scikit-learn`: Ridge trùng đến sai số làm tròn; Random Forest (histogram + CART + bootstrap + OOB) đạt MAPE 15,7%, khác bản thư viện không có ý nghĩa thống kê.")
bullet("Các quyết định về dữ liệu đều kiểm chứng bằng CV trên tập train: học trên log giá giảm MAPE từ 19,6% xuống 16,2%; trọng số mẫu và oversampling giữ nguyên MAPE tổng nhưng giảm khoảng 3 điểm % sai số ở xe trên 2 tỷ; undersampling làm kết quả kém đi.")
bullet("Yếu tố quyết định giá: tuổi xe (~31%), hộp số (~18%), hãng (~16%), dòng xe (~13%), kiểu dáng (~7%).")

h2("6.2. Hạn chế")
bullet("**Giá rao bán, không phải giá giao dịch:** luôn có phần thương lượng mà mô hình không biết.")
bullet("**Thiếu đặc trưng quan trọng:** phiên bản/trang bị, tình trạng thân vỏ và nội thất, số đời chủ. Đây là nguyên nhân chính của sai số cao ở xe trên 2 tỷ (27%) và xe dưới 200 triệu (35%).")
bullet("**Tin đăng lại:** khoảng 14% tin test có bản sao trong train; trên phần còn lại MAPE của Random Forest là 16,2%.")
bullet("**Rò rỉ nhẹ trong tiền xử lý:** việc điền thiếu dùng thống kê trên toàn bộ dữ liệu trước khi chia (chỉ dựa trên đặc trưng, không dùng giá); bộ lọc giá trả trước dùng giá trên toàn bộ dữ liệu (là bước sửa nhãn). Rủi ro thấp nhưng cần nêu rõ.")
bullet("Giá dự đoán là `exp()` của dự đoán log, tức ước lượng **trung vị** của giá, hơi thấp hơn giá trung bình; phù hợp với MAPE nên không hiệu chỉnh.")
bullet("Dữ liệu là ảnh chụp tại một thời điểm (10/2026); mô hình cần được huấn luyện lại định kỳ khi thị trường thay đổi.")

h2("6.3. Hướng phát triển")
bullet("Crawl thêm phần mô tả tin đăng để trích phiên bản, trang bị, và lọc giá trả trước theo từ khóa (\"trả trước\", \"góp\", \"cọc\").")
bullet("Chia train/test theo nhóm (`StratifiedGroupKFold`) để loại ảnh hưởng của tin đăng lại.")
bullet("Thử **Gradient Boosting** (học tuần tự các cây sửa lỗi của nhau), có thể dùng lại lớp cây đã tự cài đặt.")
bullet("Thử hàm mất mát theo phần trăm để cải thiện hai đầu thang giá.")
bullet("Xây dựng giao diện web nhỏ cho phép người dùng nhập thông tin xe và nhận giá tham khảo, dựa trên `price_model.py`.")

# ================================================================== TÀI LIỆU THAM KHẢO
page_break()
CHAPTER[0] = 7
h1("TÀI LIỆU THAM KHẢO")
refs = [
    "Hoerl, A. E., & Kennard, R. W. (1970). Ridge regression: Biased estimation for nonorthogonal problems. *Technometrics*, 12(1), 55–67.",
    "Breiman, L., Friedman, J., Olshen, R., & Stone, C. (1984). *Classification and Regression Trees*. Wadsworth.",
    "Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32.",
    "Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The Elements of Statistical Learning* (2nd ed.). Springer.",
    "Ke, G., Meng, Q., Finley, T., et al. (2017). LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural Information Processing Systems 30*.",
    "Nesterov, Y. (1983). A method for solving the convex programming problem with convergence rate O(1/k²). *Soviet Mathematics Doklady*, 27, 372–376.",
    "Efron, B., & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall.",
    "Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.",
    "Chợ Tốt Xe. Chuyên mục mua bán ô tô. https://xe.chotot.com/mua-ban-oto (truy cập 25/10/2026).",
]
for k, r in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.first_line_indent = Cm(-1)
    add_runs(p, f"[{k}]\t" + r)

# ================================================================== PHỤ LỤC
page_break()
CHAPTER[0] = "PL"
h1("PHỤ LỤC")
h2("A. Cấu trúc mã nguồn")
table(["Đường dẫn", "Nội dung"], [
    ["`src/crawl_data.ipynb`", "Thu thập dữ liệu từ Chợ Tốt"],
    ["`src/visualize_raw_data.ipynb`", "Biểu đồ khám phá dữ liệu thô"],
    ["`src/preprocess_data.ipynb`", "Tiền xử lý, tạo `clean_data_oto.csv`"],
    ["`src/model.ipynb`", "Ridge và Random Forest (thư viện + tự cài đặt), đánh giá, thí nghiệm, xuất mô hình"],
    ["`src/figures/`", "Các biểu đồ dùng trong báo cáo"],
    ["`model/price_model.py`", "Nạp mô hình và dự đoán giá từ thông tin thô"],
    ["`slides/`", "Slide trình bày"],
], [6.0, 10.0], caption="Cấu trúc thư mục dự án", align=["l", "l"])
h2("B. Cách chạy")
para("Chạy các notebook với thư mục làm việc là `src` theo thứ tự: `crawl_data` (không bắt buộc, đã có dữ liệu), `preprocess_data` (khoảng 2 phút), `model` (khoảng 12 phút, phần lớn là rừng tự cài đặt). Dùng mô hình đã lưu:", indent=False)
code = ['from price_model import load_model, predict_price', 'import pandas as pd',
        'xe = pd.DataFrame([{"carbrand": "Toyota", "carmodel": "Vios", "carorigin": "Việt Nam",',
        '    "condition_ad": "Đã sử dụng", "gearbox": "Tự động", "fuel": "Xăng",',
        '    "cartype": "Sedan", "carseats": 5, "mfdate": 2018, "mileage_km": 80000}])',
        'print(predict_price(load_model("random_forest_sklearn"), xe))   # ~303 triệu']
for line in code:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.left_indent = Cm(0.5)
    r = p.add_run(line); r.font.name = "Consolas"; r.font.size = Pt(9.5)
doc.add_paragraph()
h2("C. Phân công công việc")
table(["Thành viên", "Công việc"], [
    ["<Họ tên SV 1>", "<Nội dung công việc>"],
    ["<Họ tên SV 2>", "<Nội dung công việc>"],
], [5.0, 11.0], caption="Phân công công việc trong nhóm", align=["l", "l"])

OUT.parent.mkdir(exist_ok=True)
doc.save(OUT)
print("Saved", OUT)
