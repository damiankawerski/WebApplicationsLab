import socket

MAX_PACKET_LENGTH = 20


def pad_or_truncate(message: str) -> str:
    if len(message) < MAX_PACKET_LENGTH:
        return message.ljust(MAX_PACKET_LENGTH)
    return message[:MAX_PACKET_LENGTH]


def sendall_guaranteed(sock: socket.socket, data: bytes) -> int:
    total_sent = 0
    while total_sent < len(data):
        sent = sock.send(data[total_sent:])
        if sent == 0:
            raise OSError("CONN_ERROR")
        total_sent += sent
    return total_sent


def recvall_guaranteed(sock: socket.socket, length: int) -> bytes:
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise OSError("CONN_ERROR")
        data += chunk
    return data


def zad12(message: str, host: str = "localhost", port: int = 2908, timeout: float = 5.0) -> str:
    fixed_message = pad_or_truncate(message)
    data_to_send = fixed_message.encode("utf-8")
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            sent = sendall_guaranteed(s, data_to_send)
            print(f"Wysłano {sent} bajtów.")
            response = recvall_guaranteed(s, MAX_PACKET_LENGTH)
            print(f"Odebrano {len(response)} bajtów.")
            return response.decode("utf-8", errors="replace")
    except OSError as exc:
        return f"Blad komunikacji z serwerem {host}:{port} - {exc}"


if __name__ == "__main__":
    message = input("Podaj wiadomość do wysłania: ")
    if len(message) < MAX_PACKET_LENGTH:
        print(f"uzupełniono do {MAX_PACKET_LENGTH} znakow.")
    elif len(message) > MAX_PACKET_LENGTH:
        print(f"przycięto do {MAX_PACKET_LENGTH} znakow")
    response = zad12(message)
    print(f"Odpowiedź serwera: '{response}'")

