import re
import requests

import pandas as pd

from . import base_url


def play_by_play(game_id):
    """
    Plus-minus contributions at the player-minute level

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
    df_away.insert(1, 'team', team_away)

    # home team events
    df_home = df[['time', 'score', 'team_home', 'points_home']].copy()
    df_home.rename(columns={
        'team_home': 'event', 'points_home': 'points'}, inplace=True)
    df_home.insert(1, 'team', team_home)

    # concatenate away and home team events
    df = pd.concat((df_away, df_home), axis=0).sort_index()
    df = df[~df.event.isnull()]

    # clean game score column
    df['numeric'] = df.score.str.match('^\d+(-\d+)$')
    df.loc[~df.numeric, 'score'] = pd.NA
    df.loc[0, 'score'] = '0-0'
    df['score'] = df.score.ffill(axis=0)

    # clean points scored column
    df.loc[~df.points.str.match('\+\d+').fillna(False), 'points'] = 0
    df['points'] = df.points.astype(int)

    # drop rows with no game time
    has_time = df.time.str.match('^\d+:\d+.\d+$')
    df = df[has_time].dropna(axis=0, how='any')

    # dedupe rows (duplicates arise from split home/away tables)
    df.drop_duplicates(
        subset=['time', 'score', 'event', 'points'],
        inplace=True)

    # create column to track the quarter number
    df['start_quarter'] = df.event.str.match(
        '^Start of.*quarter$'
    ).fillna(False)

    df.insert(1, 'quarter', 1 + df.start_quarter.cumsum())
    df.drop(columns=['numeric', 'start_quarter'], inplace=True)

    return df


if __name__ == '__main__':
    print(play_by_play('201810210CLE'))
