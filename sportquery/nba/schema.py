from sqlalchemy import types

schedule_table = {
    'game_id': types.Text(),
    'game_number': types.Integer(),
    'datetime': types.DateTime(),
    'is_home': types.Boolean(),
    'team': types.Text(),
    'opponent': types.Text(),
    'outcome': types.Text(),
    'team_points': types.Integer(),
    'opponent_points': types.Integer(),
    'cumulative_wins': types.Integer(),
    'cumulative_losses': types.Integer(),
    'streak': types.Integer()}
