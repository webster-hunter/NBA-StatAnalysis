import sqlite3
import pandas as pd
#import tabulate
import os

def RefereeTeamRecord(conn):
    
    records = pd.DataFrame(columns=['ref_id','ref_name','team','W','L'])
    officials = []

    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT official_id FROM officials")
    result = cursor.fetchall()

    #officials = [i[0] for i in result]
    for i in result:
        cursor.execute(f"SELECT DISTINCT first_name, last_name FROM officials WHERE official_id={i[0]}")
        refName = cursor.fetchall()

        # query game ids associated with official
        cursor.execute(f"SELECT game_id FROM officials WHERE official_id={i[0]}")
        gameIDs = cursor.fetchall()

        for j in gameIDs:
            # query game result information using game id
            cursor.execute(f"SELECT team_abbreviation_home, team_abbreviation_away, wl_home FROM game WHERE game_id='{j[0]}'")
            game_info = cursor.fetchall()

            # HOME TEAM
            try:
                # find row corresponding to ref id and home team, excepts if not found
                row = records.loc[records['ref_id'] == j[0][2:] & records['team'] == game_info[0][0]]
                
                # increment W or L column
                if(game_info[0][2] == 'W'):
                    records.at[row,'W'] += 1
                else:
                    records.at[row,'L'] += 1
            except: # team and ref combo not already recorded
                if(game_info[0][2] == 'W'):
                    new_rec = {'ref_id': j[0][2:],'ref_name': refName[0][0] + " " + refName[0][1],'team': game_info[0][0],'W': 1,'L': 0}
                else:
                    new_rec = {'ref_id': j[0][2:],'ref_name': refName[0][0] + " " + refName[0][1],'team': game_info[0][0],'W': 0,'L': 1}

                # add to dataframe    
                records = pd.concat([records, pd.DataFrame([new_rec])], ignore_index=True)
            
            # AWAY TEAM
            try:
                # find row corresponding to ref id and home team, excepts if not found
                row = records.loc[records['ref_id'] == j[0][2:] & records['team'] == game_info[0][1]]
                
                # increment W or L column
                if(game_info[0][2] == 'L'):
                    records.at[row,'W'] += 1
                else:
                    records.at[row,'L'] += 1
            except: # team and ref combo not already recorded
                if(game_info[0][2] == 'L'):
                    new_rec = {'ref_id': j[0][2:],'ref_name': refName[0][0] + " " + refName[0][1],'team': game_info[0][1],'W': 1,'L': 0}
                else:
                    new_rec = {'ref_id': j[0][2:],'ref_name': refName[0][0] + " " + refName[0][1],'team': game_info[0][1],'W': 0,'L': 1}

                # add to dataframe    
                records = pd.concat([records, pd.DataFrame([new_rec])], ignore_index=True)

    records.to_csv(os.getcwd()+'\\refereeTeamRecord.csv', index = True)
   
   