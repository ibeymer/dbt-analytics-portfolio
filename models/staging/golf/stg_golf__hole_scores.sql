with source as (

    select * from {{ ref('raw_golf_hole_scores') }}

),

renamed as (

    select
        cast(score_id as integer)            as score_id,
        cast(round_id as integer)            as round_id,
        cast(hole_number as integer)         as hole_number,
        cast(par as integer)                 as par,
        cast(strokes as integer)             as strokes,
        cast(fairway_hit as integer)         as fairway_hit,          -- null on par 3s
        cast(green_in_regulation as integer) as green_in_regulation,
        cast(putts as integer)               as putts

    from source

)

select * from renamed
