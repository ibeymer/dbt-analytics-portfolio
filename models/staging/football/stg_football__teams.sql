with source as (

    select * from {{ ref('raw_football_teams') }}

),

renamed as (

    select
        cast(team_id as integer)      as team_id,
        team_name,
        city,
        cast(founded_year as integer) as founded_year,
        stadium,
        cast(capacity as integer)     as capacity

    from source

)

select * from renamed
