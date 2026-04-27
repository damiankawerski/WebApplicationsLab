import socket
import datetime
import sys

HOST         = "127.0.0.1"
DEFAULT_PORT = 1100

FAKE_MESSAGES = [
    {
        "num": 1,
        "headers": {
            "From": "alice@example.com",
            "To":   "user@pop3test.local",
            "Subject": "Test 1 – zwykła wiadomość",
            "Date": "Mon, 01 Jan 2024 10:00:00 +0100",
        },
        "body": "Cześć!\r\nTo jest pierwsza testowa wiadomość.\r\nPozdrawiam,\r\nAlice",
    },
    {
        "num": 2,
        "headers": {
            "From": "bob@example.com",
            "To":   "user@pop3test.local",
            "Subject": "Test 2 – dłuższa wiadomość",
            "Date": "Tue, 02 Jan 2024 11:00:00 +0100",
        },
        "body": (
            "Witaj!\r\n\r\n"
            "To jest druga testowa wiadomość, nieco dłuższa.\r\n"
            "Zawiera kilka linii tekstu.\r\n\r\n"
            "Linia 1: Lorem ipsum dolor sit amet.\r\n"
            "Linia 2: Consectetur adipiscing elit.\r\n"
            "Linia 3: Sed do eiusmod tempor incididunt.\r\n\r\n"
            "Z poważaniem,\r\nBob"
        ),
    },
    {
        "num": 3,
        "headers": {
            "From": "carol@example.com",
            "To":   "user@pop3test.local",
            "Subject": "Test 3 – wiadomość z MIME",
            "Date": "Wed, 03 Jan 2024 12:00:00 +0100",
            "MIME-Version": "1.0",
            "Content-Type": 'multipart/mixed; boundary="testboundary123"',
        },
        "body": (
            "--testboundary123\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n\r\n"
            "Treść wiadomości z załącznikiem.\r\n\r\n"
            "--testboundary123\r\n"
            "Content-Type: text/plain; name=\"notatka.txt\"\r\n"
            "Content-Transfer-Encoding: base64\r\n"
            "Content-Disposition: attachment; filename=\"notatka.txt\"\r\n\r\n"
            "VGVzdG93eSBwbGlrIHRla3N0b3d5LgpUbyBqZXN0IHphxYLEhWN6bmlrLg==\r\n\r\n"
            "--testboundary123--"
        ),
    },
]

def _build_raw(msg):
    header_lines = "\r\n".join(f"{k}: {v}" for k, v in msg["headers"].items())
    return f"{header_lines}\r\n\r\n{msg['body']}"

for m in FAKE_MESSAGES:
    m["raw"]  = _build_raw(m)
    m["size"] = len(m["raw"].encode())
    m["deleted"] = False

class C:
    RESET  = "\033[0m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"

def ts():
    return datetime.datetime.now().strftime("%H:%M:%S")

def log_s(msg):
    pass

def log_c(addr, msg):
    pass

