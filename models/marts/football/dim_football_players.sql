with players as (

    select * from {{ ref('stg_football__players') }}

),

teams as (

    select * from {{ ref('stg_football__teams') }}

)

select
    p.player_id,
    p.full_name,
    p.position,
    p.country,
    p.birth_date,
    date_diff('year', p.birth_date, current_date) as age,
    p.shirt_number,
    p.team_id,
    t.team_name
from players p
left join teams t on p.team_id = t.team_id
