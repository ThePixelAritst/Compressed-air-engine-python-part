import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Listening...")

last_count = 0
while True:
    data, addr = sock.recvfrom(1024)
    fetched_packed = (data.decode()).split()
    time_difference = float(fetched_packed[1])
    rpm = (60*10**6/time_difference)
    rpm = rpm.__round__()
    increment = int(fetched_packed[0]) - last_count
    last_count = int(fetched_packed[0])
    print(f"cur. rpm: {rpm}; current counter: {int(fetched_packed[0])}, increment: {increment} ")
