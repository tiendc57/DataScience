"""Tiện ích dùng chung cho các notebook: hình cho slide, xuất bảng, số liệu chốt.

- save_slide(fig, name): lưu bản hình cho slide (PNG 200 dpi + PDF) vào figures/slides/.
- SLIDE_RC: cấu hình chữ to cho hình slide, dùng với `with plt.rc_context(SLIDE_RC):`.
- save_table(df, name, title, note, part): lưu tables/<name>.csv (utf-8-sig để Excel đọc đúng dấu)
  và ghi bảng Markdown vào tables/bang_bao_cao.md.
- update_numbers(**kw): cập nhật tables/so_lieu_chot.json.

bang_bao_cao.md được ghép lại từ ba phần (preprocess, process, model). Mỗi notebook gọi
start_tables(part) ở đầu để xóa phần của chính nó, nên chạy lại một notebook không làm bảng bị lặp.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

FIG_DIR = Path("figures")
SLIDE_DIR = FIG_DIR / "slides"
TABLE_DIR = Path("tables")
for _d in (FIG_DIR, SLIDE_DIR, TABLE_DIR):
    _d.mkdir(parents=True, exist_ok=True)

BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#9aa0a6"
LIGHT_BLUE, LIGHT_ORANGE = "#8fb8ee", "#f4a98a"

SLIDE_RC = {                       # chữ to, đọc được khi chiếu
    "figure.figsize": (10, 5.6),   # tỉ lệ 16:9 cho vùng nội dung slide
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "font.size": 13,
    "axes.titlesize": 15,
    "axes.labelsize": 13,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
}

PARTS = ["preprocess", "process", "model"]
PART_TITLES = {"preprocess": "Tiền xử lý (preprocess_data.ipynb)",
               "process": "Xử lý dữ liệu sau khi chia tập (process_data.ipynb)",
               "model": "Mô hình (model.ipynb)"}


def vn(x, d=0):
    """Định dạng số kiểu Việt Nam: 1.234,5"""
    return f"{x:,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def save_slide(fig, name):
    """Lưu bản dùng cho slide: PNG để chèn, PDF để in nét."""
    fig.savefig(SLIDE_DIR / f"{name}.png", dpi=200, bbox_inches="tight", facecolor="white")
    fig.savefig(SLIDE_DIR / f"{name}.pdf", bbox_inches="tight", facecolor="white")


def _part_file(part):
    return TABLE_DIR / f"_md_{part}.md"


def _rebuild_md():
    out = ["# Bảng số liệu cho báo cáo và slide\n",
           "Tự sinh khi chạy preprocess_data → process_data → model. Mỗi bảng cũng có bản .csv cùng tên.\n"]
    for p in PARTS:
        f = _part_file(p)
        if f.exists():
            out.append(f"\n# {PART_TITLES[p]}\n")
            out.append(f.read_text(encoding="utf-8"))
    (TABLE_DIR / "bang_bao_cao.md").write_text("".join(out), encoding="utf-8")


def start_tables(part):
    """Xóa các bảng Markdown của notebook này (gọi một lần ở đầu notebook)."""
    _part_file(part).unlink(missing_ok=True)
    _rebuild_md()


def save_table(df, name, title, note="", part="model", index=True, floatfmt=".3f"):
    """Lưu CSV và nối bảng Markdown vào phần của notebook trong tables/bang_bao_cao.md."""
    df.to_csv(TABLE_DIR / f"{name}.csv", encoding="utf-8-sig", index=index)
    md = df.to_markdown(index=index, floatfmt=floatfmt)
    with open(_part_file(part), "a", encoding="utf-8") as f:
        f.write(f"\n## {title}\n\n`tables/{name}.csv`\n\n{md}\n")
        if note:
            f.write(f"\n*{note}*\n")
    _rebuild_md()


def update_numbers(**kw):
    """Cập nhật tables/so_lieu_chot.json (các con số lẻ dùng trong slide)."""
    path = TABLE_DIR / "so_lieu_chot.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data.update(kw)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data
