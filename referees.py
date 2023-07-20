import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import statistics
import datetime
import time

def CreateTeamRecord(conn,startYear=None,endYear=None,gameType=None,minGames=None):
    """
    [V3] Optimized version of algorithm used to obtain per-team records for officials

    Parameters:
    conn: SQLite database connection
    startYear: Inclusive Start year for query. Date will be set to 8/1/XXXX so that the only the season beginning in the selected year will be included.
    endYear: Inclusive end year for query. Date will be set to 8/1/XXXX so that the only the season ending in the selected year will be included.
    gameType: 

    Returns:
    records: dataframe containing every recorded official's per-team record
    """
    startTime = time.time()

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
    
        print("[SETUP] Game Filters: "+str(gameType))
    
    # create timestamp for start date
    if (startYear != None):
        dateStart = datetime.datetime(startYear,8,1)
        # dateStart = int(dt.timestamp())

    # create timestamp for end date
    if (startYear != None):
        dateEnd = datetime.datetime(endYear,8,1)
        # dateEnd = int(dt.timestamp())

    # print setup notification for date range
    start = str(dateStart.year) if startYear is not None else "1946"
    end = str(dateEnd.year) if endYear is not None else "Present"
    print(f"[SETUP] Season Range: {start} - {end}\n")
    
    # simplest form of the query
    query = (
            f"SELECT officials.first_name || ' ' || officials.last_name as ref_name, "
            f"game.team_abbreviation_home as team, "
            f"COUNT(case when game.wl_home='W' then 1 else null end) as W, "
            f"COUNT(case when game.wl_home='L' then 1 else null end) as L "
            f"FROM game "
            f"INNER JOIN officials ON game.game_id = officials.game_id "
        )
    
    # append game types if passed
    if gameType is not None:
        gameType = [f"'{_}'" for _ in gameType]
        query += f" WHERE game.season_type IN ({','.join(gameType)}) " if "WHERE" not in query else f" AND game.season_type IN ({','.join(gameType)}) "

    # append starting year if specified
    if startYear is not None:
        query += f" WHERE game.game_date > '{dateStart}' " if "WHERE" not in query else f" AND game.game_date > '{dateStart}' "

    # append ending year if specified
    if endYear is not None:
        query += f" WHERE game.game_date < '{dateEnd}'" if "WHERE" not in query else f" AND game.game_date < '{dateEnd}'"

    # group results by referee name and team
    query += f" GROUP BY ref_name, team"

    # filter out results that fall short of minimum game threshold if specified
    if minGames is not None:
        query += f" HAVING (W + L) >= {minGames}"
    
    records = pd.read_sql_query(query, conn)
    records['rate'] = records['W'] / (records['W'] + records['L'])

    # write result to csv
    #records.to_csv(os.getcwd()+'\\refereeTeamRecord.csv', index = True)

    operationTime = time.time() - startTime
    print('[TIMER] Referee team records created in {:.2} seconds.\n'.format(operationTime))

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



    


