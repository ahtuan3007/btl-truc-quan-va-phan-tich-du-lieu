"""Tạo 13 biểu đồ Goodreads từ dữ liệu đã làm sạch."""

import argparse
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
MIN_GROUP_N = 30
TOP_N = 12
PAGE_BANDS = ["1-200", "201-400", "401-600", "601+"]
RATING_BIN_LABELS = ["1 ≤ R < 3,5", "3,5 ≤ R < 4", "4 ≤ R < 4,5", "4,5 ≤ R ≤ 5"]
THRESHOLDS = (1, 100, 500, 1000)
BLUE, TEAL, INK, GRAY = "#2563A0", "#147D80", "#24364A", "#66778A"
PALETTE = ["#CFDEE9", "#77A9C7", "#267AA0", "#11656C"]


# ---------- Hàm phụ trợ ----------
def number(x):
    return f"{int(x):,}".replace(",", ".")


def dec(x, places=3):
    return f"{x:.{places}f}".replace(".", ",")


def wrapped(value, width=29):
    return "\n".join(textwrap.wrap(str(value), width=width, break_long_words=False))


def configure_style():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans", "font.size": 10.5,
            "axes.labelcolor": INK, "axes.edgecolor": "#AAB6C1", "text.color": INK,
            "xtick.color": GRAY, "ytick.color": GRAY,
            "axes.spines.top": False, "axes.spines.right": False,
            "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
            "axes.titleweight": "bold",
        }
    )


def figure(title, subtitle, note, height=6.4):
    fig = plt.figure(figsize=(11.6, height))
    fig.suptitle(title, x=0.075, y=0.965, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.075, 0.91, subtitle, fontsize=10.7, color=GRAY, va="top")
    fig.text(0.075, 0.052, note, fontsize=9.1, color=GRAY, va="bottom", linespacing=1.45)
    return fig


def axis(fig, left=0.10, bottom=0.20, width=0.84, height=0.61):
    return fig.add_axes([left, bottom, width, height])


def polish(ax, grid="y"):
    ax.set_axisbelow(True)
    ax.grid(axis=grid, color="#E8EDF2", linewidth=0.8)
    ax.tick_params(length=0, pad=7)


def group_stats(frame, key):
    """n = số Book Id duy nhất, mean = Rating trung bình theo nhóm."""
    return (
        frame.dropna(subset=[key])
        .groupby(key, observed=True)
        .agg(n=("book_id", "nunique"), mean=("rating", "mean"))
        .reset_index()
    )


def top_by_n(groups, key):
    ok = groups.loc[groups["n"].ge(MIN_GROUP_N)]
    return ok.sort_values(["n", key], ascending=[False, True]).head(TOP_N)


def load_data(root):
    processed = root / "data/processed"
    clean = pd.read_csv(
        processed / "books_cleaned_master.csv",
        dtype={"book_id": str, "pages": "Int64", "publication_year": "Int64", "publication_decade": "Int64"},
        keep_default_na=False,
        na_values=[""],
    )
    bridge = pd.read_csv(processed / "book_genres_bridge.csv", dtype=str, keep_default_na=False)
    return clean, bridge


