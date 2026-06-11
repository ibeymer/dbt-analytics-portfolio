with source as (

    select * from {{ ref('raw_nfl_teams') }}

),

renamed as (

    select
        cast(team_id as integer) as team_id,
        abbreviation,
        display_name,
        location,
        nickname,
        conference,
        division

    from source

)

select * from renamed
