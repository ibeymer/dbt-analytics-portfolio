-- Ad-hoc analysis (compiled by `dbt compile`, not materialized).
-- Cross-domain "best performers" pull: the league's top scorer alongside the
-- lowest scoring-average golfer.

with top_scorer as (
    select
        'football'                as sport,
        full_name                 as performer,
        team_name                 as affiliation,
        goals                     as headline_metric,
        'goals'                   as metric_name
    from {{ ref('mart_football_player_season_summary') }}
    order by goals desc
    limit 1
),

best_golfer as (
    select
        'golf'                    as sport,
        full_name                 as performer,
        country                   as affiliation,
        scoring_average           as headline_metric,
        'scoring average'         as metric_name
    from {{ ref('mart_golf_player_scoring_summary') }}
    order by scoring_average asc
    limit 1
)

select * from top_scorer
union all
select * from best_golfer
