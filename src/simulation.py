# Imports
import pandas as pd
import random
import joblib
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# load trained model and saved mappings
model = joblib.load(os.path.join(base_dir, "models", "trained_model.pkl"))
compound_map = joblib.load(os.path.join(base_dir, "models", "compound_map.pkl"))
team_map = joblib.load(os.path.join(base_dir, "models", "team_map.pkl"))


# pit stop times
pit_stop_medians = {
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

pit_lane_time = 20

# simulation function
# A function that takes a strategy, trained model, total laps and team as input and returns total race time
def simulate_strategy(strategy, model, total_laps, team):
    total_time = 0
    lap_number = 1
    lap_data = []  # store lap by lap data

    degradation_thresholds = {
        "SOFT":   {"threshold": 12, "rate": 0.20},
        "MEDIUM": {"threshold": 20, "rate": 0.12},
        "HARD":   {"threshold": 30, "rate": 0.14},
    }

    for stint_number, (compound, stint_length) in enumerate(strategy, start=1):
        tyre_life = 0

        for i in range(stint_length):
            input_data = pd.DataFrame([{
                "LapNumber": lap_number,
                "Stint": stint_number,
                "Compound": compound,
                "TyreLife": tyre_life,
                "Team": team,
                "FuelLoad": total_laps - lap_number
            }])

            input_data["Compound"] = input_data["Compound"].map(compound_map)
            input_data["Team"] = input_data["Team"].map(team_map)

            lap_time = model.predict(input_data)[0]

            deg = degradation_thresholds[compound]

            if tyre_life > deg["threshold"]:
                laps_over = tyre_life - deg["threshold"]
                degradation_penalty = (laps_over ** 1.5) * deg["rate"]
                lap_time += degradation_penalty

            total_time += lap_time

            # store each lap
            lap_data.append({
                "Lap": lap_number,
                "Stint": stint_number,
                "Compound": compound,
                "Tyre Life": tyre_life,
                "Lap Time (s)": round(lap_time, 3)
            })

            tyre_life += 1
            lap_number += 1

        if stint_number < len(strategy):
            base_time = pit_stop_medians.get(team, 2.7)
            pit_time = pit_lane_time + base_time
            total_time += pit_time

    return total_time, lap_data  # return both
