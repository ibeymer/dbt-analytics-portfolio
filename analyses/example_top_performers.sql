-- Ad-hoc analysis (compiled by `dbt compile`, not materialized).
-- Cross-domain "best performers" pull: the NFL's best team by win pct alongside
-- the golfer with the lowest scoring average.

with best_nfl_team as (
    select
        'nfl'                     as sport,
        display_name              as performer,
        division                  as affiliation,
        win_pct                   as headline_metric,
        'win pct'                 as metric_name
    from {{ ref('mart_nfl_standings') }}
    order by win_pct desc, point_differential desc
    limit 1
),

best_golfer as (
    select
        'golf'                    as sport,
        player_name               as performer,
        cast(best_finish as varchar) as affiliation,
        scoring_average           as headline_metric,
        'scoring average'         as metric_name
    from {{ ref('mart_golf_player_scoring_summary') }}
    order by scoring_average asc
    limit 1
)

select * from best_nfl_team
union all
select * from best_golfer
