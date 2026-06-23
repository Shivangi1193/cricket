import streamlit as st

import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from navbar import show_navbar
import pandas as pd
import json

st.set_page_config(
    page_title="Top Players",
    page_icon="📊",
    layout="wide"
)

show_navbar()


with open("data/players.json", "r", encoding="utf-8") as f:
    players = json.load(f)

with open("data/batting_stats.json", "r", encoding="utf-8") as f:
    batting_stats = json.load(f)

with open("data/bowling_stats.json", "r", encoding="utf-8") as f:
    bowling_stats = json.load(f)



st.subheader("🔍 Search Player")

player_names = sorted(
    [player["player_name"] for player in players]
)

selected_player = st.selectbox(
    "Enter Player Name",
    options=player_names,
    index=None,
    placeholder="Type player name..."
)

# -------------------------
# Player Profile
# -------------------------

if selected_player:

    player = next(
        p for p in players
        if p["player_name"] == selected_player
    )

    st.divider()

    st.header(f"👤 {player['player_name']}")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Role:**", player.get("role", "N/A"))
        st.write("**Country:**", player.get("country", "N/A"))
        st.write("**Batting Style:**", player.get("batting_style", "N/A"))

    with col2:
        st.write("**Bowling Style:**", player.get("bowling_style", "N/A"))
        st.write("**Birth Place:**", player.get("birth_place", "N/A"))
        st.write("**Keeper:**", player.get("is_keeper", False))

    # Player Batting Stats

    player_batting = pd.DataFrame(
        [
            row
            for row in batting_stats
            if row["player_id"] == player["player_id"]
        ]
    )

    if not player_batting.empty:

        st.subheader("🏏 Batting Statistics")

        st.dataframe(
            player_batting,
            use_container_width=True,
            hide_index=True
        )

    # Player Bowling Stats

    player_bowling = pd.DataFrame(
        [
            row
            for row in bowling_stats
            if row["player_id"] == player["player_id"]
        ]
    )

    if not player_bowling.empty:

        st.subheader("🎯 Bowling Statistics")

        st.dataframe(
            player_bowling,
            use_container_width=True,
            hide_index=True
        )

st.divider()

# -------------------------
# Top Players Section
# -------------------------

st.subheader("🏆 Current Leaders")

col1, col2 = st.columns(2)

# Top Batsmen
with col1:

    st.markdown("### 🏏 Top 5 Batsmen")

    top_batsmen = (
        pd.DataFrame(batting_stats)
        .sort_values(
            "runs",
            ascending=False
        )
        .drop_duplicates(
            subset=["player_id"]
        )
        .head(5)
    )

    st.dataframe(
        top_batsmen[
            [
                "player_name",
                "format",
                "runs",
                "strike_rate"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# Top Bowlers
with col2:

    st.markdown("### 🎯 Top 5 Bowlers")

    top_bowlers = (
        pd.DataFrame(bowling_stats)
        .sort_values(
            "wickets",
            ascending=False
        )
        .drop_duplicates(
            subset=["player_id"]
        )
        .head(5)
    )

    st.dataframe(
        top_bowlers[
            [
                "player_name",
                "format",
                "wickets",
                "average",
                "economy"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )
