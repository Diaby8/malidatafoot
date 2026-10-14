"""Bande son de la vidéo explicative v2 (sons de synthèse, sans musique sous droits) : un clic par passe, un souffle à chaque
mouvement de caméra, une note nette à chaque nouvelle couche, un coup sourd sur la tête, un accord à la fin.
Les temps suivent la table T de video_v2.py. usage : python3 sons_v2.py sortie.wav"""
import json, os, sys, wave
import numpy as np
ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.dirname(os.path.dirname(ICI))
SR = 48000
T = dict(hook=0, zero=1.38, rien=2.45, evts=5.28, plonge=7.9, couche1=9.27, actA=10.62, actB=15.6, couche2=15.86, couche3=18.97, couche4=21.32, cote=23.5, f1=26.11, f2=27.18, f3=28.45, f4=30.72, carrousel=34.31, dor=36.38, mur=37.93, mot1=41.63, mot2=42.45, fin=44.22, quest=47.51, duree=51.3)
P = json.load(open(os.path.join(RACINE, 'poc/xt/top_possession.json')))['meilleure']
def ts(e):
    h, m, s = e['timestamp'].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
t0 = ts(P['sequence'][0]); reel = P['fin']['t_relatif_s']
passes = [ts(e) - t0 for e in P['sequence'] if e['type'] == 'Pass' and e.get('equipe') == 'Mali']
vt = lambda r: T['actA'] + r / reel * (T['actB'] - T['actA'])
N = int(SR * T['duree']); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(7)
def poser(t, sig, g=1.0, pan=0.0):
    i = int(t * SR); n = min(len(sig), N - i)
    if n <= 0: return
    L[i:i + n] += sig[:n] * g * (1 - max(0, pan)); R[i:i + n] += sig[:n] * g * (1 + min(0, pan))
def env(n, a=.004, r=None):
    e = np.ones(n); ka = max(1, int(a * SR)); e[:ka] = np.linspace(0, 1, ka)
    kr = n - ka if r is None else int(r * SR); e[-kr:] *= np.linspace(1, 0, kr) ** 2; return e
def clic(f=2400, d=.035):
    n = int(d * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * f * t) * env(n, .001) * .5 + rng.normal(0, 1, n) * env(n, .0005, d * .9) * .08
def note(f, d=.28):
    n = int(d * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * env(n, .006) * .45
def souffle(d=1.0, f0=300, f1=1800):
    n = int(d * SR); b = rng.normal(0, 1, n); out = np.zeros(n); y = 0.0
    fc = np.geomspace(f0, f1, n); a = 1 - np.exp(-2 * np.pi * fc / SR)
    for i in range(n): y += a[i] * (b[i] - y); out[i] = y
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.6; return out * e * 1.4
def coup(f=70, d=.45):
    n = int(d * SR); t = np.arange(n) / SR; fr = f * (1 + 1.5 * np.exp(-t * 30)); ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.sin(ph) * np.exp(-t * 7) * .9
def accord(fs=(220, 277.2, 329.6, 440), d=2.6):
    n = int(d * SR); t = np.arange(n) / SR; s = sum(np.sin(2 * np.pi * f * t) for f in fs) / len(fs); return s * env(n, .02, d * .8) * .55
poser(T['zero'], coup(55, .7), .9)                                       # le 0-0
poser(T['evts'], souffle(1.6, 900, 4000), .18)                           # le compteur des événements
poser(T['plonge'] - .1, souffle(1.5, 200, 2200), .5)                     # la plongée
for i, k in enumerate(('couche1', 'couche2', 'couche3', 'couche4')): poser(T[k], note([660, 740, 830, 990][i]), .35)
for r in passes: poser(vt(r), clic(2200 + 300 * rng.random()), .5, pan=float(rng.uniform(-.4, .4)))
poser(T['couche3'] + .2, note(1320, .18), .25)                           # +0,25
poser(T['cote'] - .2, coup(90, .35), .7)                                 # la tête, à côté
for k in ('f1', 'f2', 'f3', 'f4'): poser(T[k], souffle(.45, 600, 3000), .32); poser(T[k] + .05, note(880, .16), .25)
poser(T['carrousel'] - .1, souffle(.9, 400, 2600), .45)                  # le jaune entre
for i in range(6): poser(T['carrousel'] + .3 + i * .22, clic(1500, .03), .3, pan=-.5 + i * .2)
poser(T['carrousel'] + 1.6, coup(120, .25), .45)                         # arrêt sur Dorgeles
poser(T['mur'], souffle(2.4, 1800, 150), .45)                            # le dézoom
for k in ('mot1', 'mot2'): poser(T[k], note(740, .14), .25)
poser(T['fin'], accord(), .6); poser(T['quest'], note(990, .2), .3)
m = max(np.abs(L).max(), np.abs(R).max()); g = .5 / m
pcm = (np.stack([L, R], 1) * g * 32767).astype(np.int16)
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print('ok', sys.argv[1], len(passes), 'passes')
