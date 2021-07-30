import re

import pandas as pd
import requests

from . import base_url, team_abbr


def get_teams(season):
    """
    Return list of `team_abbr` strings for the given season

    Args:
        season (int): The requested season year to pull teams for

    Returns:
        list of str: abbreviated name of all teams in season `season`

    """
    season_url = f'{base_url}/leagues/NBA_{season}.html'
    r = requests.get(season_url)

    html = re.sub('(<!--)|(-->)', '', r.text, flags=re.DOTALL)

    df, = pd.read_html(html, attrs={'id': 'advanced-team'})
    df.columns = df.columns.droplevel()

    df['Team'] = df.Team.str.rstrip('*')  # remove trailing asterisk

    teams_full = df.Team[df.Team != 'League Average'].tolist()

    return [team_abbr[team_full] for team_full in teams_full]


if __name__ == '__main__':

    teams = get_teams(2017)
    print(teams)
