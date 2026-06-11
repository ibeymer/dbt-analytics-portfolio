with source as (

    select * from {{ ref('raw_golf_players') }}

),

renamed as (

    select
        cast(player_id as integer) as player_id,
        player_name

    from source

)

select * from renamed
