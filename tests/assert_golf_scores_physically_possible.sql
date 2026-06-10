-- Business-rule test: a golfer cannot take fewer than one stroke per hole, so a
-- round's total strokes must be at least the number of holes played.
-- A singular test passes when it returns zero rows.

select
    round_id,
    total_strokes,
    holes_played
from {{ ref('int_golf__round_scoring') }}
where total_strokes < holes_played
