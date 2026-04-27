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


def recv_multiline(sock):
    lines = []
    while True:
        line = recv_line(sock)
        if line == ".":
            break
        lines.append(line)
    return lines


def send_cmd(sock, cmd):
    sock.sendall((cmd + "\r\n").encode())


def check_ok(line, context=""):
    if not line.startswith("+OK"):
        raise RuntimeError(f"Błąd serwera {context}: {line}")


def delete_smallest(user, password):
    ssl_context = ssl.create_default_context()

    with socket.create_connection((POP3_HOST, POP3_PORT)) as raw_sock:
        sock = ssl_context.wrap_socket(raw_sock, server_hostname=POP3_HOST)
        check_ok(recv_line(sock), "powitanie")

        send_cmd(sock, f"USER {user}")
        check_ok(recv_line(sock), "USER")

        send_cmd(sock, f"PASS {password}")
        check_ok(recv_line(sock), "PASS")

        send_cmd(sock, "LIST")
        check_ok(recv_line(sock), "LIST")
        entries = recv_multiline(sock)

        messages = []
        for entry in entries:
            parts = entry.split()
            if len(parts) == 2:
                messages.append((int(parts[0]), int(parts[1])))

        if not messages:
            print("Skrzynka jest pusta – brak wiadomości do usunięcia.")
            send_cmd(sock, "QUIT")
            recv_line(sock)
            return

        smallest_num, smallest_size = min(messages, key=lambda x: x[1])
        print(f"Najmniejsza wiadomość: nr {smallest_num} ({smallest_size} B)")

        confirm = input(f"Czy usunąć wiadomość nr {smallest_num}? [t/N]: ").strip().lower()
        if confirm != "t":
            print("Anulowano")
            send_cmd(sock, "QUIT")
            recv_line(sock)
            return

        send_cmd(sock, f"DELE {smallest_num}")
        check_ok(recv_line(sock), "DELE")

        send_cmd(sock, "QUIT")
        check_ok(recv_line(sock), "QUIT")

        print(f"Usunięto wiadomość nr {smallest_num} ({smallest_size} B)")


if __name__ == "__main__":
    user     = input("Login: ").strip()
    password = input("Hasło: ").strip()
    delete_smallest(user, password)