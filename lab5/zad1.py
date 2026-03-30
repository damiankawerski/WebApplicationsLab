import socket

HOST = "127.0.0.1"
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    while True:
        guess = input("Podaj liczbę: ")
        s.sendall(guess.encode())

        data = s.recv(1024).decode()
        print("Serwer:", data)

        if "równa" in data or "good" in data.lower():
            print("Success")
            break