with source as (

    select * from {{ ref('raw_golf_rounds') }}

),

renamed as (

    select
        cast(round_id as integer)      as round_id,
        cast(player_id as integer)     as player_id,
        cast(course_id as integer)     as course_id,
        tournament,
        cast(round_date as date)       as round_date,
        cast(round_number as integer)  as round_number,
        cast(total_strokes as integer) as total_strokes

    from source

)

select * from renamed
