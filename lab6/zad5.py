import socket
import base64
import ssl
import getpass
import os
import uuid

SMTP_HOST = "poczta.interia.pl"
SMTP_PORT = 587


IMAGE_MIME_TYPES = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".bmp":  "image/bmp",
    ".webp": "image/webp",
}


def get_image_mime_type(path):
    ext = os.path.splitext(path)[1].lower()
    return IMAGE_MIME_TYPES.get(ext, "application/octet-stream")


def recv(sock):
    data = b""
    while True:
        chunk = sock.recv(4096)
        data += chunk
        if b"\r\n" in data:
            break
    response = data.decode()
    print(f"<< {response.strip()}")
    return response


def send(sock, cmd):
    print(f">> {cmd.strip()}")
    sock.sendall((cmd + "\r\n").encode())


def build_mime_with_image(sender, recipient, subject, body, image_path):
    boundary = f"----=_Part_{uuid.uuid4().hex}"
    filename  = os.path.basename(image_path)
    mime_type = get_image_mime_type(image_path)

    with open(image_path, "rb") as f:
        image_data = f.read()
    encoded_image = base64.b64encode(image_data).decode()
    encoded_lines = "\r\n".join(
        encoded_image[i:i+76] for i in range(0, len(encoded_image), 76)
    )

    print("[Załącznik]")

    mime = (
        f"From: {sender}\r\n"
        f"To: {recipient}\r\n"
        f"Subject: {subject}\r\n"
        f"MIME-Version: 1.0\r\n"
        f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\r\n"
        f"\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Transfer-Encoding: 8bit\r\n"
        f"\r\n"
        f"{body}\r\n"
        f"\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: {mime_type}; name=\"{filename}\"\r\n"
        f"Content-Transfer-Encoding: base64\r\n"
        f"Content-Disposition: attachment; filename=\"{filename}\"\r\n"
        f"\r\n"
        f"{encoded_lines}\r\n"
        f"\r\n"
        f"--{boundary}--\r\n"
    )
    return mime


def send_email_with_image(sender, password, recipient, subject, body, image_path):
    print("Łączenie...")

    with socket.create_connection((SMTP_HOST, SMTP_PORT)) as raw_sock:
        recv(raw_sock)

        send(raw_sock, "EHLO localhost")
        recv(raw_sock)

        send(raw_sock, "STARTTLS")
        recv(raw_sock)

        context = ssl.create_default_context()
        sock = context.wrap_socket(raw_sock, server_hostname=SMTP_HOST)
        print("TLS")

        send(sock, "EHLO localhost")
        recv(sock)

        send(sock, "AUTH LOGIN")
        recv(sock)

        send(sock, base64.b64encode(sender.encode()).decode())
        recv(sock)

        send(sock, base64.b64encode(password.encode()).decode())
        recv(sock)

        send(sock, f"MAIL FROM:<{sender}>")
        recv(sock)

        send(sock, f"RCPT TO:<{recipient}>")
        recv(sock)

        send(sock, "DATA")
        recv(sock)

        mime_message = build_mime_with_image(sender, recipient, subject, body, image_path)
        payload = mime_message + ".\r\n"
        print(">> [DATA]")
        sock.sendall(payload.encode())
        recv(sock)

        send(sock, "QUIT")
        recv(sock)

    print("Wysłano.")


if __name__ == "__main__":
    sender     = input("Od: ").strip()
    password   = getpass.getpass("Hasło: ")
    recipient  = input("Do: ").strip()
    subject    = input("Temat: ").strip()
    body       = input("Treść: ").strip()
    image_path = input("Plik: ").strip()

    if not os.path.isfile(image_path):
        print("Błąd: brak pliku.")
        exit(1)

    send_email_with_image(sender, password, recipient, subject, body, image_path)