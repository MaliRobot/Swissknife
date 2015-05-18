from parse import fetch 
from window import Window
from sys import argv
from os import getcwd, listdir
import Tkinter

if __name__ == "__main__":
    print argv
    if len(argv) > 1:
        if argv[1] == 'gui':
            gui = Window()
    else:
        path = getcwd()
        if path == '':
            fullpath = getcwd()
        if listdir(path) == []:
            print "no files to work with!"
        else:
            fetch(path)