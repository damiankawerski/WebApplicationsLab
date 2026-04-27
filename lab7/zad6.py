import socket
import ssl

POP3_HOST = "poczta.interia.pl"
POP3_PORT = 995


def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\r\n"):
        buf += sock.recv(1)
    return buf.decode(errors="replace").strip()


def send_cmd(sock, cmd):
    sock.sendall((cmd + "\r\n").encode())


def check_ok(line, context=""):
    if not line.startswith("+OK"):
        raise RuntimeError(f"Błąd POP3 [{context}]: {line}")


class POP3Client:
    def __init__(self, host, port):
        raw_sock = socket.create_connection((host, port))
        ssl_context = ssl.create_default_context()
        self.sock = ssl_context.wrap_socket(raw_sock, server_hostname=host)

    def connect(self):
        return recv_line(self.sock)

    def user(self, username):
        send_cmd(self.sock, f"USER {username}")
        return recv_line(self.sock)

    def passwd(self, password):
        send_cmd(self.sock, f"PASS {password}")
        return recv_line(self.sock)

    def stat(self):
        send_cmd(self.sock, "STAT")
        resp = recv_line(self.sock)
        check_ok(resp, "STAT")
        parts = resp.split()
        return int(parts[1]), int(parts[2])

    def quit(self):
        send_cmd(self.sock, "QUIT")
        return recv_line(self.sock)

    def close(self):
        self.sock.close()


def main():
    user     = input("Login: ").strip()
    password = input("Hasło: ").strip()

    client = POP3Client(POP3_HOST, POP3_PORT)
    try:
        check_ok(client.connect(), "connect")
        check_ok(client.user(user), "USER")
        check_ok(client.passwd(password), "PASS")

        count, total = client.stat()

        print(f"Liczba wiadomości: {count}")
        print(f"Łączny rozmiar: {total} B")

        client.quit()
    finally:
        client.close()


if __name__ == "__main__":
    main()