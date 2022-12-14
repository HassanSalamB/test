import os
import re
import sys
import shutil
import argparse
from pkg_resources import parse_version as pv

################# Helper Functions ########################
    
def copy_package(masterData, systemNameVersionFolder, systemVersionLatest, apsVersionLatest, systemVersionNew, apsVersionNew):
    for package in os.listdir(os.path.join(masterData, systemNameVersionFolder, systemVersionLatest, apsVersionLatest.split('_')[0], apsVersionLatest)):
        shutil.copytree(os.path.join(masterData, systemNameVersionFolder, systemVersionLatest, apsVersionLatest.split('_')[0], apsVersionLatest, package), os.path.join(masterData, systemNameVersionFolder, systemVersionNew, apsVersionLatest.split('_')[0], apsVersionNew, package))
        print(f"--PASS: Copied {package} from {apsVersionLatest} to {apsVersionNew}")

def create_system_version_new(masterData, systemNameVersionFolder, systemVersionNew, systemVersionCorridorMax):
    if not os.path.exists(os.path.join(masterData, systemNameVersionFolder, systemVersionNew)):
        # Check if the new systemVersionNew is within the corridorMax
        if pv(systemVersionNew.split("_")[-1]) > pv(systemVersionCorridorMax):
            print(f"--ERROR: systemVersionNew > max corridor value! Cannot increment further!")
            return False
        # Create systemVersion folder
        os.mkdir(os.path.join(masterData, systemNameVersionFolder, systemVersionNew))
        print(f"--PASS: Created systemVersionNew folder: {systemVersionNew}")
    return True

# latest version finder
def find_latest_version(version):
    major, minor, micro = re.search('(\d+)\.(\d+)\.(\d+)', version).groups()
    return int(major) or 0, int(minor) or 0, int(micro) or 0

# check if systemName exist in masterdata folder
def check_system_exists(masterData, systemName):
    if not os.path.exists(os.path.join(masterData, systemName)):
        print(f"--ERROR: {systemName} does not exist in the masterdata template....exiting!")
        return False
    else:
        print(f"--INFO: {systemName} exists in the masterdata template!")
        return True

# check if version is in format 1.0.0 and is a number
def check_version_input(version):
    if len(version.split('.')) != 3:
        print(f"--ERROR: Invalid version input: {version}! Please input in the format of x.y.z")
        return False
    for x in version.split('.'):
        if not x.isdigit():
            print(f"--ERROR: Invalid version input: {version}! Please input numbers only")
            return False
    return True

# function to check systemVersionInch is a number and systemVersionIncPos is either major minor or patch
def check_version_IncAndPos(systemVersionInc, systemVersionIncPos):
    if not systemVersionInc.isdigit():
        print(f"--ERROR: Invalid systemVersionInc input:{systemVersionInc}, Please input numbers only!")
        return False
    if systemVersionIncPos not in ["major", "minor", "patch"]:
        print(f"--ERROR: Invalid systemVersionIncPos input:{systemVersionIncPos}, Please input major, minor or patch!")
        return False
    return True

########################### Main functions ########################################

