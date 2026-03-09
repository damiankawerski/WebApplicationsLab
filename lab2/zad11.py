import socket

MAX_PACKET_LENGTH = 20


def pad_or_truncate(message: str) -> str:
    if len(message) < MAX_PACKET_LENGTH:
        return message.ljust(MAX_PACKET_LENGTH)
    return message[:MAX_PACKET_LENGTH]


def zad11(message: str, host: str = "localhost", port: int = 2908, timeout: float = 5.0) -> str:
    fixed_message = pad_or_truncate(message)
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall(fixed_message.encode("utf-8"))
            response = b""
            while len(response) < MAX_PACKET_LENGTH:
                chunk = s.recv(MAX_PACKET_LENGTH - len(response))
                if not chunk:
                    break
                response += chunk
            return response.decode("utf-8", errors="replace")
    except OSError as exc:
        return f"Blad komunikacji z serwerem {host}:{port} - {exc}"


if __name__ == "__main__":
    message = input("Podaj wiadomość do wysłania ")
    if len(message) < MAX_PACKET_LENGTH:
        print(f"uzupełniono do {MAX_PACKET_LENGTH} znakow.")
    elif len(message) > MAX_PACKET_LENGTH:
        print(f"przycięto do {MAX_PACKET_LENGTH} znakow")
    response = zad11(message)
    print(f"Odpowiedź serwera: '{response}'")

