exec((__import__('pathlib').Path(__file__).parent/'audit_independent.py').read_text(encoding='utf-8').split('# Explain the original')[0])

def daxvalue(v):
    if v is None:return 'BLANK()'
    if isinstance(v,str):return '"'+v.replace('"','""')+'"'
    return str(v)
def filterargs(f):
    args=["TREATAS({TRUE()}, 'Sách'[Mẫu phân tích])"]
    cols={'language_group':"'Sách'[Mã ngôn ngữ]",'page_band':"'Sách'[Nhóm số trang gốc]",'publication_decade':"'Sách'[Thập niên]"}
    # Use model test conventions, checked against the shipped query strings.
    for col,field in cols.items():
        if col in f:args.append('TREATAS({'+','.join(daxvalue(v) for v in f[col])+'}, '+field+')')
    if 'genres' in f:
        ks=gmap.loc[gmap.genre_label.isin(f['genres']),'genre_key'].tolist()
        args.append("TREATAS({"+','.join(map(str,ks))+"}, 'Thể loại'[Khóa])")
    if 'publisher_clean' in f:
        ks=pmap.loc[pmap.publisher_clean.isin([v or '' for v in f['publisher_clean']]),'publisher_key'].tolist()
        args.append("TREATAS({"+','.join(map(str,ks))+"}, 'Nhà xuất bản'[Khóa])")
    if 'n_ratings_min' in f:args.append("FILTER(ALL('Sách'[Số lượt đánh giá]),'Sách'[Số lượt đánh giá]>="+str(f['n_ratings_min'])+')')
    if 'n_ratings_max' in f:args.append("FILTER(ALL('Sách'[Số lượt đánh giá]),'Sách'[Số lượt đánh giá]<="+str(f['n_ratings_max'])+')')
    return args

# Get exact model field names from the shipped query set, not guessing translated labels.
original=json.loads((e/'model_test_queries.json').read_text(encoding='utf-8-sig'))
queries=[]
selected=[c for c in fixtures['cases'] if c['id'] in ['all','language_English','pages_1-200','pages_201-400','pages_601+','count_min_500','count_min_1000','genre_union','decade_1990','decade_2000']]
for c in selected:
    f=c['filters'];sub=filter_case(f)
    for typ,dim,keycol,sourcecol in [('genre','Thể loại','genre_key','genre_label'),('publisher','Nhà xuất bản','publisher_key','publisher_clean')]:
        frame=bridge.loc[bridge.book_id.isin(sub.book_id)] if typ=='genre' else sub
        if typ=='genre' and 'genres' in f:frame=frame.loc[frame.genre_label.isin(f['genres'])]
        counts=frame.groupby(sourcecol).book_id.nunique().rename('n').reset_index()
        counts=counts.loc[counts.n.ge(30)].sort_values(['n',sourcecol],ascending=[False,True]).head(12)
        mp=gmap if typ=='genre' else pmap
        expected=sorted(mp.loc[mp[sourcecol].isin(counts[sourcecol]),keycol].tolist())
        measure='Thuộc Top thể loại' if typ=='genre' else 'Thuộc Top nhà xuất bản'
        query="EVALUATE FILTER(SUMMARIZECOLUMNS('"+dim+"'[Khóa], "+', '.join(filterargs(f))+', "keep", ['+measure+']), [keep]=1)'
        queries.append({'name':c['id']+'_'+typ+'_top12','query':query,'expected_keys':expected,'keycol':dim+'[Khóa]'})
    grouped=bridge.loc[bridge.book_id.isin(sub.book_id)]
    if 'genres' in f:grouped=grouped.loc[grouped.genre_label.isin(f['genres'])]
    top=grouped.groupby('genre_label').book_id.nunique().rename('n').reset_index()
    top=top.loc[top.n.ge(30)].sort_values(['n','genre_label'],ascending=[False,True]).head(12)
    eligible=joined.loc[joined.book_id.isin(sub.book_id)&joined.genre_label.isin(top.genre_label)].copy()
    binrows=eligible.groupby(['genre_label','bin'],observed=True).book_id.nunique()
    expected={(int(gmap.loc[gmap.genre_label.eq(label),'genre_key'].iloc[0]),str(bin)):int(n) for (label,bin),n in binrows.items()}
    query="EVALUATE SUMMARIZECOLUMNS('Thể loại'[Khóa], 'Sách'[Khoảng Rating 4 mức], "+', '.join(filterargs(f))+', "value", [Số bản ghi Top thể loại])'
    queries.append({'name':c['id']+'_stack_top12_bins','query':query,'expected_cells':[[k[0],k[1],v] for k,v in expected.items()]})
    if c['id'] in ['all','genre_union','count_min_500']:
        for n in [50,100]:
            q="EVALUATE VAR R=SUMMARIZECOLUMNS('Sách'[Mã sách], 'Sách'[Tên sách tra cứu], "+', '.join(filterargs(f))+", TREATAS({"+str(n)+"},'Top N'[Giá trị]), \"rank\",[Hạng trong bộ lọc],\"keep\",[Trong Top N]) RETURN SELECTCOLUMNS(FILTER(R,[keep]=1),\"id\",'Sách'[Mã sách],\"rank\",[rank]) ORDER BY [rank]"
            queries.append({'name':c['id']+'_rank_'+str(n),'query':q,'expected_ids':sub.head(n).book_id.tolist()})
(OUT/'extra_queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2),encoding='utf-8-sig')
print('generated',len(queries))
