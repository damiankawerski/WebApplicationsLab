from utils import validate_ip
  
def zad3():
    ip_input = input("Podaj adres IP: ")
    if validate_ip(ip_input):
        print(f"{ip_input} jest poprawnym adresem IP.")
    else:
        print(f"{ip_input} nie jest poprawnym adresem IP.")
