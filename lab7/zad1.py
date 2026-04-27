import socket
import ssl

POP3_HOST = "poczta.interia.pl"
POP3_PORT = 995


def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        buf += chunk
    return buf.decode(errors="replace").strip()


def send_cmd(sock, cmd):
    sock.sendall((cmd + "\r\n").encode())


def check_ok(line, context=""):
    if not line.startswith("+OK"):
        raise RuntimeError(f"Błąd serwera {context}: {line}")


def count_messages(user, password):
    ssl_context = ssl.create_default_context()

    with socket.create_connection((POP3_HOST, POP3_PORT)) as raw_sock:
        sock = ssl_context.wrap_socket(raw_sock, server_hostname=POP3_HOST)

        greeting = recv_line(sock)
        check_ok(greeting, "powitanie")
        send_cmd(sock, f"USER {user}")
        check_ok(recv_line(sock), "USER")

        send_cmd(sock, f"PASS {password}")
        check_ok(recv_line(sock), "PASS")

        send_cmd(sock, "STAT")
        stat = recv_line(sock)
        check_ok(stat, "STAT")

        parts = stat.split()
        count = parts[1]
        total = parts[2]

        print(f"Liczba wiadomości w skrzynce: {count}")
        print(f"Łączny rozmiar: {total} B")

        send_cmd(sock, "QUIT")
        recv_line(sock)


if __name__ == "__main__":
    user     = input("Login: ").strip()
    password = input("Hasło: ").strip()
    count_messages(user, password)