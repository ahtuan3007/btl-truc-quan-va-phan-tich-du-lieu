"""Kiểm tra các rủi ro có thể làm thay đổi ý nghĩa dữ liệu hoặc ghi nhầm output."""

from pathlib import Path
import contextlib
import importlib
import io
import tempfile
import unittest

import pandas as pd

import run_phase_4_5 as pipeline


def sample_raw():
    row = {
        "Book Id": "001",
        "Title": "  Book  A ",
        "Author": "Writer  / Editor",
        "average_rating": "4.50",
        "isbn": "043938950x",
        "isbn13": "0073999768442",
        "language_code": "en-US",
        "num_pages": "0",
        "ratings_count": "0",
        "text_reviews_count": "1",
        "publication_date": "11/31/2000",
        "publisher": "Not Avail",
        "genres": "Fantasy,Magic;Fiction",
    }
    return pd.DataFrame([row], index=[17])


class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.raw = sample_raw()
        self.clean, self.bridge, self.dimension, _, _ = pipeline.clean_books(self.raw)

    def test_original_values_and_record_index_are_preserved(self):
        pd.testing.assert_frame_equal(self.clean[self.raw.columns], self.raw)
        self.assertEqual(self.clean.loc[17, "book_id"], "001")

    def test_invalid_calendar_date_is_not_guessed(self):
        self.assertTrue(pd.isna(self.clean.loc[17, "publication_date_iso"]))
        self.assertTrue(self.clean.loc[17, "date_invalid"])
        self.assertTrue(pd.isna(self.clean.loc[17, "pages"]))

    def test_positive_rating_with_zero_count_is_retained_and_flagged(self):
        self.assertEqual(self.clean.loc[17, "rating"], 4.5)
        self.assertEqual(self.clean.loc[17, "n_reviews"], 1)
        self.assertTrue(self.clean.loc[17, "positive_rating_zero_count"])
        self.assertFalse(self.clean.loc[17, "rating_eligible"])

    def test_hierarchical_comma_is_not_split_into_two_genres(self):
        self.assertEqual(self.bridge.genre_label.tolist(), ["Fantasy,Magic", "Fiction"])
        self.assertEqual(len(self.dimension), 2)

    def test_isbn_x_and_non_isbn_ean_are_distinguished(self):
        self.assertTrue(pipeline.isbn10("043938950x"))
        self.assertTrue(pipeline.isbn10("043938950X"))
        self.assertFalse(pipeline.isbn13("0073999768442"))
        self.assertEqual(self.clean.loc[17, "isbn13"], "0073999768442")

    def test_valid_date_remains_aligned_with_non_default_dataframe_index(self):
        raw = self.raw.copy()
        raw.loc[17, "publication_date"] = "2/29/2000"
        clean, *_ = pipeline.clean_books(raw)
        self.assertEqual(clean.loc[17, "publication_date_iso"], "2000-02-29")


class ExecutionTests(unittest.TestCase):
    def test_reload_does_not_run_pipeline_or_print_results(self):
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            importlib.reload(pipeline)
        self.assertEqual(captured.getvalue(), "")

    def test_wrong_source_is_rejected_before_creating_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wrong = root / "wrong.csv"
            wrong.write_text("book_id,rating\n1,5\n", encoding="utf-8")
            out = root / "outputs"
            with self.assertRaisesRegex(ValueError, "snapshot"):
                pipeline.run_pipeline(wrong, out)
            self.assertFalse(out.exists())


class SnapshotIntegrationTests(unittest.TestCase):
    def test_full_pipeline_matches_the_reviewed_report(self):
        source = pipeline.HERE / "data/raw/Goodreads_books_with_genres.csv"
        with tempfile.TemporaryDirectory() as tmp:
            result = pipeline.run_pipeline(source, Path(tmp))
            self.assertTrue(all(result["validation"].values()))
            self.assertEqual(result["primary_n"], 8402)
            self.assertEqual(result["approx_n"], 8189)
            pages = next(
                row
                for row in result["correlations"]
                if row["sample"] == "min_ratings_100" and row["variable"] == "pages"
            )
            self.assertEqual(pages["pairwise_n"], 8385)
            self.assertAlmostEqual(pages["spearman"], 0.1255696453, places=9)


if __name__ == "__main__":
    unittest.main()
