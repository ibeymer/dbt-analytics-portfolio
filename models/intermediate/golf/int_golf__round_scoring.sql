{#
    One row per round, enriched with course par (to compute score-to-par) and
    hole-level aggregates (putts, greens in regulation, fairways hit). This is
    the analytical grain the golf scoring mart rolls up by player.
#}

with rounds as (

    select * from {{ ref('stg_golf__rounds') }}

),

courses as (

    select * from {{ ref('stg_golf__courses') }}

),

hole_scores as (

    select * from {{ ref('stg_golf__hole_scores') }}

),

hole_agg as (

    select
        round_id,
        count(*)                                            as holes_played,
        sum(putts)                                          as total_putts,
        sum(green_in_regulation)                            as greens_in_regulation,
        sum(case when fairway_hit = 1 then 1 else 0 end)    as fairways_hit,
        sum(case when fairway_hit is not null then 1 else 0 end)
                                                            as fairway_opportunities
    from hole_scores
    group by round_id

),

final as (

    select
        r.round_id,
        r.player_id,
        r.course_id,
        r.tournament,
        r.round_date,
        r.round_number,
        r.total_strokes,
        c.par                       as course_par,
        r.total_strokes - c.par     as score_to_par,
        h.holes_played,
        h.total_putts,
        h.greens_in_regulation,
        h.fairways_hit,
        h.fairway_opportunities
    from rounds r
    inner join courses c on r.course_id = c.course_id
    inner join hole_agg h on r.round_id = h.round_id

)

select * from final
