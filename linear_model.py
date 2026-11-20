import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. Settings you can change --------------------------------------------
WEIGHTS = {
    "Centre-Forward":     {"goals_total": 3, "shots_on_target": 2, "shots_total": 1,
                           "goals_assists": 1.5, "duels_won": 0.5},
    "Second Striker":     {"goals_total": 2.5, "goals_assists": 2, "shots_on_target": 1.5,
                           "passes_key": 1.5, "dribbles_success": 1},
    "Left Winger":        {"goals_total": 2, "goals_assists": 2, "dribbles_success": 2,
                           "passes_key": 1.5, "shots_on_target": 1},
    "Right Winger":       {"goals_total": 2, "goals_assists": 2, "dribbles_success": 2,
                           "passes_key": 1.5, "shots_on_target": 1},
    "Attacking Midfield": {"goals_total": 2, "goals_assists": 2, "passes_key": 2,
                           "dribbles_success": 1, "shots_on_target": 1},
    "Central Midfield":   {"goals_assists": 1.5, "passes_key": 1.5, "passes_total": 1,
                           "tackles_interceptions": 1.5, "duels_won": 1.5, "goals_total": 1},
    "Defensive Midfield": {"tackles_total": 2, "tackles_interceptions": 2,
                           "duels_won": 2, "passes_total": 1, "tackles_blocks": 1},
    "Left Midfield":      {"goals_assists": 2, "passes_key": 1.5, "dribbles_success": 1.5,
                           "goals_total": 1.5, "tackles_total": 0.5},
    "Right Midfield":     {"goals_assists": 2, "passes_key": 1.5, "dribbles_success": 1.5,
                           "goals_total": 1.5, "tackles_total": 0.5},
    "Centre-Back":        {"tackles_interceptions": 2, "tackles_blocks": 2, "duels_won": 2,
                           "tackles_total": 1.5, "passes_total": 1, "goals_total": 0.5},
    "Left-Back":          {"tackles_total": 2, "tackles_interceptions": 1.5, "duels_won": 1.5,
                           "passes_key": 1.5, "goals_assists": 1.5, "dribbles_success": 1},
    "Right-Back":         {"tackles_total": 2, "tackles_interceptions": 1.5, "duels_won": 1.5,
                           "passes_key": 1.5, "goals_assists": 1.5, "dribbles_success": 1},
    "Goalkeeper":         {"save_pct": 3, "saves_total": 1.5, "penalties_saved": 1,
                           "goals_conceded": 2.5, "passes_total": 0.5},
}

CARD_WEIGHTS = {"cards_yellow": 1, "cards_red": 3}   # penalty for every position
CARD_PENALTY = 0.2
MIN_MINUTES = 900            # ignore players with too little playing time

# Columns that are already rates (e.g., percentages) and don't need per-90 adjustment
RATE_COLS = {"save_pct"}

# Columns where lower values are better (e.g., cards, goals conceded)
LOWER_IS_BETTER = {"cards_yellow", "cards_red", "goals_conceded"}


def score_group(group, name):
    weights = WEIGHTS[name]
    cols = list(weights) + list(CARD_WEIGHTS)
    data = group[cols].copy()
    per90_cols = [c for c in cols if c not in RATE_COLS]
    data[per90_cols] = data[per90_cols].div(group["minutes"] / 90, axis=0)
    ranks = data.rank(pct=True)
    for c in LOWER_IS_BETTER & set(cols):
        ranks[c] = 1 - ranks[c] + 1 / len(group)
    good = sum(ranks[c] * w for c, w in weights.items()) / sum(weights.values())
    bad = sum(ranks[c] * w for c, w in CARD_WEIGHTS.items()) / sum(CARD_WEIGHTS.values())
    return good - CARD_PENALTY * bad


def add_score(df, group_col="sub_position"):
    df = df[df["minutes"] >= MIN_MINUTES].copy()
    if "saves_total" in df.columns:
        df["save_pct"] = df["saves_total"] / (df["saves_total"] + df["goals_conceded"])
    df["score"] = 0.0
    for name, group in df.groupby(group_col):
        df.loc[group.index, "score"] = score_group(group, name)
    return df

# --- 4. Regression: score -> market value ----------------------------------
def fit_value_model(df):
    X = df[["score", "age"]].values
    y = df["market_value_in_eur"].values / 1e6      # value in millions of euros
    model = LinearRegression().fit(X, y)
    df["predicted_value"] = model.predict(X)
    df["gap"] = df["value_m"] - df["predicted_value"]
    print("R-squared:", round(r2_score(y, model.predict(X)), 3))
    print("Coefficient:", model.coef_[0], "Intercept:", model.intercept_)
    return model, df


def plot_results(df, model):
    sns.set_theme(style="whitegrid")

    # Create scatterplot for market value vs performance score
    sns.scatterplot(x="score", y="value_m", data=df, s=90)

    # Line drawn from the linear regression model's predictions
    xs = np.linspace(df["score"].min(), df["score"].max(), 100)
    plt.plot(xs, model.predict(xs.reshape(-1, 1)), color="grey", linestyle="--")

    # Name each player next to their dot
    for _, row in df.iterrows():
        plt.text(row["score"] + 0.01, row["value_m"] + 2, row["player_name"])

    plt.xlim(df["score"].min() - 0.05, df["score"].max() + 0.12)
    plt.title("Midfielder Market Value based on Performance Score")
    plt.xlabel("Performance Score")
    plt.ylabel("Market Value (millions of euros)")
    plt.show()

if __name__ == "__main__":
    df = pd.read_csv("training_data.csv")
    df = add_score(df)
    df["value_m"] = df["market_value_in_eur"] / 1e6
    model, df = fit_value_model(df)
    out = df[["player_name", "score", "value_m", "predicted_value", "gap"]]
    print(out.round(2).to_string(index=False))
    plot_results(df, model)
    