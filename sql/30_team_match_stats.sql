-- GOLD 30 — une ligne par équipe et par match : résultat, buts attendus, style de jeu.
create or replace table gold.team_match_stats as
with e as (select * from silver.events where period <= 4),
side as (
    select match_id, home_team as team, away_team as opponent, home_score as goals_for, away_score as goals_against, true as is_home from silver.matches
    union all
    select match_id, away_team, home_team, away_score, home_score, false from silver.matches
),
agg as (
    select match_id, team,
        count(*) filter (type = 'Shot')                                              as shots,
        count(*) filter (type = 'Shot' and shot_outcome in ('Goal', 'Saved', 'Saved to Post')) as shots_on_target,
        coalesce(sum(shot_xg) filter (type = 'Shot'), 0)                             as xg,
        coalesce(sum(shot_xg) filter (type = 'Shot' and shot_type <> 'Penalty'), 0)  as npxg,
        count(*) filter (type = 'Shot' and shot_outcome = 'Goal')                    as goals_from_shots,
        count(*) filter (type = 'Own Goal For')                                      as own_goals_for,
        count(*) filter (type = 'Pass')                                              as passes,
        count(*) filter (type = 'Pass' and pass_outcome is null)                     as passes_completed,
        count(*) filter (type = 'Pass' and x >= 80)                                  as final_third_passes,
        count(*) filter (type = 'Pressure')                                          as pressures,
        -- pressing : passes tentées dans ses propres 60 % (sert au PPDA de l'adversaire)
        count(*) filter (type = 'Pass' and x <= 72)                                  as passes_own_60,
        -- actions défensives dans les 60 % offensifs : tacles, interceptions, fautes
        count(*) filter (x >= 48 and (type in ('Interception', 'Foul Committed')
                         or (type = 'Duel' and duel_type = 'Tackle')))                as def_actions_high
    from e group by 1, 2
)
select s.match_id, m.match_date, m.stage, s.team, s.opponent, s.is_home, s.goals_for, s.goals_against,
       a.shots, a.shots_on_target, a.xg, a.npxg, o.xg as xg_against, o.shots as shots_against,
       a.goals_from_shots + a.own_goals_for                         as goals_from_events,
       a.passes, a.passes_completed * 100.0 / a.passes              as pass_pct,
       a.passes * 100.0 / (a.passes + o.passes)                     as possession_pct,      -- part des passes du match
       a.final_third_passes * 100.0 / nullif(a.final_third_passes + o.final_third_passes, 0) as field_tilt_pct,
       o.passes_own_60 * 1.0 / nullif(a.def_actions_high, 0)        as ppda,                -- bas = pressing intense
       a.pressures
from side s
join silver.matches m using (match_id)
join agg a on a.match_id = s.match_id and a.team = s.team
join agg o on o.match_id = s.match_id and o.team = s.opponent;
