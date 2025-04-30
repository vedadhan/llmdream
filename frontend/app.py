import streamlit as st
import requests
import pandas as pd
import traceback

st.title("🏏 Dream11 AI Team Predictor")

# Define IPL teams
ipl_teams = [
    "Chennai Super Kings (CSK)",
    "Royal Challengers Bangalore (RCB)",
    "Mumbai Indians (MI)",
    "Kolkata Knight Riders (KKR)",
    "Delhi Capitals (DC)",
    "Punjab Kings (PBKS)",
    "Rajasthan Royals (RR)",
    "Sunrisers Hyderabad (SRH)",
    "Lucknow Super Giants (LSG)",
    "Gujarat Titans (GT)"
]

# Create two columns for team selection
col1, col2 = st.columns(2)

with col1:
    team1 = st.selectbox(
        "Select First Team",
        ipl_teams,
        index=0
    )

with col2:
    # Filter out the selected team1 from options
    remaining_teams = [team for team in ipl_teams if team != team1]
    team2 = st.selectbox(
        "Select Second Team",
        remaining_teams,
        index=0
    )

# Add match number input
match_number = st.number_input(
    "Enter Match Number",
    min_value=1,
    max_value=74,  # Maximum matches in an IPL season
    value=1,
    step=1
)

if st.button("Predict Team"):
    with st.spinner("Fetching data and predicting..."):
        try:
            # Extract team codes from the selected teams
            team1_code = team1.split("(")[1].replace(")", "").strip()
            team2_code = team2.split("(")[1].replace(")", "").strip()

            response = requests.post(
                f"http://localhost:8000/predict-live-team/{team1_code}/{team2_code}/{match_number}",
                timeout=10
            )
            response.raise_for_status()

            result = response.json()
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success("Optimal team predicted successfully!")
                team_df = pd.DataFrame(result["players"])
                selected_team = result["team"]

                st.subheader("🔝 Selected Dream11 Team")
                st.table(team_df[team_df["name"].isin(selected_team)])

                st.subheader("📋 All Players with Predicted Points")
                st.dataframe(team_df.sort_values(
                    by="predicted_points", ascending=False))
        except requests.exceptions.RequestException as e:
            st.error(
                f"Failed to connect to the backend server. Please make sure the backend is running.")
            st.error(f"Error details: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.error(f"Error details: {traceback.format_exc()}")
