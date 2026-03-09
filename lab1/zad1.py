from utils import read_from_console, write_to_file

def zad1():
    content = read_from_console()
    filename = 'lab1zad1.txt'
    write_to_file(filename, content)