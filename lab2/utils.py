from datetime import datetime
import ntplib
import socket

def get_user_input():
    number1 = input("Podaj pierwszą liczbę (lub 'exit' aby zakończyć): ")
    if number1.lower() == "exit":
        return None
    number2 = input("Podaj drugą liczbę (lub 'exit' aby zakończyć): ")
    if number2.lower() == "exit":
        return None
    operator = input("Podaj operator (+, -, *, /) (lub 'exit' aby zakończyć): ")
    if operator.lower() == "exit":
        return None
    return number1, number2, operator


def get_time_and_date(host: str = "ntp.task.gda.pl", timeout: float = 5.0) -> str:
    try:
        client = ntplib.NTPClient()
        response = client.request(host, version=3, timeout=timeout)
        current_dt = datetime.fromtimestamp(response.tx_time)
        return current_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as exc:
        return f"Blad pobierania czasu NTP z {host} - {exc}"
    

def send_message_to_server_tcp(message: str, host: str = "localhost", port: int = 2900) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(message.encode())
            response = s.recv(1024).decode()
            return response
    except Exception as exc:
        return f"Blad komunikacji z serwerem {host}:{port} - {exc}"
    
    
def send_message_to_server_udp(message: str, host: str = "localhost", port: int = 2901):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message.encode(), (host, port))
            response, _ = s.recvfrom(1024)
            return response.decode()
    except Exception as exc:
        return f"Blad komunikacji z serwerem {host}:{port} - {exc}" 
    
def send_message_to_server_udp_calc(
    number1: float,
    number2: float,
    operator: str,
    host: str = "localhost",
    port: int = 2902,
    timeout: float = 5.0,
) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            s.sendto(str(number1).encode(), (host, port))
            s.sendto(operator.encode(), (host, port))
            s.sendto(str(number2).encode(), (host, port))
            response, _ = s.recvfrom(1024)
            return response.decode()
    except Exception as exc:
        return f"Blad komunikacji z serwerem {host}:{port} - {exc}"