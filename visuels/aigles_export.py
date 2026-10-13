"""Historique des Aigles pour les visuels : un match par ligne, vu du côté du Mali (gold.aigles_matchs, source
martj42/international_results, CC0), écrit dans aigles_histoire.json (non suivi par git).
usage : python aigles_export.py   (depuis visuels/, après python taches.py donnees)"""
import json
from pathlib import Path
import duckdb
c = duckdb.connect(str(Path(__file__).resolve().parent.parent / 'data' / 'warehouse.duckdb'), read_only=True)
cols = ['date', 'competition', 'adversaire', 'buts_pour', 'buts_contre', 'resultat', 'lieu', 'tirs_au_but', 'tab_gagnes', 'amical', 'annee']
M = [dict(zip(cols, r)) for r in c.sql(f"select {','.join(cols)} from gold.aigles_matchs order by date").fetchall()]
for m in M: m['date'] = m['date'].isoformat()
assert len(M) > 500 and all(m['resultat'] in 'VND' for m in M)
d = dict(source="martj42/international_results (CC0), recoupé avec StatsBomb", matchs=M,
         premier=M[0]['date'], dernier=M[-1]['date'], n=len(M))
Path('aigles_histoire.json').write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')
print('ok', len(M), 'matchs du', M[0]['date'], 'au', M[-1]['date'])
