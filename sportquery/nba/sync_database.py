#!/usr/bin/env python3
import pandas as pd
import prefect
from prefect import Flow, Parameter, task
import sqlalchemy

from .. import cachedir
from .boxscore import get_boxscore
from .play_by_play import get_play_by_play
from .plus_minus import get_plus_minus
from .schedule import get_schedule
from .teams import get_teams

db_path = cachedir / 'nba.db'
db_path.parent.mkdir(parents=True, exist_ok=True)


@task
def initialize_database():
    """
    Establish a sqlite database engine and return a connection to the database.

    """
    engine = sqlalchemy.create_engine(f'sqlite:///{db_path.expanduser()}')

    metadata = sqlalchemy.MetaData()

    sqlalchemy.Table(
        'schedule', metadata,
        sqlalchemy.Column('game_id', sqlalchemy.types.Text),
        sqlalchemy.Column('season', sqlalchemy.types.Integer),
        sqlalchemy.Column('game_number', sqlalchemy.types.Integer),
        sqlalchemy.Column('datetime', sqlalchemy.types.DateTime),
        sqlalchemy.Column('is_home', sqlalchemy.types.Boolean),
        sqlalchemy.Column('team', sqlalchemy.types.Text),
        sqlalchemy.Column('opponent', sqlalchemy.types.Text),
        sqlalchemy.Column('outcome', sqlalchemy.types.Text),
        sqlalchemy.Column('team_points', sqlalchemy.types.Integer),
        sqlalchemy.Column('opponent_points', sqlalchemy.types.Integer),
        sqlalchemy.Column('cumulative_wins', sqlalchemy.types.Integer),
        sqlalchemy.Column('cumulative_losses', sqlalchemy.types.Integer),
        sqlalchemy.Column('streak', sqlalchemy.types.Integer),
        sqlalchemy.UniqueConstraint('game_id', 'team'))

    sqlalchemy.Table(
        'boxscore', metadata,
        sqlalchemy.Column('game_id', sqlalchemy.types.Text),
        sqlalchemy.Column('team', sqlalchemy.types.Text),
        sqlalchemy.Column('is_home', sqlalchemy.types.Boolean),
        sqlalchemy.Column('player', sqlalchemy.types.Text),
        sqlalchemy.Column('mp', sqlalchemy.types.Integer),
        sqlalchemy.Column('fg', sqlalchemy.types.Integer),
        sqlalchemy.Column('fga', sqlalchemy.types.Integer),
        sqlalchemy.Column('fg_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('3p', sqlalchemy.types.Integer),
        sqlalchemy.Column('3pa', sqlalchemy.types.Integer),
        sqlalchemy.Column('3p_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('ft', sqlalchemy.types.Integer),
        sqlalchemy.Column('fta', sqlalchemy.types.Integer),
        sqlalchemy.Column('ft_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('orb', sqlalchemy.types.Integer),
        sqlalchemy.Column('drb', sqlalchemy.types.Integer),
        sqlalchemy.Column('trb', sqlalchemy.types.Integer),
        sqlalchemy.Column('ast', sqlalchemy.types.Integer),
        sqlalchemy.Column('stl', sqlalchemy.types.Integer),
        sqlalchemy.Column('blk', sqlalchemy.types.Integer),
        sqlalchemy.Column('tov', sqlalchemy.types.Integer),
        sqlalchemy.Column('pf', sqlalchemy.types.Integer),
        sqlalchemy.Column('pts', sqlalchemy.types.Integer),
        sqlalchemy.Column('plus_minus', sqlalchemy.types.Integer),
        sqlalchemy.Column('ts_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('efg_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('3par', sqlalchemy.types.Float),
        sqlalchemy.Column('ftr', sqlalchemy.types.Float),
        sqlalchemy.Column('orb_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('drb_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('trb_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('ast_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('stl_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('blk_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('tov_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('usg_perc', sqlalchemy.types.Float),
        sqlalchemy.Column('ortg', sqlalchemy.types.Float),
        sqlalchemy.Column('drtg', sqlalchemy.types.Float),
        sqlalchemy.Column('bpm', sqlalchemy.types.Float),
        sqlalchemy.Column('pts_q1', sqlalchemy.types.Float),
        sqlalchemy.Column('pts_q2', sqlalchemy.types.Float),
        sqlalchemy.Column('pts_q3', sqlalchemy.types.Float),
        sqlalchemy.Column('pts_q4', sqlalchemy.types.Float))

    sqlalchemy.Table(
        'plus_minus', metadata,
        sqlalchemy.Column('game_id', sqlalchemy.types.Text),
        sqlalchemy.Column('player', sqlalchemy.types.Text),
        sqlalchemy.Column('subin_minute', sqlalchemy.types.Float),
        sqlalchemy.Column('subout_minute', sqlalchemy.types.Float),
        sqlalchemy.Column('plus_minus', sqlalchemy.types.Integer))

    sqlalchemy.Table(
        'play_by_play', metadata,
        sqlalchemy.Column('game_id', sqlalchemy.types.Text),
        sqlalchemy.Column('time', sqlalchemy.types.Text),
        sqlalchemy.Column('quarter', sqlalchemy.types.Integer),
        sqlalchemy.Column('city', sqlalchemy.types.Text),
        sqlalchemy.Column('is_home', sqlalchemy.types.Text),
        sqlalchemy.Column('score', sqlalchemy.types.Text),
        sqlalchemy.Column('event', sqlalchemy.types.Text),
        sqlalchemy.Column('points', sqlalchemy.types.Integer))

    metadata.create_all(engine)

    return engine


@task
def update_schedules(conn, current_season, start_season=2003):
    """
    Iterate over all seasons from `start_season` to `current_season` inclusive
    and pull team schedules. The schedules for the latest season in the
    database are dropped and repopulated.

    Args:
        conn (sqlalchemy.engine.base.Engine): sqlalchemy engine connection
        current_season (int): year of the last season to pull data for
        start_season (int, optional): year of the first season to pull data for

    Returns:
        pd.DataFrame: pandas dataframe containing the `game_id` of all
            completed games

    """
    logger = prefect.context.get('logger')

    start_season = pd.read_sql(
        'select max(season) from schedule', conn
    ).squeeze() or start_season

    logger.info(f'latest season = {start_season}, dropping and updating...')
    conn.execute(f'delete from schedule where season == {start_season}')

    for season in range(start_season, current_season + 1):
        for team in get_teams(season):
            logger.info(f'syncing schedule: {season} {team}')
            schedule = get_schedule(team, season)
            schedule.insert(1, 'season', season)
            schedule.to_sql('schedule', conn, if_exists='append', index=False)

    completed_games = pd.read_sql(
        'select distinct game_id from schedule where outcome is not null', conn)

    return completed_games.game_id


@task
def update_boxscores(conn, game_ids):
    """
    Pull basic and advanced boxscore numbers at the player and team level
    for the specified NBA games and perist to the database.

    Args:
        conn (sqlalchemy.engine.base.Engine): sqlalchemy engine connection
        game_ids (pd.Series): unique game identifiers to pull boxscore stats for

    Returns:
        None

    """
    recorded_game_ids = pd.read_sql(
        'select distinct game_id from boxscore', conn
    ).squeeze()

    unrecorded_game_ids = game_ids[~game_ids.isin(recorded_game_ids)]

    logger = prefect.context.get('logger')

    for game_id in unrecorded_game_ids.values:
        logger.info(f'syncing {game_id}')
        boxscore = get_boxscore(game_id)
        boxscore.to_sql('boxscore', conn, if_exists='append', index=False)


@task
def update_plus_minus(conn, game_ids):
    """
    Pull individual player plus-minus for all substitutions over the course
    of the specified NBA games and persist to the database.

    Args:
        conn (sqlalchemy.engine.base.Engine): sqlalchemy engine connection
        game_ids (pd.Series): unique game identifiers to pull boxscore stats for

    Returns:
        None

    """
    recorded_game_ids = pd.read_sql(
        'select distinct game_id from plus_minus', conn
    ).squeeze()

    unrecorded_game_ids = game_ids[~game_ids.isin(recorded_game_ids)]

    logger = prefect.context.get('logger')

    for game_id in unrecorded_game_ids.values:
        logger.info(f'syncing {game_id}')
        plus_minus = get_plus_minus(game_id)
        plus_minus.to_sql('plus_minus', conn, if_exists='append', index=False)


@task
def update_play_by_play(conn, game_ids):
    """
    Pull individual play descriptions and score data over the course
    of the specified NBA games and persist to the database.

    Args:
        conn (sqlalchemy.engine.base.Engine): sqlalchemy engine connection
        game_ids (pd.Series): unique game identifiers to pull boxscore stats for

    Returns:
        None

    """
    recorded_game_ids = pd.read_sql(
        'select distinct game_id from play_by_play', conn
    ).squeeze()

    unrecorded_game_ids = game_ids[~game_ids.isin(recorded_game_ids)]

    logger = prefect.context.get('logger')

    for game_id in unrecorded_game_ids.values:
        logger.info(f'syncing {game_id}')
        play_by_play = get_play_by_play(game_id)
        play_by_play.to_sql('play_by_play', conn, if_exists='append',
                            index=False)


with Flow('sync NBA database') as flow:
    current_season = Parameter('current_season', default=2021)
    conn = initialize_database()
    game_ids = update_schedules(conn, current_season)
    update_boxscores(conn, game_ids)
    update_plus_minus(conn, game_ids)
    update_play_by_play(conn, game_ids)

if __name__ == '__main__':
    flow.run(current_season=2021)
