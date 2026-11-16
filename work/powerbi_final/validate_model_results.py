from pathlib import Path
import json
import math

B = Path(__file__).resolve().parent
queries = json.loads((B/"model_test_queries.json").read_text(encoding="utf-8-sig"))
results = {q["name"]: q for q in json.loads((B/"model_query_results.json").read_text(encoding="utf-8-sig"))}
checks = 0
errors = []
maximum_error = 0

def check(actual, expected, label):
    global checks, maximum_error
    checks += 1
    if isinstance(expected, (float, int)) and not isinstance(expected, bool):
        if actual is None:
            errors.append({"check": label, "actual": actual, "expected": expected})
        else:
            error = abs(float(actual) - float(expected))
            maximum_error = max(maximum_error, error)
            if error > 1e-10:
                errors.append({"check": label, "actual": actual, "expected": expected})
    elif actual != expected:
        errors.append({"check": label, "actual": actual, "expected": expected})

for q in queries:
    result = results.get(q["name"])
    if result is None or result.get("error"):
        errors.append({"query": q["name"], "error": None if result is None else result["error"]})
        continue
    rows = result["rows"]
    if q["kind"] == "stats":
        check(len(rows), 1, q["name"]+":row_count")
        if rows:
            for k, value in q["expected"].items():
                check(rows[0].get("["+k+"]"), value, q["name"]+":"+k)
    elif q["kind"] == "ranking":
        ids = [str(r["[book_id]"]) for r in rows]
        check(ids, q["expected_ids"], q["name"]+":ordered_ids")
        check([r["[rank]"] for r in rows], list(range(1, len(rows)+1)), q["name"]+":ordinal_ranks")
    elif q["kind"] == "groups":
        keycol = next(k for k in rows[0] if k.endswith("[Khóa]")) if rows else None
        actual = {str(r[keycol]): r for r in rows}
        check(sorted(actual), sorted(q["expected"]), q["name"]+":exact_keys")
        for key, expect in q["expected"].items():
            if key in actual:
                for metric in ["n", "mean", "median"]:
                    check(actual[key].get("["+metric+"]"), expect[metric], q["name"]+":"+key+":"+metric)
    elif q["kind"] == "bins":
        group = {}
        for row in rows:
            key = str(row["Thể loại[Khóa]"])
            group.setdefault(key, {"n": 0, "sum_share": 0.0})
            group[key]["n"] += row["[n]"]
            group[key]["sum_share"] += row["[share]"]
        references = next(qx["expected"] for qx in queries if qx["name"] == "groups_genre_primary_stats_by_key")
        for key, rec in group.items():
            check(rec["sum_share"], 1.0, "genre_bin_sum:"+key)
            check(rec["n"], references[key]["n"], "genre_bin_n:"+key)
    elif q["kind"] == "source":
        for key, value in {"master_n": 11127, "unique_ids": 11127, "bridge_n": 94794,
                           "genre_n": 890, "publisher_n": 2283}.items():
            check(rows[0].get("["+key+"]"), value, "source:"+key)
    elif q["kind"] == "histogram":
        manifest = json.loads((B/"../charts_stage6/chart_manifest.json").read_text(encoding="utf-8"))
        chart = manifest["charts"][0]
        expected = dict(zip([round(x, 1) for x in chart["histogram_left_edges"]], chart["histogram_counts"]))
        actual = {round(float(r["Sách[Khoảng điểm đánh giá]"]), 1): r["[n]"] for r in rows}
        for edge, n in expected.items():
            check(actual.get(edge, 0), n, "decimal_histogram:"+str(edge))

out = {"query_count": len(queries), "meaningful_checks": checks, "failed_checks": len(errors),
       "max_absolute_numeric_error": maximum_error, "errors": errors}
(B/"model_validation_summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({**out, "errors": errors[:8]}, ensure_ascii=True))
