#final working with real times
import subprocess

directory = "/home/allgovision/AGV/data/AllGoVision/ProgramData"

# Execute the shell command and capture the output
command = f"ls {directory} | grep LOAD"
output_bytes = subprocess.check_output(command, shell=True)
output = output_bytes.decode('utf-8')


# Split the output by lines and store it in a list
output_list = output.splitlines()

# Print the list
#print(output_list)
# Extract the desired values from the output
desired_values_list = [item.split('_')[0] for item in output_list]
#desired_values_list=['819171C0-05BB-11EE-AE14-11ED779CE9E5', '8556DE30-05BB-11EE-AE14-11ED779CE9E5', '8885AFF0-05BB-11EE-AE14-11ED779CE9E5', '8BF05230-05BB-11EE-AE14-11ED779CE9E5', '8FA67C60-05BB-11EE-AE14-11ED779CE9E5']  #for now 
# Print the list of desired values
#print(desired_values_list)


from datetime import datetime
import pymysql
import numpy as np
import argparse
from datetime import datetime, timedelta
from openpyxl import load_workbook
import os
# Open the log file in read mode
pkt_count = 0
i=0
j=0
timestamp_list=[]
cam_list=[]
pkt_list=[]
avg_decode_list=[]
avg_fps_list=[]


cam_name=""
hardware=""
avg_cpu_decode=0.0
avg_gpu_decode=0.0
avg_cpu_decode_fps=0.0
avg_gpu_decode_fps=0.0
timestamp=""
last_line=-1
data={}
flag=0


parser = argparse.ArgumentParser(description="Execute SQL queries on a database.")
parser.add_argument("database", type=str, help="Name of the database to execute queries on.")
parser.add_argument("runningtime", type=str, help="Time to run script")
parser.add_argument("maindbhost", type=str, help="Host of the main database server")

args = parser.parse_args()
db_name = args.database
time_to_run=args.runningtime
main_db_host = args.maindbhost

