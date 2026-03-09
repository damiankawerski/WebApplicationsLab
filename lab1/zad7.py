import sys
import socket

def zad7():
  if len(sys.argv) != 2:
    print("Użycie: python main.py <adres_ip_lub_hostname> <port>")
    sys.exit(1)

  host = sys.argv[1]

  port_iter = range(1, 65536) 
  open_ports = []

  for port in port_iter:
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        result = s.connect_ex((host, port))
        if result == 0:
          open_ports.append(port)
    except Exception as e:
      print(f"Wystąpił błąd podczas skanowania portu {port}: {e}")

  print(f"Otwarte porty na hoście {host}: {open_ports}")