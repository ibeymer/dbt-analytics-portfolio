-- Completeness test: a stroke-play major runs four rounds, so every tournament
-- in the dataset must have all four round numbers represented in the scores.
-- Catches an incomplete extract (e.g. a tournament that wasn't finished yet).
-- A singular test passes when it returns zero rows.

select
    tournament_id,
    count(distinct round_number) as distinct_rounds
from {{ ref('stg_golf__round_scores') }}
group by tournament_id
having count(distinct round_number) != 4
