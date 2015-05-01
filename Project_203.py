
import re, os, shutil, csv
from urllib import unquote
from subprocess import Popen
from unicodedata  import normalize
from Tkinter import *

class Window:
    """ Interface from where you can pass location of Osku's Tool to the
    program (fullpath) if Swissknife is not in the same folder. """
    # temporarily disabled for more convenient testing
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
    """ Class to store and process mission data and mission files. """
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
                    if 'lite' not in dirpath:
                        self.btc_file[os.path.join(dirpath, f)] = os.path.basename(f)
                elif f == 'FAR_revive_init.sqf':
                    self.far_file[os.path.join(dirpath, f)] = os.path.basename(f)
                
         print self.sqm_file, self.ext_file, self.btc_file, self.far_file
         
         self.player_count = 0
         self.island  = 'unknown_island'
         self.addons_on = False
         self.game_type = 'unk'
         self.mission_des = ''
         self.mission_name = 'no_name'
         self.author = 'unknown_author'
         
    def examine_sqm(self):
         """ Search through sqm file to look for number of players, find out if 
         mission uses addons, erase briefing info parameter and get mission 
         description if it's there """
         
         if self.sqm_file == {}:
             return None
         
         watch_for_addons = False
         new_sqm = 'new_sqm.sqm'
         
         overview_text_check = re.compile('\s*overviewText[ =]', re.IGNORECASE)
         all_in_arma_island = re.compile('\s*"aia_', re.IGNORECASE)
         
         infile = open(self.sqm_file.keys()[0], 'r')
         outfile = open(new_sqm, 'w')
         
         """
            WHAT IF THIS COULD BE HANDLED BY READING ENTIRE FILE
            VIA 'READ' AND THEN SEARCHING FOR STRINGS AND DETELING
            BRIEFING LINE
            """ 
         
         for line in infile:
                # erasing briefing name
                if 'briefingName="' in line or 'briefingName' in line:
                    print 'briefing name erased in .sqm!'
                    line = line.replace(line,'        briefingName="";\n')
                    
                # counting number of players
                elif 'player="' in line:
                    print 'counting players', self.player_count
                    self.player_count +=1
                    
                # checking addons and island
                elif ('addOns[]=' in line or 'addOnsAuto[]=' in line) and self.addons_on == False:
                    watch_for_addons = True
                    print 'addons: ', self.addons_on 
                elif '};' in line:
                    watch_for_addons = False
                elif '"a3_map_altis"' in line:
                    self.island = 'altis'
                elif '"a3_map_stratis"' in line:
                    self.island = 'stratis'
                elif '"thirskw"' in line:
                    self.island = 'thirskw'
                elif all_in_arma_island.match(line):
                    if self.island == 'unknown_island':
                        self.island = line.replace('"aia_','').replace('_config"','').strip().rstrip(',')
                        if self.island != 'saralite' or self.island != 'sara_dbe1' or self.island == 'sara':
                            self.island = 'unknown_island'
                elif '"bootcamp_acr"' in line:
                    self.island = 'bootcamp_acr'
                elif '"smd_sahrani_a2"' in line:
                    self.island = 'smd_sahrani_a2'
                elif '"woodland_acr"' in line:
                    self.island = 'woodland_acr'
                elif '"pja305"' in line:
                    self.island = 'n\'ziwasogo'
                elif '"map_vr"' in line:
                    self.island = 'vr'
                elif '"mcn_hazarkot"' in line:
                    self.island = 'mcn_hazarkot'
                elif '"fata"' in line:
                    self.island = 'fata'
                elif '"panovo_island"' in line:
                    self.island = 'panovo'
                elif '"colleville_island"' in line:
                    self.island = 'colleville_island'
                elif '"baranow_island"' in line:
                    self.island = 'baranow_island'
                elif '"ivachev_island"' in line:
                    self.island = 'ivachev_island'
                elif '"staszow_island"' in line:
                    self.island = 'staszow_island'
                elif watch_for_addons == True and self.addons_on == False:  
                    if ('"a3_') not in line and ('"A3_') not in line:
                        if '{' not in line: 
                            self.addons_on = True
                            
                # check if mission description is inside sqm
                elif overview_text_check.match(line):
                    des = line.split("=")[1].split(";")[0]
                    self.mission_des = self.mission_description(des)
                    print 'mission description is ', self.mission_des 
                                         
                outfile.write(line)
                
         #if (self.island != 'altis' or self.island != 'stratis') and self.addons_on == False:
         #    self.addons_on = True
                
         infile.close()
         outfile.close()
         sqm_data = [self.player_count, self.island, self.addons_on]              
         return [sqm_data, new_sqm]
         
    def examine_ext(self):
         """ Method to handle data from ext file, erase briefing name, set 
         respawn to group, find game type, mission name, description, 
         author's name. """
         
         if self.ext_file == {}:
             return None
         
         game_types = ['coop','dm','tdm','ctf','sc','cti','rpg','seize','defend',
         'zdm','zctf','zcoop','zsc','zcti','ztdm','zrpg','zgm','zvz','zvp', 'sp']
        
         respawn_check = re.compile('respawn[ =]', re.IGNORECASE)
         on_load_name_check = re.compile('onLoadName[ =]', re.IGNORECASE)
         on_load_mission_check = re.compile('onLoadMission[ =]', re.IGNORECASE)
         overview_text_check = re.compile('overviewText[ =]', re.IGNORECASE)
         
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
                        self.mission_name = self.mission_name.strip().split(';')[0].lower()
                        self.mission_name = self.mission_name.strip(' _').replace('__','_').replace(' ','_')
                        self.mission_name = self.mission_name.translate(None, '";,*=-()\'.&#/<>|').rstrip('_') 
                    print 'mission name is ', self.mission_name
                
                # checking mission description
                elif overview_text_check.search(line) or on_load_mission_check.search(line):
                    print line
                    des = line.split("=")[1]
                    self.mission_des = self.mission_description(des)
                    print 'mission description is ', self.mission_des
                
                # checking respawn type    
                elif respawn_check.match(line): 
                    print 'setting respawn'
                    line = line.replace(line,'Respawn = 4;\n')
                    
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
                    self.author = self.author.translate(None, '"";.[]').split(";")[0]
                    print 'mission author: ', self.author         
                
                outfile.write(line)              
         
         infile.close()
         outfile.close()       
         ext_data = [self.mission_name, self.mission_des, self.game_type]       
         return [ext_data, new_ext]
         
    def examine_btc(self):
         """ Method to disable BTC respawn. """
         
         if self.btc_file == {}:
             return None
             
         has_respawn_btc = False
         btc_0 = 'BTC_disable_respawn = 0;'
         btc_1 = 'BTC_disable_respawn = 1;'  
         
         new_btc = 'new_btc.sqm'
         
         infile = open(self.btc_file.keys()[0], 'r')
         source = self.btc_file.keys()[0]
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
         return [source, new_btc]
         
    def examine_far(self):
         """ Method to change FAR respawn to option 3. """
         
         if self.far_file == {}:
             return None
         
         has_revive_far = False
         far = 'FAR_ReviveMode ='
         far_2 = 'FAR_ReviveMode = 2;' 
         
         new_far = 'new_far.sqm'
         infile = open(self.far_file.keys()[0], 'r')
         outfile = open(new_far, 'w')
         
         for line in infile:
            if far in line:
                line = line.replace(line, '%s\n' % (far_2))
                print 'FAR line replacement: ', line
                has_revive_far = True
                print 'FAR: ' + str(has_revive_far)
            outfile.write(line)            
         infile.close()
         outfile.close()
         return new_far
         
    def mission_description(self, des):
         """ method to extract mission description """
         if des != None or des != '':
            des = des.translate(None, '";').strip()
            if len(des) > len(self.mission_des):
                self.mission_des = des
         return self.mission_des 
         
    def folder_name(self, original_folder_name):
         """ generate new folder name from the acquired data """
         
         islands = ['chernarus', 'utes', 'zargabad', 'takistan', 'bystrica', 
         'bukovina', 'shapur', 'desert', 'sahrani', 'imrali', 'thirskw', 
         'thirsk', 'namalsk', 'fallujah', 'lingor', 'clafghan', 'rahmadi', 
         'southern_sahrani', 'united_sahrani', 'porto', 'takistan_mountains',
         'mountains_acr', 'chernarus_summer', 'proving_grounds', 'n\'ziwasogo', 
         'praa_av', 'fdf_isle1_a', 'provinggrounds_pmc', 'staszow_island', 'panovo', 
         'colleville_island', '_island', 'sara', 'saralite', 'sara_dbe1', 
         'afghanistan', 'vr'] 
            
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
             
         if player_count == '01' and game_type == 'un':
             game_type = 'sp'
             
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
         if self.mission_name == 'no_name' or self.mission_name == '':
             name = unquote(original_folder_name)
             name = name.translate(None, '";,*=-()&#/<>|').replace('__','_').replace(' ','_').split(".")[0].lower()
             self.mission_name = name
             in_brackets = re.compile(r'\[(^)]*\)')
             self.mission_name = re.sub(in_brackets, '', self.mission_name)
             in_brackets_sq = re.compile(r'\[[^)]*\]')
             self.mission_name = re.sub(in_brackets_sq, '', self.mission_name)
             self.mission_name = self.mission_name.rstrip('_')
         # this check is to get rid of repetition of player count and mission type
         """
            THIS DOES NOT GET RID OF PLAYER COUNT IN MISSION NAME ALWAYS
            CASES WHERE IT DOES NOT:
                co@05_co5_the_convoy_ukf.clafghan
                co@08_co@08_weapon_of_mass_destruction.bootcamp_acr
            BETTER USE RE
         """
         if self.mission_name[0:4] == game_type + player_count: 
             self.mission_name = self.mission_name[5:]
         if self.mission_name[0:5] == game_type + str(addons) + player_count: 
             self.mission_name = self.mission_name[6:]
                 
         print 'name from filename is ', self.mission_name
            
         # make new folder name using data found in files
         if game_type == 'sp':
             if game_type == self.mission_name[0:2]:
                folder_name = self.mission_name, '.', self.island
             else: 
                folder_name = game_type, str(addons), '_', self.mission_name, '.', self.island
         else:                 
             folder_name = game_type, str(addons), player_count, '_', self.mission_name, '.', self.island # '.pbo' not needed, Osku's Tool adds .pbo   
         
         # final checks - removal of unwanted characters
         folder_name = ''.join(folder_name)
         folder_name = folder_name.rstrip('_').replace('__','_')
         return folder_name
         
    def copy_and_replace(self, original_file, edit): 
        """ rename files in mission folder, erase originals, move copies """   
        os.remove(original_file)
        shutil.copy(edit, original_file)
        os.remove(edit)  
     
    def modify_folders(self, original_name, folder_name):
        """ rename folder, warn if duplicate """  
        print original_name, folder_name           
        try:
            os.rename(original_name, folder_name)
        except NameError:
            print 'warning: required files are not found'
        except WindowsError:
            print 'warning: folder with the same name already exists or bad filename'
            folder_name = folder_name + '.DUPLICATE'
            os.rename(original_name, folder_name)
            """
            FIND A WAY TO HANDLE DUPLICATES REGARDLESS OF HOW MANY THERE ARE
            """    
            
    def mission_info(self):
         """ prints out mission info """
         print '\n'
         print '==========================================================================='
         print 'Mission name: ', self.mission_name 
         print 'Mission description: ', self.mission_des  
         print 'Player count: ', str(self.player_count)
         print 'Game type: ', self.game_type 
         print 'Addons: ', str(self.addons_on)
         print 'Island: ', self.island
         print 'Author: ', self.author
         print '==========================================================================='
                                
