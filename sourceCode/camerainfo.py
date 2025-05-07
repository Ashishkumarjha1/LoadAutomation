#working with 5camera
import os
import re
import pymysql
import datetime
import argparse
import subprocess
from datetime import datetime
from datetime import timedelta

# Parse command line arguments
parser = argparse.ArgumentParser(description="Execute SQL queries on a database.")
parser.add_argument("database", type=str, help="Name of the database to execute queries on.")
parser.add_argument("cameralist", type=str, help="Comma-separated list of cameras.")
parser.add_argument("runningtime", type=str, help="Time to run script")
parser.add_argument("maindbhost", type=str, help="Host of the main database server")

args = parser.parse_args()
db_name = args.database
main_db_host = args.maindbhost
camera_name = args.cameralist  
time_to_run=args.runningtime
#print(camera_name)
camera_name =camera_name[1:-1].split(',')
modified_indices_list = [item.strip() for item in camera_name]
#print(type(camera_name))
#print("Modified Indices:", camera_name)
#print(camera_name[0])

connection = pymysql.connect(host=main_db_host,
                                            database=db_name,
                                            user='root',
                                            password='pass',
                                            port=3306)

# Set the constant part of the path
constant_path = "/home/allgovision/AGV/data/AllGoVision/ProgramData/"

# Set the camera name that you are searching for
#camera_name = ["LOAD1","LOAD2","LOAD3","LOAD4","LOAD5"]
camPath = {}
starttime=-1
index=-1
update = [-1 for i in range(len(camera_name))]
# update=[-1,-1,-1,-1,-1]  #here we are keeping update of line numbers till where we have reached in files of all cameras

cam1path=-1
cam1=camera_name[0]
for directory in os.listdir(constant_path):  
    if cam1 in directory:
        # If the directory name contains the camera name, construct the full path and print it
        path = os.path.join(constant_path, directory)
        cam1path = path
if starttime == -1: #here we are storing starttime of camera
    result = subprocess.run(['file', '-i', path+'/INFO.1.txt'], stdout=subprocess.PIPE)
    file_type = result.stdout.decode()
    # Check if the file is binary or text
    if 'charset=binary' in file_type or 'application/octet-stream' in file_type:
        #print("Reading as binary file...")
        # Read the binary file and decode it (assuming UTF-8 encoding, with error handling)
        with open(path+'/INFO.1.txt', 'rb') as f:
            infolines = f.read().decode('utf-8', errors='replace').splitlines()  # Handle decoding errors by replacing invalid chars
    else:
        #print("Reading as text file...")
        # Read the text file in normal mode
        with open(path+'/INFO.1.txt', 'r', encoding='utf-8', errors='replace') as f:
            infolines = f.readlines()
    
        
    #getting the starttime of the cameras
    for i in range(len(infolines)):
        if 'INFO' in infolines[i].upper()  and 'Initialize Analytics successful' in infolines[i+1]:
            oLineSplit = infolines[i].split("\n")[0].split("  ")
            iMemory = oLineSplit[0].split(".")[0]
            starttime= iMemory.split("[")[1]
            break
# Convert starttime to datetime object
start_datetime = datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S")

# Calculate the endtime based on start_datetime and time_to_run
end_datetime = start_datetime + timedelta(seconds=int(time_to_run))

starttime=-1
while datetime.now() <= end_datetime:

    for e in range(len(camera_name)):
        # Loop through all directories in the constant path
        for directory in os.listdir(constant_path):
            # Check if the directory name contains the camera name
            if re.search(r'{}$'.format(re.escape(camera_name[e])), directory):
            # if camera_name[e] in directory:
                # If the directory name contains the camera name, construct the full path and print it
                path = os.path.join(constant_path, directory)
                camPath[camera_name[e]] = path

        if starttime == -1: #here we are storing starttime of camera
            result = subprocess.run(['file', '-i', path+'/INFO.1.txt'], stdout=subprocess.PIPE)
            file_type = result.stdout.decode()
            # Check if the file is binary or text
            if 'charset=binary' in file_type or 'application/octet-stream' in file_type:
                #print("Reading as binary file...")
                # Read the binary file and decode it (assuming UTF-8 encoding, with error handling)
                with open(path+'/INFO.1.txt', 'rb') as f:
                    infolines = f.read().decode('utf-8', errors='replace').splitlines()  # Handle decoding errors by replacing invalid chars
            else:
                #print("Reading as text file...")
                # Read the text file in normal mode
                with open(path+'/INFO.1.txt', 'r', encoding='utf-8', errors='replace') as f:
                    infolines = f.readlines()
            
            for i in range(len(infolines)):
                if 'INFO' in infolines[i].upper()  and 'Initialize Analytics successful' in infolines[i+1]:
                    oLineSplit = infolines[i].split("\n")[0].split("  ")
                    iMemory = oLineSplit[0].split(".")[0]
                    #print(iMemory)
                    starttime= iMemory.split("[")[1]
                    #print(type(timeStamp))
                    break
            # print("Start Time is: ",starttime)


        encodedf=-1
        decodedf=-1
        inputFps=-1
        outputFps=-1

        
            
        result = subprocess.run(['file', '-i', path+'/INFO.1.txt'], stdout=subprocess.PIPE)
        file_type = result.stdout.decode()
        # Check if the file is binary or text
        if 'charset=binary' in file_type or 'application/octet-stream' in file_type:
            #print("Reading as binary file...")
            # Read the binary file and decode it (assuming UTF-8 encoding, with error handling)
            with open(path+'/INFO.1.txt', 'rb') as f:
                infolines = f.read().decode('utf-8', errors='replace').splitlines()  # Handle decoding errors by replacing invalid chars
        else:
            #print("Reading as text file...")
            # Read the text file in normal mode
            with open(path+'/INFO.1.txt', 'r', encoding='utf-8', errors='replace') as f:
                infolines = f.readlines()    

        for i in range(len(infolines)): #here we are going through the file in loop and finding the inputfps,outputfps and timestamp
            if 'Input fps' in infolines[i] and 'Output fps' in infolines[i]:
                oLineSplit = infolines[i].split("I")[-1]
                ol=infolines[i].split("I")[0]
                ol1=ol.split(".")[0]
                time_stamp=ol1.split("[")[-1]
                d1=datetime.strptime(time_stamp, "%Y-%m-%d %H:%M:%S")
                d2 = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
                rel_time=d1-d2
                rel_time=str(rel_time)
                g=oLineSplit.split(" ")
                inputFps=g[3]
                inputFps=inputFps.split(";")[0]
                outputFps=g[7]
                inputFps=float(inputFps)
                outputFps=float(outputFps)
            
                #print(type(timeStamp))
                if(i>update[e]): #here we are checking the last line of file where we have reached for particular camera
                  query='Insert into camerainfo (TimeStamp,RelativeTime,CameraName,InputFPS,OutputFPS,EnqueuedFrames,DecodedFrames) VALUES (%s,%s,%s,%s, %s,%s,%s)'
                  cursor=connection.cursor()
                  cursor.execute(query,(time_stamp,rel_time,camera_name[e],inputFps,outputFps,encodedf,decodedf))
                  connection.commit()   
                  update[e]=i