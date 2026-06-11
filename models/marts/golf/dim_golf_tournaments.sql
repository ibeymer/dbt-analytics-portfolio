with tournaments as (

    select * from {{ ref('stg_golf__tournaments') }}

)

select
    tournament_id,
    tournament_name,
    season,
    end_date
from tournaments
