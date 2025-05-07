import subprocess
import os
import pymysql
import re
import platform

def get_linux_version():
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('VERSION_ID='):
                    version = line.split('=')[1].strip().strip('"')
                    version_int = int(float(version))  # Convert to float and then to int
                    return version_int
    except (FileNotFoundError, ValueError):
        return None

version = get_linux_version()
#print("Linux OS version:", version)


def connectDB(db_name,db_ip):
    #connect to database
    try:
        connection = pymysql.connect(host=db_ip,
                                                    database=db_name,
                                                    user='root',
                                                    password='pass',
                                                    port=3306)
        print("Successfully connected to database.")
        return connection
    except pymysql.Error as e:
        print(f"Failed to connect to database: {e}")
        return False

def getServerInfo(camList):
    #temperature
    iShutdownTemp = -1
    iSlowdownTemp = -1
    iMaxOpTemp = -1
    tempCmd = "nvidia-smi -q -d temperature -i 0"
    result = subprocess.run(tempCmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: ",result.stderr)
    else:
        tempOutput = result.stdout
        tempLines=tempOutput.splitlines()

        for oLine in range(len(tempLines)):
            if "GPU Shutdown Temp" in tempLines[oLine]:
                oLineSplit = int(tempLines[oLine].split("\n")[0].split(": ")[1].split(" C")[0])
                iShutdownTemp = oLineSplit

            elif "GPU Slowdown Temp" in tempLines[oLine]:
                oLineSplit = int(tempLines[oLine].split("\n")[0].split(": ")[1].split(" C")[0])
                iSlowdownTemp = oLineSplit

            elif "GPU Max Operating Temp" in tempLines[oLine]:
                oLineSplit = int(tempLines[oLine].split("\n")[0].split(": ")[1].split(" C")[0])
                iMaxOpTemp = oLineSplit

    #clock
    i_max_clock_mhz=-1
    clockCmd="nvidia-smi -q -d CLOCK -i 0"
    result = subprocess.run(clockCmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: ",result.stderr)
    else:
        clockOutput = result.stdout
        clockLines=clockOutput.splitlines()
        for oLine in range(len(clockLines)):
            if "Max Clocks" in clockLines[oLine]:
                if "Graphics" in clockLines[oLine+1]:
                    iLineVal = int(clockLines[oLine+1].split("\n")[0].split(": ")[1].split(" ")[0])
                    i_max_clock_mhz = iLineVal


    timeStamp = "date +'%Y-%m-%d %H:%M:%S'"
    result = subprocess.run(timeStamp, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: ",result.stderr)
    formatted_time = result.stdout


    #power
    iMaxPower = -1
    powerCmd="nvidia-smi -i 0"
    result = subprocess.run(powerCmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: ",result.stderr)
    else:
        powerOutput = result.stdout
        powerLines=powerOutput.splitlines()
        iMaxPower = -1
        for oLine in range(len(powerLines)):
            if ("MiB" in powerLines[oLine]) and ("W" in powerLines[oLine]) and ("C" in powerLines[oLine]):
                oLineSplit = powerLines[oLine].split("\n")[0].split(" / ")
                powerValue = oLineSplit[1].split("W")[0].strip()
                if "/" in powerValue:
                    iMaxPow = powerValue.split("/")[-1].strip()
                else:
                    iMaxPow = powerValue
                iMaxPower = int(iMaxPow) if iMaxPow else 0
                #print(type(iMaxPower))

        

    #serverip
    server_ip=-1
    ipCmd="hostname -I"
    result = subprocess.run(ipCmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: ",result.stderr)
    else:
        ipOutput = result.stdout
        ipList=ipOutput.split()
        server_ip=-1
        for i in range(len(ipList)):
            g=ipList[i].split('.')
            if(g[2]=='10'):
                server_ip=str(ipList[i])
                break

    #CPUCore info
    cores=-1
    modelName = ""
    cpuCmd="lscpu"
    result = subprocess.run(cpuCmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: ",result.stderr)
    else:
        cpuOutput = result.stdout
        cpuLines=cpuOutput.splitlines()
        for oLine in range(len(cpuLines)):
            if ("CPU(s):" in cpuLines[oLine] and cores == -1):
                splits=cpuLines[oLine].split(":")[-1]
                cores=int(splits)
            if ("Model name" in cpuLines[oLine]):
                modelName=cpuLines[oLine].split(":")[-1].lstrip()

    #RAM
    ram=-1
    ramCmd="free -h"
    result = subprocess.run(ramCmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: ",result.stderr)
    else:
        if version==18:
            ramOutput = result.stdout
            ramLines=ramOutput.splitlines()
            for i in range(len(ramLines)):
              if("Mem" in ramLines[i]):
                splits=ramLines[i].split("G")[0].split(":")[-1].lstrip()
                ram=float(splits)
                ram = ram * 1024
                break


        else:
            ramOutput = result.stdout
            ramLines=ramOutput.splitlines()
            for i in range(len(ramLines)):
              if("Mem" in ramLines[i]):
                splits=ramLines[i].split("Gi")[0].split(":")[-1].lstrip()
                ram=float(splits)
                
                break

    #gpuName
    gpuName = ""
    gpuNameCmd="nvidia-smi --query-gpu=name --format=csv,noheader"
    result = subprocess.run(gpuNameCmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: ",result.stderr)
    else:
        gpuName = result.stdout.split("\n")[0]

    storagestatus=1

    constant_path = "/home/allgovision/AGV/data/AllGoVision/ProgramData/"
    camConfigPath = []
    for camName in camList:
        # Loop through all directories in the constant path
        for directory in os.listdir(constant_path):
            # Check if the directory name contains the camera name
            if re.search(r'{}$'.format(re.escape(camName)), directory):
                # If the directory name contains the camera name,
                # construct the full path and append to path list
                configFile = camName + '.cfg'
                path = os.path.join(constant_path, directory,configFile)
                camConfigPath.append(path)

    all_features = set()
    # Regular expression pattern to match the analyticsFeaturesObject field
    pattern = r'analyticsFeaturesObject\s*=\s*(.*)'

    # Loop through each cam file
    for cam_file in camConfigPath:
        with open(cam_file, 'r') as f:
            config_lines = f.readlines()

            # Loop through each line in the current cam file
            for line in config_lines:
                match = re.search(pattern, line)

                if match:
                    feature = match.group(1)
                    all_features.add(feature)

    pattern1 = r"\b\d+\b"
    targetFPS = ""
    # Loop through each cam file
    for cam_file in camConfigPath:
        with open(cam_file, 'r') as f:
            config_lines = f.readlines()

            for line in config_lines:
                if "TargetFrameRate" in line and targetFPS == "":
                    targetFPS = re.findall(pattern1, line)

    # Convert the list of features to a comma-separated string
    features_string = ', '.join(all_features)



    return i_max_clock_mhz, iShutdownTemp, iSlowdownTemp, iMaxOpTemp, iMaxPower, storagestatus, cores, ram, gpuName, modelName, formatted_time, server_ip, features_string, targetFPS[0]


def addServerInfoToDB(db_name,camList,db_ip):

    connection = connectDB(db_name,db_ip)
    cursor = connection.cursor()
    if connection == False:
        return "connectionFailed"


    i_max_clock_mhz, iShutdownTemp, iSlowdownTemp, iMaxOpTemp, iMaxPower, storagestatus, cores, ram, gpuName, modelName, formatted_time, server_ip, features_string, targetFPS = getServerInfo(camList)
    # Check if the IP already exists in the table

    try:
        cursor.execute("SELECT COUNT(*) FROM serverinfo WHERE ServerIP=%s", (server_ip,))
        result = cursor.fetchone()

        if result[0] > 0:
            # IP already exists, update the row
            query = "UPDATE serverinfo SET GraphicsMaxClock=%s, ShutdownTemp=%s, SlowdownTemp=%s, MaxOperatingTemp=%s, GPUMaxPower=%s, Storagestatus=%s, CPUCores=%s, RAM=%s, GPUName=%s, ModelName=%s, Features=%s, TimeStamp=%s, TargetFPS=%s WHERE ServerIP=%s"
            cursor.execute(query, (i_max_clock_mhz, iShutdownTemp, iSlowdownTemp, iMaxOpTemp, iMaxPower, storagestatus, cores, ram, gpuName, modelName, features_string, formatted_time, targetFPS, server_ip))
            print("Server info updated")
        else:
            # IP does not exist, insert a new row
            query = "INSERT INTO serverinfo (ServerIP, GraphicsMaxClock, ShutdownTemp, SlowdownTemp, MaxOperatingTemp, GPUMaxPower, Storagestatus, CPUCores, RAM, GPUName, ModelName, Features, TargetFPS, TimeStamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE GraphicsMaxClock=%s, ShutdownTemp=%s, SlowdownTemp=%s, MaxOperatingTemp=%s, GPUMaxPower=%s, Storagestatus=%s, CPUCores=%s, RAM=%s, GPUName=%s, ModelName=%s, Features=%s, TargetFPS=%s, TimeStamp=%s"
            cursor.execute(query, (server_ip, i_max_clock_mhz, iShutdownTemp, iSlowdownTemp, iMaxOpTemp, iMaxPower, storagestatus, cores, ram, gpuName, modelName, features_string, targetFPS, formatted_time, i_max_clock_mhz, iShutdownTemp, iSlowdownTemp, iMaxOpTemp, iMaxPower, storagestatus, cores, ram, gpuName, modelName, features_string, targetFPS, formatted_time))
            print("Server is registered successfully.")

        # Commit the changes to the database
        connection.commit()
        connection.close()
        return "additionSuccess"
    except pymysql.Error as e:
        print(f"Failed to add serverinfo to database {db_name}: {e}")
        connection.rollback()
        connection.close()
        return "additionFailed"

