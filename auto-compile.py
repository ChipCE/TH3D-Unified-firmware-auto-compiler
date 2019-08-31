import json
import os
import shutil
import sys

MARLIN_PATH = "Marlin/"
AUTO_COMPILE_DIR = "Auto-compile-output/"
ENVI_NAME = "LPC1769"
AUTO_COMPILE_VERSION = "v0.2.3p"
DEBUG = True

############################ FUNCTIONS ##################################
def debugMsg(msg):
    if DEBUG:
        print(msg)

def saveFile(fileName,fileData):
    try:
        with open(fileName,'w') as fileToSave:
            fileToSave.writelines(fileData)
            return True
    except IOError as err:
        print(err)
        return False


#########################################################################

print("TH3D Unified firmware auto compiler " + AUTO_COMPILE_VERSION)

try:
    with open('auto-compile.json', 'r') as f:
        config = json.load(f)
except IOError as err:
    print(err)
    print("Press ENTER to exit.")
    input()
    sys.exit(1)

#print("Cleanup build folder...")
#os.system("platformio run --target clean -e "+ENVI_NAME)

#create folder to save compiled file
try:
    os.makedirs(AUTO_COMPILE_DIR, exist_ok=True)
except FileExistsError:
    # directory already exists
    pass

# get the terget file name from config
configFile = config['config-file']
print("Target config file : " + configFile)

# loop through each profile
try:
    print("# Trying to read target config file : " + config['config-file'])
    with open(MARLIN_PATH+configFile, 'r') as file :
        configFileData = file.read()
        debugMsg(configFileData)
        #backup
        shutil.copy(MARLIN_PATH+configFile,MARLIN_PATH+configFile+".compile.bak")
        # loop through 
        for profile in config['compile-profile']:
            tmpConfigFileData = configFileData
            debugMsg(profile)
            print("Making " + configFile + " for " + profile['profile-name'])
            #replace text
            for keyword in profile['keyword']:
                debugMsg(keyword)
                tmpConfigFileData = tmpConfigFileData.replace(keyword['find']+"\n",keyword['replace']+"\n")
            #save file
            debugMsg(tmpConfigFileData)
            # also save the config file for preference
            if DEBUG:
                saveFile(AUTO_COMPILE_DIR + profile['profile-name'] + "." + configFile,tmpConfigFileData)
            # overwrite the default config file 
            if saveFile(MARLIN_PATH+configFile,tmpConfigFileData):
                print("Saved OK!\nCompilling...")
                #execute build command
                os.system("platformio run -e "+ENVI_NAME)
                #copy binary file
                print("Copy binary output file to "+AUTO_COMPILE_DIR + profile['profile-name'] + ".firmware.bin")
                shutil.copy(".pioenvs/"+ ENVI_NAME +"/firmware.bin",AUTO_COMPILE_DIR + profile['profile-name'] + ".firmware.bin")
            else:
                print("Cannot save config file " + configFile + " for " + profile['profile-name'])
                print("Skip build for " + profile['profile-name'])

        # restore thr original config file
        print("Restore the original "+configFile)
        saveFile(MARLIN_PATH+configFile,configFileData)
        print("Cleanup build folder...")
        shutil.rmtree(".pioenvs")
        shutil.rmtree(".piolib")
        shutil.rmtree(".piolibdeps")
        print("Done :3")
        print("Press ENTER to exit.")
        input()
        sys.exit(0)
except IOError as err:
    print(err)
    print("Press ENTER to exit.")
    input()
    sys.exit(1)