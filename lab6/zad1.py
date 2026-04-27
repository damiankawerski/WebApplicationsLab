import socket
import base64
import getpass

SMTP_HOST = "poczta.interia.pl"
SMTP_PORT = 587


def recv(sock):
    data = b""
    while True:
        chunk = sock.recv(4096)
        data += chunk
        if data.endswith(b"\r\n") or b"\r\n" in data:
            break
    response = data.decode()
    print(f"<< {response.strip()}")
    return response


def send(sock, cmd):
    print(f">> {cmd.strip()}")
    sock.sendall((cmd + "\r\n").encode())


def send_email(sender, password, recipient, subject, body):
    print("Łączenie...")

    with socket.create_connection((SMTP_HOST, SMTP_PORT)) as sock:

        recv(sock)


        send(sock, "EHLO localhost")
        recv(sock)


        send(sock, "STARTTLS")
        recv(sock)

        import ssl
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=SMTP_HOST)
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

        message = (
            f"From: {sender}\r\n"
            f"To: {recipient}\r\n"
            f"Subject: {subject}\r\n"
            f"\r\n"
            f"{body}\r\n"
            f".\r\n"
        )
        print(">> [DATA]")
        sock.sendall(message.encode())
        recv(sock)


        send(sock, "QUIT")
        recv(sock)

    print("Wysłano.")


if __name__ == "__main__":
    sender    = input("Od: ").strip()
    password  = getpass.getpass("Hasło: ")
    recipient = input("Do: ").strip()
    subject   = input("Temat: ").strip()
    body      = input("Treść: ").strip()

    send_email(sender, password, recipient, subject, body)