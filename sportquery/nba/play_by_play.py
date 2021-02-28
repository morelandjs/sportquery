import re

import pandas as pd
import requests

from . import base_url


def get_play_by_play(game_id):
    """
    Text description and current score of all plays in `game_id`.

    Args:
        game_id (str): unique game identifier

    Returns:
        pd.DataFrame: pandas dataframe of individual game plays

    """
    plus_minus_url = f'{base_url}/boxscores/pbp/{game_id}.html'

    r = requests.get(plus_minus_url)

    html = re.sub('(<!--)|(-->)', '', r.text, flags=re.DOTALL)

    df, = pd.read_html(html, attrs={'id': 'pbp'})

    df = df['1st Q']
    team_away = df.columns[1]
    team_home = df.columns[5]

    df.columns = [
        'time',
        'team_away',
        'points_away',
        'score',
        'points_home',
        'team_home']

    # away team events
    df_away = df[['time', 'score', 'team_away', 'points_away']].copy()
    df_away.rename(columns={
        'team_away': 'event', 'points_away': 'points'}, inplace=True)
    df_away.insert(1, 'city', team_away)
    df_away.insert(2, 'is_home', 0)

    # home team events
    df_home = df[['time', 'score', 'team_home', 'points_home']].copy()
    df_home.rename(columns={
        'team_home': 'event', 'points_home': 'points'}, inplace=True)
    df_home.insert(1, 'city', team_home)
    df_home.insert(2, 'is_home', 1)

    # concatenate away and home team events
    df = pd.concat((df_away, df_home), axis=0).sort_index()
    df = df[~df.event.isnull()]

    # clean game score column
    df['numeric'] = df.score.str.match(r'^\d+(-\d+)$')
    df.loc[~df.numeric, 'score'] = pd.NA
    df.loc[0, 'score'] = '0-0'
    df['score'] = df.score.ffill(axis=0)

    # clean points scored column
    df.loc[~df.points.str.match(r'\+\d+').fillna(False), 'points'] = 0
    df['points'] = df.points.astype(int)

    # drop rows with no game time
    has_time = df.time.str.match(r'^\d+:\d+.\d+$')
    df = df[has_time].dropna(axis=0, how='any')

    # dedupe rows (duplicates arise from split home/away tables)
    df.drop_duplicates(
        subset=['time', 'score', 'event', 'points'],
        inplace=True)

    # create column to track the quarter number
    df['minute'] = df.time.str.split(':').str[0].astype(int)
    df['start_quarter'] = (
        df.minute > df.minute.shift(1).fillna(0)).astype(int)
    df.insert(1, 'quarter', df.start_quarter.cumsum())

    # create an indicator for end of game
    df['end_game'] = 0
    df.loc[df.index[-1], 'end_game'] = 1

    # parse game score
    score = df.score.str.split('-')
    df['score_away'] = score.str[0].astype(int)
    df['score_home'] = score.str[1].astype(int)

    df.insert(0, 'game_id', game_id)

    df.drop(columns=['numeric', 'minute', 'score'], inplace=True)

    columns = [
        'game_id',
        'city',
        'is_home',
        'quarter',
        'start_quarter',
        'end_game',
        'time',
        'score_away',
        'score_home',
        'points',
        'event']

    return df[columns]


if __name__ == '__main__':
    print(get_play_by_play('202102090SAS').to_string())
