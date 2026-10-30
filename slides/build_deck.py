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


# ================================================================ NỘI DUNG 35 SLIDE
# Không dùng slide ngăn cách phần: mỗi slide có dòng nhãn nhỏ (kicker) cho biết đang ở phần nào.
GRAY = RGBColor(0x9A, 0xA0, 0xA6)


def caption(slide, x, y, w, t, size=12):
    text(slide, x, y, w, 0.4, [t], size=size, color=MUTED)


def callout(slide, x, y, w, h, title, body, dark=False, size=13):
    box(slide, x, y, w, h, fill=BLUE if dark else TINT)
    text(slide, x + 0.2, y + 0.08, w - 0.4, 0.4, [title], size=size + 2, color=YELLOW if dark else BLUE, bold=True)
    text(slide, x + 0.2, y + 0.5, w - 0.4, h - 0.55, body if isinstance(body, list) else [body], size=size,
         color=WHITE if dark else INK, space_after=4)


# ---------------------------------------------------------------- 1. Bìa
ps = [sh for sh in S_TITLE.shapes if sh.has_text_frame]
main = max(ps, key=lambda sh: len(sh.text_frame.paragraphs))
paras = main.text_frame.paragraphs
set_para(paras[0], "Đề tài môn Khoa học dữ liệu")
set_para(paras[1], "Dự đoán giá ô tô cũ trên Chợ Tốt bằng Random Forest", size=34)
for shp in ps:
    for p in shp.text_frame.paragraphs:
        t = p.text.strip()
        if t.startswith("SVTH"):
            set_para(p, "SVTH: <Họ tên SV 1> – <Họ tên SV 2>")
        elif t.upper().startswith("KHO"):
            set_para(p, "GVHD: <Tên giảng viên>")
S_TITLE.notes_slide.notes_text_frame.text = (
    "Chào thầy cô. Nhóm em trình bày đề tài dự đoán giá rao bán ô tô trên Chợ Tốt. Mô hình được phân tích kỹ là Random Forest, "
    "làm hai bản: dùng thư viện scikit-learn và tự cài đặt bằng NumPy. Ridge Regression chỉ dùng làm mốc so sánh.")
order.append(S_TITLE)

# ---------------------------------------------------------------- 2. Nội dung
s = content("Nội dung trình bày", "Năm phần của bài báo cáo",
            "Bài trình bày đi theo đúng quy trình một dự án học máy từ đầu đến cuối.")
items = [("01", "Giới thiệu đề tài", "Bài toán, mục tiêu và quy trình thực hiện"),
         ("02", "Thu thập và khám phá dữ liệu", "Crawl 14.835 tin rao bán ô tô từ Chợ Tốt"),
         ("03", "Tiền xử lý dữ liệu", "Làm sạch, điền thiếu, gộp nhãn, log giá, mất cân bằng"),
         ("04", "Mô hình Random Forest", "Lý thuyết, bản thư viện, bản tự cài đặt, kiểm chứng; Ridge để so sánh"),
         ("05", "Kết quả và kết luận", "Đánh giá trên tập test, diễn giải, thí nghiệm, hạn chế")]
for k, (n, t, d) in enumerate(items):
    y = 1.6 + k * 0.88
    badge(s, 1.2, y, 0.68, n, fill=BLUE if k % 2 == 0 else ORANGE, size=18)
    text(s, 2.1, y - 0.02, 9.5, 0.4, [t], size=20, color=INK, bold=True)
    text(s, 2.1, y + 0.36, 9.5, 0.35, [d], size=14, color=MUTED)

# ---------------------------------------------------------------- 3. Bài toán
s = content("Phần 1 · Giới thiệu", "Bài toán: ước lượng giá một chiếc xe từ thông tin trong tin đăng",
            "Người mua và người bán xe cũ đều cần một mốc giá hợp lý. Đây là bài toán hồi quy có giám sát: đầu vào là các thuộc tính "
            "ai cũng thấy trong tin đăng, đầu ra là giá rao bán tính bằng triệu đồng.")
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
text(s, 7.25, 3.98, 5.2, 0.4, ["Yêu cầu của đề tài"], size=16, color=BLUE, bold=True)
text(s, 7.25, 4.4, 5.3, 1.5, ["Một mô hình từ đầu đến cuối, có thước đo đánh giá",
                              "Phân tích kỹ Random Forest, tự cài đặt và kiểm chứng",
                              "Có kỹ thuật xử lý dữ liệu mất cân bằng"],
     size=14, bullets=True, space_after=5)

# ---------------------------------------------------------------- 4. Quy trình
s = content("Phần 1 · Giới thiệu", "Quy trình thực hiện",
            "Năm bước, mỗi bước một notebook. Mọi quyết định ở bước tiền xử lý và mô hình đều kiểm chứng bằng số liệu trên tập train; "
            "tập test chỉ dùng một lần ở bước đánh giá.")
steps = [("Thu thập", "Crawl Chợ Tốt\n14.835 tin"), ("Tiền xử lý", "Làm sạch, điền thiếu\n13.937 tin"),
         ("Mô hình", "Random Forest\nthư viện + tự cài đặt"), ("Đánh giá", "MAPE, R², ±20%\ntheo phân khúc"),
         ("Triển khai", "Lưu mô hình\nprice_model.py")]
for k, (t, d) in enumerate(steps):
    x = 0.6 + k * 2.5
    box(s, x, 1.8, 2.1, 2.6, fill=TINT if k % 2 == 0 else TINT_Y)
    badge(s, x + 0.7, 2.0, 0.7, str(k + 1), fill=BLUE if k % 2 == 0 else ORANGE, size=20)
    text(s, x + 0.1, 2.85, 1.9, 0.45, [t], size=18, color=BLUE, bold=True, align=PP_ALIGN.CENTER)
    text(s, x + 0.1, 3.35, 1.9, 0.95, d.split("\n"), size=13, color=INK, align=PP_ALIGN.CENTER, space_after=2)
    if k < 4:
        arrow(s, x + 2.13, 2.9, 0.32, 0.4)
text(s, 0.6, 4.7, 12.1, 0.5, [[("Chống rò rỉ dữ liệu: ", {"bold": True, "color": BLUE}),
                              ("mọi lựa chọn (cách mã hóa, tham số, log giá, kỹ thuật cân bằng) quyết định bằng CV hoặc OOB trên tập train.", {})]], size=15)
text(s, 0.6, 5.3, 12.1, 0.5, [[("Tái lập: ", {"bold": True, "color": BLUE}),
                              ("mọi bước ngẫu nhiên cố định random_state = 42, chạy lại cho đúng cùng kết quả.", {})]], size=15)

# ---------------------------------------------------------------- 5. Thu thập
s = content("Phần 2 · Thu thập dữ liệu", "Crawl 14.835 tin rao bán ô tô từ Chợ Tốt",
            "Code crawl duyệt 750 trang danh sách mới nhất, lấy link từng tin, rồi vào trang chi tiết đọc các thẻ HTML có thuộc tính itemprop, "
            "ví dụ itemprop='mileage_v2' là số km. Có nghỉ giữa các yêu cầu và cơ chế chạy tiếp khi bị ngắt.")
stats = [("750", "trang danh sách"), ("14.835", "tin rao bán"), ("12", "thuộc tính mỗi tin"), ("25/10/2026", "ngày thu thập")]
for k, (v, l) in enumerate(stats):
    x = 0.6 + k * 3.05
    box(s, x, 1.6, 2.8, 1.45, fill=BLUE if k == 1 else TINT)
    text(s, x, 1.68, 2.8, 0.75, [v], size=32, color=WHITE if k == 1 else BLUE, bold=True, align=PP_ALIGN.CENTER)
    text(s, x, 2.42, 2.8, 0.45, [l], size=14, color=WHITE if k == 1 else MUTED, align=PP_ALIGN.CENTER)
