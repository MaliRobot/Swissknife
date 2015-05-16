from Tkinter import *
from parse import fetch
import os

class Window:
    """ Interface from where you can pass location of Osku's Tool to the
    program (fullpath) if Swissknife is not in the same folder. """
    def __init__(self):
        self.master = Tk()
        self.master.geometry("400x150")
        self.master.title("Swissknife")
                
        self.first_label = Label(self.master, text="Enter Osku's Tool input full path:")
        self.first_label.pack(side=TOP)
        
        # area to paste path for Osku's tool
        self.entry = Entry(self.master, width = 300)
        self.entry.pack(side=TOP)
        self.entry.focus_set()   
        
        # label
        self.second_label = Label(self.master, text="Example: F:\Games\Arma 2\Osku's tool\input")
        self.second_label.pack()
        
        # process button
        self.button = Button(self.master, text="Process", fg="red", width = 10, height=2, command=self.entry_get)
        self.button.pack(padx=20, pady=10, side=LEFT)
        
        self.button2 = Button(self.master, text="Current dir.", width = 10, height = 2, command=self.current)
        self.button2.pack(padx=20, pady = 10, side=LEFT)
        
        # quit button
        self.button3 = Button(self.master, text="Quit", width = 10, height = 2, command=self.quit)
        self.button3.pack(padx=20, pady = 10, side=LEFT)
        
        self.master.mainloop()
        
    def entry_get(self):
        path = self.entry.get()
        if path != None:       
            fetch(path)  
        
    def current(self):
        path = os.getcwd()
        self.entry.delete(0, 'end')
        self.entry.insert(0,path)
        #fetch(path)
     
    def quit(self):
        self.master.destroy()  