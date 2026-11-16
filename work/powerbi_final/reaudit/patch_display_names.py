"""Apply only PBIR projection display-name overrides to a COPY of the report.

The supported displayName field is documented by RoleProjection in the local
visualConfiguration.json schema. No semantic field, DAX, filter, geometry,
sorting, source value, or queryRef is modified. Defaults to dry-run.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


RANKING_ALIASES = {
    "Hạng trong bộ lọc": "Hạng",
    "Tên sách tra cứu": "Tên sách và ID",
    "Điểm đánh giá": "Rating",
    "Số lượt đánh giá": "Lượt chấm",
    "Số lượt nhận xét": "Review",
    "Số trang": "Số trang",
    "Năm xuất bản": "Năm",
}
SCATTER_X_ALIASES = {
    "scatterPages": ("Trang điểm", "Số trang"),
    "scatterRatings": ("Log lượt chấm điểm", "ln(1 + lượt chấm)"),
    "scatterReviews": ("Log review điểm", "ln(1 + review)"),
}
TOOLTIP_ALIASES = {
    "Tên điểm": "Tên sách",
    "Trang điểm": "Số trang",
    "Lượt chấm điểm": "Lượt chấm",
    "Review điểm": "Review",
}


def property_name(projection: dict) -> str:
    field = projection["field"]
    for kind in ("Measure", "Column"):
        if kind in field:
            return field[kind]["Property"]
    raise AssertionError(f"Unexpected projection: {projection['queryRef']}")


def remove_display_names(value):
    if isinstance(value, dict):
        return {k: remove_display_names(v) for k, v in value.items() if k != "displayName"}
    if isinstance(value, list):
        return [remove_display_names(v) for v in value]
    return value


def patch(report_root: Path, apply: bool = False) -> list[dict]:
    root = report_root.resolve()
    forbidden = Path(__file__).resolve().parents[1] / "Goodreads_Ready.Report"
    if root == forbidden:
        raise ValueError("Copy the original report before applying this patch.")
    assert root.is_dir(), root
    manifest = []
    for name in ["ranking", *SCATTER_X_ALIASES]:
        matches = list(root.glob(f"definition/pages/*/visuals/{name}/visual.json"))
        assert len(matches) == 1, (name, len(matches))
        path = matches[0]
        before = json.loads(path.read_text(encoding="utf-8-sig"))
        after = copy.deepcopy(before)
        roles = after["visual"]["query"]["queryState"]
        changes = []

        def alias(projection, label):
            previous = projection.get("displayName")
            projection["displayName"] = label
            changes.append({"queryRef": projection["queryRef"], "before": previous, "after": label})

        if name == "ranking":
            projections = roles["Values"]["projections"]
            assert {property_name(p) for p in projections} == set(RANKING_ALIASES)
            for projection in projections:
                alias(projection, RANKING_ALIASES[property_name(projection)])
        else:
            x = roles["X"]["projections"]
            y = roles["Y"]["projections"]
            assert len(x) == len(y) == 1
            expected_x, label_x = SCATTER_X_ALIASES[name]
            assert property_name(x[0]) == expected_x, (name, property_name(x[0]))
            assert property_name(y[0]) == "Rating điểm"
            alias(x[0], label_x)
            alias(y[0], "Rating")
            for projection in roles.get("Tooltips", {}).get("projections", []):
                prop = property_name(projection)
                if prop in TOOLTIP_ALIASES:
                    alias(projection, TOOLTIP_ALIASES[prop])

        assert remove_display_names(before) == remove_display_names(after), path
        if apply:
            path.write_text(json.dumps(after, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest.append({"visual": name, "relative_path": path.relative_to(root).as_posix(), "changes": changes})
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    changes = patch(args.report_root, args.apply)
    result = {"applied": args.apply, "visuals": len(changes), "projection_aliases": sum(len(x["changes"]) for x in changes), "changes": changes}
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True))


if __name__ == "__main__":
    main()
