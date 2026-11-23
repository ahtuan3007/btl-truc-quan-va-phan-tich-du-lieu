"""Thống kê mô tả, so sánh nhóm và xuất các bảng EDA Goodreads."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MIN_GROUP_SIZE = 30
SENSITIVITY_THRESHOLDS = (1, 100, 500, 1000)
NUM_COLS = ["rating", "pages", "n_ratings", "n_reviews", "publication_year"]


def describe(df, cols=NUM_COLS):
    """Thống kê mô tả, số quan sát riêng theo biến."""
    d = df[cols].astype(float)
    out = pd.DataFrame(
        {
            "n": d.count(),
            "missing": d.isna().sum(),
            "mean": d.mean(),
            "sd": d.std(),
            "min": d.min(),
            "q05": d.quantile(0.05),
            "q25": d.quantile(0.25),
            "median": d.median(),
            "q75": d.quantile(0.75),
            "q95": d.quantile(0.95),
            "max": d.max(),
        }
    )
    out.index.name = "variable"
    return out.reset_index()


def group_summary(frame, key):
    """N là số Book Id duy nhất trong nhóm; nhóm đa nhãn có thể chồng lấn."""
    g = frame.dropna(subset=[key]).groupby(key, sort=True, observed=True)
    out = g.agg(
        n=("book_id", "nunique"),
        mean=("rating", "mean"),
        median=("rating", "median"),
        sd=("rating", "std"),
        q25=("rating", lambda s: s.quantile(0.25)),
        q75=("rating", lambda s: s.quantile(0.75)),
        median_n_ratings=("n_ratings", "median"),
    ).reset_index()
    out[key] = out[key].astype(str)
    out["min_group_30"] = out["n"] >= MIN_GROUP_SIZE
    return out


def corr_table(frame, label):
    """Pearson và Spearman theo từng cặp có dữ liệu; log dùng ln(1+x)."""
    rows = []
    for col in ["pages", "n_ratings", "n_reviews", "publication_year"]:
        pair = pd.DataFrame({"x": frame[col], "y": frame["rating"]}).dropna().astype(float)
        rows.append(
            {
                "sample": label,
                "variable": col,
                "pairwise_n": len(pair),
                "spearman": pair["x"].rank().corr(pair["y"].rank()),
                "pearson_raw": pair["x"].corr(pair["y"]),
                "pearson_log1p": np.log1p(pair["x"]).corr(pair["y"]) if col != "publication_year" else np.nan,
            }
        )
    return pd.DataFrame(rows)


def by_mean(g):
    """Chỉ lấy nhóm đủ cỡ mẫu, sắp xếp theo mean giảm dần."""
    return g.loc[g["min_group_30"]].sort_values(["mean", "n"], ascending=False)


def load_data(data_root):
    processed = data_root / "data/processed"
    clean = pd.read_csv(
        processed / "books_cleaned_master.csv",
        dtype={"book_id": str, "pages": "Int64", "publication_year": "Int64", "publication_decade": "Int64"},
        keep_default_na=False,
        na_values=[""],
    )
    bridge = pd.read_csv(processed / "book_genres_bridge.csv", dtype=str, keep_default_na=False)
    return clean, bridge


def run_eda(data_root, output_root):
    clean, bridge = load_data(data_root)
    tables = output_root / "eda_tables"
    tables.mkdir(parents=True, exist_ok=True)

    def save(df, name, index=False):
        df.to_csv(tables / f"{name}.csv", index=index, encoding="utf-8-sig", float_format="%.8f")

    N = len(clean)
    eligible = clean.loc[clean["rating_eligible"]]
    primary = clean.loc[clean["primary_sample"]]

    # 1. Thống kê mô tả
    save(describe(eligible), "descriptive_eligible")
    save(describe(primary), "descriptive_primary")

    # 2. Độ nhạy theo ngưỡng số lượt đánh giá
    sensitivity, correlations = [], []
    for t in SENSITIVITY_THRESHOLDS:
        s = eligible.loc[eligible["n_ratings"].ge(t)]
        sensitivity.append(
            {
                "min_ratings": t,
                "n": len(s),
                "retained_pct_raw": len(s) / N * 100,
                "mean_rating": s["rating"].mean(),
                "median_rating": s["rating"].median(),
                "sd_rating": s["rating"].std(),
                "q25": s["rating"].quantile(0.25),
                "q75": s["rating"].quantile(0.75),
            }
        )
        correlations.append(corr_table(s, f"min_ratings_{t}"))
    save(pd.DataFrame(sensitivity), "threshold_sensitivity")
    save(pd.concat(correlations, ignore_index=True), "correlations_by_threshold")

    # 3. So sánh nhóm
    for col, name in [
        ("page_band", "pages"),
        ("language_group", "language"),
        ("publisher_clean", "publisher"),
        ("publication_decade", "decade"),
    ]:
        g = group_summary(primary, col)
        save(g, f"group_{name}_all")
        save(by_mean(g), f"group_{name}_n30")

    joined = primary[
        ["book_id", "rating", "n_ratings", "n_reviews", "pages", "language_group", "publication_year", "publication_decade"]
    ].merge(bridge, on="book_id", validate="one_to_many")
    genre_groups = group_summary(joined, "genre_label")
    genre_top_n = genre_groups.sort_values("n", ascending=False).head(12)
    save(genre_groups, "group_genre_all")
    save(by_mean(genre_groups), "group_genre_n30")
    save(genre_top_n, "group_genre_top12_by_size")

    # 4. Ví dụ lọc dữ liệu
    filtered = primary.loc[
        primary["pages"].gt(0)
        & primary["publication_year"].between(1990, 2010)
        & primary["language_group"].eq("English"),
        ["book_id", "title_clean", "rating", "pages", "n_ratings", "publication_year", "language_group"],
    ]
    save(filtered, "filter_example_English_1990_2010_pages_positive")

    # 5. Pivot thập niên x nhóm số trang
    pivot_args = dict(index="publication_decade", columns="page_band", observed=True)
    mean_pivot = primary.pivot_table(values="rating", aggfunc="mean", **pivot_args)
    n_pivot = primary.pivot_table(values="book_id", aggfunc="nunique", **pivot_args).fillna(0).astype(int)
    save(mean_pivot, "pivot_rating_decade_by_pages", index=True)
    save(n_pivot, "pivot_n_decade_by_pages", index=True)
    save(mean_pivot.where(n_pivot.ge(MIN_GROUP_SIZE)), "pivot_rating_decade_by_pages_n30", index=True)

    # 6. Độ nhạy theo phiên bản sách (mỗi title+author giữ 1 bản nhiều đánh giá nhất)
    approx = primary.sort_values(["n_ratings", "book_id"], ascending=[False, True]).drop_duplicates(
        "title_author_key"
    )
    save(corr_table(approx, "approx_one_per_title_author"), "correlations_edition_sensitivity")
    approx_joined = approx[["book_id", "rating", "n_ratings"]].merge(bridge, on="book_id", validate="one_to_many")
    save(group_summary(approx_joined, "genre_label"), "group_genre_edition_sensitivity")
    save(group_summary(approx, "publisher_clean"), "group_publisher_edition_sensitivity")

    # 7. Độ nhạy theo số trang và phân tầng
    save(
        corr_table(primary.loc[primary["pages"].between(20, 2000)], "pages_20_2000_sensitivity"),
        "correlations_pages_sensitivity",
    )
    stratified = [
        corr_table(joined.loc[joined["genre_label"].eq(g)], f"genre: {g}")
        for g in genre_top_n["genre_label"].head(6)
    ]
    stratified.append(corr_table(primary.loc[primary["language_group"].eq("English")], "language: English"))
    save(pd.concat(stratified, ignore_index=True), "correlations_stratified")

    # 8. Luồng mẫu
    flow = pd.DataFrame(
        [
            ("raw/master", N),
            ("rating 1-5", int(clean["rating"].between(1, 5).sum())),
            ("eligible rating and count>0", len(eligible)),
            ("primary count>=100", len(primary)),
            ("primary with positive pages", int(primary["pages"].notna().sum())),
            ("primary with valid publication date", int(primary["publication_date_iso"].notna().sum())),
            ("primary with genres", int((~primary["genres_missing"]).sum())),
            ("primary with publisher", int(primary["publisher_clean"].notna().sum())),
            ("approx one per title+author", len(approx)),
        ],
        columns=["sample", "n"],
    )
    save(flow, "sample_flow")
    return len(primary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=HERE)
    parser.add_argument("--output-root", type=Path, default=HERE)
    args = parser.parse_args()
    n = run_eda(args.data_root, args.output_root)
    print(f"Xong EDA. primary_n = {n}. Kết quả trong {args.output_root / 'eda_tables'}")


if __name__ == "__main__":
    main()
