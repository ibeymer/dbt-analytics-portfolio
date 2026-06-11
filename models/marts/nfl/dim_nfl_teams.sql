with teams as (

    select * from {{ ref('stg_nfl__teams') }}

)

select
    team_id,
    abbreviation,
    display_name,
    location,
    nickname,
    conference,
    division
from teams
