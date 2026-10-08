-- GOLD 25 — combien d'actions chaque joueur a faites à chaque poste.
-- Sert à vérifier qu'un joueur a vraiment tenu un rôle avant de le comparer aux joueurs de ce rôle.
create or replace table gold.player_positions as
select player_id, position, count(*) as n
from silver.events
where player_id is not null and position is not null and position <> 'Substitute' and period <= 4
group by 1, 2;
