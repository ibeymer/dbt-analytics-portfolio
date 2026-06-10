with source as (

    select * from {{ ref('raw_golf_courses') }}

),

renamed as (

    select
        cast(course_id as integer) as course_id,
        course_name,
        location,
        cast(par as integer)       as par,
        cast(yardage as integer)   as yardage,
        cast(num_holes as integer) as num_holes

    from source

)

select * from renamed
