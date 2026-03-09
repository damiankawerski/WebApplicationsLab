import ipaddress

def read_from_console():
    filename = input("Podaj zawartość pliku: ")
    return filename

def write_to_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)


def write_to_binary_file(filename, source_filename):
    with open(source_filename, 'rb') as source:
        content = source.read()

    with open(filename, 'wb') as f:
        f.write(content)

def validate_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def get_hostname_from_ip(ip_str):
    import socket
    try:
        hostname, _, _ = socket.gethostbyaddr(ip_str)
        return hostname
    except socket.herror:
        return None
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None
    
def get_ip_from_hostname(hostname):
    import socket
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror:
        return None
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None