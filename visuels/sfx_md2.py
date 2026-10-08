"""Effets sonores de la vidéo de lancement MaliDataFoot (37,45 s) — synthèse procédurale, calée sur la timeline de md2.html.
Sons gardés : djembés, impacts, souffles, coups de bois, tics, clameur. Pas de mélodie. Cloches retirées (voir CLOCHES)."""
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile

SR = 48000
DUR = 37.45
N = int(SR * DUR)
rng = np.random.default_rng(26)
mix = np.zeros((N, 2), dtype=np.float64)


# Nouvelle vidéo : l'accroche de l'ancien gabarit est jouée 1,26 fois plus vite, puis tout est avancé de 0,65 s.
# Les blocs écrits pour l'ancien minutage passent par W ; les nouveaux (fiche, duel, fin) donnent leur temps réel.
WARP = True
def W(t):
    return t / 1.26 if t < 3.15 else t - 0.65


def put(sig, t, gain=1.0, pan=0.0):
    """Place un son mono (ou stéréo) à l'instant t. pan: -1 gauche … +1 droite."""
    i = int(round((W(t) if WARP else t) * SR))
    if i >= N:
        return
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4)
        r = np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l, sig * r], axis=1) * np.sqrt(2) * 0.7071
    n = min(len(sig), N - i)
    mix[i:i + n] += sig[:n] * gain


def tt(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR))


def bp(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype='band', fs=SR, output='sos')
    return sosfilt(sos, x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype='high', fs=SR, output='sos'), x)


def fade(x, a=0.003, r=0.01):
    n = len(x)
    na, nr = min(int(a * SR), n // 2), min(int(r * SR), n // 2)
    e = np.ones(n)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return x * (e[:, None] if x.ndim == 2 else e)


def sweep_noise(d, f0, f1, q=0.55, shape='bell', skew=0.5):
    """Souffle filtré dont la fréquence centrale glisse de f0 à f1 (filtrage par STFT)."""
    n = int(d * SR)
    x = rng.standard_normal(n + 4096)
    win, hop = 1024, 256
    w = np.hanning(win)
    out = np.zeros(len(x) + win)
    freqs = np.fft.rfftfreq(win, 1 / SR)
    nfr = (len(x) - win) // hop
    for k in range(nfr):
        p = min(1.0, k * hop / n)
        fc = f0 * (f1 / f0) ** p
        g = np.exp(-0.5 * (np.log(np.maximum(freqs, 1) / fc) / q) ** 2)
        seg = np.fft.irfft(np.fft.rfft(x[k * hop:k * hop + win] * w) * g)
        out[k * hop:k * hop + win] += seg * w
    out = out[:n]
    p = np.linspace(0, 1, n)
    if shape == 'bell':
        env = np.sin(np.pi * p ** (np.log(0.5) / np.log(skew))) ** 2
    elif shape == 'rise':
        env = p ** 2.2
        env[-int(0.012 * SR):] *= np.linspace(1, 0, int(0.012 * SR))
    else:
        env = (1 - p) ** 2
    out *= env
    return out / (np.max(np.abs(out)) + 1e-9)


def whoosh(d, f0=300, f1=2600, pan0=-0.7, pan1=0.7, skew=0.5):
    m = sweep_noise(d, f0, f1, skew=skew)
    p = np.linspace(pan0, pan1, len(m))
    l = np.cos((p + 1) * np.pi / 4)
    r = np.sin((p + 1) * np.pi / 4)
    return np.stack([m * l, m * r], axis=1)


def djembe(kind):
    if kind == 'bass':
        t = tt(0.7)
        f = 62 + 55 * np.exp(-t / 0.028)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
        s += 0.35 * lp(noise(0.7), 900) * np.exp(-t / 0.012)
    elif kind == 'tone':
        t = tt(0.4)
        f = 300 + 60 * np.exp(-t / 0.015)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.085)
        s += 0.35 * np.sin(2 * np.pi * 1.59 * np.cumsum(f) / SR) * np.exp(-t / 0.05)
        s += 0.4 * bp(noise(0.4), 500, 1600) * np.exp(-t / 0.014)
    else:  # slap
        t = tt(0.3)
        s = 0.9 * bp(noise(0.3), 900, 4200) * np.exp(-t / 0.032)
        s += 0.6 * np.sin(2 * np.pi * 540 * t) * np.exp(-t / 0.045)
        s += 0.3 * np.sin(2 * np.pi * 1130 * t) * np.exp(-t / 0.03)
    return fade(s / np.max(np.abs(s)), 0.0005, 0.03)


