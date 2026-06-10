{#
    Career-to-date scoring profile per golfer: scoring average, average score to
    par, and the headline strokes-gained-style rates (GIR%, fairway%, putts per
    round). Ranked by scoring average (lower is better).
#}

with round_scoring as (

    select * from {{ ref('int_golf__round_scoring') }}

),

players as (

    select * from {{ ref('stg_golf__players') }}

),

aggregated as (

    select
        player_id,
        count(*)                    as rounds_played,
        sum(total_strokes)          as total_strokes,
        sum(score_to_par)           as cumulative_score_to_par,
        sum(total_putts)            as total_putts,
        sum(greens_in_regulation)   as total_gir,
        sum(holes_played)           as total_holes,
        sum(fairways_hit)           as total_fairways_hit,
        sum(fairway_opportunities)  as total_fairway_opportunities
    from round_scoring
    group by player_id

)

select
    a.player_id,
    p.full_name,
    p.country,
    a.rounds_played,
    round({{ safe_divide('a.total_strokes', 'a.rounds_played') }}, 2)
        as scoring_average,
    round({{ safe_divide('a.cumulative_score_to_par', 'a.rounds_played') }}, 2)
        as avg_score_to_par,
    round({{ safe_divide('a.total_putts', 'a.rounds_played') }}, 2)
        as putts_per_round,
    round({{ pct('a.total_gir', 'a.total_holes') }}, 1)
        as gir_pct,
    round({{ pct('a.total_fairways_hit', 'a.total_fairway_opportunities') }}, 1)
        as fairway_pct,
    row_number() over (
        order by {{ safe_divide('a.total_strokes', 'a.rounds_played') }}
    ) as scoring_rank
from aggregated a
inner join players p on a.player_id = p.player_id
order by scoring_rank
