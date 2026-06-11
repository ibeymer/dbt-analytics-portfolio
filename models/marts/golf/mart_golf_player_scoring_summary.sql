{#
    Player scoring profile across all tournaments in the dataset: scoring average
    (strokes per round), average score to par, rounds and tournaments played, cuts
    made, and best finish. Ranked by scoring average (lower is better). Minimum 4
    rounds played so small samples don't top the leaderboard.
#}

with scoring as (

    select * from {{ ref('int_golf__player_tournament_scoring') }}

),

players as (

    select * from {{ ref('stg_golf__players') }}

),

aggregated as (

    select
        player_id,
        count(distinct tournament_id)               as tournaments_played,
        sum(rounds_played)                          as rounds_played,
        sum(total_strokes)                          as total_strokes,
        sum(score_to_par)                           as cumulative_score_to_par,
        sum(case when made_cut then 1 else 0 end)   as cuts_made,
        min(finish_position)                        as best_finish
    from scoring
    group by player_id

)

select
    a.player_id,
    p.player_name,
    a.tournaments_played,
    a.rounds_played,
    a.cuts_made,
    a.best_finish,
    round({{ safe_divide('a.total_strokes', 'a.rounds_played') }}, 2)
        as scoring_average,
    round({{ safe_divide('a.cumulative_score_to_par', 'a.rounds_played') }}, 2)
        as avg_score_to_par_per_round,
    row_number() over (
        order by {{ safe_divide('a.total_strokes', 'a.rounds_played') }}
    ) as scoring_rank
from aggregated a
inner join players p on a.player_id = p.player_id
where a.rounds_played >= 4
order by scoring_rank
