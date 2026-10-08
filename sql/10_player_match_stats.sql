-- GOLD 10 — une ligne par joueur et par match.
-- Repère StatsBomb : terrain de 120 x 80, chaque équipe attaque vers x = 120.
-- Surface adverse : x >= 102 et 18 <= y <= 62. Dernier tiers : x >= 80.
create or replace table gold.player_match_stats as
with e as (
    select *,
           sqrt(pow(120 - x, 2) + pow(40 - y, 2))         as d_start,   -- distance au but adverse
           sqrt(pow(120 - end_x, 2) + pow(40 - end_y, 2)) as d_end,
           (end_x >= 102 and end_y between 18 and 62)     as ends_in_box,
           (x >= 102 and y between 18 and 62)             as starts_in_box
    from silver.events
    where period <= 4 and player_id is not null
),
xa as (     -- passe décisive attendue : valeur du tir que la passe a amené
    select p.match_id, p.player_id, sum(s.shot_xg) as xa
    from silver.events p
    join silver.events s on s.event_id = p.pass_assisted_shot_id
    where p.type = 'Pass' and p.period <= 4
    group by 1, 2
)
select
    e.match_id, e.team, e.player_id,
    -- finition
    count(*) filter (type = 'Shot')                                                   as shots,
    count(*) filter (type = 'Shot' and shot_outcome in ('Goal', 'Saved', 'Saved to Post')) as shots_on_target,
    count(*) filter (type = 'Shot' and shot_outcome = 'Goal')                         as goals,
    count(*) filter (type = 'Shot' and shot_outcome = 'Goal' and shot_type <> 'Penalty') as np_goals,
    coalesce(sum(shot_xg) filter (type = 'Shot'), 0)                                  as xg,
    coalesce(sum(shot_xg) filter (type = 'Shot' and shot_type <> 'Penalty'), 0)       as npxg,
    -- passes
    count(*) filter (type = 'Pass')                                                   as passes,
    count(*) filter (type = 'Pass' and pass_outcome is null)                          as passes_completed,
    count(*) filter (type = 'Pass' and (pass_shot_assist or pass_goal_assist))        as key_passes,
    count(*) filter (type = 'Pass' and pass_goal_assist)                              as assists,
    count(*) filter (type = 'Pass' and pass_outcome is null and ends_in_box and not starts_in_box
                     and coalesce(pass_type, '') not in ('Corner', 'Free Kick', 'Throw-in')) as passes_into_box,
    count(*) filter (type = 'Pass' and pass_outcome is null and x < 80 and end_x >= 80) as passes_into_final_third,
    -- progression : passe réussie dans le jeu, hors des 40 % défensifs, qui rapproche le ballon
    -- du but d'au moins 10 yards, ou qui entre dans la surface
    count(*) filter (type = 'Pass' and pass_outcome is null and x >= 48
                     and coalesce(pass_type, '') not in ('Corner', 'Free Kick', 'Throw-in', 'Goal Kick', 'Kick Off')
                     and (d_start - d_end >= 10 or (ends_in_box and not starts_in_box))) as prog_passes,
    count(*) filter (type = 'Carry' and end_x >= 60
                     and (d_start - d_end >= 10 or (ends_in_box and not starts_in_box))) as prog_carries,
    count(*) filter (type = 'Dribble')                                                as dribbles,
    count(*) filter (type = 'Dribble' and dribble_outcome = 'Complete')               as dribbles_won,
    count(*) filter (type = 'Ball Receipt*' and starts_in_box and not receipt_incomplete)                        as receptions_in_box,
    -- défense
    count(*) filter (type = 'Duel' and duel_type = 'Tackle'
                     and duel_outcome in ('Won', 'Success In Play', 'Success Out'))   as tackles_won,
    count(*) filter (type = 'Interception'
                     and interception_outcome in ('Won', 'Success In Play', 'Success Out')) as interceptions,
    count(*) filter (type = 'Pressure')                                               as pressures,
    count(*) filter (type = 'Ball Recovery' and not recovery_failure)                 as recoveries,
    count(*) filter (type = 'Clearance')                                              as clearances,
    count(*) filter (type = 'Block')                                                  as blocks,
    count(*) filter (aerial_won)                                                      as aerials_won,
    count(*) filter (type = 'Duel' and duel_type = 'Aerial Lost')                     as aerials_lost,
    count(*) filter (type = 'Foul Committed')                                         as fouls,
    -- tentatives, pour les taux de réussite
    count(*) filter (type = 'Pass' and pass_cross)                                    as crosses,
    count(*) filter (type = 'Pass' and pass_cross and pass_outcome is null)           as crosses_completed,
    count(*) filter (type = 'Duel' and duel_type = 'Tackle')                          as tackles,
    max(coalesce(xa.xa, 0))                                                           as xa
from e
left join xa on xa.match_id = e.match_id and xa.player_id = e.player_id
group by 1, 2, 3;
