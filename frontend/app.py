import streamlit as st
import requests
import pandas as pd

st.title("🏏 Dream11 AI Team Predictor")
match_id = st.text_input("Enter Match ID from Cricbuzz (e.g., 74597):")

if st.button("Predict Team") and match_id:
    with st.spinner("Fetching data and predicting..."):
        response = requests.post(
            f"http://localhost:8000/predict-live-team/{match_id}")
        if response.status_code == 200:
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
        else:
            st.error("Failed to get prediction from backend.")