def find_folders(fullpath):
    """ search for folders inside input folder """
    directories = [fullpath + "\\" + x for x in os.listdir(fullpath)]
    return directories

def unpack(fullpath):
    """ unpack mission files using Osku's Tool and CPBO """
    oskus_input = os.path.dirname(fullpath)
    p = Popen("cmd.exe /c extract.bat", cwd=r"%s" % (oskus_input))
    stdout, stderr = p.communicate()
    
def repack(fullpath):
    """ repack mission files using Osku's Tool and CPBO """
    oskus_repack = os.path.dirname(fullpath)
    p = Popen("cmd.exe /c repack.bat", cwd=r"%s" % (oskus_repack))
    stdout, stderr = p.communicate()

def arma_island_name_lookup(island):
    island_collection = {'thirskw' : 'Thirsk Winter',
                         'thirsk' : 'Thirsk', 
                         'chernarus_summer' : 'Chernarus summer',
                         'bootcamp_acr' : 'Bukovina', 
                         'woodland_acr' : 'Bystrica', 
                         'afghan' : 'Afghanistan',
                         'praa_av' : 'Afghan Village', 
                         'smd_sahrani_a2' : 'Sahrani',
                         'shapur_baf' : 'Shapur', 
                         'provinggrounds_pmc' : 'Proving Grounds',
                         'desert_e' : 'Desert',
                         'mountains_acr' : 'Takistan Cutout',
                         'vr' : 'VR',
                         'mcn_hazarkot' : 'Hazar-Kot',
                         'fata' : 'Fata',
                         'colleville_island' : 'Colleville',
                         'baranow_island' : 'Baranow Island',
                         'ivachev_island' : 'Ivachev Island',
                         'staszow_island' : 'Staszow Island',
                         'panovo' : 'Panovo', 
                         'fdf_isle1_a' : 'Podagorsk',
                         'sara' : 'Sahrani',
                         'saralite' : 'South Sahrani',
                         'sara_dbe1' : 'United Sahrani'}
    
    if island in island_collection:
        return island_collection[island]
    return None