flow = ["Trang danh sách\n?page=1..750", "Link từng tin\n(bỏ link trùng)", "Trang chi tiết\nđọc thẻ itemprop", "raw_data_oto.csv\n14 cột"]
for k, f in enumerate(flow):
    x = 0.6 + k * 3.05
    box(s, x, 3.35, 2.6, 1.0, fill=TINT_Y)
    text(s, x, 3.4, 2.6, 0.9, f.split("\n"), size=14, color=INK, bold=False, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space_after=0)
    if k < 3:
        arrow(s, x + 2.65, 3.7, 0.35, 0.3)
text(s, 0.6, 4.6, 12.1, 1.5, ["requests + BeautifulSoup; tự lùi thời gian khi bị trả mã 403 / 429; nghỉ 0,5 giây mỗi tin, 1 giây mỗi trang",
                              "Chỉ lấy thông tin công khai, không đăng nhập, không lấy thông tin liên hệ người bán; chỉ dùng cho học tập",
                              "Chạy tiếp được khi bị ngắt: bỏ qua các URL đã có trong file"], size=14, bullets=True, space_after=6)

# ---------------------------------------------------------------- 6. Từ điển dữ liệu
s = content("Phần 2 · Thu thập dữ liệu", "Từ điển dữ liệu: biết cột nào người bán gõ tự do",
            "Cột chọn từ danh sách thì sạch, không lỗi chính tả. Hai cột gõ tự do là số km và giá, cũng là hai nguồn lỗi chính "
            "cần kiểm tra ở bước tiền xử lý. URL chứa vị trí tin đăng.")
rows = [["Cột", "Ý nghĩa", "Người bán nhập", "Xử lý"],
        ["carbrand / carmodel", "Hãng / dòng xe", "chọn từ danh sách", "gộp nhãn hiếm theo cấp"],
        ["mfdate", "Năm sản xuất", "chọn (có \"trước 1980\")", "→ tuổi xe = 2026 − năm"],
        ["mileage_v2", "Số km đã đi", [("gõ tự do", {"color": ORANGE, "bold": True})], "kiểm tra km vô lý, điền thiếu"],
        ["gearbox / fuel", "Hộp số / nhiên liệu", "chọn (3 / 4 giá trị)", "one-hot"],
        ["cartype / carseats", "Kiểu dáng / số chỗ", "chọn, không bắt buộc", "điền theo dòng xe"],
        ["carorigin", "Xuất xứ", "chọn, không bắt buộc", "thiếu 41% → \"Không rõ\""],
        ["condition_ad", "Tình trạng", "Mới / Đã sử dụng", "sửa xe \"Mới\" quá 3 năm tuổi"],
        ["veh_warranty_policy", "Bảo hành", "một giá trị duy nhất", "bỏ cột"],
        ["price", "Giá rao bán (đồng)", [("gõ tự do", {"color": ORANGE, "bold": True})], "biến mục tiêu, loại giá sai"],
        ["url", "Đường dẫn tin", "tự sinh, chứa tỉnh/thành", "trích tỉnh/thành rồi bỏ"]]
table(s, 0.6, 1.55, 12.1, rows, [2.7, 2.7, 3.1, 3.6], size=13, row_h=0.41)

# ---------------------------------------------------------------- 7. Cơ chế thu thập
s = content("Phần 2 · Thu thập dữ liệu", "Cách dữ liệu được tạo ra quyết định cách xử lý",
            "Hiểu code crawl giúp biết mỗi loại lỗi đến từ đâu. Ví dụ N/A là do code không tìm thấy thẻ, tức người bán bỏ trống, "
            "còn 'Khác' là lựa chọn thật của người bán nên phải giữ.")
rows = [["Cơ chế", "Hệ quả", "Cách xử lý"],
        ["Không tìm thấy thẻ → ghi \"N/A\"", "Thiếu thật", "đổi về NaN (đọc với keep_default_na=False)"],
        ["Trang hiện \"Đang cập nhật\" khi bỏ trống xuất xứ", "Cũng là thiếu thật", "đổi về NaN"],
        ["Danh sách có sẵn \"Khác\", \"Dòng khác\"", "Lựa chọn thật của người bán", "giữ làm nhãn (trừ số chỗ \"Khác\")"],
        ["Số km, giá là ô gõ tự do", "Gõ thiếu/thừa số 0, giá giả, giá trả trước", "luật kiểm tra ở phần 3"],
        ["Trang xe \"Mới\" không có ô số km", "Mọi xe mới thiếu số km", "điền 0 km"],
        ["Bảo hành ghi \"Bảo hành hãng\" ở mọi tin", "Không phân biệt được tin nào", "bỏ cột"],
        ["Một lần crawl, 750 trang mới nhất", "Ảnh chụp thị trường; giá rao, không phải giá bán", "tuổi xe tính theo 2026; nêu ở hạn chế"]]
table(s, 0.6, 1.6, 12.1, rows, [4.3, 3.9, 3.9], size=13, row_h=0.5, first_bold=False)

# ---------------------------------------------------------------- 8. EDA: thiếu và cơ cấu
s = content("Phần 2 · Khám phá dữ liệu", "Dữ liệu thô: thiếu nhiều ở các cột không bắt buộc",
            "Xuất xứ thiếu khoảng 41%, kiểu dáng 33%, số chỗ 25%: đều là ô không bắt buộc nhập. Số km thiếu chủ yếu ở xe mới. "
            "Dữ liệu tập trung vào xe đã dùng, hộp số tự động, xăng, và TP.HCM, Hà Nội chiếm khoảng 2/3 số tin.")
picture(s, FIG / "01_missing.png", 0.5, 1.5, 5.6, 3.0)
picture(s, FIG / "02_co_cau.png", 6.3, 1.7, 6.5, 2.6)
cards = [("41%", "xuất xứ bị thiếu → giữ nhãn \"Không rõ\""), ("100%", "xe mới thiếu số km → thiếu có cấu trúc"),
         ("67%", "số tin ở TP.HCM và Hà Nội")]
for k, (v, d) in enumerate(cards):
    x = 0.6 + k * 4.1
    box(s, x, 4.8, 3.8, 1.1, fill=TINT)
    text(s, x + 0.15, 4.85, 1.3, 1.0, [v], size=24, color=ORANGE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 1.45, 4.85, 2.25, 1.0, [d], size=13, anchor=MSO_ANCHOR.MIDDLE, space_after=0)

# ---------------------------------------------------------------- 9. EDA: giá
s = content("Phần 2 · Khám phá dữ liệu", "Tuổi xe và thương hiệu quyết định phần lớn giá",
            "Giá trung vị tăng đều theo năm sản xuất và quan hệ không tuyến tính: xe mất giá nhanh những năm đầu. "
            "Xe sang Đức có giá và độ phân tán cao hơn hẳn xe phổ thông.")
picture(s, FIG / "08_gia_theo_nam.png", 0.5, 1.5, 6.1, 3.7)
picture(s, FIG / "05_gia_theo_hang.png", 6.75, 1.5, 6.1, 3.7)
caption(s, 0.6, 5.3, 5.9, "Xe đời 2001 trung vị khoảng 73 triệu, xe đời 2026 khoảng 624 triệu", 14)
caption(s, 6.85, 5.3, 5.9, "BMW, Mercedes đắt và phân tán rộng; Suzuki, Chevrolet rẻ và tập trung", 14)

# ---------------------------------------------------------------- 10. Chuẩn hóa, trùng
s = content("Phần 3 · Tiền xử lý", "Chuẩn hóa giá trị giả, trích vị trí, loại tin trùng",
            "Bước đầu tiên đưa dữ liệu về đúng kiểu: chuỗi '1.095.000.000' thành số, N/A thành thiếu thật. "
            "Tin trùng hoàn toàn (cùng mọi thuộc tính và giá) bị loại vì nếu một bản ở train, một bản ở test thì điểm đánh giá cao ảo.")
