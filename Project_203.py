
import re, os, shutil, csv
from Tkinter import *

class Window:

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
         self.sqf_file = {}
         for dirpath, subdirs, files in os.walk(path):
            for f in files:
                if f.endswith(".sqm"):
                    self.sqm_file[os.path.join(dirpath, f)] = os.path.basename(f)
                elif f.endswith(".ext"):
                    self.ext_file[os.path.join(dirpath, f)] = os.path.basename(f)
                elif f == '=BTC=_revive_init.sqf':
                    self.sqf_file[os.path.join(dirpath, f)] = os.path.basename(f)
                
         print self.sqm_file, self.ext_file, self.sqf_file
         
         self.player_count = 0
         self.island  = 'unknown_island'
         self.addons_on = False
         self.game_type = 'unk'
         self.mission_des = ''
         self.mission_name = 'no_name'
         
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
                elif '};' in line or self.addons_on == True:
                    watch_for_addons = False
                elif '"a3_map_altis"' in line:
                    self.island = 'altis'
                elif '"a3_map_stratis"' in line:
                    self.island = 'stratis'
                elif watch_for_addons == True and self.addons_on == False:  
                    if ('"a3_') in line or ('"A3_') in line or ('{') in line:
                        self.addons_on = False
                    else:
                        self.addons_on = True                       
                outfile.write(line)
         infile.close()
         outfile.close()
         sqm_data = [self.player_count, self.island, self.addons_on]              
         return sqm_data, new_sqm
         
     def examine_ext(self):
         
         game_types = ['coop','dm','tdm','ctf','sc','cti','rpg','seize','defend',
         'zdm','zctf','zcoop','zsc','zcti','ztdm','zrpg','zgm','zvz','zvp']
        
         respawn_check = re.compile('respawn = ', re.IGNORECASE)
         on_load_name_check = re.compile('onLoadName = ', re.IGNORECASE)
         on_load_mission_check = re.compile('onLoadMission = ', re.IGNORECASE)
         
         new_ext = 'new_ext.ext'
         infile = open(self.ext_file.keys()[0], 'r')
         outfile = open(new_ext, 'w')
         
         for line in infile:
                if 'briefingname' in line.lower():
                    print 'briefing name erased in .ext!'
                    line = line.replace(line,'')
                #find better solution for case insensitive search    
                elif on_load_name_check.match(line):
                    load_name = re.search(' (.*$)', line)
                    if load_name != None:
                        self.mission_name = load_name.group()[3:]
                        self.mission_name = self.mission_name.replace(' ','_')
                        self.mission_name = self.mission_name.lower()
                    else:
                        self.mission_name = 'no_name'    
                    print 'mission name is ', self.mission_name
                elif on_load_mission_check.match(line):
                    des = re.search(' (.*$)', line)
                    if des != None:
                        self.mission_des = des.group()[3:]
                    else:
                        self.mission_des = 'no description'    
                    print 'mission description is ', self.mission_des    
                elif respawn_check.match(line): #and has_respawn_btc == False:
                    print 'setting respawn'
                    if re.search(r'[0-5]', line) != None:
                        line = 'Respawn = 4;\n'
                    else: 
                        line = 'Respawn = "GROUP";\n'
                elif "gametype =" in line.lower():
                    for game in game_types:
                        if game in line.lower():
                            self.game_type = game         
                outfile.write(line)              
         infile.close()
         outfile.close()       
         ext_data = [self.mission_name, self.mission_des, self.game_type]       
         return ext_data, new_ext
         
     def examine_btc(self):
         
         has_respawn_btc = False
         btc_0 = 'BTC_disable_respawn = 0;'
         btc_1 = 'BTC_disable_respawn = 1;'  
         
         new_btc = 'new_btc.sqm'
         infile = open(self.sqf_file.keys()[0], 'r')
         outfile = open(new_btc, 'w')
         
         for line in infile:
                if btc_0 in line:
                    print 'found BTC'
                    line = line.replace(line, '%s\n' % (btc_1))
                    has_respawn_btc = True
                    print 'btc: ' + str(has_respawn_btc)
                outfile.write(line)            
         infile.close()
         outfile.close()
         return new_btc
         
     def folder_name(self): 
         game_type = self.game_type[:2]
         
         if self.addons_on:
             addons = '@'
         else:
             addons = ''
         if self.player_count < 10:
             player_count = '0' + str(self.player_count)
         else:
             player_count = str(self.player_count)
                         
         folder_name = game_type, str(addons), player_count, '_', self.mission_name, '.', self.island, '.pbo'
         folder_name = ''.join(folder_name)
         return folder_name
         
     def copy_and_replace(self, original_file, edit): 
        ''' rename files in mission folder, erase originals, move copies '''   
        os.remove(original_file)
        shutil.copy(edit, original_file)
        os.remove(edit)  
     
     def modify_folders(self, original_name, folder_name):             
        try:
            os.rename(original_name, folder_name)
        except NameError:
            print 'required files are not found'
        except WindowsError:
            print 'folder with the same name already exists'
        #finally:
        #    os.rename(original_name, folder_name + '1')    
            
     def mission_info(self):
         print '\n'
         print 'Mission name: ', self.mission_name 
         print 'Mission description: ', self.mission_des  
         print 'Player count: ', str(self.player_count)
         print 'Game type: ', self.game_type 
         print 'Addons: ', str(self.addons_on)
         print 'Island: ', self.island
                                
fullpath = "F:\Games\Arma 2\Osku's tool\input"

def find_folders(fullpath):
    '''  search for folders inside main folder  '''
    directories = [fullpath + "\\" + x for x in os.listdir(fullpath)]
    return directories

def main():    
    list_file = open('new_missions_list.csv', 'w')
    writer = csv.writer(list_file)
    
    start = find_folders(fullpath)
    
    for mis in start:
        mis1 = Mission(mis)

        try:
            sqm = mis1.examine_sqm()
        except IndexError:
            'no sqm file in directory'
        
        try:                        
            ext = mis1.examine_ext()
        except IndexError:
            print 'no ext file in directory'        
        except WindowsError:
            print 'no ext file in directory'
        finally:
            ext = None
            
        try:    
            mis1.examine_btc()
        except IndexError:
            print 'no sqf file in directory'
        
        print sqm, ext
        folder_name = mis1.folder_name()    
        print folder_name
    
        mis1.copy_and_replace(mis + '\\mission.sqm', sqm[1])
        
        if ext != None:
            try:
                mis1.copy_and_replace(mis + '\\description.ext', ext[1])
            except WindowsError:
                print 'no ext file in directory'
        
        folder_name = folder_name.translate(None, '!@#$:;*,"=-')
        mis1.modify_folders(mis, fullpath + '\\' + folder_name)
        
        
        writer.writerow((mis1.player_count, folder_name, mis1.mission_des, 'author', '', '', '', mis1.island))
    list_file.close()
    
main()