import pandas as pd
from rapidfuzz import process, fuzz

def load_data():
    """Load your API-Football stats and the two Transfermarkt files."""
    stats_df = pd.read_csv("player_stats.csv")
    players_df = pd.read_csv("players.csv")
    valuations_df = pd.read_csv("player_valuations.csv")
    return stats_df, players_df, valuations_df


def match_player_id(player_name, players_df, threshold=90):
    tm_names = players_df["name"].tolist()
    your_name = player_name
    match, score, idx = process.extractOne(your_name, tm_names, scorer=fuzz.WRatio)
    print(match, score)
    # TODO: compare the score to `threshold`
    if score >= threshold:
        player_id = players_df.iloc[idx]["player_id"]
    else:
        print(f"Low-confidence match: '{your_name}' -> '{match}' (score {score}) — check manually")
        player_id = None
    if player_id is not None:
        return player_id
    return None


def get_valuation_for_season(player_id, valuations_df, season=2024):
    player_valuations = valuations_df[valuations_df["player_id"] == player_id]
    if player_valuations.empty:
        print(f"No valuations found for player_id {player_id}")
        return None

    player_valuations["date"] = pd.to_datetime(player_valuations["date"]).copy()
    target_date = pd.Timestamp(f"{season}-07-31")

    closest_row = player_valuations.iloc[(player_valuations["date"] - target_date).abs().argsort()[:1]]
    return closest_row


def build_training_data(stats_df, players_df, valuations_df):
    """Combine everything into one row-per-player-season training table."""
    rows = []
    for _, stats in stats_df.iterrows():
        player_name = stats["player_name"]  # Assuming stats_df has a "player_name" column
        player_id = match_player_id(player_name, players_df)
        if player_id is not None:
            valuation = get_valuation_for_season(player_id, valuations_df)
            if valuation is not None:
                combined_row = stats.to_dict()
                combined_row.update(valuation.iloc[0].to_dict())  # Combine stats and valuation data
                rows.append(combined_row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    stats_df, players_df, valuations_df = load_data()
    training_df = build_training_data(stats_df, players_df, valuations_df)
    training_df.to_csv("training_data.csv", index=False)
    print(training_df)