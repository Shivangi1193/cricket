import json
import sqlite3
from pathlib import Path

DB_NAME = "cricket.db"
# Use a raw string (r"") or forward slashes for Windows paths
JSON_FOLDER = Path("./data")

def create_schema(cursor):
    """Defines the relational architecture of the database."""
    print("Creating table schemas...")

    # 1. Independent Tables (No Foreign Keys)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT,
            short_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venues (
            venue_id INTEGER PRIMARY KEY,
            ground TEXT,
            city TEXT,
            timezone TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS series (
            series_id INTEGER PRIMARY KEY,
            series_name TEXT,
            match_type TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            player_name TEXT,
            is_captain BOOLEAN,
            is_keeper BOOLEAN,
            role TEXT,
            batting_style TEXT,
            bowling_style TEXT,
            birth_place TEXT,
            country TEXT
        )
    ''')

    # 2. Dependent Tables (Contains Foreign Keys)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY,
            series_id INTEGER,
            team1_id INTEGER,
            team2_id INTEGER,
            venue_id INTEGER,
            status TEXT,
            FOREIGN KEY (series_id) REFERENCES series (series_id),
            FOREIGN KEY (team1_id) REFERENCES teams (team_id),
            FOREIGN KEY (team2_id) REFERENCES teams (team_id),
            FOREIGN KEY (venue_id) REFERENCES venues (venue_id)
        )
    ''')

    # Note: Using composite primary keys for stats since a player has stats per 'format'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batting_stats (
            player_id INTEGER,
            player_name TEXT,
            format TEXT,
            matches INTEGER,
            innings INTEGER,
            runs INTEGER,
            balls INTEGER,
            strike_rate REAL,
            ducks INTEGER,
            fifties INTEGER,
            hundreds INTEGER,
            PRIMARY KEY (player_id, format),
            FOREIGN KEY (player_id) REFERENCES players (player_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bowling_stats (
            player_id INTEGER,
            player_name TEXT,
            format TEXT,
            matches INTEGER,
            innings INTEGER,
            balls INTEGER,
            runs INTEGER,
            maidens INTEGER,
            wickets INTEGER,
            average REAL,
            economy REAL,
            strike_rate REAL,
            best_bowling_innings TEXT,
            best_bowling_match TEXT,
            four_wickets INTEGER,
            five_wickets INTEGER,
            ten_wickets INTEGER,
            PRIMARY KEY (player_id, format),
            FOREIGN KEY (player_id) REFERENCES players (player_id)
        )
    ''')

    # User image had scorecards.json, text had scoreboards.json. Adjust name if needed.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scorecards (
            match_id INTEGER,
            innings_id INTEGER,
            bat_team_name TEXT,
            score INTEGER,
            wickets INTEGER,
            overs REAL,
            PRIMARY KEY (match_id, innings_id),
            FOREIGN KEY (match_id) REFERENCES matches (match_id)
        )
    ''')

def insert_data(conn, cursor):
    """Reads JSON files and inserts them into the respective tables."""
    
    # Mapping JSON filenames to their table names and exact column lists
    # Order matters: populate independent tables first so Foreign Keys don't fail
    file_configs = {
        "teams.json": {"table": "teams", "cols": ["team_id", "team_name", "short_name"]},
        "venues.json": {"table": "venues", "cols": ["venue_id", "ground", "city", "timezone"]},
        "series.json": {"table": "series", "cols": ["series_id", "series_name", "match_type"]},
        "players.json": {"table": "players", "cols": ["player_id", "player_name", "is_captain", "is_keeper", "role", "batting_style", "bowling_style", "birth_place", "country"]},
        "matches.json": {"table": "matches", "cols": ["match_id", "series_id", "team1_id", "team2_id", "venue_id", "status"]},
        "scorecards.json": {"table": "scorecards", "cols": ["match_id", "innings_id", "bat_team_name", "score", "wickets", "overs"]}, # OR scoreboards.json depending on actual filename
        "batting_stats.json": {"table": "batting_stats", "cols": ["player_id", "player_name", "format", "matches", "innings", "runs", "balls", "strike_rate", "ducks", "fifties", "hundreds"]},
        "bowling_stats.json": {"table": "bowling_stats", "cols": ["player_id", "player_name", "format", "matches", "innings", "balls", "runs", "maidens", "wickets", "average", "economy", "strike_rate", "best_bowling_innings", "best_bowling_match", "four_wickets", "five_wickets", "ten_wickets"]}
    }

    for filename, config in file_configs.items():
        file_path = JSON_FOLDER / filename
        
        if not file_path.exists():
            print(f"Warning: {filename} not found in directory. Skipping.")
            continue
            
        print(f"Reading and loading {filename} into {config['table']}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if not data:
                continue

            table = config["table"]
            cols = config["cols"]
            
            # Create placeholders like (?, ?, ?)
            placeholders = ", ".join(["?"] * len(cols))
            col_names = ", ".join(cols)
            
            # OR IGNORE prevents crashing if you run the script twice and duplicate IDs exist
            query = f"INSERT OR IGNORE INTO {table} ({col_names}) VALUES ({placeholders})"
            
            # Extract tuples of values matching the column order
            values_list = []
            for item in data:
                row = tuple(item.get(col, None) for col in cols)
                values_list.append(row)
                
            cursor.executemany(query, values_list)
            conn.commit()

def main():
    # Connect to the DB (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Enable foreign key enforcement in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    create_schema(cursor)
    insert_data(conn, cursor)
    
    conn.close()
    print("Database creation complete!")

if __name__ == "__main__":
    main()
