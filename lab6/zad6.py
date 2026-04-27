import socket
import base64
import ssl
import getpass

SMTP_HOST = "poczta.interia.pl"
SMTP_PORT = 587


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


def send_cmd(sock, cmd, show=True):
    if show:
        print(f">> {cmd.strip()}")
    sock.sendall((cmd + "\r\n").encode())


def check(code, expected, msg=""):
    if code != expected:
        raise RuntimeError(f"Błąd SMTP (oczekiwano {expected}, dostano {code}): {msg}")


def smtp_client():
    sender    = input("Od: ").strip()
    password  = getpass.getpass("Hasło: ")
    rcpt_raw  = input("Do (,): ").strip()
    recipients = [r.strip() for r in rcpt_raw.split(",") if r.strip()]
    subject   = input("Temat: ").strip()
    print("Treść:")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    body = "\r\n".join(lines)

    print("Łączenie...")

    with socket.create_connection((SMTP_HOST, SMTP_PORT)) as raw_sock:
        code, _ = recv_response(raw_sock)
        check(code, 220, "Brak powitania serwera")

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

        send_cmd(sock, base64.b64encode(sender.encode()).decode(), show=False)
        print(">> [login base64]")
        code, _ = recv_response(sock)
        check(code, 334)

        send_cmd(sock, base64.b64encode(password.encode()).decode(), show=False)
        print(">> [hasło base64]")
        code, _ = recv_response(sock)
        check(code, 235, "Błąd uwierzytelnienia – sprawdź login i hasło")

        send_cmd(sock, f"MAIL FROM:<{sender}>")
        code, _ = recv_response(sock)
        check(code, 250)

        for rcpt in recipients:
            send_cmd(sock, f"RCPT TO:<{rcpt}>")
            code, _ = recv_response(sock)
            check(code, 250, f"Odrzucono odbiorcę: {rcpt}")

        send_cmd(sock, "DATA")
        code, _ = recv_response(sock)
        check(code, 354)

        to_header = ", ".join(recipients)
        message = (
            f"From: {sender}\r\n"
            f"To: {to_header}\r\n"
            f"Subject: {subject}\r\n"
            f"MIME-Version: 1.0\r\n"
            f"Content-Type: text/plain; charset=utf-8\r\n"
            f"\r\n"
            f"{body}\r\n"
            f".\r\n"
        )
        print(">> [DATA]")
        sock.sendall(message.encode())
        code, _ = recv_response(sock)
        check(code, 250, "Serwer nie przyjął wiadomości")

        send_cmd(sock, "QUIT")
        recv_response(sock)

    print("Wysłano.")


if __name__ == "__main__":
    smtp_client()