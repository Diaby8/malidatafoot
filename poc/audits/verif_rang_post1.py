import csv,sys,collections
R=[r for r in csv.DictReader(open(sys.argv[1],encoding='utf-8')) if r['home_score'] not in ('','NA')]
CANT={'African Cup of Nations','African Cup of Nations qualification'}
caf={t for r in R if r['date']>='2020' and r['tournament'] in CANT for t in (r['home_team'],r['away_team'])}
print('équipes africaines (CAN ou éliminatoires depuis 2020) :',len(caf))
def rang(filtre,depuis='2020-01-01',seuil=10,label=''):
    s=collections.defaultdict(lambda:[0,0])
    for r in R:
        if r['date']>=depuis and filtre(r['tournament']):
            for t,enc in ((r['home_team'],int(r['away_score'])),(r['away_team'],int(r['home_score']))):
                if t in caf: s[t][0]+=1; s[t][1]+=enc
    L=sorted([(b/n,t,n,b) for t,(n,b) in s.items() if n>=seuil])
    top=' | '.join(f'{i+1} {t} {b}/{n}={m:.3f}' for i,(m,t,n,b) in enumerate(L[:5]))
    rm=[i+1 for i,x in enumerate(L) if x[1]=='Mali'][0]
    print(f'{label:<55} Mali {rm}e sur {len(L)} :: {top}')
base=lambda t:t in CANT|{'FIFA World Cup qualification'}
rang(base,label='A. base (CAN + élim. CAN + élim. Mondial)')
rang(lambda t:base(t) or t=='FIFA World Cup',label='B. + phase finale du Mondial (2022, 2026)')
rang(lambda t:t!='Friendly',label='C. tout sauf amicaux (Coupe arabe, COSAFA, etc.)')
rang(lambda t:True,label='D. tout, amicaux compris')
for d in ('2021-01-01','2022-01-01','2023-01-01','2019-01-01','2018-01-01'): rang(base,d,label=f'E. base depuis {d[:4]}')
for sl in (20,30,40): rang(base,seuil=sl,label=f'F. base, au moins {sl} matchs')
print('\nTournois hors amicaux joués par des équipes africaines depuis 2020 :')
c=collections.Counter(r['tournament'] for r in R if r['date']>='2020' and (r['home_team'] in caf or r['away_team'] in caf))
for k,v in c.most_common(): print(f'  {v:4} {k}')
