import socket
import base64
import ssl
import getpass

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


def send_email_multi(sender, password, recipients, subject, body):
    """
    recipients: lista adresów e-mail (list[str])
    """
    print(f"\nŁączenie z {SMTP_HOST}:{SMTP_PORT}...\n")

    with socket.create_connection((SMTP_HOST, SMTP_PORT)) as raw_sock:
        recv(raw_sock)

        send(raw_sock, "EHLO localhost")
        recv(raw_sock)

        send(raw_sock, "STARTTLS")
        recv(raw_sock)

        context = ssl.create_default_context()
        sock = context.wrap_socket(raw_sock, server_hostname=SMTP_HOST)
        print("[TLS aktywne]\n")

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

        # Każdy odbiorca osobnym RCPT TO
        for rcpt in recipients:
            send(sock, f"RCPT TO:<{rcpt.strip()}>")
            recv(sock)

        send(sock, "DATA")
        recv(sock)

        to_header = ", ".join(recipients)
        message = (
            f"From: {sender}\r\n"
            f"To: {to_header}\r\n"
            f"Subject: {subject}\r\n"
            f"\r\n"
            f"{body}\r\n"
            f".\r\n"
        )
        print(">> [treść wiadomości + .]")
        sock.sendall(message.encode())
        recv(sock)

        send(sock, "QUIT")
        recv(sock)

    print("\nWiadomość wysłana do wszystkich odbiorców!")


if __name__ == "__main__":
    print("=== Zadanie 2: Wysyłanie e-mail do wielu odbiorców przez ESMTP ===\n")
    sender    = input("Adres nadawcy (login@interia.pl): ").strip()
    password  = getpass.getpass("Hasło: ")
    rcpt_raw  = input("Adresy odbiorców (oddzielone przecinkami): ").strip()
    recipients = [r.strip() for r in rcpt_raw.split(",") if r.strip()]
    subject   = input("Temat: ").strip()
    body      = input("Treść: ").strip()

    print(f"\nOdbiorcy: {recipients}")
    send_email_multi(sender, password, recipients, subject, body)