import requests
import json
import os
import time
import sys
from navbar import convert_batting_stats, convert_bowling_stats

API_KEYS = [
    "8f41e97626msh3345fa983b84672p1d9757jsned2eb13e9264",
    "bca03b80a2mshcc7e09a32e41806p1445d4jsn2a51049c00cc",
    "984ea21795msh215a377894c6679p114480jsn8d51964727a3"
]

current_key_idx = 0

BASE_URL = "https://cricbuzz-cricket2.p.rapidapi.com"

os.makedirs("data", exist_ok=True)

def get_headers():
    return {
        "x-rapidapi-key": API_KEYS[current_key_idx],
        "x-rapidapi-host": "cricbuzz-cricket2.p.rapidapi.com",
        "Content-Type": "application/json"
    }

def get_data(endpoint):
    global current_key_idx
    while current_key_idx < len(API_KEYS):
        try:
            response = requests.get(BASE_URL + endpoint, headers=get_headers())
            if response.status_code == 429:
                response_text = response.text.lower()
                if "exceeded" in response_text or "quota" in response_text:
                    print(f" Key {current_key_idx + 1} exhausted its daily limit!")
                    current_key_idx += 1
                    if current_key_idx < len(API_KEYS):
                        continue  
                else:
                    time.sleep(5)
                    continue
            if response.status_code == 403:
                print(f"\n Key {current_key_idx + 1} is invalid or forbidden.")
                current_key_idx += 1
                if current_key_idx < len(API_KEYS):
                    continue
                else:
                    break

            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"Error in {endpoint}: {e}")
            return None
            
    print("\n CRITICAL: All API keys have been exhausted for the day, Please update the API_KEYS list with fresh keys and run again.")
    print(" All fetched data has already been saved to your JSON files.")
    sys.exit(0) 

def save_json(filename, data):
    with open(f"data/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
def load_json(filename):
    filepath = f"data/{filename}"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return []


existing_players_list = load_json("players.json")
existing_batting_players = load_json("batting_stats.json")
existing_bowling_players = load_json("bowling_stats.json")
players = {p["player_id"]: p for p in existing_players_list} 
teams = {t["team_id"]: t for t in load_json("teams.json")}
series = {s["series_id"]: s for s in load_json("series.json")}
matches = {m["match_id"]: m for m in load_json("matches.json")}
venues = {v["venue_id"]: v for v in load_json("venues.json")}
scorecards = load_json("scorecards.json")
batting_stats = {x["player_id"]for x in existing_batting_players}
bowling_stats = {x["player_id"]for x in existing_bowling_players}

rankings = load_json("rankings.json") if load_json("rankings.json") else {"batsmen": [], "bowlers": [], "allrounders": []}

print("Fetching Live Matches")
live = get_data("/matches/v1/live")
match_ids = []
if live:
    for type_match in live.get("typeMatches", []):
        for series_match in type_match.get("seriesMatches", []):
            if "seriesAdWrapper" not in series_match: continue
            wrapper = series_match["seriesAdWrapper"]
            series_id = wrapper["seriesId"]
            series[series_id] = {"series_id": series_id, "series_name": wrapper["seriesName"],"match_type":type_match.get("matchType", "")}
            save_json("series.json", list(series.values()))
            for match in wrapper.get("matches", []):
                match_state = match.get("matchInfo", {}).get("state", "")
                if match_state in ["Complete", "Abandon"]: continue
                match_ids.append(match["matchInfo"]["matchId"])

print(f"Found {len(match_ids)} active matches.")
for match_id in match_ids:
    print(f"Fetching details for Match {match_id}")
    data = get_data(f"/mcenter/v1/{match_id}")
    if not data: continue
    team1, team2 = data["team1"], data["team2"]
    venue = data['venueinfo']
    teams[team1["teamid"]] = {"team_id": team1["teamid"], "team_name": team1["teamname"], "short_name": team1["teamsname"]}
    teams[team2["teamid"]] = {"team_id": team2["teamid"], "team_name": team2["teamname"], "short_name": team2["teamsname"]}
    venues[venue["id"]] = {"venue_id": venue["id"], "ground": venue["ground"], "city": venue["city"], "timezone": venue["timezone"]}
    matches[match_id] = {
        "match_id": match_id, "series_id": data["seriesid"],
        "team1_id": team1["teamid"], "team2_id": team2["teamid"],
        "venue_id": venue["id"], "status": data["status"]
    }
    scorecard = get_data(f"/mcenter/v1/{match_id}/scard")
    if scorecard:
        for innings in scorecard.get("scorecard", []):
            scorecards.append({
                "match_id": match_id, "innings_id": innings.get("inningsid"),
                "bat_team_name": innings.get("batteamname"), "score": innings.get("score"),
                "wickets": innings.get("wickets"), "overs": innings.get("overs")
            })
            for bat in innings.get("batsman", []):
                pid = bat["id"]
                if pid not in players:
                    players[pid] = {"player_id": pid, "player_name": bat["name"], "is_captain": bat.get("iscaptain"), "is_keeper": bat.get("iskeeper")}
                    
            for bowl in innings.get("bowler", []):
                pid = bowl["id"]
                if pid not in players:
                    players[pid] = {"player_id": pid, "player_name": bowl["name"], "is_captain": bowl.get("iscaptain"), "is_keeper": bowl.get("iskeeper")}

    save_json("teams.json", list(teams.values()))
    save_json("venues.json", list(venues.values()))
    save_json("matches.json", list(matches.values()))
    save_json("scorecards.json", scorecards)
    save_json("players.json", list(players.values()))

players_updated = 0
for pid, p_data in players.items():
    if "role" not in p_data or not p_data["role"]:
        print(f"Fetching biography for Player ID: {pid}...")
        player_info = get_data(f"/stats/v1/player/{pid}")
        batting_data= get_data(f"/stats/v1/player/{pid}/batting")
        bowling_data= get_data(f"/stats/v1/player/{pid}/bowling")
        
        if batting_data:
            batting_stats.extend(convert_batting_stats(batting_data,pid,p_data["player_name"]))
            save_json("batting_stats.json", batting_stats)

        if bowling_data:
            bowling_stats.extend(convert_bowling_stats(bowling_data,pid,p_data["player_name"]))
            save_json("bowling_stats.json", bowling_stats)

        if player_info:
            players[pid].update({
                "role": player_info.get("role"), "batting_style": player_info.get("battingStyle"),
                "bowling_style": player_info.get("bowlingStyle"), "birth_place": player_info.get("birthPlace"),
                "country": player_info.get("intlTeam")
            })
            save_json("players.json", list(players.values()))
            players_updated += 1

print(f" Downloaded full biographies for {players_updated} new players.")

# Uncomment these if you want to fetch rankings.
# print("\nFetching Rankings")
# rankings["batsmen"] = get_data("/stats/v1/rankings/batsmen?formatType=odi")
# rankings["bowlers"] = get_data("/stats/v1/rankings/bowlers?formatType=odi")
# rankings["allrounders"] = get_data("/stats/v1/rankings/allrounders?formatType=odi")
# save_json("rankings.json", rankings)
