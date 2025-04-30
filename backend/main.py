from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Dream11 AI Team Predictor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model
try:
    model = joblib.load('model.joblib')
except FileNotFoundError:
    model = None


@app.get("/")
async def root():
    return {"message": "Dream11 AI Team Predictor API is running"}


@app.post("/predict-live-team/{team1_code}/{team2_code}/{match_number}")
async def predict_live_team(team1_code: str, team2_code: str, match_number: int):
    try:
        # TODO: Implement the actual prediction logic here
        # This is a placeholder response
        return {
            "players": [
                {"name": "Player1", "predicted_points": 85.5},
                {"name": "Player2", "predicted_points": 78.2},
                # Add more players as needed
            ],
            "team": ["Player1", "Player2"]  # Selected team
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
