with source as (

    select * from {{ ref('raw_golf_results') }}

),

renamed as (

    select
        cast(tournament_id as bigint)    as tournament_id,
        cast(player_id as integer)       as player_id,
        cast(finish_position as integer) as finish_position,
        cast(total_strokes as integer)   as total_strokes,
        cast(total_to_par as integer)    as total_to_par

    from source

)

select * from renamed
