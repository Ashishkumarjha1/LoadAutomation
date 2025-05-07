
# Latest code 31May2024
import subprocess
import pymysql
import datetime
import argparse
from datetime import datetime, timedelta
import time
import os
import re
from datetime import datetime

# create file for storing logs for testing


# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Execute SQL queries on a database.")
parser.add_argument("database", type=str,
                    help="Name of the database to execute queries on.")
parser.add_argument("cameralist", type=str,
                    help="Comma-separated list of cameras.")
parser.add_argument("runningtime", type=str, help="Time to run script")
parser.add_argument("maindbhost", type=str,
                    help="Host of the main database server")

args = parser.parse_args()
db_name = args.database
main_db_host = args.maindbhost
camera_name = args.cameralist
time_to_run = args.runningtime


# print(camera_name)
camera_name = camera_name[1:-1].split(',')
modified_indices_list = [item.strip() for item in camera_name]
# camera_name=camera_name[0]

interval = 5


# Set the constant part of the path
constant_path = "/home/allgovision/AGV/data/AllGoVision/ProgramData/"

# Here we are finding the starting time from INFO.txt file of any camera running
camPath = {}
starttime = -1
for directory in os.listdir(constant_path):
    # Check if the directory name contains the camera name
    if camera_name[0] in directory:
        # if camera_name[0] in directory:
        # If the directory name contains the camera name, construct the full path and print it
        path = os.path.join(constant_path, directory)
        camPath[camera_name[0]] = path

# with open(path+'/INFO.1.txt') as f:
#     infolines = f.readlines()

result = subprocess.run(
    ['file', '-i', path+'/INFO.1.txt'], stdout=subprocess.PIPE)
file_type = result.stdout.decode()
# Check if the file is binary or text
if 'charset=binary' in file_type or 'application/octet-stream' in file_type:
    # print("Reading as binary file...")
    # Read the binary file and decode it (assuming UTF-8 encoding, with error handling)
    with open(path+'/INFO.1.txt', 'rb') as f:
        # Handle decoding errors by replacing invalid chars
        infolines = f.read().decode('utf-8', errors='replace').splitlines()

else:
    # print("Reading as text file...")
    # Read the text file in normal mode
    with open(path+'/INFO.1.txt', 'r', encoding='utf-8', errors='replace') as f:
        infolines = f.readlines()

for i in range(len(infolines)):
    if 'INFO' in infolines[i].upper() and 'Initialize Analytics successful' in infolines[i+1]:
        oLineSplit = infolines[i].split("\n")[0].split("  ")
        iMemory = oLineSplit[0].split(".")[0]
        # print(iMemory)
        starttime = iMemory.split("[")[1]
        # print(type(timeStamp))
        break
# print("Start Time is: ",starttime)
# Convert starttime to datetime object
start_datetime = datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S")


# Calculate the endtime based on start_datetime and time_to_run
end_datetime = start_datetime + timedelta(seconds=int(time_to_run))


connection = pymysql.connect(host=main_db_host,
                             database=db_name,
                             user='root',
                             password='pass',
                             port=3306)
# print(datetime.now())
# print(end_datetime)

# Get the number of GPUs in machine
gpu_cmd = "nvidia-smi --query-gpu=count --format=csv,noheader,nounits | head -n 1"
gpu_result = subprocess.run(
    gpu_cmd, shell=True, capture_output=True, text=True)
# Check for errors
if gpu_result.returncode != 0:
    print("Error: ", gpu_result.stderr)
    exit()
# Extract and process the output
gpu_output = gpu_result.stdout.strip()  # Removing any extra spaces/newlines
gpu_count = int(gpu_output)


