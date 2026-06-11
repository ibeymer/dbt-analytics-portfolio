{#
    One row per player per round, with player and tournament names plus the
    round's strokes, par, and score to par.
#}

with round_scores as (

    select * from {{ ref('stg_golf__round_scores') }}

),

players as (

    select * from {{ ref('stg_golf__players') }}

),

tournaments as (

    select * from {{ ref('stg_golf__tournaments') }}

)

select
    rs.tournament_id,
    t.tournament_name,
    t.season,
    rs.player_id,
    p.player_name,
    rs.round_number,
    rs.strokes,
    rs.round_par,
    rs.score_to_par
from round_scores rs
inner join players p on rs.player_id = p.player_id
inner join tournaments t on rs.tournament_id = t.tournament_id
