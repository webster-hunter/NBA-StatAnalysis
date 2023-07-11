import sqlite3
import zipfile
import pandas as pd

def dbSetup():
    # extract stats dataset on setup
    with zipfile.ZipFile("archive/nba_player-box_stats.zip","r") as zip_ref:
        zip_ref.extractall("archive")

    # read csv into dataframe
    df = pd.read_csv("archive/nba_player-box_stats.csv")

    # clean column names
    df.columns = df.columns.str.strip()

    #connect to SQLite server
    connection = sqlite3.connect("nba")

    #load df to SQLite
    df.to_sql("player_box_score", connection, if_exists='replace')

    #return connection object to be used later
    return connection