import tkinter as tk
from tkinter import simpledialog, Label, Entry, IntVar, Checkbutton, W, Scale, ttk, Menu, Button
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import referees

class Ref:
    def __init__(self,rt,connection):
        root = rt
        root.title("Referees")

        # Calculate the desired window size based on screen resolution
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        default_width = int(screen_width * 0.3)
        default_height = int(screen_height * 0.4)

        # Set the default window size
        root.geometry(f"{default_width}x{default_height}")

        # define attributes
        self.root = root
        self.df = None
        self.tree = None
        self.conn = connection
        self.table_shown = False
        self.histo_shown = False

        # Create a top-level menu
        menubar = Menu(root)
        root.config(menu=menubar)
        
        # Create buttons
        # Create empty labels to take up extra space on either side of the buttons
        left_spacer = tk.Label(self.root)
        right_spacer = tk.Label(self.root)

        # Configure the grid to allow the spacers to expand and take up extra space
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(4, weight=1)

        # Add the spacers to the grid
        left_spacer.grid(row=0, column=0, sticky='ew')
        right_spacer.grid(row=0, column=4, sticky='ew')

        # search/filter button
        self.filter_button = Button(root, text="Search Filters", command=self.teamRecord) 
        self.filter_button.grid(row=0, column=1, padx=10, pady=10)

        # table display button
        self.table_button = tk.Button(root, text="Show Table", command=self.showTable, state="disabled")
        self.table_button.grid(row=0, column=2, padx=10, pady=10)

        # histogram button
        self.histo_button = tk.Button(root, text="Show Plot", command=self.showPlot, state="disabled")
        self.histo_button.grid(row=0, column=3, padx=10, pady=10)

        # Frame for the plot
        self.plot_frame = tk.Frame(root)
        self.plot_frame.grid(row=0, column=1, rowspan=3)

        self.tree_frame = None


    def teamRecord(self):
        startYear, endYear, gameType, minGames = TeamRecordDialog(self.root).result
        print(f"[FILTER] Game Type: {gameType}")
        print(f"[FILTER] Min Games: {minGames}")

        self.df = referees.CreateTeamRecord(conn=self.conn, startYear=startYear, endYear=endYear, minGames=minGames)

        if self.df is not None:
            self.table_button.config(state="normal")
            self.histo_button.config(state="normal")
    

    def showTable(self):
        self.df = self.df.sort_values(by='rate', ascending=False)

        if self.table_shown:
            # If table is already shown, destroy it and change the button text to "Show Table"
            self.tree_frame.destroy()
            self.tree_frame = None
            self.table_shown = False
            self.table_button.config(text="Show Table")

        else:
            # If table is not shown, create it and change the button text to "Hide Table"
            self.tree_frame = tk.Frame(self.root)
            self.tree_frame.grid(row=0, column=0, sticky="nsew")

            self.tree = ttk.Treeview(self.tree_frame, show="headings")
            self.tree["columns"]=tuple(self.df.columns)

            # Create columns
            for i in self.df.columns:
                self.tree.column(i, width=100)
                self.tree.heading(i, text=i)

            # Add data
            for index, row in self.df.iterrows():
                self.tree.insert("", "end", values=tuple(row))

            self.tree.grid()
            self.table_shown = True
            self.table_button.config(text="Hide Table")

        self.manage_layout()


    def showPlot(self):
        if self.histo_shown:
            # If plot is already shown, hide it and change the button text to "Show Plot"
            self.plot_frame.grid_remove()
            self.histo_shown = False
            self.histo_button.config(text="Show Plot")
        else:
            # If plot is not shown, create it and change the button text to "Hide Plot"
            fig = Figure(figsize=(10, 5), dpi=100)
            ax = fig.add_subplot(111)
            ax.hist(self.df['rate'], bins=25)
            ax.set_title("Histogram of Rate")
            ax.set_xlabel("Rate")
            ax.set_ylabel("Frequency")

            # Clear frame
            for widget in self.plot_frame.winfo_children():
                widget.destroy()

            # Add plot to frame
            self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)  
            self.canvas.draw()
            self.canvas.get_tk_widget().pack()

            # Create a new frame for the toolbar
            toolbar_frame = tk.Frame(self.plot_frame)
            toolbar_frame.pack()

            self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
            self.toolbar.update()

            self.plot_frame.grid(row=3, column=0, columnspan=4)

            self.histo_shown = True
            self.histo_button.config(text="Hide Plot")

        self.manage_layout()

    
    def manage_layout(self):
        # Hide all widgets
        self.tree_frame.grid_remove()
        self.plot_frame.grid_remove()

        # Now show the widgets in the desired order
        row = 3
        if self.table_shown:
            self.tree_frame.grid(row=row, column=0, columnspan=4)
            row += 1
        if self.histo_shown:
            self.plot_frame.grid(row=row, column=0, columnspan=4)

        self.root.update_idletasks()  # Update "idle" tasks in the application
        width = self.root.winfo_reqwidth()  # Get the width required by the window
        height = self.root.winfo_reqheight()  # Get the height required by the window
        self.root.geometry(f'{width}x{height}')  # Set the new size of the window


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