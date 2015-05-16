import sys, os
from parse import fetch 
from window import *

if __name__ == "__main__":

    #if len(sys.argv)==1:
    #    if sys.argv[1] == 'gui':
    gui = Window()
    #path = os.getcwd()
    #print fullpath, 'aaaa'
    #if fullpath == '':
    #    fullpath = os.getcwd()
    #print 'prosao'
    #filenames = next(os.walk(fullpath))[2]
    ##print filenames
    #if "extract.bat" in filenames and "repack.bat" in filenames and "reset.bat" in filenames:
    #    fullpath = fullpath  + "\\input"
    ##else:
    ##    fullpath = "F:\Games\Arma 2\Osku's tool\input"
    ##print os.listdir(fullpath + "\\input")
    #if os.listdir(fullpath) == []:
    #    print "no files to work with!"
    #else:
    #    fetch(fullpath)