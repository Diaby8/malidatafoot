-- GOLD 20 — une ligne par joueur sur le tournoi : totaux, temps de jeu, valeurs par 90 minutes.
create or replace table gold.player_tournament as
with pos as (   -- poste principal : celui où le joueur a le plus d'événements
    select player_id, position, row_number() over (partition by player_id order by count(*) desc) as rk
    from silver.events
    where player_id is not null and position is not null and position <> 'Substitute' and period <= 4
    group by 1, 2
),
mins as (
    select player_id, team, sum(minutes) as minutes, count(*) as matches, sum(started::int) as starts
    from silver.player_match_minutes group by 1, 2
),
tot as (
    select player_id,
           sum(shots) shots, sum(shots_on_target) shots_on_target, sum(goals) goals, sum(np_goals) np_goals,
           sum(xg) xg, sum(npxg) npxg, sum(xa) xa, sum(passes) passes, sum(passes_completed) passes_completed,
           sum(key_passes) key_passes, sum(assists) assists, sum(passes_into_box) passes_into_box,
           sum(passes_into_final_third) passes_into_final_third, sum(prog_passes) prog_passes,
           sum(prog_carries) prog_carries, sum(dribbles) dribbles, sum(dribbles_won) dribbles_won,
           sum(receptions_in_box) receptions_in_box, sum(tackles_won) tackles_won,
           sum(interceptions) interceptions, sum(pressures) pressures, sum(recoveries) recoveries,
           sum(clearances) clearances, sum(blocks) blocks, sum(aerials_won) aerials_won,
           sum(aerials_lost) aerials_lost, sum(fouls) fouls,
           sum(crosses) crosses, sum(crosses_completed) crosses_completed, sum(tackles) tackles
    from gold.player_match_stats group by 1
)
select
    m.player_id, pl.display_name as player, m.team, p.position,
    case when p.position = 'Goalkeeper' then 'GAR'
         when p.position like '%Back%' then 'DEF'
         when p.position like '%Midfield%' then 'MIL'
         else 'ATT' end                                   as pos_group,
    m.minutes, m.matches, m.starts,
    m.minutes / max(m.minutes) over (partition by m.team)  as minutes_share,  -- part du temps de jeu max de son équipe
    t.* exclude (player_id),
    t.npxg * 90 / m.minutes                               as npxg_p90,
    t.np_goals * 90 / m.minutes                           as np_goals_p90,
    t.shots * 90 / m.minutes                              as shots_p90,
    t.xa * 90 / m.minutes                                 as xa_p90,
    t.key_passes * 90 / m.minutes                         as key_passes_p90,
    t.passes_into_box * 90 / m.minutes                    as passes_into_box_p90,
    t.prog_passes * 90 / m.minutes                        as prog_passes_p90,
    t.prog_carries * 90 / m.minutes                       as prog_carries_p90,
    t.dribbles_won * 90 / m.minutes                       as dribbles_won_p90,
    (t.tackles_won + t.interceptions) * 90 / m.minutes    as tackles_interceptions_p90,
    t.pressures * 90 / m.minutes                          as pressures_p90,
    t.recoveries * 90 / m.minutes                         as recoveries_p90,
    t.aerials_won * 90 / m.minutes                        as aerials_won_p90,
    t.receptions_in_box * 90 / m.minutes                  as receptions_in_box_p90,
    t.passes_into_final_third * 90 / m.minutes            as passes_final_third_p90,
    t.clearances * 90 / m.minutes                         as clearances_p90,
    t.blocks * 90 / m.minutes                             as blocks_p90,
    t.passes_completed * 100.0 / nullif(t.passes, 0)      as pass_pct
from mins m
join tot t using (player_id)
join silver.players pl using (player_id)
left join pos p on p.player_id = m.player_id and p.rk = 1
where m.minutes > 0;
