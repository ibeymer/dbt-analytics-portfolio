{#
    Unpivot each match into two rows — one per team — with result, points, and
    goal columns from that team's perspective. This "long" grain is what the
    league-standings mart aggregates over.
#}

with matches as (

    select * from {{ ref('stg_football__matches') }}

),

home_side as (

    select
        match_id,
        season,
        match_date,
        'home'         as venue,
        home_team_id   as team_id,
        away_team_id   as opponent_id,
        home_goals     as goals_for,
        away_goals     as goals_against
    from matches

),

away_side as (

    select
        match_id,
        season,
        match_date,
        'away'         as venue,
        away_team_id   as team_id,
        home_team_id   as opponent_id,
        away_goals     as goals_for,
        home_goals     as goals_against
    from matches

),

unioned as (

    select * from home_side
    union all
    select * from away_side

),

final as (

    select
        *,
        goals_for - goals_against as goal_difference,
        case
            when goals_for > goals_against then 'W'
            when goals_for = goals_against then 'D'
            else 'L'
        end as result,
        case
            when goals_for > goals_against then 3
            when goals_for = goals_against then 1
            else 0
        end as points
    from unioned

)

select * from final