def explicit_folder():
    print("Welcome to the explicit folder creation!")
    # Input examples
    # systemName = 'System-C'
    # systemVersion = '2.0.0'
    # apsNameVersion = {"APS-C": "0.0.1", "APS-D": "0.0.1"} 
    systemName = args.sn
    systemVersion = args.sv
    apsNameVersion = dict(pair.split('=') for pair in args.anv)  

    # variables created from the input
    systemNameVersion = systemName + '_' + systemVersion
    systemNameVersionFolder = systemName + '_' + 'Versions'

    # Check version input from user for systemVersion
    if check_version_input(systemVersion) != True:
        return False
    # Check version input from user for apsNameVersion
    for i in apsNameVersion:
        if check_version_input(apsNameVersion[i]) != True:
            return False
        
    # file_path where template exist and will be updated as per the user configuration
    masterData = os.path.join(os.getcwd(), "../masterdata")

    # 1. CHECK if systemName exist in masterdata folder, if not throw error
    if check_system_exists(masterData, systemName) != True:
        return False

    # 2. CHECK if APS name exists in the masterdata folder, if not throw error
    apsNameList = []
    for apsName in os.listdir(os.path.join(masterData, systemName)):
        apsNameList.append(apsName)
    print(f"--INFO: Items in masterdata: {apsNameList}")
    for i in apsNameVersion:
        if i not in apsNameList:
            print(f"--ERROR: {i} does not exist in the masterdata template....exiting!")
            return False
        else:
            print(f"--INFO: {i} exists in the masterdata template!")

    # 3. CHECK if systemNameVersionsFolder exists in the masterdata folder, if not create it
    if not os.path.exists(os.path.join(masterData, systemNameVersionFolder)):
        print(f"--ERROR: {systemNameVersionFolder} does not exist in the masterdata template....creating it!")
        for index, i in enumerate(apsNameVersion):
            os.makedirs(os.path.join(masterData, systemNameVersionFolder,
                        systemNameVersion, i, i + '_' + apsNameVersion[i]))
            print(f"--PASS: {index+1}. Created {systemNameVersionFolder} -> {systemNameVersion} -> {i} -> {i + '_' + apsNameVersion[i]}!")
    else:
        print(f"--INFO: {systemNameVersionFolder} exists in the masterdata template!")

        # 4. CHECK: if systemNameVersion exists, if not,  create it
        if not os.path.exists(os.path.join(masterData, systemNameVersionFolder, systemNameVersion)):
            print(f"--ERROR: {systemNameVersion} does not exist...creating it!")
            for index, i in enumerate(apsNameVersion):
                os.makedirs(os.path.join(masterData, systemNameVersionFolder,
                            systemNameVersion, i, i + '_' + apsNameVersion[i]))
                print(f"--PASS: Created {systemNameVersion} -> {i} -> {i + '_' + apsNameVersion[i]}!")

    # 5. CHECK: if APS name inside systemVersion exists, if not, create APS name folder
        else:
            print(
                f"--INFO: {systemNameVersion} exists in {systemNameVersionFolder}!")
            for index, i in enumerate(apsNameVersion):
                if not os.path.exists(os.path.join(masterData, systemNameVersionFolder, systemNameVersion, i)):
                    print(f"--ERROR: {index+1}. {i} does not exist in {systemNameVersion}...creating it!")
                    os.makedirs(os.path.join(masterData, systemNameVersionFolder,
                                systemNameVersion, i, i + '_' + apsNameVersion[i]))
                    print(f"--PASS: Created {i} -> {i + '_' + apsNameVersion[i]}")

                # 6. CHECK: if APS version inside APS name exists, if not, create APS version folder
                else:
                    print(f"--INFO: {index+1}. {i} exists in {systemNameVersion}!")
                    if not os.path.exists(os.path.join(masterData, systemNameVersionFolder, systemNameVersion, i, i + '_' + apsNameVersion[i])):
                        print(f"--ERROR: {index+1}. {i + '_' + apsNameVersion[i]} does not exist in {i}...creating it!")
                        os.makedirs(os.path.join(masterData, systemNameVersionFolder,
                                    systemNameVersion, i, i + '_' + apsNameVersion[i]))
                        print(f"--PASS: Created {i + '_' + apsNameVersion[i]}")
                    else:
                        print(f"--INFO: {index+1}. {i + '_' + apsNameVersion[i]} exists in {i}!")

     # Create package from masterdata
    for index, i in enumerate(apsNameVersion):
        for packageName in os.listdir(os.path.join(masterData, systemName, i)):
            print(f"--INFO: {index+1}. {packageName} exists in {i} of the masterData!")
            if not os.path.exists(os.path.join(masterData, systemNameVersionFolder, systemNameVersion, i, i + '_' + apsNameVersion[i], packageName)):
                shutil.copytree(os.path.join(masterData, systemName, i, packageName), os.path.join(
                masterData, systemNameVersionFolder, systemNameVersion, i, i + '_' + apsNameVersion[i], packageName))
                print(f"--PASS: {index+1}. Created {packageName} in {i + '_' + apsNameVersion[i]}!")
            else:
                print(f"--INFO: {index+1}. {packageName} ALREADY exists in {i + '_' + apsNameVersion[i]}! \n This is where package versions will be created from build pipeline!")

        print('*'*20)
    return True


