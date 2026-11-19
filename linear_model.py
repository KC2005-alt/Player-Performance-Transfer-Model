import stats as st 
from sklearn.linear_model import LinearRegression 
from sklearn.metrics import r2_score
import numpy as np 
import statsmodels.api as sm
import pandas as pd

df = pd.read_csv("training_data.csv")
df["goals_per_90"] = df["goals_total"] / (df["minutes"] / 90)
per_90_cols = ["goals_total", "goals_assists", "passes_key", "dribbles_success"]
for col in per_90_cols:
    df[col + "_per_90"] = df[col] / (df["minutes"] / 90)
print(df[["player_name"] + [c + "_per_90" for c in per_90_cols]])

def linear_regression(X, y, new_data=None):
    model = LinearRegression()
    model.fit(X,y)

    # R-Squared
    y_pred = model.predict(X)
    r_squared = r2_score(y,y_pred)
    print("R-Squared: ", r_squared)

    # P-Values
    X_intercept = sm.add_constant(X)
    model_sm = sm.OLS(y,X_intercept).fit()
    print("P-Values: ",model_sm.pvalues)

    # Coef
    print("Coef: ",model.coef_)
    print("Intercept: ",model.intercept_)

    # Predictions
    if new_data is not None:
        predictions = model.predict(new_data)
        print("Predictions based on data",predictions)

   
# Data Pass
X = np.array()
y = np.array()
new_data = np.array()


# Print Outcomes

linear_regression(X,y,new_data)


