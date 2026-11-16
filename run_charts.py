"""Stage 6: reproducible static charts from the reviewed Goodreads snapshot.

Read-only inputs. No cleaning, pipeline rerun, Power BI modification, or sampling.
Run after placing this file beside run_phase_4_5.py, or pass --data-root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
LOCKED_HASHES = {
    "data/raw/Goodreads_books_with_genres.csv": "721fc3bbe6367e91f2d3537d2cbe1c1ca4b585535d8ce63862c38a353d662b97",
    "data/processed/books_cleaned_master.csv": "7985d617d177b64d51396f027bc529edbe72ddbdc7b34e8f66196831ba14d929",
    "data/processed/book_genres_bridge.csv": "87a13c46b0d89473292f325287415d4aecc58e5a7c47c43456594b2d7dee97f7",
}
PRIMARY_N = 8402
MIN_GROUP_N = 30
TOP_N = 12
PAGE_BANDS = ["1-200", "201-400", "401-600", "601+"]
RATING_BIN_LABELS = ["1 ≤ R < 3,5", "3,5 ≤ R < 4", "4 ≤ R < 4,5", "4,5 ≤ R ≤ 5"]
BLUE, TEAL, INK, GRAY = "#2563A0", "#147D80", "#24364A", "#66778A"
PALETTE = ["#CFDEE9", "#77A9C7", "#267AA0", "#11656C"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(x: float | int) -> str:
    return f"{int(x):,}".replace(",", ".")


def dec(x: float, places: int = 3) -> str:
    return f"{x:.{places}f}".replace(".", ",")


def as_records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.to_json(orient="records", force_ascii=False))


def wrapped(value: str, width: int = 29) -> str:
    return "\n".join(textwrap.wrap(str(value), width=width, break_long_words=False))


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10.5,
            "axes.labelcolor": INK,
            "axes.edgecolor": "#AAB6C1",
            "text.color": INK,
            "xtick.color": GRAY,
            "ytick.color": GRAY,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.titleweight": "bold",
        }
    )


def figure(title: str, subtitle: str, note: str, height: float = 6.4):
    fig = plt.figure(figsize=(11.6, height))
    fig.suptitle(title, x=0.075, y=0.965, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.075, 0.91, subtitle, fontsize=10.7, color=GRAY, va="top")
    fig.text(0.075, 0.052, note, fontsize=9.1, color=GRAY, va="bottom", linespacing=1.45)
    return fig


def axis(fig, left=0.10, bottom=0.20, width=0.84, height=0.61):
    return fig.add_axes([left, bottom, width, height])


def polish(ax, grid="y") -> None:
    ax.set_axisbelow(True)
    ax.grid(axis=grid, color="#E8EDF2", linewidth=0.8)
    ax.tick_params(length=0, pad=7)


def validate_and_load(root: Path):
    """Verify source locks and recompute chart data against reviewed EDA CSVs."""
    input_hashes = {}
    for rel, expected in LOCKED_HASHES.items():
        actual = digest(root / rel)
        if actual != expected:
            raise ValueError(f"Input fingerprint differs from reviewed snapshot: {rel}")
        input_hashes[rel] = actual

    master_text = pd.read_csv(root / "data/processed/books_cleaned_master.csv", dtype=str, keep_default_na=False)
    raw = pd.read_csv(root / "data/raw/Goodreads_books_with_genres.csv", dtype=str, keep_default_na=False)
    if len(master_text) != 11127 or not master_text[raw.columns].equals(raw):
        raise ValueError("Master does not preserve all 11,127 original records/values.")
    master = master_text.copy()
    for col in ["rating", "n_ratings", "n_reviews", "pages", "publication_year", "publication_decade"]:
        master[col] = pd.to_numeric(master[col].replace("", np.nan), errors="raise")
    master["book_id"] = master.book_id.astype(str)
    if not master.book_id.is_unique:
        raise ValueError("Master key is not unique.")
    expected_primary = master.rating.between(1, 5) & master.n_ratings.ge(100)
    if not expected_primary.equals(master_text.primary_sample.eq("True")):
        raise ValueError("Primary sample flag does not match the documented rule.")
    primary = master.loc[expected_primary].copy()
    if len(primary) != PRIMARY_N:
        raise ValueError("Primary sample size differs from the reviewed 8,402 records.")
    bridge = pd.read_csv(root / "data/processed/book_genres_bridge.csv", dtype=str, keep_default_na=False)
    if len(bridge) != 94794 or bridge.duplicated(["book_id", "genre_label"]).any():
        raise ValueError("Genre bridge contains duplicate pairs or unexpected row count.")
    if not bridge.book_id.isin(master.book_id).all():
        raise ValueError("Genre bridge has orphan Book Id values.")
    expected_pairs = {(bid, g.strip()) for bid, gs in zip(raw["Book Id"], raw.genres) for g in gs.split(";") if g.strip()}
    if set(bridge.itertuples(index=False, name=None)) != expected_pairs:
        raise ValueError("Bridge labels differ from the original semicolon-separated labels.")
    joined = bridge.merge(primary, on="book_id", how="inner", validate="many_to_one")

    def read_eda(name):
        rel = f"eda_tables/{name}.csv"
        input_hashes[rel] = digest(root / rel)
        return pd.read_csv(root / rel)

    def compare_groups(frame, key, name):
        calculated = frame.loc[frame[key].ne("") & frame[key].notna()].groupby(key, sort=True).agg(n=("book_id", "nunique"), mean=("rating", "mean"))
        reference = read_eda(name).set_index(key)
        reference.index = reference.index.astype(calculated.index.dtype)
        if set(calculated.index) != set(reference.index):
            raise ValueError(f"Group labels differ from existing EDA: {name}")
        ref = reference.reindex(calculated.index)
        if not np.array_equal(calculated.n, ref.n) or not np.allclose(calculated["mean"], ref["mean"], atol=5.1e-9, rtol=0):
            raise ValueError(f"Group count/mean mismatch against existing EDA: {name}")
        return reference.reset_index()

    groups = {
        "pages": compare_groups(primary, "page_band", "group_pages_all"),
        "language": compare_groups(primary, "language_group", "group_language_all"),
        "publisher": compare_groups(primary, "publisher_clean", "group_publisher_all"),
        "decade": compare_groups(primary, "publication_decade", "group_decade_all"),
        "genre": compare_groups(joined, "genre_label", "group_genre_all"),
    }
    correlations = read_eda("correlations_by_threshold")
    main_correlations = correlations.loc[correlations["sample"].eq("min_ratings_100")].set_index("variable")
    for col in ["pages", "n_ratings", "n_reviews", "publication_year"]:
        pair = primary[[col, "rating"]].dropna()
        rho = pair[col].rank().corr(pair.rating.rank())
        if len(pair) != int(main_correlations.loc[col, "pairwise_n"]) or abs(rho - main_correlations.loc[col, "spearman"]) > 5.1e-9:
            raise ValueError(f"Correlation/count mismatch: {col}")
    sensitivity = read_eda("threshold_sensitivity")
    for row in sensitivity.itertuples():
        sub = master.loc[master.rating.between(1, 5) & master.n_ratings.ge(row.min_ratings)]
        if len(sub) != int(row.n) or abs(sub.rating.mean() - row.mean_rating) > 5.1e-9:
            raise ValueError("Threshold sensitivity table does not match master.")
    checks = {
        "raw_and_master_hashes_locked": True,
        "original_13_columns_and_11127_rows_preserved": True,
        "unique_master_book_ids": True,
        "primary_8402_no_sampling": True,
        "genre_bridge_94794_exact_unique_pairs": True,
        "five_group_tables_recomputed_against_existing_eda": True,
        "four_correlations_and_pairwise_counts_recomputed": True,
        "threshold_counts_and_means_recomputed": True,
        "primary_missing_pages_17": int(primary.pages.isna().sum()) == 17,
        "primary_missing_year_1": int(primary.publication_year.isna().sum()) == 1,
        "primary_missing_publisher_3": int(primary.publisher_clean.eq("").sum()) == 3,
        "primary_missing_genre_2": int(primary.genres.eq("").sum()) == 2,
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    return master, primary, bridge, joined, groups, main_correlations, sensitivity, input_hashes, checks


def run(data_root: Path, output_dir: Path, work_dir: Path) -> dict:
    loaded = validate_and_load(data_root)
    master, primary, bridge, joined, groups, correlations, sensitivity, input_hashes, checks = loaded
    output_dir = output_dir.resolve()
    work_dir = work_dir.resolve()
    # Only this script's named products are replaced. Never clear a directory.
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    table_dir = work_dir / "BangThamChieu"
    table_dir.mkdir(exist_ok=True)
    configure_style()
    mean = float(primary.rating.mean())
    median = float(primary.rating.median())
    chart_entries = []

    def save(fig, filename, title, subtitle, caption, n, factors, extra=None):
        path = output_dir / filename
        fig.savefig(path, dpi=190, metadata={"Title": title, "Description": caption, "Software": f"Matplotlib {matplotlib.__version__}"})
        plt.close(fig)
        entry = {
            "file": filename, "title": title, "sample": subtitle, "n": int(n),
            "factors": factors, "caption": caption, "sha256": digest(path),
            "width_inches": float(fig.get_figwidth()), "height_inches": float(fig.get_figheight()),
        }
        if extra:
            entry.update(extra)
        chart_entries.append(entry)

    # 01: distribution, every primary record included.
    title = "Phân phối Rating trong mẫu phân tích chính"
    subtitle = "8.402 bản ghi · Rating 1–5 · ít nhất 100 lượt chấm"
    note = "Mỗi bản ghi có trọng số như nhau; không nhân theo lượt chấm.\nNguồn: Goodreads-books-with-genres; dữ liệu gốc và thời điểm bổ sung genre khác nhau."
    fig = figure(title, subtitle, note)
    ax = axis(fig)
    # Match Power BI's decimal intervals; floating linspace edges can put an
    # exact boundary such as 3.9 into the preceding interval.
    hundredths = np.rint(primary.rating.to_numpy()*100).astype("int64")
    bin_codes = hundredths // 10
    codes = np.arange(10, 50)
    counts = np.array([(bin_codes == code).sum() for code in codes])
    ax.bar(codes/10, counts, width=0.1, align="edge", color=BLUE,
           edgecolor="white", linewidth=0.5)
    if int(counts.sum()) != PRIMARY_N:
        raise AssertionError("Histogram omitted a primary record.")
    ax.axvline(mean, color=TEAL, lw=1.8, label=f"Trung bình {dec(mean)}")
    ax.axvline(median, color=INK, lw=1.2, linestyle="--", label=f"Trung vị {dec(median, 2)}")
    ax.set(xlim=(1, 5), xlabel="Rating", ylabel="Số bản ghi")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 1)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: number(x)))
    ax.legend(frameon=False, loc="upper left")
    polish(ax)
    save(fig, "01_PhanPhoi_Rating_MauChinh.png", title, subtitle,
         f"Mẫu chính có trung bình {dec(mean)}, trung vị {dec(median, 2)}; các khoảng [x;x+0,1) dùng quy tắc thập phân khớp Power BI.", PRIMARY_N, ["rating"],
         {"histogram_left_edges": (codes/10).tolist(), "histogram_counts": counts.tolist(),
          "bin_definition": "floor(round(rating*100)/10)/10; [x,x+0.1)"})

    # 02: distributions by page band; unknown pages are not filled with zero.
    page_valid = primary.loc[primary.pages.notna() & primary.pages.gt(0)]
    arrays = [page_valid.loc[page_valid.page_band.eq(b), "rating"].to_numpy() for b in PAGE_BANDS]
    title = "Phân phối Rating theo nhóm số trang"
    subtitle = "8.385 bản ghi có số trang dương · 17 bản ghi thiếu số trang không dùng trong hình"
    note = "Hộp: Q1–Q3; vạch giữa: trung vị; râu: 1,5 IQR; các chấm ngoài râu vẫn được giữ.\nSố trang là đặc điểm ghi trên bản ghi/ấn bản; nhóm thể loại và tuyển tập có thể khác nhau."
    fig = figure(title, subtitle, note)
    ax = axis(fig)
    boxes = ax.boxplot(arrays, tick_labels=[f"{b} trang\nn = {number(len(a))}" for b, a in zip(PAGE_BANDS, arrays)], patch_artist=True,
                       medianprops={"color": INK, "linewidth": 1.8}, whiskerprops={"color": GRAY}, capprops={"color": GRAY},
                       flierprops={"marker": ".", "markersize": 2.5, "alpha": 0.3, "markeredgecolor": BLUE})
    for box, color in zip(boxes["boxes"], PALETTE):
        box.set(facecolor=color, edgecolor=BLUE, alpha=0.8)
    ax.axhline(mean, color=TEAL, lw=1, linestyle="--", label=f"Trung bình mẫu chính {dec(mean)}")
    ax.set(ylim=(1, 5), ylabel="Rating")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 1)))
    ax.legend(frameon=False, loc="lower right")
    polish(ax)
    save(fig, "02_Boxplot_Rating_NhomSoTrang.png", title, subtitle,
         "Các phân phối Rating chồng lấn. Chênh lệch nhóm độ dài chưa chứng minh thêm số trang sẽ làm Rating tăng.", len(page_valid), ["pages"])

    def mean_bar(table, key, filename, title, subtitle, note, factor, width=29):
        fig = figure(title, subtitle, note, height=7.5 if len(table) > 7 else 6.3)
        left = 0.34 if len(table) > 7 else 0.23
        ax = axis(fig, left=left, bottom=0.20, width=0.94-left, height=0.61)
        ypos = np.arange(len(table))
        ax.barh(ypos, table["mean"], color=BLUE, height=0.64)
        ax.set_yticks(ypos, [wrapped(v, width) for v in table[key]])
        ax.invert_yaxis()
        ax.axvline(mean, color=TEAL, linestyle="--", lw=1.2, label=f"Toàn mẫu chính: {dec(mean)}")
        label_x = max(float(table["mean"].max()) + 0.10, mean + 0.15)
        for i, row in enumerate(table.itertuples(index=False)):
            ax.text(label_x, i, f"{dec(float(getattr(row, 'mean')))}  ·  n={number(getattr(row, 'n'))}", va="center", fontsize=9.4)
        ax.set(xlim=(0, 5.65), xticks=[0, 1, 2, 3, 4, 5], xlabel="Rating trung bình theo bản ghi")
        ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.01), fontsize=9.3)
        polish(ax, "x")
        displayed_n = int(joined.loc[joined.genre_label.isin(table[key]), "book_id"].nunique()) if factor == "genres" else int(table.n.sum())
        low = table.loc[table["mean"].idxmin()]
        high = table.loc[table["mean"].idxmax()]
        finding = "" if factor == "pages" else f"Trong các nhóm hiển thị, {high[key]} có trung bình {dec(float(high['mean']))} (n={number(high['n'])}); {low[key]} có trung bình {dec(float(low['mean']))} (n={number(low['n'])}). "
        save(fig, filename, title, subtitle, finding + note.replace("\n", " "), displayed_n, [factor],
             {"group_n_is_overlapping": factor == "genres", "sum_group_memberships": int(table.n.sum()), "groups": as_records(table)})

    pages_table = groups["pages"].set_index("page_band").loc[PAGE_BANDS].reset_index()
    mean_bar(pages_table, "page_band", "03_TrungBinh_Rating_NhomSoTrang.png", "Rating trung bình theo nhóm số trang",
             "Mẫu chính có số trang dương · bốn nhóm đều có ít nhất 30 bản ghi",
             "Nhóm 601+ trang: 4,119; nhóm 201–400: 3,912. Nhóm 1–200 cao hơn 201–400 nên không có xu hướng tăng đều.\nĐường đứt: trung bình 8.402 bản ghi; không phải mô hình nhân quả.", "pages")

    # Exact case-sensitive EDA keys, largest groups rather than highest rating.
    genre_top = groups["genre"].loc[groups["genre"].n.ge(MIN_GROUP_N)].sort_values(["n", "genre_label"], ascending=[False, True]).head(TOP_N)
    publisher_top = groups["publisher"].loc[groups["publisher"].n.ge(MIN_GROUP_N)].sort_values(["n", "publisher_clean"], ascending=[False, True]).head(TOP_N)
    mean_bar(genre_top, "genre_label", "04_Rating_Top12_NhanTheLoai_TheoN.png", "Rating của 12 nhãn thể loại có nhiều bản ghi nhất",
             "Chọn và sắp xếp theo n giảm dần; hòa n thì theo nhãn gốc · chỉ nhóm n ≥ 30",
             "Một sách thuộc nhiều nhãn; tổng n giữa các nhóm không cộng thành số sách duy nhất.\nGiữ nguyên nhãn và chữ hoa/thường; dấu phẩy bên trong nhãn không bị tách.", "genres")
    mean_bar(publisher_top, "publisher_clean", "05_Rating_Top12_NhaXuatBan_TheoN.png", "Rating của 12 nhà xuất bản có nhiều bản ghi nhất",
             "Chọn và sắp xếp theo n giảm dần; hòa n thì theo tên gốc · chỉ nhóm n ≥ 30",
             "Giữ tên sau chuẩn hóa khoảng trắng; không gộp theo chữ thường hoặc gộp các imprint.\nKhác biệt có thể phản ánh cơ cấu tác phẩm; chưa đo tác động của nhà xuất bản.", "publisher")

    # 06 and 07: language coverage and adequately-supported comparisons.
    languages = groups["language"].sort_values(["n", "language_group"], ascending=[False, True]).copy()
    counts_language = languages[["language_group", "n"]].head(8).reset_index(drop=True).copy()
    remainder = int(languages.n.sum() - counts_language.n.sum())
    if remainder:
        counts_language.loc[len(counts_language)] = ["Các mã còn lại", remainder]
    if int(counts_language.n.sum()) != PRIMARY_N:
        raise AssertionError("Language coverage chart does not reconcile to 8,402 records.")
    title = "Mức độ bao phủ ngôn ngữ trong mẫu chính"
    subtitle = f"English: 8.212 / 8.402 bản ghi ({dec(8212/8402*100, 2)}%)"
    fig = figure(title, subtitle, "English gộp eng, en-US, en-GB, en-CA; các mã khác giữ riêng.\nHình hiển thị tám nhóm nhiều bản ghi nhất và phần còn lại; trục số lượng theo log10.", height=6.8)
    ax = axis(fig, left=0.23, width=0.70)
    y = np.arange(len(counts_language))
    ax.barh(y, counts_language.n, color=[TEAL] + [BLUE]*(len(y)-1), height=0.65)
    ax.set_yticks(y, counts_language.language_group)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(0.7, 18000)
    ax.set_xticks([1, 10, 100, 1000, 10000], ["1", "10", "100", "1.000", "10.000"])
    for i, row in enumerate(counts_language.itertuples()):
        ax.text(row.n*1.15, i, f"{number(row.n)} ({dec(row.n/PRIMARY_N*100, 2)}%)", va="center", fontsize=9.5)
    ax.set_xlabel("Số bản ghi, trục log10")
    polish(ax, "x")
    save(fig, "06_BaoPhu_NgonNgu.png", title, subtitle, "So sánh ngôn ngữ mất cân đối mạnh: English chiếm 97,74% mẫu chính; không suy rộng các nhóm nhỏ.", PRIMARY_N, ["language"])
    supported_languages = languages.loc[languages.n.ge(MIN_GROUP_N)].copy()
    mean_bar(supported_languages, "language_group", "07_Rating_NgonNgu_N30.png", "Rating theo ngôn ngữ có đủ số bản ghi",
             "Chỉ nhóm n ≥ 30 · sắp xếp theo số bản ghi, không theo Rating",
             "English chiếm phần lớn mẫu. Mỗi nhóm có cơ cấu sách và ấn bản khác nhau.\nKhông kết luận ngôn ngữ gây ra chênh lệch Rating; các mã nhỏ không bị xóa khỏi master.", "language")

    # 08: cohort mean with a separate denominator panel.
    decades = groups["decade"].copy()
    decades["publication_decade"] = decades.publication_decade.astype(int)
    decades = decades.set_index("publication_decade").reindex(range(1900, 2030, 10))
    decades["n"] = decades.n.fillna(0).astype(int)
    decades["mean_shown_n30"] = decades["mean"].where(decades.n.ge(MIN_GROUP_N))
    title = "Rating theo thập niên xuất bản của bản ghi"
    subtitle = "8.401 bản ghi có ngày hợp lệ · chỉ vẽ Rating trung bình khi nhóm có n ≥ 30"
    fig = figure(title, subtitle, "Đường đứt: trung bình mẫu chính 3,955. Năm của bản ghi/ấn bản, chưa xác minh năm xuất bản đầu tiên.\nĐây là so sánh nhóm năm xuất bản, không phải lịch sử Rating tăng hoặc giảm theo thời gian.", height=7.2)
    ax = fig.add_axes([0.105, 0.48, 0.83, 0.32])
    axn = fig.add_axes([0.105, 0.20, 0.83, 0.19], sharex=ax)
    ax.plot(decades.index, decades.mean_shown_n30, marker="o", color=BLUE, lw=2.2)
    ax.axhline(mean, color=TEAL, linestyle="--", lw=1.1)
    for yr, row in decades.loc[decades.n.ge(MIN_GROUP_N)].iterrows():
        ax.annotate(dec(row["mean"]), (yr, row["mean"]), xytext=(0, 10), textcoords="offset points", ha="center", fontsize=9)
    ax.set(ylim=(3.75, 4.25), ylabel="Rating trung bình")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 1)))
    ax.tick_params(labelbottom=False)
    axn.bar(decades.index, decades.n, width=7.5, color=[BLUE if v>=MIN_GROUP_N else "#B9C6D2" for v in decades.n])
    for yr, value in decades.n.items():
        if value:
            axn.text(yr, value + 120, number(value), ha="center", fontsize=8.6)
    axn.set(xticks=list(decades.index), xlabel="Thập niên xuất bản trên bản ghi", ylabel="Số bản ghi", ylim=(0, 7200))
    axn.yaxis.set_major_formatter(FuncFormatter(lambda x, _: number(x)))
    axn.set_xticklabels([str(v) for v in decades.index], fontsize=8.8)
    polish(ax)
    polish(axn)
    save(fig, "08_Rating_VaN_TheoThapNien.png", title, subtitle,
         "Các nhóm năm khác nhau có cỡ mẫu rất khác nhau; thập niên 2000 chiếm 5.833 bản ghi. Trung bình của nhóm n<30 không được vẽ.", 8401, ["publication_year"])

    # 09: percentages are conditional on genre, not portions of a disjoint whole.
    selected = joined.loc[joined.genre_label.isin(genre_top.genre_label)].copy()
    selected["rating_bin"] = pd.cut(selected.rating, [1, 3.5, 4, 4.5, 5.0000001], right=False, labels=RATING_BIN_LABELS)
    composition = selected.groupby(["genre_label", "rating_bin"], observed=False).book_id.nunique().unstack(fill_value=0).reindex(genre_top.genre_label)
    if not np.array_equal(composition.sum(axis=1), genre_top.n):
        raise AssertionError("100% stack denominator differs from unique books in genre.")
    shares = composition.div(composition.sum(axis=1), axis=0)*100
    title = "Cơ cấu mức Rating trong 12 nhãn thể loại phổ biến"
    subtitle = "12 nhãn phổ biến theo n · cột chồng 100% tính riêng trong từng nhãn"
    fig = figure(title, subtitle, "Mẫu số mỗi thanh là số Book Id duy nhất trong nhãn; n thể hiện bên phải.\nNhãn đa trị chồng lấn giữa các thanh; không cộng tỷ lệ hoặc số sách qua các nhãn.", height=7.7)
    ax = axis(fig, left=0.34, width=0.59, height=0.60)
    left = np.zeros(len(shares))
    for label, color in zip(RATING_BIN_LABELS, PALETTE):
        vals = shares[label].to_numpy()
        ax.barh(np.arange(len(shares)), vals, left=left, color=color, height=0.67, label=label, edgecolor="white", linewidth=0.3)
        for i, (val, start) in enumerate(zip(vals, left)):
            if val >= 12:
                ax.text(start+val/2, i, f"{dec(val, 0)}%", ha="center", va="center", fontsize=8.9, color=INK if color==PALETTE[0] else "white")
        left += vals
    ax.set_yticks(np.arange(len(shares)), [wrapped(v) for v in shares.index])
    ax.invert_yaxis()
    for i, value in enumerate(composition.sum(axis=1)):
        ax.text(101, i, f"n={number(value)}", va="center", fontsize=9)
    ax.set(xlim=(0, 114), xticks=[0, 25, 50, 75, 100], xlabel="Tỷ lệ bản ghi trong nhãn (%)")
    ax.legend(frameon=False, ncol=2, loc="lower left", bbox_to_anchor=(0, 1.01), fontsize=9)
    polish(ax, "x")
    save(fig, "09_CotChong100_Rating_TheoTheLoai.png", title, subtitle,
         "Các mức Rating dùng khoảng [1;3,5), [3,5;4), [4;4,5), [4,5;5]. Tỷ lệ được tính riêng trong từng nhãn đa trị.", int(selected.book_id.nunique()), ["genres", "rating"],
         {"membership_rows": len(selected), "unique_books_in_selected_genres": int(selected.book_id.nunique()), "rating_bins": RATING_BIN_LABELS})

    # 10-12: scatter all individual records, never means or random samples.
    def scatter(col, filename, title, xlabel, log_display=False):
        sub = primary.loc[primary[col].notna()].copy()
        if col == "pages":
            sub = sub.loc[sub.pages.gt(0)]
        subtitle = f"{number(len(sub))} chấm = {number(len(sub))} Book Id · giữ toàn bộ bản ghi có dữ liệu cho cặp biến"
        note = "Đường đứt: Rating trung bình mẫu chính. Không khớp đường hồi quy hoặc suy luận nhân quả.\nLượt chấm/nhận xét có thể khác cấp tác phẩm và ấn bản; xem giới hạn nguồn trong báo cáo."
        fig = figure(title, subtitle, note)
        ax = axis(fig)
        xs = np.log1p(sub[col]) if log_display else sub[col]
        points = ax.scatter(xs, sub.rating, s=10, alpha=0.23, c=BLUE, edgecolors="none", rasterized=True)
        if points.get_offsets().shape[0] != len(sub) or not np.isfinite(np.asarray(xs, dtype=float)).all():
            raise AssertionError("Scatter plot does not contain every finite individual record.")
        ax.axhline(mean, color=TEAL, linestyle="--", lw=1.2)
        rho = sub[col].rank().corr(sub.rating.rank())
        ax.text(0.99, 0.98, f"Spearman ρ = {dec(rho, 3)}\nn = {number(len(sub))}", transform=ax.transAxes, ha="right", va="top", color=INK, fontsize=10)
        ax.set(xlabel=xlabel, ylabel="Rating", ylim=(1, 5.05))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 1)))
        if log_display:
            ticks = [0, 10, 100, 1000, 10000, 100000, 1000000, 5000000]
            ticks = [t for t in ticks if t >= (0 if sub[col].min()==0 else 100) and t <= sub[col].max()*1.1]
            ax.set_xticks(np.log1p(ticks), [number(t) for t in ticks])
        else:
            ax.set_xlim(0, float(sub[col].max())*1.03)
            ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: number(v)))
        polish(ax)
        save(fig, filename, title, subtitle,
             f"Hiển thị toàn bộ {number(len(sub))} bản ghi, không lấy mẫu hoặc tổng hợp thành điểm trung bình. Spearman ρ = {dec(rho, 6)}. " + ("Trục ngang đặt tại ln(1+x), nhãn hiển thị số gốc; phép log chỉ phục vụ hiển thị." if log_display else "Trục số trang tuyến tính, giữ cả bản ghi nhiều trang."), len(sub), [col],
             {"scatter_points": len(sub), "x_display_transform": "ln(1+x)" if log_display else "none", "spearman": float(rho)})

    scatter("pages", "10_Scatter_Rating_SoTrang.png", "Mối liên hệ giữa số trang và Rating", "Số trang trên bản ghi/ấn bản")
    scatter("n_ratings", "11_Scatter_Rating_LuotCham.png", "Mối liên hệ giữa lượt chấm sao và Rating", "Số lượt chấm sao — trục ln(1+x), nhãn số gốc", True)
    scatter("n_reviews", "12_Scatter_Rating_NhanXet.png", "Mối liên hệ giữa số bài nhận xét và Rating", "Số bài nhận xét — trục ln(1+x), nhãn số gốc", True)

    # 13: threshold sensitivity is an explicit sample change, not source cleaning.
    title = "Độ nhạy của Rating trung bình theo ngưỡng lượt chấm"
    subtitle = "Bốn ngưỡng 1, 100, 500 và 1.000 · không xóa vĩnh viễn các bản ghi dưới ngưỡng"
    fig = figure(title, subtitle, "Mỗi ngưỡng tạo một tập bản ghi khác nhau, không phải diễn biến theo thời gian.\nMốc 100 là quy ước của mẫu chính, không bảo đảm tính đại diện hoặc độ chính xác thống kê.", height=7.0)
    ax = fig.add_axes([0.12, 0.48, 0.80, 0.31])
    axn = fig.add_axes([0.12, 0.20, 0.80, 0.18], sharex=ax)
    xx = np.arange(len(sensitivity))
    ax.plot(xx, sensitivity.mean_rating, marker="o", color=BLUE, lw=2.2)
    for i, row in enumerate(sensitivity.itertuples()):
        ax.annotate(dec(row.mean_rating), (i, row.mean_rating), xytext=(0, 10), textcoords="offset points", ha="center")
    ax.set(ylim=(3.90, 4.02), ylabel="Rating trung bình")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: dec(x, 2)))
    ax.tick_params(labelbottom=False)
    axn.bar(xx, sensitivity.n, width=0.52, color=[TEAL if n==100 else "#9DB8CE" for n in sensitivity.min_ratings])
    for i, row in enumerate(sensitivity.itertuples()):
        axn.text(i, row.n+250, number(row.n), ha="center", fontsize=9.5)
    axn.set(xticks=xx, xticklabels=[number(v) for v in sensitivity.min_ratings], ylabel="Số bản ghi", xlabel="Ngưỡng lượt chấm tối thiểu", ylim=(0, 14000))
    axn.yaxis.set_major_formatter(FuncFormatter(lambda x, _: number(x)))
    polish(ax)
    polish(axn)
    save(fig, "13_DoNhay_NguongLuotCham.png", title, subtitle,
         "Rating trung bình thay đổi từ 3,943 ở ngưỡng 1 đến 3,964 ở ngưỡng 1.000, chênh lệch khoảng 0,021 điểm. Ngưỡng cao cũng làm giảm số quan sát.", int(sensitivity.n.max()), ["n_ratings", "sample_selection"], {"n_varies_by_threshold": True, "threshold_samples": as_records(sensitivity)})

    # Report facts: categorical and numeric evidence are not mixed into an effect ranking.
    factor_rows = []
    for col, label in [("pages", "Số trang"), ("n_ratings", "Lượt chấm sao"), ("n_reviews", "Bài nhận xét"), ("publication_year", "Nhóm năm xuất bản")]:
        factor_rows.append({"factor": label, "type": "numeric/pairwise", "n": int(correlations.loc[col, "pairwise_n"]), "missing_from_primary": PRIMARY_N-int(correlations.loc[col, "pairwise_n"]), "spearman": float(correlations.loc[col, "spearman"]), "supported_groups_n30": "", "selection": "all observed primary records; no sampling"})
    for key, label, frame, col in [("genre", "Nhãn thể loại", joined, "genre_label"), ("publisher", "Nhà xuất bản", primary.loc[primary.publisher_clean.ne("")], "publisher_clean"), ("language", "Ngôn ngữ", primary, "language_group")]:
        available = int(frame.book_id.nunique())
        factor_rows.append({"factor": label, "type": "categorical/group comparison", "n": available, "missing_from_primary": PRIMARY_N-available, "spearman": "", "supported_groups_n30": int(groups[key].n.ge(MIN_GROUP_N).sum()), "selection": "exact source-case labels; genre overlaps; top12 by n for genre/publisher"})
    factors = pd.DataFrame(factor_rows)
    for name, table in [("Top12_TheLoai_TheoN.csv", genre_top), ("Top12_NhaXuatBan_TheoN.csv", publisher_top), ("BaoPhu_NgonNgu.csv", languages), ("ThapNien_Rating_VaN.csv", decades.reset_index()), ("BayYeuTo_ThamChieu.csv", factors)]:
        table.to_csv(table_dir / name, index=False, encoding="utf-8-sig", float_format="%.8f")
    comp_long = composition.reset_index().melt(id_vars="genre_label", var_name="rating_bin", value_name="n")
    comp_long["genre_n"] = comp_long.genre_label.map(composition.sum(axis=1))
    comp_long["percent"] = comp_long.n / comp_long.genre_n * 100
    comp_long.to_csv(table_dir / "CotChong100_TheLoai_ChiTiet.csv", index=False, encoding="utf-8-sig", float_format="%.8f")
    facts = {
        "raw_records": len(master), "primary_records": PRIMARY_N,
        "primary_mean_rating": mean, "primary_median_rating": median,
        "primary_rating_q25": float(primary.rating.quantile(.25)), "primary_rating_q75": float(primary.rating.quantile(.75)),
        "primary_rating_min": float(primary.rating.min()), "primary_rating_max": float(primary.rating.max()),
        "primary_missing_pages": int(primary.pages.isna().sum()), "primary_missing_year": int(primary.publication_year.isna().sum()),
        "primary_missing_genre": int(primary.genres.eq("").sum()), "primary_missing_publisher": int(primary.publisher_clean.eq("").sum()),
        "primary_english_n": int(primary.language_group.eq("English").sum()), "primary_english_pct": float(primary.language_group.eq("English").mean()*100),
        "seven_factors": as_records(factors), "page_groups": as_records(pages_table), "genre_top12_by_n": as_records(genre_top),
        "publisher_top12_by_n": as_records(publisher_top), "language_supported_n30": as_records(supported_languages),
        "threshold_sensitivity": as_records(sensitivity), "decade_cohorts": as_records(decades.reset_index()),
        "rating_bins": RATING_BIN_LABELS, "comparison_min_group_n": MIN_GROUP_N,
        "categorical_top_rule": "n descending, original case-sensitive label ascending for ties; top 12 after n>=30",
        "unit": "Goodreads Book Id record/edition; not verified unique work",
        "cautions": ["No causal interpretation", "Publication cohort is not rating history", "Genres overlap; no sum across genre groups", "Work-level average vs edition-level counts remains uncertain", "No weights applied to claim population representativeness"],
    }
    (work_dir / "SuKien_ThamChieu_BaoCao.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    after = {rel: digest(data_root / rel) for rel in input_hashes}
    if after != input_hashes:
        raise AssertionError("A source input changed during chart generation.")
    checks.update({"all_inputs_unchanged_after_rendering": True, "language_coverage_reconciles_8402": int(counts_language.n.sum()) == PRIMARY_N, "scatter_pages_points_8385": 8385 == chart_entries[9]["scatter_points"], "scatter_rating_counts_points_8402": 8402 == chart_entries[10]["scatter_points"], "scatter_reviews_points_8402": 8402 == chart_entries[11]["scatter_points"], "thirteen_pngs": len(chart_entries)==13})
    if not all(checks.values()):
        raise AssertionError(checks)
    captions = ["# Chú thích hình cho phần trực quan hóa", "", "Tất cả hình dùng mẫu chính Rating 1–5 và n_ratings ≥ 100, trừ hình 13 đối chiếu ngưỡng. n trong so sánh nhóm là số Book Id duy nhất. Các hình tĩnh được dựng bằng Python từ dữ liệu đã kiểm tra.", ""]
    for i, entry in enumerate(chart_entries, 1):
        captions.extend([f"## Hình {i} {entry['title']}", "", f"File: `{entry['file']}`", "", entry["sample"], "", entry["caption"], ""])
    (output_dir / "ChuThich_Hinh_Python.md").write_text("\n".join(captions), encoding="utf-8")
    manifest = {
        "stage": "6 static Python visualizations", "source_dataset": "middlelight/goodreadsbookswithgenres, version 1",
        "primary_rule": "rating in [1,5] AND n_ratings>=100", "primary_n": PRIMARY_N, "min_group_n": MIN_GROUP_N,
        "sample_exception": "Figure 13 compares thresholds 1,100,500,1000 and has no single common denominator.",
        "input_sha256": input_hashes, "validation": checks,
        "software": {"python_chart_library": f"matplotlib {matplotlib.__version__}", "pandas": pd.__version__, "numpy": np.__version__},
        "charts": chart_entries,
    }
    (work_dir / "chart_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=HERE, help="Folder containing reviewed data/ and eda_tables/.")
    default_output = HERE.parent / "04_PowerBI_BanChinh/BieuDo_BaoCao" if HERE.name == "02_Code_DuLieu_EDA" else HERE / "chart_outputs"
    parser.add_argument("--output-dir", type=Path, default=default_output, help="PNG and caption destination. Replaces only this script's named products, not unrelated files.")
    parser.add_argument("--work-dir", type=Path, default=HERE / "work/charts_stage6", help="Manifest, validation, report facts and reference tables, separate from final PNGs.")
    args = parser.parse_args(argv)
    result = run(args.data_root.resolve(), args.output_dir, args.work_dir)
    print(json.dumps({"png_count": len(result["charts"]), "primary_n": result["primary_n"], "validation_passed": all(result["validation"].values())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
