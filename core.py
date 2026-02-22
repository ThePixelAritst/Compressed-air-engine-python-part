import socket
import keyboard
from handle_file import File_handling
from plot_graph import graph
from keyboard_controller import timeout_action



# operational variables

rpm_array = [0]
time_array = [0]
time_index = 0
rotation_number = 1 # 1 because when a signal arrives it means it already completed a rotation
receive_attempt_count = 0
stop_flag = False


# functions for all
def detect_interrupt(event): #detects key press during the listening phase
    global stop_flag
    if event.event_type == keyboard.KEY_DOWN:
        stop_flag = True

def save_rpm(time_data): #saves the current rpm into an array, which it expands
    time_since_last_rev = float(time_data[1])
    revs = round((60*10**6/time_since_last_rev),1)
    rpm_array.append(revs)
    return revs

def save_time(time_data): #saves the current time signature into an array, which it expands
    fetched_period = float(time_data[1])*10**-6
    global time_index
    last_period = time_array[time_index]
    print(time_index)
    if time_index == 0:
        current_period = 0
    else:    
        current_period = fetched_period + last_period
    current_period = round(current_period,3)
    time_array.append(current_period)
    time_index +=1
    return current_period

def draw_only_initiation(): # the option to not initiate the program and only draw the graph from existing data directory
    print("Press any key to interrupt startup\n")
    if timeout_action(3.5):
        graph.set_from_file()
        graph.draw_graph()
        exit()

def file_rename_prompt():
    print("Press any key to rename newly created file\n")
    if timeout_action(3):
        file.rename_file()

draw_only_initiation()




print("Startup initiated")

# setup of the connection
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(2)

# main loop, here it loops until an interrupt is detected
file = File_handling() # initiation of the file system
keyboard.hook(detect_interrupt) # starts the listening for any key press
print("Listening...")
while not stop_flag:
    try: #if the connection times out, this block will be skipped
        data = sock.recv(1024) # receives information from motoras list, where [n of finished revolution, time period of the last revolution in microsec (10**-6)]
        if not data: exit("Connection closed by peer")
        receive_attempt_count = 0
        fetched_packet = (data.decode()).split()
        print(f"Motor: {fetched_packet[0]}, Python: {rotation_number}")
        rotation_number +=1
        current_rpm = save_rpm(fetched_packet)
        current_time = save_time(fetched_packet)
        print(f"Current RPM: {current_rpm}, completed revolutions: {rotation_number}, at time: {current_time}")
    except:
        print(f"unsuccessful receive attempt: {receive_attempt_count}")
        receive_attempt_count +=1
        continue

print("Listening stop")
print(f"{len(time_array)} total points")

keyboard.unhook_all()

#save data
file.save_to_file(f"{[len(time_array),len(rpm_array)]}")
file.save_to_file(time_array)
file.save_to_file(rpm_array)
file.close_file()

file.fetch_file_name()
file_rename_prompt()

graph.set_from_data(time_array,rpm_array,file.fetch_file_name())
graph.draw_graph()