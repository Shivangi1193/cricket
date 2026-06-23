
# navbar.py

import streamlit as st

def show_navbar():
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] a {
        text-decoration: none !important;
        text-align: center;
        padding: 10px 12px;
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.page_link("app.py", label="🏠 Home")

    with col2:
        st.page_link(
            "pages/A_Live_Matches.py",
            label="⚡ Live Matches"
        )

    with col3:
        st.page_link(
            "pages/B_Top_Player.py",
            label="📊 Top Players"
        )

    with col4:
        st.page_link(
            "pages/C_Insights_Trends.py",
            label="📈 Insights & Trends"
        )

    with col5:
        st.page_link(
            "pages/D_Data_control.py",
            label="🛠️ Data Control"
        )

    st.markdown("---")


    import json


def convert_batting_stats(data, player_id, player_name):
    formats = data["headers"][1:]  # Test, ODI, T20, IPL

    metric_map = {
        "Matches": "matches",
        "Innings": "innings",
        "Runs": "runs",
        "Balls": "balls",
        "HS": "highest",
        "Avg": "average",
        "SR": "strike_rate",
        "NO": "not_out",
        "4s": "fours",
        "6s": "sixes",
        "Ducks": "ducks",
        "50s": "fifties",
        "100s": "hundreds"
    }

    result = []

    for idx, fmt in enumerate(formats, start=1):

        row = {
            "player_id": player_id,
            "player_name": player_name,
            "format": fmt
        }

        for metric in data["values"]:
            metric_name = metric["values"][0]

            if metric_name in metric_map:
                value = metric["values"][idx]

                col_name = metric_map[metric_name]

                # Convert numeric values
                try:
                    if "." in str(value):
                        value = float(value)
                    else:
                        value = int(value)
                except:
                    pass

                row[col_name] = value

        result.append(row)

    return result

def convert_bowling_stats(data, player_id, player_name):
    formats = data["headers"][1:]  # Test, ODI, T20, IPL

    metric_map = {
        "Matches": "matches",
        "Innings": "innings",
        "Balls": "balls",
        "Runs": "runs",
        "Maidens": "maidens",
        "Wickets": "wickets",
        "Avg": "average",
        "Eco": "economy",
        "SR": "strike_rate",
        "BBI": "best_bowling_innings",
        "BBM": "best_bowling_match",
        "4w": "four_wickets",
        "5w": "five_wickets",
        "10w": "ten_wickets"
    }

    result = []

    for idx, fmt in enumerate(formats, start=1):

        row = {
            "player_id": player_id,
            "player_name": player_name,
            "format": fmt
        }

        for metric in data["values"]:

            metric_name = metric["values"][0]

            if metric_name in metric_map:

                value = metric["values"][idx]

                if metric_name not in ["BBI", "BBM"]:
                    try:
                        if "." in str(value):
                            value = float(value)
                        else:
                            value = int(value)
                    except:
                        pass

                row[metric_map[metric_name]] = value

        result.append(row)

    return result
