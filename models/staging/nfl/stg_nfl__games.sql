with source as (

    select * from {{ ref('raw_nfl_games') }}

),

renamed as (

    select
        cast(game_id as bigint)       as game_id,
        cast(season as integer)       as season,
        cast(week as integer)         as week,
        cast(game_date as date)       as game_date,
        cast(home_team_id as integer) as home_team_id,
        cast(away_team_id as integer) as away_team_id,
        cast(home_score as integer)   as home_score,
        cast(away_score as integer)   as away_score

    from source

)

select * from renamed
