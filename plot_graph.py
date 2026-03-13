import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.animation as anim
from matplotlib.ticker import AutoMinorLocator
import math
import ast
import os
from pathlib import Path
from handle_file import file
import numpy as np
import imageio_ffmpeg

# Purely technical
MAX_WATCHDOG = 5 # maximum number of attempts for file input
COLLUMN_NUMBER = 10
GRAPH_COLLUMNS = 7

# Crucial setup
SAVE_FIG = True # Saves the generated graph to file
SIZE_X = 22 # canvas size, width
SIZE_Y = 10 # canvas size, height

# Derivation function controls
MAX_ACCELERATION = 1500 #maximum acceleration that will still be displayed, no data lost
LIMIT_ACCELERATION = True # turns on MAX_ACCELERATION limit, if False will display all calculated values
ACCELERATION_LOG10 = False # displays acceleration in symlog scale

# Graphical settings
TITLE_SIZE = 28
LABEL_SIZE = 12 # basically everything not a title uses this
STAT_TEXT = True # info board with some useful and cool stats

AX1_COLOR = "black" # color of main (rpm) line
AX2_COLOR = "#237fd4" # color of secondary line
AX1_LINE = 2.5 # linewidth of the main (rpm) line



class Graphing():
    def __init__(self):
        plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
        self.fig = plt.figure(num="Main Figure",figsize=[SIZE_X,SIZE_Y],layout="constrained")
        if STAT_TEXT:
            self.ax1 = self.fig.add_subplot(1,COLLUMN_NUMBER,(1,GRAPH_COLLUMNS))
        else:
            self.ax1 = self.fig.add_subplot()
        self.ax2 = self.ax1.twinx()
        self.x_ax1=[]
        self.main = []
        self.y_ax1=[]
        self.y_ax2 = []
        self.secondary = []
        self.run_name = None
        self.secondary_label = ""
        self.main_label = "Rotational speed [RPM]"
        self.ax2_stat = ""
    
    def verify_data(self):
        if self.axis_length[0] != self.axis_length[1]:
            raise ValueError(f"Invalid data length, X: {self.axis_length[0]}, Y: {self.axis_length[1]}")

    def set_from_file(self):
        file_path, returned_data = file.open_and_separate()
        self.axis_length = ast.literal_eval(returned_data[0])
        #self.verify_data()
        self.x_ax1 = ast.literal_eval(returned_data[1]) #X axis data
        self.y_ax1 = ast.literal_eval(returned_data[2]) #Y axis data
        self.run_name = os.path.basename(file_path).split(".")[0] #converts the filepath to only show the name of the file to be displayed

    def set_from_data(self,set_x,set_y,name="Not Set"):
        self.axis_length[len(self.x_ax1),len(self.y_ax2)]
        #self.verify_data()
        self.x_ax1 = set_x
        self.y_ax1 = set_y
        self.run_name = name

    def basic_data_read(self):
        self.float_run_time = round(self.x_ax1[-1],2)
        self.ceil_run_time = math.ceil(self.float_run_time)
        self.x_points = len(self.x_ax1)
        self.x_max = max(self.x_ax1)

    def save_plotted_graph(self,save_name,animated,format=None,animated_writer="ffmpeg"):
        base_directory = Path(__file__).resolve().parent
        if animated:
            if not format:
                format = "mp4"
            print("Saving animated figure")
            data_path = os.path.join(base_directory,"graphs","animated",f"{save_name}.{format}")
            self.ani.save(data_path,writer=animated_writer)
        else:
            if not format:
                format = "png"
            print("Saving static figure")
            data_path = os.path.join(base_directory,"graphs","static",f"{save_name}.{format}")
            plt.savefig(data_path)




    def calculate_derivation(self):
        pointer = 0
        real_derivation = 0
        derivation_edge = [0,0]
        self.y_ax2=[]
        while pointer < len(self.y_ax1):
            if (self.y_ax1[pointer] or self.y_ax1[pointer-1]) == np.nan:
                self.y_ax2.append(np.nan)
                pointer += 1
                continue

            raw_derivation = self.y_ax1[pointer]-self.y_ax1[pointer-1]
            if self.x_ax1[pointer]-self.x_ax1[pointer-1] != 0:
                interval_coeficient = 1/(self.x_ax1[pointer]-self.x_ax1[pointer-1])
            else:
                interval_coeficient = 1

            real_derivation = raw_derivation * interval_coeficient
            pointer += 1

            if real_derivation > derivation_edge[1]:
                derivation_edge[1] = real_derivation
            elif real_derivation < derivation_edge[0]:
                derivation_edge[0] = real_derivation

            if real_derivation > MAX_ACCELERATION or real_derivation < -MAX_ACCELERATION and LIMIT_ACCELERATION:
                real_derivation = np.nan

            real_derivation = round(real_derivation,2)
            

            self.y_ax2.append(real_derivation)     

        self.ax2.set_ybound(min(self.y_ax1)-(min(self.y_ax1)/10),max(self.y_ax1)+(max(self.y_ax1)/10))
        if ACCELERATION_LOG10:
            self.secondary_label = "Acceleration [log(RPM/s)]"
        else:
            self.secondary_label = "RPM Acceleration [RPM/s]"

        self.ax2_stat = f"Max Accl.: {round(derivation_edge[1],1)} RPM/s\nMin Accl.: {round(derivation_edge[0],1)} RPM/s" #\nAvg. Accl.: {sum(self.y_ax2)/len(self.y_ax2)} <- nefunguje kvůli NaN hodnotám
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



    def set_stat_subplot(self):
        self.ax_text = self.fig.add_subplot(1,COLLUMN_NUMBER,(GRAPH_COLLUMNS+1,COLLUMN_NUMBER))
        self.ax_text.set_title("Statistics",fontsize=TITLE_SIZE)
        self.ax_text.axis("off")



    def display_stat_text(self):
        self.set_stat_subplot()
        acceleration_limit = "None"
        if LIMIT_ACCELERATION:
            acceleration_limit = MAX_ACCELERATION
        self.full_stat_text = f"Max Speed: {max(self.y_ax1)} RPM\nAvg. Speed: {round(sum(self.y_ax1)/self.x_points,1)} RPM\n{self.ax2_stat}\nRuntime: {self.float_run_time} s\nCutoff: {acceleration_limit}\nPoints: {self.x_points}"
        self.statistics = self.ax_text.text( # cool and useful stats display
                (0.1),
                (0),
                self.full_stat_text,
                bbox={"facecolor": "white","pad": 3.5},
                fontsize=TITLE_SIZE*0.8
            )
        
    def set_common(self):
        self.calculate_derivation()
        self.basic_data_read()

        self.ax1.set_title(f"Analysis of: {self.run_name}",size=TITLE_SIZE)

        self.ax1.set_xlabel("Time [second]",size=LABEL_SIZE)
        self.ax1.set_ylabel(self.main_label,size=LABEL_SIZE)
        self.ax1.grid()

        self.ax1.set_zorder(10)
        self.ax2.set_zorder(1)
        self.ax1.patch.set_visible(False)  # prevents background blocking

        if ACCELERATION_LOG10:
            self.ax2.set_yscale("symlog")
        else:
            self.ax2.yaxis.set_minor_locator(AutoMinorLocator(4))

    def display_legend(self):
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
        
    def plot_main(self,x_coord,y_coord):
        self.main, = self.ax1.plot(
            x_coord,
            y_coord,
            linewidth=AX1_LINE,
            label=self.main_label,
            color=AX1_COLOR
        )
    
    def plot_secondary(self,x_coord,y_coord):
        self.secondary, = self.ax2.plot(
            x_coord,
            y_coord,
            color=AX2_COLOR,
            linewidth=1.3,
            label=self.secondary_label
        )



    def draw_static(self):
        print("generating static graph")
        
        self.set_common()

        #plot lines
        self.plot_secondary(self.x_ax1,self.y_ax2)
        self.plot_main(self.x_ax1,self.y_ax1)


        self.display_legend() #displays legend
        
        self.main.set_path_effects([pe.Stroke(linewidth=(AX1_LINE*2),foreground="white"),pe.Normal()]) # makes sure main line has a slight white outline
        

        #display horizontal lines
        self.ax1.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=AX1_COLOR)
        self.ax2.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=AX2_COLOR)
        #self.ax1.vlines((self.x_ax1[-1]/2), ymin=0, ymax=max(self.y_ax1), color="red") #for debug only, shows line in the middle of the time

        if STAT_TEXT:
            self.display_stat_text()

        print("Generation of static graph successful")
        if SAVE_FIG:
            self.save_plotted_graph(self.run_name,False)
        plt.show()


    # Animation Portion

    def initiate_animation(self):
        self.main.set_data([],[])
        self.secondary.set_data([],[])
        return(self.main,self.secondary)
    
    def update_frame(self,frame_number):
        # secondary line update
        self.secondary.set_data(self.x_ax1[:frame_number],self.y_ax2[:frame_number])
        # main line update
        self.main.set_data(self.x_ax1[:frame_number],self.y_ax1[:frame_number])
        # set text
        #self.debug_text.set_text(f"Frame: {frame_number}\nFrame count: {len(self.x_ax1)}")
        self.statistics.set_text(f"Cur. Speed: {self.y_ax1[frame_number-1]} RPM\nCur. Accl.: {self.y_ax2[frame_number-1]} RPM/s\n{self.full_stat_text}\nCur. Frame: {frame_number}")
        print(frame_number)
        return(self.main,self.secondary,self.statistics)

    def animate(self,frame_rate):
        print("Generating animation")
        LIMIT_RESERVE = 1.1
        self.set_common()

        self.plot_main([],[])
        self.plot_secondary([],[])

        self.ax1.set_ylim(
            min(self.y_ax1) * LIMIT_RESERVE,
            max(self.y_ax1) * LIMIT_RESERVE
        )

        self.ax1.set_xlim(-0.1 * self.x_max, self.x_max * LIMIT_RESERVE)

        self.ax2.set_ylim(
            np.nanmin(self.y_ax2) * LIMIT_RESERVE,
            np.nanmax(self.y_ax2) * LIMIT_RESERVE
        )

        self.ax2.set_xlim(-0.1 * self.x_max, self.x_max * LIMIT_RESERVE)

        self.main.set_path_effects([pe.Stroke(linewidth=(AX1_LINE*2),foreground="white"),pe.Normal()]) # makes sure main line has a slight white outline
        

        #display horizontal lines
        self.ax1.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=AX1_COLOR)
        self.ax2.hlines(y=0,xmin=0,xmax=self.x_ax1[-1],linestyles="dashed",color=AX2_COLOR)
        #self.ax1.vlines((self.x_ax1[-1]/2), ymin=0, ymax=max(self.y_ax1), color="red") #for debug only, shows line in the middle of the time
        
        self.display_legend()

        if STAT_TEXT:
            self.display_stat_text()

        self.ani = anim.FuncAnimation(
            self.fig,
            self.update_frame,
            init_func=self.initiate_animation,
            blit=True,
            frames= len(self.x_ax1),
            interval= 1000*(self.float_run_time)/(len(self.x_ax1))
        )
        if SAVE_FIG:
            self.save_plotted_graph(self.run_name,True)
        print("finished")
        plt.show()
    

graph = Graphing()  