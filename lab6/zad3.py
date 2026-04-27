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


def send_spoofed_email(real_sender, password, spoofed_from, recipient, subject, body):
    """
    real_sender  – prawdziwe konto SMTP (uwierzytelnienie + envelope MAIL FROM)
    spoofed_from – sfałszowany adres w nagłówku From:
    """
    print(f"\nŁączenie z {SMTP_HOST}:{SMTP_PORT}...\n")
    print(f"[!] Envelope MAIL FROM : {real_sender}")
    print(f"[!] Nagłówek From:       {spoofed_from}  ← PODMIENIONY\n")

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

        send(sock, base64.b64encode(real_sender.encode()).decode())
        recv(sock)

        send(sock, base64.b64encode(password.encode()).decode())
        recv(sock)

        # Envelope MAIL FROM = prawdziwy nadawca (wymóg serwera)
        send(sock, f"MAIL FROM:<{real_sender}>")
        recv(sock)

        send(sock, f"RCPT TO:<{recipient}>")
        recv(sock)

        send(sock, "DATA")
        recv(sock)

        # Nagłówek From: = sfałszowany adres
        message = (
            f"From: {spoofed_from}\r\n"          # ← podmieniony From
            f"To: {recipient}\r\n"
            f"Subject: {subject}\r\n"
            f"X-Originating-Email: {real_sender}\r\n"  # informacyjny nagłówek
            f"\r\n"
            f"{body}\r\n"
            f".\r\n"
        )
        print(">> [treść wiadomości (spoofed From) + .]")
        sock.sendall(message.encode())
        recv(sock)

        send(sock, "QUIT")
        recv(sock)

    print("\nWiadomość wysłana (From podmieniony w nagłówkach).")


if __name__ == "__main__":
    print("=== Zadanie 3: E-mail ze sfałszowanym nadawcą (spoofing) ===")
    print("UWAGA: Tylko do celów edukacyjnych!\n")

    real_sender  = input("Twój prawdziwy adres (login@interia.pl): ").strip()
    password     = getpass.getpass("Hasło: ")
    spoofed_from = input("Sfałszowany adres From (np. ktos@example.com): ").strip()
    recipient    = input("Adres odbiorcy: ").strip()
    subject      = input("Temat: ").strip()
    body         = input("Treść: ").strip()

    send_spoofed_email(real_sender, password, spoofed_from, recipient, subject, body)