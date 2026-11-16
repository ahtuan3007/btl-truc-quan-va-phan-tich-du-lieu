from pathlib import Path
from datetime import datetime
import json, unicodedata, hashlib
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
e=ROOT/'work/powerbi_final'
raw=pd.read_csv(ROOT/'data/raw/Goodreads_books_with_genres.csv',dtype=str,keep_default_na=False)
saved=pd.read_csv(ROOT/'data/processed/books_cleaned_master.csv',dtype=str,keep_default_na=False)
bridge=pd.read_csv(ROOT/'data/processed/book_genres_bridge.csv',dtype=str,keep_default_na=False)
gmap=pd.read_csv(e/'genre_key_map.csv',keep_default_na=False)
pmap=pd.read_csv(e/'publisher_key_map.csv',keep_default_na=False)
results={r['name']:r['rows'] for r in json.loads((e/'model_query_results.json').read_text(encoding='utf-8-sig'))}
fixtures=json.loads((e/'expected_filter_cases.json').read_text(encoding='utf-8-sig'))
checks={}; errors=[]
def same(a,b,label,tol=1e-10):
    ok=(a==b) if not (isinstance(a,(float,np.floating)) or isinstance(b,(float,np.floating))) else (pd.isna(a) and pd.isna(b) or abs(a-b)<=tol)
    if not ok: errors.append({'name':label,'actual':str(a),'expected':str(b)})
def norm(s): return ' '.join(unicodedata.normalize('NFKC',s).split())
def year(s):
    try: return datetime.strptime(s,'%m/%d/%Y').year
    except ValueError:return np.nan
data=pd.DataFrame({'book_id':raw['Book Id'],'rating':raw.average_rating.astype(float),
    'n_ratings':raw.ratings_count.astype(int),'n_reviews':raw.text_reviews_count.astype(int),
    'pages':raw.num_pages.astype(float).replace(0,np.nan),'publication_year':raw.publication_date.map(year),
    'publisher_clean':raw.publisher.map(norm).map(lambda s:'' if s.casefold() in ('not avail','not available','') else s),
    'language_group':raw.language_code.map(norm).replace({'eng':'English','en-US':'English','en-GB':'English','en-CA':'English'})})
data['publication_decade']=data.publication_year.floordiv(10)*10
data['page_band']=pd.cut(data.pages,[0,200,400,600,np.inf],labels=['1-200','201-400','401-600','601+']).astype(str).replace('nan','')
primary=data.loc[data.rating.between(1,5)&data.n_ratings.ge(100)].copy()
same(len(primary),8402,'independent primary n')
same(saved[raw.columns].equals(raw),True,'source13columns unchanged')
same(set(primary.book_id),set(saved.loc[saved.primary_sample.eq('True'),'book_id']),'primary ids')
derived_bridge=pd.DataFrame([(bid,norm(g)) for bid,gs in zip(raw['Book Id'],raw.genres) for g in gs.split(';') if norm(g)],columns=['book_id','genre_label'])
same(derived_bridge.equals(bridge),True,'bridge from source semicolon labels')
same(bridge.duplicated().sum(),0,'bridge duplicates')
joined=bridge.merge(primary,on='book_id',validate='many_to_one')
primary['bin']=pd.cut(primary.rating,[1,3.5,4,4.5,5.00001],right=False,labels=['[1;3.5)','[3.5;4)','[4;4.5)','[4.5;5]'])
joined=joined.merge(primary[['book_id','bin']],on='book_id',validate='many_to_one')
primary_stats={'n':len(primary),'mean':primary.rating.mean(),'median':primary.rating.median(),'sd':primary.rating.std(),
    'q25':primary.rating.quantile(.25),'q75':primary.rating.quantile(.75)}
for key in ('n','mean','median','sd'):same(results['stats_all'][0]['['+key+']'],primary_stats[key],'default '+key)
for var in ['pages','n_ratings','n_reviews','publication_year']:
    for thresh in [1,100,500,1000]:
        pair=data.loc[data.rating.between(1,5)&data.n_ratings.ge(thresh),[var,'rating']].dropna()
        x,y=pair[var].to_numpy(),pair.rating.to_numpy()
        sp=float(np.corrcoef(pd.Series(x).rank(),pd.Series(y).rank())[0,1]);pe=float(np.corrcoef(x,y)[0,1])
        table=pd.read_csv(ROOT/'eda_tables/correlations_by_threshold.csv')
        row=table.loc[table['sample'].eq('min_ratings_'+str(thresh))&table.variable.eq(var)].iloc[0]
        same(len(pair),row.pairwise_n,f'corr {var} {thresh} N');same(sp,row.spearman,f'corr {var} {thresh} sp',5.1e-9);same(pe,row.pearson_raw,f'corr {var} {thresh} pe',5.1e-9)
        if var!='publication_year': same(float(np.corrcoef(np.log1p(x),y)[0,1]),row.pearson_log1p,f'corr {var} {thresh} log',5.1e-9)
        if thresh==100: checks['correlation_'+var]={'n':len(pair),'spearman':sp,'pearson':pe}