cards = [("Giá trị giả", ["\"N/A\", \"Đang cập nhật\" → thiếu thật", "\"Khác\" ở số chỗ → thiếu; \"Dòng khác\" giữ làm nhãn",
                          "\"109.366\" → 109366 (bỏ dấu chấm)", "\"trước năm 1980\" → 1979"]),
         ("Vị trí và cột thừa", ["Trích tỉnh/thành từ URL: 63 tỉnh, 100% số tin",
                                 "Không tách quận/huyện: 453 giá trị, trung vị 4 tin/quận",
                                 "Bỏ no, url, veh_warranty_policy"]),
         ("Tin trùng", ["691 tin giống hệt mọi thuộc tính và giá (4,7%)", "331 trong số đó là xe mới của đại lý",
                        "Giữ một bản → còn 14.144 tin"])]
for k, (t, b) in enumerate(cards):
    x = 0.6 + k * 4.1
    box(s, x, 1.6, 3.8, 4.3, fill=TINT if k != 2 else TINT_Y)
    text(s, x + 0.2, 1.72, 3.4, 0.45, [t], size=18, color=BLUE, bold=True)
    text(s, x + 0.2, 2.3, 3.45, 3.5, b, size=14, bullets=True, space_after=8)

# ---------------------------------------------------------------- 11. Giá trị bất hợp lý
s = content("Phần 3 · Tiền xử lý", "Phát hiện giá trị bất hợp lý bằng hiểu biết thực tế",
            "Không cắt ngoại lệ theo phần trăm máy móc. Phân biệt sai dữ liệu (không thể xảy ra, loại hoặc sửa) với ngoại lệ thật "
            "(xe siêu sang vài tỷ là có thật, giữ). Làm trước khi điền thiếu để không điền dựa trên số sai.")
rows = [["Cột", "Quy tắc", "Lý do", "Số dòng"],
        ["Giá", "< 20 triệu hoặc > 10 tỷ → loại", "gõ thiếu / thừa số 0, không biết giá đúng", "64"],
        ["Giá", "dãy số liên tiếp 123.456.789 → loại", "giá giả khi không muốn công khai giá", "14"],
        ["Tình trạng", "\"Mới\" mà hơn 3 năm tuổi → \"Đã sử dụng\"", "ghi sai (Tucson 2011 \"mới\")", "6 (sửa)"],
        ["Số km", "xe đã dùng > 500.000 km → thiếu", "nhập thừa số 0", "106"],
        ["Số km", "xe ≥ 2 năm tuổi mà < 100 km → thiếu", "nhập theo đơn vị nghìn km", "447"],
        ["Số km", "> 100.000 km/năm → thiếu", "bất khả thi với xe dân dụng", "25"]]
