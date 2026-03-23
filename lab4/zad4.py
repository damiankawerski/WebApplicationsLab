import socket

HOST = "127.0.0.1"
PORT = 9004

def calculate(message: str) -> str:
    parts = message.strip().split()
    if len(parts) != 3:
        return "BŁĄD: Oczekiwano formatu: 'liczba operator liczba'"

    left_str, operator, right_str = parts

    try:
        left = float(left_str)
        right = float(right_str)
    except ValueError:
        return "BŁĄD: Nieprawidłowe liczby"

    if operator == "+":
        result = left + right
    elif operator == "-":
        result = left - right
    elif operator == "*":
        result = left * right
    elif operator == "/":
        if right == 0:
            return "BŁĄD: Dzielenie przez zero"
        result = left / right
    else:
        return f"BŁĄD: Nieznany operator '{operator}'. Dozwolone: + - * /"

    if result == int(result):
        return str(int(result))
    return str(result)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
        server_sock.bind((HOST, PORT))
        print(f"[*] Serwer kalkulator (UDP) nasłuchuje na {HOST}:{PORT}")
        print(f"[*] Format: 'liczba operator liczba' (np. '10 + 5')")

        while True:
            data, addr = server_sock.recvfrom(1024)
            message = data.decode(errors='replace')
            print(f"[>] Odebrano od {addr}: {message}")

            response = calculate(message)
            server_sock.sendto(response.encode(), addr)
            print(f"[<] Wysłano do {addr}: {response}")

if __name__ == "__main__":
    main()