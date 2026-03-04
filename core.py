import socket
from handle_file import file
from plot_graph import graph
from keyboard_controller import timeout_action,detect_keystroke,clear_keyboard_buffer


# operational variables

rpm_array = [0]
time_array = [0]
time_index = 0
rotation_number = 1 # 1 because when a signal arrives it means it already completed a rotation
receive_attempt_count = 0
stop_flag = False

# operational constants

UDP_IP = "0.0.0.0"
UDP_PORT = 5005


# functions for all

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

def set_start_stop(is_stop):
    x_intersect = 0
    x1 = time_array[-2]
    x2 = time_array[-1]
    y1 = rpm_array[-2]
    y2 = rpm_array[-1]

    if y1 != y2: #if y1 = y2, division with 0 would be attempted. Unlikely, but neccessary
        x_intersect = ((y1-y2) + (x2-x1))/(y1-y2)
    elif is_stop:
        x_intersect = x2
    else:
        x_intersect = x1 

    if is_stop: #if the calculation was for the stop, the point can be added to the end of the graph
        time_array.append(x_intersect)
        rpm_array.append(0)
    else: #since this was a start, and a 2 points already exist before this was created, it needs to be added before these points
        time_array.insert(len(time_array)-3,x_intersect)
        rpm_array.insert(len(rpm_array)-3,0)
    
def calculate_horizontal_intersect(y_level=0):
    x1 = time_array[len(time_array-2)]
    x2 = time_array[len(time_array-1)]
    y1 = rpm_array[len(rpm_array-2)]
    y2 = rpm_array[len(rpm_array-1)]

    if y1 != y2:
        x_intersect = ((x1-x2)*y_level+(y1-y2)*x1+(x2-x1)*y1)/(y1-y2)
    else:
        raise Exception("Undefined intersect")
    
    return x_intersect


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
        current_rpm = save_rpm(fetched_packet)
        current_time = save_time(fetched_packet)
        if receive_attempt_count > 0:
            set_start_stop(False)
        if fetched_packet:
            pass
        print(f"Current RPM: {current_rpm}, completed revolutions: {rotation_number}, at time: {current_time}")
        receive_attempt_count = 0
    except:
        print(f"unsuccessful receive attempt: {receive_attempt_count}")
        if receive_attempt_count == 0 and len(time_array) > 5:
            set_start_stop(True)
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
graph.draw_graph()