"""Dựng slide báo cáo từ template DUT bằng python-pptx."""
import copy
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu
from lxml import etree

TEMPLATE, OUT = sys.argv[1], sys.argv[2]
FIG = Path("E:/DataScience/src/figures")

BLUE = RGBColor(0x07, 0x52, 0x89)       # xanh Bách Khoa (nền template)
BLUE2 = RGBColor(0x17, 0x5D, 0x98)
YELLOW = RGBColor(0xFF, 0xD4, 0x00)     # vàng đậm, đọc được trên nền trắng khi làm khối
ORANGE = RGBColor(0xEB, 0x68, 0x34)     # nhấn (cùng màu cam trong biểu đồ notebook)
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x5B, 0x67, 0x75)
TINT = RGBColor(0xEA, 0xF2, 0xFA)       # nền thẻ
TINT_Y = RGBColor(0xFF, 0xF6, 0xCC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Arial"

prs = Presentation(TEMPLATE)
tpl = list(prs.slides)
S_TITLE, S_SECTION, S_THANKS = tpl[0], tpl[3], tpl[14]
L_CONTENT = prs.slide_masters[1].slide_layouts[0]      # nền trắng, tòa nhà mờ, sóng vàng, logo
L_SECTION = S_SECTION.slide_layout

order = []          # thứ tự slide cuối cùng


# ---------------------------------------------------------------- tiện ích chung
def strip_placeholders(slide):
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)


def add_slide_number(slide):
    # Thêm placeholder số trang (kế thừa vị trí, kiểu chữ từ layout)
    xml = (
        '<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<p:nvSpPr><p:cNvPr id="900" name="Slide Number"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        '<p:nvPr><p:ph type="sldNum" sz="quarter" idx="12"/></p:nvPr></p:nvSpPr><p:spPr/>'
        '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:fld id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" type="slidenum">'
        '<a:rPr lang="vi-VN"/><a:t>‹#›</a:t></a:fld><a:endParaRPr lang="vi-VN"/></a:p></p:txBody></p:sp>')
    slide.shapes._spTree.append(etree.fromstring(xml))


def style_run(run, size, color=INK, bold=False, italic=False, font=FONT):
    f = run.font
    f.size, f.bold, f.italic, f.name = Pt(size), bold, italic, font
    f.color.rgb = color
    rpr = run._r.get_or_add_rPr()
    rpr.set("lang", "vi-VN")


