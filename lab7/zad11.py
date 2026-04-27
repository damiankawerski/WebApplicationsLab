import socket
import ssl
import base64
import os
import re

POP3_HOST = "poczta.interia.pl"
POP3_PORT = 995
SAVE_DIR  = "."


def recv_line(sock):
    buf = b""
    while not buf.endswith(b"\r\n"):
        buf += sock.recv(1)
    return buf.decode(errors="replace").strip()


def send_cmd(sock, cmd, show=True):
    sock.sendall((cmd + "\r\n").encode())


def check_ok(line, context=""):
    if not line.startswith("+OK"):
        raise RuntimeError(f"Błąd POP3 [{context}]: {line}")


class POP3Client:
    def __init__(self, host, port):
        raw_sock = socket.create_connection((host, port))
        ssl_context = ssl.create_default_context()
        self.sock = ssl_context.wrap_socket(raw_sock, server_hostname=host)

    def _recv(self, quiet=False):
        line = recv_line(self.sock)
        return line

    def _send(self, cmd, show=True):
        send_cmd(self.sock, cmd, show)

    def connect(self):
        return self._recv()

    def user(self, u):
        self._send(f"USER {u}")
        return self._recv()

    def passwd(self, p):
        self._send(f"PASS {p}")
        return self._recv()

    def list_messages(self):
        self._send("LIST")
        header = self._recv()
        check_ok(header, "LIST")
        messages = []
        while True:
            line = self._recv(quiet=True)
            if line == ".":
                break
            parts = line.split()
            if len(parts) == 2:
                messages.append((int(parts[0]), int(parts[1])))
        return messages

    def retr(self, num):
        self._send(f"RETR {num}")
        header = self._recv()
        check_ok(header, f"RETR {num}")
        lines = []
        while True:
            line = self._recv(quiet=True)
            if line == ".":
                break
            if line.startswith(".."):
                line = line[1:]
            lines.append(line)
        return lines

    def quit(self):
        self._send("QUIT")
        return self._recv()

    def close(self):
        self.sock.close()


def find_image_attachments(raw_lines):
    text = "\r\n".join(raw_lines)

    boundary_match = re.search(
        r'Content-Type:\s*multipart/\w+;\s*boundary="?([^"\r\n]+)"?',
        text, re.IGNORECASE
    )
    if not boundary_match:
        return []

    boundary = boundary_match.group(1).strip()

    parts = text.split("--" + boundary)

    attachments = []

    for part in parts:
        if not part.strip() or part.strip() == "--":
            continue

        ct_match = re.search(r"Content-Type:\s*([^\r\n;]+)", part, re.IGNORECASE)
        if not ct_match:
            continue
        content_type = ct_match.group(1).strip().lower()

        if not content_type.startswith("image/"):
            continue

        cte_match = re.search(r"Content-Transfer-Encoding:\s*(\S+)", part, re.IGNORECASE)
        encoding = cte_match.group(1).strip().lower() if cte_match else "7bit"

        filename = None
        fn_match = re.search(
            r'(?:filename|name)="?([^"\r\n;]+)"?', part, re.IGNORECASE
        )
        if fn_match:
            filename = fn_match.group(1).strip()

        if not filename:
            ext = content_type.split("/")[1]
            filename = f"attachment.{ext}"

        body_match = re.search(r"\r?\n\r?\n([\s\S]+)", part)
        if not body_match:
            continue
        body_raw = body_match.group(1).strip()

        if encoding == "base64":
            try:
                image_bytes = base64.b64decode(body_raw.replace("\r\n", "").replace("\n", ""))
            except Exception:
                continue
        else:
            image_bytes = body_raw.encode(errors="replace")

        attachments.append({"filename": filename, "data": image_bytes, "type": content_type})

    return attachments


def main():
    user     = input("Login: ").strip()
    password = input("Hasło: ").strip()
    msg_num  = input("Numer wiadomości do sprawdzenia (Enter = przeszukaj wszystkie): ").strip()

    client = POP3Client(POP3_HOST, POP3_PORT)
    try:
        check_ok(client.connect(), "connect")
        check_ok(client.user(user), "USER")
        check_ok(client.passwd(password), "PASS")

        if msg_num.isdigit():
            to_check = [(int(msg_num), 0)]
        else:
            to_check = client.list_messages()

        found_any = False

        for num, size in to_check:
            raw = client.retr(num)
            attachments = find_image_attachments(raw)

            for att in attachments:
                found_any = True
                save_path = os.path.join(SAVE_DIR, att["filename"])
                with open(save_path, "wb") as f:
                    f.write(att["data"])
                print(f"Zapisano: {save_path}")

        if not found_any:
            print("Brak załączników obrazkowych")

        client.quit()
    finally:
        client.close()


if __name__ == "__main__":
    main()