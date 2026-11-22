"""BTL trực quan và phân tích dữ liệu — Goodreads. Chỉ làm sạch và EDA; không chạy khi import."""

from pathlib import Path
from datetime import datetime
import argparse
import hashlib
import json
import re
import unicodedata
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SNAPSHOT_PATH = HERE / "data/reference/source_snapshot.json"
PRIMARY_MIN_RATINGS = 100
MIN_GROUP_SIZE = 30
SENSITIVITY_THRESHOLDS = (1, 100, 500, 1000)


def text(s):
    """Chuẩn hóa Unicode NFKC và khoảng trắng; không sửa nội dung theo suy đoán."""
    return re.sub("\\s+", " ", unicodedata.normalize("NFKC", str(s))).strip()


def isbn10(s):
    """Kiểm tra ISBN10; chấp nhận x/X mà không sửa chuỗi nguồn."""
    if not re.fullmatch("\\d{9}[\\dXx]", s):
        return False
    return sum(((10 if c.upper() == "X" else int(c)) * (10 - i) for i, c in enumerate(s))) % 11 == 0


def isbn13(s):
    """ISBN13 cần đủ 13 chữ số, tiền tố 978/979 và checksum đúng."""
    return (
        bool(re.fullmatch("97[89]\\d{10}", s))
        and sum((int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s))) % 10 == 0
    )


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


