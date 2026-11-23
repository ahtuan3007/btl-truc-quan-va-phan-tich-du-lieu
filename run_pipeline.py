"""Chạy từng bước hoặc toàn bộ quy trình phân tích Goodreads."""

import argparse
from pathlib import Path

from clean_goodreads import HERE, SOURCE_PATH, run_cleaning
from eda_goodreads import run_eda
from viz_goodreads import run as run_viz


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", choices=("all", "clean", "eda", "visualize"), default="all",
                        help="Bước cần chạy (mặc định: cả ba bước theo thứ tự).")
    parser.add_argument("--input", type=Path, default=SOURCE_PATH, help="CSV nguồn.")
    parser.add_argument("--data-root", type=Path,
                        help="Thư mục chứa data/processed (chỉ dùng cho --step eda hoặc visualize).")
    parser.add_argument("--output-root", type=Path, default=HERE)
    args = parser.parse_args()
    if args.data_root and args.step in ("all", "clean"):
        parser.error("--data-root chỉ dùng cho --step eda hoặc --step visualize.")

    output_root = args.output_root.resolve()
    data_root = (args.data_root or output_root).resolve()

    if args.step in ("all", "clean"):
        books, links, genres = run_cleaning(args.input.resolve(), output_root)
        print(f"[clean] {books} sách, {links} liên kết thể loại, {genres} thể loại")
    if args.step in ("all", "eda"):
        primary_n = run_eda(data_root, output_root)
        print(f"[eda] primary_n = {primary_n}, bảng trong {output_root / 'eda_tables'}")
    if args.step in ("all", "visualize"):
        count = run_viz(data_root, output_root / "chart_outputs")
        print(f"[visualize] {count} biểu đồ trong {output_root / 'chart_outputs'}")


if __name__ == "__main__":
    main()
