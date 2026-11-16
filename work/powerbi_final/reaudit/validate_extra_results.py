from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
queries=json.loads((HERE/'extra_queries.json').read_text(encoding='utf-8-sig'))
results={r['name']:r for r in json.loads((HERE/'extra_results.json').read_text(encoding='utf-8-sig'))}
errors=[]
for q in queries:
    r=results.get(q['name'])
    if not r or r['error']:
        errors.append({'query':q['name'],'error':None if not r else r['error']});continue
    rows=r['rows']
    if 'expected_keys' in q:
        actual=sorted(int(row[q['keycol']]) for row in rows)
        expected=sorted(q['expected_keys'])
    elif 'expected_ids' in q:
        actual=[str(row['[id]']) for row in rows]
        expected=q['expected_ids']
    else:
        # COUNT=0 cells are explicit in the COALESCE DAX measure, whereas
        # pandas observed=True omits empty categories. Check this convention
        # without dropping any positive cell or permitting an extra genre.
        expected_groups={cell[0] for cell in q['expected_cells']}
        allowed_bins={'[1;3.5)','[3.5;4)','[4;4.5)','[4.5;5]'}
        for row in rows:
            assert row['[value]']>=0
            assert int(row['Thể loại[Khóa]']) in expected_groups
            assert row['Sách[Khoảng Rating 4 mức]'] in allowed_bins
        actual=sorted([int(row['Thể loại[Khóa]']),row['Sách[Khoảng Rating 4 mức]'],int(row['[value]'])] for row in rows if row['[value]']>0)
        expected=sorted(q['expected_cells'])
    if actual!=expected:
        errors.append({'query':q['name'],'expected':expected,'actual':actual})
out={'query_count':len(queries),'failed_queries':len(errors),'errors':errors,
     'coverage':'Top12 genre/publisher and genre composition in ten filter contexts; Top50/100 all, genre union and minimum500 ratings'}
(HERE/'extra_validation_summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({**out,'errors':errors[:3]},ensure_ascii=True))
assert not errors
