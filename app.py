import streamlit as st
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
fastf1.Cache.enable_cache(".cache")
st.title("Formula 1 Data Analysis Dashboard")


year = st.sidebar.selectbox("Select Year", [2023, 2024, 2025])
event_schedule = fastf1.get_event_schedule(year)
gp_names = event_schedule['EventName'].tolist()
gp = st.sidebar.selectbox("Select Grand Prix", gp_names)

@st.cache_data
def load_race(year, gp):
    session = fastf1.get_session(year, gp, 'R')
    session.load()
    return session

session = load_race(year, gp)

drivers = session.results['Driver'].unique()
selected_drivers = st.sidebar.multiselect("Select Drivers", drivers, max_selections=2)

if len(selected_drivers) == 2:
    df = session.laps
    fig, ax = plt.subplots()
    for driver in selected_drivers:
        laps = df.pick_driver(driver)
        lap_times = laps['LapTime'].dt.total_seconds()
        ax.plot(laps['LapNumber'], lap_times, label=driver)
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time (s)')
    ax.set_title(f'{selected_drivers[0]} vs {selected_drivers[1]} - {gp} {year}')
    ax.legend()
    st.pyplot(fig)
else:
    st.write("Please select two drivers to compare.")
