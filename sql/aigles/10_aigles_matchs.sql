-- GOLD AIGLES 10 — un match du Mali par ligne, vu du côté du Mali.
-- lieu : « domicile » (au Mali, ou désigné à domicile), « extérieur », ou « neutre » (ni l'un ni l'autre).
create or replace table gold.aigles_matchs as
with m as (
    select date, tournament as competition, city as ville, country as pays, neutral as neutre,
           case when home_team = '{equipe}' then away_team else home_team end            as adversaire,
           case when home_team = '{equipe}' then home_score else away_score end          as buts_pour,
           case when home_team = '{equipe}' then away_score else home_score end          as buts_contre,
           home_team = '{equipe}'                                                        as designe_domicile,
           home_team, away_team
    from silver.intl_matches
    where home_team = '{equipe}' or away_team = '{equipe}'
),
tab as (
    select date, home_team, away_team, winner from silver.intl_shootouts
)
select m.date, m.competition, m.adversaire, m.buts_pour, m.buts_contre,
       case when m.buts_pour > m.buts_contre then 'V' when m.buts_pour < m.buts_contre then 'D' else 'N' end as resultat,
       case when not m.neutre and m.designe_domicile then 'domicile'
            when not m.neutre then 'extérieur' else 'neutre' end                          as lieu,
       m.ville, m.pays,
       tab.winner is not null                                                             as tirs_au_but,
       case when tab.winner is null then null else tab.winner = '{equipe}' end           as tab_gagnes,
       m.competition = 'Friendly'                                                         as amical,
       year(m.date)                                                                       as annee
from m left join tab using (date, home_team, away_team)
order by m.date;
