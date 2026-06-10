with source as (

    select * from {{ ref('raw_football_player_match_stats') }}

),

renamed as (

    select
        cast(stat_id as integer)        as stat_id,
        cast(match_id as integer)       as match_id,
        cast(player_id as integer)      as player_id,
        cast(minutes_played as integer) as minutes_played,
        cast(goals as integer)          as goals,
        cast(assists as integer)        as assists,
        cast(shots as integer)          as shots,
        cast(passes as integer)         as passes,
        cast(tackles as integer)        as tackles,
        cast(yellow_cards as integer)   as yellow_cards,
        cast(red_cards as integer)      as red_cards

    from source

)

select * from renamed
