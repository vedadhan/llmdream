import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


def extract_scorecard(match_url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(match_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    batting_stats = []
    bowling_stats = []

    # Extract venue and pitch information
    venue_info = "NA"
    pitch_condition = "NA"

    # Extract venue with multiple possible selectors
    venue_selectors = [
        "span.cb-font-12.text-gray",
        "div.cb-col.cb-col-100.cb-minfo-tm-nm",
        "div.cb-col.cb-col-100.cb-minfo-tm-nm span",
        "div.cb-col.cb-col-100.cb-minfo-tm-nm div"
    ]

    for selector in venue_selectors:
        venue_section = soup.select_one(selector)
        if venue_section and venue_section.text.strip():
            venue_text = venue_section.text.strip()
            # Clean up the venue text
            venue_text = venue_text.replace("Venue:", "").strip()
            venue_text = venue_text.replace("at", "").strip()
            if venue_text and len(venue_text) > 3:  # Basic validation
                venue_info = venue_text
                break

    # Extract pitch condition
    pitch_section = soup.find("div", class_="cb-col cb-col-100 cb-minfo-tm-nm")
    if pitch_section:
        pitch_text = pitch_section.text.strip().lower()
        if any(word in pitch_text for word in ["batting", "good for batting", "flat"]):
            pitch_condition = "Batting Friendly"
        elif any(word in pitch_text for word in ["bowling", "good for bowling", "seaming", "spinning"]):
            pitch_condition = "Bowling Friendly"
        else:
            pitch_condition = "Balanced"

    # Extract batting statistics
    innings_blocks = soup.find_all(
        "div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")

    if not innings_blocks:
        print(
            "⚠️ Could not find innings blocks. The page may have changed or is JS-rendered.")
        return pd.DataFrame(), pd.DataFrame()

    for block in innings_blocks:
        team_header = block.find("span")
        if not team_header:
            continue
        team_name = team_header.text.strip()

        # Extract batting stats
        rows = block.find_all("div", class_="cb-col cb-col-100 cb-scrd-itms")
        for row in rows:
            cols = row.find_all("div")
            if len(cols) >= 7:
                player_name = cols[0].text.strip()
                if player_name in ["Extras", "Total"]:
                    continue
                runs = cols[2].text.strip()
                balls = cols[3].text.strip()
                fours = cols[5].text.strip()
                sixes = cols[6].text.strip()
                sr = cols[7].text.strip() if len(cols) > 7 else "NA"

                batting_stats.append({
                    "Player": player_name,
                    "Team": team_name,
                    "Runs": runs,
                    "Balls": balls,
                    "4s": fours,
                    "6s": sixes,
                    "Strike Rate": sr,
                    "Venue": venue_info,
                    "Pitch Condition": pitch_condition
                })

        # Extract bowling stats
        print(f"\n🔍 Looking for bowling section for team: {team_name}")

        # Try different ways to find the bowling section
        bowling_section = None

        # Method 1: Look for bowling header
        bowling_header = block.find(
            "div", class_="cb-col cb-col-100 cb-scrd-sub-hdr")
        if bowling_header and ("Bowler" in bowling_header.text or "BOWLING" in bowling_header.text):
            print("Found bowling section using header")
            bowling_section = bowling_header

        # Method 2: Look for bowling stats rows
        if not bowling_section:
            bowling_rows = block.find_all(
                "div", class_="cb-col cb-col-100 cb-scrd-itms")
            for row in bowling_rows:
                if row.find("a", class_="cb-text-link") and len(row.find_all("div", class_="cb-col")) >= 8:
                    print("Found bowling section using rows")
                    bowling_section = row.find_previous(
                        "div", class_="cb-col cb-col-100 cb-scrd-sub-hdr")
                    break

        if bowling_section:
            print("Processing bowling section")
            # Get all rows after the bowling section
            current_row = bowling_section.find_next(
                "div", class_="cb-col cb-col-100 cb-scrd-itms")
            while current_row and not current_row.find("div", class_="cb-col cb-col-100 cb-scrd-sub-hdr"):
                try:
                    # Extract player name
                    player_link = current_row.find("a", class_="cb-text-link")
                    if player_link:
                        player_name = player_link.text.strip()
                        print(f"Processing bowler: {player_name}")

                        # Extract bowling stats
                        cols = current_row.find_all("div", class_="cb-col")
                        if len(cols) >= 8:
                            overs = cols[1].text.strip()
                            maidens = cols[2].text.strip()
                            runs_given = cols[3].text.strip()
                            wickets = cols[4].text.strip()
                            noballs = cols[5].text.strip()
                            wides = cols[6].text.strip()
                            economy = cols[7].text.strip()

                            bowling_stats.append({
                                "Player": player_name,
                                "Team": team_name,
                                "Overs": overs,
                                "Maidens": maidens,
                                "Runs Given": runs_given,
                                "Wickets": wickets,
                                "No Balls": noballs,
                                "Wides": wides,
                                "Economy": economy,
                                "Venue": venue_info,
                                "Pitch Condition": pitch_condition
                            })
                            print(f"Added bowling stats for {player_name}")
                except Exception as e:
                    print(f"Error processing bowling row: {e}")

                # Move to next row
                current_row = current_row.find_next(
                    "div", class_="cb-col cb-col-100 cb-scrd-itms")
        else:
            print("Could not find bowling section")

    return pd.DataFrame(batting_stats), pd.DataFrame(bowling_stats)


def save_to_csv(df, filename, match_url):
    if df.empty:
        print(f"❌ No data extracted for {filename}.")
        return
    os.makedirs("data", exist_ok=True)
    # Extract match identifier from URL
    match_id = match_url.split('/')[-1]
    full_filename = f"{match_id}_{filename}"
    df.to_csv(os.path.join("data", full_filename), index=False)
    print(f"✅ Scorecard saved to data/{full_filename}")


# Example match URL from Cricbuzz
match_url = "https://www.cricbuzz.com/live-cricket-scorecard/115282/csk-vs-pbks-49th-match-indian-premier-league-2025"

# Extract both batting and bowling statistics
batting_df, bowling_df = extract_scorecard(match_url)

# Save batting statistics to a separate CSV file
save_to_csv(batting_df, "batting.csv", match_url)

# Save bowling statistics to a separate CSV file
save_to_csv(bowling_df, "bowling.csv", match_url)
