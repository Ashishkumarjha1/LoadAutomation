import pymysql
import datetime
import os
import subprocess
import re
import argparse
from datetime import datetime
from datetime import timedelta


# Parse command line arguments
parser = argparse.ArgumentParser(description="Execute SQL queries on a database.")
parser.add_argument("database", type=str, help="Name of the database to execute queries on.")
parser.add_argument("host", type=str, help="Host of the database server")
parser.add_argument("cameralist", type=str, help="Comma-separated list of cameras.")
parser.add_argument("runningtime", type=str, help="Time to run script")
parser.add_argument("maindbhost", type=str, help="Host of the main database server")

args = parser.parse_args()
db_name = args.database
db_host = args.host
main_db_host = args.maindbhost
camera_name=args.cameralist
time_to_run=args.runningtime
camera_name =camera_name[1:-1].split(',')



connection = pymysql.connect(host=db_host,
            database='allgovision',
            user='root',
            password='pass',
            port=3306)

connection2 = pymysql.connect(host=main_db_host,
            database=db_name,
            user='root',
            password='pass',
            port=3306)
constant_path = "/home/allgovision/AGV/data/AllGoVision/ProgramData/"
#camera_name = ["LOAD1","LOAD2","LOAD3","LOAD4","LOAD5"]
camPath = {}
starttime=-1
index=-1


cam1path=-1
cam1=camera_name[0]
for directory in os.listdir(constant_path):
      if cam1 in directory:
      # if cam1 in directory:
            # If the directory name contains the camera name, construct the full path and print it
            path = os.path.join(constant_path, directory)
            cam1path = path
if starttime == -1: #here we are storing starttime of camera
      # with open(path+'/INFO.1.txt') as f:
      #       infolines = f.readlines()
            
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
 for cam in camera_name:
      for directory in os.listdir(constant_path):  
            if re.search(r'{}$'.format(re.escape(cam)), directory):
                  # If the directory name contains the camera name, construct the full path and print it
                  path = os.path.join(constant_path, directory)
                  camPath[cam] = path  
      
      
      
      if starttime == -1: #here we are storing starttime of camera
            # with open(path+'/INFO.1.txt') as f:
            #       infolines = f.readlines()
            
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
     
      d2 = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
      #print(d2) #2023-03-15 14:51:05
      query='select TimeStamp,CamName,AlarmDescription,ObjectType,AgentRectangle from alarm where TimeStamp>=%s and CamName=%s'
      cursor = connection.cursor()
      cursor.execute(query,(str(d2),cam))
      result=cursor.fetchall()
      connection.commit()

      #here going through the every alarm
      for i in result:
            g=str(i[0])
            d1=datetime.strptime(g, "%Y-%m-%d %H:%M:%S")
            # print(d1)
            rel_time=d1-d2 
            rel_time=str(rel_time)
            q=str(i[4])
            #checking that the particular alarm is present in the alerts table or not based on bounding box
            
            query='select * from alerts where BoundingBox = %s' 
            cursor=connection2.cursor()
            cursor.execute(query,q)
            d=cursor.fetchall()
            connection2.commit()

            # if the alarm is not present in the alerts table then add it
            if d:  
                  continue
            else:     
                  query='Insert into alerts (TimeStamp,RelativeTime,CameraName,Feature,ObjectType,BoundingBox) VALUES(%s,%s,%s,%s,%s,%s)'
                  cursor=connection2.cursor()
                  cursor.execute(query,(i[0],rel_time,i[1],i[2],i[3],i[4]))
                  connection2.commit()