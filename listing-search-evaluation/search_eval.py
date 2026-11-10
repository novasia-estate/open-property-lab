"""Transparent ranking evaluation on explicitly authored synthetic judgments."""
import json,math,re,unicodedata
from pathlib import Path


def tokens(text):
    return set(re.findall(r'\w+',unicodedata.normalize('NFKC',text).casefold(),flags=re.UNICODE))


def lexical_rank(query,corpus):
    words=tokens(query['text'])
    scored=[(len(words & tokens(row['en']+' '+row['ru'])),row['id']) for row in corpus]
    return [key for score,key in sorted(scored,key=lambda x:(-x[0],x[1])) if score>0]


def eligible(row,criteria):
    allowed={'min_bedrooms','max_bedrooms','max_budget_points','pets','near_transit','garden'}
    if set(criteria)-allowed: raise ValueError('Unsupported explicit filter')
    for key in ('min_bedrooms','max_bedrooms','max_budget_points'):
        if key in criteria and (type(criteria[key]) is not int or criteria[key]<0):
            raise ValueError('Numeric filters must be nonnegative integers')
    if criteria.get('min_bedrooms',0)>criteria.get('max_bedrooms',1000):
        raise ValueError('Contradictory bedroom range')
    for key in ('near_transit','garden'):
        if key in criteria and type(criteria[key]) is not bool: raise ValueError('Boolean filter required')
    if 'pets' in criteria and criteria['pets'] not in ('allowed','not_allowed','unknown'):
        raise ValueError('Pet policy must be explicit, including unknown')
    if row['bedrooms']<criteria.get('min_bedrooms',0):return False
    if row['bedrooms']>criteria.get('max_bedrooms',1000):return False
    if row['budget_points']>criteria.get('max_budget_points',10**12):return False
    for key in ('pets','near_transit','garden'):
        if key in criteria and row[key]!=criteria[key]:return False
    return True


def constrained_rank(query,corpus):
    # Explicit structured filters are supplied by the query author. This does
    # not infer constraints or negation from the natural-language query.
    pool=[r for r in corpus if eligible(r,query.get('criteria',{}))]
    words=tokens(query['text'])
    return [key for _,key in sorted([(len(words & tokens(r['en']+' '+r['ru'])),r['id']) for r in pool],key=lambda x:(-x[0],x[1]))]


def metrics(ranking,judgments,k=3):
    if type(k) is not int or k<1:raise ValueError('k must be a positive integer')
    if len(set(ranking))!=len(ranking):raise ValueError('Duplicate ranking identifiers')
    if set(ranking)-set(judgments):raise ValueError('Unjudged candidate identifier')
    if any(type(g) is not int or not 0<=g<=3 for g in judgments.values()):
        raise ValueError('Grades must be integers0..3')
    grades=[judgments[x] for x in ranking[:k]]
    relevant=sum(g>0 for g in judgments.values());hits=sum(g>0 for g in grades)
    def dcg(items):return sum((2**g-1)/math.log2(i+2) for i,g in enumerate(items))
    ideal=dcg(sorted(judgments.values(),reverse=True)[:k])
    return {'precision_at_k':hits/k,'recall_at_k':hits/relevant if relevant else 0.,
            'ndcg_at_k':dcg(grades)/ideal if ideal else 0.,
            'reciprocal_rank_at_k':next((1/(i+1) for i,g in enumerate(grades) if g>0),0.),
            'relevant_candidates':relevant,'retrieved_at_k':len(grades)}


def load(root):
    root=Path(root)
    corpus,queries,qrels=[json.loads((root/name).read_text(encoding='utf-8')) for name in ('corpus.json','queries.json','qrels.json')]
    ids=[x['id'] for x in corpus];qids=[x['id'] for x in queries]
    if len(ids)!=len(set(ids)) or len(qids)!=len(set(qids)):raise ValueError('Duplicate corpus/query identifiers')
    if set(qids)!=set(qrels):raise ValueError('Missing or extra query judgments')
    for row in corpus:
        if row['pets'] not in ('allowed','not_allowed','unknown'):raise ValueError('Invalid pet policy')
        if type(row['bedrooms']) is not int or row['bedrooms']<0 or type(row['budget_points']) is not int or row['budget_points']<0:raise ValueError('Invalid numeric corpus field')
        if any(type(row[k]) is not bool for k in ('near_transit','garden')):raise ValueError('Invalid boolean corpus field')
    for q in queries:
        if set(qrels[q['id']])!=set(ids):raise ValueError('Every candidate requires an explicit judgment')
        metrics([],qrels[q['id']]);eligible(corpus[0],q['criteria'])
    return corpus,queries,qrels


def evaluate(root,k=3):
    corpus,queries,qrels=load(root);rows=[]
    for name,ranker in [('lexical_only',lexical_rank),('explicit_filters_plus_lexical',constrained_rank)]:
        for q in queries:
            ranking=ranker(q,corpus);scores=metrics(ranking,qrels[q['id']],k)
            rows.append({'system':name,'query_id':q['id'],'language':q['language'],'query':q['text'],
                         'explicit_filters':q['criteria'],'ranking':ranking,
                         'missed_relevant_ids':[key for key,g in qrels[q['id']].items() if g>0 and key not in ranking[:k]],**scores})
    summary=[]
    for name in ('lexical_only','explicit_filters_plus_lexical'):
        answerable=[r for r in rows if r['system']==name and r['relevant_candidates']>0]
        unanswerable=[r for r in rows if r['system']==name and r['relevant_candidates']==0]
        summary.append({'system':name,'answerable_queries':len(answerable),
                        **{key:sum(r[key] for r in answerable)/len(answerable) if answerable else 0. for key in ('precision_at_k','recall_at_k','ndcg_at_k','reciprocal_rank_at_k')},
                        'no_relevant_queries':len(unanswerable),'correct_empty_results':sum(not r['ranking'] for r in unanswerable)})
    return {'k':k,'scope':'Authored synthetic English/Russian cases; not live listings, trained-model performance or a representative benchmark.',
            'candidate_count':len(corpus),'query_count':len(queries),'summary':summary,'per_query':rows}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',default=str(Path(__file__).parent));p.add_argument('--output');args=p.parse_args();text=json.dumps(evaluate(args.root),ensure_ascii=False,indent=2)+'\n'
    if args.output:Path(args.output).write_text(text,encoding='utf-8')
    else:print(text,end='')
