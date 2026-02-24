import matplotlib
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import ast
import os

MAX_WATCHDOG = 5

class Graphing():
    def __init__(self):
        self.fig, self.ax1 = plt.subplots()
        self.ax2 = self.ax1.twinx()
        self.x=[]
        self.y=[]
        self.rev = []
        self.run_name = None

    def set_from_file(self):
        readable = False
        watchdog = 0
        while readable == False:
            try:
                file_path = input("Please insert full path to file:\n").strip()
                datafile = open(file_path,"r")
                readable = datafile.readable()
            except:
                print(f"File at specified directory does not exist. Watchdog: {watchdog}/{MAX_WATCHDOG}")
                if watchdog >= MAX_WATCHDOG:
                    exit("Watchdog exceeded")
                watchdog += 1
            if not readable:
                print("Unreadable file")
                watchdog += 1
                continue
            separated_datafile = datafile.readlines()
            processed_check = ast.literal_eval(separated_datafile[0]) #converts the mess of a string into a list with ints 
            if processed_check[0] != processed_check[1]:
                Exception("Count does not match. Cannot draw graph")
            elif len(separated_datafile) < 2:
                Exception("Incorrect file, cannot draw graph")
        self.x = ast.literal_eval(separated_datafile[1])
        self.y = ast.literal_eval(separated_datafile[2])
        self.run_name = os.path.basename(file_path).split(".")[0] #converts the filepath to only show the name of the file to be displayed

    def set_from_data(self,set_x,set_y,name="Not Set"):
        self.x = set_x
        self.y = set_y
        self.run_name = name


    def draw_graph(self):
        print("generating graph")
        i = 1
        while i <= len(self.x):
            self.rev.append(i)
            i+=1
        self.ax1.set_title(f"RPM based on time. Data of run:  {self.run_name}")

        self.ax2.set_ylabel("Completed revolutions (count)")
        self.ax2.set_ybound(0,len(self.x)+len(self.x)/10)

        self.ax1.set_xlabel("Time (second)")
        self.ax1.set_ylabel("Rotational speed (RPM)")

        self.ax1.plot(self.x,self.y,linewidth=2.2)
        self.ax2.plot(self.x,self.rev,color="orange",linewidth=1.4)

        self.ax1.grid(axis="y")

        self.ax1.set_label("RPM")
        self.ax2.set_label("Rev. Count")

        plt.show()


graph = Graphing()  