while datetime.now() <= end_datetime:

    timeStamp = "date +'%Y-%m-%d %H:%M:%S'"
    timestamp_result = subprocess.run(
        timeStamp, shell=True, capture_output=True, text=True)
    if timestamp_result.returncode != 0:
        print("Error: ", timestamp_result.stderr)
        exit()
    formatted_time = timestamp_result.stdout
    curr_time = formatted_time.splitlines()[0]
    d1 = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
    rel_time = d1-d2
    rel_time = str(rel_time)

    IPCmd = "hostname -I"
    IP_result = subprocess.run(
        IPCmd, shell=True, capture_output=True, text=True)
    if IP_result.returncode != 0:
        print("Error: ", IP_result.stderr)
        exit()
    IP_output = IP_result.stdout
    IP_lines = IP_output.split()

    server_ip = -1
    # serverip
    for i in range(len(IP_lines)):
        g = IP_lines[i].split('.')
        if (g[2] == '10'):
            # print(IP_lines[i])
            server_ip = str(IP_lines[i])
            break

    cpustatCmd = "docker stats --no-stream --format \"{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\""
    cpustatresult = subprocess.run(
        cpustatCmd, shell=True, capture_output=True, text=True)
    if cpustatresult.returncode != 0:
        print("Error: ", cpustatresult.stderr)
        exit()
    cpustats_output = cpustatresult.stdout
    cpustats_lines = cpustats_output.splitlines()

    oDockerConList = []
    for oLine in cpustats_lines:
        oLineSplit = oLine.split("\n")[0]
        oLineSplit = oLineSplit.split("\t")
        oContStr = oLineSplit[0]
        fCPUUsage = float(oLineSplit[1].split("%")[0])
        oMemUsageStr = (oLineSplit[2].split(" /")[0])
        fMemUsage = 0.0

        oMemUnitStr = "MiB"
        if "MiB" in oMemUsageStr:
            fMemUsage = float(oMemUsageStr.split("MiB")[0])
        elif "GiB" in oMemUsageStr:
            fMemUsage = float(oMemUsageStr.split("GiB")[0])
            fMemUsage = fMemUsage * 1024
            oMemUnitStr = "GiB"
        bAddedToList = False
        for i, oDocCont in enumerate(oDockerConList):
            if oDocCont["container_name"] == oContStr:
                oDockerConList[i]["cpu_percent"].append(fCPUUsage)
                oDockerConList[i]["cpu_mem"].append(fMemUsage)
                oDockerConList[i]["cpu_mem_unit"].append(oMemUnitStr)
                bAddedToList = True
                break
        if bAddedToList == False:
            oDockerConDict = {"container_name": oContStr,
                              "cpu_percent": [fCPUUsage],
                              "cpu_mem": [fMemUsage],
                              "cpu_mem_unit": oMemUnitStr}
            oDockerConList.append(oDockerConDict)

    # Iterate over the list of dictionaries
    oDockerConListSorted = sorted(
        oDockerConList, key=lambda x: x['container_name'])
    # print(oDockerConListSorted)
    cpuusagevalues = [formatted_time.split("\n")[0], rel_time, server_ip]
    cpumemoryvalues = [formatted_time.split("\n")[0], rel_time, server_ip]
    columns = ['TimeStamp', 'RelativeTime', 'ServerIP']
    for d in oDockerConListSorted:
        cpuusagevalues.append(d['cpu_percent'][0])
        cpumemoryvalues.append(d['cpu_mem'][0])
        columns.append(d['container_name'].replace("-", "_").replace(".", "_"))

    cursor = connection.cursor()

    cpuusagedata = list(zip(columns, cpuusagevalues))

    # Generate the INSERT query
    query = "INSERT INTO cpuusage ({}) VALUES ({})".format(
        ', '.join([row[0] for row in cpuusagedata]),
        ', '.join(['%s' for row in cpuusagedata])
    )
    # print(cpuusagedata)
    cursor.execute(query, [row[1] for row in cpuusagedata])
    connection.commit()

    cpumemoryusagedata = list(zip(columns, cpumemoryvalues))
    # Generate the INSERT query
    query = "INSERT INTO cpumemoryusage ({}) VALUES ({})".format(
        ', '.join([row[0] for row in cpumemoryusagedata]),
        ', '.join(['%s' for row in cpumemoryusagedata])
    )
    cursor.execute(query, [row[1] for row in cpumemoryusagedata])
    connection.commit()

    # commands to get gpustats
    temp_Cmd = "nvidia-smi -q -d temperature -i 0"
    temp_result = subprocess.run(
        temp_Cmd, shell=True, capture_output=True, text=True)
    if temp_result.returncode != 0:
        print("Error: ", temp_result.stderr)
        exit()
    temp_output = temp_result.stdout
    temp_lines = temp_output.splitlines()

    oCurrTempList = []
    iShutdownTemp = -1
    iSlowdownTemp = -1
    iMaxOpTemp = -1

    # temperature
    for oLine in range(len(temp_lines)):
        if "GPU Current Temp" in temp_lines[oLine]:
            oLineSplit = int(temp_lines[oLine].split(
                "\n")[0].split(": ")[1].split(" C")[0])
            oCurrTempList.append(oLineSplit)
            curr_temp = str(oLineSplit)
        elif "GPU Shutdown Temp" in temp_lines[oLine]:
            oLineSplit = int(temp_lines[oLine].split(
                "\n")[0].split(": ")[1].split(" C")[0])
            iShutdownTemp = oLineSplit
            b = iShutdownTemp
        elif "GPU Slowdown Temp" in temp_lines[oLine]:
            oLineSplit = int(temp_lines[oLine].split(
                "\n")[0].split(": ")[1].split(" C")[0])
            iSlowdownTemp = oLineSplit
            c = iSlowdownTemp

        elif "GPU Max Operating Temp" in temp_lines[oLine]:
            oLineSplit = int(temp_lines[oLine].split(
                "\n")[0].split(": ")[1].split(" C")[0])
            iMaxOpTemp = oLineSplit
            d = iMaxOpTemp

    timeStamp = "date +'%Y-%m-%d %H:%M:%S'"
    timestamp_result = subprocess.run(
        timeStamp, shell=True, capture_output=True, text=True)
    if timestamp_result.returncode != 0:
        print("Error: ", timestamp_result.stderr)
        exit()
    formatted_time = timestamp_result.stdout

    clockCmd = "nvidia-smi -q -d CLOCK -i 0"
    clock_result = subprocess.run(
        clockCmd, shell=True, capture_output=True, text=True)
    if clock_result.returncode != 0:
        print("Error: #", clock_result.stderr)
        exit()
    clock_output = clock_result.stdout
    clock_lines = clock_output.splitlines()

    # clock
    bMaxClocksDet = False
    bCurrClockDet = False
    iMaxClockMhz = -1
    oCurrClockMhz = []
    i_max_clock_mhz = -1
    graphics_curr_clock = -1
    for oLine in range(len(clock_lines)):
        if bMaxClocksDet == True:
            bMaxClocksDet = False
            if "Graphics" in clock_lines[oLine]:
                iLineVal = int(clock_lines[oLine].split("\n")[
                               0].split(": ")[1].split(" ")[0])
                iMaxClockMhz = iLineVal
                i_max_clock_mhz = iMaxClockMhz
        elif bCurrClockDet == True:
            bCurrClockDet = False
            if "Graphics" in clock_lines[oLine]:
                iLineVal = int(clock_lines[oLine].split("\n")[
                               0].split(": ")[1].split(" ")[0])
                graphics_curr_clock = iLineVal
                oCurrClockMhz.append(iLineVal)
        if "Max Clocks" in clock_lines[oLine]:
            bMaxClocksDet = True
        elif "Clocks" == clock_lines[oLine].replace(" ", "").split("\n")[0]:
            bCurrClockDet = True

    powerCmd = "nvidia-smi"  # it will give output for both gpu cards
    power_result = subprocess.run(
        powerCmd, shell=True, capture_output=True, text=True)
    if power_result.returncode != 0:
        print("Error: @", power_result.stderr)
        exit()
    power_output = power_result.stdout
    power_lines = power_output.splitlines()
    # power
    iMaxPower = -1
    oCurrPowList = []
    iMaxUsage = -1
    oCurrUsage = []
    curr_power = 0
    h = -1
    curr_usage = 0
    gpu_memory = 0

    for oLine in range(len(power_lines)):

        if ("MiB" in power_lines[oLine]) and ("W" in power_lines[oLine]) and ("C" in power_lines[oLine]):

            # Power
            oLineSplit = power_lines[oLine].split("\n")[0].split(" / ")
            iCurrPow = oLineSplit[0].split(" ")[-1].split("W")[0]
            # added the gpupower for both gpucards
            curr_power = curr_power+int(iCurrPow)

            oCurrPowList.append(int(iCurrPow))
            powerValue = oLineSplit[1].split("W")[0].strip()
            if "/" in powerValue:
                iMaxPow = powerValue.split("/")[-1].strip()
            else:
                iMaxPow = powerValue
            iMaxPower = int(iMaxPow) if iMaxPow else 0
            # Usage
            oLineSplit = power_lines[oLine].split("\n")[0]
            iCurrUsage = oLineSplit.split(" ")
            iCurrUsage = [c for c in iCurrUsage if c != ""][-3]

            iCurrUsage = int(iCurrUsage.split("%")[0])
            # add the current usage of two gpu cards
            curr_usage = curr_usage+int(iCurrUsage)

            oCurrUsage.append(int(iCurrUsage))
            if iCurrUsage > iMaxUsage:
                iMaxUsage = iCurrUsage
            # gpumemory
            oLineSplit = power_lines[oLine].split("\n")[0].split(" / ")
            # print(oLineSplit)
            iMemory = oLineSplit[1].split("MiB")[0]
            # print(iMemory)
            gpu_memory = gpu_memory+int(iMemory.split("|")[1].replace(" ", ""))

            oCurrPowList.append(int(iCurrPow))

    IPCmd = "hostname -I"
    IP_result = subprocess.run(
        IPCmd, shell=True, capture_output=True, text=True)
    if IP_result.returncode != 0:
        print("Error: ", IP_result.stderr)
        exit()
    ip_output = IP_result.stdout
    ip_lines = ip_output.split()

    server_ip = -1
    # serverip
    for i in range(len(ip_lines)):
        g = ip_lines[i].split('.')
        # print(g)
        if (g[2] == '10'):
            #    print(ip_lines[i])
            server_ip = str(ip_lines[i])
            break
    # taking average of curr_power,  curr_usage,gpu_memory
    curr_power = int(curr_power/gpu_count)
    curr_usage = int(curr_usage/gpu_count)
    gpu_memory = int(gpu_memory/gpu_count)
    # print(curr_power,curr_usage,gpu_memory)
    sql = "INSERT INTO gpustats (TimeStamp,RelativeTime,ServerIP,GraphicsCurrClock,CurrentTemp,CurrentPowerUsage,GPUUsagePerc,GPUMemory) VALUES (%s,%s ,%s,%s,%s,%s,%s,%s)"
    val = (formatted_time, rel_time, server_ip, graphics_curr_clock,
           curr_temp, curr_power, curr_usage, gpu_memory)
    cursor.execute(sql, val)
    connection.commit()

    time.sleep(interval)
