import streamlit as st
import pandas as pd
import plotly.express as px

import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestRegressor
st.title("🌳 SmartCool AI")

st.subheader("Urban Heat Mitigation Dashboard")

city = st.selectbox(
    "Select a City",
    ["Chennai", "Bengaluru", "Hyderabad"]
)
if city == "Chennai":
    df = pd.read_csv("heat_data.csv")

elif city == "Bengaluru":
    df = pd.read_csv("bengaluru_data.csv")

else:
    df = pd.read_csv("hyderabad_data.csv")
# Calculate Priority Score

df["Priority Score"] = (
    df["Temperature"] * 2
    + (1 - df["Vegetation"]) * 50
)

df["Priority Score"] = df["Priority Score"].round(0)


# AI Model Training

X = df[["Temperature", "Vegetation"]]

y = df["Priority Score"]

model = RandomForestRegressor(
    n_estimators=50,
    random_state=42
)

model.fit(X, y)

df["AI Predicted Score"] = model.predict(X).round(0)
st.subheader("📋 Heat Dataset")

st.dataframe(
    df[
        [
            "Area",
            "Temperature",
            "Vegetation",
            "Priority Score",
            "AI Predicted Score"
        ]
    ]
)
st.subheader("📈 Heat Risk Analysis")

fig = px.bar(
    df,
    x="Area",
    y="AI Predicted Score",
    color="AI Predicted Score",
    title="AI Predicted Heat Risk by Area"
)

st.plotly_chart(fig, use_container_width=True)


st.write(f"### 📍 Analysis for {city}")

col1, col2, col3 = st.columns(3)



avg_temp = round(df["Temperature"].mean(), 1)

avg_veg = round(df["Vegetation"].mean(), 2)

hotspots = len(df[df["Temperature"] >= 40])
with col1:
    st.metric(
        "Average Temperature",
        f"{avg_temp}°C"
    )

with col2:
    st.metric(
        "Heat Hotspots",
        hotspots
    )

with col3:
    st.metric(
        "Vegetation Index",
        avg_veg
    )

st.warning("⚠️ High Urban Heat Stress Detected")
st.subheader("🌳 Recommended Cooling Strategy")

highest_score = df["AI Predicted Score"].max()

if highest_score >= 120:
    action = "Increase Tree Cover by 20%"
    reduction = "3.0°C"
    priority = "HIGH"

elif highest_score >= 110:
    action = "Cool Roof Implementation"
    reduction = "1.8°C"
    priority = "MEDIUM"

else:
    action = "Routine Monitoring"
    reduction = "0.5°C"
    priority = "LOW"

st.success(f"""
Recommended Action:
{action}

Expected Temperature Reduction:
{reduction}

Priority:
{priority}
""")

st.subheader("🎛️ Cooling Intervention Simulator")

tree_cover = st.slider(
    "Increase Tree Cover (%)",
    0,
    30,
    15
)

predicted_reduction = round(tree_cover * 0.15, 2)

st.info(
    f"Estimated Temperature Reduction: {predicted_reduction}°C"
)

new_temperature = round(
    avg_temp - predicted_reduction,
    2
)

st.metric(
    "Predicted New Average Temperature",
    f"{new_temperature}°C"
) 
st.subheader("📊 Intervention Comparison")

comparison_data = {
    "Strategy": [
        "Increase Tree Cover",
        "Cool Roofs",
        "Trees + Cool Roofs"
    ],
    "Temperature Reduction": [
        "2.3°C",
        "1.4°C",
        "3.1°C"
    ],
    "Priority": [
        "Medium",
        "Medium",
        "High"
    ]
}

st.table(comparison_data)
st.subheader(f"🗺️ {city} Heat Hotspots")
st.markdown("""
### Risk Legend

🔴 High Risk (AI Score ≥ 120)

🟠 Medium Risk (AI Score 110–119)

🟢 Low Risk (AI Score < 110)
""")

# Create map centered on Chennai
m = folium.Map(
    location=[
        df["Latitude"].mean(),
        df["Longitude"].mean()
    ],
    zoom_start=11
)
# Example hotspot markers
# High Risk Hotspot
for index, row in df.iterrows():

    if row["AI Predicted Score"] >= 120:
        color = "red"
        risk = "High Risk"

    elif row["AI Predicted Score"] >= 110:
        color = "orange"
        risk = "Medium Risk"

    else:
        color = "green"
        risk = "Low Risk"

    folium.CircleMarker(
        location=[
            row["Latitude"],
            row["Longitude"]
        ],
        radius=10,
        popup=f"""
        <b>{row['Area']}</b><br>
        Temperature: {row['Temperature']}°C<br>
        Vegetation: {row['Vegetation']}<br>
        AI Score: {row['AI Predicted Score']}<br>
        Risk Level: {risk}
        """,
        color=color,
        fill=True,
        fill_color=color
    ).add_to(m)
# Display map
st_folium(m, width=700)

# NATIONAL LEADERBOARD

st.subheader("🇮🇳 National Heat Risk Leaderboard")

chennai_df = pd.read_csv("heat_data.csv")
bengaluru_df = pd.read_csv("bengaluru_data.csv")
hyderabad_df = pd.read_csv("hyderabad_data.csv")

india_df = pd.concat(
    [chennai_df, bengaluru_df, hyderabad_df],
    ignore_index=True
)

india_df["Priority Score"] = (
    india_df["Temperature"] * 2
    + (1 - india_df["Vegetation"]) * 50
)

top5 = india_df.sort_values(
    by="Priority Score",
    ascending=False
).head(5)

st.table(
    top5[
        [
            "Area",
            "City",
            "Priority Score"
        ]
    ]
)
st.subheader("📊 Top 5 Heat Risk Areas in India")

fig = px.bar(
    top5,
    x="Area",
    y="Priority Score",
    color="City",
    title="Highest Heat Risk Areas Across Cities"
)

st.plotly_chart(fig, width="stretch")

st.subheader("🏙️ City Heat Risk Comparison")

city_summary = india_df.groupby("City").agg({
    "Temperature": "mean",
    "Priority Score": "mean"
}).reset_index()

fig_city = px.bar(
    city_summary,
    x="City",
    y="Priority Score",
    color="City",
    title="Average Heat Risk by City"
)

st.plotly_chart(fig_city, width="stretch")

# EXISTING RANKING BELOW



st.subheader("🏆 Heat Mitigation Priority Ranking")

ranking_df = df.sort_values(
    by="AI Predicted Score",
    ascending=False
)

csv = ranking_df.to_csv(index=False)

st.download_button(
    label="📥 Download Heat Risk Report",
    data=csv,
    file_name=f"{city}_heat_report.csv",
    mime="text/csv"
)
st.table(
    ranking_df[
        [
            "Area",
            "AI Predicted Score"
        ]
    ]
)