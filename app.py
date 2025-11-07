import streamlit as st
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import tempfile  # to use Streamlit-safe temporary cache folder

try:
    fastf1.Cache.enable_cache(tempfile.gettempdir())  
except Exception as e:
    st.warning("Could not enable FastF1 cache. Continuing without it.")
    st.write(e)

st.title("Formula 1 Data Dashboard")
st.write("Analyse driver and team consistency with FastF1 data.")

year = st.sidebar.selectbox("Select Year", [2023, 2024, 2025])

try:
    schedule = fastf1.get_event_schedule(year)
    gp_names = schedule["EventName"].tolist()
except Exception as e:
    gp_names = []
    st.warning(f"Could not load race schedule: {e}")

gp = st.sidebar.selectbox("Select Grand Prix", gp_names if gp_names else ["Monaco Grand Prix"])

analysis_type = st.sidebar.radio(
    "Select Analysis Type",
    ["Driver vs Driver", "Single Driver Consistency"],
)

@st.cache_data(show_spinner=True)
def load_laps(year, gp):
    try:
        session = fastf1.get_session(year, gp, "R")
        session.load()
        return session.laps
    except Exception as e:
        st.error(f"Could not load race data: {e}")
        return pd.DataFrame()  # always return something

laps = load_laps(year, gp)

if laps.empty:
    st.warning("No lap data found for this race. Please try another event.")
    st.stop()

if analysis_type == "Driver vs Driver":
    drivers = laps["Driver"].unique().tolist()
    selected = st.sidebar.multiselect("Select up to two drivers", drivers)

    if len(selected) == 2:
        d1, d2 = selected
        laps1 = laps.pick_driver(d1)
        laps2 = laps.pick_driver(d2)

        laps1["LapTimeSec"] = laps1["LapTime"].dt.total_seconds()
        laps2["LapTimeSec"] = laps2["LapTime"].dt.total_seconds()

        roll1 = laps1["LapTimeSec"].rolling(5, min_periods=1).std()
        roll2 = laps2["LapTimeSec"].rolling(5, min_periods=1).std()

        plt.style.use("seaborn-v0_8-darkgrid")
        plt.rcParams.update({
            "figure.figsize": (12, 6),       # bigger figure
            "figure.dpi": 100,               # good balance for Streamlit
            "axes.labelsize": 12,
            "axes.titlesize": 14,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
        })

fig, ax = plt.subplots()

ax.plot(laps1["LapNumber"], roll1, label=f"{d1} rolling std (5 laps)", linewidth=1.8)
ax.plot(laps2["LapNumber"], roll2, label=f"{d2} rolling std (5 laps)", linewidth=1.8)
ax.set_xlabel("Lap Number")
ax.set_ylabel("Rolling Standard Deviation (s)")
ax.set_title(f"Consistency Comparison: {d1} vs {d2} — {gp} {year}")
ax.legend()

st.pyplot(fig, clear_figure=True, use_container_width=True)
        
plt.figure(figsize=(10, 5), dpi=150) 
plt.plot(laps1["LapNumber"], roll1, label=f"{d1} rolling std (5 laps)")
plt.plot(laps2["LapNumber"], roll2, label=f"{d2} rolling std (5 laps)")
plt.xlabel("Lap Number")
plt.ylabel("Rolling Standard Deviation (s)")
plt.title(f"Consistency Comparison: {d1} vs {d2} — {gp} {year}")
plt.legend()
st.pyplot(plt)

elif len(selected) < 2:
       st.info("Please select two drivers to compare.")
else:
       st.warning("You selected more than two drivers. Please choose exactly two.")

