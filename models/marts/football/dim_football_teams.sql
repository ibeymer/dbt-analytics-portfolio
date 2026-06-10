with teams as (

    select * from {{ ref('stg_football__teams') }}

)

select
    team_id,
    team_name,
    city,
    founded_year,
    stadium,
    capacity
from teams
