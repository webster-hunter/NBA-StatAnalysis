import os
import sys
import time
import pandas as pd
import sqlite3
import zipfile
import referees
from display import main_menu

if __name__ == '__main__':
    print("\033c", end='')

    startTime = time.time()

    # setup database file if non-existent
    if not os.path.isfile('nba.sqlite'):
        try:
            with zipfile.ZipFile("archive/nba_player-box_stats.zip","r") as zipObj:
                listOfFileNames = zipObj.namelist()

            for fileName in listOfFileNames:
                if fileName.endswith('.sqlite'):
                    zipObj.extract(fileName)

            #connect to SQLite server
            connection = sqlite3.connect("nba.sqlite")
        except:
            print('[ERROR] Unable to setup database.')
            sys.exit()
    else:
        connection = sqlite3.Connection('nba.sqlite')
        print('[SETUP] Database file already exists.')
    
    # print database setup time
    operationTime = time.time() - startTime
    print('[TIMER] Database setup completed in {:.2} seconds.\n'.format(operationTime))

    main_menu(conn = connection)

    # print(f"[FILTER] Game Type: {gameType}")
    # print(f"[FILTER] Min Games: {minGames}")

    # refTeamRecord = referees.CreateTeamRecord(conn=connection,startYear=startYear,endYear=endYear,minGames=minGames)

    # display histogram of team win rates per official 
    # referees.Histogram(refTeamRecord)



    

