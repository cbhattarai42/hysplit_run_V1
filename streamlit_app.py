# streamlit_app.py

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from datetime import datetime
import os

st.set_page_config(page_title="HYSPLIT Trajectory Viewer", layout="wide")

st.title("🛰️ HYSPLIT Trajectory Viewer")
st.markdown("Upload your HYSPLIT trajectory file (.tdump) and visualize it on an interactive map.")

# Upload .tdump file
tdump_file = st.file_uploader("Upload HYSPLIT .tdump file", type=["tdump"])

def parse_tdump(file):
    lines = file.readlines()
    header_lines = 8
    data = []
    for line in lines[header_lines:]:
        parts = line.decode("utf-8").split()
        if len(parts) >= 10:
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

if tdump_file:
    df = parse_tdump(tdump_file)
    st.success("Trajectory file loaded successfully.")
    
    # Show basic stats
    st.write("Trajectory Summary:")
    st.dataframe(df.describe())

    # Create map
    m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=5)
    traj_groups = df.groupby("traj_num")

    for traj_id, group in traj_groups:
        points = list(zip(group["lat"], group["lon"]))
        folium.PolyLine(points, color="blue", weight=2.5, opacity=0.8, tooltip=f"Trajectory {traj_id}").add_to(m)
        folium.Marker(points[0], popup=f"Start of Trajectory {traj_id}", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(points[-1], popup=f"End of Trajectory {traj_id}", icon=folium.Icon(color="red")).add_to(m)

    st.markdown("### 🌍 Trajectory Map")
    st.components.v1.html(m._repr_html_(), height=600, scrolling=True)

else:
    st.info("Please upload a .tdump file to begin.")

