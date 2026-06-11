with players as (

    select * from {{ ref('stg_golf__players') }}

)

select
    player_id,
    player_name
from players
