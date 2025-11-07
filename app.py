import streamlit as st
import fastf1
import pandas as pd
import matplotlib.pyplot as plt

try:
    import tempfile
    fastf1.Cache.enable_cache(tempfile.gettempdir())
except Exception as e:
    st.warning("Couldn't enable fastf1 caching. Continuing without it.")
    st.write(e)

st.title ("F1 Data Dashboard")
st.write ("Analyse and compare driver and teams using different metrics.")

year= st.sidebar.selectbox("Select year",[2023,2024,2025])
try:
    schedule=  fastf1.get_event_schedule(year)
    gp_names= schedule["EventName"].tolist()
except Exception:
    gp_names= []
gp= st.sidebar.selectbox("Select Grand Prix", gp_names if gp_names else ["Monaco Grand Prix"])

analysis_type= st.sidebar.radio(
    "Select Analysis Type",
    ["Driver vs Driver", "Single Driver Consistency"],
)

@st.cache_data(show_spinner=True)
def load_laps(year,gp):
    try:
        session= fastf1.get_session(year,gp,"R")
        session.load()
        return session.laps
    except Exception as e:
        st.error(f"Could not load race data: {e}")
        return pd.DataFrame

if analysis_type == "Driver vs Driver":
    drivers= laps["Driver"].unique().tolist()
    selected = st.sidebar.multiselect("Select Two Drivers", drivers, max_selections=2)

    if len(selected) == 2:
        d1, d2 = selected
        laps1 = laps.pick_driver(d1)
        laps2 = laps.pick_driver(d2)

        laps1["LapTimeSec"] = laps1["LapTime"].dt.total_seconds()
        laps2["LapTimeSec"] = laps2["LapTime"].dt.total_seconds()

        roll1 = laps1["LapTimeSec"].rolling(5, min_periods=1).std()
        roll2 = laps2["LapTimeSec"].rolling(5, min_periods=1).std()

        plt.style.use("seaborn-v0_8-darkgrid")
        plt.figure(figsize=(10, 5))
        plt.plot(laps1["LapNumber"], roll1, label=f"{d1} rolling std (5 laps)")
        plt.plot(laps2["LapNumber"], roll2, label=f"{d2} rolling std (5 laps)")
        plt.xlabel("Lap Number")
        plt.ylabel("Rolling Standard Deviation (s)")
        plt.title(f"Consistency Comparison: {d1} vs {d2} — {gp} {year}")
        plt.legend()
        st.pyplot(plt)
        
if analysis_type == "Single Driver Consistency":
    drivers = laps["Driver"].unique().tolist()
    d = st.sidebar.selectbox("Select Driver", drivers)

    laps_d = laps.pick_driver(d)
    laps_d["LapTimeSec"] = laps_d["LapTime"].dt.total_seconds()

    roll = laps_d["LapTimeSec"].rolling(5, min_periods=1).std()

    plt.style.use("seaborn-v0_8-darkgrid")
    plt.figure(figsize=(10, 5))
    plt.plot(laps_d["LapNumber"], roll, label=f"{d} rolling std (5 laps)")
    plt.xlabel("Lap Number")
    plt.ylabel("Rolling Standard Deviation (s)")
    plt.title(f"{d} Consistency — {gp} {year}")
    plt.legend()
    st.pyplot(plt)
