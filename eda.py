"""Tính thống kê mô tả, so sánh nhóm và xuất các bảng EDA Goodreads."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from clean_data import (
    DEFAULT_OUTPUT_ROOT,
    HERE,
    PRIMARY_MIN_RATINGS,
    cleaning_diagnostics,
    load_cleaned,
    load_snapshot,
)


MIN_GROUP_SIZE = 30
SENSITIVITY_THRESHOLDS = (1, 100, 500, 1000)


def describe(df, cols):
    """Thống kê mô tả với số quan sát riêng theo biến."""
    rows = []
    for c in cols:
        s = df[c].dropna().astype(float)
        rows.append(
            {
                "variable": c,
                "n": len(s),
                "missing": int(df[c].isna().sum()),
                "mean": s.mean(),
                "sd": s.std(),
                "min": s.min(),
                "q05": s.quantile(0.05),
                "q25": s.quantile(0.25),
                "median": s.median(),
                "q75": s.quantile(0.75),
                "q95": s.quantile(0.95),
                "max": s.max(),
            }
        )
    return pd.DataFrame(rows)


def group_summary(frame, key):
    """N là Book Id duy nhất trong nhóm; nhóm đa nhãn có thể chồng lấn."""
    rows = []
    for label, g in frame.dropna(subset=[key]).groupby(key, sort=True, observed=True):
        s = g.rating.astype(float)
        rows.append(
            {
                key: str(label),
                "n": g.book_id.nunique(),
                "mean": s.mean(),
                "median": s.median(),
                "sd": s.std(),
                "q25": s.quantile(0.25),
                "q75": s.quantile(0.75),
                "median_n_ratings": g.n_ratings.median(),
                "min_group_30": g.book_id.nunique() >= MIN_GROUP_SIZE,
            }
        )
    return pd.DataFrame(rows)


def corr_table(frame, label):
    """Pearson và Spearman theo từng cặp có dữ liệu; log dùng ln(1+x)."""
    rows = []
    for col in ["pages", "n_ratings", "n_reviews", "publication_year"]:
        x = frame[col]
        y = frame.rating
        pair = pd.DataFrame({"x": x, "y": y}).dropna().astype(float)
        spearman = pair.x.rank(method="average").corr(pair.y.rank(method="average"))
        pearson = pair.x.corr(pair.y)
        logpearson = np.log1p(pair.x).corr(pair.y) if col != "publication_year" else np.nan
        rows.append(
            {
                "sample": label,
                "variable": col,
                "pairwise_n": len(pair),
                "spearman": spearman,
                "pearson_raw": pearson,
                "pearson_log1p": logpearson,
            }
        )
    return pd.DataFrame(rows)


def records(frame):
    """Đưa bảng số về JSON; giá trị thiếu trở thành null."""
    return json.loads(frame.to_json(orient="records", force_ascii=False))


def top(frame, col="mean", n=8):
    """Chọn nhóm đủ cỡ mẫu theo quy ước đã công bố."""
    return records(
        frame.loc[frame.min_group_30].sort_values([col, "n"], ascending=[False, False]).head(n)
    )


def run_eda(data_root: Path, output_root: Path) -> dict:
    """Đọc dữ liệu sạch đã xuất và ghi kết quả EDA vào thư mục đích."""
    clean, bridge = load_cleaned(data_root)
    snapshot = load_snapshot()
    raw = clean[snapshot["columns"]]
    change_log, summary, dictionary = cleaning_diagnostics(raw, clean)
    validation_file = data_root / "work/validation_results.json"
    checks = json.loads(validation_file.read_text(encoding="utf-8")) if validation_file.is_file() else {}
    N = len(clean)
    tables = output_root / "eda_tables"
    work = output_root / "work"
    tables.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)

    def save(df, name, index=False):
        df.to_csv(tables / (name + ".csv"), index=index, encoding="utf-8-sig", float_format="%.8f")

    eligible = clean.loc[clean.rating_eligible].copy()
    primary = clean.loc[clean.primary_sample].copy()
    save(
        describe(eligible, ["rating", "pages", "n_ratings", "n_reviews", "publication_year"]),
        "descriptive_eligible",
    )
    save(
        describe(primary, ["rating", "pages", "n_ratings", "n_reviews", "publication_year"]),
        "descriptive_primary",
    )
    sensitivity = []
    correlations = []
    for threshold in SENSITIVITY_THRESHOLDS:
        s = eligible.loc[eligible.n_ratings.ge(threshold)]
        sensitivity.append(
            {
                "min_ratings": threshold,
                "n": len(s),
                "retained_pct_raw": len(s) / N * 100,
                "mean_rating": s.rating.mean(),
                "median_rating": s.rating.median(),
                "sd_rating": s.rating.std(),
                "q25": s.rating.quantile(0.25),
                "q75": s.rating.quantile(0.75),
            }
        )
        correlations.append(corr_table(s, f"min_ratings_{threshold}"))
    sensitivity = pd.DataFrame(sensitivity)
    correlations = pd.concat(correlations, ignore_index=True)
    save(sensitivity, "threshold_sensitivity")
    save(correlations, "correlations_by_threshold")
    groups = {}
    for col, name in [
        ("page_band", "pages"),
        ("language_group", "language"),
        ("publisher_clean", "publisher"),
        ("publication_decade", "decade"),
    ]:
        g = group_summary(primary, col)
        groups[name] = g
        save(g, "group_" + name + "_all")
        save(
            g.loc[g.min_group_30].sort_values(["mean", "n"], ascending=[False, False]),
            "group_" + name + "_n30",
        )
    joined = primary[
        [
            "book_id",
            "rating",
            "n_ratings",
            "n_reviews",
            "pages",
            "language_group",
            "publication_year",
            "publication_decade",
        ]
    ].merge(bridge, on="book_id", validate="one_to_many")
    genre_groups = group_summary(joined, "genre_label")
    save(genre_groups, "group_genre_all")
    genre_n30 = genre_groups.loc[genre_groups.min_group_30].sort_values(
        ["mean", "n"], ascending=[False, False]
    )
    save(genre_n30, "group_genre_n30")
    genre_top_n = genre_groups.sort_values("n", ascending=False).head(12)
    save(genre_top_n, "group_genre_top12_by_size")
    filtered = primary.loc[
        primary.pages.gt(0)
        & primary.publication_year.between(1990, 2010)
        & primary.language_group.eq("English")
    ]
    save(
        filtered[
            [
                "book_id",
                "title_clean",
                "rating",
                "pages",
                "n_ratings",
                "publication_year",
                "language_group",
            ]
        ],
        "filter_example_English_1990_2010_pages_positive",
    )
    mean_pivot = primary.pivot_table(
        index="publication_decade",
        columns="page_band",
        values="rating",
        aggfunc="mean",
        observed=True,
    )
    n_pivot = (
        primary.pivot_table(
            index="publication_decade",
            columns="page_band",
            values="book_id",
            aggfunc="nunique",
            observed=True,
        )
        .fillna(0)
        .astype(int)
    )
    save(mean_pivot, "pivot_rating_decade_by_pages", index=True)
    save(n_pivot, "pivot_n_decade_by_pages", index=True)
    save(
        mean_pivot.where(n_pivot.ge(MIN_GROUP_SIZE)), "pivot_rating_decade_by_pages_n30", index=True
    )
    approx = primary.sort_values(
        ["n_ratings", "book_id"],
        ascending=[False, True],
        key=lambda s: pd.to_numeric(s) if s.name == "book_id" else s,
    ).drop_duplicates("title_author_key")
    approx_corr = corr_table(approx, "approx_one_per_title_author")
    save(approx_corr, "correlations_edition_sensitivity")
    approx_joined = approx[["book_id", "rating", "n_ratings"]].merge(
        bridge, on="book_id", validate="one_to_many"
    )
    approx_genres = group_summary(approx_joined, "genre_label")
    save(approx_genres, "group_genre_edition_sensitivity")
    approx_publishers = group_summary(approx, "publisher_clean")
    save(approx_publishers, "group_publisher_edition_sensitivity")
    page_restricted = primary.loc[primary.pages.between(20, 2000)]
    page_corr = corr_table(page_restricted, "pages_20_2000_sensitivity")
    save(page_corr, "correlations_pages_sensitivity")
    stratified = []
    for genre in genre_top_n.genre_label.head(6):
        sub = joined.loc[joined.genre_label.eq(genre)]
        c = corr_table(sub, f"genre: {genre}")
        stratified.append(c)
    stratified.append(
        corr_table(primary.loc[primary.language_group.eq("English")], "language: English")
    )
    stratified = pd.concat(stratified, ignore_index=True)
    save(stratified, "correlations_stratified")
    flow = pd.DataFrame(
        [
            {"sample": "raw/master", "n": N, "note": "All original records retained"},
            {
                "sample": "rating 1-5",
                "n": int(clean.rating.between(1, 5).sum()),
                "note": "Includes positive ratings with zero rating count",
            },
            {
                "sample": "eligible rating and count>0",
                "n": len(eligible),
                "note": "Descriptive baseline with observed count support",
            },
            {
                "sample": "primary count>=100",
                "n": len(primary),
                "note": "Operational main comparison sample",
            },
            {
                "sample": "primary with positive pages",
                "n": int(primary.pages.notna().sum()),
                "note": "Pairwise length analysis",
            },
            {
                "sample": "primary with valid publication date",
                "n": int(primary.publication_date_iso.notna().sum()),
                "note": "Time cohorts",
            },
            {
                "sample": "primary with genres",
                "n": int((~primary.genres_missing).sum()),
                "note": "Genre comparisons",
            },
            {
                "sample": "primary with publisher",
                "n": int(primary.publisher_clean.notna().sum()),
                "note": "Publisher comparisons",
            },
            {
                "sample": "approx one per title+author",
                "n": len(approx),
                "note": "Sensitivity only; master unchanged",
            },
        ]
    )
    save(flow, "sample_flow")
    save(summary, "cleaning_summary")
    save(change_log, "cell_change_log")
    save(dictionary, "cleaned_data_dictionary")
    results = {
        "source_sha256": snapshot["sha256"],
        "rows_raw": N,
        "columns_master": len(clean.columns),
        "base_n": len(eligible),
        "primary_n": len(primary),
        "approx_n": len(approx),
        "filtered_example_n": len(filtered),
        "cleaning": records(summary),
        "sample_flow": records(flow),
        "threshold_sensitivity": records(sensitivity),
        "correlations": records(correlations),
        "descriptive_primary": records(
            describe(primary, ["rating", "pages", "n_ratings", "n_reviews", "publication_year"])
        ),
        "descriptive_eligible": records(
            describe(eligible, ["rating", "pages", "n_ratings", "n_reviews", "publication_year"])
        ),
        "page_groups": records(groups["pages"]),
        "language_groups": records(groups["language"]),
        "decade_groups": records(groups["decade"]),
        "publisher_top_mean_n30": top(groups["publisher"]),
        "publisher_top_size_n30": top(groups["publisher"], "n"),
        "genre_top_mean_n30": top(genre_groups),
        "genre_top_size": records(genre_top_n),
        "genre_groups_total": len(genre_groups),
        "genre_groups_n30": int(genre_groups.min_group_30.sum()),
        "publisher_groups_total": len(groups["publisher"]),
        "publisher_groups_n30": int(groups["publisher"].min_group_30.sum()),
        "approx_correlations": records(approx_corr),
        "approx_genre_top_mean_n30": top(approx_genres),
        "approx_publisher_top_mean_n30": top(approx_publishers),
        "page_restricted_correlations": records(page_corr),
        "stratified_correlations": records(stratified),
        "pivot_mean": records(mean_pivot.reset_index()),
        "pivot_n": records(n_pivot.reset_index()),
        "validation": checks,
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "analysis_config": {
            "primary_min_ratings": PRIMARY_MIN_RATINGS,
            "minimum_group_size": MIN_GROUP_SIZE,
            "sensitivity_thresholds": list(SENSITIVITY_THRESHOLDS),
            "page_bins": ["1-200", "201-400", "401-600", "601+"],
            "unit": "Goodreads record/edition; not verified unique work",
        },
    }
    (work / "eda_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
    )
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=HERE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)
    analysis = run_eda(args.data_root, args.output_root)
    print(json.dumps({"primary_n": analysis["primary_n"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
