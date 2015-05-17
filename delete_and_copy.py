import os, shutil, sys
from subprocess import Popen


if len(sys.argv) > 1:
    input_path = sys.argv[1] + '\input'
    backup_path = sys.argv[1] + '\_backup_'
    oskus_tool = sys.argv[1]    

else:
    input_path = "F:\Games\Arma 2\Osku's tool\input"
    backup_path = "F:\Games\Arma 2\Osku's tool\_backup_"
    oskus_tool = "F:\Games\Arma 2\Osku's tool"

def delete_files(input_path): 
    for dirpath, subdirs, files in os.walk(input_path):
        for dirs in subdirs:
            print input_path, dirs
            shutil.rmtree(os.path.join(input_path, dirs)) 
            
            
def copy_files(backup_path, input_path):
    for dirpath, subdirs, files in os.walk(backup_path):
        for f in files:
            print input_path, f
            shutil.copy(os.path.join(backup_path, f), input_path) 
            
def unpack(oskus_tool):
    p = Popen("cmd.exe /c extract.bat", cwd=r"%s" % (oskus_tool))
    stdout, stderr = p.communicate()
    print p.returncode # is 0 if success
    
def main():
    delete_files(input_path)
    copy_files(backup_path, input_path)
    unpack(oskus_tool) 
         
if __name__ == "__main__":
    main()
          
