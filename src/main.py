import streamlit as st
import uuid
from simulation import simulate_strategy, model

st.title("F1 Strategy Simulator")

st.markdown("""
    <style>
    button[kind="primary"] {
        border: none;
        background: none;
        color: #0068C9;
    }
    button[kind="primary"]:hover {
        border: none;
        background: none;
        color: red;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "strategies" not in st.session_state:
    st.session_state.strategies = [
        [
            {"id": str(uuid.uuid4()), "compound": "SOFT", "length": 1},
            {"id": str(uuid.uuid4()), "compound": "MEDIUM", "length": 1}
        ]
    ]
if "invalid_strategies" not in st.session_state:
    st.session_state.invalid_strategies = set()
if "invalid_reasons" not in st.session_state:
    st.session_state.invalid_reasons = {}

if "team" not in st.session_state:
    st.session_state.team = "Red Bull"
if "laps" not in st.session_state:
    st.session_state.laps = 58

team_options = [
    "Red Bull", "Ferrari", "Mercedes", "McLaren",
    "Aston Martin", "Alpine", "AlphaTauri",
    "Alfa Romeo", "Haas", "Williams"
]

laps = st.number_input("Number of Laps", min_value=1, value=st.session_state.laps)
st.session_state.laps = laps

team = st.selectbox("Team", team_options, 
    index=team_options.index(st.session_state.team))
st.session_state.team = team

# Add strategy button
if st.button("+ Add Another Strategy", type="primary"):
    st.session_state.simulate_done = False
    st.session_state.strategies.append([
        {"id": str(uuid.uuid4()), "compound": "SOFT", "length": 1},
        {"id": str(uuid.uuid4()), "compound": "MEDIUM", "length": 1}
    ])
    st.rerun()

# Loop through strategies
for s_idx, strategy in enumerate(st.session_state.strategies):
    col_title, col_delete = st.columns([10, 1])

    with col_title:
        if s_idx in st.session_state.invalid_strategies:
            st.subheader(f":red[Strategy {s_idx + 1}]")
            st.error(st.session_state.invalid_reasons.get(s_idx, "Invalid strategy"))
        else:
            st.subheader(f"Strategy {s_idx + 1}")

    with col_delete:
        if s_idx > 0:
            if st.button("−", key=f"remove_strategy_{s_idx}"):
                st.session_state.simulate_done = False
                st.session_state.strategies.pop(s_idx)
                st.rerun()

    # Column headings
    col0, col1, col2, col3 = st.columns([1, 2, 2, 1])
    with col1: st.markdown("**Compound**")
    with col2: st.markdown("**Stint**")

    # Loop through pit stops
    for p_idx, stop in enumerate(strategy):
        uid = stop["id"]
        col0, col1, col2, col3 = st.columns([1, 2, 2, 1])

        with col0:
            st.write("Start" if p_idx == 0 else f"Pit-Stop {p_idx}")

        with col1:
            stop["compound"] = st.selectbox(
                "Compound", ["SOFT", "MEDIUM", "HARD"],
                index=["SOFT", "MEDIUM", "HARD"].index(stop["compound"]),
                key=f"compound_{uid}",
                label_visibility="collapsed",
                on_change=lambda: setattr(st.session_state, "simulate_done", False)
            )

        with col2:
            stop["length"] = st.number_input(
                "Stint", min_value=1,
                value=stop["length"],
                key=f"length_{uid}",
                label_visibility="collapsed",
                on_change=lambda: setattr(st.session_state, "simulate_done", False)
            )

        with col3:
            if p_idx > 1:
                if st.button("−", key=f"remove_{uid}"):
                    st.session_state.simulate_done = False
                    strategy.pop(p_idx)
                    st.rerun()

    # Add pit stop button
    if st.button("+ Add Another Pit Stop", key=f"addpit_{s_idx}", type="primary"):
        st.session_state.simulate_done = False
        strategy.append({"id": str(uuid.uuid4()), "compound": "SOFT", "length": 1})
        st.rerun()

col_sim, col_reset = st.columns([3, 1])

with col_sim:
       
    # Simulate button
    if st.button("Simulate All Strategies"):
        st.session_state.invalid_strategies = set()
        st.session_state.invalid_reasons = {}

        for i, strat in enumerate(st.session_state.strategies):
            total = sum(s["length"] for s in strat)
            if total != laps:
                st.session_state.invalid_strategies.add(i)
                st.session_state.invalid_reasons[i] = f"Stint lengths must add up to {laps} laps"

        if not st.session_state.invalid_strategies:
            with st.spinner("Simulating strategies..."):
                results = []
                lap_by_lap = []
                total_times = []

                for i, strat in enumerate(st.session_state.strategies):
                    strategy_tuples = [(s["compound"], s["length"]) for s in strat]
                    total_time, lap_data = simulate_strategy(strategy_tuples, model, laps, team)
                    minutes = int(total_time // 60)
                    seconds = total_time % 60
                    total_times.append(total_time)
                    results.append({
                        "Strategy": f"Strategy {i+1}",
                        "Stints": "\n".join([f"{s['compound']} ({s['length']} laps)" for s in strat]),
                        "Total Time": f"{minutes}m {seconds:.3f}s"
                    })
                    lap_by_lap.append(lap_data)

            best_idx = total_times.index(min(total_times))
            st.session_state.results = results
            st.session_state.lap_by_lap = lap_by_lap
            st.session_state.best_idx = best_idx
            st.session_state.go_to_results = True

        st.rerun()

with col_reset:
    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()


if st.session_state.get("go_to_results"):
    st.session_state.go_to_results = False
    st.switch_page("pages/results.py")