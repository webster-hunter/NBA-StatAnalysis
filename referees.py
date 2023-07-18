import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import statistics
import datetime

def CreateTeamRecord(conn,startYear=None,endYear=None,gameType=None):
    # translate gameType params to game type filters
    for type in gameType:
        match gameType:
            case 'pre':
                gameType[type] = 'Pre Seson'
            case 'reg':
                gameType[type] = 'Regular Season'
            case 'post':
                gameType[type] = 'Playoffs'
            case 'asg':
                gameType[type] = 'All Star'
            case _:
                print('[ERROR] Invalid Game Type Filter')
    
    # create timestamp for start date
    dt = datetime(
        year = startYear,
        month = 8,
        day = 1
    )
    dateStart = int(dt.timestamp())

    # create timestamp for end date
    dt = datetime(
        year = endYear,
        month = 8,
        day = 1
    )
    dateEnd = int(dt.timestamp())

    # data frame will be composed of referee id/name, team, and officiating record 
    records = pd.DataFrame(columns=['ref_name','team','W','L','rate'])
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
        game_info = []
        for j in gameIDs:
            # query game result information using game id
            if (gameType == None):
                cursor.execute(f"SELECT team_abbreviation_home, team_abbreviation_away, wl_home FROM game WHERE game_id='{j[0]}'")
                game_info = cursor.fetchall()
            else:
                for x in gameType:
                    cursor.execute(f"SELECT team_abbreviation_home, team_abbreviation_away, wl_home FROM game " + 
                                    "WHERE game_id='{j[0]}' "
                                    "AND gameType = {x}")
                    temp = cursor.fetchall()
                    game_info = game_info + temp
            

            # iterate thru game info to tally win-loss record per team
            # note for iter: 0 = home team, 1 = away team
            for iter in [0,1]:
                # search for existing record, empty if not found
                new_rec = records.loc[(records['ref_name'] == refName[0][0] + " " + refName[0][1]) & (records['team'] == game_info[0][iter])]

                # if empty, create new row
                if (new_rec.empty):
                    if(game_info[0][2] == 'W'):
                        new_rec = {'ref_name': refName[0][0] + " " + refName[0][1],'team': game_info[0][iter],'W': 1,'L': 0, 'rate': 1.000}
                    else: 
                        new_rec = {'ref_name': refName[0][0] + " " + refName[0][1],'team': game_info[0][iter],'W': 0,'L': 1, 'rate': 0.000}
                    
                    # add new row to records
                    records = pd.concat([records, pd.DataFrame([new_rec])], ignore_index=True)
                else:
                    if(game_info[0][2] == 'W'):
                        new_rec.loc[:,'W'] += 1
                    else: 
                        new_rec.loc[:,'L'] += 1

                    new_rec.loc[:,'rate'] = new_rec.loc[:,'W'] / (new_rec.loc[:,'W'] + new_rec.loc[:,'L'])

                    records.loc[records.ref_name.isin(new_rec.ref_name) & records.team.isin(new_rec.team), cols] = new_rec[cols]

            count = count + 1
        
        print('[INFO] Official: {}, Game Records Logged: {}.'.format(refName[0][0] + " " + refName[0][1], count))

    # write result to csv
    records.to_csv(os.getcwd()+'\\refereeTeamRecord.csv', index = True)

    # return dataframe
    return records

def GetHighestRates(df,minGames,asc):
    filtered = df.query('(W + L) > '+ minGames)
    df = filtered.sort_values(by=['rate'], ascending = asc)

    return df

def Histogram(df):
    rates = df['rate'].to_list()

    plt.hist(rates, bins=20)

    plt.xlabel('Win Rate')
    plt.ylabel('Occurrence')
    plt.title('Team Win Rate Per Official Histogram')
    plt.grid(True)

    plt.show()

def CumSumHistogram(df):
    rates = df['rate'].to_list()

    fig, ax = plt.subplots(figsize=(8, 4))

    sigma = statistics.stdev(rates)
    mu = 0.5
    n_bins = 100

    # plot the cumulative histogram
    n, bins, patches = ax.hist(rates, n_bins, density=True, histtype='step',
                            cumulative=True, label='Empirical')

    # Add a line showing the expected distribution.
    y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
        np.exp(-0.5 * (1 / sigma * (bins - mu))**2))
    y = y.cumsum()
    y /= y[-1]

    ax.plot(bins, y, 'k--', linewidth=1.5, label='Theoretical')

    # tidy up the figure
    ax.grid(True)
    ax.legend(loc='right')
    ax.set_title('Cumulative Step Histogram')
    ax.set_xlabel('Team Win Rate Per Official')
    ax.set_ylabel('Likelihood of Occurrence')

    plt.show()



    


