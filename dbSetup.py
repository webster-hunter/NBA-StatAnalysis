import sqlite3
import os
import zipfile
import pandas as pd

def dbSetup():
    # extract sqlite file
    with zipfile.ZipFile("archive/nba_player-box_stats.zip","r") as zipObj:
        listOfFileNames = zipObj.namelist()

        for fileName in listOfFileNames:
            if fileName.endswith('.sqlite'):
                zipObj.extract(fileName)

    #connect to SQLite server
    connection = sqlite3.connect("nba.sqlite")

    #return connection object to be used later
    return connection