def impact(size=1.0):
    d = 1.6 * size
    t = tt(d)
    f = 36 + 44 * np.exp(-t / 0.06)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.42 * size))
    s += 0.7 * lp(noise(d), 1800) * np.exp(-t / 0.11)
    s += 0.45 * bp(noise(d), 1500, 7000) * np.exp(-t / 0.035)
    s = np.tanh(1.6 * s)
    return fade(s / np.max(np.abs(s)), 0.0005, 0.05)


def tick(f=2600, d=0.03):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006) + 0.5 * hp(noise(d), 4000) * np.exp(-t / 0.003)
    return fade(s / np.max(np.abs(s)), 0.0003, 0.004)


def wood(f=820, d=0.16):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.03) + 0.45 * np.sin(2 * np.pi * f * 2.71 * t) * np.exp(-t / 0.014)
    s += 0.3 * bp(noise(d), 1500, 5000) * np.exp(-t / 0.004)
    return fade(s / np.max(np.abs(s)), 0.0003, 0.01)


def thock():
    t = tt(0.3)
    f = 140 + 120 * np.exp(-t / 0.012)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.06)
    s += 0.5 * bp(noise(0.3), 700, 3000) * np.exp(-t / 0.01)
    return fade(s / np.max(np.abs(s)), 0.0004, 0.02)


def click():
    t = tt(0.09)
    s = np.sin(2 * np.pi * 1900 * t) * np.exp(-t / 0.005) + 0.8 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.018)
    return fade(s / np.max(np.abs(s)), 0.0003, 0.01)


def pop(f0=380, f1=980, d=0.12):
    t = tt(d)
    f = f0 * (f1 / f0) ** (t / d)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035)
    return fade(s, 0.001, 0.02)


def bell(f, d=0.9, bright=1.0):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.28)
    s += 0.4 * bright * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.13)
    s += 0.2 * bright * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.06)
    return fade(s / np.max(np.abs(s)), 0.001, 0.05)


def shimmer(d=1.0):
    t = tt(d)
    s = np.zeros_like(t)
    for _ in range(26):
        f = rng.uniform(3800, 9500)
        ph = rng.uniform(0, 6.28)
        on = rng.uniform(0, d * 0.6)
        e = np.clip((t - on) / 0.02, 0, 1) * np.exp(-np.clip(t - on, 0, None) / rng.uniform(0.08, 0.3))
        s += np.sin(2 * np.pi * f * t + ph) * e
    return fade(s / np.max(np.abs(s)), 0.01, 0.1)


def paper(d=0.4):
    t = tt(d)
    s = bp(noise(d), 1800, 7500) * (0.55 + 0.45 * np.sin(2 * np.pi * 23 * t)) ** 2 * np.sin(np.pi * t / d) ** 1.5
    return fade(s / np.max(np.abs(s)), 0.005, 0.05)


