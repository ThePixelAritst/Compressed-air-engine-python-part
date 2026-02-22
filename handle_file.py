from pathlib import Path
import time
import os



class File_handling():
    def __init__(self):
        self.date = time.strftime("%Y-%m-%d--%a--%H-%M-%S") #creates a date in the following form: "YYYY-MM-DD--Name of day--HH-MinMin-SS"
        self.base_directory = Path(__file__).resolve().parent
        self.data_path = os.path.join(self.base_directory,"data",f"{self.date}.txt") #self.base_directory / "data" / self.date + ".txt"
        self.data_file = open(self.data_path,"a")
        self.file_name = self.date

    def save_to_file(self,text):
        self.data_file.write(f"{text}\n")
        self.data_file.flush()

    def fetch_date_name(self):
        return self.date
    
    def close_file(self):
        self.data_file.close()

    def fetch_file_name(self):
        self.file_name = (os.path.basename(self.data_path).split("."))[0]
        print(f"Current file name: {self.file_name}")
        return self.file_name
        
    def rename_file(self): #closes the file automatically just in case
        self.close_file()
        chosen_file_name = input("Input chosen name (without extensions):\n").strip("./,")
        new_name = os.path.join(self.base_directory,"data",f"{chosen_file_name}.txt")
        os.rename(self.data_path, new_name)
        self.data_path = new_name