# ---------- Chương trình chính ----------
def run(root, out):
    clean, bridge = load_data(root)
    primary = clean.loc[clean["primary_sample"]].copy()
    joined = bridge.merge(primary[["book_id", "rating"]], on="book_id", validate="many_to_one")
    out.mkdir(parents=True, exist_ok=True)
    configure_style()

    N = len(primary)
    mean, median = float(primary.rating.mean()), float(primary.rating.median())
    count = 0

    def save(fig, filename):
        nonlocal count
        fig.savefig(out / filename, dpi=190)
        plt.close(fig)
        count += 1

    # 01. Phân phối Rating (khoảng thập phân [x; x+0,1) khớp Power BI)
    fig = figure(
        "Phân phối Rating trong mẫu phân tích chính",
        f"{number(N)} bản ghi · Rating 1–5 · ít nhất 100 lượt chấm",
        "Mỗi bản ghi có trọng số như nhau; không nhân theo lượt chấm.\n"
        "Nguồn: Goodreads-books-with-genres; dữ liệu gốc và thời điểm bổ sung genre khác nhau.",
    )
    ax = axis(fig)
    codes = np.minimum(np.rint(primary.rating.to_numpy() * 100).astype(int) // 10, 49)
    counts = np.bincount(codes, minlength=50)[10:50]
    ax.bar(np.arange(10, 50) / 10, counts, width=0.1, align="edge", color=BLUE, edgecolor="white", linewidth=0.5)
    ax.axvline(mean, color=TEAL, lw=1.8, label=f"Trung bình {dec(mean)}")
    ax.axvline(median, color=INK, lw=1.2, linestyle="--", label=f"Trung vị {dec(median, 2)}")
    ax.set(xlim=(1, 5), xlabel="Rating", ylabel="Số bản ghi")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 1)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: number(x)))
    ax.legend(frameon=False, loc="upper left")
    polish(ax)
    save(fig, "01_PhanPhoi_Rating_MauChinh.png")

    # 02. Boxplot theo nhóm số trang
    page_valid = primary.loc[primary.pages.notna()]
    arrays = [page_valid.loc[page_valid.page_band.eq(b), "rating"].to_numpy() for b in PAGE_BANDS]
    fig = figure(
        "Phân phối Rating theo nhóm số trang",
        f"{number(len(page_valid))} bản ghi có số trang dương · {number(N - len(page_valid))} bản ghi thiếu số trang không dùng trong hình",
        "Hộp: Q1–Q3; vạch giữa: trung vị; râu: 1,5 IQR; các chấm ngoài râu vẫn được giữ.\n"
        "Số trang là đặc điểm ghi trên bản ghi/ấn bản; nhóm thể loại và tuyển tập có thể khác nhau.",
    )
    ax = axis(fig)
    boxes = ax.boxplot(
        arrays,
        tick_labels=[f"{b} trang\nn = {number(len(a))}" for b, a in zip(PAGE_BANDS, arrays)],
        patch_artist=True,
        medianprops={"color": INK, "linewidth": 1.8},
        whiskerprops={"color": GRAY},
        capprops={"color": GRAY},
        flierprops={"marker": ".", "markersize": 2.5, "alpha": 0.3, "markeredgecolor": BLUE},
    )
    for box, color in zip(boxes["boxes"], PALETTE):
        box.set(facecolor=color, edgecolor=BLUE, alpha=0.8)
    ax.axhline(mean, color=TEAL, lw=1, linestyle="--", label=f"Trung bình mẫu chính {dec(mean)}")
    ax.set(ylim=(1, 5), ylabel="Rating")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 1)))
    ax.legend(frameon=False, loc="lower right")
    polish(ax)
    save(fig, "02_Boxplot_Rating_NhomSoTrang.png")

    # Hàm vẽ cột ngang Rating trung bình (dùng cho hình 03, 04, 05, 07)
    def mean_bar(table, key, filename, title, subtitle, note, width=29):
        big = len(table) > 7
        fig = figure(title, subtitle, note, height=7.5 if big else 6.3)
        left = 0.34 if big else 0.23
        ax = axis(fig, left=left, width=0.94 - left)
        y = np.arange(len(table))
        ax.barh(y, table["mean"], color=BLUE, height=0.64)
        ax.set_yticks(y, [wrapped(v, width) for v in table[key]])
        ax.invert_yaxis()
        ax.axvline(mean, color=TEAL, linestyle="--", lw=1.2, label=f"Toàn mẫu chính: {dec(mean)}")
        label_x = max(float(table["mean"].max()) + 0.10, mean + 0.15)
        for i, (m, n) in enumerate(zip(table["mean"], table["n"])):
            ax.text(label_x, i, f"{dec(m)}  ·  n={number(n)}", va="center", fontsize=9.4)
        ax.set(xlim=(0, 5.65), xticks=range(6), xlabel="Rating trung bình theo bản ghi")
        ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.01), fontsize=9.3)
        polish(ax, "x")
        save(fig, filename)

    # 03. Rating trung bình theo nhóm số trang
    pages_table = group_stats(page_valid, "page_band").set_index("page_band").loc[PAGE_BANDS].reset_index()
    hi, lo = pages_table.loc[pages_table["mean"].idxmax()], pages_table.loc[pages_table["mean"].idxmin()]
    mean_bar(
        pages_table, "page_band", "03_TrungBinh_Rating_NhomSoTrang.png",
        "Rating trung bình theo nhóm số trang",
        "Mẫu chính có số trang dương · bốn nhóm đều có ít nhất 30 bản ghi",
        f"Cao nhất: nhóm {hi.page_band} ({dec(hi['mean'])}); thấp nhất: nhóm {lo.page_band} ({dec(lo['mean'])}).\n"
        f"Đường đứt: trung bình {number(N)} bản ghi; không phải mô hình nhân quả.",
    )

    # 04, 05. Top 12 thể loại / nhà xuất bản theo n
    genre_groups = group_stats(joined, "genre_label")
    genre_top = top_by_n(genre_groups, "genre_label")
    publisher_groups = group_stats(primary, "publisher_clean")
    publisher_top = top_by_n(publisher_groups, "publisher_clean")
    mean_bar(
        genre_top, "genre_label", "04_Rating_Top12_NhanTheLoai_TheoN.png",
        "Rating của 12 nhãn thể loại có nhiều bản ghi nhất",
        "Chọn và sắp xếp theo n giảm dần; hòa n thì theo nhãn gốc · chỉ nhóm n ≥ 30",
        "Một sách thuộc nhiều nhãn; tổng n giữa các nhóm không cộng thành số sách duy nhất.\n"
        "Giữ nguyên nhãn và chữ hoa/thường; dấu phẩy bên trong nhãn không bị tách.",
    )
    mean_bar(
        publisher_top, "publisher_clean", "05_Rating_Top12_NhaXuatBan_TheoN.png",
        "Rating của 12 nhà xuất bản có nhiều bản ghi nhất",
        "Chọn và sắp xếp theo n giảm dần; hòa n thì theo tên gốc · chỉ nhóm n ≥ 30",
        "Giữ tên sau chuẩn hóa khoảng trắng; không gộp theo chữ thường hoặc gộp các imprint.\n"
        "Khác biệt có thể phản ánh cơ cấu tác phẩm; chưa đo tác động của nhà xuất bản.",
    )

    # 06. Mức độ bao phủ ngôn ngữ
    languages = group_stats(primary, "language_group").sort_values(["n", "language_group"], ascending=[False, True])
    cover = languages[["language_group", "n"]].head(8).reset_index(drop=True)
    rest = int(languages.n.sum() - cover.n.sum())
    if rest:
        cover.loc[len(cover)] = ["Các mã còn lại", rest]
    english = int(primary.language_group.eq("English").sum())
    fig = figure(
        "Mức độ bao phủ ngôn ngữ trong mẫu chính",
        f"English: {number(english)} / {number(N)} bản ghi ({dec(english / N * 100, 2)}%)",
        "English gộp eng, en-US, en-GB, en-CA; các mã khác giữ riêng.\n"
        "Hình hiển thị tám nhóm nhiều bản ghi nhất và phần còn lại; trục số lượng theo log10.",
        height=6.8,
    )
    ax = axis(fig, left=0.23, width=0.70)
    y = np.arange(len(cover))
    ax.barh(y, cover.n, color=[TEAL] + [BLUE] * (len(y) - 1), height=0.65)
    ax.set_yticks(y, cover.language_group)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(0.7, 18000)
    ax.set_xticks([1, 10, 100, 1000, 10000], ["1", "10", "100", "1.000", "10.000"])
    for i, n in enumerate(cover.n):
        ax.text(n * 1.15, i, f"{number(n)} ({dec(n / N * 100, 2)}%)", va="center", fontsize=9.5)
    ax.set_xlabel("Số bản ghi, trục log10")
    polish(ax, "x")
    save(fig, "06_BaoPhu_NgonNgu.png")

    # 07. Rating theo ngôn ngữ (n >= 30)
    supported = languages.loc[languages.n.ge(MIN_GROUP_N)]
    mean_bar(
        supported, "language_group", "07_Rating_NgonNgu_N30.png",
        "Rating theo ngôn ngữ có đủ số bản ghi",
        "Chỉ nhóm n ≥ 30 · sắp xếp theo số bản ghi, không theo Rating",
        "English chiếm phần lớn mẫu. Mỗi nhóm có cơ cấu sách và ấn bản khác nhau.\n"
        "Không kết luận ngôn ngữ gây ra chênh lệch Rating; các mã nhỏ không bị xóa khỏi master.",
    )

    # 08. Rating theo thập niên (kèm panel cỡ mẫu)
    dec_groups = group_stats(primary, "publication_decade")
    dec_groups["publication_decade"] = dec_groups.publication_decade.astype(int)
    decades = dec_groups.set_index("publication_decade").reindex(range(1900, 2030, 10))
    decades["n"] = decades.n.fillna(0).astype(int)
    decades["shown"] = decades["mean"].where(decades.n.ge(MIN_GROUP_N))
    fig = figure(
        "Rating theo thập niên xuất bản của bản ghi",
        f"{number(decades.n.sum())} bản ghi có ngày hợp lệ · chỉ vẽ Rating trung bình khi nhóm có n ≥ 30",
        f"Đường đứt: trung bình mẫu chính {dec(mean)}. Năm của bản ghi/ấn bản, chưa xác minh năm xuất bản đầu tiên.\n"
        "Đây là so sánh nhóm năm xuất bản, không phải lịch sử Rating tăng hoặc giảm theo thời gian.",
        height=7.2,
    )
    ax = fig.add_axes([0.105, 0.48, 0.83, 0.32])
    axn = fig.add_axes([0.105, 0.20, 0.83, 0.19], sharex=ax)
    ax.plot(decades.index, decades.shown, marker="o", color=BLUE, lw=2.2)
    ax.axhline(mean, color=TEAL, linestyle="--", lw=1.1)
    for yr, m in decades.loc[decades.n.ge(MIN_GROUP_N), "mean"].items():
        ax.annotate(dec(m), (yr, m), xytext=(0, 10), textcoords="offset points", ha="center", fontsize=9)
    ax.set(ylim=(decades.shown.min() - 0.06, decades.shown.max() + 0.10), ylabel="Rating trung bình")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 1)))
    ax.tick_params(labelbottom=False)
    axn.bar(decades.index, decades.n, width=7.5, color=[BLUE if v >= MIN_GROUP_N else "#B9C6D2" for v in decades.n])
    for yr, v in decades.n.items():
        if v:
            axn.text(yr, v + decades.n.max() * 0.02, number(v), ha="center", fontsize=8.6)
    axn.set(xticks=list(decades.index), xlabel="Thập niên xuất bản trên bản ghi", ylabel="Số bản ghi",
            ylim=(0, decades.n.max() * 1.15))
    axn.set_xticklabels([str(v) for v in decades.index], fontsize=8.8)
    axn.yaxis.set_major_formatter(FuncFormatter(lambda x, _: number(x)))
    polish(ax)
    polish(axn)
    save(fig, "08_Rating_VaN_TheoThapNien.png")

    # 09. Cột chồng 100% cơ cấu Rating theo thể loại
    selected = joined.loc[joined.genre_label.isin(genre_top.genre_label)].copy()
    selected["rating_bin"] = pd.cut(selected.rating, [1, 3.5, 4, 4.5, 5.0000001], right=False, labels=RATING_BIN_LABELS)
    composition = (
        selected.groupby(["genre_label", "rating_bin"], observed=False).book_id.nunique()
        .unstack(fill_value=0).reindex(genre_top.genre_label)
    )
    shares = composition.div(composition.sum(axis=1), axis=0) * 100
    fig = figure(
        "Cơ cấu mức Rating trong 12 nhãn thể loại phổ biến",
        "12 nhãn phổ biến theo n · cột chồng 100% tính riêng trong từng nhãn",
        "Mẫu số mỗi thanh là số Book Id duy nhất trong nhãn; n thể hiện bên phải.\n"
        "Nhãn đa trị chồng lấn giữa các thanh; không cộng tỷ lệ hoặc số sách qua các nhãn.",
        height=7.7,
    )
    ax = axis(fig, left=0.34, width=0.59, height=0.60)
    start = np.zeros(len(shares))
    for label, color in zip(RATING_BIN_LABELS, PALETTE):
        vals = shares[label].to_numpy()
        ax.barh(np.arange(len(shares)), vals, left=start, color=color, height=0.67, label=label,
                edgecolor="white", linewidth=0.3)
        for i, (v, s) in enumerate(zip(vals, start)):
            if v >= 12:
                ax.text(s + v / 2, i, f"{dec(v, 0)}%", ha="center", va="center", fontsize=8.9,
                        color=INK if color == PALETTE[0] else "white")
        start += vals
    ax.set_yticks(np.arange(len(shares)), [wrapped(v) for v in shares.index])
    ax.invert_yaxis()
    for i, n in enumerate(composition.sum(axis=1)):
        ax.text(101, i, f"n={number(n)}", va="center", fontsize=9)
    ax.set(xlim=(0, 114), xticks=[0, 25, 50, 75, 100], xlabel="Tỷ lệ bản ghi trong nhãn (%)")
    ax.legend(frameon=False, ncol=2, loc="lower left", bbox_to_anchor=(0, 1.01), fontsize=9)
    polish(ax, "x")
    save(fig, "09_CotChong100_Rating_TheoTheLoai.png")

    # 10-12. Scatter: vẽ từng bản ghi
    def scatter(col, filename, title, xlabel, log_display=False):
        sub = primary.loc[primary[col].notna()]
        x_raw = sub[col].astype(float)
        fig = figure(
            title,
            f"{number(len(sub))} chấm = {number(len(sub))} Book Id · giữ toàn bộ bản ghi có dữ liệu cho cặp biến",
            "Đường đứt: Rating trung bình mẫu chính. Không khớp đường hồi quy hoặc suy luận nhân quả.\n"
            "Lượt chấm/nhận xét có thể khác cấp tác phẩm và ấn bản; xem giới hạn nguồn trong báo cáo.",
        )
        ax = axis(fig)
        ax.scatter(np.log1p(x_raw) if log_display else x_raw, sub.rating, s=10, alpha=0.23, c=BLUE,
                   edgecolors="none", rasterized=True)
        ax.axhline(mean, color=TEAL, linestyle="--", lw=1.2)
        rho = x_raw.rank().corr(sub.rating.rank())
        ax.text(0.99, 0.98, f"Spearman ρ = {dec(rho, 3)}\nn = {number(len(sub))}", transform=ax.transAxes,
                ha="right", va="top", color=INK, fontsize=10)
        ax.set(xlabel=xlabel, ylabel="Rating", ylim=(1, 5.05))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 1)))
        if log_display:
            floor = 0 if x_raw.min() == 0 else 100
            ticks = [t for t in (0, 10, 100, 1000, 10000, 100000, 1000000, 5000000)
                     if floor <= t <= x_raw.max() * 1.1]
            ax.set_xticks(np.log1p(ticks), [number(t) for t in ticks])
        else:
            ax.set_xlim(0, x_raw.max() * 1.03)
            ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: number(v)))
        polish(ax)
        save(fig, filename)

    scatter("pages", "10_Scatter_Rating_SoTrang.png", "Mối liên hệ giữa số trang và Rating",
            "Số trang trên bản ghi/ấn bản")
    scatter("n_ratings", "11_Scatter_Rating_LuotCham.png", "Mối liên hệ giữa lượt chấm sao và Rating",
            "Số lượt chấm sao — trục ln(1+x), nhãn số gốc", True)
    scatter("n_reviews", "12_Scatter_Rating_NhanXet.png", "Mối liên hệ giữa số bài nhận xét và Rating",
            "Số bài nhận xét — trục ln(1+x), nhãn số gốc", True)

    # 13. Độ nhạy theo ngưỡng lượt chấm
    valid = clean.loc[clean.rating.between(1, 5)]
    sens = pd.DataFrame(
        [(t, len(s), s.rating.mean()) for t in THRESHOLDS for s in [valid.loc[valid.n_ratings.ge(t)]]],
        columns=["min_ratings", "n", "mean_rating"],
    )
    fig = figure(
        "Độ nhạy của Rating trung bình theo ngưỡng lượt chấm",
        "Bốn ngưỡng 1, 100, 500 và 1.000 · không xóa vĩnh viễn các bản ghi dưới ngưỡng",
        "Mỗi ngưỡng tạo một tập bản ghi khác nhau, không phải diễn biến theo thời gian.\n"
        "Mốc 100 là quy ước của mẫu chính, không bảo đảm tính đại diện hoặc độ chính xác thống kê.",
        height=7.0,
    )
    ax = fig.add_axes([0.12, 0.48, 0.80, 0.31])
    axn = fig.add_axes([0.12, 0.20, 0.80, 0.18], sharex=ax)
    xx = np.arange(len(sens))
    ax.plot(xx, sens.mean_rating, marker="o", color=BLUE, lw=2.2)
    for i, m in enumerate(sens.mean_rating):
        ax.annotate(dec(m), (i, m), xytext=(0, 10), textcoords="offset points", ha="center")
    ax.set(ylim=(sens.mean_rating.min() - 0.03, sens.mean_rating.max() + 0.05), ylabel="Rating trung bình")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 2)))
    ax.tick_params(labelbottom=False)
    axn.bar(xx, sens.n, width=0.52, color=[TEAL if t == 100 else "#9DB8CE" for t in sens.min_ratings])
    for i, n in enumerate(sens.n):
        axn.text(i, n + sens.n.max() * 0.02, number(n), ha="center", fontsize=9.5)
    axn.set(xticks=xx, xticklabels=[number(v) for v in sens.min_ratings], ylabel="Số bản ghi",
            xlabel="Ngưỡng lượt chấm tối thiểu", ylim=(0, sens.n.max() * 1.18))
    axn.yaxis.set_major_formatter(FuncFormatter(lambda x, _: number(x)))
    polish(ax)
    polish(axn)
    save(fig, "13_DoNhay_NguongLuotCham.png")

    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=HERE, help="Thư mục chứa data/processed/")
    parser.add_argument("--output-dir", type=Path, default=HERE / "chart_outputs")
    args = parser.parse_args()
    n = run(args.data_root.resolve(), args.output_dir.resolve())
    print(f"Xong: {n} biểu đồ trong {args.output_dir}")


if __name__ == "__main__":
    main()
