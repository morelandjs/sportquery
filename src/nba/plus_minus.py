import re
import requests

from bs4 import BeautifulSoup
import pandas as pd
from unidecode import unidecode

from . import base_url


def _unpack_plus_minus(div):
    width = int(re.search(r'\d+', div.get('style')).group())
    numeric = re.search(r'[-+]?\d+', div.text)
    points = int(numeric.group()) if numeric else None
    return width, points


def plus_minus(game_id):
    """
    Plus-minus contributions at the player-minute level

    """
    plus_minus_url = f'{base_url}/boxscores/plus-minus/{game_id}.html'

    r = requests.get(plus_minus_url)

    page = re.sub('(<!--)|(-->)', '', r.text, flags=re.DOTALL)

    soup = BeautifulSoup(page, 'html.parser')

    all_players = [
        unidecode(re.search(r'(?:(?!\().)*', div.text).group()).strip()
        for div in soup.find_all('div', attrs={'class': 'player'})]

    all_intervals = [[
        _unpack_plus_minus(d) for d in div.find_all('div')]
        for div in soup.find_all('div', attrs={'class': 'player-plusminus'})]

    df_plus_minus = pd.DataFrame(columns=[
        'player', 'subin_minute', 'subout_minute', 'plus_minus'])

    for player, intervals in zip(all_players, all_intervals):
        df = pd.DataFrame(intervals, columns=['duration', 'points'])
        df.duration *= 48. / df.duration.sum()

        df['player'] = player
        df['subin_minute'] = df.duration.shift(1).cumsum().fillna(0)
        df['subout_minute'] = df.duration.cumsum()
        df['plus_minus'] = df.points

        df.dropna(axis=0, inplace=True)
        df.drop(columns=['duration', 'points'], inplace=True)

        df_plus_minus = df_plus_minus.append(df)

    df_plus_minus.insert(0, 'game_id', game_id)

    return df_plus_minus.reset_index(drop=True)


if __name__ == '__main__':
    print(plus_minus('201810210CLE').to_string())
