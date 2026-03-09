import sys
import socket

def zad7():
  if len(sys.argv) != 3:
    print("Użycie: python main.py <adres_ip_lub_hostname> <port>")
    sys.exit(1)

  host = sys.argv[1]
  port = sys.argv[2]

  if not port.isdigit():
    print("Port musi być liczbą całkowitą.")
    sys.exit(1)

  port = int(port)

  try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.settimeout(5) 
      s.connect((host, port))
      
      try:
        service = socket.getservbyport(port)
      except OSError:
        service = "nieznana"
      print(f"Połączenie z {host}:{port} zostało nawiązane pomyślnie.")
      print(f"Usługa działająca na porcie {port}: {service}")
  except socket.timeout:
    print(f"Przekroczono czas oczekiwania na połączenie z {host}:{port}.")
  except socket.gaierror:
    print(f"Nie można rozpoznać adresu: {host}")
  except ConnectionRefusedError:
    print(f"Połączenie odrzucone przez {host}:{port}.")
  except Exception as e:
    print(f"Wystąpił błąd: {e}")

zad7()