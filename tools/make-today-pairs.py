#!/usr/bin/env python3
"""Builds today-pairs.js from daily-results.js: Pick 3 pairs (US games) that didn't play yesterday,
are overdue, came once / twice yesterday. Public winning numbers only."""
import itertools,json,datetime as dt,collections,sys
from zoneinfo import ZoneInfo
src=open('daily-results.js',encoding='utf-8').read()
body=src.split('const DAILY_RESULTS = `')[1].split('`')[0]
CAN={'Atlantic Canada','Ontario','Québec','Quebec','Western Canada'}
ORD={'Morning':0,'Midday':1,'Day':1,'Afternoon':2,'Evening':3,'Night':4}
rows=[l.split('|') for l in body.strip().split('\n') if l.count('|')==4]
p3=[(d,s,dr,n) for d,s,g,dr,n in rows if g=='Pick 3' and s not in CAN]
p3.sort(key=lambda r:(r[0],ORD.get(r[2],2)))
today=dt.datetime.now(ZoneInfo('America/Chicago')).date()
yday=(today-dt.timedelta(days=1)).isoformat()
seq=[r for r in p3 if r[0]<=yday]
if not seq:sys.exit('no data')
pairs=lambda n:{''.join(sorted(c)) for c in itertools.combinations(n,2)}
allp=[''.join(x) for x in itertools.combinations_with_replacement('0123456789',2)]
last={};
for i,r in enumerate(seq):
    for p in pairs(r[3]):last[p]=i
N=len(seq);gap={p:(N-1-last[p]) if p in last else N for p in allp}
cnt=collections.Counter()
for r in seq:
    if r[0]==yday:
        for p in pairs(r[3]):cnt[p]+=1
mir=lambda p:''.join(str((int(c)+5)%10) for c in p)
def fl(p):
    d=p[0]==p[1];g=gap[p]
    return 2 if g>=(107 if d else 56) else 1 if g>=(71 if d else 37) else 0
digits=sum(int(c) for c in today.strftime('%m%d%Y'))
dd=digits%10
out=dict(
 date=today.isoformat(),label=today.strftime('%A, %B ')+str(today.day)+today.strftime(', %Y'),
 through=yday,draws=sum(1 for r in seq if r[0]==yday),
 dateDigit=dict(sum=digits,digit=dd,mirror=(dd+5)%10,math='+'.join(today.strftime('%m%d%Y'))+' = '+str(digits)),
 didnt=[dict(p=p,gap=gap[p],flames=fl(p),mirror=mir(p)) for p in allp if cnt[p]==0],
 overdue=[dict(p=p,gap=gap[p],flames=fl(p),mirror=mir(p)) for p in sorted(allp,key=lambda p:-gap[p]) if fl(p) and cnt[p]>0],
 once=[p for p in allp if cnt[p]==1],twice=[p for p in allp if cnt[p]==2],
 note='Counted from the NumberState results board (US Pick 3 games, Central time). Tracking only, not a prediction.')
open('today-pairs.js','w',encoding='utf-8').write('window.TODAY_PAIRS='+json.dumps(out,ensure_ascii=False)+';\n')
print(out['label'],out['through'],out['draws'],[x['p'] for x in out['didnt']])
