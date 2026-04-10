# Imports
import pandas as pd
import joblib
import os

# gets path to the project root (jumps 2 levels up from current position)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# load trained model and saved mappings using the root path
model = joblib.load(os.path.join(base_dir, "models", "trained_model.pkl"))
compound_map = joblib.load(os.path.join(base_dir, "models", "compound_map.pkl"))
team_map = joblib.load(os.path.join(base_dir, "models", "team_map.pkl"))


# median pit stop times per team (in seconds)
median_pit_stop = {
    "Ferrari": 2.3,
    "Red Bull": 2.4,
    "Mercedes": 2.5,
    "McLaren": 2.7,
    "Aston Martin": 2.7,
    "Alpine": 2.8,
    "AlphaTauri": 2.8,
    "Alfa Romeo": 2.9,
    "Haas": 2.9,
    "Williams": 3.0
}

pit_lane_time = 20 # average

# simulation function
# A function that takes a strategy, trained model, total laps and team as input and returns total race time
def simulate_strategy(strategy, model, total_laps, team):
    total_time = 0
    lap_number = 1
    lap_data = []  # store lap by lap data

    # tyre degradation thresholds and penelty rate for each compound
    degradation_thresholds = {
        "SOFT":   {"threshold": 12, "rate": 0.20},
        "MEDIUM": {"threshold": 20, "rate": 0.12},
        "HARD":   {"threshold": 30, "rate": 0.14},
    }

    # loop through each stint in strategy
    for stint_number, (compound, stint_length) in enumerate(strategy, start=1):
        tyre_life = 0

        # simulating each lap within the stint
        for i in range(stint_length):

            # input features for the model (in data row format)
            input_data = pd.DataFrame([{
                "LapNumber": lap_number,
                "Stint": stint_number,
                "Compound": compound,
                "TyreLife": tyre_life,
                "Team": team,
                "FuelLoad": total_laps - lap_number
            }])

            # encoding categorical features using saved mappings (for consistency)
            input_data["Compound"] = input_data["Compound"].map(compound_map)
            input_data["Team"] = input_data["Team"].map(team_map)

            # predict lap times usign trained model
            lap_time = model.predict(input_data)[0]

            # applying extra degradation penetly if tyre life exceeds threshold
            deg = degradation_thresholds[compound]
            if tyre_life > deg["threshold"]:
                laps_over = tyre_life - deg["threshold"]
                degradation_penalty = (laps_over ** 1.5) * deg["rate"]
                lap_time += degradation_penalty

            total_time += lap_time

            # store each lap detail (for lap-by-lap table)
            lap_data.append({
                "Lap": lap_number,
                "Stint": stint_number,
                "Compound": compound,
                "Tyre Life": tyre_life,
                "Lap Time (s)": round(lap_time, 3)
            })

            tyre_life += 1
            lap_number += 1

        # adding pit stop time after each stint, except the last one
        if stint_number < len(strategy):
            base_time = median_pit_stop.get(team, 2.7)
            pit_time = pit_lane_time + base_time
            total_time += pit_time

    # return total race time and lap by lap breakdown
    return total_time, lap_data 
