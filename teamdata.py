import sqlite3
import pandas as pd

def getTeamYear(conn, team, year):
    query = "SELECT * FROM player_box_score WHERE Team=\""+team+"\" AND Season="+year
    df = pd.read_sql_query(query, conn)
    print(df.to_markdown())