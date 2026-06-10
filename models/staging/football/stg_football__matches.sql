with source as (

    select * from {{ ref('raw_football_matches') }}

),

renamed as (

    select
        cast(match_id as integer)      as match_id,
        season,
        cast(match_date as date)       as match_date,
        cast(home_team_id as integer)  as home_team_id,
        cast(away_team_id as integer)  as away_team_id,
        cast(home_goals as integer)    as home_goals,
        cast(away_goals as integer)    as away_goals,
        cast(attendance as integer)    as attendance

    from source

)

select * from renamed
