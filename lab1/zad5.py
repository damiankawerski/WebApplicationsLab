from utils import get_ip_from_hostname
import sys

def zad5():
  if len(sys.argv) != 2:
    print("Użycie: python main.py <nazwa_hosta>")
    sys.exit(1)
     
  hostname = sys.argv[1]

  try:
    ip_address = get_ip_from_hostname(hostname)
    if ip_address:
      print(f"Adres IP dla hosta {hostname}: {ip_address}")
    else:
      print(f"Nie znaleziono adresu IP dla hosta {hostname}")
  except Exception as e:
    print(f"Wystąpił błąd: {e}")