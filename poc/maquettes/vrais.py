import json, os, subprocess, sys
SH='/tmp/claude-0/-home-claude/0d468fea-34ce-5de5-a264-0cb0f60bc885/scratchpad'
sys.path.insert(0, SH); import formats
SUJETS = [  # dossier, plans TikTok (nom html sans .html), plans X (natifs X ou convertis)
 ('01-defense', ['T_pv_1','T_pv_2'], ['pv_1','pv_2']),
 ('02-points-fifa-rwanda', ['T_pv_3'], ['pv_3']),
 ('03-simulation-groupe-k', ['T_ms_2','poc_c3'], ['ms_1','ms_2']),
 ('04-video-A-le-1-1', ['va_1','va_2','vt_1','vt_2','va_5'], None),
 ('05-video-B-trois-questions', ['poc_b1','vt_1','poc_b3'], None),
 ('06-video-C-boite-a-outils', ['poc_c1','poc_c2','poc_c3'], None),
 ('07-terrain', ['va_3','vt_1'], None),
 ('09-recuperer-haut', ['poc_e1','poc_e2'], None),
 ('10-styles', ['poc_f1'], None),
 ('11-maudit', ['poc_g1'], None),
 ('12-roi-du-nul', ['poc_g2'], None),
 ('13-sinayoko-selection', ['pj_s1','pj_s2'], None),
 ('14-sinayoko-premier-defenseur', ['a14_s14_1','a14_s14_2'], None),
 ('15-sinayoko-il-finit', ['a14_s15_1','a14_s15_2'], None),
 ('16-onze-contre-dix', ['a14_s16_1','a14_s16_2'], None),
 ('17-par-ou-attaque-le-mali', ['a14_s17_1','a14_s17_2'], None),
 ('18-tirer-de-loin', ['a14_s18_1','a14_s18_2'], None),
 ('19-rassemblement-septembre', ['a19_1','a19_2','a19_3'], None)]
json.dump(SUJETS, open(SH + '/sujets.json', 'w'))
for d, tt, xx in SUJETS:
    for n in ('pv_1', 'pv_2', 'pv_3', 'ms_1', 'ms_2'):
        formats.x_vers_tt(f'_{n}.html', n)
    if xx is None:
        for n in tt: formats.tt_vers_x(f'_{n}.html', n)
