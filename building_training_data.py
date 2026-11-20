import pandas as pd
from rapidfuzz import process


def load_data():
    """Load your API-Football stats and the two Transfermarkt files."""
    stats_df = pd.read_csv("player_stats.csv")
    players_df = pd.read_csv("players.csv")
    valuations_df = pd.read_csv("player_valuations.csv")
    return stats_df, players_df, valuations_df


POSITION_MAP = {"Goalkeeper": "Goalkeeper", "Defender": "Defender",
                "Midfielder": "Midfield", "Attacker": "Attack"}

def match_player_id(player_name, season, position, players_df):
    initial = player_name[0].upper()
    candidates = players_df[
        (players_df["last_season"] >= season)
        & (players_df["first_name"].fillna("").str.upper().str.startswith(initial))
        & (players_df["position"] == POSITION_MAP[position])
    ]
    if candidates.empty:
        return None
    match, score, idx = process.extractOne(player_name, candidates["name"].tolist())
    return candidates.iloc[idx]["player_id"]


def get_valuation_for_season(player_id, valuations_df, season=2024):
    player_valuations = valuations_df[valuations_df["player_id"] == player_id].copy()
    if player_valuations.empty:
        print(f"No valuations found for player_id {player_id}")
        return None

    player_valuations["date"] = pd.to_datetime(player_valuations["date"])
    target_date = pd.Timestamp(f"{season}-07-31")

    closest_row = player_valuations.iloc[(player_valuations["date"] - target_date).abs().argsort()[:1]]
    closest_row = closest_row.rename(columns={"player_id": "tm_player_id"})
    return closest_row


def aggregate_player_stats(stats_df):
    stats_df = stats_df[stats_df["minutes"] > 0]
    cols = [
        "goals_total", "goals_assists", "minutes",
        "shots_total", "shots_on_target",
        "passes_total", "passes_key",
        "tackles_total", "tackles_blocks", "tackles_interceptions",
        "duels_total", "duels_won",
        "dribbles_attempted", "dribbles_success", "dribbles_past",
        "fouls_committed", "cards_yellow", "cards_red",
    ]
    return stats_df.groupby(["player_name", "player_id", "season", "position"], as_index=False)[cols].sum()


def build_training_data(stats_df, players_df, valuations_df):
    """Combine everything into one row-per-player-season training table."""
    stats_df = aggregate_player_stats(stats_df)
    rows = []
    for _, stats in stats_df.iterrows():
        player_id = match_player_id(stats["player_name"], stats["season"], stats["position"], players_df)
        if player_id is None:
            print(f"No Transfermarkt match for {stats['player_name']}")
            continue
        valuation = get_valuation_for_season(player_id, valuations_df, stats["season"] + 1)
        if valuation is None:
            continue
        tm_row = players_df.loc[players_df["player_id"] == player_id].iloc[0]
        combined_row = stats.to_dict()
        combined_row["player_name"] = tm_row["name"]
        combined_row["sub_position"] = tm_row["sub_position"]
        combined_row.update(valuation.iloc[0].to_dict())
        date_of_birth = pd.to_datetime(tm_row["date_of_birth"])
        combined_row["age"] = round((combined_row["date"] - date_of_birth).days / 365.25, 1)
        rows.append(combined_row)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    stats_df, players_df, valuations_df = load_data()
    training_df = build_training_data(stats_df, players_df, valuations_df)
    training_df.to_csv("training_data.csv", index=False)
    print(training_df)