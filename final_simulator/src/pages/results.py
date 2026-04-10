import streamlit as st
import pandas as pd

st.title("Simulation Results")

# css to style buttons
st.markdown("""
    <style>
    button[kind="primary"] {
        border: none;
        background: none;
        color: #0068C9;
        margin-top: -8px;
    }
    button[kind="primary"]:hover {
        border: none;
        background: none;
        color: red;
    }
    </style>
""", unsafe_allow_html=True)

# if not simulation was run yet, show warning and 'go back' button
if "results" not in st.session_state or not st.session_state.results:
    st.warning("No results yet — run a simulation first.")
    if st.button("Go Back"):
        st.switch_page("main.py")
else:
    # table header row
    col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
    with col1: st.markdown("**Strategy**")
    with col2: st.markdown("**Stints**")
    with col3: st.markdown("**Total Time**")
    with col4: st.markdown("**Details**")

    st.divider()

    # loop thru each strategy result and add to row
    for i, result in enumerate(st.session_state.results):
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])

        with col1:
            # show trophy icon next to the fastest strategy
            if i == st.session_state.best_idx:
                st.markdown(f"🏆 **{i+1}**")
            else:
                st.markdown(f"**{i+1}**")

        with col2:
            # write the fastest strategy's stint in red, and others in plain text
            if i == st.session_state.best_idx:
                st.markdown("<br>".join([f"**:red[{s}]**" for s in result["Stints"].split("\n")]), unsafe_allow_html=True)
            else:
                st.markdown("<br>".join(result["Stints"].split("\n")), unsafe_allow_html=True)

        with col3:
            # write the fastest strategy's total time result in red, and others in plain text
            if i == st.session_state.best_idx:
                st.markdown(f":red[**{result['Total Time']}**] ✅")
            else:
                st.write(result["Total Time"])

        with col4:
            # toggle lap by lap breakdown button
            if st.button("Lap-by-Lap", key=f"lbl_{i}", type="primary"):
                st.session_state[f"show_lbl_{i}"] = not st.session_state.get(f"show_lbl_{i}", False)

        # show lap by lap predictions label if button toggled on
        if st.session_state.get(f"show_lbl_{i}", False):
            df_lbl = pd.DataFrame(st.session_state.lap_by_lap[i])
            df_lbl.index = df_lbl.index + 1
            st.table(df_lbl)

        st.divider()

    # nagivate back to simulator button
    if st.button("← Back to Simulator"):
        st.switch_page("main.py")