def implicit_folder():
    print("Welcome to the implicit folder creator!")
    # Input examples
    # systemName= "System-C"
    # systemVersionInc= "1"
    # systemVersionIncPos= "major"
    # apsVersionInc= "" --optional
    # apsVersionIncPosition= ""  --optional
    # systemVersionCorridorBase= "0.0.0"  --optional
    # systemVersionCorridorMax= "9.9.9"  --optional
    

    systemName = args.sn
    systemVersionInc = args.svi
    systemVersionIncPos = args.svip
    systemVersionCorridorBase = args.svcb
    systemVersionCorridorMax = args.svcm
    apsVersionInc = args.avi
    apsVersionIncPosition = args.avip

    # If no corridor provided
    if systemVersionCorridorBase == None: systemVersionCorridorBase = '0.0.0'
    if systemVersionCorridorMax == None: systemVersionCorridorMax = '9.9.9'
    print
    # If no aps version increment provided
    if apsVersionInc == None : apsVersionInc = systemVersionInc
    if apsVersionIncPosition == None : apsVersionIncPosition = systemVersionIncPos

    # created variable from input
    systemNameVersionFolder = systemName + '_' + 'Versions'

    # Check the user input for corridor versions
    if check_version_input(systemVersionCorridorBase) != True or check_version_input(systemVersionCorridorMax) != True:
        return False

    # Check the user input for system version increment and position
    if check_version_IncAndPos(systemVersionInc, systemVersionIncPos) != True:
        return False
    
    # Check the user input for aps version increment and position
    if check_version_IncAndPos(apsVersionInc, apsVersionIncPosition) != True:
        return False

    # File_path where template exist and will be updated as per the user configuration
    masterData = os.path.join(os.getcwd(), "../masterdata")

    # CHECK if systemName exists in masterdata
    if check_system_exists(masterData, systemName) != True:
        return False

    # CHECK if systemNameVersionFolder exists
    if check_system_exists(masterData, systemNameVersionFolder) != True:
        return False

    # Get the systemVersionLatest within corridor
    corridorList = []
    for folder in os.listdir(os.path.join(masterData, systemNameVersionFolder)):
        # corridor conditions 
        if pv(folder.split("_")[-1]) >= pv(systemVersionCorridorBase) and pv(folder.split("_")[-1]) <= pv(systemVersionCorridorMax):
            corridorList.append(folder)
    if corridorList == []:
        print(f"--ERROR: the corridorList is empty! Correct the corridor paramters!")
        return False
    else:
        systemVersionLatest = max(corridorList, key=find_latest_version)
        print(f"--INFO: The systemVersionLatest: {systemVersionLatest}")

        # CHECK: if the systemVersionLatest has reached systemVersionCorridorMax
        if pv(systemVersionLatest.split("_")[-1]) > pv(systemVersionCorridorMax):
            print(f"--ERROR: systemVersionLatest > max corridor value! Cannot increment further!")
            return False

        else:
        # Get the {APSName:apsLatestVersion} from the systemVersionLatest
            apsNameVersionMap = {}
            for apsName in os.listdir(os.path.join(masterData, systemNameVersionFolder, systemVersionLatest)):
                for apsVersion in os.listdir(os.path.join(masterData, systemNameVersionFolder, systemVersionLatest, apsName)):
                    if apsName not in apsNameVersionMap:
                        apsNameVersionMap[apsName] = [apsVersion]
                    else:
                        apsNameVersionMap[apsName].append(apsVersion)
            print(f"--INFO: Map APS name and versions within {systemVersionLatest}: \n {apsNameVersionMap}")
            # Get the latest from the apsNameVersionList
            apsNameVersionList = []
            for apsName in apsNameVersionMap:
                apsNameVersionList.append(max(apsNameVersionMap[apsName], key=find_latest_version))

        # Increment systemVersionLatest     
        # Getting systemVersionLatest major, minor, patch
        majorLatest = systemVersionLatest.split('_')[-1].split('.')[0]
        minorLatest = systemVersionLatest.split('_')[-1].split('.')[1]
        patchLatest = systemVersionLatest.split('_')[-1].split('.')[2] 

        if systemVersionIncPos == 'major':
            majorNew = str(int(majorLatest) + int(systemVersionInc))
            systemVersionNew = systemName + '_' + majorNew + '.' + minorLatest + '.' + patchLatest
            # Check if the new systemVersionNew is within the corridorMax and create systemVersionNew folder
            create_system_version_new(masterData, systemNameVersionFolder, systemVersionNew, systemVersionCorridorMax)
        if systemVersionIncPos == 'minor':
            minorNew = str(int(minorLatest) + int(systemVersionInc))
            systemVersionNew = systemName + '_' + majorLatest + '.' + minorNew + '.' + patchLatest
            # Check if the new systemVersionNew is within the corridorMax and create systemVersionNew folder
            create_system_version_new(masterData, systemNameVersionFolder, systemVersionNew, systemVersionCorridorMax)
        if systemVersionIncPos == 'patch':
            patchNew = str(int(patchLatest) + int(systemVersionInc))
            systemVersionNew = systemName + '_' + majorLatest + '.' + minorLatest + '.' + patchNew
            # Check if the new systemVersionNew is within the corridorMax and create systemVersionNew folder
            create_system_version_new(masterData, systemNameVersionFolder, systemVersionNew, systemVersionCorridorMax)
        
        # Increment apsVersionLatest
        for index, apsVersionLatest in enumerate(apsNameVersionList):
            # Getting apsVersionLatest major, minor, patch
            majorLatest = apsVersionLatest.split('_')[-1].split('.')[0]
            minorLatest = apsVersionLatest.split('_')[-1].split('.')[1]
            patchLatest = apsVersionLatest.split('_')[-1].split('.')[2]

            if apsVersionIncPosition == 'major':
                majorNew = str(int(apsVersionLatest.split('_')[-1].split('.')[0]) + int(apsVersionInc))
                apsVersionNew = apsVersionLatest.split('_')[0] + '_' + majorNew + '.' + minorLatest + '.' + patchLatest
                # Create apsName and apsVersion folder
                os.makedirs(os.path.join(masterData, systemNameVersionFolder, systemVersionNew, apsVersionLatest.split('_')[0], apsVersionNew))
                print(f"--PASS: {index+1}. Created apsVersionNew folder: {apsVersionNew}")
                # Copy the package folder from the apsVersionLatest to apsVersionNew
                copy_package(masterData, systemNameVersionFolder, systemVersionLatest, apsVersionLatest, systemVersionNew, apsVersionNew)

            if apsVersionIncPosition == 'minor':
                minorNew = str(int(apsVersionLatest.split('_')[-1].split('.')[1]) + int(apsVersionInc))
                apsVersionNew = apsVersionLatest.split('_')[0] + '_' + majorLatest + '.' + minorNew + '.' + patchLatest
                # Create apsName and apsVersion folder
                os.makedirs(os.path.join(masterData, systemNameVersionFolder, systemVersionNew, apsVersionLatest.split('_')[0], apsVersionNew))
                print(f"--PASS: {index+1}. Created apsVersionNew folder: {apsVersionNew}")
                # Copy the package folder from the apsVersionLatest to apsVersionNew
                copy_package(masterData, systemNameVersionFolder, systemVersionLatest, apsVersionLatest, systemVersionNew, apsVersionNew)

            if apsVersionIncPosition == 'patch':
                patchNew = str(int(apsVersionLatest.split('_')[-1].split('.')[2]) + int(apsVersionInc))
                apsVersionNew = apsVersionLatest.split('_')[0] + '_' + majorLatest + '.' + minorLatest + '.' + patchNew
                # Create apsName and apsVersion folder
                os.makedirs(os.path.join(masterData, systemNameVersionFolder, systemVersionNew, apsVersionLatest.split('_')[0], apsVersionNew))
                print(f"--PASS: {index+1}. Created apsVersionNew folder: {apsVersionNew}") 
                # Copy the package folder from the apsVersionLatest to apsVersionNew
                copy_package(masterData, systemNameVersionFolder, systemVersionLatest, apsVersionLatest, systemVersionNew, apsVersionNew)

    return True