group_sets={}
for typ,col,frame in [('genre','genre_label',joined),('publisher','publisher_clean',primary),('language','language_group',primary),('pages','page_band',primary),('decade','publication_decade',primary)]:
    work=frame.loc[frame[col].notna()&frame[col].ne('')]
    grouped=work.groupby(col).agg(n=('book_id','nunique'),mean=('rating','mean'),median=('rating','median'),sd=('rating','std'),q25=('rating',lambda x:x.quantile(.25)),q75=('rating',lambda x:x.quantile(.75)),median_n_ratings=('n_ratings','median'))
    group_sets[typ]=grouped
    tab=pd.read_csv(ROOT/f'eda_tables/group_{typ}_all.csv',keep_default_na=False)
    for _,row in tab.iterrows():
        label=row[col]
        if typ=='decade': label=int(label)
        for metric in ['n','mean','median','sd','q25','q75','median_n_ratings']:
            value=float(row[metric]) if row[metric]!='' else np.nan
            same(grouped.loc[label,metric],value,f'EDA {typ} {label} {metric}',5.1e-9)
    same(len(tab),len(grouped),f'EDA group count {typ}')
    if typ in ['genre','publisher']:
        mapping=gmap if typ=='genre' else pmap
        keyname=typ+'_key';sourcecol='genre_label' if typ=='genre' else 'publisher_clean'
        for r in results['groups_'+typ+'_primary_stats_by_key']:
            key=r['Thể loại[Khóa]' if typ=='genre' else 'Nhà xuất bản[Khóa]']
            label=mapping.loc[mapping[keyname].eq(key),sourcecol].iloc[0]
            values=primary.loc[primary.publisher_clean.eq(''),'rating'] if typ=='publisher' and key==0 else work.loc[work[col].eq(label),'rating']
            for metric,value in [('n',len(values)),('mean',values.mean()),('median',values.median())]: same(r['['+metric+']'],value,f'model group {typ} {key} {metric}')
        top=grouped.loc[grouped.n.ge(30)].reset_index().sort_values(['n',col],ascending=[False,True]).head(12)
        ids=mapping.sort_values(sourcecol)[keyname].tolist()
        same(ids,sorted(ids),f'{typ} numeric keys preserve exact source text ordering')
        checks['top12_'+typ]=top[[col,'n','mean']].to_dict('records')

bin_counts=joined.groupby(['genre_label','bin'],observed=True).book_id.nunique()
keydict=dict(zip(gmap.genre_key,gmap.genre_label))
seen=set()
for r in results['genre_rating_bins']:
    label=keydict[r['Thể loại[Khóa]']];bin=r['Sách[Khoảng Rating 4 mức]']
    n=int(bin_counts.loc[(label,bin)])
    same(r['[n]'],n,f'exact genre bin count {label} {bin}')
    same(r['[share]'],n/group_sets['genre'].loc[label,'n'],f'exact genre bin share {label} {bin}')
    seen.add((label,bin))
same(seen,set(bin_counts.index), 'model bin row set, no missing/extra bins')
checks['all_1888_genre_bin_counts_and_shares_checked']=len(seen)

def filter_case(filters):
    out=primary.copy()
    for col in ['language_group','page_band','publication_decade','publisher_clean']:
        if col in filters:
            vals=filters[col]; hasnone=None in vals
            mask=out[col].isin([v for v in vals if v is not None])
            if hasnone: mask|=out[col].isna()|out[col].eq('')
            out=out.loc[mask]
    if 'genres' in filters:
        out=out.loc[out.book_id.isin(bridge.loc[bridge.genre_label.isin(filters['genres']),'book_id'])]
    if 'book_ids' in filters:out=out.loc[out.book_id.isin(filters['book_ids'])]
    if 'n_ratings_min' in filters:out=out.loc[out.n_ratings.ge(filters['n_ratings_min'])]
    if 'n_ratings_max' in filters:out=out.loc[out.n_ratings.le(filters['n_ratings_max'])]
    out=out.assign(numeric_id=out.book_id.astype(int))
    return out.sort_values(['rating','n_ratings','numeric_id'],ascending=[False,False,True])
for case in fixtures['cases']:
    out=filter_case(case['filters']);model=results['stats_'+case['id']][0]
    for metric,value in [('n',len(out)),('mean',out.rating.mean() if len(out) else None),('median',out.rating.median() if len(out) else None)]:same(model['['+metric+']'],value,'independent case '+case['id']+' '+metric)
    rankname='rank_'+case['id']+'_10'
    if rankname in results:
        same([str(r['[book_id]']) for r in results[rankname]],out.head(10).book_id.tolist(),'independent rank '+case['id'])
checks['56_filters_independently_recomputed']=len(fixtures['cases'])

# Explain the original 9,173 counter without using it as truth for this audit.
queries=json.loads((e/'model_test_queries.json').read_text(encoding='utf-8-sig'))
breakdown={}
for q in queries:
    kind=q['kind'];rows=results[q['name']]
    if kind=='stats':n=1+len(q['expected'])
    elif kind=='ranking':n=2
    elif kind=='groups':n=1+3*len(q['expected'])
    elif kind=='bins':n=2*len({r['Thể loại[Khóa]'] for r in rows})
    elif kind=='source':n=5
    elif kind=='histogram':n=40
    breakdown[kind]=breakdown.get(kind,0)+n
checks['original_9173_counter_breakdown']=breakdown
checks['original_9173_limitations']=[
    'These are scalar/list comparison assertions, not 9,173 independent experiments or all UI states.',
    'Original genre-bin validator checks per-genre total and summed share only, not each of 1,888 count/share cells. This audit independently checked every returned bin count/share and row set.',
    'Does not prove teacher requirements, narrative correctness, uncertainty, causal interpretation or visual design.',
    'Top12 selection measures under ties and cross-filter contexts are not exercised by original 81 queries; key ordering is consistent but live selection needs separate query/UI check.',
    'Expected fixtures and old validator were authored together; independent recomputation is more meaningful than repeatedly rerunning the same validator.'
]
checks['summary']=primary_stats
checks['errors']=errors
checks['error_count']=len(errors)
(OUT/'independent_numeric_audit.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2,default=lambda v:int(v) if isinstance(v,np.integer) else float(v)),encoding='utf-8')
print(json.dumps({'errors':len(errors),'error_examples':errors[:8],'primary':primary_stats,'bins_checked':len(seen),'old_counter':breakdown},ensure_ascii=True))
