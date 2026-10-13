"""Données des bannières « terrain derrière » : les actions avec ballon, les passes réussies et les tirs du Mali
à la CAN 2023 (StatsBomb Open Data, silver.events), écrites dans banniere_passes.json (non suivi par git, comme vitrine.json).
usage : python banniere_donnees.py   (depuis visuels/, après python taches.py donnees)"""
import json
from pathlib import Path
import duckdb
c = duckdb.connect(str(Path(__file__).resolve().parent.parent / 'data' / 'warehouse.duckdb'), read_only=True)
q = lambda s: c.sql(s).fetchall()
P = q("""select round(x,1),round(y,1),round(end_x,1),round(end_y,1) from silver.events
         where team='Mali' and type='Pass' and pass_outcome is null and x is not null and end_x is not null""")
T = q("select round(x,1),round(y,1),shot_xg,shot_outcome='Goal',shot_type from silver.events where team='Mali' and type='Shot'")
A = q("select round(x,1),round(y,1) from silver.events where team='Mali' and type in ('Pass','Carry','Shot','Dribble') and x is not null")
d = dict(source="StatsBomb Open Data, CAN 2023, 5 matchs du Mali", passes_reussies=len(P), tirs=len(T), buts=sum(1 for t in T if t[3]),
         passes=P, shots=[dict(x=a, y=b, xg=g, but=bool(o), type=s) for a, b, g, o, s in T],
         actions_avec_ballon=[list(a) for a in A], actions_note="passes, conduites, tirs et dribbles du Mali (lieu de départ), 5 matchs")
assert d['tirs'] == 64 and d['buts'] == 5, "les chiffres de référence de la CAN 2023 ont changé : recompter avant de publier"
Path('banniere_passes.json').write_text(json.dumps(d), encoding='utf-8'); print('ok', len(A), 'actions,', len(P), 'passes réussies,', len(T), 'tirs')
