"""Vitrine verticale 1080x1920 : gabarit vitv.tpl.html + données du pipeline (vitrine.json)."""
import json
t=open('vitv.tpl.html',encoding='utf-8').read()
assert t.count('/*DATA*/')==1
D=json.load(open('vitrine.json',encoding='utf-8'))
open('vitv.html','w',encoding='utf-8').write(t.replace('/*DATA*/',json.dumps(D,ensure_ascii=False)))
print('ok')
