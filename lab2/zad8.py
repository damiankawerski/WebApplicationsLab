import sys
import socket

def zad8():
  if len(sys.argv) != 2:
    print("Użycie: python zad8.py <adres_ip_lub_hostname>")
    sys.exit(1)

  host = sys.argv[1]

  port_iter = range(1, 65536) 
  open_ports = []
  open_services = {}

  for port in port_iter:
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        result = s.connect_ex((host, port))
        if result == 0:
          try:
            service = socket.getservbyport(port)
          except OSError:
            service = "nieznana"
          open_ports.append(port)
          open_services[port] = service
    except Exception as e:
      print(f"Wystąpił błąd podczas skanowania portu {port}: {e}")

  print(f"Otwarte porty na hoście {host}: {open_ports}")
  print(f"Usługi działające na otwartych portach: {open_services}")

zad8()