from subprocess import Popen
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

    input_path = path + "\\input"
    backup_path = path + "\\_backup_"
    output = path + "\\output"
    cpbo_path = path + "\\cpbo\\cpbo.exe"
    
    check_make(input_path, backup_path, output)
    
    missions = [] 
    for dirpath, subdirs, files in os.walk(input_path):
        missions.append(files)

    for f in missions[0]:
        path = input_path + '\\' + str(f)
        print path
        p = Popen([cpbo_path, "-y", "-e", path])
        p.wait()
        
    for f in missions[0]:
        path = input_path + '\\' + str(f)
        try:
            move(path, backup_path)
        except Exception as e:
            print e, ' file already present: ', path
            os.remove(path)
# debugging       
#unpack_and_backup(path)
        
def repack(path):

    input_path = path + "\\input"
    output = path + "\\output"
    cpbo_path = path + "\\cpbo\\cpbo.exe"
    
    check_make(input_path, output)
    
    missions = [] 
    for item in os.listdir(input_path):
        if os.path.isdir(os.path.join(input_path, item)):
            missions.append(item)

    clear_folder(output)

    for f in missions:
        path = input_path + '\\' + str(f)
        p = Popen([cpbo_path, "-y", "-p", path])
        p.wait()
        move(path + '.pbo', output)

# debugging        
#repack(path)

