{#
    Unpivot each game into two rows — one per team — with the result (W/L/T) and
    points scored / allowed from that team's perspective. This long grain is what
    the standings mart aggregates over.
#}

with games as (

    select * from {{ ref('stg_nfl__games') }}

),

home_side as (

    select
        game_id, season, week, game_date,
        home_team_id as team_id,
        away_team_id as opponent_id,
        home_score   as points_for,
        away_score   as points_against
    from games

),

away_side as (

    select
        game_id, season, week, game_date,
        away_team_id as team_id,
        home_team_id as opponent_id,
        away_score   as points_for,
        home_score   as points_against
    from games

),

unioned as (

    select * from home_side
    union all
    select * from away_side

),

final as (

    select
        *,
        points_for - points_against as point_differential,
        case
            when points_for > points_against then 'W'
            when points_for < points_against then 'L'
            else 'T'
        end as result
    from unioned

)

select * from final
