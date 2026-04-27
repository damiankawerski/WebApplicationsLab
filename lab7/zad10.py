import socket
import ssl

POP3_HOST = "poczta.interia.pl"
POP3_PORT = 995


def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\r\n"):
        buf += sock.recv(1)
    return buf.decode(errors="replace").strip()


def recv_line_quiet(sock):
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

    def list_messages(self):
        send_cmd(self.sock, "LIST")
        header = recv_line(self.sock)
        check_ok(header, "LIST")
        messages = []
        while True:
            line = recv_line(self.sock)
            if line == ".":
                break
            parts = line.split()
            if len(parts) == 2:
                messages.append((int(parts[0]), int(parts[1])))
        return messages

    def retr(self, num):
        send_cmd(self.sock, f"RETR {num}")
        header = recv_line(self.sock)
        check_ok(header, f"RETR {num}")
        lines = []
        while True:
            line = recv_line_quiet(self.sock)
            if line == ".":
                break
            if line.startswith(".."):
                line = line[1:]
            lines.append(line)
        return lines

    def quit(self):
        send_cmd(self.sock, "QUIT")
        return recv_line(self.sock)

    def close(self):
        self.sock.close()


def parse_headers(lines):
    headers = {}
    for line in lines:
        if line == "":
            break
        for key in ("From", "To", "Subject", "Date"):
            if line.lower().startswith(key.lower() + ":"):
                headers[key] = line[len(key)+1:].strip()
    return headers


def main():
    user     = input("Login: ").strip()
    password = input("Hasło: ").strip()

    verbose = input("Wyświetlić pełną treść każdej wiadomości? [t/N]: ").strip().lower() == "t"

    client = POP3Client(POP3_HOST, POP3_PORT)
    try:
        check_ok(client.connect(), "connect")
        check_ok(client.user(user), "USER")
        check_ok(client.passwd(password), "PASS")

        messages = client.list_messages()

        if not messages:
            print("Skrzynka jest pusta.")
            client.quit()
            return

        print(f"Wiadomości: {len(messages)}")

        for num, size in messages:
            body = client.retr(num)
            headers = parse_headers(body)

            print(f"Wiadomość #{num} ({size} B)")
            print(f"Od: {headers.get('From', '?')}")
            print(f"Do: {headers.get('To', '?')}")
            print(f"Temat: {headers.get('Subject', '?')}")
            print(f"Data: {headers.get('Date', '?')}")

            if verbose:
                in_body = False
                for line in body:
                    if not in_body:
                        if line == "":
                            in_body = True
                    else:
                        print(line)

        print(f"Razem: {len(messages)}")

        client.quit()
    finally:
        client.close()


if __name__ == "__main__":
    main()