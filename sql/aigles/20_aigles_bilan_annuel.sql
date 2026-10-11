-- GOLD AIGLES 20 — bilan par année : matchs, victoires, nuls, défaites, buts.
create or replace table gold.aigles_bilan_annuel as
select annee,
       count(*)                                  as matchs,
       count(*) filter (resultat = 'V')          as victoires,
       count(*) filter (resultat = 'N')          as nuls,
       count(*) filter (resultat = 'D')          as defaites,
       sum(buts_pour)                            as buts_pour,
       sum(buts_contre)                          as buts_contre,
       count(*) filter (not amical)              as matchs_officiels
from gold.aigles_matchs
group by annee
order by annee;
