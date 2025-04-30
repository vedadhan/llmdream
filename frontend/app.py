import streamlit as st
import requests
import pandas as pd
import traceback

st.title("🏏 Dream11 AI Team Predictor")

# Add IPL season selection
season = st.selectbox(
    "Select IPL Season",
    ["2025", "2024", "2023", "2022", "2021", "2020"]
)

# Add match number input
match_number = st.number_input(
    "Enter IPL Match Number",
    min_value=1,
    max_value=74,  # Maximum matches in an IPL season
    value=1,
    step=1
)

if st.button("Predict Team"):
    with st.spinner("Fetching data and predicting..."):
        try:
            response = requests.post(
                f"http://localhost:8000/predict-live-team/{season}/{match_number}",
                timeout=10  # Add timeout
            )
            response.raise_for_status()  # Raise exception for bad status codes

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
