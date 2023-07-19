import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import statistics
import datetime

def TeamRecordOPT(conn,startYear=None,endYear=None,gameType=None):
    """
    [V2] Optimized version of algorithm used to obtain per-team records for officials

    Parameters:
    conn: SQLite database connection
    startYear: Inclusive Start year for query. Date will be set to 8/1/XXXX so that the only the season beginning in the selected year will be included.
    endYear: Inclusive end year for query. Date will be set to 8/1/XXXX so that the only the season ending in the selected year will be included.
    gameType: 

    Returns:
    records: dataframe containing every recorded official's per-team record
    """

    # translate gameType params to game type filters
    if (gameType != None):
        for i, type in enumerate(gameType):
            if(type == "pre") :
                gameType[i] = 'Pre Season'
            elif(type == "reg"):
                gameType[i] = 'Regular Season'
            elif(type == "post"):
                gameType[i] = 'Playoffs'
            elif(type == "asg"):
                gameType[i] = 'All Star'
            else:
                print('[ERROR] Invalid Game Type Filter')
                del gameType[i]
    
        print("[SETUP] Game Filters: "+str(gameType)+"\n")
    
    # create timestamp for start date
    if (startYear != None):
        dt = datetime.datetime(
            year = startYear,
            month = 8,
            day = 1
        )
        dateStart = int(dt.timestamp())

    # create timestamp for end date
    if (startYear != None):
        dt = datetime(
            year = endYear,
            month = 8,
            day = 1
        )
        dateEnd = int(dt.timestamp())

    cursor = conn.cursor()

    result = []
    if gameType is not None:
        for t in gameType:
            query = (
                f"SELECT officials.first_name, officials.last_name, "
                f"game.team_abbreviation_home, game.team_abbreviation_away, "
                f"game.wl_home, game.season_type "
                f"FROM game "
                f"INNER JOIN officials ON game.game_id = officials.game_id "
                f"WHERE game.season_type='{t}' "
            )

            cursor.execute(query)
            temp = cursor.fetchall()
            result = result + temp
    else:
        query = (
            f"SELECT officials.first_name, officials.last_name, "
            f"game.team_abbreviation_home, game.team_abbreviation_away, "
            f"game.wl_home, game.season_type "
            f"FROM game "
            f"INNER JOIN officials ON game.game_id = officials.game_id "
        )
        
        cursor.execute(query)
        result = cursor.fetchall()

    count = len(result)

    records = pd.DataFrame(columns=['ref_name','team','W','L','rate'])
    cols = list(records.columns)

    for i, row in enumerate(result):
        # Calculate progress and update progress bar every 1000 iterations
        if i % 50 == 0 or i == count-1:  # also update for the last element
            progress = (i+1) / count

            # Create progress bar
            bar_length = 50  # Length of the progress bar
            filled_length = int(progress * bar_length)
            if filled_length > 0:
                moving_part = i % filled_length
                bar = "#" * moving_part + " " + "#" * (filled_length - moving_part - 1) + " " * (bar_length - filled_length)
            else:
                bar = " " * bar_length

            # Print progress bar
            print("\rProgress: [{0}] {1:.1f}%".format(bar, progress * 100), end='', flush=True)


        # for each row, add the result for the home team (index 2) and the away team (index 3)
        for index in [2,3]:
            refName =  row[0] + " " + row[1]
            new_rec = records.loc[(records['ref_name'] == refName) & (records['team'] == row[index])]

            # if empty, create new row
            # since the 4th entry is home team win/loss, we can narrow down our conditional
            if (new_rec.empty):
                if((row[4] == 'W' and index == 2) or (row[4] == 'L' and index == 3)):
                    new_rec = {'ref_name': refName,'team': row[index],'W': 1,'L': 0, 'rate': 1.000}
                else: 
                    new_rec = {'ref_name': refName,'team': row[index],'W': 0,'L': 1, 'rate': 0.000}

                # add new row to records
                records = pd.concat([records, pd.DataFrame([new_rec])], ignore_index=True)
            else:
                if((row[4] == 'W' and index == 2) or (row[4] == 'L' and index == 3)):
                    new_rec.loc[:,'W'] += 1
                else: 
                    new_rec.loc[:,'L'] += 1

                new_rec.loc[:,'rate'] = new_rec.loc[:,'W'] / (new_rec.loc[:,'W'] + new_rec.loc[:,'L'])

                records.loc[records.ref_name.isin(new_rec.ref_name) & records.team.isin(new_rec.team), cols] = new_rec[cols]

    # write result to csv
    records.to_csv(os.getcwd()+'\\refereeTeamRecord.csv', index = True)

    # return dataframe
    return records




#-------------------------------------------------------------------------

def CreateTeamRecord(conn,startYear=None,endYear=None,gameType=None):
    # translate gameType params to game type filters
    for i, type in enumerate(gameType):
        if(type == "pre") :
            gameType[i] = 'Pre Season'
        elif(type == "reg"):
            gameType[i] = 'Regular Season'
        elif(type == "post"):
            gameType[i] = 'Playoffs'
        elif(type == "asg"):
            gameType[i] = 'All Star'
        else:
            print('[ERROR] Invalid Game Type Filter')
            del gameType[i]

    if (gameType != None):
        print("[SETUP] Game Filters: "+str(gameType)+"\n")
    
    # create timestamp for start date
    if (startYear != None):
        dt = datetime.datetime(
            year = startYear,
            month = 8,
            day = 1
        )
        dateStart = int(dt.timestamp())

    # create timestamp for end date
    if (startYear != None):
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
            cursor.execute(f"SELECT team_abbreviation_home, team_abbreviation_away, wl_home, season_type FROM game WHERE game_id='{j[0]}'")
            game_info = cursor.fetchall()

            if (game_info[0][3] not in gameType):
                continue

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
        if (count > 0):
            print('[INFO] Official: {}, Game Records Logged: {}.'.format(refName[0][0] + " " + refName[0][1], count))

    # write result to csv
    records.to_csv(os.getcwd()+'\\refereeTeamRecord.csv', index = True)

    # return dataframe
    return records

def SortHighestRates(df,minGames,asc):
    filtered = df.query('(W + L) > '+ str(minGames))
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



    


