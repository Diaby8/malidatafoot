# independent recount from raw JSON (no shared code)
import json
B='/home/claude/repo/malidatafoot/data/bronze'
ms=[m for m in json.load(open(B+'/matches/1267/107.json')) if 'Mali' in (m['home_team']['home_team_name'],m['away_team']['away_team_name'])]
SKIP={'Starting XI','Half Start','Half End','Tactical Shift','Substitution','Player On','Player Off','Injury Stoppage','Referee Ball-Drop','Bad Behaviour','Own Goal For','Own Goal Against'}
nreg=0; sx=0; fwd=0; ln=0; oppz=0; da=0; pres=0; opp_pass=0
for m in ms:
    ev=[e for e in json.load(open(f"{B}/events/{m['match_id']}.json")) if e['period']<=4]
    ev.sort(key=lambda e:e['index'])
    first={}; order=[]
    for e in ev:
        if e['type']['name'] in SKIP: continue
        if e['possession'] not in first: first[e['possession']]=e; order.append(e['possession'])
    for i,p in enumerate(order[1:],1):
        e=first[p]; prev=first[order[i-1]]
        if e['possession_team']['name']=='Mali' and prev['possession_team']['name']!='Mali' and e['play_pattern']['name'] in ('Regular Play','From Counter') and e['type']['name']!='Goal Keeper':
            nreg+=1; sx+=e['location'][0]
    for e in ev:
        t=e['type']['name']; mine=e['team']['name']=='Mali'
        if t=='Pass':
            pt=e['pass'].get('type',{}).get('name'); op=pt not in ('Corner','Free Kick','Goal Kick','Throw-in','Kick Off')
            if mine and op and 'outcome' not in e['pass']:
                fwd+=e['pass']['end_location'][0]-e['location'][0]; ln+=e['pass']['length']
            if not mine: opp_pass+=1
            if not mine and op and e['location'][0]<=72: oppz+=1
        if mine and t=='Pressure': pres+=1
        if mine and e.get('location') and e['location'][0]>=48 and (t in ('Interception','Foul Committed','Dribbled Past') or (t=='Duel' and e['duel']['type']['name']=='Tackle')): da+=1
print('regains',nreg,'mean x',round(sx/nreg,2),'directness',round(fwd/ln,4),'ppda',round(oppz/da,3),'press/100 opp passes',round(pres/opp_pass*100,2))
