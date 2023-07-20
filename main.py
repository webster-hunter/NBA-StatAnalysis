import os
import sys
import time
import pandas as pd
import sqlite3
import zipfile
import referees

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
    
    # print setup time for user
    operationTime = time.time() - startTime
    print('[TIMER] Database setup completed in {:.2} seconds.\n'.format(operationTime))

    referees.CreateTeamRecord(conn=connection,minGames=20)

    #---------------------------------------
    # # create referee record csv file if non-existent or out of date 
    # if not os.path.isfile('refereeTeamRecord.csv'):
    #     refTeamRecord = referees.CreateTeamRecord(connection,gameType=['reg'])
    # # retrieve referee record df if csv exists
    # else: 
    #     refTeamRecord = pd.read_csv("RefereeTeamRecord.csv", usecols = ['ref_name', 'team', 'W', 'L', 'rate'])

    # # output execution time
    # setupTime = time.time() - operationTime
    # print('\n[INFO] Referee team records compiled in {:.2} seconds.\n'.format(operationTime))

    # # filter games officiated and sort by win-rate
    # # params: dataframe, min games, ascending/descending
    # refTeamRecord = referees.GetHighestRates(refTeamRecord,20,False)

    # # display histogram of team win rates per official 
    # referees.Histogram(refTeamRecord)

    # # display cumulative sum histogram
    # #referees.CumSumHistogram(refTeamRecord)


    

