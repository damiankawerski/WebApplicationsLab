import socket
import base64
import ssl
import getpass
import uuid

SMTP_HOST = "poczta.interia.pl"
SMTP_PORT = 587


# ---------- SMTP helpers ----------

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


# ---------- Budowanie wiadomości HTML ----------

def build_html_email(sender, recipients_str, subject, plain_body, html_body):
    """
    Tworzy wiadomość multipart/alternative:
      - text/plain  (fallback)
      - text/html   (sformatowana wersja HTML)
    """
    boundary = f"----=_AltBoundary_{uuid.uuid4().hex}"

    msg = (
        f"From: {sender}\r\n"
        f"To: {recipients_str}\r\n"
        f"Subject: {subject}\r\n"
        f"MIME-Version: 1.0\r\n"
        f"Content-Type: multipart/alternative; boundary=\"{boundary}\"\r\n"
        f"\r\n"

        # Część 1 – plain text (fallback)
        f"--{boundary}\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Transfer-Encoding: 8bit\r\n"
        f"\r\n"
        f"{plain_body}\r\n"
        f"\r\n"

        # Część 2 – HTML
        f"--{boundary}\r\n"
        f"Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Transfer-Encoding: 8bit\r\n"
        f"\r\n"
        f"{html_body}\r\n"
        f"\r\n"

        f"--{boundary}--\r\n"
    )
    return msg


def plain_to_html(plain: str) -> str:
    """
    Automatycznie konwertuje podstawowe znaczniki tekstowe na HTML:
      **tekst**   → <strong>
      *tekst*     → <em>
      __tekst__   → <u>
      ~~tekst~~   → <s>
      `tekst`     → <code>
    """
    import re
    html = plain
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         html)
    html = re.sub(r'__(.+?)__',     r'<u>\1</u>',           html)
    html = re.sub(r'~~(.+?)~~',     r'<s>\1</s>',           html)
    html = re.sub(r'`(.+?)`',       r'<code>\1</code>',     html)
    # Nowe linie → <br>
    html = html.replace("\r\n", "<br>\r\n").replace("\n", "<br>\n")
    return (
        "<!DOCTYPE html>\r\n"
        "<html><head><meta charset=\"utf-8\"></head>\r\n"
        "<body style=\"font-family: Arial, sans-serif; font-size: 14px;\">\r\n"
        f"{html}\r\n"
        "</body></html>"
    )


# ---------- Klient SMTP ----------

def smtp_html_client():
    print("=== Zadanie 9: Klient SMTP – wiadomość HTML ===\n")
    print("Składnia formatowania w treści:")
    print("  **pogrubienie**  *kursywa*  __podkreślenie__  ~~przekreślenie~~  `kod`\n")

    sender    = input("Adres nadawcy (login@interia.pl): ").strip()
    password  = getpass.getpass("Hasło: ")
    rcpt_raw  = input("Adresy odbiorców (oddzielone przecinkami): ").strip()
    recipients = [r.strip() for r in rcpt_raw.split(",") if r.strip()]
    subject   = input("Temat: ").strip()
    print("Treść (zakończ pustą linią, używaj znaczników formatowania):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    plain_body = "\r\n".join(lines)

    # Konwersja na HTML
    html_body = plain_to_html(plain_body)

    print("\n--- Podgląd HTML ---")
    print(html_body[:800])
    print("--- Koniec podglądu ---\n")

    print(f"Łączenie z {SMTP_HOST}:{SMTP_PORT}...\n")

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
        print("[TLS aktywne]\n")

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
        mime_msg = build_html_email(sender, recipients_str, subject, plain_body, html_body)
        payload  = mime_msg + ".\r\n"

        print(">> [MIME multipart/alternative (plain + HTML) + .]")
        sock.sendall(payload.encode("utf-8"))
        code, _ = recv_response(sock)
        check(code, 250)

        send_cmd(sock, "QUIT")
        recv_response(sock)

    print("\n✓ Wiadomość HTML wysłana!")


if __name__ == "__main__":
    smtp_html_client()