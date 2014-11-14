
import re, os, shutil, csv, urllib
from Tkinter import *

class Window:
    # temporarilly disabled for more convenient testing
    def __init__(self):
        
        self.master = Tk()
        self.master.geometry("400x150")
        self.master.title("Swissknife")
        
        frame = Frame(self.master, width=500, height=100)
        
        self.first_label = Label(self.master, text="Enter Osku's Tool input full path:")
        self.first_label.pack(side=TOP)
        
        # area to paste path for Osku's tool
        self.entry = Entry(frame, width = 300)
        self.entry.pack(side=TOP)
        frame.pack()
        self.entry.focus_set()
        
        # process button
        self.button = Button(frame, text="Process", fg="red", width = 10, height=2, command=self.entry_get)
        self.button.pack(side=LEFT, padx=50, pady=10)
        
        # quit button
        self.button2 = Button(frame, text="Quit", width = 10, height = 2, command=self.quit)
        self.button2.pack(side=RIGHT, padx=60, pady = 10)
        
        # label
        self.second_label = Label(self.master, text="Example: F:\Games\Arma 2\Osku's tool\input")
        self.second_label.pack(side=TOP)
        
    def start(self):
        self.master.mainloop()
    
    def entry_get(self):
        print self.entry.get()
        fullpath = self.entry.get()
        search_files(fullpath)
     
    def quit(self):
        self.master.destroy()  