if __name__ == "__main__":
    # read values from argparse
    parser = argparse.ArgumentParser(description='[INFO]: To know the system inputs type- "explicit -h" or "implicit -h" in CLI')

    if len(sys.argv) <=1 or '-h' in sys.argv[1] or '--help' in sys.argv[1]:
        parser.print_help()
        sys.exit()
    # check is cli contains '=', if yes then its explicit or else implicit
    if 'explicit' in sys.argv[0:] or '=' in sys.argv[3]:
        # Create a explicit subcommand    
        parser.set_defaults(func=explicit_folder)
        parser.add_argument('sn', help='system name')
        parser.add_argument('sv', help='system version')
        parser.add_argument('anv', nargs='*', help='Set a number of key-value pairs')
           # Explicit e.g: (3 mandatory inputs and 0 optionals)
            # $ System-C 1.0.0 APS-C=APS-C_0.0.1 APS-D=0.0.1

    else:
        if 'implicit' in sys.argv[0:] or '=' not in sys.argv[3]:
            # Create a implicit subcommand       
            parser.set_defaults(func=implicit_folder)
            parser.add_argument('sn', help= 'system name')
            parser.add_argument('svi', help= 'system version')
            parser.add_argument('svip', help= 'system version increment position')
            parser.add_argument('-avi', help= 'aps version increment')
            parser.add_argument('-avip', help= 'aps version increment position')
            parser.add_argument('-svcb', help= 'system version corridor base')
            parser.add_argument('-svcm', help= 'system version corridor max')
                # Implicit e.g: (3 mandatory inputs and 4 optionals)
                 # $ System-C 1 major -avi 1 -avip minor -svcb 0.0.0 -svcm 9.9.9

    args = parser.parse_args()
    args.func()

