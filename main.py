import requests
import pandas as pd
from datetime import datetime as current
import time
# import matplotlib.pyplot as plot 

# from sklearn.linear_model import LinearRegression

api = "c92746597bae4a5081858bbe1336dbbe"
url = "http://api.football-data.org/v4/competitions/"
leagues_url = "http://api.football-data.org/v4/competitions/"
teams_url = "http://api.football-data.org/v4/competitions/WC/teams"
player_url = " http://api.football-data.org/v4/persons/44"
headers = {'X-Auth-Token': api}
now = current.now()

def fetch_json(url,headers = headers,params = None):
    try:
        response = requests.get(url,headers = headers,params = params)
        response.raise_for_status()
        if response.status_code == 200:
            res = response.json()
            return res
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        message = e.response.text
        if status == 404:
            print("Resource not found. Check the URL.")
        elif status == 401:
            print("Unauthorized. Check your API token or login.")
        elif status == 429:
            for i in range(3):
                print(f"Rate limited. Attempt {i+1} of 3, waiting 6 seconds...")
                time.sleep(6)
                result = fetch_json(url, headers)
                if result is not None:
                    return result
            return None
        elif 500 <= status < 600:
            print("Server error. Try again later or set up a retry.")
        else:
            print(f"HTTP error occurred: {status} - {message}")


        return None

def get_leagues(leagueID = 0,leagueName = ""):
    fetch = fetch_json(url,headers=headers)
    leagues = [
        {
            league["name"]:league["id"]
        }

        for league in fetch["competitions"]
    ]          

Leagues_id = {
    'BSA': 2013,   # Campeonato Brasileiro Série A
    'ELC': 2016,   # Championship
    'PL': 2021,    # Premier League
    'CL': 2001,    # UEFA Champions League
    'EC': 2018,    # European Championship
    'FL1': 2015,   # Ligue 1
    'BL1': 2002,   # Bundesliga
    'SA': 2019,    # Serie A
    'DED': 2003,   # Eredivisie
    'PPL': 2017,   # Primeira Liga
    'PD': 2014,    # Primera Division
    'WC': 2000,    # FIFA World Cup
}

Leagues = {
    'Campeonato Brasileiro Série A': 'BSA',
    'Championship': 'ELC',
    'Premier League': 'PL',
    'UEFA Champions League': 'CL',
    'European Championship': 'EC',
    'Ligue 1': 'FL1',
    'Bundesliga': 'BL1',
    'Serie A': 'SA',
    'Eredivisie': 'DED',
    'Primeira Liga': 'PPL',
    'La Liga': 'PD',
    'FIFA World Cup': 'WC',
}

def get_teams_from_league(league_name,seasons = 2026,league_dict = Leagues):
   
    if league_dict is None:
        return None
    if league_name in league_dict:
        teams_url = f"{url}{league_dict[league_name]}/teams"
    else:
        return None

    fetch = fetch_json(teams_url,headers = headers,params = {'season':seasons})
  
    if fetch is None:
        return None

    team_names = []
    for team in fetch["teams"]:
        team_names.append(team["shortName"])

    return team_names

def get_team_id(league_name,team_name = "Chelsea"):
   
    league_teams = get_teams_from_league(league_name)
    league_dict = Leagues
    if league_dict is None:
        return None
    if league_name in league_dict:
        teams_url = f"{url}{league_dict[league_name]}/teams"
    else:
        return None

    fetch = fetch_json(teams_url,headers = headers)
    if fetch is None:
        return None
    
    team_id = {}
    if team_name in league_teams:
        position = league_teams.index(team_name)
        team_id[team_name] = fetch["teams"][position]["id"]
    else:
        return None

    return team_id[team_name]




def get_player_id(league_name,team_name,player_name):
    team_id = get_team_id(league_name,team_name)
    if team_id is None:
        return None

    team_url = f"http://api.football-data.org/v4/teams/{team_id}"
    club = fetch_json(team_url)
    pIndex = 100
    squad = club["squad"]
    for player_info in squad:
        player = player_info["name"]
        if player_name == player:
            pIndex = squad.index(player_info)
            break
        
    if pIndex > len(squad):
        return None
        
    player_id = {}
    player_id[player_name] = squad[pIndex]["id"]

    if player_id is None:
        return None
    return player_id[player_name]

ardGuler = get_player_id("UEFA Champions League","Real Madrid","Ferland Mendy")
print(ardGuler)






    


    

# def get_all_teams(league_dict=Leagues):
#     all_dfs = []
#     current_year = now.year

#     for league_name, league_abb in league_dict.items():
#         if league_name == "European Championship":
#             season = current_year - 2 if current_year % 4 == 2 else current_year
#             league_teams = get_teams_from_league(league_name, season)
#             print(f"Getting teams from {league_name} {season}")
#         elif league_name == "FIFA World Cup":
#             season = current_year 
#             league_teams = get_teams_from_league(league_name, season)
            
#         else:
#             league_teams = get_teams_from_league(league_name)
#             print(f"Getting teams from {league_name} {current_year}")

#         time.sleep(2)
#         if league_teams is None:
#             continue

#         df = pd.DataFrame({league_name: league_teams})
#         all_dfs.append(df)  # <- the fix: save this iteration's df before it's overwritten

#     all_teams_df = pd.concat(all_dfs, axis=1)  # <- concat the WHOLE collected list, once
#     all_teams_df.to_csv("teams.csv", index=False)

    






