import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Load the CSV file
df = pd.read_csv("2024 grandprix abu dhabi.csv")

# Take first 20 rows
df_sample = df.head(10)
print(df_sample)

# Features (example: TireLife, LapNumber)
X = df_sample[['TyreLife', 'LapNumber']]
y = df_sample['LapTime_in_seconds']

# small Random Forest model
model = RandomForestRegressor(n_estimators=5, random_state=42)
model.fit(X, y)

# Make predictions
preds = model.predict(X)
print("Predicted lap times:", preds)
