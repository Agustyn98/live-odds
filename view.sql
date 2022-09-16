SELECT team1, team2, time, team1_score, team2_score, team1_odds, draw_odds, team2_odds FROM
(
SELECT team1, team2,
time,
ROW_NUMBER() OVER(partition by time, team1, team2) as r, 
team1_score, team2_score,
team1_odds * 100 / total as team1_odds, 
draw_odds * 100 / total as draw_odds, 
team2_odds * 100 / total as team2_odds,
FROM (
  SELECT team1, team2, time, team1_score, team2_score,
  (1 / team1_odds  ) as team1_odds,
  (1 / draw_odds )  as draw_odds,
  (1 / team2_odds  )  as team2_odds,
  (1 / team1_odds + 1 / draw_odds + 1 / team2_odds) as total
  FROM `marine-bison-360321.betting_dataset.match_bets2`
  WHERE datetime >= CAST ( FORMAT_DATE("%Y%m%d", CURRENT_DATE() - 1) as INT64 )
  )
) 
WHERE r = 1
ORDER BY team1, team2, time
