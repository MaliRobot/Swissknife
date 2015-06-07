# -*- coding: utf-8 -*-

import re, os, shutil, csv
from urllib import unquote
from files import *

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
                
         print self.sqm_file, self.ext_file, self.btc_file, self.far_file, path
         
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
         
         for line in infile:
                # erasing briefing name
                if re.findall(r'briefingName=\"(.+?)\"', line) != []:
                    print 'briefing name erased in .sqm!'
                    line = re.sub(r'briefingName=\"(.+?)\"', 'briefingName=""', line)
                    
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
                elif watch_for_addons == True and '{' not in line:
                    if '"a3_map_altis"' in line:
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
                    elif '"utes"' in line:
                        self.island = 'utes'
                    elif '"pra_3"' in line:
                        self.island = 'kunduz'
                    elif '"a3_map_isladuala3"' in line:
                        self.island = 'isla_duala'
                    elif '"panovo_island"' in line:
                        self.island = 'panovo'
                    elif '"colleville_island"' in line:
                        self.island = 'colleville'
                    elif '"baranow_island"' in line:
                        self.island = 'baranow'
                    elif '"ivachev_island"' in line:
                        self.island = 'ivachev'
                    elif '"staszow_island"' in line:
                        self.island = 'staszow'
                    if self.addons_on == False:  
                        if ('a3_') not in line and ('A3_') not in line:
                            self.addons_on = True 
                            
                # check if mission description is inside sqm
                elif overview_text_check.match(line):
                    des = line.split("=")[1].split(";")[0]
                    self.mission_des = self.mission_description(des)
                    print 'mission description is ', self.mission_des
                                         
                outfile.write(line)
                
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
                
                # we can get the number of players from the Header class, 
                # maxPlayers parameter, but it is not reliable mathod        
                #elif re.match(r'\s+maxPlayers[ ]{0,1}=', line):
                #    self.player_count = int(re.sub(r'[\D]', '', line))
                
                # checking mission name     
                elif on_load_name_check.match(line):
                    load_name = re.search('=(.*$)', line)
                    if load_name != None:
                        self.mission_name = load_name.group()[2:]
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
                elif "author =" in line.lower() or "author=" in line.lower():
                    print 'checking mission author name'
                    self.author = ' '.join(line.split(' ')[2:])
                    self.author = self.author.translate(None, '"";.[]').split(";")[0]
                    self.author = self.author.strip()
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
             
         btc_0 = 'BTC_disable_respawn = 0;'
         btc_1 = 'BTC_disable_respawn = 1;'  
         
         new_btc = 'new_btc.sqm'
         
         infile = open(self.btc_file.keys()[0], 'r')
         source = self.btc_file.keys()[0]
         
         data = infile.read()
         if btc_0 in data:  
             print 'btc respawn not disabled'
             outfile = open(new_btc, 'w')
             data = data.replace("BTC_disable_respawn = 0;", "BTC_disable_respawn = 1;")
             outfile.write(data)
             outfile.close()
             print 'btc respawn now disabled'                                       
         elif btc_1 not in data.splitlines():
             outfile = open(new_btc, 'w')             
             for line in infile:
                 if 'EDITABLE' in line:
                     line = line + '\nBTC_disable_respawn = 1;'
                     print 'disable respawn parameter added'
                 outfile.write(line + '\n')
             outfile.close()
         else:
            print 'btc respawn already disabled'
            infile.close()
            return []
            
         infile.close()
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
         'praa_av', 'fdf_isle1_a', 'provinggrounds_pmc', 'staszow', 'panovo', 
         'colleville', 'baranow', 'ivachev', 'sara', 'saralite', 'sara_dbe1', 
         'afghanistan', 'vr', 'kunduz', 'isla_duala'] 
            
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
         self.mission_name = self.mission_name.decode('ascii','ignore').encode("windows-1252") 
          
         # if mission name is not found in ext, look for mission name in file name                               
         if self.mission_name.lower() in set(['no_name','', '$str_mission_name', '$str_namemission', '$str_loadtitle', '_']):
             name = unquote(original_folder_name)
             name = name.translate(None, '";,*=-()&#/<>|').replace('__','_').replace(' ','_')
             name = ''.join([x.lower() for x in name.split(".")[:-1]])
             name = re.sub(r'\[(^)]*\)', '', name)
             name = re.sub(r'\[[^)]*\]', '', name)
             self.mission_name = name
         # this check is to get rid of repetition of player count and mission type
         self.mission_name = re.sub(r'[_]{0,1}c[oop\W]{0,4}[_][0-9]{1,2}[_][0-9]{0,2}', '', self.mission_name)
         self.mission_name = re.sub(r'[_]{0,1}c[oop\W]{0,4}[_]{0,1}[0-9]{1,4}[_]', '', self.mission_name)
         self.mission_name = re.sub(r'[_]{0,1}c[oop\W]{2,4}[0-9]{1,4}[_]{0,1}', '', self.mission_name)
         self.mission_name = re.sub(r'_sp_', '', self.mission_name)
         #self.mission_name = re.sub(r'(.+?)\1+', r'\1', self.mission_name)
         self.mission_name = re.sub(r'spco[o]{0,1}p_', '', self.mission_name)
         self.mission_name = self.mission_name.strip('_')
         
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
             folder_name = game_type, str(addons), player_count, '_', self.mission_name, '.', self.island  
         
         # final checks - removal of unwanted characters and repetitions (co, sp, etc.)
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
            os.rename(original_name, folder_name.decode('ascii','ignore').encode("windows-1252"))
            return 'Done'
        except UnicodeEncodeError:
            os.rename(original_name, folder_name.encode('utf-8'))
            return 'Done'
        except NameError:
            print 'warning: required files are not found'
            return 'ERROR: Folder cannot be found'
        except WindowsError:
            print 'warning: folder with the same name already exists or bad filename'
            return 'ERROR: Possible duplicate mission'  
            
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
    
