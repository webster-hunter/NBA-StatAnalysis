import os
import sys
import time
import pandas as pd
import sqlite3
import dbSetup
import referees

if __name__ == '__main__':
    startTime = time.time()

    # setup database file if non-existent
    if not os.path.isfile('nba.sqlite'):
        try:
            connection = dbSetup.dbSetup()
        except:
            print('[ERROR] Unable to setup database.')
            sys.exit()
    else:
        connection = sqlite3.Connection('nba.sqlite')
        print('[INFO] Database file already exists.')
    
    # print setup time for user
    operationTime = time.time() - startTime
    print('[INFO] Database setup completed in {:.2} seconds.\n'.format(operationTime))

    # reset timer
    startTime = time.time()

    # create referee record csv file if non-existent or out of date 
    if not os.path.isfile('refereeTeamRecord.csv'):
        refTeamRecord = referees.CreateTeamRecord(connection)
    # retrieve referee record df if csv exists
    else: 
        refTeamRecord = pd.read_csv("RefereeTeamRecord.csv", usecols = ['ref_name', 'team', 'W', 'L', 'rate'])

    # output execution time
    setupTime = time.time() - startTime
    print('\n[INFO] Referee team records compiled in {:.2} seconds.\n'.format(operationTime))

    # filter games officiated and sort by win-rate
    refTeamRecord = referees.GetHighestRates(refTeamRecord)

    # display histogram of team win rates per official 
    # referees.Histogram(refTeamRecord)

    referees.CumSumHistogram(refTeamRecord)


    

