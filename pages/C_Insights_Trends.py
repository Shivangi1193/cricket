import streamlit as st
import sqlite3
import pandas as pd
from navbar import show_navbar

# 1. Page Configuration
st.set_page_config(
    page_title="Insights & Trends",
    page_icon="📈",
    layout="wide"
)

show_navbar()

st.title("📈 Cricket Insights & Trends Dashboard")
st.write("Select a question from the categories below to run real-time SQL analysis on `cricket.db`.")

# 2. Database Helper Function
DB_NAME = "cricket.db"

def run_query(query):
    """Executes a SQL query against cricket.db and returns a pandas DataFrame."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql_query(query, conn)
            return df
    except sqlite3.Error as e:
        st.error(f"SQL Error: {e}")
        return None

# 3. Define Questions and their Respective SQL Queries
queries = {
    # --- BEGINNER LEVEL ---
    "Question 1: Find all players who represent India": """
        SELECT player_name, role, batting_style, bowling_style 
        FROM players 
        WHERE LOWER(country) = 'india';
    """,
    "Question 2: Show all matches and their locations": """
        SELECT m.match_id, s.series_name, t1.team_name AS team1, t2.team_name AS team2, v.ground, v.city, m.status
        FROM matches m
        LEFT JOIN series s ON m.series_id = s.series_id
        LEFT JOIN teams t1 ON m.team1_id = t1.team_id
        LEFT JOIN teams t2 ON m.team2_id = t2.team_id
        LEFT JOIN venues v ON m.venue_id = v.venue_id;
    """,
    "Question 3: Top 10 highest run-scorers in ODI cricket": """
        SELECT player_name, runs, (CAST(runs AS REAL) / NULLIF(innings, 0)) AS batting_average, fifties, hundreds
        FROM batting_stats
        WHERE format = 'ODI'
        ORDER BY runs DESC
        LIMIT 10;
    """,
    "Question 4: Display all unique cricket venues categorized by city": """
        SELECT ground, city, timezone 
        FROM venues 
        ORDER BY city ASC;
    """,
    "Question 5: Calculate match innings entries completed per team": """
        SELECT bat_team_name AS team_name, COUNT(*) AS total_innings_played, SUM(score) AS total_runs_scored
        FROM scorecards
        GROUP BY bat_team_name
        ORDER BY total_runs_scored DESC;
    """,
    "Question 6: Count players belonging to each playing role": """
        SELECT role, COUNT(*) AS player_count
        FROM players
        WHERE role IS NOT NULL AND role != ''
        GROUP BY role
        ORDER BY player_count DESC;
    """,
    "Question 7: Highest individual tournament runs recorded by format": """
        SELECT format, MAX(runs) AS highest_accumulated_runs, player_name
        FROM batting_stats
        GROUP BY format;
    """,
    "Question 8: Show series details by international match types": """
        SELECT series_name, match_type
        FROM series
        ORDER BY match_type DESC;
    """,

    # --- INTERMEDIATE LEVEL ---
    "Question 9: Find players with substantial runs and wickets across formats": """
        SELECT bat.player_name, bat.format, bat.runs, bowl.wickets
        FROM batting_stats bat
        JOIN bowling_stats bowl ON bat.player_id = bowl.player_id AND bat.format = bowl.format
        WHERE bat.runs > 1000 AND bowl.wickets > 30
        ORDER BY bat.runs DESC;
    """,
    "Question 10: Get scorecard details of high-scoring innings matches": """
        SELECT s.match_id, s.bat_team_name, s.score, s.wickets, s.overs, m.status
        FROM scorecards s
        JOIN matches m ON s.match_id = m.match_id
        WHERE s.score >= 200
        ORDER BY s.score DESC;
    """,
    "Question 11: Compare player performances across multiple formats": """
        SELECT player_name, 
               SUM(CASE WHEN format = 'Test' THEN runs ELSE 0 END) AS Test_Runs,
               SUM(CASE WHEN format = 'ODI' THEN runs ELSE 0 END) AS ODI_Runs,
               SUM(CASE WHEN format = 'T20' OR format = 'T20I' THEN runs ELSE 0 END) AS T20_Runs,
               AVG(strike_rate) AS avg_strike_rate
        FROM batting_stats
        GROUP BY player_id, player_name
        HAVING COUNT(DISTINCT format) >= 2;
    """,
    "Question 12: Analyze matches hosted per specific ground venue location": """
        SELECT v.ground, v.city, COUNT(m.match_id) AS total_matches_hosted
        FROM venues v
        JOIN matches m ON v.venue_id = m.venue_id
        GROUP BY v.venue_id
        ORDER BY total_matches_hosted DESC;
    """,
    "Question 13: High scorecard performance stats mapping per innings": """
        SELECT match_id, innings_id, bat_team_name, score, wickets
        FROM scorecards
        WHERE score >= 150
        ORDER BY score DESC, wickets ASC;
    """,
    "Question 14: Examine bowler economy rates across formats": """
        SELECT player_name, format, matches, wickets, economy, average
        FROM bowling_stats
        WHERE matches >= 5 AND economy > 0
        ORDER BY economy ASC;
    """,
    "Question 15: Identify players with multiple ducks across formats": """
        SELECT player_name, format, matches, ducks
        FROM batting_stats
        WHERE ducks > 0
        ORDER BY ducks DESC, matches ASC;
    """,
    "Question 16: Track aggregate runs and centuries achieved by country origin": """
        SELECT p.country, COUNT(DISTINCT p.player_id) AS active_players, SUM(b.runs) AS aggregate_runs, SUM(b.hundreds) AS total_centuries
        FROM players p
        JOIN batting_stats b ON p.player_id = b.player_id
        GROUP BY p.country
        ORDER BY aggregate_runs DESC;
    """,

    # --- ADVANCED LEVEL ---
    "Question 17: Performance conversion index of multi-format centuries vs ducks": """
        SELECT player_name, SUM(hundreds) AS total_hundreds, SUM(ducks) AS total_ducks,
               (CAST(SUM(hundreds) AS REAL) / NULLIF(SUM(ducks), 0)) AS conversion_ratio
        FROM batting_stats
        GROUP BY player_id
        HAVING total_hundreds > 0 OR total_ducks > 0
        ORDER BY total_hundreds DESC;
    """,
    "Question 18: Find elite economical bowlers in limited-overs formats": """
        SELECT player_name, format, matches, wickets, economy
        FROM bowling_stats
        WHERE format IN ('ODI', 'T20', 'T20I') AND matches >= 10 AND economy BETWEEN 1.0 AND 5.5
        ORDER BY economy ASC, wickets DESC;
    """,
    "Question 19: Determine consistent scoring batsmen with stable century outputs": """
        SELECT player_name, SUM(matches) AS total_matches, SUM(runs) AS total_runs, SUM(hundreds) AS total_hundreds
        FROM batting_stats
        GROUP BY player_id
        HAVING total_runs > 500 AND total_hundreds >= 1
        ORDER BY total_hundreds DESC, total_runs DESC;
    """,
    "Question 20: Cross-examination of batting versus bowling match appearances": """
        SELECT p.player_name, p.role, p.country, 
               COALESCE(SUM(b.matches), 0) AS batting_caps, 
               COALESCE(SUM(bo.matches), 0) AS bowling_caps
        FROM players p
        LEFT JOIN batting_stats b ON p.player_id = b.player_id
        LEFT JOIN bowling_stats bo ON p.player_id = bo.player_id
        GROUP BY p.player_id
        HAVING batting_caps > 0 OR bowling_caps > 0
        ORDER BY (batting_caps + bowling_caps) DESC;
    """,
    "Question 21: Custom comprehensive rating metric formulas for formats": """
        SELECT player_name, format,
               ((runs * 0.01) + (fifties * 0.5) + (hundreds * 1.5)) AS calculated_batting_score
        FROM batting_stats
        WHERE matches > 0
        ORDER BY calculated_batting_score DESC
        LIMIT 15;
    """,
    "Question 22: Team dynamic metrics inside a common shared series": """
        SELECT m.series_id, s.series_name, COUNT(m.match_id) AS match_count
        FROM matches m
        JOIN series s ON m.series_id = s.series_id
        GROUP BY m.series_id
        ORDER BY match_count DESC;
    """,
    "Question 23: Classification metrics of top-performing historical roles": """
        SELECT p.role, AVG(b.strike_rate) AS avg_strike_rate, SUM(b.runs) AS cumulative_runs
        FROM players p
        JOIN batting_stats b ON p.player_id = b.player_id
        WHERE b.innings > 0
        GROUP BY p.role
        ORDER BY cumulative_runs DESC;
    """,
    "Question 24: Analytical overview of scoreboard matches with high wicket margins": """
        SELECT m.match_id, s.bat_team_name, s.score, s.wickets, m.status
        FROM matches m
        JOIN scorecards s ON m.match_id = s.match_id
        WHERE s.wickets >= 5
        ORDER BY s.wickets DESC;
    """,
    "Question 25: Comprehensive structural validation overview of current database records": """
        SELECT 'Players' AS table_name, COUNT(*) AS active_records FROM players
        UNION ALL
        SELECT 'Matches', COUNT(*) FROM matches
        UNION ALL
        SELECT 'Teams', COUNT(*) FROM teams
        UNION ALL
        SELECT 'Venues', COUNT(*) FROM venues;
    """
}

# 4. User Interface Selection Layout
level = st.radio("Select Difficulty Level:", ["Beginner", "Intermediate", "Advanced"], horizontal=True)

# Filter questions dynamically based on radio button selection
if level == "Beginner":
    selected_keys = [k for k in queries.keys() if "Question 1:" in k or "Question 2:" in k or "Question 3:" in k or "Question 4:" in k or "Question 5:" in k or "Question 6:" in k or "Question 7:" in k or "Question 8:" in k]
elif level == "Intermediate":
    selected_keys = [k for k in queries.keys() if any(f"Question {i}:" in k for i in range(9, 17))]
else:
    selected_keys = [k for k in queries.keys() if any(f"Question {i}:" in k for i in range(17, 26))]

chosen_question = st.selectbox("Choose a Query to Run:", selected_keys)

# 5. Execution Section
if chosen_question:
    st.subheader(f"📊 Query Analysis Result")
    sql_to_execute = queries[chosen_question]
    
    # Expandable view to double-check the behind-the-scenes SQL query execution
    with st.expander("🔍 View Raw SQL Query String"):
        st.code(sql_to_execute, language="sql")
        
    # Execute and output the dynamic table dataframe
    with st.spinner("Fetching matching database records..."):
        result_df = run_query(sql_to_execute)
        
    if result_df is not None:
        if not result_df.empty:
            st.success(f"Successfully loaded {len(result_df)} matching data rows!")
            st.dataframe(result_df, use_container_width=True)
        else:
            st.info("Query completed successfully, but returned 0 rows matching your criteria. Check if database tables have been fully populated.")
