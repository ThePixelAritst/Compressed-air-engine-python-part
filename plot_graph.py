#import matplotlib
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import ast
import os
from handle_file import file


MAX_WATCHDOG = 5

class Graphing():
    def __init__(self):
        self.fig, self.ax1 = plt.subplots()
        self.ax2 = self.ax1.twinx()
        self.x_ax1=[]
        self.y_ax1=[]
        self.y_ax2 = []
        self.run_name = None

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
        derivation=0
        self.y_ax2=[]
        while pointer < len(self.y_ax1):
            derivation = self.y_ax1[pointer]-self.y_ax1[pointer-1]
            self.y_ax2.append(derivation)
            pointer += 1

        self.ax2.set_ylabel("RPM derivation")
        self.ax2.set_ybound(min(self.y_ax1)-(min(self.y_ax1)/10),max(self.y_ax1)+(max(self.y_ax1)/10))

    def calculate_rev_count(self):
        i = 1
        self.y_ax2=[]
        while i <= len(self.x_ax1):
            self.y_ax2.append(i)
            i+=1
        self.ax2.set_ylabel("Completed revolutions (count)")
        self.ax2.set_ybound(0,len(self.y_ax1)+len(self.y_ax1)/10)

    def draw_graph(self):
        print("generating graph")
        
        self.calculate_derivation()

        self.ax1.set_title(f"Analysis of run:  {self.run_name}")

        self.ax1.set_xlabel("Time (second)")
        self.ax1.set_ylabel("Rotational speed (RPM)")

        self.ax1.plot(self.x_ax1,self.y_ax1,linewidth=2.2)
        self.ax2.plot(self.x_ax1,self.y_ax2,color="orange",linewidth=1.4)

        self.ax1.grid(axis="y")

        self.ax1.set_label("RPM")
        self.ax2.set_label("Rev. Count")

        plt.show()


graph = Graphing()  