def arma_island_name_lookup(island):
    island_collection = {'thirskw' : 'Thirsk Winter',
                         'thirsk' : 'Thirsk', 
                         'chernarus_summer' : 'Chernarus summer',
                         'utes' : 'Utes',
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
                         'baranow' : 'Baranow',
                         'ivachev' : 'Ivachev',
                         'staszow' : 'Staszow',
                         'panovo' : 'Panovo', 
                         'fdf_isle1_a' : 'Podagorsk',
                         'sara' : 'Sahrani',
                         'saralite' : 'South Sahrani',
                         'sara_dbe1' : 'United Sahrani',
                         'kunduz' : 'Kunduz',
                         'isla_duala' : 'Isla Duala'}
    
    if island in island_collection:
        return island_collection[island]
    return None

def fetch(path):
    """ calls function to search for missions and then process them iteratively,
    copy files, rename folders, and write data to csv file """ 
    
    fullpath = path  + "\\input"
        
    unpack_and_backup(path)
                
    list_file = open('new_missions_list.csv', 'wb')
    writer = csv.writer(list_file)
    
    start = find_folders(path + '\\' + 'input')

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
        if sqm:
            mission.copy_and_replace(mis + '\\mission.sqm', sqm[1])
        
        if ext:
            mission.copy_and_replace(mis + '\\description.ext', ext[1])

        if btc:    
            mission.copy_and_replace(btc[0], btc[1])
            
        if far:
            mission.copy_and_replace(mission.far_file.keys()[0], far)
        
        # rename folder
        folder_name = folder_name.translate(None, '!#$:;*,"=-[]').rstrip('_')
        folder_name = folder_name.lower()

        rename_folder = mission.modify_folders(mis, fullpath + '\\' + folder_name)
        if rename_folder != 'Done':
             folder_name = folder_name + ' ' + rename_folder
        
        island_lookup = arma_island_name_lookup(mission.island)
        if island_lookup is not None:
            island = island_lookup
        else:
            island = mission.island
            
        done = repack(path, folder_name.decode('ascii','ignore').encode("windows-1252"))
            
        # insert entry in mission list csv
        if done == False:
            folder_name = 'ERROR_REPACKING ' + folder_name
            
        #writer.writerow((mission.player_count, folder_name.encode('utf-8'), mission.mission_des, mission.author, '', '', '', island.title(), original_folder_name))
        try:
            writer.writerow((mission.player_count, folder_name.decode('ascii','ignore').encode("windows-1252"), mission.mission_des, mission.author, '', '', '', island.title(), original_folder_name))
        except UnicodeEncodeError:
            writer.writerow((mission.player_count, folder_name.encode('utf-8'), mission.mission_des, mission.author, '', '', '', island.title(), original_folder_name))
    list_file.close()
    
    #repack(path)
    
# if you need this script as standalone uncomment this

#if __name__ == "__main__":
#    # hardcoded fullpath for testing purposes
#    fullpath = os.getcwd()
#    filenames = next(os.walk(fullpath))[2]
#    #print filenames
#    if "extract.bat" in filenames and "repack.bat" in filenames and "reset.bat" in filenames:
#        fullpath = fullpath  + "\\input"
#    #else:
#    #    fullpath = "F:\Games\Arma 2\Osku's tool\input"
#    #print os.listdir(fullpath + "\\input")
#    if os.listdir(fullpath) == []:
#        print "no files to work with!"
#    else:
#        main(fullpath)
    