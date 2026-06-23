import streamlit as st
import sqlite3
import pandas as pd
from navbar import show_navbar

# 1. Page Configuration
st.set_page_config(
    page_title="Data Control",
    page_icon="🛠️",
    layout="wide"
)

show_navbar()

st.title("🛠️ Data Control & CRUD Dashboard")
st.write("Manage your relational database operations. Select a table below to Create, Read, Update, or Delete entries.")

DB_NAME = "cricket.db"

# 2. Database Helper Operations
def run_query(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

def fetch_dataframe(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(query, conn, params=params)

# 3. Dynamic Configuration Schema
# Defines UI forms and column parameters mapping exactly to cricket.db
TABLE_CONFIGS = {
    "teams": {
        "pk": "team_id",
        "columns": ["team_id", "team_name", "short_name"],
        "types": {"team_id": "int", "team_name": "text", "short_name": "text"}
    },
    "venues": {
        "pk": "venue_id",
        "columns": ["venue_id", "ground", "city", "timezone"],
        "types": {"venue_id": "int", "ground": "text", "city": "text", "timezone": "text"}
    },
    "series": {
        "pk": "series_id",
        "columns": ["series_id", "series_name", "match_type"],
        "types": {"series_id": "int", "series_name": "text", "match_type": "text"}
    },
    "players": {
        "pk": "player_id",
        "columns": ["player_id", "player_name", "is_captain", "is_keeper", "role", "batting_style", "bowling_style", "birth_place", "country"],
        "types": {"player_id": "int", "player_name": "text", "is_captain": "bool", "is_keeper": "bool", "role": "text", "batting_style": "text", "bowling_style": "text", "birth_place": "text", "country": "text"}
    },
    "matches": {
        "pk": "match_id",
        "columns": ["match_id", "series_id", "team1_id", "team2_id", "venue_id", "status"],
        "types": {"match_id": "int", "series_id": "int", "team1_id": "int", "team2_id": "int", "venue_id": "int", "status": "text"}
    }
}

# 4. Table Selector View
selected_table = st.selectbox("🗂️ Select Database Table to Manage:", list(TABLE_CONFIGS.keys()))
config = TABLE_CONFIGS[selected_table]
pk_col = config["pk"]

# --- READ OPERATION ---
st.subheader(f"📋 Current Records in `{selected_table}`")
df = fetch_dataframe(f"SELECT * FROM {selected_table}")
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info(f"The table `{selected_table}` is currently empty.")

# Create isolated tabs for writing operations (Create, Update, Delete)
tab_create, tab_update, tab_delete = st.tabs(["➕ Insert Record", "✏️ Update Record", "🗑️ Delete Record"])

# --- CREATE OPERATION ---
with tab_create:
    st.write(f"Add a new row entry into `{selected_table}`")
    with st.form(key=f"form_create_{selected_table}", clear_on_submit=True):
        new_data = {}
        for col in config["columns"]:
            col_type = config["types"][col]
            if col_type == "int":
                new_data[col] = st.number_input(f"Enter {col}", step=1, value=0)
            elif col_type == "bool":
                new_data[col] = st.checkbox(f"{col}")
            else:
                new_data[col] = st.text_input(f"Enter {col}", value="")
        
        submit_create = st.form_submit_button(label="Save New Record")
        
        if submit_create:
            try:
                cols_str = ", ".join(config["columns"])
                placeholders = ", ".join(["?"] * len(config["columns"]))
                vals = tuple(new_data[c] for c in config["columns"])
                
                run_query(f"INSERT INTO {selected_table} ({cols_str}) VALUES ({placeholders})", vals)
                st.success(f"🎉 New record successfully inserted into `{selected_table}`!")
                st.rerun()
            except sqlite3.Error as e:
                st.error(f"Failed to insert record: {e}")

# --- UPDATE OPERATION ---
with tab_update:
    if not df.empty:
        st.write(f"Modify an existing record's details based on its Primary Key identifier")
        selected_pk_val = st.selectbox(f"Select `{pk_col}` to modify:", df[pk_col].tolist(), key="update_pk_select")
        
        # Pre-fill inputs with existing values from dataframe match
        existing_row = df[df[pk_col] == selected_pk_val].iloc[0]
        
        with st.form(key=f"form_update_{selected_table}"):
            updated_data = {}
            for col in config["columns"]:
                if col == pk_col:
                    st.write(f"**Modifying Primary Key `{pk_col}`:** {selected_pk_val}")
                    updated_data[col] = selected_pk_val
                    continue
                
                col_type = config["types"][col]
                current_val = existing_row[col]
                
                if col_type == "int":
                    updated_data[col] = st.number_input(f"Update {col}", step=1, value=int(current_val) if pd.notna(current_val) else 0)
                elif col_type == "bool":
                    updated_data[col] = st.checkbox(f"Update {col}", value=bool(current_val) if pd.notna(current_val) else False)
                else:
                    updated_data[col] = st.text_input(f"Update {col}", value=str(current_val) if pd.notna(current_val) else "")
            
            submit_update = st.form_submit_button(label="Save Updated Changes")
            
            if submit_update:
                try:
                    # Set up structural update assignments (excluding PK)
                    update_cols = [c for c in config["columns"] if c != pk_col]
                    set_clause = ", ".join([f"{c} = ?" for c in update_cols])
                    vals = tuple(updated_data[c] for c in update_cols) + (selected_pk_val,)
                    
                    run_query(f"UPDATE {selected_table} SET {set_clause} WHERE {pk_col} = ?", vals)
                    st.success(f"✏️ Record `{selected_pk_val}` modified successfully!")
                    st.rerun()
                except sqlite3.Error as e:
                    st.error(f"Failed to update record: {e}")
    else:
        st.info("No rows available to update.")

# --- DELETE OPERATION ---
with tab_delete:
    if not df.empty:
        st.write(f"Permanently remove a record row entry")
        delete_pk_val = st.selectbox(f"Select `{pk_col}` to target for deletion:", df[pk_col].tolist(), key="delete_pk_select")
        
        confirm_checkbox = st.checkbox("⚠️ I confirm that I want to permanently delete this row entry and understand it cannot be undone.")
        submit_delete = st.button(label="Execute Permanent Deletion", type="primary")
        
        if submit_delete:
            if confirm_checkbox:
                try:
                    run_query(f"DELETE FROM {selected_table} WHERE {pk_col} = ?", (delete_pk_val,))
                    st.success(f"🗑️ Record entry `{delete_pk_val}` safely removed from `{selected_table}`.")
                    st.rerun()
                except sqlite3.Error as e:
                    st.error(f"Foreign Key Constraint or DB Error preventing execution: {e}")
            else:
                st.warning("Please check the confirmation box first before executing data deletions.")
    else:
        st.info("No rows available to delete.")
