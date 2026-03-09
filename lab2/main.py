from utils import *


def main():

    # Zadanie 1
    print("Aktualna data i czas:")
    print(get_time_and_date())

    # Zadanie 2
    # message = "Hello, Server!"
    # response = send_message_to_server_tcp(message)
    # print(f"Odpowiedź od serwera: {response}")

    # Zadanie 3 
    # while (1):
    #     message = input("Wpisz wiadomość do wysłania do serwera (lub 'exit' aby zakończyć): ")
    #     if message.lower() == "exit":
    #         print("Zakończenie programu.")
    #         break
    #     response = send_message_to_server_tcp(message)
    #     print(f"Odpowiedź od serwera: {response}")

    # Zadanie 4
    # message = "Hello, Server!"
    # response = send_message_to_server_udp(message)
    # print(f"Odpowiedź od serwera: {response}")

    # Zadanie 5
    # while (1):
    #     message = input("Wpisz wiadomość do wysłania do serwera (lub 'exit' aby zakończyć): ")
    #     if message.lower() == "exit":
    #         print("Zakończenie programu.")
    #         break
    #     response = send_message_to_server_udp(message)
    #     print(f"Odpowiedź od serwera: {response}")

    # Zadanie 6
    # while True:
    #     user_input = get_user_input()
    #     if user_input is None:
    #         print("Zakończenie programu.")
    #         break
    #     number1, number2, operator = user_input
    #     result = send_message_to_server_udp_calc(number1, number2, operator)
    #     print(f"Wynik operacji {number1} {operator} {number2} = {result}")

    


if __name__ == "__main__":
    main()