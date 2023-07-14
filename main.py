import os
import sys
import time
import pandas
import sqlite3
import dbSetup
import teams
import players
import referees

if __name__ == '__main__':
    startTime = time.time()

    # setup database file
    if not os.path.isfile('nba.sqlite'):
        try:
            connection = dbSetup.dbSetup()
        except:
            print('[ERROR] Unable to setup database.')
            sys.exit()
    else:
        connection = sqlite3.Connection('nba.sqlite')
        print('[INFO] Database file already exists.\n')
    
    #print setup time for user
    setupTime = time.time() - startTime
    print('[INFO] Database setup completed in {:.2} seconds.\n'.format(setupTime))

    referees.RefereeTeamRecord(connection)

    # ---------- TESTING ----------
    #teamYear = team.getTeamYear(connection,"MIA","2003")
    #os.remove("nba")
    

