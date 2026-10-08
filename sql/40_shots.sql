-- GOLD 40 — tous les tirs, prêts à tracer (hors séances de tirs au but).
create or replace table gold.shots as
select e.match_id, m.match_date, e.team, p.display_name as player, e.player_id, e.period, e.minute, e.t_match,
       e.x, e.y, e.shot_xg as xg, e.shot_outcome as outcome, e.shot_type, e.shot_body_part as body_part,
       e.play_pattern, (e.shot_outcome = 'Goal') as is_goal
from silver.events_clock e
join silver.matches m using (match_id)
left join silver.players p using (player_id)
where e.type = 'Shot';
