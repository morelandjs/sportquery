import re
import requests

import numpy as np
import pandas as pd

from . import base_url, team_abbr


def get_schedule(team, season):
    """
    Return the game schedule of the specified `team` and `season`
    as a pandas dataframe.

    """
    schedule_url = f'{base_url}/teams/{team}/{season}_games.html'

    r = requests.get(schedule_url)

    html = re.sub('(<!--)|(-->)', '', r.text, flags=re.DOTALL)

    df, = pd.read_html(html, attrs={'id': 'games'})

    df.drop(columns=['Unnamed: 3', 'Unnamed: 4', 'Unnamed: 8', 'Notes'],
            inplace=True)  # empty columns

    df.columns = [
        'game_number',
        'date',
        'time',
        'is_home',
        'opponent',
        'outcome',
        'team_points',
        'opponent_points',
        'cumulative_wins',
        'cumulative_losses',
        'streak']

    df = df[df.game_number != 'G']

    df['date'] = pd.to_datetime(df.date)

    df['time'] = (df.time + 'm').str.upper()

    timestamp = pd.to_datetime(
        df.date.astype(str).str.cat(df.time, sep=' '),
        format='%Y-%m-%d %I:%M%p')

    df.insert(1, 'datetime', timestamp)

    df.insert(5, 'team', team)

    df['is_home'] = df.is_home.replace({
        '@': False, pd.NA: True})

    df['streak'] = df.streak.str.replace(
        'L ', '-'
    ).str.replace(
        'W ', ''
    ).astype(int)

    df['opponent'] = df.opponent.replace(team_abbr)

    team_home = np.where(df.is_home, df.team, df.opponent)

    game_id = df.date.astype(str).str.replace('-', '') + '0' + team_home
    df.insert(1, 'game_id', game_id)

    df.drop(columns=['date', 'time'], inplace=True)

    return df


if __name__ == '__main__':
    print(get_schedule('NOP', 2018))