def crowd(d=4.2):
    """Clameur de stade : souffle + chœur de voix désaccordées, façonnés par des formants."""
    n = int(d * SR)
    t = np.arange(n) / SR
    v = np.zeros(n)
    for _ in range(110):
        f0 = rng.uniform(130, 380)
        glide = 1 + rng.uniform(0.02, 0.22) * np.clip(t / 0.9, 0, 1) - rng.uniform(0, 0.12) * np.clip((t - 1.6) / 2.4, 0, 1)
        vib = 1 + 0.012 * np.sin(2 * np.pi * rng.uniform(4, 7) * t + rng.uniform(0, 6.28))
        ph = 2 * np.pi * np.cumsum(f0 * glide * vib) / SR
        a = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.3, 1.6) * t + rng.uniform(0, 6.28))
        on = rng.uniform(0, 0.5)
        a *= np.clip((t - on) / rng.uniform(0.15, 0.5), 0, 1)
        tone = sum(np.sin(k * ph + rng.uniform(0, 6.28)) / k for k in range(1, 9))
        v += tone * a
    x = 0.42 * v / np.max(np.abs(v)) + 0.9 * rng.standard_normal(n) * 0.35
    # formants (a / o ouverts) par STFT
    win, hop = 2048, 512
    w = np.hanning(win)
    fr = np.fft.rfftfreq(win, 1 / SR)
    g = np.zeros_like(fr)
    for fc, bw, amp in [(650, 260, 1.0), (1120, 320, 0.8), (2550, 520, 0.42), (3500, 700, 0.2), (300, 180, 0.35)]:
        g += amp * np.exp(-0.5 * ((fr - fc) / bw) ** 2)
    xp = np.concatenate([x, np.zeros(win)])
    out = np.zeros(len(xp) + win)
    for k in range((len(xp) - win) // hop):
        out[k * hop:k * hop + win] += np.fft.irfft(np.fft.rfft(xp[k * hop:k * hop + win] * w) * g) * w
    out = out[:n]
    lfo = lp(rng.standard_normal(n), 5) * 60
    env = np.clip(t / 0.4, 0, 1) ** 1.4 * np.where(t < 1.5, 1, np.exp(-(t - 1.5) / 1.05))
    out *= env * (1 + 0.25 * lfo / (np.max(np.abs(lfo)) + 1e-9))
    out /= np.max(np.abs(out))
    # stéréo large : deux versions décalées
    r = np.roll(out, int(0.013 * SR)) * 0.95
    return fade(np.stack([out, r], axis=1), 0.02, 0.4)


def _g(fn, k):
    return lambda *a, **kw: fn(*a, **kw) * k


# équilibre : les petits sons d'interface doivent rester audibles sur un téléphone
tick, wood, click, pop, bell = _g(tick, 2.3), _g(wood, 1.8), _g(click, 1.5), _g(pop, 1.7), _g(bell, 1.6)
# Cloches retirées le 8 octobre 2026 (Diaby : « les ting ting, ça fait trop »). Mettre CLOCHES = True pour les remettre.
CLOCHES = False
if not CLOCHES:
    bell = lambda *a, **k: np.zeros(1)
thock, whoosh, sweep_noise, shimmer, paper = _g(thock, 1.35), _g(whoosh, 1.5), _g(sweep_noise, 1.4), _g(shimmer, 1.7), _g(paper, 1.6)
impact, crowd = _g(impact, 0.7), _g(crowd, 0.92)


# ------------------------------------------------------------------ TIMELINE vitrine MaliDataFoot (calée sur tim.json)
import json
TM = json.load(open('tim.json')); TT = TM['TT']; VD = json.load(open('vitrine.json', encoding='utf-8'))
def swish_in(t):
    put(whoosh(0.4, 700, 4200, -0.8, 0.2), t, 0.28); put(thock(), t + 0.29, 0.36, -0.5)
def swish_out(t):
    put(whoosh(0.4, 2600, 500, -0.2, -0.8, skew=0.35), t, 0.24)
def roll(t0, t1, gain=0.05, pan=0.2, f=3400):
    t, step = t0, 0.022
    while t < t1:
        put(tick(f, 0.014), t, gain, pan); step *= 1.07; t += step

# accroche
put(tick(3200), 0.06, 0.18, -0.4)
put(djembe('tone'), 0.16, 0.55, -0.25); put(djembe('slap'), 0.55, 0.55, 0.25)   # deux lignes : « Les Aigles » / « jouent. »
roll(0.75, 1.35, 0.045, 0.0)
put(sweep_noise(0.9, 500, 5200, shape='rise'), 0.6, 0.3)
put(impact(0.8), 1.50, 0.8, -0.15); put(djembe('bass'), 1.50, 0.6)
put(impact(1.1), 1.82, 1.0, 0.1);  put(djembe('bass'), 1.82, 0.75); put(djembe('slap'), 1.82, 0.4, 0.3)
put(whoosh(0.85, 240, 3200, -0.9, 0.9, skew=0.55), 2.66, 0.75); put(whoosh(0.7, 900, 6500, -0.6, 0.8, skew=0.6), 2.78, 0.3)
put(impact(0.5), 3.35, 0.25)

# 1 — la carte des tirs : un petit son par tir, une cloche par but
t = TT['tirs']; o = TT['but'] - 0.25
swish_in(t); put(sweep_noise(0.8, 400, 2600, shape='rise'), t + 0.15, 0.14)
shots = VD['tirs']
for i, s in enumerate(shots):
    ts = t + 0.6 + i / len(shots) * 1.6; pan = (s['y'] - 40) / 60
    if s['is_goal']:
        put(bell(1050 + 60 * (i % 6), 0.5), ts, 0.13, pan); put(pop(500, 1300), ts, 0.2, pan)
    else:
        put(pop(300 + 700 * s['xg'], 700 + 1200 * s['xg'], 0.07), ts, 0.07 + 0.16 * s['xg'], pan)
put(whoosh(0.4, 500, 2600, -0.5, 0.5), t + 2.7, 0.24)
for i in range(3):
    put(bell(1318.5 + 220 * i, 0.6), t + 2.8 + i * 0.12, 0.14, 0.3); put(pop(), t + 2.8 + i * 0.12, 0.15, 0.3)
put(djembe('slap'), t + 2.8, 0.35, -0.5); roll(t + 2.85, t + 3.6, 0.045, -0.6)
swish_out(o - 0.02)

# 2 — l'anatomie d'un but : un coup de bois par passe, qui monte, puis le but
t = TT['but']; o = TT['fil'] - 0.25; BU = TM['BUT']
swish_in(t); put(sweep_noise(0.7, 400, 2400, shape='rise'), t + 0.1, 0.12)
np_ = 0
for e in BU['seq']:
    if e['type'] == 'Pass':
        put(wood(620 + 55 * np_, 0.09), e['at'], 0.24, -0.6 + 0.11 * np_); put(tick(2400 + 90 * np_, 0.02), e['at'], 0.06, -0.6 + 0.11 * np_); np_ += 1
    elif e['type'] == 'Carry':
        put(tick(1700, 0.016), e['at'], 0.035, 0.0)
put(sweep_noise(BU['A'] * 0.9, 300, 3600, shape='rise'), BU['T0'] + 0.3, 0.13)
shot_t = [e['at'] for e in BU['seq'] if e['type'] == 'Shot'][0]
put(whoosh(0.3, 900, 5200, 0.2, 0.9, skew=0.6), shot_t - 0.05, 0.4)
g = BU['goal']
put(impact(1.1), g, 0.95, 0.3); put(djembe('bass'), g, 0.7, 0.3); put(djembe('slap'), g + 0.01, 0.4, 0.4); put(bell(1568, 0.9), g + 0.02, 0.2, 0.3); put(shimmer(1.0), g + 0.03, 0.12)
put(crowd(2.0), g + 0.02, 0.1)
for i in range(3):
    put(thock(), g + 0.15 + i * 0.13, 0.45, 0.5); put(pop(420 + 70 * i, 1000 + 130 * i), g + 0.2 + i * 0.13, 0.15, 0.5)
roll(g + 0.3, g + 1.0, 0.04, 0.6)
swish_out(o - 0.02)

# 3 — le fil du match
t = TT['fil']; o = TT['res'] - 0.25; FI = TM['FIL']
swish_in(t); put(sweep_noise(FI['RVD'], 260, 2200, shape='rise'), FI['RV0'], 0.13)
for i, m in enumerate(FI['marks']):
    if not m['goal']:
        put(wood(2100, 0.12), m['t'], 0.24, 0.4); put(djembe('slap'), m['t'], 0.35, 0.4)
    elif i == 1:
        put(bell(1568, 0.7), m['t'], 0.17, -0.2); put(pop(500, 1300), m['t'], 0.22, -0.2); put(djembe('tone'), m['t'], 0.4, -0.2)
    else:
        put(impact(0.6), m['t'], 0.55, 0.3); put(djembe('bass'), m['t'], 0.5, 0.3)
if FI['red']:
    put(djembe('bass'), FI['red'], 0.45, -0.3); put(thock(), FI['red'], 0.4, -0.3)
e = FI['RV0'] + FI['RVD']
roll(e - 0.2, e + 0.4, 0.045, 0.7)
put(thock(), t + 2.95, 0.5, -0.6); roll(t + 3.05, t + 3.65, 0.04, -0.4)
swish_out(o - 0.02)

# 4 — le réseau de passes
t = TT['res']; o = TT['fiche'] - 0.25
swish_in(t); put(sweep_noise(0.7, 400, 2400, shape='rise'), t + 0.1, 0.12)
for i, n in enumerate(VD['reseau_passes']['nodes']):
    put(pop(360 + 45 * i, 900 + 90 * i), t + 0.6 + i * 0.06, 0.17, (n['y'] - 40) / 55)
roll(t + 1.2, t + 2.2, 0.035, 0.0, 2800)
put(impact(0.6), t + 2.45, 0.55, -0.3); put(djembe('tone'), t + 2.45, 0.45, -0.3); put(bell(1318.5, 0.8), t + 2.47, 0.16, -0.3)
put(thock(), t + 2.62, 0.45, -0.6); roll(t + 2.8, t + 3.4, 0.04, -0.6)
swish_out(o - 0.02)

# 5 — la fiche joueur (nouvelle DA) : volet rouge, photo, note qui monte, radar, lignes du tableau
WARP = False
t = 21.5
put(whoosh(0.5, 400, 3200, -0.6, 0.6, skew=0.5), t - 0.17, 0.35)
put(thock(), t + 0.3, 0.45, -0.5); put(pop(), t + 0.36, 0.18, -0.5)
roll(t + 0.6, t + 1.45, 0.035, 0.6)
put(thock(), t + 1.5, 0.4, 0.6); put(bell(1318.5, 0.7), t + 1.52, 0.12, 0.6)
put(sweep_noise(0.8, 300, 2600, shape='rise'), t + 1.3, 0.12)
put(pop(420, 1100), t + 2.05, 0.2, -0.3)
for i in range(10):
    put(wood(640 + 55 * i, 0.07), t + 1.95 + i * 0.06, 0.14, -0.5 + 0.1 * i)
for i in range(3):
    put(pop(480 + 90 * i, 1200 + 120 * i), t + 2.95 + i * 0.12, 0.16, -0.5 + 0.5 * i)

# 6 — le duel (nuit) : un coup par joueur, les deux notes, les barres qui s'ouvrent des deux côtés
t = 27.1
put(whoosh(0.5, 3200, 400, 0.6, -0.6, skew=0.5), t - 0.17, 0.5)
put(djembe('tone'), t + 0.32, 0.5, -0.6); put(djembe('slap'), t + 0.4, 0.5, 0.6)
roll(t + 0.65, t + 1.55, 0.035, 0.0, 3000)
put(thock(), t + 1.55, 0.45, -0.3); put(thock(), t + 1.67, 0.45, 0.3); put(bell(1568, 0.8), t + 1.69, 0.13)
for i in range(11):                        # six lignes « ce qu'ils font » puis cinq lignes « ce qu'ils réussissent »
    ts = t + (1.3 + i * 0.05 if i < 6 else 2.15 + (i - 6) * 0.05)
    put(wood(900 + 40 * i, 0.07), ts, 0.15, -0.6); put(wood(820 + 40 * i, 0.07), ts + 0.05, 0.15, 0.6)
put(pop(500, 1300), t + 2.85, 0.22); put(djembe('tone'), t + 2.87, 0.3)

# 8 — fin : le duel s'efface (33,1 s), le logo se pose, le nom, les comptes
put(whoosh(0.9, 3400, 260, -0.9, 0.9, skew=0.5), 33.05, 0.7)
t = 32.25
put(impact(0.9), t + 1.02, 0.6); put(djembe('bass'), t + 1.02, 0.55); put(thock(), t + 1.04, 0.5); put(shimmer(1.3), t + 1.06, 0.14)
for i in range(3):
    put(wood(760 + 130 * i), t + 1.18 + i * 0.1, 0.2, -0.3 + i * 0.3)
put(sweep_noise(0.7, 900, 5200, shape='rise'), t + 1.2, 0.12)
for i in range(5):
    put(bell(1046 + 130 * i, 0.4), t + 1.35 + i * 0.12, 0.09, -0.3 + i * 0.15)
put(pop(), t + 2.01, 0.25); put(thock(), t + 2.05, 0.35); put(bell(1318.5, 0.8), t + 2.07, 0.15)
for i, f in enumerate([740, 880, 1046]):
    put(wood(f), t + 2.35 + i * 0.08, 0.22, (i - 1) * 0.3)
put(djembe('slap'), t + 3.5, 0.2); put(tick(2600), t + 3.5, 0.1)

# ------------------------------------------------------------------ MASTER
ir_n = int(1.1 * SR)
it = np.arange(ir_n) / SR
wet = np.zeros_like(mix)
for ch in range(2):
    ir = rng.standard_normal(ir_n) * np.exp(-it / 0.26)
    ir[:int(0.012 * SR)] = 0
    ir = hp(lp(ir, 6500), 250)
    w = fftconvolve(mix[:, ch], ir)[:N]
    wet[:, ch] = w / (np.max(np.abs(w)) + 1e-9)
out = mix + 0.11 * wet * np.max(np.abs(mix))
# compresseur doux (3:1 au-dessus de -26 dB) pour resserrer la dynamique
lvl = np.sqrt(lp(np.max(out ** 2, axis=1), 18) .clip(1e-12)) / np.max(np.abs(out))
thr = 10 ** (-26 / 20)
gain = np.where(lvl > thr, (lvl / thr) ** (1 / 3 - 1), 1.0)
gain = lp(gain, 40).clip(0.05, 1.0)
out = out * gain[:, None]
out = np.tanh(out / np.max(np.abs(out)) * 1.5) / np.tanh(1.5)
out *= 10 ** (-1.5 / 20) / np.max(np.abs(out))
fo = int(0.3 * SR)
out[-fo:] *= np.linspace(1, 0, fo)[:, None]
wavfile.write('sfx_md2.wav', SR, (out * 32767).astype(np.int16))
rms = 20 * np.log10(np.sqrt(np.mean(out ** 2)))
print('ok', out.shape, 'peak %.2f' % np.max(np.abs(out)), 'rms %.1f dBFS' % rms)
