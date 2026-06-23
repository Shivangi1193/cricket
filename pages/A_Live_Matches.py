import streamlit as st
import live as live_data
from navbar import show_navbar

st.set_page_config(
    page_title="Live Matches",
    page_icon="⚡",
    layout="wide"
)

show_navbar()

st.title("⚡ Live Matches")

st.info("This section will display live match data from Cricbuzz API.")

matches = ["International", "League", "Domestic", "Women"]

st.markdown(
    "<h3 style='font-weight:bold; color:#00BFFF;'>Matches</h3>",
    unsafe_allow_html=True
)

# Initialize session state
if "selected_match_type" not in st.session_state:
    st.session_state.selected_match_type = None

# Match type buttons
cols = st.columns(len(matches))

for col, match_type in zip(cols, matches):
    with col:
        if st.button(match_type):
            st.session_state.selected_match_type = match_type

selected = st.session_state.selected_match_type

if selected:
    st.markdown(
        f"<h4 style='color:#FFD700;'>Ongoing Series - {selected}</h4>",
        unsafe_allow_html=True
    )

    series_list = live_data.series_list(selected)

    series = st.selectbox(
        "Select Series",
        series_list,
        key="series_select"
    )

    if series:
        st.markdown(
            f"<h4 style='color:#FFD700;'>Ongoing Matches - {series}</h4>",
            unsafe_allow_html=True
        )

        matches_list = live_data.match_list(series)

        if matches_list:
            match = st.selectbox(
                "Select Match",
                matches_list,
                key="match_select"
            )

            if match:
                st.markdown(
                    f"<h4 style='color:#FFD700;'>Match Details - {match}</h4>",
                    unsafe_allow_html=True
                )

                match_info = live_data.match_details(match)
                st.caption("⚡ LIVE MATCH DETAILS")
                col_header1, col_header2 = st.columns([3, 1])
                with col_header1:
                    st.title(match_info['teams'])
                    st.caption(f"🏟️ {match_info['venue']}")
                with col_header2:
                    st.info(match_info['status'])
                st.divider()               
                col_score1, col_score2 = st.columns(2)
                with col_score1:
                    st.metric(
                        label=f"{match_info['teamA'].upper()}",
                        value=match_info['teamAScore'],
                        delta=f"({match_info['teamAOvers']} Ov)",
                        delta_color="off" )
                with col_score2:
                    st.metric(
                        label=f"{match_info['teamB'].upper()}",
                        value=match_info['teamBScore'],
                        delta=f"({match_info['teamBOvers']} Ov)",
                        delta_color="off")
        else:
            st.warning("No ongoing matches found for the selected series.")