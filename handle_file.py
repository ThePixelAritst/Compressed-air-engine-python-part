from pathlib import Path
import time



class File_handling():
    def __init__(self):
        date = time.strftime("%Y-%m-%d--%a--%H-%M-%S") #creates a date in the following form: "YYYY-MM-DD--Name of day--HH-MinMin-SS"
        base_directory = Path(__file__).resolve().parent
        data_path = base_directory / "data" / date
        self.data_file = open(f"{data_path}.txt","a")

    def save_to_file(self,text):
        self.data_file.write(f"{text}\n")
        self.data_file.flush()

file = File_handling()