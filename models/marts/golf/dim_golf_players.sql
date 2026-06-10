with players as (

    select * from {{ ref('stg_golf__players') }}

)

select
    player_id,
    full_name,
    country,
    turned_pro_year,
    handedness
from players
