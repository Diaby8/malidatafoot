import json, glob, pandas as pd
B='/home/claude/repo/malidatafoot/data/bronze'
def ts(s):
    h,m,r=s.split(':'); return int(h)*3600+int(m)*60+float(r)
matches=json.load(open(f'{B}/matches/1267/107.json'))
rows=[]; mrows=[]
for m in matches:
    mid=m['match_id']; ev=json.load(open(f'{B}/events/{mid}.json'))
    periods=set(e['period'] for e in ev)
    mrows.append(dict(match_id=mid,home=m['home_team']['home_team_name'],away=m['away_team']['away_team_name'],
        hs=m['home_score'],as_=m['away_score'],stage=m['competition_stage']['name'],date=m['match_date'],
        minutes=120 if 3 in periods else 90, periods=sorted(periods)))
    for e in ev:
        t=e['type']['name']; d=dict(match_id=mid,id=e['id'],index=e['index'],period=e['period'],t=ts(e['timestamp']),
          minute=e['minute'],type=t,team=e['team']['name'],poss=e['possession'],poss_team=e['possession_team']['name'],
          pp=e['play_pattern']['name'],x=None,y=None,ex=None,ey=None,outcome=None,sub=None,length=None,
          cross=False,xg=None,under_pressure=e.get('under_pressure',False),counterpress=e.get('counterpress',False),
          player=(e.get('player') or {}).get('name'),duration=e.get('duration'))
        if 'location' in e: d['x'],d['y']=e['location'][:2]
        k={'Pass':'pass','Carry':'carry','Shot':'shot','Duel':'duel','Interception':'interception','Dribble':'dribble',
           'Ball Recovery':'ball_recovery','Goal Keeper':'goalkeeper','Clearance':'clearance','50/50':'50_50','Block':'block','Ball Receipt*':'ball_receipt'}.get(t)
        o=e.get(k,{}) if k else {}
        if 'end_location' in o: d['ex'],d['ey']=o['end_location'][:2]
        if 'outcome' in o: d['outcome']=o['outcome']['name']
        if 'type' in o: d['sub']=o['type']['name']
        if t=='Pass':
            d['length']=o.get('length'); d['cross']=o.get('cross',False)
            if o.get('type'): d['sub']=o['type']['name']
        if t=='Shot': d['xg']=o.get('statsbomb_xg')
        if t=='Ball Recovery': d['outcome']='Failure' if o.get('recovery_failure') else 'Success'
        if t=='Block' and o.get('deflection'): d['sub']='deflection'
        rows.append(d)
E=pd.DataFrame(rows); M=pd.DataFrame(mrows)
E.to_pickle('events.pkl'); M.to_pickle('matches.pkl')
print(E.shape, M.minutes.value_counts().to_dict(), M.stage.value_counts().to_dict())
