import re
import requests

import pandas as pd
from unidecode import unidecode

from .schema import boxscore_dtypes
from . import base_url


def _parse_boxscore(html, table_name):
    """
    Parse and return basic boxscore stats for the specified team
    abbreviation.

    """
    df, = pd.read_html(html, attrs={'id': table_name})

    df.columns = df.columns.droplevel()

    df.rename({'Starters': 'PLAYER'}, axis=1, inplace=True)

    df['PLAYER'] = df.PLAYER.str.replace(
        'Team Totals', 'All').apply(lambda s: unidecode(s))

    df = df[df.PLAYER != 'Reserves']

    df.replace('Did Not Play', 'NaN', inplace=True)

    return df


def boxscore(game_id):
    """
    Boxscore data for the specified `game_id`.

    """
    boxscore_url = f'{base_url}/boxscores/{game_id}.html'

    r = requests.get(boxscore_url)

    html = re.sub('(<!--)|(-->)', '', r.text, flags=re.DOTALL)

    # parse home and away team abbreviations
    df_line_score, = pd.read_html(html, attrs={'id': 'line_score'})
    df_scoring = df_line_score['Scoring'].drop(columns='T')
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
    ], axis=0).drop(columns='MP')

    # merge dataframes
    df_box = df_bsc.merge(
        df_adv, on=['TEAM', 'IS_HOME', 'PLAYER']
    ).merge(df_scoring, on=['TEAM', 'PLAYER'], how='left')
    df_box.insert(0, 'GAME_ID', game_id)
    df_box.columns = df_box.columns.str.replace('%', '_PERC').str.upper()
    df_box.rename({'+/-': 'PLUS_MINUS'}, axis=1, inplace=True)

    # convert minutes to float representation
    elapsed = df_box.MP.str.split(':')
    whole_min = elapsed.str[0].astype(float)
    partial_min = (elapsed.str[1].astype(float) / 60.).fillna(0)
    df_box['MP'] = whole_min + partial_min

    # enforce data types
    df_box = df_box.astype(boxscore_dtypes)
    print(df_box.head(14).T.to_string())



if __name__ == '__main__':
    boxscore('201810210CLE')
