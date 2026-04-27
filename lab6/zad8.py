import socket
import base64
import ssl
import getpass
import os
import uuid

SMTP_HOST = "poczta.interia.pl"
SMTP_PORT = 587

IMAGE_MIME_MAP = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".bmp":  "image/bmp",
    ".webp": "image/webp",
    ".tiff": "image/tiff",
    ".svg":  "image/svg+xml",
}


def get_mime_type(path):
    ext = os.path.splitext(path)[1].lower()
    return IMAGE_MIME_MAP.get(ext, "application/octet-stream")




def recv_response(sock):
    data = b""
    while True:
        chunk = sock.recv(4096)
        data += chunk
        lines = data.decode(errors="replace").splitlines()
        if lines:
            last = lines[-1]
            if len(last) >= 4 and last[3] == " ":
                break
    response = data.decode(errors="replace")
    code = int(response[:3])
    print(f"<< {response.strip()}")
    return code, response


def send_cmd(sock, cmd, display=None):
    shown = display if display is not None else cmd.strip()
    print(f">> {shown}")
    sock.sendall((cmd + "\r\n").encode())


def check(code, expected, context=""):
    if code != expected:
        raise RuntimeError(f"SMTP {code} (oczekiwano {expected}) {context}")




def encode_base64_chunked(data: bytes, width=76) -> str:
    encoded = base64.b64encode(data).decode("ascii")
    return "\r\n".join(encoded[i:i+width] for i in range(0, len(encoded), width))


def build_multipart_image(sender, recipients_str, subject, body, image_path):
    boundary  = f"----=_MimeBoundary_{uuid.uuid4().hex}"
    filename  = os.path.basename(image_path)
    mime_type = get_mime_type(image_path)

    with open(image_path, "rb") as f:
        raw = f.read()

    encoded = encode_base64_chunked(raw)
    print("[Załącznik]")

    headers = (
        f"From: {sender}\r\n"
        f"To: {recipients_str}\r\n"
        f"Subject: {subject}\r\n"
        f"MIME-Version: 1.0\r\n"
        f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\r\n"
    )

    text_part = (
        f"\r\n--{boundary}\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Transfer-Encoding: 8bit\r\n"
        f"\r\n"
        f"{body}\r\n"
    )

    image_part = (
        f"\r\n--{boundary}\r\n"
        f"Content-Type: {mime_type}; name=\"{filename}\"\r\n"
        f"Content-Transfer-Encoding: base64\r\n"
        f"Content-Disposition: attachment; filename=\"{filename}\"\r\n"
        f"\r\n"
        f"{encoded}\r\n"
    )

    closing = f"\r\n--{boundary}--\r\n"

    return headers + text_part + image_part + closing




def smtp_client_with_image():
    sender     = input("Od: ").strip()
    password   = getpass.getpass("Hasło: ")
    rcpt_raw   = input("Do (,): ").strip()
    recipients = [r.strip() for r in rcpt_raw.split(",") if r.strip()]
    subject    = input("Temat: ").strip()
    print("Treść:")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    body       = "\r\n".join(lines)
    image_path = input("Plik: ").strip()

    if not os.path.isfile(image_path):
        print("Błąd: brak pliku.")
        return

    print("Łączenie...")

    with socket.create_connection((SMTP_HOST, SMTP_PORT)) as raw_sock:
        code, _ = recv_response(raw_sock)
        check(code, 220)

        send_cmd(raw_sock, "EHLO localhost")
        code, _ = recv_response(raw_sock)
        check(code, 250)

        send_cmd(raw_sock, "STARTTLS")
        code, _ = recv_response(raw_sock)
        check(code, 220)

        context = ssl.create_default_context()
        sock = context.wrap_socket(raw_sock, server_hostname=SMTP_HOST)
        print("TLS")

        send_cmd(sock, "EHLO localhost")
        code, _ = recv_response(sock)
        check(code, 250)

        send_cmd(sock, "AUTH LOGIN")
        code, _ = recv_response(sock)
        check(code, 334)

        send_cmd(sock, base64.b64encode(sender.encode()).decode(), display="[login base64]")
        code, _ = recv_response(sock)
        check(code, 334)

        send_cmd(sock, base64.b64encode(password.encode()).decode(), display="[hasło base64]")
        code, _ = recv_response(sock)
        check(code, 235, "Błąd uwierzytelnienia")

        send_cmd(sock, f"MAIL FROM:<{sender}>")
        code, _ = recv_response(sock)
        check(code, 250)

        for rcpt in recipients:
            send_cmd(sock, f"RCPT TO:<{rcpt}>")
            code, _ = recv_response(sock)
            check(code, 250, f"Odrzucono: {rcpt}")

        send_cmd(sock, "DATA")
        code, _ = recv_response(sock)
        check(code, 354)

        recipients_str = ", ".join(recipients)
        mime_body = build_multipart_image(sender, recipients_str, subject, body, image_path)
        payload = mime_body + ".\r\n"

        print(">> [DATA]")
        sock.sendall(payload.encode())
        code, _ = recv_response(sock)
        check(code, 250)

        send_cmd(sock, "QUIT")
        recv_response(sock)

    print("Wysłano.")


if __name__ == "__main__":
    smtp_client_with_image()