import os
import time
from pathlib import Path
import program_settings as sett
datset = sett.data_settings
genset = sett.general_settings

class Data():
    def __init__(self,opened_file,format):
        if opened_file is None or opened_file.closed:
            raise ValueError(f"Expected an open file object, got: {opened_file!r}")
        self.file = opened_file
        self.format = format

    def file_write(self,string_to_write):
        self.file.write(string_to_write)


class File(Data):   
    def create_file(self,format=datset.DEFAULT_FORMAT): #creates file
        if self.file_open:
            raise RuntimeError("Cannot create secondary file in one class instance")
        self.file_open = True
        self.file_name = time.strftime("%Y-%m-%d--%a--%H-%M-%S")
        if datset.DEBUG_MODE:
            self.folder_directory = datset.DEBUG_DIRECTORY
        else:
            self.folder_directory = os.path.join(Path(__file__).resolve().parents[1],"data")
        self.format = format
        self.full_path = os.path.join(self.folder_directory,f"{self.file_name}.{self.format}")
        self.file = open(self.full_path,"a")


    def close_file(self):
        self.file.close()
        self.file_open = False

    def rename_file(self):
        chosen_name = None
        os.rename(self.full_path,os.path.join(self.folder_directory,f"{chosen_name}.{self.format}"))


    def open_file(self,handover=None):
        if self.file_open:
            raise RuntimeError("Cannot open secondary file in one class instance")
    
        elif handover:
            self.full_path = handover

        else:
            attempt = 0
            while attempt < genset.MAX_WATCHDOG:
                try:
                    unconfirmed_path = input("Please input file to be opened:\n")
                    if not( Path(unconfirmed_path).exists() and Path(unconfirmed_path).is_file()):
                        raise ValueError()
                    else:
                        self.full_path = unconfirmed_path
                        print("Path valid")
                        break
                except Exception:
                    attempt += 1
                    print(f"\nInvalid or unreadable file. Attempt {attempt}/{genset.MAX_WATCHDOG}")
                finally:
                    if attempt >= genset.MAX_WATCHDOG:
                        exit("Watchdog exceeded, terminating program")
                          
        self.format = (os.path.basename(self.full_path).split()[-1]).split(".")
        #self.file_name =    
        self.folder_directory = Path(self.full_path).resolve().parent
        self.file = open(self.full_path)
            
        
    def __init__(self,open_file=True,format=datset.DEFAULT_FORMAT,handover=None):
        self.file_open = False
        if open_file:
            self.open_file(handover)
        else:
            self.create_file(format)
        if not hasattr(self, 'file') or self.file is None:
            raise RuntimeError("File not created, cannot initiate Data Class")
        #print(f"File {self.file_name} initiated successfully")
        super().__init__(self.file,format=format)


open_file = File(open_file=True)
print(open_file.format)
open_file.file_write("test_from_call")