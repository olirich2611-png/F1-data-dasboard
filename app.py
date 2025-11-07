import streamlit as st
import fastf1
import pandas as pd
import plotly.graph_objects as go
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
        
        fig = go.Figure()

        fig.add_trace(go.Scatter(
           x=laps1["LapNumber"],
           y=roll1,
           mode="lines",
           name=f"{d1} rolling std (5 laps)"
        ))

        fig.add_trace(go.Scatter(
          x=laps2["LapNumber"],
          y=roll2,
          mode="lines",
          name=f"{d2} rolling std (5 laps)"
       ))

       fig.update_layout(
         title=f"Consistency Comparison: {d1} vs {d2} — {gp} {year}",
         xaxis_title="Lap Number",
         yaxis_title="Rolling Standard Deviation (s)",
         template="plotly_dark",          
         legend_title="Driver",
         width=1000,
         height=500
      )

      st.plotly_chart(fig, use_container_width=True)



    elif len(selected) < 2:
        st.info("👆 Please select two drivers to compare.")
    else:
        st.warning("⚠️ You selected more than two drivers. Please choose exactly two.")