def set_bullet(p, color=BLUE, indent=0.22):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(Inches(indent))))
    pPr.set("indent", str(-int(Inches(indent))))
    for tag in ("a:buClr", "a:buFont", "a:buChar", "a:buNone"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    buClr = etree.SubElement(pPr, qn("a:buClr"))
    etree.SubElement(buClr, qn("a:srgbClr")).set("val", str(color))
    etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
    etree.SubElement(pPr, qn("a:buChar")).set("char", "•")


def text(slide, x, y, w, h, paras, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, bullets=False, space_after=6, line=1.1, name=None):
    """paras: list; mỗi phần tử là str hoặc list các (text, {opts})."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = anchor
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        p.line_spacing = line
        runs = [(para, {})] if isinstance(para, str) else para
        for t, o in runs:
            r = p.add_run()
            r.text = t
            style_run(r, o.get("size", size), o.get("color", color), o.get("bold", bold), o.get("italic", False))
        if bullets:
            set_bullet(p)
    return tb


def box(slide, x, y, w, h, fill=TINT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, line=None, radius=0.08):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1.25)
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.text_frame.text = ""
    return s


def badge(slide, x, y, d, label, fill=BLUE, color=WHITE, size=16):
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    c.fill.solid(); c.fill.fore_color.rgb = fill
    c.line.fill.background(); c.shadow.inherit = False
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    style_run(r, size, color, bold=True)
    return c


def arrow(slide, x, y, w, h, fill=YELLOW):
    a = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = fill
    a.line.fill.background(); a.shadow.inherit = False
    return a


def picture(slide, path, x, y, w, h, align="center"):
    """Chèn ảnh vừa khung (giữ tỉ lệ)."""
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    px = x + (w - pw) / 2 if align == "center" else x
    py = y + (h - ph) / 2
    pic = slide.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(pw), Inches(ph))
    return pic


def table(slide, x, y, w, rows, col_w, size=12, row_h=0.36, header_fill=BLUE, first_bold=True):
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    tbl = gt.table
    tblPr = tbl._tbl.tblPr
    for attr in ("firstRow", "bandRow"):
        tblPr.set(attr, "0")
    style = tblPr.find(qn("a:tableStyleId"))
    if style is not None:
        style.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"     # No Style, Table Grid
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(row_h)
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if i == 0:
                cell.fill.fore_color.rgb = header_fill
            else:
                cell.fill.fore_color.rgb = WHITE if i % 2 else TINT
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            runs = [(val, {})] if isinstance(val, str) else val
            for t, o in runs:
                r = p.add_run(); r.text = t
                if i == 0:
                    style_run(r, size, WHITE, bold=True)
                else:
                    style_run(r, o.get("size", size), o.get("color", INK),
                              bold=o.get("bold", first_bold and j == 0))
            # viền mảnh xám nhạt
            tcPr = cell._tc.get_or_add_tcPr()
            for side in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
                ln = etree.SubElement(tcPr, qn(side), w="6350")
                sf = etree.SubElement(ln, qn("a:solidFill"))
                etree.SubElement(sf, qn("a:srgbClr")).set("val", "C9D6E3")
    return gt


def style_chart(chart, legend=True, size=12):
    chart.font.name = FONT
    chart.font.size = Pt(size)
    chart.font.color.rgb = MUTED
    chart.has_legend = legend
    if legend:
        chart.legend.position = XL_LEGEND_POSITION.TOP
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(size)
    va = chart.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(0xE3, 0xE8, 0xEE)
    va.format.line.fill.background()
    va.tick_labels.font.size = Pt(size - 1)
    ca = chart.category_axis
    ca.format.line.color.rgb = RGBColor(0xBF, 0xC7, 0xD1)
    ca.tick_labels.font.size = Pt(size)


def content(kicker, title, notes=""):
    s = prs.slides.add_slide(L_CONTENT)
    strip_placeholders(s)
    text(s, 0.6, 0.3, 10.5, 0.35, [kicker.upper()], size=12, color=ORANGE, bold=True, name="Kicker")
    text(s, 0.6, 0.6, 12.1, 0.8, [title], size=28, color=BLUE, bold=True, name="Title")
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    order.append(s)
    return s


def set_para(p, new_text, size=None):
    """Giữ định dạng run đầu tiên của đoạn, thay toàn bộ chữ."""
    runs = p.runs
    if not runs:
        r = p.add_run(); r.text = new_text; return
    runs[0].text = new_text
    if size:
        runs[0].font.size = Pt(size)
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def section(num, title, notes=""):
    s = prs.slides.add_slide(L_SECTION)
    strip_placeholders(s)
    src_csld = S_SECTION._element.find(qn("p:cSld"))
    bg = src_csld.find(qn("p:bg"))
    if bg is not None:
        s._element.find(qn("p:cSld")).insert(0, copy.deepcopy(bg))
    for el in S_SECTION.shapes._spTree.iterchildren():
        if el.tag in (qn("p:sp"), qn("p:cxnSp"), qn("p:pic"), qn("p:grpSp")):
            s.shapes._spTree.append(copy.deepcopy(el))
    tb = [sh for sh in s.shapes if sh.has_text_frame and "PHẦN" in sh.text_frame.text][0]
    tb.width = Inches(5.3)
    ps = tb.text_frame.paragraphs
    set_para(ps[0], f"PHẦN {num}")
    set_para(ps[1], title, size=38)
    for sh in s.shapes:
        if sh.shape_id != tb.shape_id and not sh.has_text_frame or (sh.shape_id != tb.shape_id and not sh.text_frame.text.strip()):
            sh.left = tb.left + tb.width + Inches(0.2)
    for p in ps[2:]:
        p._p.getparent().remove(p._p)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    order.append(s)
    return s


# ---------------------------------------------------------------- 1. Bìa
ps = [sh for sh in S_TITLE.shapes if sh.has_text_frame]
main = max(ps, key=lambda sh: len(sh.text_frame.paragraphs))
paras = main.text_frame.paragraphs
texts = [p.text for p in paras]
set_para(paras[0], "Đề tài môn Khoa học dữ liệu")
set_para(paras[1], "Dự đoán giá ô tô cũ trên Chợ Tốt bằng Ridge Regression và Random Forest", size=34)
for shp in ps:
    for p in shp.text_frame.paragraphs:
        t = p.text.strip()
        if t.startswith("SVTH"):
            set_para(p, "SVTH: <Họ tên SV 1> – <Họ tên SV 2>")
        elif t.upper().startswith("KHO"):
            set_para(p, "GVHD: <Tên giảng viên>")
S_TITLE.notes_slide.notes_text_frame.text = (
    "Giới thiệu đề tài: xây dựng mô hình học máy từ đầu đến cuối để dự đoán giá rao bán ô tô trên Chợ Tốt, "
    "gồm thu thập dữ liệu, tiền xử lý, hai mô hình Ridge và Random Forest (mỗi mô hình có bản thư viện và bản tự cài đặt), "
    "đánh giá và diễn giải.")
order.append(S_TITLE)

# ---------------------------------------------------------------- 2. Nội dung
s = content("Nội dung trình bày", "Năm phần của bài báo cáo",
            "Bài trình bày đi theo đúng quy trình một dự án học máy: bài toán, dữ liệu, tiền xử lý, mô hình, kết quả.")
items = [("01", "Giới thiệu đề tài", "Bài toán, mục tiêu và quy trình thực hiện"),
         ("02", "Thu thập dữ liệu", "Crawl 14.835 tin rao bán ô tô từ Chợ Tốt"),
         ("03", "Tiền xử lý dữ liệu", "Làm sạch, điền thiếu, gộp nhãn, đặc trưng, mất cân bằng"),
         ("04", "Xây dựng mô hình", "Ridge Regression và Random Forest: thư viện và tự cài đặt"),
         ("05", "Kết quả và kết luận", "Đánh giá trên tập test, diễn giải, hạn chế")]
for k, (n, t, d) in enumerate(items):
    y = 1.6 + k * 0.88
    badge(s, 1.2, y, 0.68, n, fill=BLUE if k % 2 == 0 else ORANGE, size=18)
    text(s, 2.1, y - 0.02, 8.5, 0.4, [t], size=20, color=INK, bold=True)
    text(s, 2.1, y + 0.36, 8.5, 0.35, [d], size=14, color=MUTED)

# ---------------------------------------------------------------- PHẦN 1
section(1, "GIỚI THIỆU ĐỀ TÀI")

s = content("Phần 1 · Giới thiệu", "Bài toán: ước lượng giá một chiếc xe từ thông tin trong tin đăng",
            "Người mua và người bán xe cũ đều cần biết một mức giá hợp lý. Đây là bài toán hồi quy: đầu vào là các thuộc tính "
            "mà ai cũng thấy trong tin đăng, đầu ra là giá rao bán tính bằng triệu đồng.")
box(s, 0.6, 1.65, 5.0, 4.25, fill=TINT)
text(s, 0.85, 1.8, 4.6, 0.4, ["Đầu vào: thông tin trong tin đăng"], size=16, color=BLUE, bold=True)
text(s, 0.85, 2.3, 4.6, 3.5, ["Hãng, dòng xe", "Năm sản xuất, số km đã đi", "Hộp số, nhiên liệu",
                              "Kiểu dáng, số chỗ", "Xuất xứ, tình trạng (mới / đã dùng)"],
     size=16, bullets=True, space_after=8)
arrow(s, 5.85, 3.45, 0.9, 0.6)
box(s, 7.0, 1.65, 5.7, 1.95, fill=BLUE)
text(s, 7.25, 1.8, 5.2, 0.4, ["Đầu ra"], size=16, color=YELLOW, bold=True)
text(s, 7.25, 2.2, 5.2, 1.3, [[("Giá rao bán", {"size": 26, "bold": True, "color": WHITE})],
                               [("(triệu đồng) - bài toán hồi quy có giám sát", {"size": 15, "color": WHITE})]])
box(s, 7.0, 3.85, 5.7, 2.05, fill=TINT_Y)
text(s, 7.25, 3.98, 5.2, 0.4, ["Mục tiêu của đề tài"], size=16, color=BLUE, bold=True)
text(s, 7.25, 4.4, 5.3, 1.5, ["Xây dựng mô hình từ đầu đến cuối, có thước đo đánh giá",
                              "Tự cài đặt 2 mô hình, kiểm chứng với thư viện",
                              "Xử lý dữ liệu mất cân bằng theo phân khúc giá"],
     size=14, bullets=True, space_after=5)

s = content("Phần 1 · Giới thiệu", "Quy trình thực hiện",
            "Năm bước. Mỗi quyết định ở bước tiền xử lý và mô hình đều được kiểm chứng bằng số liệu, "
            "và tập test chỉ dùng một lần ở bước đánh giá.")
steps = [("Thu thập", "Crawl Chợ Tốt\n14.835 tin"), ("Tiền xử lý", "Làm sạch, điền thiếu\n13.937 tin"),
         ("Mô hình", "Ridge, Random Forest\nthư viện + tự cài đặt"), ("Đánh giá", "MAPE, R², ±20%\ntheo phân khúc"),
         ("Triển khai", "Lưu mô hình\nprice_model.py")]
for k, (t, d) in enumerate(steps):
    x = 0.6 + k * 2.5
    box(s, x, 2.0, 2.1, 2.6, fill=TINT if k % 2 == 0 else TINT_Y)
    badge(s, x + 0.7, 2.2, 0.7, str(k + 1), fill=BLUE if k % 2 == 0 else ORANGE, size=20)
    text(s, x + 0.1, 3.05, 1.9, 0.45, [t], size=18, color=BLUE, bold=True, align=PP_ALIGN.CENTER)
    text(s, x + 0.1, 3.55, 1.9, 0.95, d.split("\n"), size=13, color=INK, align=PP_ALIGN.CENTER, space_after=2)
    if k < 4:
        arrow(s, x + 2.13, 3.1, 0.32, 0.4)
text(s, 0.6, 4.95, 12.0, 0.9,
     [[("Nguyên tắc chống rò rỉ dữ liệu: ", {"bold": True, "color": BLUE}),
       ("mọi lựa chọn (tham số, biến đổi biến mục tiêu, kỹ thuật cân bằng) đều quyết định bằng cross-validation "
        "hoặc OOB trên tập train. Tập test chỉ dùng một lần để báo cáo kết quả cuối.", {})]], size=15)

# ---------------------------------------------------------------- PHẦN 2
section(2, "THU THẬP DỮ LIỆU")

s = content("Phần 2 · Thu thập dữ liệu", "Crawl 14.835 tin rao bán ô tô từ Chợ Tốt",
            "Code crawl duyệt 750 trang danh sách mới nhất, vào từng tin, đọc các thẻ HTML có thuộc tính itemprop. "
            "Có nghỉ giữa các yêu cầu và cơ chế chạy tiếp khi bị ngắt.")
stats = [("750", "trang danh sách"), ("14.835", "tin rao bán"), ("12", "thuộc tính mỗi tin"), ("25/10/2026", "ngày thu thập")]
for k, (v, l) in enumerate(stats):
    x = 0.6 + k * 3.05
    box(s, x, 1.6, 2.8, 1.45, fill=BLUE if k == 1 else TINT)
    text(s, x, 1.68, 2.8, 0.75, [v], size=32, color=WHITE if k == 1 else BLUE, bold=True, align=PP_ALIGN.CENTER)
    text(s, x, 2.42, 2.8, 0.45, [l], size=14, color=WHITE if k == 1 else MUTED, align=PP_ALIGN.CENTER)
text(s, 0.6, 3.35, 6.0, 0.4, ["Cách thu thập"], size=18, color=BLUE, bold=True)
text(s, 0.6, 3.8, 6.0, 2.3, ["requests + BeautifulSoup đọc thẻ itemprop của từng tin",
                             "Bỏ URL trùng (tin ưu tiên lặp lại ở mọi trang)",
                             "Chạy tiếp được khi bị ngắt (bỏ qua URL đã có)"], size=15, bullets=True)
text(s, 6.9, 3.35, 5.8, 0.4, ["Thu thập có trách nhiệm"], size=18, color=BLUE, bold=True)
text(s, 6.9, 3.8, 5.8, 2.3, ["Nghỉ 0,5 giây mỗi tin, 1 giây mỗi trang",
                             "Tự lùi thời gian khi bị trả mã 403 / 429",
                             "Chỉ lấy thông tin công khai, không lấy liên hệ người bán"], size=15, bullets=True)

s = content("Phần 2 · Thu thập dữ liệu", "Từ điển dữ liệu: biết cột nào người bán gõ tự do",
            "Cột chọn từ danh sách thì sạch, không lỗi chính tả. Hai cột gõ tự do là số km và giá, cũng là hai nguồn lỗi chính "
            "cần kiểm tra ở bước tiền xử lý. URL chứa vị trí tin đăng.")
rows = [["Cột", "Ý nghĩa", "Người bán nhập", "Xử lý"],
        ["carbrand / carmodel", "Hãng / dòng xe", "chọn từ danh sách", "gộp nhãn hiếm theo cấp"],
        ["mfdate", "Năm sản xuất", "chọn (có \"trước 1980\")", "→ tuổi xe = 2026 − năm"],
        ["mileage_v2", "Số km đã đi", [("gõ tự do", {"color": ORANGE, "bold": True})], "kiểm tra km vô lý, điền thiếu"],
        ["gearbox / fuel", "Hộp số / nhiên liệu", "chọn (3 / 4 giá trị)", "one-hot"],
        ["cartype / carseats", "Kiểu dáng / số chỗ", "chọn, không bắt buộc", "điền theo dòng xe"],
        ["carorigin", "Xuất xứ", "chọn, không bắt buộc", "thiếu 40% → \"Không rõ\""],
        ["condition_ad", "Tình trạng", "Mới / Đã sử dụng", "sửa xe \"Mới\" quá 3 năm tuổi"],
        ["veh_warranty_policy", "Bảo hành", "một giá trị duy nhất", "bỏ cột"],
        ["price", "Giá rao bán (đồng)", [("gõ tự do", {"color": ORANGE, "bold": True})], "biến mục tiêu, loại giá sai"],
        ["url", "Đường dẫn tin", "tự sinh, chứa tỉnh/thành", "trích tỉnh/thành rồi bỏ"]]
table(s, 0.6, 1.55, 12.1, rows, [2.7, 2.7, 3.1, 3.6], size=13, row_h=0.41)

# ---------------------------------------------------------------- PHẦN 3
section(3, "TIỀN XỬ LÝ DỮ LIỆU")

s = content("Phần 3 · Khám phá dữ liệu", "Giá lệch phải mạnh nên mô hình học trên log(giá)",
            "Đa số xe 200-800 triệu, một ít xe vài tỷ. Học trên giá gốc thì vài xe đắt lấn át. Log biến sai số tuyệt đối "
            "thành sai số tương đối, khớp với thước đo chính MAPE. Phần 5 kiểm chứng bằng số liệu: MAPE 16,2% so với 19,6%.")
picture(s, FIG / "04_phan_bo_gia.png", 0.6, 1.5, 6.6, 4.5)
box(s, 7.6, 1.6, 5.1, 1.5, fill=BLUE)
text(s, 7.6, 1.68, 5.1, 0.7, [[("5,08  →  −0,20", {"size": 30, "bold": True, "color": YELLOW})]], align=PP_ALIGN.CENTER)
text(s, 7.6, 2.4, 5.1, 0.5, ["độ lệch của giá trước và sau khi lấy log"], size=14, color=WHITE, align=PP_ALIGN.CENTER)
text(s, 7.6, 3.35, 5.1, 2.7, ["Mô hình học ln(giá), dự đoán xong dùng exp() để ra triệu đồng",
                              "Lệch 10% ở xe 200 triệu và ở xe 2 tỷ được phạt như nhau",
                              "Mọi thước đo vẫn tính trên giá thật"], size=15, bullets=True, space_after=10)

s = content("Phần 3 · Khám phá dữ liệu", "Tuổi xe và thương hiệu quyết định phần lớn giá",
            "Giá trung vị tăng đều theo năm sản xuất. Xe sang Đức có giá và độ phân tán cao hơn hẳn xe phổ thông.")
picture(s, FIG / "08_gia_theo_nam.png", 0.5, 1.5, 6.1, 3.7)
picture(s, FIG / "05_gia_theo_hang.png", 6.75, 1.5, 6.1, 3.7)
text(s, 0.6, 5.3, 5.9, 0.8, ["Xe đời 2001 trung vị khoảng 73 triệu, xe đời 2026 khoảng 624 triệu"], size=14, color=MUTED)
text(s, 6.85, 5.3, 5.9, 0.8, ["BMW, Mercedes đắt và phân tán rộng; Suzuki, Chevrolet rẻ và tập trung"], size=14, color=MUTED)

s = content("Phần 3 · Làm sạch", "Từ 14.835 tin thô còn 13.937 tin sạch (giữ 93,9%)",
            "Mỗi bước loại bỏ đều có lý do cụ thể. Không cắt ngoại lệ theo phần trăm máy móc: xe siêu sang giá vài tỷ là thật nên được giữ.")
funnel = [("14.835", "tin thô"), ("−691", "tin trùng lặp\n(đăng lại, đại lý)"), ("−64", "giá thiếu, < 20 triệu\nhoặc > 10 tỷ"),
          ("−14", "giá giả\n123.456.789"), ("−129", "giá trả trước\n/ đặt cọc"), ("13.937", "tin sạch")]
for k, (v, l) in enumerate(funnel):
    x = 0.6 + k * 2.05
    end = k in (0, 5)
    box(s, x, 1.85, 1.8, 2.3, fill=BLUE if end else TINT)
    text(s, x, 2.05, 1.8, 0.7, [v], size=28 if end else 26, color=YELLOW if end else ORANGE, bold=True, align=PP_ALIGN.CENTER)
    text(s, x + 0.05, 2.85, 1.7, 1.1, l.split("\n"), size=13, color=WHITE if end else INK, align=PP_ALIGN.CENTER, space_after=0)
    if k < 5:
        arrow(s, x + 1.82, 2.85, 0.22, 0.3)
text(s, 0.6, 4.5, 12.1, 0.4, ["Không xóa dòng, chỉ sửa giá trị"], size=17, color=BLUE, bold=True)
text(s, 0.6, 4.95, 12.1, 1.2, ["578 giá trị km vô lý (> 500.000 km, < 100 km ở xe ≥ 2 tuổi, > 100.000 km/năm) → coi là thiếu rồi điền lại",
                              "6 xe ghi \"Mới\" nhưng hơn 3 năm tuổi (ví dụ Tucson 2011) → đổi thành \"Đã sử dụng\""],
     size=15, bullets=True)

s = content("Phần 3 · Làm sạch", "Biến mục tiêu sai là lỗi nguy hiểm nhất",
            "Giá là ô gõ tự do. Một tin ghi tiền trả trước thay vì giá xe làm mô hình bị chấm sai hàng trăm phần trăm. "
            "Quy tắc so với chính mẫu xe đó, không dùng một ngưỡng tuyệt đối.")
cards = [("64 tin", "Lỗi nhập liệu", "Giá thiếu, dưới 20 triệu hoặc trên 10 tỷ: gõ thiếu / thừa số 0. Không biết giá đúng nên loại."),
         ("14 tin", "Giá giả", "Dãy số liên tiếp 123.456.789: người bán không muốn công khai giá. Giữ 399.999.999 (định giá tâm lý)."),
         ("129 tin", "Giá trả trước / đặt cọc", "Giá < 30% trung vị của xe cùng hãng, dòng, năm (nhóm ≥ 3 xe). 94% số tin này có giá < 200 triệu.")]
for k, (v, t, d) in enumerate(cards):
    x = 0.6 + k * 4.1
    box(s, x, 1.6, 3.8, 2.75, fill=TINT)
    text(s, x + 0.25, 1.75, 3.3, 0.7, [v], size=30, color=ORANGE, bold=True)
    text(s, x + 0.25, 2.45, 3.3, 0.45, [t], size=17, color=BLUE, bold=True)
    text(s, x + 0.25, 2.95, 3.35, 1.35, [d], size=15, color=INK)
box(s, 0.6, 4.6, 12.1, 1.0, fill=TINT_Y)
text(s, 0.85, 4.68, 11.6, 0.85, [[("Ví dụ: ", {"bold": True, "color": BLUE}),
                                   ("Toyota Fortuner 2026 \"mới\" rao 125 triệu, trong khi trung vị của xe cùng đời là 1.249 triệu. "
                                    "Đây là tiền trả trước, không phải giá xe.", {})]], size=15, anchor=MSO_ANCHOR.MIDDLE)

s = content("Phần 3 · Giá trị thiếu", "Hiểu vì sao thiếu trước khi điền",
            "Số km thiếu có cấu trúc: trang tin xe mới không có ô số km, nên điền 0 là đúng bản chất. Điền trung vị sẽ biến xe mới "
            "thành xe đã chạy 66.000 km. Kiểu dáng và số chỗ do dòng xe quyết định nên điền theo dòng xe.")
rows = [["Cột", "% thiếu", "Vì sao thiếu", "Cách xử lý"],
        ["Số km", "12,2%", "Xe mới không có ô số km", "Xe mới = 0 km; 814 xe cũ: trung vị theo năm SX + cột đánh dấu mileage_missing"],
        ["Kiểu dáng", "32,9%", "Không bắt buộc nhập", "Mode theo hãng + dòng xe (4.336 tin); không suy ra được → \"Không rõ\" (243)"],
        ["Số chỗ", "24,9%", "Không bắt buộc nhập", "Mode theo dòng xe, rồi theo hãng"],
        ["Xuất xứ", "40,5%", "Không bắt buộc, quá nhiều", "Giữ nhãn riêng \"Không rõ\", không đoán"],
        ["Giá", "1 tin", "Biến mục tiêu", "Xóa dòng, không bao giờ điền đáp án"]]
table(s, 0.6, 1.6, 12.1, rows, [1.6, 1.2, 3.2, 6.1], size=14, row_h=0.62)
text(s, 0.6, 5.5, 12.1, 0.6, [[("Vì sao kiểu dáng không lùi về hãng: ", {"bold": True, "color": BLUE}),
                              ("một hãng bán cả sedan, SUV, bán tải; đoán theo hãng là đoán mò.", {})]], size=14)

s = content("Phần 3 · Gộp nhãn hiếm", "Gộp nhãn hiếm theo cấp: dòng xe → hãng → nhóm hãng",
            "Cách cũ dồn mọi dòng hiếm của mọi hãng vào một nhãn 'Dòng khác', chiếm 65% số xe trên 2 tỷ. Cách mới lùi về hãng gần nhất "
            "còn đủ mẫu. Ngưỡng 30/10 chọn bằng 5-fold CV trên tập train.")
levels = [("Dòng xe ≥ 10 tin", "giữ nguyên", "Toyota Vios"),
          ("Dòng xe hiếm", "→ \"<Hãng> - dòng khác\"", "Mercedes Benz - dòng khác"),
          ("Hãng < 30 tin", "→ nhóm cao cấp / phổ thông", "Bentley → Hãng cao cấp khác")]
for k, (a, b, ex) in enumerate(levels):
    y = 1.6 + k * 1.2
    badge(s, 0.6, y + 0.15, 0.6, str(k + 1), fill=BLUE, size=16)
    box(s, 1.35, y, 4.6, 1.0, fill=TINT)
    text(s, 1.5, y + 0.05, 4.4, 0.45, [[(a + " ", {"bold": True, "color": BLUE}), (b, {})]], size=15)
    text(s, 1.5, y + 0.5, 4.4, 0.4, ["Ví dụ: " + ex], size=13, color=MUTED)
text(s, 0.6, 5.3, 5.4, 0.8, [[("69 hãng → 28 nhóm;  509 dòng → 214 nhóm", {"bold": True, "color": BLUE})]], size=15)
cd = CategoryChartData()
cd.categories = ["Ridge: tổng", "Ridge: xe > 2 tỷ", "RF: tổng", "RF: xe > 2 tỷ"]
cd.add_series("Cách cũ", (21.9, 43.0, 16.3, 29.2))
cd.add_series("Cách mới (chọn)", (18.9, 32.2, 16.1, 28.7))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6.3), Inches(1.5), Inches(6.4), Inches(4.5), cd)
ch = gf.chart
style_chart(ch)
ch.has_title = True
ch.chart_title.text_frame.text = "MAPE (%) - 5-fold CV trên train"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
ch.chart_title.text_frame.paragraphs[0].runs[0].font.color.rgb = INK
for ser, col in zip(ch.series, (RGBColor(0xB8, 0xC4, 0xD2), BLUE)):
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = col
plot = ch.plots[0]
plot.gap_width = 60
plot.has_data_labels = True
plot.data_labels.number_format = '0.0'
plot.data_labels.number_format_is_linked = False
plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
plot.data_labels.font.size = Pt(12)
plot.data_labels.font.color.rgb = INK

s = content("Phần 3 · Đặc trưng", "Đặc trưng đầu vào: biến đổi theo bản chất từng mô hình",
            "Ridge chỉ cộng các hiệu ứng tuyến tính, nên cần age² và log(km) để biểu diễn khấu hao nhanh những năm đầu. "
            "Cây chỉ so sánh ngưỡng, các biến đổi đơn điệu không thay đổi gì.")
rows = [["Nhóm đặc trưng", "Ridge Regression", "Random Forest"],
        ["Phân loại (one-hot)", "hãng, dòng xe, xuất xứ, tình trạng, hộp số, nhiên liệu, kiểu dáng", "giống Ridge"],
        ["Tuổi xe", "tuổi, tuổi²", "tuổi"],
        ["Số km", "log(1+km), log(1+km/năm)", "km, km/năm (giữ nguyên)"],
        ["Khác", "số chỗ, mileage_missing", "số chỗ, mileage_missing"],
        ["Chuẩn hóa", "StandardScaler (phạt L2 công bằng)", "không cần"],
        ["Số cột sau mã hóa", "278", "277"]]
table(s, 0.6, 1.6, 12.1, rows, [2.8, 5.3, 4.0], size=14, row_h=0.5)
box(s, 0.6, 5.3, 12.1, 0.8, fill=TINT_Y)
text(s, 0.85, 5.35, 11.6, 0.7, [[("Không dùng: ", {"bold": True, "color": BLUE}),
                                 ("giá (đáp án), năm SX (trùng tuổi xe), tỉnh/thành (CV cho thấy gần như không cải thiện: MAPE RF 16,10% → 16,04%).", {})]],
     size=14, anchor=MSO_ANCHOR.MIDDLE)

s = content("Phần 3 · Mất cân bằng", "Dữ liệu mất cân bằng theo phân khúc giá",
            "Biến mục tiêu liên tục nên không có lớp thiểu số. Mất cân bằng thể hiện ở mật độ dữ liệu: rất nhiều xe 200 triệu - 1 tỷ, "
            "rất ít xe trên 2 tỷ. Mô hình tối ưu sai số trung bình sẽ học kém ở vùng thưa.")
cd = CategoryChartData()
cd.categories = ["< 200 triệu", "200-500", "500-1.000", "1-2 tỷ", "> 2 tỷ"]
cd.add_series("Số tin", (1972, 5907, 4529, 1071, 458))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.5), Inches(1.5), Inches(7.2), Inches(4.6), cd)
ch = gf.chart
style_chart(ch, legend=False)
ch.has_title = True
ch.chart_title.text_frame.text = "Số tin theo phân khúc giá (13.937 tin)"
r0 = ch.chart_title.text_frame.paragraphs[0].runs[0]
r0.font.size = Pt(14); r0.font.bold = True; r0.font.color.rgb = INK
ser = ch.series[0]
ser.format.fill.solid(); ser.format.fill.fore_color.rgb = BLUE
pt = ser.points[4]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = ORANGE
plot = ch.plots[0]; plot.gap_width = 50
plot.has_data_labels = True
plot.data_labels.number_format = '#,##0'; plot.data_labels.number_format_is_linked = False
plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
plot.data_labels.font.size = Pt(12); plot.data_labels.font.color.rgb = INK
box(s, 8.1, 1.6, 4.6, 1.5, fill=BLUE)
text(s, 8.1, 1.68, 4.6, 0.75, [[("12,9 lần", {"size": 32, "bold": True, "color": YELLOW})]], align=PP_ALIGN.CENTER)
text(s, 8.2, 2.42, 4.4, 0.6, ["phân khúc đông nhất so với xe trên 2 tỷ (3,3%)"], size=13, color=WHITE, align=PP_ALIGN.CENTER)
text(s, 8.1, 3.35, 4.6, 0.4, ["Cách xử lý"], size=17, color=BLUE, bold=True)
text(s, 8.1, 3.8, 4.6, 2.3, ["Học trên log(giá) để giảm lệch",
                             "Chia train/test phân tầng theo phân khúc",
                             "Thử trọng số mẫu, oversampling, undersampling: chỉ trong phần train của từng fold"],
     size=14, bullets=True, space_after=8)

# ---------------------------------------------------------------- PHẦN 4
section(4, "XÂY DỰNG MÔ HÌNH")

s = content("Phần 4 · Thiết kế thực nghiệm", "Chia dữ liệu và chọn tham số không dùng tập test",
            "Tập test không tham gia bất kỳ lựa chọn nào. Không cần tập validation riêng: 5-fold CV ổn định hơn với chỉ khoảng 460 xe trên 2 tỷ.")
picture(s, FIG / "m01_chia_train_test.png", 0.5, 1.55, 6.9, 3.4)
text(s, 0.6, 5.1, 6.7, 0.9, ["Chia phân tầng: mỗi phân khúc giá có cùng tỉ lệ ở train (11.149 tin) và test (2.788 tin)"],
     size=14, color=MUTED)
steps = [("Train 80%", "học mô hình, chọn tham số bằng 5-fold CV (Ridge) hoặc OOB (rừng tự viết)"),
         ("Test 20%", "dùng đúng một lần để báo cáo kết quả cuối"),
         ("Hai bản cài đặt", "thư viện scikit-learn làm chuẩn; bản tự viết bằng NumPy được kiểm chứng với nó")]
for k, (t, d) in enumerate(steps):
    y = 1.65 + k * 1.45
    badge(s, 7.8, y, 0.6, str(k + 1), fill=BLUE if k != 1 else ORANGE)
    text(s, 8.6, y - 0.05, 4.1, 0.4, [t], size=17, color=BLUE, bold=True)
    text(s, 8.6, y + 0.38, 4.1, 0.95, [d], size=14)

s = content("Phần 4 · Thước đo", "Sáu thước đo, MAPE là thước đo chính",
            "MAPE là chính vì lệch 100 triệu là nhỏ với xe 3 tỷ nhưng rất lớn với xe 150 triệu. Luôn báo thêm MAPE theo từng phân khúc giá.")
metrics = [("MAPE", "Sai số phần trăm trung bình. Thước đo chính", True),
           ("MedAPE", "Trung vị sai số %: sai số \"điển hình\"", False),
           ("MAE", "Trung bình đoán lệch bao nhiêu triệu", False),
           ("RMSE", "Phạt nặng lỗi lớn (thường ở xe sang)", False),
           ("R² (log)", "Tỉ lệ biến thiên log giá được giải thích", False),
           ("±10% / ±20%", "Tỉ lệ xe được định giá lệch không quá 10% / 20%", False)]
for k, (m, d, main_) in enumerate(metrics):
    x = 0.6 + (k % 3) * 4.1
    y = 1.6 + (k // 3) * 2.0
    box(s, x, y, 3.8, 1.75, fill=BLUE if main_ else TINT)
    text(s, x + 0.25, y + 0.15, 3.3, 0.6, [m], size=24, color=YELLOW if main_ else BLUE, bold=True)
    text(s, x + 0.25, y + 0.8, 3.35, 0.9, [d], size=14, color=WHITE if main_ else INK)
text(s, 0.6, 5.65, 12.1, 0.45, [[("Mốc so sánh (baseline): ", {"bold": True, "color": BLUE}),
                                 ("luôn đoán giá trung vị của tập train. Mô hình phải tốt hơn hẳn mức này mới có ý nghĩa.", {})]], size=14)

s = content("Phần 4 · Mô hình 1", "Ridge Regression: hồi quy tuyến tính có phạt L2",
            "Có khoảng 278 cột sau one-hot, nhiều cột tương quan mạnh như Toyota và Toyota Vios. Khoản phạt kéo hệ số về gần 0 để mô hình ổn định. "
            "Alpha chọn bằng 5-fold CV: 0,56.")
box(s, 0.6, 1.6, 6.0, 1.6, fill=TINT)
text(s, 0.8, 1.7, 5.6, 0.4, ["Hàm mất mát"], size=15, color=BLUE, bold=True)
text(s, 0.8, 2.15, 5.6, 0.9, [[("J(w) = ", {}), ("(1/2n) Σ (yᵢ − ŷᵢ)²", {"bold": True}), ("  +  ", {}),
                               ("(α/2) Σ wⱼ²", {"bold": True, "color": ORANGE})],
                              [("sai số dự đoán            khoản phạt trọng số", {"size": 12, "color": MUTED})]], size=20)
text(s, 0.6, 3.45, 6.0, 2.6, ["ŷ = w₀ + w₁x₁ + … + wₚxₚ, dự đoán log giá",
                              "α nhỏ: gần như không phạt, dễ overfit; α lớn: hệ số bị ép về 0, underfit",
                              "Diễn giải: hệ số w nghĩa là giá thay đổi khoảng (eʷ − 1) × 100%"], size=15, bullets=True, space_after=9)
picture(s, FIG / "m02_ridge_chon_alpha.png", 6.9, 1.6, 5.9, 4.3)

s = content("Phần 4 · Mô hình 1", "Ridge tự cài đặt: hai cách giải, trùng khớp thư viện",
            "Nghiệm đóng giải trực tiếp hệ phương trình tuyến tính. Gradient descent có momentum Nesterov dùng để minh họa quá trình tối ưu "
            "và kiểm chứng chéo. K-fold tự viết chọn đúng cùng alpha với GridSearchCV.")
box(s, 0.6, 1.6, 3.9, 1.5, fill=TINT)
text(s, 0.8, 1.68, 3.6, 0.4, ["1. Nghiệm đóng"], size=16, color=BLUE, bold=True)
text(s, 0.8, 2.1, 3.6, 0.9, ["(AᵀA/n + αI′) w = Aᵀy/n", "giải một lần, chính xác"], size=14, space_after=2)
box(s, 0.6, 3.3, 3.9, 1.5, fill=TINT)
text(s, 0.8, 3.38, 3.6, 0.4, ["2. Gradient descent"], size=16, color=BLUE, bold=True)
text(s, 0.8, 3.8, 3.6, 0.9, ["momentum Nesterov, bước học 1/L", "5.000 vòng lặp, 23 giây"], size=14, space_after=2)
box(s, 0.6, 5.0, 3.9, 1.05, fill=BLUE)
text(s, 0.8, 5.05, 3.6, 0.95, [[("Lệch hệ số so với sklearn: ", {"color": WHITE}), ("2,8 × 10⁻¹¹", {"bold": True, "color": YELLOW})],
                               [("MAPE test: 18,5% cả hai bản", {"color": WHITE})]], size=14, anchor=MSO_ANCHOR.MIDDLE, space_after=2)
picture(s, FIG / "m03_ridge_kiem_chung.png", 4.8, 1.6, 8.0, 4.4)

s = content("Phần 4 · Mô hình 2", "Random Forest: lấy trung bình nhiều cây khác nhau",
            "Một cây sâu học thuộc dữ liệu train nên phương sai cao. Rừng huấn luyện mỗi cây trên một mẫu bootstrap, mỗi lần chia nút chỉ xét "
            "một phần đặc trưng ngẫu nhiên, rồi lấy trung bình. Khoảng 37% mẫu không được chọn (out-of-bag) dùng để ước lượng sai số.")
box(s, 0.6, 2.3, 1.9, 1.15, fill=BLUE)
text(s, 0.6, 2.33, 1.9, 1.1, ["Tập train", "11.149 xe"], size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space_after=2)
for k, lab in enumerate(["Bootstrap 1", "Bootstrap 2", "…", "Bootstrap N"]):
    y = 1.55 + k * 0.68
    arrow(s, 2.6, y + 0.13, 0.5, 0.28, fill=YELLOW)
    box(s, 3.2, y, 1.9, 0.55, fill=TINT)
    text(s, 3.2, y + 0.02, 1.9, 0.5, [lab], size=13, color=BLUE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    arrow(s, 5.2, y + 0.13, 0.4, 0.28, fill=YELLOW)
    box(s, 5.7, y, 1.8, 0.55, fill=TINT_Y)
    text(s, 5.7, y + 0.02, 1.8, 0.5, ["Cây " + ("N" if k == 3 else ("…" if k == 2 else str(k + 1)))], size=13, color=INK, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
arrow(s, 7.65, 2.65, 0.5, 0.45, fill=ORANGE)
box(s, 8.3, 2.3, 1.9, 1.15, fill=ORANGE)
text(s, 8.3, 2.33, 1.9, 1.1, ["Lấy trung bình", "dự đoán"], size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space_after=2)
text(s, 10.5, 1.6, 2.3, 2.6, [[("Mỗi nút: ", {"bold": True, "color": BLUE}), ("chọn đặc trưng và ngưỡng giảm SSE nhiều nhất", {})],
                              [("gain = S²ₗ/nₗ + S²ᵣ/nᵣ − S²/n", {"bold": True, "size": 13})]], size=13, space_after=8)
rows = [["Tham số", "Tác dụng", "Giá trị chọn (thư viện)"],
        ["n_estimators", "số cây; nhiều hơn thì ổn định hơn rồi bão hòa", "300"],
        ["max_depth", "độ sâu tối đa của cây", "30"],
        ["min_samples_leaf", "số mẫu tối thiểu ở mỗi lá", "1"],
        ["max_features", "tỉ lệ đặc trưng xét mỗi lần chia", "0,5"]]
table(s, 0.6, 4.45, 12.1, rows, [2.6, 6.5, 3.0], size=13, row_h=0.32)

s = content("Phần 4 · Mô hình 2", "Random Forest tự cài đặt bằng NumPy",
            "Kỹ thuật histogram: chia mỗi đặc trưng thành 32 bin một lần, mỗi nút chỉ cần đếm bằng bincount rồi cộng dồn là có gain "
            "của mọi ngưỡng cùng lúc. Kiểm chứng thành phần: một cây tự viết cho kết quả gần như cây của sklearn.")
cls = [("Binner", "chia đặc trưng thành 32 bin theo phân vị"),
       ("RegressionTreeScratch", "cây CART: tìm phép chia giảm SSE lớn nhất bằng histogram"),
       ("RandomForestScratch", "bootstrap + chọn ngẫu nhiên đặc trưng + trung bình, có OOB và độ quan trọng")]
for k, (c, d) in enumerate(cls):
    y = 1.6 + k * 1.05
    box(s, 0.6, y, 6.0, 0.9, fill=TINT)
    text(s, 0.8, y + 0.05, 5.7, 0.4, [c], size=15, color=BLUE, bold=True)
    text(s, 0.8, y + 0.45, 5.7, 0.4, [d], size=13)
text(s, 0.6, 4.85, 6.0, 1.2, [[("Kiểm chứng: ", {"bold": True, "color": BLUE}),
                              ("dựng cây đơn cùng tham số (lá ≥ 5 mẫu, không giới hạn độ sâu) với cả hai bản, so số nút và R² trên cùng dữ liệu.", {})]],
     size=14)
text(s, 7.0, 1.6, 5.7, 0.4, ["Một cây: tự cài đặt so với thư viện"], size=16, color=BLUE, bold=True)
rows = [["", "Thư viện", "Tự cài đặt"],
        ["Số nút", "3.481", "3.429"],
        ["R² (log) train", "0,929", "0,927"],
        ["R² (log) test", "0,842", "0,851"],
        ["MAPE test", "19,6%", "18,6%"],
        ["Thời gian", "0,3 giây", "1,7 giây"]]
table(s, 7.0, 2.1, 5.7, rows, [2.3, 1.7, 1.7], size=14, row_h=0.5)
text(s, 7.0, 5.25, 5.7, 0.8, ["R² train cao hơn hẳn R² test: một cây có phương sai cao, đó là lý do cần rừng"], size=13, color=MUTED)

s = content("Phần 4 · Mô hình 2", "Từ một cây đến một rừng: sai số giảm 24%",
            "Rừng tự viết chọn tham số bằng OOB trên 6 cấu hình (mỗi cấu hình 30 cây), rồi huấn luyện 100 cây trong khoảng 2 phút. "
            "OOB R² 0,892, rất sát bản thư viện 0,896.")
picture(s, FIG / "m05_rf_so_cay.png", 0.5, 1.5, 7.6, 4.5)
stats = [("0,346 → 0,263", "OOB RMSE: 1 cây → 100 cây"), ("0,892", "OOB R² tự cài đặt (thư viện: 0,896)"),
         ("30 / 2 / 0,5", "độ sâu / lá tối thiểu / tỉ lệ đặc trưng (chọn bằng OOB)")]
for k, (v, l) in enumerate(stats):
    y = 1.6 + k * 1.45
    box(s, 8.4, y, 4.3, 1.25, fill=BLUE if k == 0 else TINT)
    text(s, 8.55, y + 0.08, 4.0, 0.6, [v], size=24, color=YELLOW if k == 0 else BLUE, bold=True)
    text(s, 8.55, y + 0.68, 4.0, 0.5, [l], size=13, color=WHITE if k == 0 else INK)

# ---------------------------------------------------------------- PHẦN 5
section(5, "KẾT QUẢ VÀ ĐÁNH GIÁ")

s = content("Phần 5 · Kết quả", "Random Forest: sai số 15,5%, 80% xe lệch không quá 20%",
            "Cả hai mô hình vượt xa baseline. Bản tự cài đặt gần như trùng bản thư viện. Đánh giá trên 2.788 tin test, dùng một lần.")
big = [("83,5%", "Baseline", RGBColor(0x9A, 0xA0, 0xA6)), ("18,5%", "Ridge", BLUE), ("15,5%", "Random Forest", ORANGE)]
for k, (v, l, col) in enumerate(big):
    x = 0.6 + k * 4.1
    box(s, x, 1.55, 3.8, 1.45, fill=col)
    text(s, x, 1.6, 3.8, 0.8, [v], size=36, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    text(s, x, 2.4, 3.8, 0.45, [l + " · MAPE"], size=14, color=WHITE, align=PP_ALIGN.CENTER)
rows = [["Mô hình", "MAPE", "MedAPE", "MAE (triệu)", "R² (log)", "Lệch ≤ 20%", "Huấn luyện"],
        ["Baseline (trung vị)", "83,5%", "40,0%", "337", "0,00", "26%", "-"],
        ["Ridge - thư viện", "18,5%", "10,7%", "120", "0,873", "75%", "0,04 giây"],
        ["Ridge - tự cài đặt", "18,5%", "10,7%", "120", "0,873", "75%", "0,03 giây"],
        [[("Random Forest - thư viện", {"bold": True, "color": ORANGE})], [("15,5%", {"bold": True})], "9,0%", "102", "0,891", "80%", "9 giây"],
        ["Random Forest - tự cài đặt", "15,7%", "9,0%", "106", "0,887", "80%", "2 phút"]]
table(s, 0.6, 3.25, 12.1, rows, [3.4, 1.3, 1.4, 1.6, 1.3, 1.5, 1.6], size=14, row_h=0.46)

s = content("Phần 5 · Kết quả", "Mô hình tốt ở phân khúc giữa, kém ở hai đầu thang giá",
            "Phân khúc 200 triệu - 1 tỷ chiếm khoảng 75% thị trường, sai số khoảng 11%. Xe dưới 200 triệu: chênh vài chục triệu đã là phần trăm lớn. "
            "Xe trên 2 tỷ: ít dữ liệu và thiếu thông tin phiên bản, trang bị.")
picture(s, FIG / "m07_mape_phan_khuc.png", 0.5, 1.5, 12.3, 3.6)
cards = [("~11%", "sai số ở phân khúc 200 triệu - 1 tỷ (75% thị trường)"),
         ("35%", "xe dưới 200 triệu: giá thấp, tình trạng xe cũ rất khác nhau"),
         ("27%", "xe trên 2 tỷ: chỉ 3% dữ liệu, thiếu phiên bản / trang bị")]
for k, (v, d) in enumerate(cards):
    x = 0.6 + k * 4.1
    box(s, x, 5.2, 3.8, 0.85, fill=TINT)
    text(s, x + 0.15, 5.25, 1.2, 0.75, [v], size=22, color=ORANGE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 1.35, 5.25, 2.35, 0.75, [d], size=12, anchor=MSO_ANCHOR.MIDDLE, space_after=0)

s = content("Phần 5 · Kết quả", "Chênh lệch có ý nghĩa thống kê không? Bootstrap ghép cặp",
            "Lấy mẫu lại tập test 1.000 lần, mỗi lần tính hiệu MAPE của hai mô hình trên cùng các xe. Khoảng tin cậy của hiệu không chứa 0 "
            "nghĩa là chênh lệch có ý nghĩa.")
picture(s, FIG / "m10_khoang_tin_cay.png", 0.4, 1.7, 7.5, 3.4)
text(s, 0.6, 5.25, 7.2, 0.8, ["Khoảng tin cậy 95% của MAPE từng mô hình. Hai khoảng chồng nhau một chút, "
                              "nên cần so hiệu ghép cặp (bên phải) mới kết luận đúng."], size=13, color=MUTED)
res = [("RF tốt hơn Ridge", "3,0 điểm %", "KTC 95%: 2,1 → 4,0", "có ý nghĩa", BLUE),
       ("RF tự cài đặt − thư viện", "0,19 điểm %", "KTC 95%: −0,04 → 0,46", "không khác biệt", TINT),
       ("Ridge tự cài đặt − thư viện", "0", "cùng một nghiệm", "trùng khớp", TINT)]
for k, (t, v, ci, verdict, col) in enumerate(res):
    y = 1.6 + k * 1.5
    dark = col == BLUE
    box(s, 8.1, y, 4.6, 1.3, fill=col)
    text(s, 8.3, y + 0.06, 4.2, 0.4, [t], size=14, color=WHITE if dark else BLUE, bold=True)
    text(s, 8.3, y + 0.45, 2.1, 0.55, [v], size=22, color=YELLOW if dark else ORANGE, bold=True)
    text(s, 10.35, y + 0.47, 2.3, 0.75, [ci, verdict], size=12, color=WHITE if dark else INK, space_after=0)

s = content("Phần 5 · Diễn giải", "Mô hình học được gì về giá xe?",
            "Bên trái: Ridge cho biết mỗi thuộc tính làm giá tăng giảm bao nhiêu phần trăm. Hệ số dòng xe là phần chênh so với mức chung của hãng. "
            "Bên phải: Random Forest, tuổi xe chiếm khoảng 1/3 độ quan trọng; hộp số cao vì xe số sàn thường là xe cũ, phân khúc thấp.")
picture(s, FIG / "m04_ridge_he_so.png", 0.4, 1.45, 6.2, 4.35)
picture(s, FIG / "m12_do_quan_trong.png", 6.7, 1.45, 6.2, 4.35)
text(s, 0.6, 5.8, 5.8, 0.4, ["Ridge: Land Cruiser, Alphard +250-300%; VinFast VF2 −65%"], size=13, color=MUTED)
text(s, 6.8, 5.8, 6.0, 0.4, ["RF: tuổi xe 31%, hộp số 18%, hãng 16%, dòng xe 13%"], size=13, color=MUTED)

s = content("Phần 5 · Diễn giải", "Random Forest học được mỗi dòng xe khấu hao khác nhau",
            "Cố định mọi thuộc tính, chỉ thay đổi tuổi xe với 15.000 km mỗi năm. Ridge buộc mọi dòng xe mất cùng một tỉ lệ % mỗi năm. "
            "Random Forest học được Mercedes C Class mất giá rất nhanh 3-4 năm đầu: đó là tương tác giữa dòng xe và tuổi xe.")
picture(s, FIG / "m13_duong_khau_hao.png", 0.5, 1.5, 12.3, 3.75)
text(s, 0.6, 5.35, 12.1, 0.75, [[("Vì sao Random Forest chính xác hơn: ", {"bold": True, "color": BLUE}),
                                 ("giá phụ thuộc phi tuyến và có tương tác giữa các đặc trưng. Mức chênh 3 điểm % MAPE chính là phần mô hình tuyến tính bỏ lỡ.", {})]],
     size=15)

s = content("Phần 5 · Thí nghiệm", "Log giá và xử lý mất cân bằng: kiểm chứng bằng CV trên train",
            "Log giá giảm MAPE từ 19,6% xuống 16,2%. Trọng số mẫu và oversampling giữ nguyên MAPE tổng nhưng giảm sai số xe trên 2 tỷ khoảng 3 điểm %. "
            "Undersampling bỏ 22% dữ liệu và làm kết quả kém đi.")
picture(s, FIG / "m14_log_va_mat_can_bang.png", 0.5, 1.5, 12.3, 3.55)
cards = [("Log giá", "19,6% → 16,2% MAPE tổng"), ("Oversampling", "xe > 2 tỷ: 27,4% → 24,5%"), ("Undersampling", "mất 22% dữ liệu, MAPE 16,8%")]
for k, (t, d) in enumerate(cards):
    x = 0.6 + k * 4.1
    box(s, x, 5.15, 3.8, 0.9, fill=TINT if k != 0 else BLUE)
    text(s, x + 0.2, 5.2, 3.5, 0.4, [t], size=15, color=YELLOW if k == 0 else BLUE, bold=True)
    text(s, x + 0.2, 5.58, 3.5, 0.4, [d], size=13, color=WHITE if k == 0 else INK)

s = content("Kết luận", "Kết luận",
            "Tóm tắt bốn ý chính để trả lời câu hỏi của đề tài.")
pts = [("15,5%", "Random Forest dự đoán giá với MAPE 15,5%; 80% xe lệch không quá 20%; tốt hơn Ridge có ý nghĩa thống kê"),
       ("3 điểm %", "Quan hệ phi tuyến và tương tác (mỗi dòng xe khấu hao khác nhau) là phần Ridge bỏ lỡ"),
       ("≈ thư viện", "Hai mô hình tự cài đặt cho kết quả tương đương thư viện; khác biệt lớn nhất là tốc độ"),
       ("CV trên train", "Mọi quyết định đều kiểm chứng bằng số liệu: log giá, gộp nhãn, xử lý mất cân bằng")]
for k, (v, d) in enumerate(pts):
    x = 0.6 + (k % 2) * 6.15
    y = 1.6 + (k // 2) * 2.2
    box(s, x, y, 5.95, 1.95, fill=BLUE if k == 0 else TINT)
    text(s, x + 0.25, y + 0.12, 5.4, 0.65, [v], size=28, color=YELLOW if k == 0 else ORANGE, bold=True)
    text(s, x + 0.25, y + 0.82, 5.5, 1.05, [d], size=15, color=WHITE if k == 0 else INK)

s = content("Kết luận", "Hạn chế và hướng phát triển",
            "Con số 15,5% hơi lạc quan do có tin đăng lại: trên nhóm tin không có bản sao trong train, MAPE là 16,2%.")
box(s, 0.6, 1.6, 5.95, 3.9, fill=TINT)
text(s, 0.85, 1.72, 5.5, 0.45, ["Hạn chế"], size=18, color=BLUE, bold=True)
text(s, 0.85, 2.25, 5.5, 3.7, ["Giá rao bán, không phải giá giao dịch thực",
                               "14% tin test có bản sao (tin đăng lại) trong train: MAPE trên nhóm còn lại 16,2%",
                               "Thiếu phiên bản, trang bị, tình trạng thân vỏ, số đời chủ",
                               "Giá trả trước nhận diện bằng quy tắc, có thể còn sót"], size=16, bullets=True, space_after=12)
box(s, 6.75, 1.6, 5.95, 3.9, fill=TINT_Y)
text(s, 7.0, 1.72, 5.5, 0.45, ["Hướng phát triển"], size=18, color=BLUE, bold=True)
text(s, 7.0, 2.25, 5.5, 3.7, ["Crawl thêm mô tả tin đăng: lọc giá cọc theo từ khóa, lấy phiên bản xe",
                              "Chia train/test theo nhóm để mọi bản đăng của một xe nằm cùng phía",
                              "Gradient Boosting: dùng lại lớp cây đã tự cài đặt",
                              "Dùng oversampling nếu ưu tiên định giá xe sang"], size=16, bullets=True, space_after=12)

# ---------------------------------------------------------------- Cảm ơn
order.append(S_THANKS)

# ---------------------------------------------------------------- xóa slide mẫu, sắp xếp
sldIdLst = prs.slides._sldIdLst
keep = {id(sl._element) for sl in order}
id_of = {}
for sldId in list(sldIdLst):
    part = prs.part.related_part(sldId.rId)
    if id(part._element) not in keep:
        prs.part.drop_rel(sldId.rId)
        sldIdLst.remove(sldId)
    else:
        id_of[id(part._element)] = sldId
for sl in order:
    el = id_of[id(sl._element)]
    sldIdLst.remove(el)
    sldIdLst.append(el)

prs.save(OUT)
print("slides:", len(prs.slides))
