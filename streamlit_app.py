# hysplit_app.py

import streamlit as st
import pandas as pd
import folium
from datetime import datetime
import os
import subprocess

st.set_page_config(page_title="HYSPLIT Trajectory Tool", layout="wide")
st.title("🛰️ HYSPLIT Trajectory Generator and Viewer")

# --- User Inputs ---
st.sidebar.header("Trajectory Settings")

date_input = st.sidebar.date_input("Start Date", value=datetime.today())
time_input = st.sidebar.time_input("Start Time", value=datetime.now().time())
lat = st.sidebar.number_input("Latitude", value=40.0)
lon = st.sidebar.number_input("Longitude", value=-75.0)
height = st.sidebar.number_input("Starting Height (m)", value=500)
duration = st.sidebar.number_input("Duration (hours)", value=24)
direction = st.sidebar.selectbox("Trajectory Direction", ["Backward", "Forward"])
met_type = st.sidebar.selectbox("Meteorological File Type", ["GFS", "NAM", "RAP"])

run_button = st.sidebar.button("Run HYSPLIT")

# --- HYSPLIT Execution ---
def run_hysplit(date, time, lat, lon, height, duration, direction, met_type):
    # Format date/time
    year = date.year % 100
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"
    hour = f"{time.hour:02d}"

    # Create CONTROL file
    control_text = f"""{year} {month} {day} {hour}
1
{lat} {lon} {height}
{duration}
0
{direction[0].lower()}
1
{met_type}
"""
    with open("CONTROL", "w") as f:
        f.write(control_text)

    # Run HYSPLIT (assumes hysplit executable is in PATH)
    subprocess.run(["hyts_std"], check=True)

    # Read output
    with open("tdump", "r") as f:
        lines = f.readlines()[8:]  # skip header
    data = []
    for line in lines:
        parts = line.split()
        data.append({
            "traj_num": int(parts[0]),
            "year": int(parts[1]),
            "month": int(parts[2]),
            "day": int(parts[3]),
            "hour": int(parts[4]),
            "forecast_hour": int(parts[5]),
            "lat": float(parts[6]),
            "lon": float(parts[7]),
            "height": float(parts[8])
        })
    return pd.DataFrame(data)

# --- Run and Plot ---
if run_button:
    try:
        df = run_hysplit(date_input, time_input, lat, lon, height, duration, direction, met_type)
        st.success("Trajectory generated successfully.")

        # Plot map
        m = folium.Map(location=[lat, lon], zoom_start=6)
        traj_groups = df.groupby("traj_num")

        for traj_id, group in traj_groups:
            points = list(zip(group["lat"], group["lon"]))
            folium.PolyLine(points, color="blue", weight=2.5, opacity=0.8, tooltip=f"Trajectory {traj_id}").add_to(m)
            folium.Marker(points[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
            folium.Marker(points[-1], popup="End", icon=folium.Icon(color="red")).add_to(m)

        st.markdown("### 🌍 Trajectory Map")
        st.components.v1.html(m._repr_html_(), height=600, scrolling=True)

    except Exception as e:
        st.error(f"Error running HYSPLIT: {e}")
