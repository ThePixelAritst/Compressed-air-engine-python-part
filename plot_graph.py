import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import ast
import os
from handle_file import file
import numpy as np

# Purely technical
MAX_WATCHDOG = 5 # maximum number of attempts for file input

# Crucial setup
SAVE_FIG = False # EXPERIMENTAL, DOES NOT WORK PROPERLY
SIZE_X = 22 # canvas size, width
SIZE_Y = 10 # canvas size, height

#Derivation function controls
MAX_ACCELERATION = 3500 #maximum acceleration that will still be displayed, no data lost
LIMIT_ACCELERATION = False # turns on MAX_ACCELERATION limit, if False will display all calculated values
ACCELERATION_LOG10 = True # displays acceleration in symlog scale

# Graphical settings
TITLE_SIZE = 28
LABEL_SIZE = 12 # basically everything not a title uses this
STAT_TEXT = True # info board with some useful and cool stats

AX1_COLOR = "black" # color of main (rpm) line
AX2_COLOR = "#ff970e" # color of secondary line
AX1_LINE = 2.5 # linewidth of the main (rpm) line

class Graphing():
    def __init__(self):
        self.fig = plt.figure(num="Main Figure",figsize=[SIZE_X,SIZE_Y])
        self.ax1 = self.fig.add_subplot()
        self.ax2 = self.ax1.twinx()
        self.x_ax1=[]
        self.y_ax1=[]
        self.y_ax2 = []
        self.run_name = None
        self.secondary_label = ""
        self.main_label = "Rotational speed [RPM]"
        self.ax2_stat = ""

    def set_from_file(self):
        file_path, returned_data = file.open_and_separate()
        self.x_ax1 = ast.literal_eval(returned_data[1])
        self.y_ax1 = ast.literal_eval(returned_data[2])
        self.run_name = os.path.basename(file_path).split(".")[0] #converts the filepath to only show the name of the file to be displayed

    def set_from_data(self,set_x,set_y,name="Not Set"):
        self.x_ax1 = set_x
        self.y_ax1 = set_y
        self.run_name = name

    def calculate_derivation(self):
        pointer = 0
        real_derivation=0
        self.y_ax2=[]
        while pointer < len(self.y_ax1):
            raw_derivation = self.y_ax1[pointer]-self.y_ax1[pointer-1]
            if self.x_ax1[pointer]-self.x_ax1[pointer-1] != 0:
                interval_coeficient = 1/(self.x_ax1[pointer]-self.x_ax1[pointer-1])
            else:
                interval_coeficient = 1

            real_derivation = raw_derivation * interval_coeficient
            pointer += 1

            if real_derivation > MAX_ACCELERATION and LIMIT_ACCELERATION:
                real_derivation = MAX_ACCELERATION
            elif real_derivation < -MAX_ACCELERATION and LIMIT_ACCELERATION:
                real_derivation = -MAX_ACCELERATION

            real_derivation = round(real_derivation,2)
            

            self.y_ax2.append(real_derivation)     

        self.ax2.set_ybound(min(self.y_ax1)-(min(self.y_ax1)/10),max(self.y_ax1)+(max(self.y_ax1)/10))
        if LIMIT_ACCELERATION:
            self.ax2.text(0.35,0.95,f"Acceleration display limit: {MAX_ACCELERATION}",transform=self.ax2.transAxes,horizontalalignment="right",va="top")
        if ACCELERATION_LOG10:
            self.secondary_label = "Acceleration [log(RPM/s)]"
        else:
            self.secondary_label = "RPM Acceleration [RPM/s]"

        self.ax2_stat = f"Max Accl.: {max(self.y_ax2)} RPM/s\nMin Accl.: {min(self.y_ax2)} RPM/s"
        self.ax2.set_ylabel(self.secondary_label,size=LABEL_SIZE)

    def calculate_rev_count(self):
        i = 1
        self.y_ax2=[]
        while i <= len(self.x_ax1):
            self.y_ax2.append(i)
            i+=1
        self.ax2.set_ylabel("Completed revolutions []",size=LABEL_SIZE)
        self.ax2.set_ybound(0,len(self.y_ax1)+len(self.y_ax1)/10)
        self.secondary_label = "Rev count"
        self.ax2_stat = f"Rev. Count: {len(self.y_ax2)}"
    
    def show_sine(self): # very experimental, does not work as of now
        self.y_ax2 = np.sin(self.x_ax1)
        self.ax2.set_ylabel("Sine of x",size=LABEL_SIZE)
        self.ax2.set_ybound(0,len(self.y_ax1)+len(self.y_ax1)/10)
        self.secondary_label = "Sine"

    def draw_graph(self):
        print("generating graph")
        
        self.calculate_derivation()

        self.ax1.set_title(f"Analysis of: {self.run_name}",size=TITLE_SIZE)

        self.ax1.set_xlabel("Time [second]",size=LABEL_SIZE)
        self.ax1.set_ylabel(self.main_label,size=LABEL_SIZE)
        self.ax1.grid()

        self.ax1.set_zorder(10)
        self.ax2.set_zorder(1)
        self.ax1.patch.set_visible(False)  # prevents background blocking

        if ACCELERATION_LOG10:
            self.ax2.set_yscale("symlog")
        
        #plot lines
        self.ax2.plot(
            self.x_ax1,
            self.y_ax2,
            color=AX2_COLOR,
            linewidth=1.3,
            label=self.secondary_label
            )
        line_rpm, = self.ax1.plot(
            self.x_ax1,
            self.y_ax1,
            linewidth=AX1_LINE,
            label=self.main_label,
            color=AX1_COLOR
            )
        
        line_rpm.set_path_effects([pe.Stroke(linewidth=(AX1_LINE*2),foreground="white"),pe.Normal()])
        
        # legend merge
        handle_ax1, label_ax1 = self.ax1.get_legend_handles_labels()
        handle_ax2, label_ax2 = self.ax2.get_legend_handles_labels()

        #display legend
        self.ax1.legend(
            handles=handle_ax1+handle_ax2,
            labels=label_ax1+label_ax2,
            loc="upper right",
            edgecolor="black",
            fancybox = False,
            fontsize= LABEL_SIZE
            )

        #display horizontal lines
        self.ax1.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=AX1_COLOR)
        self.ax2.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=AX2_COLOR)
        #self.ax1.vlines((self.x_ax1[-1]/2), ymin=0, ymax=max(self.y_ax1), color="red") #for debug only, shows line in the middle of the time

        if STAT_TEXT:
            self.ax1.text( # cool stats display
                (self.x_ax1[-1])*(0.885),
                max(self.y_ax1)*(0.80),
                f"Max Speed: {max(self.y_ax1)} RPM\n{self.ax2_stat}\nRuntime: {round(self.x_ax1[-1],1)} s\nPoints: {len(self.x_ax1)}",
                bbox={"facecolor": "white","pad": 3.5},
                fontsize=LABEL_SIZE
            )

        plt.show()


graph = Graphing()  