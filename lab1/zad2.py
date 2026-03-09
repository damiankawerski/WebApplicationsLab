from utils import read_from_console, write_to_binary_file

def zad2():
    source_filename = input("Podaj nazwę pliku źródłowego: ")
    target_filename = 'lab1zad2.png'
    write_to_binary_file(target_filename, source_filename)