# Connect to the database
try:
    conn = pymysql.connect(
        host=main_db_host,
        user='root',
        password='pass',
        db=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
except pymysql.Error as e:
    print(f"Error connecting to database: {e}")
    # Set the constant part of the path
constant_path = "/home/allgovision/DS/video_decoder_service/decode_service/n0/"
starttime=-1
for directorys in os.listdir(directory):
    # Check if the directory name contains the camera name
    if 'LOAD' in directorys:
    # if camera_name[0] in directory:
        # If the directory name contains the camera name, construct the full path and print it
        path = os.path.join(directory, directorys)

# with open(path+'/INFO.1.txt') as f:
#     infolines = f.readlines()
result = subprocess.run(['file', '-i', path+'/INFO.1.txt'], stdout=subprocess.PIPE)
file_type = result.stdout.decode()
# Check if the file is binary or text
if 'charset=binary' in file_type or 'application/octet-stream' in file_type:
    print("Reading as binary file...")
    # Read the binary file and decode it (assuming UTF-8 encoding, with error handling)
    with open(path+'/INFO.1.txt', 'rb') as f:
        infolines = f.read().decode('utf-8', errors='replace').splitlines()  # Handle decoding errors by replacing invalid chars
else:
    print("Reading as text file...")
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
# Convert starttime to datetime object
start_datetime = datetime.strptime(str(starttime), "%Y-%m-%d %H:%M:%S")


# Calculate the endtime based on start_datetime and time_to_run
end_datetime = start_datetime + timedelta(seconds=int(time_to_run))

while(datetime.now()<end_datetime):
   
    result = subprocess.run(['file', '-i', path+'/INFO.1.txt'], stdout=subprocess.PIPE)
    file_type = result.stdout.decode()
    # Check if the file is binary or text
    if 'charset=binary' in file_type or 'application/octet-stream' in file_type:
        #print("Reading as binary file...")
        # Read the binary file and decode it (assuming UTF-8 encoding, with error handling)
        with open(constant_path+'/INFO.1.txt', 'rb') as f:
            infolines = f.read().decode('utf-8', errors='replace').splitlines()  # Handle decoding errors by replacing invalid chars
    else:
        #print("Reading as text file...")
        # Read the text file in normal mode
        with open(constant_path+'/INFO.1.txt', 'r', encoding='utf-8', errors='replace') as f:
            infolines = f.readlines() 
    update=-1 
   
    
#    with open(constant_path+'INFO.1.txt') as f:
#     update=-1
#     infolines = f.readlines()
    #print(infolines)
    #print(len(infolines))
    
    for line in infolines:
     #print(line)
     update=update+1
     if(update>last_line):
      if "decoding on" in line:
           hardware=line.split("decoding on ")[1].split(" ")[0]
           #print(hardware)
           data["hardware"]=hardware
           last_line=update
           continue
     #if(update>last_line):
      #last_line=update 
      #update=update+1
      last_line=update      
      if "channel_identifier" in line:  
        #print(line)
        #j=j+1
         if "pkt_count:" in line and ", pkt_CPU_FPS:" in line:
                    #print(line)
                    w=line.split("pkt_count:")[0].split()
                    cam_name=w[3]
                    #print(cam_name)
                    cam_list.append(cam_name)
                    pkt_count = int(line.split("pkt_count:")[1].split()[0].replace(',', ''))
                    timestamp = line.split("[")[1].split("]")[0]
                    timestamp=timestamp.split(".")[0]
                    #Convert starttime to datetime object
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    data["timestamp"]=timestamp
                    data["pkt_count"]=pkt_count
                    timestamp_list.append(timestamp)
                    pkt_list.append(pkt_count)
                    #i=i+1
                    flag=1
         if "pkt_count:" in line and flag==0:
                    #print(line)
                    w=line.split("pkt_count:")[0].split()
                    cam_name=w[3]
                    #print(cam_name)
                    cam_list.append(cam_name)
                    pkt_count = int(line.split("pkt_count:")[1].split()[0])
                    timestamp = line.split("[")[1].split("]")[0]
                    timestamp=timestamp.split(".")[0]
                    #Convert starttime to datetime object
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    data["timestamp"]=timestamp
                    data["pkt_count"]=pkt_count
                    timestamp_list.append(timestamp)
                    pkt_list.append(pkt_count)
                    #i=i+1
                               

         if "avg_cpu_decode_ms" in line:
                    #hardware="cpu"
                    avg_cpu_decode=float(line.split("avg_cpu_decode_ms: ")[1].split(" ")[0])
                    data["avg_cpu_decode"]=avg_cpu_decode
                    avg_decode_list.append(avg_cpu_decode)
                    #print(hardware)  
                    #i=i+1
         if "avg_gpu_decode_ms:"in line:
                    avg_gpu_decode=float(line.split("avg_gpu_decode_ms: ")[1].split(" ")[0])
                    #print("avg_gpu_decode")
                    #print(avg_gpu_decode)
                    avg_decode_list.append(avg_gpu_decode)
                    #i=i+1

         if "Decode_CPU_FPS" in line:
                    avg_decode_fps=float(line.split("Decode_CPU_FPS: ")[1].split(",")[0])
                    #print("avg_decode_fps")
                    #print(avg_decode_fps)    
                    w=line.split("frame_count_de:")[0].split()
                    cam_name=w[3]
                    hardware="cpu"
                    #print(cam_name)
                    if cam_name in desired_values_list:    
                     avg_fps_list.append(avg_decode_fps)
                     index = cam_list.index(cam_name)
                     #print(index)
                     #i=i+1 
                     query='Insert into decoderserviceinfo (TimeStamp,PktCount,CameraName,HardwareType,AvgDecodeTime,AvgDecodeFPS) VALUES (%s,%s,%s,%s, %s,%s)'
                     cursor=conn.cursor()
                     cursor.execute(query,(timestamp_list[index],pkt_list[index],cam_list[index],hardware,avg_decode_list[index],avg_fps_list[0]))
                     conn.commit()
                     i=0 
                     timestamp_list.pop()
                     pkt_list.pop(index)
                     cam_list.pop(index)
                     avg_decode_list.pop(index)
                     avg_fps_list.pop(0) 

         if "Decode_GPU_FPS:" in line:
                    
                    avg_decode_fps=float(line.split("Decode_GPU_FPS: ")[1].split(",")[0])
                    #print("avg_decode_fps")
                    #print(avg_decode_fps)    
                    w=line.split("frame_count_de:")[0].split()
                    cam_name=w[3]
                    hardware="gpu"
                    #print(cam_name)
                    if cam_name in desired_values_list:    
                     avg_fps_list.append(avg_decode_fps)
                     index = cam_list.index(cam_name)
                     #print(index)
                     #i=i+1 
                     query='Insert into decoderserviceinfo (TimeStamp,PktCount,CameraName,HardwareType,AvgDecodeTime,AvgDecodeFPS) VALUES (%s,%s,%s,%s, %s,%s)'
                     cursor=conn.cursor()
                     cursor.execute(query,(timestamp_list[index],pkt_list[index],cam_list[index],hardware,avg_decode_list[index],avg_fps_list[0]))
                     conn.commit()
                     i=0 
                     timestamp_list.pop()
                     pkt_list.pop(index)
                     cam_list.pop(index)
                     avg_decode_list.pop(index)
                     avg_fps_list.pop(0)   
         flag=0