class Mission:
     def __init__(self, path):
         self.directory = path
         self.sqm_file = {}
         self.ext_file = {}
         self.btc_file = {}
         self.far_file = {}
         for dirpath, subdirs, files in os.walk(path):
            for f in files:
                if f.endswith(".sqm"):
                    self.sqm_file[os.path.join(dirpath, f)] = os.path.basename(f)
                elif f.endswith(".ext"):
                    self.ext_file[os.path.join(dirpath, f)] = os.path.basename(f)
                elif f == '=BTC=_revive_init.sqf':
                    self.btc_file[os.path.join(dirpath, f)] = os.path.basename(f)
                elif f == 'FAR_revive_init.sqf':
                    self.far_file[os.path.join(dirpath, f)] = os.path.basename(f)
                
         print self.sqm_file, self.ext_file, self.btc_file
         
         self.player_count = 0
         self.island  = 'unknown_island'
         self.addons_on = False
         self.game_type = 'unk'
         self.mission_des = ''
         self.mission_name = 'no_name'
         self.author = 'unknown_author'
         
     def examine_sqm(self):
         
         watch_for_addons = False
         new_sqm = 'new_sqm.sqm'
         
         infile = open(self.sqm_file.keys()[0], 'r')
         outfile = open(new_sqm, 'w')
         
         for line in infile:
                if 'briefingName="' in line or 'briefingName' in line:
                    print 'briefing name erased in .sqm!'
                    line = line.replace(line,'        briefingName="";\n')
                elif 'player="' in line:
                    print 'counting players', self.player_count
                    self.player_count +=1
                elif ('addOns[]=' in line or 'addOnsAuto[]=' in line) and self.addons_on == False:
                    watch_for_addons = True
                    print 'addons: ', self.addons_on 
                elif '};' in line:
                    watch_for_addons = False
                elif '"a3_map_altis"' in line:
                    self.island = 'altis'
                elif '"a3_map_stratis"' in line:
                    self.island = 'stratis'
                elif watch_for_addons == True and self.addons_on == False:  
                    if ('"a3_') not in line and ('"A3_') not in line:
                        if '{' not in line: 
                            self.addons_on = True                      
                outfile.write(line)
         infile.close()
         outfile.close()
         sqm_data = [self.player_count, self.island, self.addons_on]              
         return sqm_data, new_sqm
         
     def examine_ext(self):
         ''' Method to handle data from ext file, erase briefing name, set 
         respawn to group, find game type, mission name, description, 
         author's name'''
         
         game_types = ['coop','dm','tdm','ctf','sc','cti','rpg','seize','defend',
         'zdm','zctf','zcoop','zsc','zcti','ztdm','zrpg','zgm','zvz','zvp']
        
         respawn_check = re.compile('respawn[ =]', re.IGNORECASE)
         on_load_name_check = re.compile('onLoadName =', re.IGNORECASE)
         on_load_mission_check = re.compile('onLoadMission =', re.IGNORECASE)
         
         new_ext = 'new_ext.ext'
         infile = open(self.ext_file.keys()[0], 'r')
         outfile = open(new_ext, 'w')
         
         for line in infile:
                
                # erase briefing name
                if 'briefingname' in line.lower():
                    print 'briefing name erased in .ext!'
                    line = line.replace(line,'')
                
                # checking mission name     
                elif on_load_name_check.match(line):
                    load_name = re.search(' (.*$)', line)
                    if load_name != None:
                        self.mission_name = load_name.group()[3:]
                        in_brackets = re.compile(r'\[[^)]*\]')
                        self.mission_name = re.sub(in_brackets, '', self.mission_name)
                        self.mission_name = self.mission_name.replace(' ','_')
                        self.mission_name = self.mission_name.translate(None, '";,*=-()&#/<>|')
                        self.mission_name = self.mission_name.lower()
                    else:
                        self.mission_name = 'no_name'    
                    print 'mission name is ', self.mission_name
                
                # checking mission description
                elif on_load_mission_check.match(line):
                    des = re.search(' (.*$)', line)
                    if des != None:
                        self.mission_des = des.group()[3:]
                        self.mission_des = self.mission_des.translate(None, '";')
                    else:
                        self.mission_des = 'no description'    
                    print 'mission description is ', self.mission_des
                
                # checking respawn type    
                elif respawn_check.match(line): 
                    #print 'setting respawn'
                    #if re.search(r'[0-5]', line) != None:
                    line = line.replace(line,'Respawn = 4;\n')
                    #    print line
                    #else: 
                    #    line = line.replace(line,'Respawn = "GROUP";')
                    #    print line
                    
                # checking game type        
                elif "gametype =" in line.lower():
                    print 'checking game type'
                    for game in game_types:
                        if game in line.lower():
                            self.game_type = game
                            print 'game type is: ', game
                
                # checking mission makers name
                elif "author =" in line.lower():
                    print 'checking mission author name'
                    self.author = ' '.join(line.split(' ')[2:])
                    self.author = self.author.translate(None, '"";.[]')
                    print 'mission author: ', self.author         
                
                outfile.write(line)              
         
         infile.close()
         outfile.close()       
         ext_data = [self.mission_name, self.mission_des, self.game_type]       
         return ext_data, new_ext
         
     def examine_btc(self):
         ''' Method to disable BTC respawn '''
         has_respawn_btc = False
         btc_0 = 'BTC_disable_respawn = 0;'
         btc_1 = 'BTC_disable_respawn = 1;'  
         
         new_btc = 'new_btc.sqm'
         infile = open(self.btc_file.keys()[0], 'r')
         outfile = open(new_btc, 'w')
         
         for line in infile:
                if btc_0 in line:
                    print 'found BTC'
                    line = line.replace(line, '%s\n' % (btc_1))
                    print 'BTC line replacement: ', line
                    has_respawn_btc = True
                    print 'BTC: ' + str(has_respawn_btc)
                outfile.write(line)            
         infile.close()
         outfile.close()
         return new_btc
         
     def examine_far(self):
         ''' Method to change FAR respawn to option 3 '''
         has_revive_far = False
         far_1 = 'FAR_ReviveMode = 0;'
         far_2 = 'FAR_ReviveMode = 1;'
         far_3 = 'FAR_ReviveMode = 2;'  
         
         new_far = 'new_far.sqm'
         infile = open(self.far_file.keys()[0], 'r')
         outfile = open(new_far, 'w')
         
         for line in infile:
                if far_1 in line or far_2 in line:
                    line = line.replace(line, '%s\n' % (far_3))
                    print 'FAR line replacement: ', line
                    has_revive_far = True
                    print 'FAR: ' + str(has_revive_far)
                outfile.write(line)            
         infile.close()
         outfile.close()
         return new_far
         
     def folder_name(self, original_folder_name):
         '''  Generate new folder name from the acquired data '''
         
         islands = ['fallujah', 'chernarus', 'utes', 'zagrabad', 'takistan', 
         'bystrica', 'imrali'] 
            
         game_type = self.game_type[:2]
         
         # add @ symbol if mission uses addons
         if self.addons_on:
             addons = '@'
         else:
             addons = ''
         
         # add zero to number if player count is less than 10
         if self.player_count < 10:
             player_count = '0' + str(self.player_count)
         else:
             player_count = str(self.player_count)
             
         # temporary solution: when game type is not recognized - it is set to coop
         if game_type == 'un':
             game_type = 'co'
          
         # if island is not found in mission files, try looking in filename
         if self.island == 'unknown_island':
             for island in islands:
                 if island in original_folder_name.lower():
                     self.island = island
                     if self.addons_on == False:
                         self.addons_on = True
                         addons = '@'
          
         # if mission name is not found in ext, look for mission name in file name                               
         if self.mission_name == 'no_name':
             name = urllib.unquote(original_folder_name)
             name = name.translate(None, '";,*=-()&#/<>|').replace(' ','_').split(".")[0].lower()
             # remove everything that is inside "[]" brackets
             in_brackets = re.compile(r'\[(^)]*\)')
             self.mission_name = re.sub(in_brackets, '', name)
             in_brackets_sq = re.compile(r'\[[^)]*\]')
             self.mission_name = re.sub(in_brackets_sq, '', name)
             print 'name from filename is ', self.mission_name
              
            
         # make new folder name using data found in files                
         folder_name = game_type, str(addons), player_count, '_', self.mission_name, '.', self.island, '.pbo'
         folder_name = ''.join(folder_name)
         return folder_name
         
     def copy_and_replace(self, original_file, edit): 
        ''' rename files in mission folder, erase originals, move copies '''   
        os.remove(original_file)
        shutil.copy(edit, original_file)
        os.remove(edit)  
     
     def modify_folders(self, original_name, folder_name):
        ''' rename folder '''             
        try:
            os.rename(original_name, folder_name)
        except NameError:
            print 'required files are not found'
        except WindowsError:
            print 'folder with the same name already exists or bad filename'
            print original_name, folder_name
        #finally:
        #    folder_name = folder_name + '_error'
        #    os.rename(original_name, folder_name)    
            
     def mission_info(self):
         ''' print out mission info '''
         print '\n'
         print 'Mission name: ', self.mission_name 
         print 'Mission description: ', self.mission_des  
         print 'Player count: ', str(self.player_count)
         print 'Game type: ', self.game_type 
         print 'Addons: ', str(self.addons_on)
         print 'Island: ', self.island
         print 'Author: ', self.author
                                
