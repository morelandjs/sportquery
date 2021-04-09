NBA Basketball
==============

The NBA database includes the following tables:
  * **schedule**: game schedule for each team and season
  * **boxscore**: player and team level boxscore statistics
  * **play_by_play**: a description of every play in each game
  * **plus_minus**: player level substitutions and plus-minus contributions

Table schemas are described below.

schedule table
--------------

game_id (str):
  Unique game identifier. This column is a useful key to join stats contained
  in different tables.
season (int):
  NBA season year
game_number (int):
  Season game number counter (typically in range 1-82)
datetime (str):
  Scheduled tipoff timestamp. This column follows python datetime formatting.
is_home (int);
  Equals 1 if the team is playing at home, 0 otherwise.
team (str):
  NBA team abbreviation
opponent (str):
  NBA opponent abbreviation
outcome (str):
  Equal to 'W' if the team won or 'L' if the team lost
team_points (int):
  Total points scored by the team of interest
opponent_points (int):
  Total points scored by the team's opponent
cumulative_wins (int):
  Total number of wins upto and including this game
cumulative_losses (int):
  Total number of losses upto and including to this game
streak (int);
  Total number of consecutive wins or losses upto and including this game
phase (str):
  Season phase (regular or post)

boxscore table
--------------

game_id (str):
  Unique game identifier. This column is a useful key to join stats contained
  in different tables.
team (str):
  NBA team abbreviation
is_home (int):
  Equals 1 if the team is playing at home, 0 otherwise.
player (str):
  Name of the player for which the boxscore stats are tabulated. If the player
  field equals "All", the row contains aggregate statistics for all players on the
  team.
mp (float):
  Minutes played. For example 1.5 indicates one minute and thirty seconds.
fg (int):
  Field goals made
fga (int):
  Field goals attempted
fg_perc (float):
  Field goal percentage
3p (int):
  Three pointers made
3pa (int):
  Three pointers attempted
3p_perc (float):
  Three point percentage
ft (int):
  Free throws made
fta (int):
  Free throws attempted
ft_perc (int):
  Free throw percentage
orb (int):
  Offensive rebounds
drb (int):
  Deffensive rebounds
trb (int):
  Total rebounds
ast (int):
  Assists
stl (int):
  Steals
blk (int):
  Blocks
tov (int):
  Turnovers
pf (int):
  Personal fouls
pts (int):
  Points scored
plus_minus (int):
  Plus-minus contribution
ts_perc (float):
  True shooting percentage. A measure of shooting efficiency that takes into
  account two-point field goals, three-point field goals, and free throws.
efg_perc (float):
  Effective field goal percentage. This statistic adjusts for the fact that a
  three-point field goal is worth more than a two-point field goal.
3par (float):
  Three point attempt rate
ftr (float):
  Free throw attempt rate.
orb_perc (float):
  Offensive rebound percentage. An estimate of the percentage of available
  offensive rebounds a player grabbed while they were on the floor.
drb_perc (float):
  Deffensive rebound percentage. An estimate of the percentage of available
  defensive rebounds a player grabbed while they were on the floor.
trb_perc (float):
  Total rebound percentage. An estimate of the percentage of available rebounds
  a player grabbed while they were on the floor.
ast_perc (float):
  Assist percentage. An estimate of the percentage of team field goals a player
  assisted while they were on the floor.
stl_perc (float):
  Steal percentage. An estimate of the percentage of opponent possessions that
  end with a steal by the player while they were on the floor.
blk_perc (float):
  Block percentage. An estimate of the percentage of opponent two-point field
  goal attempts blocked by the player while they were on the floor.
tov_perc (float):
  Turnover percentage. An estimate of turnovers committed per 100 plays.
usg_perc (float):
  Usage percentage. A estimate of the percentage of team plays used by a player
  while they were on the floor.
ortg (float):
  An estimate of points produced (players) or scored (teams) per 100
  possessions.
drtg (float):
  A estimate of points allowed per 100 possessions.
bpm (float):
  Box plus-minus. A boxscore estimate of the points per 100 possessions a player
  contributed above a league-average player, translated to an average team.
pts_q1 (int):
  Points scored in the first quarter
pts_q2 (int):
  Points scored in the second quarter
pts_q3 (int):
  Points scored in the third quarter
pts_q4 (int):
  Points scored in the fourth quarter

play_by_play table
------------------

game_id (str):
  Unique game identifier. This column is a useful key to join stats contained
  in different tables.
time (str):
  Time remaining in the quarter when the play occured.
quarter (int):
  Quarter of the game when the play occured.
city (str):
  Ciy of the team with possession of the ball when the play occured (proxy for
  team).
is_home (int):
  Equals 1 if the team (city field) is playing at home, 0 otherwise.
score (str):
  Dash separated boxscore. Includes any points scored on the current play.
event (str):
  A text description of the play that occured.
points (int):
  Points that were scored on this play.

plus_minus table
----------------

game_id (str):
  Unique game identifier. This column is a useful key to join stats contained
  in different tables.
player (str):
  Name of the player for which the plus-minus contribution is tabulated.
subin_minute (float):
  Minutes of game time that had elapsed when the player was substituted into the
  game. For example 10.5 minutes, mean the player was substituted into the game
  after 10 minutes and 30 seconds played.
subout_minute (float):
  Same as above but for the time the player subbed out of the game.
plus_minus (int):
  Point differential that occurred during this particular player substitution
  interval.
