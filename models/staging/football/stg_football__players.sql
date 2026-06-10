with source as (

    select * from {{ ref('raw_football_players') }}

),

renamed as (

    select
        cast(player_id as integer)    as player_id,
        cast(team_id as integer)      as team_id,
        full_name,
        position,
        country,
        cast(birth_date as date)      as birth_date,
        cast(shirt_number as integer) as shirt_number

    from source

)

select * from renamed
