"""Làm sạch và kiểm tra bộ dữ liệu Goodreads dùng trong bài."""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
import argparse
import hashlib
import json
import re
import unicodedata

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE_FILE = "data/raw/Goodreads_books_with_genres.csv"
SOURCE_PATH = HERE / SOURCE_FILE
SNAPSHOT_PATH = HERE / "data/reference/source_snapshot.json"
DEFAULT_OUTPUT_ROOT = HERE / "ket_qua_chay_lai"
PRIMARY_MIN_RATINGS = 100

LOCKED_HASHES = {
    "data/raw/Goodreads_books_with_genres.csv": "721fc3bbe6367e91f2d3537d2cbe1c1ca4b585535d8ce63862c38a353d662b97",
    "data/processed/books_cleaned_master.csv": "7985d617d177b64d51396f027bc529edbe72ddbdc7b34e8f66196831ba14d929",
    "data/processed/book_genres_bridge.csv": "87a13c46b0d89473292f325287415d4aecc58e5a7c47c43456594b2d7dee97f7",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_snapshot() -> dict:
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


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
    return clean, bridge, genre_dimension


def cleaning_diagnostics(raw, clean):
    """Đối chiếu cột nguồn và cột chuẩn hóa để lập các bảng chất lượng."""
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
    return change_log, summary, dictionary


def load_cleaned(data_root: Path):
    """Đọc master và bridge, bảo toàn chuỗi nguồn, cờ và kiểu số thiếu."""
    master_file = "data/processed/books_cleaned_master.csv"
    bridge_file = "data/processed/book_genres_bridge.csv"
    for filename in (master_file, bridge_file):
        if digest(data_root / filename) != LOCKED_HASHES[filename]:
            raise ValueError(f"Dữ liệu sạch không khớp snapshot: {data_root / filename}")

    integers = ("n_ratings", "n_reviews", "pages", "publication_year", "publication_decade", "genre_count")
    floats = ("rating", "log1p_n_ratings", "log1p_n_reviews", "log1p_pages")
    flags = (
        "pages_zero", "genres_missing", "zero_rating_count", "positive_rating_zero_count",
        "review_gt_rating_count", "rating_eligible", "primary_sample", "pages_gt2000", "pages_under20",
    )
    boolean_flags = (
        "date_invalid", "publisher_missing", "isbn10_valid", "isbn13_valid", "needs_edition_review",
    )
    nullable_text = ("publication_date_iso", "page_band")
    dtypes = defaultdict(
        lambda: str,
        {
            **dict.fromkeys(integers, "Int64"),
            **dict.fromkeys(floats, float),
            **dict.fromkeys(flags, "boolean"),
            **dict.fromkeys(boolean_flags, bool),
            **dict.fromkeys(nullable_text, "string"),
        },
    )
    missing = dict.fromkeys((*integers, *floats, *nullable_text, "publisher_clean"), [""])
    clean = pd.read_csv(
        data_root / master_file, dtype=dtypes, keep_default_na=False, na_values=missing,
        float_precision="round_trip",
    )
    bridge = pd.read_csv(data_root / bridge_file, dtype=str, keep_default_na=False)
    return clean, bridge


def run_cleaning(input_path: Path, output_root: Path) -> dict:
    """Xác minh CSV gốc và xuất master, bridge, danh mục thể loại."""
    input_path = Path(input_path).resolve()
    output_root = Path(output_root).resolve()
    snapshot = load_snapshot()
    input_hash = digest(input_path)
    if input_hash != snapshot["sha256"]:
        raise ValueError(
            "File nguồn không khớp snapshot đã dùng cho báo cáo. Chưa ghi kết quả; hãy dùng đúng CSV trong data/raw."
        )
    raw = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    if raw.columns.tolist() != snapshot["columns"] or len(raw) != snapshot["rows"]:
        raise ValueError("Cấu trúc nguồn không khớp source_snapshot.json.")
    if not raw["Book Id"].is_unique:
        raise ValueError("Book Id không duy nhất; dừng trước khi xuất kết quả.")
    clean, bridge, genre_dimension = clean_books(raw)
    processed = output_root / "data/processed"
    work = output_root / "work"
    processed.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    clean.to_csv(
        processed / "books_cleaned_master.csv",
        index=False,
        encoding="utf-8-sig",
        float_format="%.10f",
    )
    bridge.to_csv(processed / "book_genres_bridge.csv", index=False, encoding="utf-8-sig")
    genre_dimension.to_csv(processed / "genres_dimension.csv", index=False, encoding="utf-8-sig")
    checks = {
        "raw_hash_unchanged": digest(input_path) == input_hash,
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
        "eligible11046": int(clean.rating_eligible.sum()) == snapshot["expected_counts"]["eligible"],
        "primary8402": int(clean.primary_sample.sum()) == snapshot["expected_counts"]["primary"],
        "no_zero_pages_in_normalized": not clean.pages.eq(0).any(),
    }
    reloaded = pd.read_csv(processed / "books_cleaned_master.csv", dtype=str, keep_default_na=False)
    checks["csv_roundtrip_original_columns_preserved"] = reloaded[raw.columns].equals(raw)
    reloaded_bridge = pd.read_csv(
        processed / "book_genres_bridge.csv", dtype=str, keep_default_na=False
    )
    checks["csv_roundtrip_bridge"] = reloaded_bridge.equals(bridge)
    checks = {k: bool(v) for k, v in checks.items()}
    (work / "validation_results.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    if not all(checks.values()):
        raise AssertionError(checks)
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SOURCE_PATH)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)
    checks = run_cleaning(args.input, args.output_root)
    print(json.dumps({"validation_passed": all(checks.values())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
