import socket
import random

HOST = "127.0.0.1"
PORT = 8080

number = random.randint(1, 100)
print("Wylosowana liczba:", number)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)

    conn, addr = s.accept()
    with conn:
        print("Połączono:", addr)

        while True:
            data = conn.recv(1024).decode()

            try:
                guess = int(data)
            except:
                conn.sendall("Zła liczba".encode())
                continue

            if guess < number:
                conn.sendall("Za mała".encode())
            elif guess > number:
                conn.sendall("Za duża".encode())
            else:
                conn.sendall("Równa".encode())
                break