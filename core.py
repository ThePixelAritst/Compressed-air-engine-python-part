import socket
from handle_file import file
from plot_graph import graph
from keyboard_controller import timeout_action,detect_keystroke,clear_keyboard_buffer
import numpy as np


# operational variables

rpm_array = []
time_array = []
time_pointer = 0
rotation_number = 1 # 1 because when a signal arrives it means it already completed a rotation
receive_attempt_count = 0
stop_flag = False
detected_stop = False

# operational constants

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

# Animation settings
ANIMATE = False
FRAME_RATE = 12

# Engine estimates
MAX_RPM_ESTIMATE = 2500
MIN_RPM_ESTIMATE = 150


# functions for all

def fetch_period_time(packet,rounding=3):
    fetched_period = round(float(packet[1])*10**-6,rounding)
    return(fetched_period) # returns the period time of the most recent period, expressed in seconds with (variable) number of decimal places

def save_rpm(time_data): #saves the current rpm into an array, which it expands
    revs = round((60/fetch_period_time(time_data)),1)
    rpm_array.append(revs)
    return revs

def save_time(time_data): #saves the current time signature into an array, which it expands
    global time_pointer
    last_period = time_array[time_pointer]
    print(time_pointer)
    if time_pointer == 0:
        current_period = 0
    else:    
        current_period = fetch_period_time(time_data,3) + last_period
    time_array.append(current_period)
    time_pointer +=1
    return current_period

def choose_animation():
    if not ANIMATE:
        graph.draw_static()
    else:
        graph.animate(FRAME_RATE)

def draw_only_initiation(): # the option to not initiate the program and only draw the graph from existing data directory
    print("Press any key to interrupt startup\n")
    if timeout_action(3.5):
        graph.set_from_file()
        choose_animation()
        exit()

def file_rename_prompt():
    print("Press any key to rename newly created file\n")
    if timeout_action(3):
        file.rename_file()

draw_only_initiation() # Asks the user if they want to only plot-graph


# Initiation protocol - boots up 

print("Initiation")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(2)

clear_keyboard_buffer()
file.inititiate_file()

# Main loop keeps listening for any incoming packets from the motor, 

print("Listening...")
while not stop_flag:
    if detect_keystroke():
        clear_keyboard_buffer()
        break
    try: #if the connection times out, this block will be skipped
        data = sock.recv(1024) # receives information from motoras list, where [n of finished revolution, time period of the last revolution in microsec (10**-6)]
        if not data: exit("Connection closed by peer")
        fetched_packet = (data.decode()).split()
        print(f"Motor: {fetched_packet[0]}, Python: {rotation_number}")
        rotation_number +=1
        time_delta = time_array[-1] - fetch_period_time(fetched_packet)
        if time_delta > 60 / MIN_RPM_ESTIMATE:
            current_rpm = save_rpm(fetched_packet)
            current_time = save_time(fetched_packet)
        current_rpm = save_rpm(fetched_packet)
        current_time = save_time(fetched_packet)
        print(f"Current RPM: {current_rpm}, completed revolutions: {rotation_number}, at time: {current_time}")
        receive_attempt_count = 0
    except:
        print(f"unsuccessful receive attempt: {receive_attempt_count}")
        receive_attempt_count +=1
        continue


print("Listening stopped")
print(f"{len(time_array)} total points")

#save data
file.save_to_file(f"{[len(time_array),len(rpm_array)]}")
file.save_to_file(time_array)
file.save_to_file(rpm_array)
file.close_file()

file.fetch_file_name()
file_rename_prompt()

graph.set_from_data(time_array,rpm_array,file.fetch_file_name())

choose_animation()