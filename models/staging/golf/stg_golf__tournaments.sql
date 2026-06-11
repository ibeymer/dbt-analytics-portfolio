with source as (

    select * from {{ ref('raw_golf_tournaments') }}

),

renamed as (

    select
        cast(tournament_id as bigint) as tournament_id,
        tournament_name,
        cast(season as integer)       as season,
        cast(end_date as date)        as end_date

    from source

)

select * from renamed
