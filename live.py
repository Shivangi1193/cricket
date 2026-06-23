import sqlite3
import pandas as pd
import os



match_dict={}
match_info = {
    "teams": "...",
    "venue": "...",
    "status": "...",
    "teamA": "...",
    "teamB": "...",
    "teamAScore": "...",
    "teamAOvers": "...",
    "teamBScore": "...",
    "teamBOvers": "..."
}


def series_list(selected):
    conn = sqlite3.connect("cricket.db")
    print(os.path.abspath("cricket.db"))
    series_query = "SELECT DISTINCT series_name FROM series WHERE match_type = ?"
    series_list =  pd.read_sql_query(series_query, conn, params=[selected])["series_name"].tolist()
    conn.close()
    return series_list

def match_list(series_name):
    mat=[]
    conn = sqlite3.connect("cricket.db")
    #Relational SQL Query connecting matches, series, and teams
    query = """"
        SELECT 
            (t1.team_name || ' vs ' || t2.team_name) AS match_name,
            m.match_id
            FROM matches m
            JOIN series s ON m.series_id = s.series_id
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            WHERE s.series_name = ?
        """
    #Fetch data directly into a Pandas DataFrame
    df = pd.read_sql_query(query, conn, params=[series_name])
    conn.close()
    mat = df["match_name"].tolist()
    match_dict = dict(zip(df["match_name"], df["match_id"]))                
    return mat


def match_details(match_name):
    conn = sqlite3.connect("cricket.db")
    cursor = conn.cursor()
    match_id = match_dict.get(match_name)
    query = """
        SELECT 
            t1.team_name, 
            t2.team_name,
            v.ground, 
            v.city,
            m.status,
            sc.team1_runs, 
            sc.team1_wickets, 
            sc.team1_overs,
            sc.team2_runs, 
            sc.team2_wickets, 
            sc.team2_overs
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        LEFT JOIN scorecards sc ON m.match_id = sc.match_id
        WHERE m.match_id = ?
    """

    cursor.execute(query, (int(match_id),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return f"No database records found for Match ID: {match_id}"

    # Unpack the retrieved database record
    (
        tA,
        tB,
        ground,
        city,
        status,
        tA_runs,
        tA_wkt,
        tA_ovr,
        tB_runs,
        tB_wkt,
        tB_ovr,
    ) = row

    # Format fields to match your target dictionary structure perfectly
    match_info = {
        "teams": f"{tA} vs {tB}",
        "venue": f"Venue: {ground}, {city}",
        "status": f"Current Update: {status}",
        "teamA": tA,
        "teamB": tB,
        "teamAScore": f"{tA_runs}/{tA_wkt}",
        "teamAOvers": tA_ovr,
        "teamBScore": f"{tB_runs}/{tB_wkt}",
        "teamBOvers": tB_ovr,
    }
    
    return match_info