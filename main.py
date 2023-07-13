import os
import sys
import time
import pandas as pd
import sqlite3
import dbSetup
import teams as team
import players as player

if __name__ == '__main__':
    startTime = time.time()

    # setup database file
    if not os.path.isfile('nba'):
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

    # ---------- TESTING ----------
    #teamYear = team.getTeamYear(connection,"MIA","2003")
    #os.remove("nba")
    

