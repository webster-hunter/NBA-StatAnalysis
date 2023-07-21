import os
import sys
import time
import sqlite3
import zipfile
from interface.RefPage import Ref
import tkinter as tk

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
            conn= sqlite3.connect("nba.sqlite")
        except:
            print('[ERROR] Unable to setup database.')
            sys.exit()
    else:
        conn = sqlite3.Connection('nba.sqlite')
        print('[SETUP] Database file already exists.')
    
    # print database setup time
    operationTime = time.time() - startTime
    print('[TIMER] Database setup completed in {:.2} seconds.\n'.format(operationTime))


    root = tk.Tk()
    app = Ref(rt = root, connection = conn)
    root.mainloop()




    

