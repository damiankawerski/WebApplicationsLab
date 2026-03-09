import socket


def zad9(ip: str, host: str = "127.0.0.1", port: int = 2906, timeout: float = 5.0) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            s.sendto(ip.encode("utf-8"), (host, port))
            response, _ = s.recvfrom(1024)
            return response.decode("utf-8", errors="replace")
    except OSError as exc:
        return f"Blad komunikacji z serwerem {host}:{port} - {exc}"


if __name__ == "__main__":
    ip = input("Podaj adres IP do sprawdzenia: ")
    print(zad9(ip))
