import re

import pandas as pd
import requests
from unidecode import unidecode

from . import base_url

boxscore_dtypes = {
    'GAME_ID': 'str',
    'TEAM': 'str',
    'IS_HOME': 'bool',
    'PLAYER': 'str',
    'MP': 'float',
    'FG': 'float',
    'FGA': 'float',
    'FG_PERC': 'float',
    '3P': 'float',
    '3PA': 'float',
    '3P_PERC': 'float',
    'FT': 'float',
    'FTA': 'float',
    'FT_PERC': 'float',
    'ORB': 'float',
    'DRB': 'float',
    'TRB': 'float',
    'AST': 'float',
    'STL': 'float',
    'BLK': 'float',
    'TOV': 'float',
    'PF': 'float',
    'PTS': 'float',
    'PLUS_MINUS': 'float',
    'TS_PERC': 'float',
    'EFG_PERC': 'float',
    '3PAR': 'float',
    'FTR': 'float',
    'ORB_PERC': 'float',
    'DRB_PERC': 'float',
    'TRB_PERC': 'float',
    'AST_PERC': 'float',
    'STL_PERC': 'float',
    'BLK_PERC': 'float',
    'TOV_PERC': 'float',
    'USG_PERC': 'float',
    'ORTG': 'float',
    'DRTG': 'float',
    'BPM': 'float',
    'PTS_Q1': 'float',
    'PTS_Q2': 'float',
    'PTS_Q3': 'float',
    'PTS_Q4': 'float'}


def _parse_boxscore(html, table_name):
    """
    Parse and return basic boxscore stats for the specified table name

    Args:
        html (str): html page data to parse
        table_name (str): boxscore table name

    Returns:
        pd.DataFrame: pandas dataframe of raw boxscore data

    """
    df, = pd.read_html(html, attrs={'id': table_name})

    df.columns = df.columns.droplevel()

    df.rename({'Starters': 'PLAYER'}, axis=1, inplace=True)

    df['PLAYER'] = df.PLAYER.str.replace(
        'Team Totals', 'All').apply(lambda s: unidecode(s))

    df = df[df.PLAYER != 'Reserves']

    df.replace('Did Not Play', 'NaN', inplace=True)

    return df


def get_boxscore(game_id):
    """
    Team and player-level boxscore data for the specified `game_id`.
    Players are distinguished by the `player` column.
    Team level stats are listed under `player = 'All'`

    Args:
        game_id (str): unique game identifier

    Returns:
        pd.DataFrame: pandas dataframe of player and team-level boxscore stats

    """
    boxscore_url = f'{base_url}/boxscores/{game_id}.html'

    r = requests.get(boxscore_url)

    html = re.sub('(<!--)|(-->)', '', r.text, flags=re.DOTALL)

    # parse home and away team abbreviations
    df_line_score, = pd.read_html(html, attrs={'id': 'line_score'})
    df_scoring = df_line_score['Scoring']
    df_scoring = df_scoring[df_scoring.columns[:5]]
    df_scoring.columns = ['TEAM', 'PTS_Q1', 'PTS_Q2', 'PTS_Q3', 'PTS_Q4']
    df_scoring.insert(1, 'PLAYER', 'All')
    team_away, team_home = df_scoring.TEAM

    # parse basic boxscore stats
    df_bsc_home, df_bsc_away = [
        _parse_boxscore(html, f'box-{team}-game-basic')
        for team in [team_home, team_away]]

    df_bsc_home.insert(0, 'TEAM', team_home)
    df_bsc_away.insert(0, 'TEAM', team_away)
    df_bsc_home.insert(1, 'IS_HOME', True)
    df_bsc_away.insert(1, 'IS_HOME', False)

    df_bsc = pd.concat([
        df_bsc_home, df_bsc_away
    ], axis=0)

    # parse advanced boxscore stats
    df_adv_home, df_adv_away = [
        _parse_boxscore(html, f'box-{team}-game-advanced')
        for team in [team_home, team_away]]

    df_adv_home.insert(0, 'TEAM', team_home)
    df_adv_away.insert(0, 'TEAM', team_away)
    df_adv_home.insert(1, 'IS_HOME', True)
    df_adv_away.insert(1, 'IS_HOME', False)

    df_adv = pd.concat([
        df_adv_home, df_adv_away
    ], axis=0).drop(
        columns='MP'
    ).rename(
        {'Unnamed: 16_level_1': 'BPM'}, axis=1)

    # merge dataframes
    df_box = df_bsc.merge(
        df_adv, on=['TEAM', 'IS_HOME', 'PLAYER']
    ).merge(df_scoring, on=['TEAM', 'PLAYER'], how='left')
    df_box.insert(0, 'GAME_ID', game_id)
    df_box.columns = df_box.columns.str.replace('%', '_PERC').str.upper()
    df_box.rename({'+/-': 'PLUS_MINUS'}, axis=1, inplace=True)
    df_box.replace({
        'Player Suspended': 'NaN',
        'Did Not Dress': 'NaN',
        'Not With Team': 'NaN'
    }, inplace=True)

    # convert minutes to float representation
    elapsed = df_box.MP.str.split(':')
    whole_min = elapsed.str[0].astype(float)
    partial_min = (elapsed.str[1].astype(float) / 60.).fillna(0)
    df_box['MP'] = whole_min + partial_min

    # this field is occasionally missing
    if "BPM" not in df_box.columns:
        df_box.insert(38, "BPM", None)

    # enforce data types
    df_box = df_box[boxscore_dtypes.keys()].astype(boxscore_dtypes)

    # make all columns lower case
    df_box.columns = df_box.columns.str.lower()

    return df_box


if __name__ == '__main__':

    df = get_boxscore('202105190MEM')
    print(df)