class POP3Session:

    VALID_USER = "user@pop3test.local"
    VALID_PASS = "test123"

    def __init__(self, conn, addr):
        self.conn  = conn
        self.addr  = addr
        self.state = "AUTHORIZATION"
        self.user  = None
        self.messages = [dict(m) for m in FAKE_MESSAGES]
        for m in self.messages:
            m["deleted"] = False

    def send(self, msg):
        log_s(f"→ {msg}")
        self.conn.sendall((msg + "\r\n").encode())

    def recv_line(self):
        buf = b""
        while not buf.endswith(b"\r\n"):
            chunk = self.conn.recv(1)
            if not chunk:
                raise ConnectionError("Klient rozłączył się")
            buf += chunk
        line = buf.decode(errors="replace").strip()
        log_c(self.addr, line)
        return line

    def active_messages(self):
        return [m for m in self.messages if not m["deleted"]]

    def get_message(self, num):
        for m in self.messages:
            if m["num"] == num and not m["deleted"]:
                return m
        return None

    def handle(self):
        self.send("+OK POP3 FakeServer ready <fake@pop3server>")

        while True:
            try:
                line = self.recv_line()
            except ConnectionError:
                log_s(f"Klient {self.addr} rozłączył się")
                break

            parts = line.split(None, 1)
            cmd   = parts[0].upper() if parts else ""
            args  = parts[1] if len(parts) > 1 else ""

            if self.state == "AUTHORIZATION":

                if cmd == "USER":
                    self.user = args.strip()
                    self.send(f"+OK {self.user}, tell me your password")

                elif cmd == "PASS":
                    self.state = "TRANSACTION"
                    active = self.active_messages()
                    total  = sum(m["size"] for m in active)
                    self.send(f"+OK Welcome! You have {len(active)} messages ({total} octets)")

                elif cmd == "QUIT":
                    self.send("+OK Farewell")
                    break

                elif cmd == "CAPA":
                    self.send("+OK Capability list follows\r\nUSER\r\nTOP\r\nUIDL\r\n.")

                else:
                    log_s(f"Nieznana komenda w AUTHORIZATION: '{cmd}'")
                    self.send(f"-ERR Not implemented: {cmd}")

            elif self.state == "TRANSACTION":

                if cmd == "STAT":
                    active = self.active_messages()
                    total  = sum(m["size"] for m in active)
                    self.send(f"+OK {len(active)} {total}")

                elif cmd == "LIST":
                    if args.strip():
                        try:
                            num = int(args.strip())
                            msg = self.get_message(num)
                            if msg:
                                self.send(f"+OK {msg['num']} {msg['size']}")
                            else:
                                self.send(f"-ERR No such message {num}")
                        except ValueError:
                            self.send("-ERR Invalid argument")
                    else:
                        active = self.active_messages()
                        total  = sum(m["size"] for m in active)
                        self.send(f"+OK {len(active)} messages ({total} octets)")
                        for m in active:
                            self.conn.sendall(f"{m['num']} {m['size']}\r\n".encode())
                        self.conn.sendall(b".\r\n")

                elif cmd == "RETR":
                    try:
                        num = int(args.strip())
                        msg = self.get_message(num)
                        if msg:
                            self.send(f"+OK {msg['size']} octets")
                            for raw_line in msg["raw"].split("\r\n"):
                                if raw_line.startswith("."):
                                    raw_line = "." + raw_line
                                self.conn.sendall((raw_line + "\r\n").encode())
                            self.conn.sendall(b".\r\n")
                        else:
                            self.send(f"-ERR No such message {num}")
                    except ValueError:
                        self.send("-ERR Invalid argument")

                elif cmd == "DELE":
                    try:
                        num = int(args.strip())
                        msg = self.get_message(num)
                        if msg:
                            msg["deleted"] = True
                            self.send(f"+OK Message {num} deleted")
                        else:
                            self.send(f"-ERR No such message {num}")
                    except ValueError:
                        self.send("-ERR Invalid argument")

                elif cmd == "RSET":
                    for m in self.messages:
                        m["deleted"] = False
                    active = self.active_messages()
                    self.send(f"+OK Maildrop has {len(active)} messages")

                elif cmd == "NOOP":
                    self.send("+OK")

                elif cmd == "STAT":
                    active = self.active_messages()
                    total  = sum(m["size"] for m in active)
                    self.send(f"+OK {len(active)} {total}")

                elif cmd == "TOP":
                    try:
                        num_lines = args.split()
                        num   = int(num_lines[0])
                        lines = int(num_lines[1]) if len(num_lines) > 1 else 0
                        msg   = self.get_message(num)
                        if msg:
                            self.send(f"+OK Top of message follows")
                            raw_lines = msg["raw"].split("\r\n")
                            in_body = False
                            body_count = 0
                            for raw_line in raw_lines:
                                if not in_body:
                                    self.conn.sendall((raw_line + "\r\n").encode())
                                    if raw_line == "":
                                        in_body = True
                                else:
                                    if body_count < lines:
                                        self.conn.sendall((raw_line + "\r\n").encode())
                                        body_count += 1
                                    else:
                                        break
                            self.conn.sendall(b".\r\n")
                        else:
                            self.send(f"-ERR No such message {num}")
                    except (ValueError, IndexError):
                        self.send("-ERR Syntax: TOP <msg> <lines>")

                elif cmd == "UIDL":
                    if args.strip():
                        try:
                            num = int(args.strip())
                            msg = self.get_message(num)
                            if msg:
                                self.send(f"+OK {msg['num']} fakeid{msg['num']:08d}")
                            else:
                                self.send(f"-ERR No such message {num}")
                        except ValueError:
                            self.send("-ERR Invalid argument")
                    else:
                        active = self.active_messages()
                        self.send(f"+OK Unique-ID listing follows")
                        for m in active:
                            self.conn.sendall(f"{m['num']} fakeid{m['num']:08d}\r\n".encode())
                        self.conn.sendall(b".\r\n")

                elif cmd == "CAPA":
                    self.send("+OK Capability list follows\r\nTOP\r\nUIDL\r\nRESP-CODES\r\n.")

                elif cmd == "QUIT":
                    deleted = [m for m in self.messages if m["deleted"]]
                    self.state = "UPDATE"
                    self.send(f"+OK POP3 server signing off ({len(deleted)} messages deleted)")
                    break

                else:
                    log_s(f"Nieznana komenda w TRANSACTION: '{cmd}'")
                    self.send(f"-ERR Command not implemented: {cmd}")

            else:
                self.send("-ERR Server in unknown state")
                break

        self.conn.close()

def run_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, port))
        srv.listen(5)

        print(f"POP3 server: {HOST}:{port}")

        while True:
            try:
                conn, addr = srv.accept()
                log_s(f"Połączenie od {addr[0]}:{addr[1]}")
                session = POP3Session(conn, addr)
                session.handle()
                log_s(f"Sesja z {addr[0]}:{addr[1]} zakończona\n")
            except KeyboardInterrupt:
                print("Serwer zatrzymany")
                break


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    run_server(port)