# hardcoded fullpath for testing purposes
fullpath = "F:\Games\Arma 2\Osku's tool\input"

def find_folders(fullpath):
    '''  search for folders inside main folder  '''
    directories = [fullpath + "\\" + x for x in os.listdir(fullpath)]
    return directories

def main():
    ''' calls function to search for missions and then process them one by one,
    copy files, rename folders, and write data to csv file''' 
        
    list_file = open('new_missions_list.csv', 'wb')
    writer = csv.writer(list_file)
    
    start = find_folders(fullpath)
    
    for mis in start:
        mis1 = Mission(mis)
        original_folder_name = os.path.basename(os.path.normpath(mis))

        try:
            sqm = mis1.examine_sqm()
        except IndexError:
            print 'no sqm file in directory or not unpacked file'
            sqm = None
        
        try:                        
            ext = mis1.examine_ext()
        except IndexError:
            print 'no ext file in directory'
            ext = None        
        except WindowsError:
            print 'no ext file in directory'
            ext = None
            
        try:    
            btc = mis1.examine_btc()
        except IndexError:
            print 'no btc file in directory'
            btc = None
            
        try:    
            far = mis1.examine_far()
        except IndexError:
            print 'no far file in directory'
            far = None
        
        print sqm, ext
        folder_name = mis1.folder_name(original_folder_name)    
        print folder_name
    
        mis1.copy_and_replace(mis + '\\mission.sqm', sqm[1])
        
        if ext != None:
            try:
                mis1.copy_and_replace(mis + '\\description.ext', ext[1])
            except WindowsError:
                print 'no ext file in directory'
                
        if btc != None:
            try:
                mis1.copy_and_replace(mis + '\\=BTC=_revive\\=BTC=_revive_init.sqf', btc)
            except WindowsError:
                print 'no sqf file in directory'
                
        if far != None:
            try:
                mis1.copy_and_replace(mis + '\\FAR_revive\\FAR_revive_init.sqf', far)
            except WindowsError:
                print 'no far file in directory'
        
        folder_name = folder_name.translate(None, '!#$:;*,"=-')
        mis1.modify_folders(mis, fullpath + '\\' + folder_name)
        
        writer.writerow((mis1.player_count, folder_name, mis1.mission_des, mis1.author, '', '', '', mis1.island, original_folder_name))
    list_file.close()
    
main()