import socket
import keyboard
import matplotlib.pyplot as plt
from handle_file import file
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import numpy as np
# setup of the connection

UDP_IP = "0.0.0.0"
UDP_PORT = 5005


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(2)

# operational variables

rpm_array = [0]
time_array = [0]
time_index = 0
rotation_number = 0
receive_attempt_count = 0
stop_flag = False

# functions for all

def detect_interrupt(event):
    global stop_flag
    if event.event_type == keyboard.KEY_DOWN:
        stop_flag = True

def save_rpm(time_data):
    time_since_last_rev = float(time_data[1])
    revs = round((60*10**6/time_since_last_rev),1)
    rpm_array.append(revs)
    return revs

def save_time(time_data):
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

# main loop, here it loops until an interrupt is detected

keyboard.hook(detect_interrupt)
print("Listening...")
while True:
    if (stop_flag==True):
        print("stopping listening")
        break
    try:
        data = sock.recv(1024)
        if not data: exit("Connection closed by peer")
        receive_attempt_count = 0
        fetched_packet = (data.decode()).split()
        print(fetched_packet)
        rotation_number +=1
        current_rpm = save_rpm(fetched_packet)
        current_time = save_time(fetched_packet)
        print(f"Current RPM: {current_rpm}, completed revolutions: {rotation_number}, at time: {current_time}")
    except:
        print("Packet timeout")
        print(f"unsuccessful receive attempt: {receive_attempt_count}")
        receive_attempt_count +=1
        continue

keyboard.unhook_all()
#rotation_count_array = np.linspace(0,rotation_number,rotation_number)


#print data to console
print(f"{rpm_array}\n\n{time_array}")
print(f"{len(rpm_array)}; {len(time_array)}")

#save data
file.save_to_file(f"{[len(time_array),len(rpm_array),rotation_number]}")
file.save_to_file(time_array)
file.save_to_file(rpm_array)
#file.save_to_file(rotation_count_array)


#create graph

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax2.set_ylabel("Revolution count")
ax1.set_title("RPM based on time")
ax1.set_xlabel("Time")
ax1.set_ylabel("RPM")
#ax1.yaxis.set_major_locator(MultipleLocator(1000))
#ax1.xaxis.set_major_locator(MultipleLocator(1))
#ax2.yaxis.set_major_locator(MultipleLocator(50))

ax1.plot(time_array,rpm_array)
#ax2.plot(time_array,rotation_count_array)
plt.show()