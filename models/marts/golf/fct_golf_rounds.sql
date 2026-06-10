{#
    One row per round played, with player and course names plus the round-level
    scoring metrics derived in the intermediate layer.
#}

with round_scoring as (

    select * from {{ ref('int_golf__round_scoring') }}

),

players as (

    select * from {{ ref('stg_golf__players') }}

),

courses as (

    select * from {{ ref('stg_golf__courses') }}

)

select
    rs.round_id,
    rs.player_id,
    pl.full_name                as player_name,
    rs.course_id,
    c.course_name,
    rs.tournament,
    rs.round_date,
    rs.round_number,
    rs.total_strokes,
    rs.course_par,
    rs.score_to_par,
    rs.total_putts,
    rs.greens_in_regulation,
    rs.fairways_hit,
    rs.fairway_opportunities,
    round({{ pct('rs.greens_in_regulation', 'rs.holes_played') }}, 1)
        as gir_pct,
    round({{ pct('rs.fairways_hit', 'rs.fairway_opportunities') }}, 1)
        as fairway_pct
from round_scoring rs
inner join players pl on rs.player_id = pl.player_id
inner join courses c on rs.course_id = c.course_id
