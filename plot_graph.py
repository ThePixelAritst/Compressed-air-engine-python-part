import matplotlib.pyplot as plt
import ast

class Graphing():
    def __init__(self):
        self.fig, self.ax1 = plt.subplots()
        self.ax2 = self.ax1.twinx()
        self.x=[]
        self.y=[]

    def read_file_content(self):
        readable = False
        while readable == False:
            file_path = input("Please insert full path to file:\n").strip()
            datafile = open(file_path,"r")
            readable = datafile.readable()
            if not readable: print("Unreadable file")
            separated_datafile = datafile.readlines()
            processed_check = ast.literal_eval(separated_datafile[0]) #converts the mess of a string into a list with ints 
            if processed_check[0] != processed_check[1]:
                Exception("Count does not match. Cannot draw graph")
            elif len(separated_datafile) < 2:
                Exception("Incorrect file, cannot draw graph")
            self.x = ast.literal_eval(separated_datafile[1])
            self.y = ast.literal_eval(separated_datafile[2])

    def set_from_data(self,set_x,set_y):
        self.x = set_x
        self.y = set_y

    def draw_graph(self):
        #self.ax2.set_ylabel("Revolution count")
        self.ax1.set_title("RPM based on time")
        self.ax1.set_xlabel("Time")
        self.ax1.set_ylabel("RPM")
        self.ax1.plot(self.x,self.y)
        self.ax1.grid(axis="y")
        plt.show()


graph = Graphing()  