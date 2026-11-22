"""Chạy từng bước hoặc toàn bộ quy trình phân tích Goodreads của Nhóm 5."""

import argparse
import json
from pathlib import Path

from clean_data import DEFAULT_OUTPUT_ROOT, SOURCE_PATH, run_cleaning
from eda import run_eda


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--step", choices=("all", "clean", "eda", "visualize"), default="all",
        help="Bước cần chạy. Mặc định chạy cả ba bước theo thứ tự.",
    )
    parser.add_argument("--input", type=Path, default=SOURCE_PATH, help="CSV nguồn đã đối chiếu.")
    parser.add_argument(
        "--data-root", type=Path,
        help="Thư mục chứa data/processed và các bảng EDA sẵn có cho bước eda hoặc visualize.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args(argv)
    if args.data_root is not None and args.step in ("all", "clean"):
        parser.error("--data-root dùng cho --step eda hoặc --step visualize.")

    output_root = args.output_root.resolve()
    input_path = args.input.resolve()
    data_root = (args.data_root or output_root).resolve()
    summary = {}
    if args.step in ("all", "clean"):
        checks = run_cleaning(input_path, output_root)
        summary["clean"] = {"validation_passed": all(checks.values())}
    if args.step in ("all", "eda"):
        analysis = run_eda(data_root, output_root)
        fields = ("rows_raw", "base_n", "primary_n", "approx_n")
        summary["eda"] = {field: analysis[field] for field in fields}
    if args.step in ("all", "visualize"):
        from visualize import run

        charts = run(
            data_root, output_root / "chart_outputs", output_root / "work/charts_stage6", input_path
        )
        summary["visualize"] = {
            "png_count": len(charts["charts"]),
            "validation_passed": all(charts["validation"].values()),
        }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
