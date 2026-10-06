import requests
import pandas as pd
from datetime import date as current
import time

# import matplotlib.pyplot as plot 

# from sklearn.linear_model import LinearRegression

api = "2d4bfb855fc3a9892bae30bdeba090fe"

leagues_url = "https://v3.football.api-sports.io/leagues"
teams_url = "https://v3.football.api-sports.io/teams"
player_url = "https://v3.football.api-sports.io/players/seasons"


headers = {'x-apisports-key': api}

now = current.today()

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
            for i in range(1,4):
                print(f"Rate limited. Attempt {i} of 3, waiting 6 seconds...")
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

def get_leagues():
    fetch = fetch_json(leagues_url,headers=headers)
   
    leagues = [
        {

            "league_id": league["league"]["id"],
            "league_name": league["league"]["name"],
        }
        for league in fetch['response']
    ]
    return leagues


LEAGUES = {
    "Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61,
    "Eredivisie": 88,
    "UEFA Champions League": 2,
    "UEFA Europa League": 3,
    "UEFA Conference League": 4,
    "UEFA Super Cup": 5,
    "Championship": 180,
    "Primeira Liga": 94,
}

# print(fetch_json(teams_url,headers=headers,params = {"league":39,"season":2024})["response"][0])
def get_teams_from_league(league_id,league_name):
    season = int(input(f"Enter a season: "))
    league_dicts = LEAGUES
    
    while season < 2022 or season > 2024:
        season = int(input("Not a valid season.Try Again!: "))
    league_name = [key for key,val in league_dicts.items() if val == league_id][0]
    print(f"Getting teams from  the {league_name} season {season - 1}/{season}:\n")
        
    fetch = fetch_json(teams_url,headers = headers,params = {"league":league_id,'season':season})
    
    if fetch is None:
        return None

    team_names = []
    for team in fetch["response"]:
        team_names.append(team["team"]["name"])

    team_names.sort()
    return team_names


# print(get_teams_from_league(180,"La Liga"))

# 
def get_team_id(team_name):
   
    fetch = fetch_json(teams_url,params = {"name":team_name})
    if fetch is None:
        return None
    team_id = {}
    team_id[team_name] = fetch["response"][0]["team"]["id"]
   
    return team_id[team_name]




# def get_player_id(league_name,team_name,player_name,
#                 dateFrom = current(2020,1,1),
#                 dateTo = current.today()):
   
#     team_id = get_team_id(league_name,team_name)
#     if team_id is None:
#         return None

#     team_url = f"http://api.football-data.org/v4/teams/{team_id}"
#     club = fetch_json(team_url)
#     pIndex = 100
#     squad = club["squad"]
#     for player_info in squad:
#         player = player_info["name"]
#         if player_name == player:
#             pIndex = squad.index(player_info)
#             break
        
#     if pIndex > len(squad):
#         return None
        
#     player_id = {}
#     player_id[player_name] = squad[pIndex]["id"]

#     if player_id is None:
#         return None
#     return player_id[player_name]

# player_id = get_player_id("La Liga","Real Madrid","Jude Bellingham")
# player_url = f"http://api.football-data.org/v4/persons/{player_id}/matches"
# fetch = fetch_json(player_url,params = {"dateFrom":current(2024,9,1),"dateTo":current(2025,9,1)})
# print(fetch)

# # def get_player_stats(league_name,club,player,season = 2026):
# #     player_id = get_player_id(league_name,club,player)
# #     player_url = f"http://api.football-data.org/v4/persons/{player_id}/matches"
# #     fetch = fetch_json(player_url)
    


    








    


    

# # def get_all_teams(league_dict=Leagues):
# #     all_dfs = []
# #     current_year = now.year

# #     for league_name, league_abb in league_dict.items():
# #         if league_name == "European Championship":
# #             season = current_year - 2 if current_year % 4 == 2 else current_year
# #             league_teams = get_teams_from_league(league_name, season)
# #             print(f"Getting teams from {league_name} {season}")
# #         elif league_name == "FIFA World Cup":
# #             season = current_year 
# #             league_teams = get_teams_from_league(league_name, season)
            
# #         else:
# #             league_teams = get_teams_from_league(league_name)
# #             print(f"Getting teams from {league_name} {current_year}")

# #         time.sleep(2)
# #         if league_teams is None:
# #             continue

# #         df = pd.DataFrame({league_name: league_teams})
# #         all_dfs.append(df)  # <- the fix: save this iteration's df before it's overwritten

# #     all_teams_df = pd.concat(all_dfs, axis=1)  # <- concat the WHOLE collected list, once
# #     all_teams_df.to_csv("teams.csv", index=False)

    






