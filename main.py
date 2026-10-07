import requests
import pandas as pd
from datetime import date as current
import time

# import matplotlib.pyplot as plot 

# from sklearn.linear_model import LinearRegression

api = "2d4bfb855fc3a9892bae30bdeba090fe"

leagues_url = "https://v3.football.api-sports.io/leagues"
teams_url = "https://v3.football.api-sports.io/teams"
player_url = "https://v3.football.api-sports.io/players"


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


def get_player_id(team_id,player_name):
    player_url = "https://v3.football.api-sports.io/players/squads"
    fetch = fetch_json(player_url,params = {"team":team_id})
    profile_url = "https://v3.football.api-sports.io/players/profiles"
    profiles = fetch_json(profile_url)
    if fetch is None:
        return None
    
    player_id = {}
    players_fullName = {}



    for player in fetch["response"][0]["players"]:
        if player["name"] == player_name:
            player_id[player_name] = player["id"]
       
   
    if player_id is None:
        return None
    return player_id[player_name]



def get_player_stats(player_id, team_id, season):
    while season < 2022 or season > 2024:
        season = int(input("Not a valid season. Try Again!: "))
    
    fetch = fetch_json(player_url, params={"id": player_id, "season": season})
    if fetch is None or not fetch["response"]:
        return None

    player_stats = {}
    stats = fetch["response"][0]["statistics"]

    for stat in stats:
        competition = stat["league"]["name"]
        position = stat["games"]["position"]
        goals = stat["goals"]["total"]
        conceded_goals = stat["goals"]["conceded"]
        assists = stat["goals"]["assists"]
        minutes = stat["games"]["minutes"]
        shots_total = stat["shots"]["total"]
        shots_on_target = stat["shots"]["on"]
        passes_total = stat["passes"]["total"]
        passes_key = stat["passes"]["key"]
        passes_accurate = stat["passes"]["accuracy"]
        tackles_total = stat["tackles"]["total"]
        tackles_blocks = stat["tackles"]["blocks"]
        tackles_interceptions = stat["tackles"]["interceptions"]
        duels_total = stat["duels"]["total"]
        duels_won = stat["duels"]["won"]
        dribbles_attempted = stat["dribbles"]["attempts"]
        dribbles_success = stat["dribbles"]["success"]
        dribbled_past = stat["dribbles"]["past"]
        saves = stat["goals"]["saves"]
        save_penalties = stat["penalty"]["saved"]
        fouls_committed = stat["fouls"]["committed"]
        yellow_cards = stat["cards"]["yellow"]
        red_cards = stat["cards"]["red"]

        player_stats[competition] = {
            "position": position,
            "goals": goals,
            "conceded_goals": conceded_goals,
            "assists": assists,
            "minutes": minutes,
            "shots": {"total": shots_total, "on_target": shots_on_target},
            "passes": {
                "total": passes_total,
                "key": passes_key,
                "accurate": passes_accurate,
            },
            "tackles": {
                "total": tackles_total,
                "blocks": tackles_blocks,
                "interceptions": tackles_interceptions,
            },
            "duels": {"total": duels_total, "won": duels_won},
            "dribbles": {
                "attempted": dribbles_attempted,
                "success": dribbles_success,
                "past": dribbled_past,
            },
            "saves": {"total":saves,"penalties saved": save_penalties},
            "fouls_committed": fouls_committed,
            "cards": {"yellow": yellow_cards, "red": red_cards},
        }
    player_fullName = fetch["response"][0]["player"]["firstname"] + " " + fetch["response"][0]["player"]["lastname"]
    print(f"This is the {player_fullName}'s stats for the {season -1}/{season} season:\n")

    return player_stats




print(get_player_stats(161907,49,2024))





