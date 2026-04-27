import socket
import base64
import ssl
import getpass
import os
import uuid

SMTP_HOST = "poczta.interia.pl"
SMTP_PORT = 587


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


def build_mime_with_text_attachment(sender, recipient, subject, body, attachment_path):
    boundary = f"----=_Part_{uuid.uuid4().hex}"
    filename = os.path.basename(attachment_path)

    with open(attachment_path, "rb") as f:
        file_data = f.read()
    encoded_file = base64.b64encode(file_data).decode()

    encoded_lines = "\r\n".join(
        encoded_file[i:i+76] for i in range(0, len(encoded_file), 76)
    )

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
        f"Content-Type: text/plain; charset=utf-8; name=\"{filename}\"\r\n"
        f"Content-Transfer-Encoding: base64\r\n"
        f"Content-Disposition: attachment; filename=\"{filename}\"\r\n"
        f"\r\n"
        f"{encoded_lines}\r\n"
        f"\r\n"
        f"--{boundary}--\r\n"
    )
    return mime


def send_email_with_text_attachment(sender, password, recipient, subject, body, attachment_path):
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

        mime_message = build_mime_with_text_attachment(
            sender, recipient, subject, body, attachment_path
        )
        payload = mime_message + ".\r\n"
        print(">> [DATA]")
        sock.sendall(payload.encode())
        recv(sock)

        send(sock, "QUIT")
        recv(sock)

    print("Wysłano.")


if __name__ == "__main__":
    sender          = input("Od: ").strip()
    password        = getpass.getpass("Hasło: ")
    recipient       = input("Do: ").strip()
    subject         = input("Temat: ").strip()
    body            = input("Treść: ").strip()
    attachment_path = input("Plik: ").strip()

    if not os.path.isfile(attachment_path):
        print("Błąd: brak pliku.")
        exit(1)

    send_email_with_text_attachment(sender, password, recipient, subject, body, attachment_path)