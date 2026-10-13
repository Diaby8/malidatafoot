"""Planche de choix des bannières « terrain derrière » : chaque bannière telle qu'elle apparaîtra sous la photo de profil, numérotée."""
from da import BASE_CSS
import sys
DOS = sys.argv[1] if len(sys.argv) > 1 else 'bt'
N = ["Un point par match depuis 1960, jaune", "Un point par match depuis 1960, nuit", "Cartes dispersées sur le terrain, jaune",
     "Cartes dispersées sur le terrain, nuit", "Cartes en éventail, jaune", "Cartes en éventail, nuit"]
it = ''.join(f'<div class="c"><div class="t"><b>{i+1}</b>{n}</div><img src="{DOS}/p{i+1}.png"></div>' for i, n in enumerate(N))
open('planche_bt.html', 'w', encoding='utf-8').write(f'''<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
html,body{{width:1560px!important;height:auto!important;overflow:visible!important;background:#0E1A13!important}}#g{{display:grid;grid-template-columns:1fr 1fr;gap:34px 30px;padding:30px}}
.c img{{width:735px;display:block;border-radius:6px}}.t{{display:flex;align-items:baseline;gap:12px;margin-bottom:10px;font:500 19px/1 "IN";color:#fff}}
.t b{{font:italic 900 34px/1 "BC";color:#F6C41C}}</style></head><body><div id="g">{it}</div>
<script>Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode().catch(()=>{{}}))]).then(()=>{{window.READY=true}})</script></body></html>''')