table(s, 0.6, 1.6, 12.1, rows, [1.6, 4.6, 4.5, 1.4], size=14, row_h=0.5)
box(s, 0.6, 5.3, 12.1, 0.7, fill=TINT_Y)
text(s, 0.85, 5.33, 11.6, 0.65, [[("Giữ lại: ", {"bold": True, "color": BLUE}),
                                  ("giá 399.999.999 (định giá tâm lý), 888.888.888 (số đẹp); xe sang thật dù là ngoại lệ thống kê.", {})]],
     size=14, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 12. Giá trả trước
s = content("Phần 3 · Tiền xử lý", "Giá trả trước / đặt cọc: nhãn sai nằm đúng ở biến cần dự đoán",
            "Nhiều tin ghi số tiền trả trước thay vì giá xe để thu hút người xem. Ngưỡng tuyệt đối không bắt được: 100 triệu hợp lý với xe 20 năm "
            "tuổi nhưng vô lý với xe 1 năm tuổi. Nên so với chính mẫu xe đó.")
box(s, 0.6, 1.6, 5.4, 2.1, fill=BLUE)
text(s, 0.85, 1.72, 5.0, 0.4, ["Quy tắc"], size=16, color=YELLOW, bold=True)
text(s, 0.85, 2.15, 5.0, 1.5, ["Loại tin có giá < 30% trung vị của các xe cùng hãng, dòng, năm sản xuất (nhóm ≥ 3 xe)"], size=16, color=WHITE)
box(s, 0.6, 3.9, 5.4, 2.0, fill=TINT)
text(s, 0.85, 4.0, 5.0, 0.6, [[("129 tin", {"size": 30, "bold": True, "color": ORANGE})]])
text(s, 0.85, 4.7, 5.0, 1.2, ["bị loại, 94% có giá dưới 200 triệu", "Đây là sửa nhãn sai, không tạo đặc trưng từ giá"], size=14, bullets=True)
rows = [["Xe", "Năm", "Tình trạng", "Giá rao", "Trung vị nhóm"],
        ["Toyota Camry", "2026", "Đã sử dụng", "300", "1.400"],
        ["Ford Everest", "2026", "Đã sử dụng", "320", "1.325"],
        ["Toyota Fortuner", "2026", "Mới", "125", "1.249"],
        ["Hyundai Santa Fe", "2025", "Mới", "220", "959"],
        ["Mercedes E Class", "2019", "Đã sử dụng", "156", "889"]]
text(s, 6.3, 1.6, 6.4, 0.4, ["Ví dụ tin bị loại (triệu đồng)"], size=16, color=BLUE, bold=True)
table(s, 6.3, 2.1, 6.4, rows, [2.2, 0.8, 1.4, 0.9, 1.1], size=13, row_h=0.5)
caption(s, 6.3, 5.25, 6.4, "Fortuner 2026 \"mới\" rao 125 triệu trong khi xe cùng đời khoảng 1,25 tỷ: đây là tiền trả trước.", 13)

# ---------------------------------------------------------------- 13. Giá trị thiếu
s = content("Phần 3 · Tiền xử lý", "Hiểu vì sao thiếu trước khi điền",
            "Số km thiếu có cấu trúc: trang tin xe mới không có ô số km, nên điền 0 là đúng bản chất; điền trung vị sẽ biến xe mới thành "
            "xe đã chạy 66.000 km. Kiểu dáng, số chỗ do dòng xe quyết định nên điền theo dòng xe. Xuất xứ thiếu quá nhiều nên không đoán.")
picture(s, FIG / "p02_thieu_va_cach_xu_ly.png", 0.5, 1.5, 12.3, 3.3)
cards = [("Thiếu có cấu trúc", "Xe mới không có ô km → điền 0, không điền trung vị"),
         ("Cờ mileage_missing", "814 xe cũ được điền km → đánh dấu để mô hình biết đó là ước lượng"),
         ("Không đoán bừa", "Kiểu dáng không suy ra được → \"Không rõ\", không lùi về hãng")]
for k, (t, d) in enumerate(cards):
    x = 0.6 + k * 4.1
    callout(s, x, 4.95, 3.8, 1.15, t, d, size=12)

# ---------------------------------------------------------------- 14. Log giá + gộp nhãn
s = content("Phần 3 · Tiền xử lý", "Học trên log(giá) và gộp nhãn hiếm theo cấp",
            "Log đưa phân phối giá về gần đối xứng, biến sai số tuyệt đối thành sai số tương đối, khớp với MAPE. "
            "Gộp nhãn hiếm: dòng xe dưới 10 tin lùi về hãng, hãng dưới 30 tin lùi về nhóm cao cấp hoặc phổ thông. Ngưỡng chọn bằng CV trên train.")
picture(s, FIG / "p03_gia_va_log_gia.png", 0.5, 1.45, 12.3, 2.75)
levels = [("Dòng xe ≥ 10 tin", "giữ nguyên: Toyota Vios"), ("Dòng xe hiếm", "→ \"Mercedes Benz - dòng khác\""),
          ("Hãng < 30 tin", "→ \"Hãng cao cấp khác\" (Bentley) / \"phổ thông khác\" (Wuling)")]
for k, (a, b) in enumerate(levels):
    x = 0.6 + k * 2.75
    box(s, x, 4.35, 2.55, 1.6, fill=TINT)
    badge(s, x + 0.12, 4.47, 0.45, str(k + 1), size=13)
    text(s, x + 0.65, 4.45, 1.85, 0.5, [a], size=13, color=BLUE, bold=True)
    text(s, x + 0.15, 5.0, 2.3, 0.9, [b], size=12)
callout(s, 8.95, 4.35, 3.75, 1.6, "69 hãng → 28;  509 dòng → 214",
        ["CV trên train: Ridge 21,9% → 18,9%; RF 16,3% → 16,1%"], dark=True, size=12)

# ---------------------------------------------------------------- 15. Mất cân bằng + tổng kết
s = content("Phần 3 · Tiền xử lý", "Mất cân bằng theo phân khúc giá; còn 13.937 tin sạch",
            "Biến mục tiêu liên tục nên không có lớp thiểu số; mất cân bằng thể hiện ở mật độ dữ liệu: xe trên 2 tỷ chỉ 3,3%, ít hơn phân khúc "
            "đông nhất gần 13 lần. Tổng cộng làm sạch giữ lại 93,9% dữ liệu, không còn giá trị thiếu.")
picture(s, FIG / "p04_phan_khuc_gia.png", 0.5, 1.5, 5.9, 2.9)
picture(s, FIG / "p01_pheu_lam_sach.png", 6.5, 1.55, 6.3, 2.8)
callout(s, 0.6, 4.6, 5.8, 1.45, "Xử lý mất cân bằng",
        ["Chia train/test phân tầng theo phân khúc; học trên log giá; báo MAPE theo phân khúc; thử trọng số mẫu / oversampling / undersampling (phần 5)"],
        size=12)
callout(s, 6.6, 4.6, 6.1, 1.45, "File sạch chỉ chứa dữ liệu thật",
        ["Không ghi mẫu nhân bản vào file: nếu không, bản sao của cùng một xe có thể nằm ở cả train lẫn test"], dark=True, size=12)

# ---------------------------------------------------------------- 16. Thiết kế thí nghiệm
s = content("Phần 4 · Thiết kế thí nghiệm", "Chia dữ liệu và chọn tham số không dùng tập test",
            "Chia 80/20 phân tầng theo phân khúc giá để tập test có đủ xe sang. Không tách tập validation riêng vì chỉ có khoảng 460 xe trên 2 tỷ; "
            "CV dùng lần lượt mọi phần của train làm validation nên ổn định hơn.")
picture(s, FIG / "m01_chia_train_test.png", 0.5, 1.55, 6.9, 3.4)
caption(s, 0.6, 5.1, 6.7, "Mỗi phân khúc giá có cùng tỉ lệ ở train (11.149 tin) và test (2.788 tin)", 14)
steps = [("Train 80%", "chọn cách mã hóa, tham số, log giá, kỹ thuật cân bằng bằng CV (thư viện) hoặc OOB (tự cài đặt)"),
         ("Test 20%", "dùng đúng một lần để báo cáo kết quả cuối"),
         ("Hai bản Random Forest", "thư viện scikit-learn làm chuẩn; bản tự viết bằng NumPy được kiểm chứng với nó")]
for k, (t, d) in enumerate(steps):
    y = 1.65 + k * 1.45
    badge(s, 7.8, y, 0.6, str(k + 1), fill=BLUE if k != 1 else ORANGE)
    text(s, 8.6, y - 0.05, 4.1, 0.4, [t], size=17, color=BLUE, bold=True)
    text(s, 8.6, y + 0.38, 4.1, 0.95, [d], size=14)

# ---------------------------------------------------------------- 17. Thước đo
s = content("Phần 4 · Thước đo", "Thước đo đánh giá: chỉ số nào cần thấp, chỉ số nào cần cao",
            "MAPE là thước đo chính vì lệch 100 triệu là nhỏ với xe 3 tỷ nhưng rất lớn với xe 150 triệu. Không chỉ số nào tốt khi đứng một mình: "
            "luôn so với baseline luôn đoán giá trung vị. Thang MAPE là quy ước tham khảo trong dự báo (Lewis, 1982).")
rows = [["Thước đo", "Ý nghĩa", "Tốt khi", "Mức tham khảo"],
        [[("MAPE", {"bold": True, "color": ORANGE})], "sai số % trung bình (thước đo chính)", "thấp", "< 10% rất tốt · 10-20% tốt · 20-50% tạm · > 50% kém"],
        ["MedAPE", "sai số % của xe \"điển hình\" (trung vị)", "thấp", "cùng thang MAPE"],
        ["MAE", "trung bình đoán lệch bao nhiêu triệu", "thấp", "tùy mức giá"],
        ["RMSE", "như MAE nhưng phạt nặng lỗi lớn", "thấp", "RMSE ≫ MAE: có vài lỗi rất lớn"],
        ["R² (log)", "tỉ lệ biến thiên log giá được giải thích", "cao", "1 hoàn hảo · 0 = đoán trung bình"],
        ["Lệch ≤ 10% / 20%", "tỉ lệ xe đoán sát giá thật", "cao", "so với baseline"]]
table(s, 0.6, 1.6, 12.1, rows, [2.3, 4.6, 1.3, 3.9], size=13, row_h=0.52)
text(s, 0.6, 5.4, 12.1, 0.6, [[("Mốc so sánh (baseline): ", {"bold": True, "color": BLUE}),
                              ("luôn đoán giá trung vị của tập train. Luôn báo thêm MAPE theo 5 phân khúc giá.", {})]], size=14)

# ---------------------------------------------------------------- 18. Mã hóa
s = content("Phần 4 · Đặc trưng cho rừng", "One-hot hay mã số thứ tự? Kiểm chứng bằng CV",
            "One-hot sinh 277 cột 0/1; mã số thứ tự chỉ 12 cột nhưng thứ tự các nhãn là tùy ý. Với one-hot, một phép chia tách thẳng một dòng xe; "
            "với mã số, xe sang và xe rẻ xếp xen kẽ theo bảng chữ cái nên cây phải chia nhiều lần. Kết quả: one-hot tốt nhất, rõ nhất ở xe trên 2 tỷ.")
picture(s, FIG / "m16_ma_hoa.png", 0.5, 1.45, 12.3, 3.45)
callout(s, 0.6, 5.0, 5.9, 1.1, "Chọn one-hot: MAPE 16,4%", ["mã số thứ tự 16,7-18,4%; xe > 2 tỷ 28,9% so với 29-39%"], dark=True, size=13)
callout(s, 6.8, 5.0, 5.9, 1.1, "Rừng không cần age², log, chuẩn hóa",
        ["cây chỉ so sánh ngưỡng: biến đổi đơn điệu cho cùng phép chia"], size=13)

# ---------------------------------------------------------------- 19. CART
s = content("Phần 4 · Lý thuyết", "Cây hồi quy CART: chia dữ liệu bằng câu hỏi có / không",
            "Đây là một cây thật độ sâu 3 học từ tập train. Câu hỏi đầu tiên là tuổi xe ≤ 13,5 năm, rồi đến hộp số sàn, kiểu dáng, số chỗ. "
            "Mỗi nút chọn câu hỏi làm giảm tổng bình phương sai số nhiều nhất; lá dự đoán bằng trung bình log giá của các xe trong lá.")
picture(s, FIG / "m17_cay_minh_hoa.png", 0.2, 1.35, 10.3, 4.45)
box(s, 10.55, 1.5, 2.25, 1.9, fill=BLUE)
text(s, 10.65, 1.56, 2.1, 0.4, ["Mức giảm SSE"], size=13, color=YELLOW, bold=True)
text(s, 10.65, 1.95, 2.1, 1.4, [[("gain = S²ₗ/nₗ + S²ᵣ/nᵣ − S²/n", {"bold": True, "color": WHITE, "size": 13})],
                                [("n: số xe, S: tổng log giá", {"color": WHITE, "size": 11})]], space_after=4)
text(s, 10.55, 3.55, 2.25, 2.4, ["Cây sâu: độ chệch thấp", "Nhưng phương sai cao: đổi vài mẫu là cây đổi hẳn",
                                 "→ cần trung bình nhiều cây"], size=12, bullets=True, space_after=6)

# ---------------------------------------------------------------- 20. Rừng
s = content("Phần 4 · Lý thuyết", "Random Forest: lấy trung bình nhiều cây khác nhau",
            "Bootstrap: mỗi cây học trên mẫu lấy có hoàn lại, chứa khoảng 63% số xe khác nhau. Mỗi lần chia nút chỉ xét một phần đặc trưng ngẫu nhiên "
            "để các cây ít giống nhau. Trung bình nhiều cây ít tương quan có phương sai nhỏ hơn hẳn một cây. Khoảng 37% xe không được chọn (out-of-bag) "
            "dùng để ước lượng sai số mà không cần tập validation.")
box(s, 0.6, 2.3, 1.9, 1.15, fill=BLUE)
text(s, 0.6, 2.33, 1.9, 1.1, ["Tập train", "11.149 xe"], size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space_after=2)
for k, lab in enumerate(["Bootstrap 1", "Bootstrap 2", "…", "Bootstrap T"]):
    y = 1.55 + k * 0.68
    arrow(s, 2.6, y + 0.13, 0.5, 0.28, fill=YELLOW)
    box(s, 3.2, y, 1.9, 0.55, fill=TINT)
    text(s, 3.2, y + 0.02, 1.9, 0.5, [lab], size=13, color=BLUE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    arrow(s, 5.2, y + 0.13, 0.4, 0.28, fill=YELLOW)
    box(s, 5.7, y, 1.8, 0.55, fill=TINT_Y)
    text(s, 5.7, y + 0.02, 1.8, 0.5, ["Cây " + ("T" if k == 3 else ("…" if k == 2 else str(k + 1)))], size=13, color=INK, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
arrow(s, 7.65, 2.65, 0.5, 0.45, fill=ORANGE)
box(s, 8.3, 2.3, 1.9, 1.15, fill=ORANGE)
text(s, 8.3, 2.33, 1.9, 1.1, ["Trung bình", "T dự đoán"], size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space_after=2)
text(s, 10.45, 1.6, 2.3, 2.6, [[("ŷ(x) = (1/T) Σ fₜ(x)", {"bold": True, "size": 15, "color": BLUE})],
                               [("trung bình T cây", {"size": 12, "color": MUTED})]], space_after=6)
ideas = [("1. Bootstrap", "mỗi cây học ~63% số xe khác nhau"), ("2. max_features", "mỗi nút chỉ xét một phần đặc trưng"),
         ("3. OOB", "~37% xe ngoài túi → ước lượng sai số")]
for k, (t, d) in enumerate(ideas):
    x = 0.6 + k * 4.1
    callout(s, x, 4.55, 3.8, 1.45, t, d, dark=(k == 2), size=13)

# ---------------------------------------------------------------- 21. RF thư viện
s = content("Phần 4 · Random Forest thư viện", "Tinh chỉnh RandomForestRegressor bằng CV trên train",
            "RandomizedSearchCV thử 12 cấu hình ngẫu nhiên, 300 cây, 3-fold CV phân tầng theo phân khúc giá. Các cấu hình tốt đều có cây sâu, lá nhỏ: "
            "dữ liệu có nhiều tổ hợp hãng-dòng-đời xe riêng biệt; việc lấy trung bình 300 cây đã kiểm soát phương sai.")
rows = [["min_samples_leaf", "max_features", "max_depth", "CV RMSE (log)"],
        [[("1", {"bold": True, "color": ORANGE})], [("0,50", {"bold": True, "color": ORANGE})], [("30", {"bold": True, "color": ORANGE})], [("0,2692", {"bold": True, "color": ORANGE})]],
        ["1", "0,33", "30", "0,2701"],
        ["2", "0,80", "30", "0,2763"],
        ["2", "0,50", "30", "0,2766"],
        ["2", "0,33", "30", "0,2793"]]
text(s, 0.6, 1.55, 7.0, 0.4, ["5 cấu hình tốt nhất (300 cây)"], size=16, color=BLUE, bold=True)
table(s, 0.6, 2.05, 7.0, rows, [2.0, 1.7, 1.5, 1.8], size=14, row_h=0.52, first_bold=False)
stats = [("0,896", "OOB R² (log) của mô hình cuối"), ("9 giây", "huấn luyện 300 cây (C/Cython, nhiều lõi)"),
         ("12 / 3-fold", "số cấu hình thử / số fold CV")]
for k, (v, l) in enumerate(stats):
    y = 1.6 + k * 1.45
    box(s, 8.0, y, 4.7, 1.25, fill=BLUE if k == 0 else TINT)
    text(s, 8.2, y + 0.08, 4.3, 0.6, [v], size=26, color=YELLOW if k == 0 else BLUE, bold=True)
    text(s, 8.2, y + 0.7, 4.3, 0.5, [l], size=13, color=WHITE if k == 0 else INK)

# ---------------------------------------------------------------- 22. RF tự cài đặt
s = content("Phần 4 · Random Forest tự cài đặt", "Tự cài đặt bằng NumPy: ba lớp, tìm ngưỡng bằng histogram",
            "Cách cơ bản phải sắp xếp từng cột ở mỗi nút, rất chậm trong Python. Kỹ thuật histogram (giống LightGBM): chia mỗi đặc trưng thành 32 bin "
            "một lần; ở mỗi nút chỉ cần np.bincount đếm số xe và tổng log giá theo bin, rồi np.cumsum cộng dồn là có gain của mọi ngưỡng cùng lúc.")
cls = [("Binner", "chia mỗi đặc trưng thành ≤ 32 bin theo phân vị (fit trên train)"),
       ("RegressionTreeScratch", "cây CART: tìm phép chia giảm SSE lớn nhất, dựng cây bằng ngăn xếp"),
       ("RandomForestScratch", "bootstrap + chọn ngẫu nhiên đặc trưng + trung bình; OOB và độ quan trọng")]
for k, (c, d) in enumerate(cls):
    y = 1.6 + k * 1.1
    badge(s, 0.6, y + 0.2, 0.5, str(k + 1), size=14)
    box(s, 1.25, y, 5.35, 0.95, fill=TINT)
    text(s, 1.4, y + 0.05, 5.1, 0.4, [c], size=15, color=BLUE, bold=True)
    text(s, 1.4, y + 0.47, 5.1, 0.45, [d], size=13)
text(s, 7.0, 1.6, 5.7, 0.4, ["Tìm ngưỡng tốt nhất ở một nút"], size=16, color=BLUE, bold=True)
hsteps = [("Đếm theo bin", "bincount: số xe, tổng log giá mỗi bin"), ("Cộng dồn", "cumsum: nhánh trái của mọi ngưỡng"),
          ("Tính gain", "công thức gain cho mọi ngưỡng cùng lúc"), ("Chọn max", "argmax trên (đặc trưng, ngưỡng)")]
for k, (t, d) in enumerate(hsteps):
    y = 2.1 + k * 0.85
    box(s, 7.0, y, 5.7, 0.72, fill=TINT_Y if k % 2 else TINT)
    text(s, 7.15, y + 0.05, 1.8, 0.62, [t], size=14, color=BLUE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 8.95, y + 0.05, 3.7, 0.62, [d], size=13, anchor=MSO_ANCHOR.MIDDLE)
box(s, 0.6, 5.0, 6.0, 1.0, fill=BLUE)
text(s, 0.8, 5.05, 5.6, 0.9, [[("Cột one-hot chỉ có 2 giá trị → không mất thông tin; ", {"color": WHITE}),
                               ("cột số mất rất ít độ chi tiết.", {"color": YELLOW, "bold": True})]], size=14, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 23. Kiểm chứng
s = content("Phần 4 · Kiểm chứng", "Kiểm chứng: một cây và cả rừng trùng khớp thư viện",
            "Bước 1: dựng một cây cùng tham số với DecisionTreeRegressor, so số nút và R². Bước 2: so dự đoán của cả rừng trên từng xe trong tập test. "
            "Tập test ở đây chỉ dùng để kiểm tra tính đúng của code, không để chọn tham số.")
text(s, 0.6, 1.55, 5.3, 0.4, ["Một cây (lá ≥ 5 mẫu)"], size=16, color=BLUE, bold=True)
rows = [["", "Thư viện", "Tự cài đặt"],
        ["Số nút", "3.481", "3.429"],
        ["R² (log) train", "0,929", "0,927"],
        ["R² (log) test", "0,842", "0,851"],
        ["MAPE test", "19,6%", "18,6%"]]
table(s, 0.6, 2.05, 5.3, rows, [2.1, 1.6, 1.6], size=14, row_h=0.5)
caption(s, 0.6, 4.65, 5.3, "R² train cao hơn hẳn R² test: một cây có phương sai cao", 13)
text(s, 6.2, 1.55, 6.6, 0.4, ["Cả rừng: dự đoán trên từng xe"], size=16, color=BLUE, bold=True)
picture(s, FIG / "m11_tu_cai_dat_vs_thu_vien.png", 6.1, 2.0, 6.7, 2.6)
cards = [("1,7%", "độ lệch trung vị giữa hai bản trên từng xe"), ("83%", "số xe lệch không quá 5%")]
for k, (v, d) in enumerate(cards):
    x = 6.2 + k * 3.3
    box(s, x, 4.8, 3.1, 1.2, fill=BLUE if k == 0 else TINT)
    text(s, x + 0.15, 4.85, 1.2, 1.1, [v], size=24, color=YELLOW if k == 0 else ORANGE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 1.35, 4.85, 1.7, 1.1, [d], size=12, color=WHITE if k == 0 else INK, anchor=MSO_ANCHOR.MIDDLE, space_after=0)

# ---------------------------------------------------------------- 24. OOB và số cây
s = content("Phần 4 · Random Forest tự cài đặt", "Từ một cây đến một rừng: sai số giảm rõ rệt",
            "Bản tự viết chọn tham số bằng OOB (6 cấu hình, mỗi cấu hình 30 cây, chỉ huấn luyện một lần), rồi huấn luyện 100 cây trong khoảng 2,4 phút. "
            "OOB RMSE giảm nhanh trong vài chục cây đầu rồi bão hòa. Trên test, rừng giảm MAPE từ khoảng 19% của một cây xuống 15,5-15,7%.")
picture(s, FIG / "m05_rf_so_cay.png", 0.4, 1.45, 5.6, 2.95)
picture(s, FIG / "m18_cay_vs_rung.png", 6.1, 1.5, 6.8, 2.9)
stats = [("0,346 → 0,263", "OOB RMSE: 1 cây → 100 cây"), ("0,892", "OOB R² tự cài đặt (thư viện 0,896)"),
         ("19% → 15,5%", "MAPE test: một cây → cả rừng")]
for k, (v, l) in enumerate(stats):
    x = 0.6 + k * 4.1
    box(s, x, 4.6, 3.8, 1.35, fill=BLUE if k == 2 else TINT)
    text(s, x + 0.2, 4.66, 3.4, 0.6, [v], size=22, color=YELLOW if k == 2 else BLUE, bold=True)
    text(s, x + 0.2, 5.3, 3.4, 0.6, [l], size=13, color=WHITE if k == 2 else INK)

# ---------------------------------------------------------------- 25. Ridge
s = content("Phần 4 · Mô hình so sánh", "Ridge Regression: mốc so sánh tuyến tính",
            "Ridge là mô hình tuyến tính tốt nhất có thể trên cùng dữ liệu: đã có age² và log(km) để biểu diễn khấu hao cong, và được tinh chỉnh bằng CV "
            "như rừng. Vì vậy phần chênh lệch giữa Ridge và Random Forest chính là đóng góp của quan hệ phi tuyến và tương tác. Ridge chỉ dùng thư viện.")
box(s, 0.6, 1.6, 6.0, 1.75, fill=TINT)
text(s, 0.8, 1.7, 5.6, 0.4, ["Hàm mất mát"], size=15, color=BLUE, bold=True)
text(s, 0.8, 2.15, 5.6, 1.1, [[("J(w) = ", {}), ("(1/2n) Σ (yᵢ − ŷᵢ)²", {"bold": True}), ("  +  ", {}),
                               ("(α/2) Σ wⱼ²", {"bold": True, "color": ORANGE})],
                              [("sai số dự đoán            khoản phạt L2", {"size": 12, "color": MUTED})]], size=20)
text(s, 0.6, 3.55, 6.0, 2.5, ["ŷ = w₀ + Σ wⱼxⱼ: tổ hợp tuyến tính, dự đoán log giá",
                              "Phạt L2 giữ hệ số ổn định khi các cột one-hot tương quan (Toyota và Toyota Vios)",
                              "α = 0,56 chọn bằng 5-fold CV trên train"], size=15, bullets=True, space_after=9)
callout(s, 7.0, 1.6, 5.7, 2.0, "Vì sao chọn Ridge làm mốc?",
        ["Cùng tập train/test, cùng thước đo, cũng được tinh chỉnh → so sánh công bằng",
         "Trả lời: phi tuyến và tương tác giúp được bao nhiêu?"], dark=True, size=13)
callout(s, 7.0, 3.8, 5.7, 2.2, "Ridge khác rừng ở đặc trưng số",
        ["Cần age², log(1+km), log(1+km/năm) và StandardScaler",
         "Vì chỉ cộng hiệu ứng tuyến tính, trong khi xe mất giá nhanh những năm đầu rồi chậm lại"], size=13)

# ---------------------------------------------------------------- 26. Kết quả tổng thể
s = content("Phần 5 · Kết quả", "Random Forest: MAPE 15,5%, 80% xe lệch không quá 20%",
            "Đánh giá trên 2.788 tin test, dùng một lần. Random Forest vượt xa baseline và tốt hơn Ridge 3 điểm %. MedAPE 9% thấp hơn MAPE nhiều: "
            "xe điển hình chỉ lệch 9%, một nhóm nhỏ xe sai nặng kéo trung bình lên. RMSE gấp 3,6 lần MAE cho thấy có vài lỗi rất lớn, chủ yếu xe sang.")
big = [("83,5%", "Baseline", GRAY), ("18,5%", "Ridge (so sánh)", BLUE), ("15,5%", "Random Forest", ORANGE)]
for k, (v, l, col) in enumerate(big):
    x = 0.6 + k * 4.1
    box(s, x, 1.55, 3.8, 1.35, fill=col)
    text(s, x, 1.58, 3.8, 0.8, [v], size=36, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    text(s, x, 2.35, 3.8, 0.45, [l + " · MAPE"], size=14, color=WHITE, align=PP_ALIGN.CENTER)
rows = [["Mô hình", "MAPE", "MedAPE", "MAE (tr)", "RMSE (tr)", "R² (log)", "≤ 20%", "Huấn luyện"],
        ["Baseline (trung vị)", "83,5%", "40,0%", "337", "724", "0,00", "26%", "–"],
        ["Ridge – thư viện", "18,5%", "10,7%", "120", "411", "0,873", "75%", "0,04 giây"],
        [[("Random Forest – thư viện", {"bold": True, "color": ORANGE})], [("15,5%", {"bold": True})], "9,0%", "102", "372", "0,891", "80%", "9 giây"],
        ["Random Forest – tự cài đặt", "15,7%", "9,0%", "106", "388", "0,887", "80%", "143 giây"]]
table(s, 0.6, 3.15, 12.1, rows, [3.5, 1.1, 1.2, 1.2, 1.3, 1.2, 1.1, 1.5], size=14, row_h=0.5)
caption(s, 0.6, 5.7, 12.1, "Theo thang tham khảo, MAPE 10-20% là mức tốt. Hai bản Random Forest gần như trùng nhau; khác biệt lớn nhất là thời gian.", 13)

# ---------------------------------------------------------------- 27. Phân khúc
s = content("Phần 5 · Kết quả", "Mô hình tốt ở phân khúc giữa, kém ở hai đầu thang giá",
            "Phân khúc 200 triệu - 1 tỷ chiếm khoảng 75% thị trường, sai số khoảng 11%. Xe dưới 200 triệu: chênh vài chục triệu đã là phần trăm lớn, "
            "và còn sót tin ghi giá trả trước. Xe trên 2 tỷ: ít dữ liệu và thiếu thông tin phiên bản, trang bị.")
picture(s, FIG / "m07_mape_phan_khuc.png", 0.5, 1.5, 12.3, 3.6)
cards = [("~11%", "sai số ở phân khúc 200 triệu - 1 tỷ (75% thị trường)"),
         ("35%", "xe dưới 200 triệu: giá thấp, tình trạng khác nhau, giá trả trước sót"),
         ("27%", "xe trên 2 tỷ: chỉ 3% dữ liệu, thiếu phiên bản / trang bị")]
for k, (v, d) in enumerate(cards):
    x = 0.6 + k * 4.1
    box(s, x, 5.2, 3.8, 0.85, fill=TINT)
    text(s, x + 0.15, 5.25, 1.2, 0.75, [v], size=22, color=ORANGE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 1.35, 5.25, 2.35, 0.75, [d], size=12, anchor=MSO_ANCHOR.MIDDLE, space_after=0)

# ---------------------------------------------------------------- 28. Dự đoán so với thực tế
s = content("Phần 5 · Kết quả", "Dự đoán so với giá thật: RF bám sát đường chéo",
            "Mỗi điểm là một xe test; trục thang log nên khoảng cách tới đường chéo là sai số phần trăm. Vùng xám là ±20%. "
            "Phần dư đối xứng quanh 0 nên mô hình không đoán lệch hệ thống; Random Forest có phân bố hẹp hơn Ridge.")
picture(s, FIG / "m08_du_doan_vs_thuc_te.png", 0.5, 1.45, 8.6, 3.7)
text(s, 9.3, 1.6, 3.4, 4.0, ["R² (log): Ridge 0,873, RF 0,891", "Lệch ≤ 20%: Ridge 75%, RF 80%",
                             "Không đoán lệch hệ thống (phần dư quanh 0)", "Điểm xa đường chéo nhất: xe rất rẻ và xe sang"],
     size=14, bullets=True, space_after=10)
caption(s, 0.6, 5.3, 12.1, "Giá dự đoán = exp(dự đoán log giá), tức ước lượng trung vị của giá; phù hợp với MAPE.", 13)

# ---------------------------------------------------------------- 29. Bootstrap
s = content("Phần 5 · Kết quả", "Chênh lệch có ý nghĩa thống kê không? Bootstrap ghép cặp",
            "Khoảng tin cậy 95% cho biết MAPE có thể dao động trong khoảng nào nếu đánh giá trên tập test khác. Cách tính: bốc lại 2.788 xe test có hoàn lại, "
            "tính MAPE, lặp 1.000 lần, bỏ 2,5% mỗi đầu. So hai mô hình: tính hiệu MAPE trên cùng các xe trong mỗi lần bốc. Khoảng của hiệu không chứa 0 "
            "nghĩa là chênh lệch có ý nghĩa.")
picture(s, FIG / "m10_khoang_tin_cay.png", 0.4, 1.6, 7.5, 3.3)
caption(s, 0.6, 5.0, 7.2, "Bốc lại tập test 1.000 lần → khoảng chứa 95% giá trị MAPE ở giữa", 13)
res = [("RF tốt hơn Ridge", "3,0 điểm %", "KTC 95%: 2,1 → 4,0", "không chứa 0 → có ý nghĩa", BLUE),
       ("RF tự cài đặt − thư viện", "0,19 điểm %", "KTC 95%: −0,04 → 0,46", "chứa 0 → ngang nhau", TINT)]
for k, (t, v, ci, verdict, col) in enumerate(res):
    y = 1.6 + k * 1.75
    dark = col == BLUE
    box(s, 8.1, y, 4.6, 1.55, fill=col)
    text(s, 8.3, y + 0.08, 4.2, 0.4, [t], size=15, color=WHITE if dark else BLUE, bold=True)
    text(s, 8.3, y + 0.55, 2.0, 0.6, [v], size=22, color=YELLOW if dark else ORANGE, bold=True)
    text(s, 10.3, y + 0.5, 2.35, 0.95, [ci, verdict], size=12, color=WHITE if dark else INK, space_after=2)
box(s, 8.1, 5.1, 4.6, 0.9, fill=TINT_Y)
text(s, 8.25, 5.12, 4.3, 0.85, ["Quy tắc: khoảng của hiệu không chứa 0 thì chênh lệch là thật"], size=13, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 30. Độ quan trọng
s = content("Phần 5 · Diễn giải", "Đặc trưng nào quyết định giá? Hai cách đo",
            "Impurity cộng mức giảm sai số khi học, nhưng bị lệch khi đặc trưng tương quan. Permutation xáo trộn từng đặc trưng trên tập test rồi đo MAPE "
            "tăng bao nhiêu. Hộp số tụt từ hạng 2 xuống hạng 4 vì trùng thông tin với tuổi xe: xe số sàn thường là xe cũ.")
picture(s, FIG / "m15_permutation_importance.png", 0.6, 1.4, 12.1, 3.6)
cards = [("Tuổi xe đứng đầu", "xáo trộn làm MAPE tăng 43 điểm %"),
         ("Hộp số: hạng 2 → 4", "trùng thông tin với tuổi xe"),
         ("Hãng: hạng 3 → 2", "giá thương hiệu khó thay thế")]
for k, (t, d) in enumerate(cards):
    x = 0.6 + k * 4.1
    callout(s, x, 5.05, 3.8, 1.0, t, d, dark=(k == 0), size=12)

# ---------------------------------------------------------------- 31. Khấu hao
s = content("Phần 5 · Diễn giải", "Random Forest học được mỗi dòng xe khấu hao khác nhau",
            "Cố định mọi thuộc tính, chỉ thay đổi tuổi xe với 15.000 km mỗi năm. Ridge buộc mọi dòng xe mất cùng một tỉ lệ % mỗi năm. "
            "Random Forest học được Mercedes C Class mất giá rất nhanh 3-4 năm đầu: đó là tương tác giữa dòng xe và tuổi xe.")
picture(s, FIG / "m13_duong_khau_hao.png", 0.5, 1.5, 12.3, 3.75)
text(s, 0.6, 5.35, 12.1, 0.75, [[("Vì sao Random Forest chính xác hơn: ", {"bold": True, "color": BLUE}),
                                 ("giá phụ thuộc phi tuyến và có tương tác giữa các đặc trưng. Mức chênh 3 điểm % chính là phần mô hình tuyến tính bỏ lỡ.", {})]],
     size=15)

# ---------------------------------------------------------------- 32. Log + mất cân bằng
s = content("Phần 5 · Thí nghiệm", "Log giá và xử lý mất cân bằng: kiểm chứng bằng CV trên train",
            "Log giá giảm MAPE từ 19,6% xuống 16,2%. Trọng số mẫu và oversampling giữ nguyên MAPE tổng nhưng giảm sai số xe trên 2 tỷ khoảng 3 điểm %. "
            "Undersampling bỏ 22% dữ liệu và làm kết quả kém đi. Cân bằng chỉ làm trong phần train của từng fold; đánh giá bằng CV vì oversampling làm OOB sai.")
picture(s, FIG / "m14_log_va_mat_can_bang.png", 0.5, 1.5, 12.3, 3.55)
cards = [("Log giá", "19,6% → 16,2% MAPE tổng"), ("Oversampling", "xe > 2 tỷ: 27,4% → 24,5%"), ("Undersampling", "mất 22% dữ liệu, MAPE 16,8%")]
for k, (t, d) in enumerate(cards):
    x = 0.6 + k * 4.1
    box(s, x, 5.15, 3.8, 0.9, fill=TINT if k != 0 else BLUE)
    text(s, x + 0.2, 5.2, 3.5, 0.4, [t], size=15, color=YELLOW if k == 0 else BLUE, bold=True)
    text(s, x + 0.2, 5.58, 3.5, 0.4, [d], size=13, color=WHITE if k == 0 else INK)

# ---------------------------------------------------------------- 33. Tin đăng lại, nhãn sai
s = content("Phần 5 · Hạn chế", "Hai nguồn sai lệch: tin đăng lại và nhãn sai còn sót",
            "Tin đăng lại làm điểm hơi lạc quan: chia theo nhóm (mọi bản đăng của một xe cùng một phía) làm MAPE CV tăng 0,5 điểm %. "
            "Ngược lại, nhiều xe bị đoán sai nhất thực ra là tin ghi giá trả trước còn sót: mô hình đoán hợp lý hơn giá rao.")
text(s, 0.6, 1.55, 5.6, 0.4, ["Chia ngẫu nhiên so với chia theo nhóm (CV)"], size=15, color=BLUE, bold=True)
rows = [["Cách chia", "MAPE", "< 200 tr", "> 2 tỷ"],
        ["Ngẫu nhiên", "16,1%", "35,7%", "27,6%"],
        ["Theo nhóm", "16,7%", "38,0%", "28,7%"]]
table(s, 0.6, 2.0, 5.6, rows, [2.0, 1.2, 1.2, 1.2], size=14, row_h=0.5)
callout(s, 0.6, 3.75, 5.6, 2.25, "Ước lượng thận trọng: 16-16,5%",
        ["14% tin test có bản sao trong train: MAPE 10,9% so với 16,2% ở phần còn lại",
         "Mức lạc quan có nhưng nhỏ, không đổi kết luận"], dark=True, size=13)
text(s, 6.5, 1.55, 6.2, 0.4, ["Xe bị đoán sai nhiều nhất (triệu đồng)"], size=15, color=BLUE, bold=True)
rows = [["Xe", "Tình trạng", "Giá rao", "Dự đoán"],
        ["Hyundai Starex 2023", "Đã dùng", "35", "655"],
        ["Toyota 4 Runner 2025", "Đã dùng", "115", "819"],
        ["Hyundai Accent 2026", "Mới", "90", "464"],
        ["Mitsubishi Xforce 2025", "Đã dùng", "170", "612"],
        ["Ford Ranger 2024", "Đã dùng", "225", "616"]]
table(s, 6.5, 2.0, 6.2, rows, [2.8, 1.3, 1.0, 1.1], size=13, row_h=0.47)
caption(s, 6.5, 4.95, 6.2, "Xe đời mới rao vài chục triệu: gần như chắc chắn là giá trả trước lọt qua luật lọc (nhóm < 3 xe).", 12)

# ---------------------------------------------------------------- 34. Lưu mô hình, demo
s = content("Phần 5 · Triển khai", "Lưu mô hình và dự đoán từ thông tin thô của xe",
            "Mô hình được lưu trong thư mục model/. Hàm predict_price nhận thông tin thô (hãng, dòng, năm, km...), tự gộp nhãn, điền km thiếu "
            "và dựng đặc trưng như lúc huấn luyện. Nạp lại cho dự đoán trùng notebook đến 10⁻¹¹ triệu.")
rows = [["File", "Nội dung"],
        ["random_forest_sklearn.joblib", "rừng thư viện (300 cây)"],
        ["random_forest_scratch.npz", "các cây và ngưỡng bin của rừng tự cài đặt"],
        ["preprocessor_rf.joblib", "bộ mã hóa one-hot (fit trên train)"],
        ["metadata.json", "bảng gộp nhãn, trung vị km theo năm, metric"],
        ["price_model.py", "load_model(), predict_price()"]]
table(s, 0.6, 1.6, 6.6, rows, [3.1, 3.5], size=13, row_h=0.5)
text(s, 7.5, 1.55, 5.2, 0.4, ["Ví dụ dự đoán (triệu đồng)"], size=15, color=BLUE, bold=True)
rows = [["Xe", "RF (TV)", "RF (TCĐ)", "Ridge"],
        ["Toyota Vios 2018, 80.000 km", "303", "303", "281"],
        ["Ford Ranger 2021, không rõ km", "515", "536", "596"]]
table(s, 7.5, 2.0, 5.2, rows, [2.6, 0.9, 0.9, 0.8], size=13, row_h=0.6)
box(s, 7.5, 4.0, 5.2, 1.9, fill=TINT_Y)
text(s, 7.7, 4.08, 4.9, 1.8, ["Xe đã dùng không rõ km → điền trung vị km theo năm sản xuất, đánh dấu mileage_missing",
                              "Dòng xe chưa gặp → lùi về \"<hãng> - dòng khác\""], size=13, bullets=True, space_after=6)

# ---------------------------------------------------------------- 35. Kết luận
s = content("Kết luận", "Kết luận, hạn chế và hướng phát triển",
            "Tóm tắt kết quả, nêu rõ hạn chế và hướng phát triển. Cảm ơn thầy cô đã lắng nghe, nhóm em sẵn sàng trả lời câu hỏi.")
pts = [("15,5%", "MAPE của Random Forest; 80% xe lệch ≤ 20%"), ("+3 điểm %", "tốt hơn Ridge, có ý nghĩa thống kê"),
       ("≈ thư viện", "rừng tự cài đặt 15,7%, kiểm chứng ở mức cây và rừng")]
for k, (v, d) in enumerate(pts):
    x = 0.6 + k * 4.1
    box(s, x, 1.55, 3.8, 1.35, fill=BLUE if k == 0 else TINT)
    text(s, x + 0.2, 1.6, 3.4, 0.65, [v], size=26, color=YELLOW if k == 0 else ORANGE, bold=True)
    text(s, x + 0.2, 2.25, 3.45, 0.65, [d], size=13, color=WHITE if k == 0 else INK)
box(s, 0.6, 3.05, 5.95, 2.35, fill=TINT)
text(s, 0.85, 3.12, 5.5, 0.4, ["Hạn chế"], size=16, color=BLUE, bold=True)
text(s, 0.85, 3.55, 5.5, 1.8, ["Giá rao bán, không phải giá giao dịch",
                               "Chưa lấy phiên bản, số đời chủ, đăng kiểm",
                               "Còn sót giá trả trước; có tin đăng lại",
                               "Ảnh chụp thị trường 10/2026, xe ≤ 10 tỷ"], size=14, bullets=True, space_after=5)
box(s, 6.75, 3.05, 5.95, 2.35, fill=TINT_Y)
text(s, 7.0, 3.12, 5.5, 0.4, ["Hướng phát triển"], size=16, color=BLUE, bold=True)
text(s, 7.0, 3.55, 5.5, 1.8, ["Crawl tiêu đề, mô tả: phiên bản xe, lọc giá trả trước",
                              "Chia train/test theo nhóm làm đánh giá chính",
                              "Gradient Boosting dùng lại lớp cây tự cài đặt",
                              "Giao diện web nhập thông tin xe, nhận giá"], size=14, bullets=True, space_after=5)
text(s, 0.6, 5.5, 12.1, 0.45, [[("Cảm ơn thầy cô đã lắng nghe!", {"bold": True, "color": ORANGE})]], size=18, align=PP_ALIGN.CENTER)


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
