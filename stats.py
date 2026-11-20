import requests
import pandas as pd
from datetime import date as current
import time
from dotenv import load_dotenv
import os



class Stats:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'x-apisports-key': self.api_key}
        self.leagues_url = "https://v3.football.api-sports.io/leagues"
        self.teams_url = "https://v3.football.api-sports.io/teams"
        self.player_url = "https://v3.football.api-sports.io/players"
        self.LEAGUES = {
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

    def fetch_json(self, url, headers=None, params=None):
        headers = headers or self.headers
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status == 404:
                print("Resource not found. Check the URL.")
            elif status == 401:
                print("Unauthorized. Check your API token or login.")
            elif status == 429:
                for _ in range(3):
                    print("Rate limited, waiting 6 seconds...")
                    time.sleep(6)
                    result = self.fetch_json(url, headers, params)
                    if result is not None:
                        return result
            elif 500 <= status < 600:
                print("Server error. Try again later.")
            else:
                print(f"HTTP error occurred: {status}")
        return None

    def get_teams_from_league(self, league_id):
        season = int(input(f"Enter a season: "))
        while season < 2022 or season > 2024:
            season = int(input("Not a valid season. Try Again!: "))
        league_name = [key for key, val in self.LEAGUES.items() if val == league_id][0]
        print(f"Getting teams from the {league_name} season {season - 1}/{season}:\n")
        
        fetch = self.fetch_json(self.teams_url, params={"league": league_id, 'season': season})
        if fetch is None:
            return None

        team_names = [team["team"]["name"] for team in fetch["response"]]
        team_names.sort()
        return team_names

    def get_team_id(self, team_name):
        fetch = self.fetch_json(self.teams_url, params={"name": team_name})
        if fetch is None:
            return None
        return fetch["response"][0]["team"]["id"]
    
    def get_squad(self, team_id, season):
        squad = []
        page = 1
        while True:
            fetch = self.fetch_json(self.player_url, params={"team": team_id, "season": season, "page": page})
            if fetch is None:
                return squad
            for item in fetch["response"]:
                squad.append((item["player"]["id"], item["player"]["name"]))
            if page >= fetch["paging"]["total"]:
                return squad
            page += 1

    def get_player_id(self, team_id, season, player_name=None):
        squad = self.get_squad(team_id, season)
        if not squad:
            return None
        if player_name is None:                      # old behaviour: show squad and ask
            for _, name in sorted(squad, key=lambda p: p[1]):
                print(name)
            player_name = input("What player do you want: ")
        for player_id, name in squad:
            if player_name.lower() in name.lower():
                return player_id, name
        return None
    
    def get_player_stats(self, player_id, team_id, season):
        while season < 2022 or season > 2024:
            season = int(input("Not a valid season. Try Again!: "))
        
        fetch = self.fetch_json(self.player_url, params={"id": player_id, "team": team_id, "season": season})
        if fetch is None or not fetch["response"]:
            return None

        player_stats = {}
        stats = fetch["response"][0]["statistics"]
        for stat in stats:
            competition = stat["league"]["name"]
            player_stats[competition] = {
                "position": stat["games"]["position"],
                "goals_total": stat["goals"]["total"],
                "goals_conceded": stat["goals"]["conceded"],
                "goals_assists": stat["goals"]["assists"],
                "minutes": stat["games"]["minutes"],
                "shots_total": stat["shots"]["total"],
                "shots_on_target": stat["shots"]["on"],
                "passes_total": stat["passes"]["total"],
                "passes_key": stat["passes"]["key"],
                "passes_accurate": stat["passes"]["accuracy"],
                "tackles_total": stat["tackles"]["total"],
                "tackles_blocks": stat["tackles"]["blocks"],
                "tackles_interceptions": stat["tackles"]["interceptions"],
                "duels_total": stat["duels"]["total"],
                "duels_won": stat["duels"]["won"],
                "dribbles_attempted": stat["dribbles"]["attempts"],
                "dribbles_success": stat["dribbles"]["success"],
                "dribbles_past": stat["dribbles"]["past"],
                "saves_total": stat["goals"]["saves"],
                "penalties_saved": stat["penalty"]["saved"],
                "fouls_committed": stat["fouls"]["committed"],
                "cards_yellow": stat["cards"]["yellow"],
                "cards_red": stat["cards"]["red"],
            }
        
        return player_stats

    def get_player_data(self, team_name=None, season=None, player_name=None, save=True):
        if team_name is None:
            team_name = input("What team do you want? ")
        if season is None:
            season = int(input("What season do you want? "))
        team_id = self.get_team_id(team_name)
        if not team_id:
            print(f"Team '{team_name}' not found")
            return None

        result = self.get_player_id(team_id, season, player_name)
        if result is None:
            print("Player not found for that team and season")
            return None
        player_id, player_name = result

        player_stats = self.get_player_stats(player_id, team_id, season)
        if player_stats is None:
            print("No stats found for that player")
            return None
        records = []
        for competition, stats in player_stats.items():
            record = {"competition": competition, "player_name": player_name,
                    "player_id": player_id, "season": season}
            record.update(stats)
            records.append(record)

        player_df = pd.DataFrame(records)
        if save:
            file_exists = os.path.exists("player_stats.csv")
            player_df.to_csv("player_stats.csv", mode="a", header=not file_exists, index=False)
        return player_df
    
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_FOOTBALL_KEY")
    stats = Stats(api_key)
    
    player_df = stats.get_player_data()
    if player_df is not None:
        print(player_df)
