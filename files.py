from subprocess import Popen, PIPE
import os
from shutil import move, rmtree

#debugging
#path = "F:\Games\Osku's tool"

def check_make(*argv):
    for f in argv:
       if not os.path.exists(f):
            os.makedirs(f) 
            
    
def clear_folder(path):
    for root, dirs, files in os.walk(path):
        for f in files:
       	    os.unlink(os.path.join(path, f))
        for d in dirs:
       	    rmtree(os.path.join(path, d))
        
# debugging
#clear_folder(path + '\\' + 'input')

def unpack_and_backup(path):
    '''
    Copy mission files to backup folder. Unpacks mission files inside 
    input folder. Tries to debinarize mission.sqm in unpacked mission file/folder.
    '''   
    input_path = path + "\\input"
    backup_path = path + "\\_backup_"
    output = path + "\\output"
    cpbo_path = path + "\\cpbo\\cpbo.exe"
    unrap_path = path + "\\unrap\\unRap.exe"
    
    check_make(input_path, backup_path, output)
    
    clear_folder(output)
    
    missions = [] 
    for dirpath, subdirs, files in os.walk(input_path):
        missions.append(files)

    for f in missions[0]:
        path = input_path + '\\' + str(f)
        print path
        p = Popen([cpbo_path, "-y", "-e", path])
        p.wait()

        try:
            move(path, backup_path)
        except Exception as e:
            print e, ' file already present: ', path
            
        # now try to debinarize mission.sqm
        folder_path = path.replace('.pbo', '')
        sqm_path = folder_path + '\\' + 'mission.sqm'
        p = Popen([unrap_path, sqm_path], stdout=PIPE)
        p.wait()
#
#        # check if mission.sqm is binarized, replace mission.sqm with .cpp
        try:
            output = [x for x in p.stdout.readlines()][-1]
            if 'mission.cpp' in output:
                move(os.getcwd() + '\\mission.cpp', path)
                os.remove(sqm_path)    
        except IndexError:
            print "unable to debinarize mission.sqm file of " + str(f) + 'mission'
            os.remove(folder_path)
        
        os.remove(path)            
                    
# debugging       
#unpack_and_backup(path)
        
def repack(path, folder_name):
    input_path = path + "\\input"
    output = path + "\\output"
    cpbo_path = path + "\\cpbo\\cpbo.exe"
    
    check_make(output)
    
    mission_path = input_path + '\\' + folder_name
    
    try:
        p = Popen([cpbo_path, "-y", "-p", mission_path])
        p.wait()
        if os.path.isfile(mission_path + '.pbo') == True:
            move(str(mission_path) + '.pbo', output)
            return True
        return False
    except UnicodeError:
        print 'Cpbo cannot handle filename'
    return False

# debugging        
#repack(path)

