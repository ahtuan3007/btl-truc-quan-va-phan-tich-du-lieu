"""Làm sạch bộ dữ liệu Goodreads."""

import argparse
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PRIMARY_MIN_RATINGS = 100
ENGLISH_CODES = {"eng", "en-US", "en-GB", "en-CA"}


def text(s):
    """Chuẩn hóa Unicode NFKC và gom khoảng trắng."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(s))).strip()


def isbn10(s):
    if not re.fullmatch(r"\d{9}[\dXx]", s):
        return False
    return sum((10 if c in "Xx" else int(c)) * (10 - i) for i, c in enumerate(s)) % 11 == 0


def isbn13(s):
    return bool(re.fullmatch(r"97[89]\d{10}", s)) and (
        sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s)) % 10 == 0
    )


def clean_books(raw):
    clean = raw.copy()
    clean["book_id"] = raw["Book Id"]
    clean["title_clean"] = raw["Title"].map(text)
    clean["author_clean"] = raw["Author"].map(text)

    # Các cột số
    clean["rating"] = pd.to_numeric(raw["average_rating"])
    clean["n_ratings"] = pd.to_numeric(raw["ratings_count"]).astype("Int64")
    clean["n_reviews"] = pd.to_numeric(raw["text_reviews_count"]).astype("Int64")
    pages = pd.to_numeric(raw["num_pages"]).astype("Int64")
    clean["pages_zero"] = pages.eq(0)
    clean["pages"] = pages.mask(pages.eq(0))

    # Ngày xuất bản
    dates = pd.to_datetime(raw["publication_date"], format="%m/%d/%Y", errors="coerce")
    clean["publication_date_iso"] = dates.dt.strftime("%Y-%m-%d").astype("string")
    clean["date_invalid"] = dates.isna()
    clean["publication_year"] = dates.dt.year.astype("Int64")
    clean["publication_decade"] = (clean["publication_year"] // 10 * 10).astype("Int64")

    # Nhà xuất bản, ngôn ngữ
    publisher = raw["publisher"].map(text)
    clean["publisher_clean"] = publisher.mask(
        publisher.str.casefold().isin(["not avail", "not available", ""])
    )
    clean["publisher_missing"] = clean["publisher_clean"].isna()
    lang = raw["language_code"].map(text)
    clean["language_group"] = lang.mask(lang.isin(ENGLISH_CODES), "English")

    # Thể loại
    genre_lists = raw["genres"].map(lambda s: [g for g in map(text, s.split(";")) if g])
    clean["genre_count"] = genre_lists.map(len).astype("Int64")
    clean["genres_missing"] = clean["genre_count"].eq(0)

    # ISBN
    clean["isbn10_valid"] = raw["isbn"].map(isbn10)
    clean["isbn13_valid"] = raw["isbn13"].map(isbn13)

    # Cờ chất lượng
    clean["zero_rating_count"] = clean["n_ratings"].eq(0)
    clean["positive_rating_zero_count"] = clean["zero_rating_count"] & clean["rating"].gt(0)
    clean["review_gt_rating_count"] = clean["n_reviews"].gt(clean["n_ratings"])
    clean["rating_eligible"] = clean["rating"].between(1, 5) & clean["n_ratings"].gt(0)
    clean["primary_sample"] = clean["rating_eligible"] & clean["n_ratings"].ge(PRIMARY_MIN_RATINGS)
    clean["title_author_key"] = (
        clean["title_clean"].str.casefold() + " || " + clean["author_clean"].str.casefold()
    )
    clean["needs_edition_review"] = clean["title_author_key"].duplicated(keep=False)
    clean["pages_gt2000"] = clean["pages"].gt(2000).fillna(False)
    clean["pages_under20"] = clean["pages"].between(1, 19).fillna(False)

    # Biến log và nhóm số trang
    for src, dst in [("n_ratings", "log1p_n_ratings"), ("n_reviews", "log1p_n_reviews"), ("pages", "log1p_pages")]:
        clean[dst] = np.log1p(clean[src].astype(float))
    clean["page_band"] = pd.cut(
        clean["pages"],
        bins=[0, 200, 400, 600, np.inf],
        labels=["1-200", "201-400", "401-600", "601+"],
    ).astype("string")

    # Bảng bridge và dimension thể loại
    bridge = (
        pd.DataFrame({"book_id": clean["book_id"], "genre_label": genre_lists})
        .explode("genre_label")
        .dropna()
        .reset_index(drop=True)
    )
    genre_dimension = pd.DataFrame({"genre_label": sorted(bridge["genre_label"].unique())})
    return clean, bridge, genre_dimension


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=HERE / "data/raw/Goodreads_books_with_genres.csv")
    parser.add_argument("--output-root", type=Path, default=HERE)
    args = parser.parse_args()

    raw = pd.read_csv(args.input, dtype=str, keep_default_na=False)
    clean, bridge, genre_dimension = clean_books(raw)

    out = args.output_root / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    clean.to_csv(out / "books_cleaned_master.csv", index=False, encoding="utf-8-sig", float_format="%.10f")
    bridge.to_csv(out / "book_genres_bridge.csv", index=False, encoding="utf-8-sig")
    genre_dimension.to_csv(out / "genres_dimension.csv", index=False, encoding="utf-8-sig")
    print(f"Xong: {len(clean)} sách, {len(bridge)} liên kết thể loại, {len(genre_dimension)} thể loại.")


if __name__ == "__main__":
    main()
