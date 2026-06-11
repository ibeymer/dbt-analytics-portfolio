{#
    One row per player per tournament: round-level scores rolled up to the
    tournament grain (rounds played, total strokes, cumulative score to par),
    joined to the finishing result. This is the reusable grain the player
    scoring-summary mart aggregates across tournaments.
#}

with round_scores as (

    select * from {{ ref('stg_golf__round_scores') }}

),

results as (

    select * from {{ ref('stg_golf__results') }}

),

round_agg as (

    select
        tournament_id,
        player_id,
        count(*)            as rounds_played,
        sum(strokes)        as total_strokes,
        sum(score_to_par)   as score_to_par,
        avg(strokes)        as avg_strokes_per_round
    from round_scores
    group by tournament_id, player_id

)

select
    ra.tournament_id,
    ra.player_id,
    ra.rounds_played,
    ra.total_strokes,
    ra.score_to_par,
    ra.avg_strokes_per_round,
    r.finish_position,
    -- a player who completed all four rounds was not cut
    ra.rounds_played = 4 as made_cut
from round_agg ra
left join results r
    on ra.tournament_id = r.tournament_id
    and ra.player_id = r.player_id
