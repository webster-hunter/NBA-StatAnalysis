import tkinter as tk
from tkinter import simpledialog,Label,Entry,IntVar,Checkbutton,W,Scale,Tk,Menu,Button
import referees

def main_menu(conn):
    root = Tk()
    root.title("NBA Stat Analysis")

    # Calculate the desired window size based on screen resolution
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    default_width = int(screen_width * 0.2)
    default_height = int(screen_height * 0.4)

    # Set the default window size
    root.geometry(f"{default_width}x{default_height}")

    def teamRecord():
        startYear, endYear, gameType, minGames = TeamRecordDialog(root).result
        print(f"[FILTER] Game Type: {gameType}")
        print(f"[FILTER] Min Games: {minGames}")

        refTeamRecord = referees.CreateTeamRecord(conn=conn,startYear=startYear,endYear=endYear,minGames=minGames)
        referees.Histogram(refTeamRecord)
        print(startYear, endYear, gameType, minGames)

    # Create a top-level menu
    menubar = Menu(root)
    root.config(menu=menubar)
    
    button_width = int(root.winfo_width() * 0.8)
    button_height = int(root.winfo_height() * 0.4)

    # Create a button
    button1 = Button(root, text="Team Record", command=teamRecord, width=button_width, height=button_height) 
    button1.pack()  # This button will call the show_dialog function when clicked

    # Add more buttons as needed, for example:
    # button2 = Button(root, text="Another function", command=another_function)
    # button2.pack()

    root.mainloop()

class TeamRecordDialog(simpledialog.Dialog):
    def __init__(self, parent):
        # Set default result
        self.result = (None, None, None, 10)
        super().__init__(parent)

    def body(self, master):
        Label(master, text="Start Year:").grid(row=0)
        Label(master, text="End Year:").grid(row=1)

        self.e1 = Entry(master)
        self.e2 = Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)

        Label(master, text="Min Games:").grid(row=2)

        # Slider for min games
        self.minGamesSlider = Scale(master, from_=0, to=100, orient="horizontal")
        self.minGamesSlider.set(10)  # Setting the default value
        self.minGamesSlider.grid(row=2, column=1)

        # Checkbox for game types
        self.gameTypeVars = {"Regular Season": IntVar(), "Postseason": IntVar()}
        for i, (text, var) in enumerate(self.gameTypeVars.items()):
            Checkbutton(master, text=text, variable=var).grid(row=3, column=i, sticky=W)

        return self.e1  # initial focus
    
    def apply(self):
        startYear = int(self.e1.get()) if self.e1.get() else None
        endYear = int(self.e2.get()) if self.e2.get() else None

        gameTypes = [key for key, var in self.gameTypeVars.items() if var.get()]
        gameType = gameTypes if gameTypes else None

        minGames = self.minGamesSlider.get()

        self.result = (startYear, endYear, gameType, minGames)

# def get_user_inputs():
#     root = tk.Tk()
#     root.withdraw()
#     dialog = TeamRecordDialog(root)
#     return dialog.result

    