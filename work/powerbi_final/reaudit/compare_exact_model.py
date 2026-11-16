from pathlib import Path
import json
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
CODE=Path(__file__).resolve().parents[3]
results=json.loads((HERE/'model_query_results.json').read_text(encoding='utf-8-sig'))
assert all(r['error'] is None for r in results)
r={q['name']:q['rows'] for q in results}
model=pd.DataFrame(r['all_master_rows'])
model.columns=[c.strip('[]') for c in model.columns]
master=pd.read_csv(CODE/'data/processed/books_cleaned_master.csv',dtype=str,keep_default_na=False)
assert model.book_id.is_unique and set(model.book_id)==set(master.book_id)
model=model.set_index('book_id').sort_index()
master=master.set_index('book_id').sort_index()
numeric=['rating','n_ratings','n_reviews','pages','publication_year','publication_decade',
         'log1p_n_ratings','log1p_n_reviews','genre_count']
diffs=[]
for c in numeric:
    expected=pd.to_numeric(master[c],errors='coerce').to_numpy(dtype=float)
    actual=pd.to_numeric(model[c],errors='coerce').to_numpy(dtype=float)
    good=np.isclose(actual,expected,rtol=0,atol=1e-11,equal_nan=True)
    if not good.all():
        diffs.append({'column':c,'mismatch_rows':int((~good).sum()),'example_ids':master.index[~good].tolist()[:5]})
assert master.primary_sample.str.lower().eq('true').equals(model.primary_sample.astype(bool))
text_details={}
for c in ['title_clean','author_clean','publisher_clean','page_band','language_group']:
    expected=master[c].fillna('')
    actual=model[c].fillna('')
    mismatch=~actual.eq(expected)
    case_mismatch=~actual.str.casefold().eq(expected.str.casefold())
    text_details[c]={'exact_case_differences':int(mismatch.sum()),'differences_other_than_case':int(case_mismatch.sum())}
    if case_mismatch.any():
        diffs.append({'column':c,'mismatch_other_than_case':int(case_mismatch.sum())})

publisher=pd.read_csv(CODE/'work/powerbi_final/publisher_key_map.csv',dtype=str,keep_default_na=False)
publisher_map=publisher.set_index('publisher_clean').publisher_key.to_dict()
expected_pub=master.publisher_clean.map(publisher_map).astype(int)
assert np.array_equal(expected_pub,model.publisher_key.to_numpy(dtype=int))
expected_bridge=pd.read_csv(CODE/'work/powerbi_final/genre_bridge_keyed.csv',dtype=str,keep_default_na=False)
actual_bridge=pd.DataFrame(r['all_bridge_pairs']).rename(columns={'[book_id]':'book_id','[genre_key]':'genre_key'}).astype(str)
actual_pairs=set(map(tuple,actual_bridge[['book_id','genre_key']].itertuples(index=False,name=None)))
expected_pairs=set(map(tuple,expected_bridge[['book_id','genre_key']].itertuples(index=False,name=None)))
assert len(actual_bridge)==94794 and len(actual_pairs)==len(actual_bridge)
assert actual_pairs==expected_pairs
display_checks={}
for result_name,dim,keycol,textcol,mapfile in [
    ('genre_dictionary','Thể loại','genre_key','genre_display','genre_key_map.csv'),
    ('publisher_dictionary','Nhà xuất bản','publisher_key','publisher_display','publisher_key_map.csv')]:
    expected=pd.read_csv(CODE/'work/powerbi_final'/mapfile,dtype=str,keep_default_na=False).set_index(keycol)[textcol].to_dict()
    actual={str(row[f'{dim}[Khóa]']):row[f'{dim}[Nhãn]'] for row in r[result_name]}
    assert actual==expected, result_name
    display_checks[result_name]={'rows':len(actual),'exact_case_display_labels':True}
if 'book_search_labels' in r:
    expected=(master.title_clean+' [ID '+master.index+']').to_dict()
    actual={row['[book_id]']:row['[book_label]'] for row in r['book_search_labels']}
    assert actual==expected
    display_checks['book_search_labels']={'rows':len(actual),'exact_case_display_labels':True}
out={'master_rows':len(master),'numeric_columns_checked':numeric,'numeric_or_noncase_value_errors':diffs,
     'primary_flags_exact':True,'publisher_keys_exact':True,
     'bridge_pairs_exact':len(actual_pairs),'text_collation':text_details,'unique_display_labels':display_checks,
     'note':'Power BI string collation can retain a shared spelling for values differing only by case. The unique search labels and keyed dimensions must be inspected separately.'}
(HERE/'exact_readback_summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True,indent=2))
assert not diffs
