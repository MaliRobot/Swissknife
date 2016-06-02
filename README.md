
SWISSKNIFE

Swissknife - a modular tool made for CiA Arma gaming clan for formatting filenames according to CiA standard, extracting data, updating mission spreadsheet list and uploading missions to a server.

Features: 
- process mission files and make them CiA server ready (change parameters and format filename)
- make a spreadsheet containing info on processed missions (extract data on no. of players, mission name, description, island and usage of addons)

Requirements:
1. cpbo.exe - from ArmaTools: http://www.armaholic.com/page.php?id=411
2. unRap.exe - you can't get it from UnBuildArma package: http://www.armaholic.com/page.php?id=3320

I reccomend to make a single exe file if you using the program in Windows. Pyinstaller params: pyinstaller --onefile --i icon.ico main.py window.py files.py parse.py

Usage:
Place exe in a folder of your choice. The folder where exe is needs to have structure like this (where everything else beside exe files is a folder):
   

     |- _backup_ 

     |- input

     |- output

     |- swissknife.exe

     |- cpbo

          |- cpbo.exe
   
      |- unrap

          |- unrap.exe
   

This is only recommendation, though, if you are using gui Swissknife you can pass location of the missions to the program, but input, output, _backup_ has to be in a single directory which also includes cpbo directory which contains cpbo.exe and unrap directory with its respective exe.

If you don't create these subfolders they will be created automatically.
In order to use Swissknife without gui just start exe and it will do all the work.
If you want to run gui, create shortcut and put "gui" in target field like this:



Or, if you use command line start exe like this: swissknife.exe gui


If you use gui, you have following options:
- either paste via ctrl-v location of missions folder (folder has to be called "input")
- or if you run exe in the folder which already contains input folder with missions you want to process, just press "Process" button. 
- alternatively, you can press "Current dir." button, this does the same as previous, but it's a way to check you are in your desired location. 


After pressing the "Process" button, the program will start. You will see a console popping up while the program is working.


It will create CSV file ready to be integrated in CiA mission spreadsheet. If it encounters duplicate file it will mark them in CSV as duplicates and such files will not be processed. You can also see all of the data that the program has extracted from the files. 

Latest version link:
https://www.dropbox.com/s/scdalr9us17ragb/swissknife.7z?dl=0

Code:
https://github.com/MaliRobot/Swissknife 


