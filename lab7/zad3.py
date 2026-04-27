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


def list_sizes(user, password):
    ssl_context = ssl.create_default_context()

    with socket.create_connection((POP3_HOST, POP3_PORT)) as raw_sock:
        sock = ssl_context.wrap_socket(raw_sock, server_hostname=POP3_HOST)
        check_ok(recv_line(sock), "powitanie")

        send_cmd(sock, f"USER {user}")
        check_ok(recv_line(sock), "USER")

        send_cmd(sock, f"PASS {password}")
        check_ok(recv_line(sock), "PASS")

        send_cmd(sock, "LIST")
        header = recv_line(sock)
        check_ok(header, "LIST")

        entries = recv_multiline(sock)

        print(f"{'Nr':>5}  {'Rozmiar (B)':>12}")

        messages = []
        for entry in entries:
            parts = entry.split()
            if len(parts) == 2:
                num, size = int(parts[0]), int(parts[1])
                messages.append((num, size))
                print(f"{num:>5}  {size:>12}")

        if messages:
            sizes = [s for _, s in messages]
            print(f"{'Min':>5}  {min(sizes):>12}")
            print(f"{'Max':>5}  {max(sizes):>12}")
            print(f"{'Suma':>5}  {sum(sizes):>12}")

        send_cmd(sock, "QUIT")
        recv_line(sock)


if __name__ == "__main__":
    user     = input("Login: ").strip()
    password = input("Hasło: ").strip()
    list_sizes(user, password)