def main(fullpath):
    """ calls function to search for missions and then process them iteratively,
    copy files, rename folders, and write data to csv file """ 
    
    unpack(fullpath)
                
    list_file = open('new_missions_list.csv', 'wb')
    writer = csv.writer(list_file)
    
    start = find_folders(fullpath)
    
    for mis in start:
        
        mission = Mission(mis)
        original_folder_name = os.path.basename(os.path.normpath(mis))

        # start processing
        sqm = mission.examine_sqm()
        ext = mission.examine_ext()
        btc = mission.examine_btc()
        far = mission.examine_far()
        print sqm, ext, btc, far
        
        # generate folder name
        folder_name = mission.folder_name(original_folder_name)    
        print folder_name
        
        # copy all files
        mission.copy_and_replace(mis + '\\mission.sqm', sqm[1])
        
        if ext:
            mission.copy_and_replace(mis + '\\description.ext', ext[1])

        if btc:    
            mission.copy_and_replace(btc[0], btc[1])
            
        if far:
            mission.copy_and_replace(mission.far_file.keys()[0], far)
        
        # rename folder
        if isinstance(folder_name, unicode) == False:
             folder_name = folder_name.translate(None, '!#$:;*,"=-[]').rstrip('_')
             folder_name_uni = normalize('NFC', folder_name.decode("utf-8")) 
             mission.modify_folders(mis, fullpath + '\\' + folder_name_uni)
        
        island_lookup = arma_island_name_lookup(mission.island)
        if island_lookup is not None:
            island = island_lookup
        else:
            island = mission.island
            
        # insert entry in mission list csv
        writer.writerow((mission.player_count, folder_name, mission.mission_des, mission.author, '', '', '', island.title(), original_folder_name))
    list_file.close()
    
    repack(fullpath)
    
    
if __name__ == "__main__":
    # hardcoded fullpath for testing purposes
    fullpath = os.getcwd()
    filenames = next(os.walk(fullpath))[2]
    #print filenames
    if "extract.bat" in filenames and "repack.bat" in filenames and "reset.bat" in filenames:
        fullpath = fullpath  + "\\input"
    #else:
    #    fullpath = "F:\Games\Arma 2\Osku's tool\input"
    #print os.listdir(fullpath + "\\input")
    if os.listdir(fullpath) == []:
        print "no files to work with!"
    else:
        main(fullpath)
    