def clean_books(raw):
    """Chuẩn hóa vào cột mới; giữ nguyên 13 cột nguồn và mọi bản ghi."""
    clean = raw.copy()
    clean["book_id"] = raw["Book Id"]
    clean["title_clean"] = raw.Title.map(text)
    clean["author_clean"] = raw.Author.map(text)
    clean["rating"] = pd.to_numeric(raw.average_rating, errors="raise")
    clean["n_ratings"] = pd.to_numeric(raw.ratings_count, errors="raise").astype("Int64")
    clean["n_reviews"] = pd.to_numeric(raw.text_reviews_count, errors="raise").astype("Int64")
    pages = pd.to_numeric(raw.num_pages, errors="raise").astype("Int64")
    clean["pages_zero"] = pages.eq(0)
    clean["pages"] = pages.mask(pages.eq(0))
    date_text = []
    for value in raw.publication_date:
        try:
            date_text.append(datetime.strptime(value, "%m/%d/%Y").date().isoformat())
        except ValueError:
            date_text.append(None)
    clean["publication_date_iso"] = pd.Series(date_text, index=raw.index, dtype="string")
    clean["date_invalid"] = clean.publication_date_iso.isna()
    clean["publication_year"] = clean.publication_date_iso.str.slice(0, 4).astype("Int64")
    clean["publication_decade"] = (clean.publication_year // 10 * 10).astype("Int64")
    publisher = raw.publisher.map(text)
    clean["publisher_clean"] = publisher.mask(
        publisher.str.casefold().isin(["not avail", "not available", ""])
    )
    clean["publisher_missing"] = clean.publisher_clean.isna()
    clean["language_group"] = raw.language_code.map(text).replace(
        {"eng": "English", "en-US": "English", "en-GB": "English", "en-CA": "English"}
    )
    genre_lists = raw.genres.map(lambda s: [text(g) for g in s.split(";") if text(g)])
    clean["genre_count"] = genre_lists.map(len).astype("Int64")
    clean["genres_missing"] = clean.genre_count.eq(0)
    clean["isbn10_valid"] = raw.isbn.map(isbn10)
    clean["isbn13_valid"] = raw.isbn13.map(isbn13)
    clean["zero_rating_count"] = clean.n_ratings.eq(0)
    clean["positive_rating_zero_count"] = clean.zero_rating_count & clean.rating.gt(0)
    clean["review_gt_rating_count"] = clean.n_reviews.gt(clean.n_ratings)
    clean["rating_eligible"] = clean.rating.between(1, 5) & clean.n_ratings.gt(0)
    clean["primary_sample"] = clean.rating_eligible & clean.n_ratings.ge(PRIMARY_MIN_RATINGS)
    clean["title_author_key"] = (
        clean.title_clean.str.casefold() + " || " + clean.author_clean.str.casefold()
    )
    clean["needs_edition_review"] = clean.title_author_key.duplicated(keep=False)
    clean["pages_gt2000"] = clean.pages.gt(2000).fillna(False)
    clean["pages_under20"] = clean.pages.between(1, 19).fillna(False)
    clean["log1p_n_ratings"] = np.log1p(clean.n_ratings.astype(float))
    clean["log1p_n_reviews"] = np.log1p(clean.n_reviews.astype(float))
    clean["log1p_pages"] = np.log1p(clean.pages.astype(float))
    clean["page_band"] = pd.cut(
        clean.pages,
        bins=[0, 200, 400, 600, np.inf],
        right=True,
        labels=["1-200", "201-400", "401-600", "601+"],
    ).astype("string")
    bridge = pd.DataFrame(
        [(bid, g) for bid, gs in zip(clean.book_id, genre_lists) for g in gs],
        columns=["book_id", "genre_label"],
    )
    genre_dimension = pd.DataFrame({"genre_label": sorted(bridge.genre_label.unique())})
    changes = []
    for src, dest, reason in [
        ("Title", "title_clean", "NFKC; trim; collapse whitespace"),
        ("Author", "author_clean", "NFKC; trim; collapse whitespace"),
        ("num_pages", "pages", "zero pages -> missing only in normalized field"),
        (
            "publication_date",
            "publication_date_iso",
            "M/D/YYYY -> ISO date; invalid calendar date -> missing",
        ),
        ("publisher", "publisher_clean", "normalize whitespace; Not Avail -> missing"),
        ("language_code", "language_group", "group modern English codes; preserve other codes"),
    ]:
        for i, (old, new) in enumerate(zip(raw[src], clean[dest])):
            new_text = "" if pd.isna(new) else str(new)
            if old != new_text:
                changes.append(
                    {
                        "book_id": clean.book_id.iloc[i],
                        "source_column": src,
                        "normalized_column": dest,
                        "old_value": old,
                        "new_value": new_text,
                        "reason": reason,
                    }
                )
    change_log = pd.DataFrame(changes)
    summary = []
    for src, dest in [
        ("Title", "title_clean"),
        ("Author", "author_clean"),
        ("num_pages", "pages"),
        ("publication_date", "publication_date_iso"),
        ("publisher", "publisher_clean"),
        ("language_code", "language_group"),
    ]:
        summary.append(
            {
                "source_column": src,
                "normalized_column": dest,
                "changed_values": int(change_log.normalized_column.eq(dest).sum()),
                "normalized_missing": int(clean[dest].isna().sum()),
            }
        )
    summary = pd.DataFrame(summary)
    return (clean, bridge, genre_dimension, change_log, summary)


def run_pipeline(input_path, output_root):
    """Đọc snapshot cố định, làm sạch, EDA, xuất CSV và kiểm tra bảo toàn."""
    input_path = Path(input_path).resolve()
    output_root = Path(output_root).resolve()
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    input_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()
    if input_hash != snapshot["sha256"]:
        raise ValueError(
            "File nguồn không khớp snapshot đã dùng cho báo cáo. Chưa ghi kết quả; hãy dùng đúng CSV trong data/raw."
        )
    raw = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    if raw.columns.tolist() != snapshot["columns"] or len(raw) != snapshot["rows"]:
        raise ValueError("Cấu trúc nguồn không khớp source_snapshot.json.")
    N = len(raw)
    if not raw["Book Id"].is_unique:
        raise ValueError("Book Id không duy nhất; dừng trước khi xuất kết quả.")
    ROOT = output_root
    PROCESSED = ROOT / "data/processed"
    TABLES = ROOT / "eda_tables"
    WORK = ROOT / "work"
    for folder in [PROCESSED, TABLES, WORK]:
        folder.mkdir(parents=True, exist_ok=True)
    clean, bridge, genre_dimension, change_log, summary = clean_books(raw)

    def save(df, name, index=False):
        df.to_csv(TABLES / (name + ".csv"), index=index, encoding="utf-8-sig", float_format="%.8f")

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
    clean.to_csv(
        PROCESSED / "books_cleaned_master.csv",
        index=False,
        encoding="utf-8-sig",
        float_format="%.10f",
    )
    bridge.to_csv(PROCESSED / "book_genres_bridge.csv", index=False, encoding="utf-8-sig")
    genre_dimension.to_csv(PROCESSED / "genres_dimension.csv", index=False, encoding="utf-8-sig")
    role_notes = {
        "book_id": "Unique record key; text",
        "rating": "Copied numeric target; unchanged value",
        "title_clean": "Title normalized with NFKC, trim and collapsed whitespace; source retained",
        "author_clean": "Contributor string normalized; no assumption of primary/co-author role",
        "pages": "Positive page count; source zero becomes missing",
        "pages_zero": "Source page count equals zero",
        "n_ratings": "Observed rating count; edition/work scope uncertain",
        "n_reviews": "Observed review count; zero retained",
        "title_author_key": "Approximate normalized title+contributor grouping; not work_id",
        "publication_date_iso": "Valid source calendar date as YYYY-MM-DD; not first publication date",
        "date_invalid": "Source calendar date does not exist or cannot be parsed",
        "publication_year": "Year from valid source publication date; missing when date is invalid",
        "publication_decade": "Floor publication_year to ten-year cohort",
        "publisher_clean": "NFKC/whitespace normalization; Not Avail becomes missing; no imprint consolidation",
        "publisher_missing": "Normalized publisher is missing",
        "language_group": "Only eng/en-US/en-GB/en-CA grouped as English",
        "genre_count": "Count of semicolon-separated nonempty raw genre labels",
        "genres_missing": "No nonempty semicolon-separated genre labels",
        "isbn10_valid": "Length and checksum validated; lowercase x accepted as X",
        "isbn13_valid": "13 digits AND prefix978/979 AND valid checksum",
        "zero_rating_count": "Source observed rating count equals zero",
        "positive_rating_zero_count": "Positive rating and observed rating count equals zero; preserve and flag",
        "review_gt_rating_count": "Observed review count exceeds rating count; semantic check flag, not proven error",
        "rating_eligible": "rating between1and5 AND n_ratings>0",
        "primary_sample": "rating_eligible AND n_ratings>=100",
        "needs_edition_review": "Normalized title+contributor key appears more than once; not confirmed duplicate work",
        "pages_gt2000": "Positive normalized pages over2000; retained, sensitivity flag only",
        "pages_under20": "Positive normalized pages1to19; retained, sensitivity flag only",
        "log1p_n_ratings": "Natural logarithm ln(1+n_ratings)",
        "log1p_n_reviews": "Natural logarithm ln(1+n_reviews), preserving zero review counts",
        "log1p_pages": "Natural logarithm ln(1+pages); missing when pages missing",
        "page_band": "Right-closed page intervals1-200,201-400,401-600,601+; missing when pages missing",
    }
    dictionary = pd.DataFrame(
        [
            {
                "column": c,
                "dtype_in_memory": str(clean[c].dtype),
                "original_column": c in raw.columns,
                "missing": int(clean[c].isna().sum()),
                "meaning": role_notes.get(
                    c,
                    (
                        "Original source value preserved"
                        if c in raw.columns
                        else "Derived field or quality flag; see code and report"
                    ),
                ),
            }
            for c in clean.columns
        ]
    )
    save(dictionary, "cleaned_data_dictionary")
    checks = {
        "raw_hash_unchanged": hashlib.sha256(input_path.read_bytes()).hexdigest() == input_hash,
        "raw_expected_hash": input_hash == snapshot["sha256"],
        "all_rows_retained": len(clean) == len(raw),
        "all_original_values_preserved": clean[raw.columns].equals(raw),
        "unique_book_ids": clean.book_id.is_unique,
        "row_order_preserved": clean.book_id.tolist() == raw["Book Id"].tolist(),
        "pages_76_missing": int(clean.pages.isna().sum())
        == snapshot["expected_counts"]["pages_missing"],
        "invalid_dates_2": int(clean.date_invalid.sum())
        == snapshot["expected_counts"]["invalid_dates"],
        "publisher_5_missing": int(clean.publisher_missing.sum())
        == snapshot["expected_counts"]["publisher_missing"],
        "english_10541": int(clean.language_group.eq("English").sum())
        == snapshot["expected_counts"]["english"],
        "zero_counts_81_preserved": int(clean.zero_rating_count.sum())
        == snapshot["expected_counts"]["zero_counts"],
        "positive_zero_count_55_preserved": int(clean.positive_rating_zero_count.sum())
        == snapshot["expected_counts"]["positive_zero_count"],
        "isbn10_invalid4": int((~clean.isbn10_valid).sum())
        == snapshot["expected_counts"]["isbn10_invalid"],
        "isbn13_invalid28": int((~clean.isbn13_valid).sum())
        == snapshot["expected_counts"]["isbn13_invalid"],
        "genre_bridge_94794": len(bridge) == snapshot["expected_counts"]["genre_links"],
        "unique_genre_pairs": not bridge.duplicated().any(),
        "bridge_keys_exist": bridge.book_id.isin(clean.book_id).all(),
        "genre_labels890": len(genre_dimension) == snapshot["expected_counts"]["genre_labels"],
        "eligible11046": len(eligible) == snapshot["expected_counts"]["eligible"],
        "primary8402": len(primary) == snapshot["expected_counts"]["primary"],
        "no_zero_pages_in_normalized": not clean.pages.eq(0).any(),
    }
    reloaded = pd.read_csv(PROCESSED / "books_cleaned_master.csv", dtype=str, keep_default_na=False)
    checks["csv_roundtrip_original_columns_preserved"] = reloaded[raw.columns].equals(raw)
    reloaded_bridge = pd.read_csv(
        PROCESSED / "book_genres_bridge.csv", dtype=str, keep_default_na=False
    )
    checks["csv_roundtrip_bridge"] = reloaded_bridge.equals(bridge)
    checks = {k: bool(v) for k, v in checks.items()}
    (WORK / "validation_results.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    if not all(checks.values()):
        raise AssertionError(checks)
    results = {
        "source_sha256": input_hash,
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
    (WORK / "eda_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
    )
    return results


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="BTL Goodreads: làm sạch và EDA theo snapshot cố định."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=HERE / "data/raw/Goodreads_books_with_genres.csv",
        help="Đường dẫn tới đúng CSV nguồn của báo cáo.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=HERE,
        help="Thư mục ghi CSV, bảng EDA và kết quả kiểm tra.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    result = run_pipeline(args.input, args.output_root)
    summary = {
        key: result[key]
        for key in ["rows_raw", "columns_master", "base_n", "primary_n", "approx_n"]
    }
    summary["validation_passed"] = all(result["validation"].values())
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
