import sqlite3
import pandas as pd
import tabulate
import time
import os

def CreateRefereeTeamRecord(conn):
    # data frame will be composed of referee id/name, team, and officiating record 
    records = pd.DataFrame(columns=['ref_name','team','W','L'])
    cols = list(records.columns)
    cursor = conn.cursor()

    # query distinct officials
    cursor.execute("SELECT DISTINCT official_id FROM officials")
    result = cursor.fetchall()

    # for every official, retrieve name and game results
    for i in result:
        # retrieve official name
        cursor.execute(f"SELECT DISTINCT first_name, last_name FROM officials WHERE official_id={i[0]}")
        refName = cursor.fetchall()

        # query game ids associated with official
        cursor.execute(f"SELECT game_id FROM officials WHERE official_id={i[0]}")
        gameIDs = cursor.fetchall()

        # count game records found
        count = 0
        for j in gameIDs:
            # query game result information using game id
            cursor.execute(f"SELECT team_abbreviation_home, team_abbreviation_away, wl_home FROM game WHERE game_id='{j[0]}'")
            game_info = cursor.fetchall()

            ### TESTING
            for iter in [0,1]:
                new_rec = records.loc[(records['ref_name'] == refName[0][0] + " " + refName[0][1]) & (records['team'] == game_info[0][iter])]

                if (new_rec.empty):
                    if(game_info[0][2] == 'W'):
                        new_rec = {'ref_name': refName[0][0] + " " + refName[0][1],'team': game_info[0][iter],'W': 1,'L': 0}
                    else: 
                        new_rec = {'ref_name': refName[0][0] + " " + refName[0][1],'team': game_info[0][iter],'W': 0,'L': 1}

                    records = pd.concat([records, pd.DataFrame([new_rec])], ignore_index=True)
                else:
                    if(game_info[0][2] == 'W'):
                        #new_rec['W'] += 1
                        #new_rec.loc[0, 'W'] += 1
                        new_rec.loc[:,'W'] += 1
                    else: 
                        #new_rec['L'] += 1
                        #new_rec.loc[0, 'L'] += 1
                        new_rec.loc[:,'L'] += 1

                    records.loc[records.ref_name.isin(new_rec.ref_name) & records.team.isin(new_rec.team), cols] = new_rec[cols]

            count = count + 1

            ### TESTING
            # if(count > 1000):
            #     print(records.to_markdown())
            #     time.sleep(10)
        
        print('[INFO] Official: {}, Game Records Logged: {}.'.format(refName[0][0] + " " + refName[0][1], count))

    records.to_csv(os.getcwd()+'\\refereeTeamRecord.csv', index = True)
   
   