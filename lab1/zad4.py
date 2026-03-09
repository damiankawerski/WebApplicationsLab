from utils import get_hostname_from_ip
import sys

def zad4():
  if len(sys.argv) != 2:
    print("Użycie: python main.py <adres_ip>")
    sys.exit(1)
     
  ip_address = sys.argv[1]

  try:
    hostname = get_hostname_from_ip(ip_address)
    if hostname:
      print(f"Hostname dla {ip_address}: {hostname}")
    else:
      print(f"Nie znaleziono hosta dla adresu {ip_address}")
  except Exception as e:
    print(f"Wystąpił błąd: {e}")