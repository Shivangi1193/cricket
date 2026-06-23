import json
import time
import requests

#api details
HEADERS = {
	"x-rapidapi-key": "9d9676e5d8mshd78eca9f9a7138ap1a9c04jsn25f0562d21dc",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
	"Content-Type": "application/json"
}

BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"

session = requests.Session()
session.headers.update(HEADERS)


# ==========================
# API CALL
# ==========================
def get_data(endpoint, retries=5):

    url = BASE_URL + endpoint

    for attempt in range(retries):

        try:

            response = session.get(
                url,
                timeout=30
            )

            if response.status_code == 429:

                wait_time = 15 * (attempt + 1)

                print(
                    f"Rate limit reached. Waiting {wait_time} seconds..."
                )

                time.sleep(wait_time)

                continue

            response.raise_for_status()

            time.sleep(1)

            return response.json()

        except Exception as e:

            print(
                f"Attempt {attempt+1} failed: {e}"
            )

            time.sleep(10)

    return None


# ==========================
# LOAD PLAYERS
# ==========================
with open(
    "data/players.json",
    "r",
    encoding="utf-8"
) as f:

    players = json.load(f)

print(f"{len(players)} players loaded")

updated = 0


# ==========================
# DOWNLOAD DETAILS
# ==========================
for player in players:

    # Skip already downloaded players
    if "role" in player:
        continue

    pid = player["player_id"]

    print(f"Fetching {pid}")

    data = get_data(
        f"/stats/v1/player/{pid}"
    )

    if data is None:
        continue

    player["full_name"] = data.get("name")
    player["nick_name"] = data.get("nickName")

    player["role"] = data.get("role")

    player["batting_style"] = data.get(
        "battingStyle"
    )

    player["bowling_style"] = data.get(
        "bowlingStyle"
    )

    player["birth_place"] = data.get(
        "birthPlace"
    )

    player["date_of_birth"] = data.get(
        "DoB"
    )

    player["height"] = data.get(
        "height"
    )

    player["country"] = data.get(
        "intlTeam"
    )

    player["bio"] = data.get(
        "bio"
    )

    updated += 1

    # Save every 25 players
    if updated % 25 == 0:

        with open(
            "data/players.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                players,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"{updated} players saved")


# ==========================
# FINAL SAVE
# ==========================
with open(
    "data/players.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        players,
        f,
        indent=4,
        ensure_ascii=False
    )
