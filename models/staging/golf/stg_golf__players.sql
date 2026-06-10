with source as (

    select * from {{ ref('raw_golf_players') }}

),

renamed as (

    select
        cast(player_id as integer)        as player_id,
        full_name,
        country,
        cast(turned_pro_year as integer)  as turned_pro_year,
        handedness

    from source

)

select * from renamed
