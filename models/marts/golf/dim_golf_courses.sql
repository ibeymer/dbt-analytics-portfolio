with courses as (

    select * from {{ ref('stg_golf__courses') }}

)

select
    course_id,
    course_name,
    location,
    par,
    yardage,
    num_holes
from courses
