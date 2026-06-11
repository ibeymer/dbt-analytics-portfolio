with source as (

    select * from {{ ref('raw_golf_round_scores') }}

),

renamed as (

    select
        cast(tournament_id as bigint)   as tournament_id,
        cast(player_id as integer)      as player_id,
        cast(round_number as integer)   as round_number,
        cast(strokes as integer)        as strokes,
        cast(score_to_par as integer)   as score_to_par,
        -- par is the round's strokes minus its score relative to par
        cast(strokes as integer) - cast(score_to_par as integer) as round_par

    from source

)

select * from renamed
