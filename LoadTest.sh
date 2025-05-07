#!/bin/bash
echo "Load Test Automation version: 1.3"

# Function to check if a command is installed
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if Ansible is installed
if ! command_exists ansible; then
  echo "Ansible is not installed."
  echo "Run ansible_sshpass_installation.sh with sudo."
  exit 1
fi

# Check if sshpass is installed
if ! command_exists sshpass; then
  echo "sshpass is not installed. Installing..."
  echo "Run ansible_sshpass_installation.sh with sudo."
  exit 1
fi

echo "Both Ansible and sshpass are installed."


# Prompt the user to enter the IP address
read -p "Enter the IP address for target machine: " ip_address

#Change if you want entries in different database
read -p "Enter the database IP address:(Make sure its running) " db_ip

# Define the server information using the entered IP address
server_info="[server1]
$ip_address ansible_connection=ssh ansible_ssh_user=allgovision ansible_ssh_pass=Vision@123"

# Write the server information to the serverinfo file
echo "$server_info" > serverinfo
# Prompt the user to enter the camera indices separated by commas
read -p "Enter the camera number for load testing (comma-separated) eg for LOAD1 enter 1 and so on or Enter in the format [Start-End] :" input
modified_indices=()
IFS=',' read -ra elements <<< "$input"

for element in "${elements[@]}"; do
  # Check if it is a range
  if [[ $element == \[*-*\] ]]; then
    range=${element#[}
    range=${range%]}
    start=${range%-*}
    end=${range#*-}
    
    for ((i=start; i<=end; i++)); do
        # Add the prefix "LOAD" to each index
        modified_index="LOAD$i"
        
        # Add the modified index to the array
        modified_indices+=("$modified_index")
    done
  else
    # Add the prefix "LOAD" to each index
    modified_index="LOAD$element"
    
    # Add the modified index to the array
    modified_indices+=("$modified_index")
  fi
done


echo "Camera Names:"
# echo $modified_indices
for modified_index in "${modified_indices[@]}"
do
    echo "$modified_index"
done

# Construct the modified indices as a comma-separated list enclosed in brackets
modified_indices_list=$(IFS=, ; echo "${modified_indices[*]}")
modified_indices_brackets="[$modified_indices_list]"
#echo $modified_indices_brackets
# Store the number of cameras in a variable
num_cameras=${#modified_indices[@]}


# Prompt the user to confirm if the cameras are already added and running
read -p "Are these cameras already added and running? (yes/no): " is_running
# Check if the cameras are already running
if [ "$is_running" = "no" ]; then
    echo "The cameras are not already running. Exiting the script."
    exit 0
fi

read -p "Enter the objects in the frame : " objects



# Prompt the user to enter the time to run in the format "M:S" (Minutes:Seconds)
read -p "Enter the time to run the load testing (in format M:S), (eg: for 1 min 30 secs, give 1:30) : " time_to_run

# Convert time to seconds
IFS=":" read -ra time_parts <<< "$time_to_run"
minutes=${time_parts[0]}
seconds=${time_parts[1]}
time_to_run=$((minutes * 60 + seconds))
echo $time_to_run



echo "Copying Python executables to the remote machine..."

#for database to excel

# Add the string "_cameras" to the num_cameras variable
num_cameras="cameras_${num_cameras}"


# Create backup file name with timestamp
now="$(date +'%d_%m_%Y_%H_%M_%S')"
database_name="LoadTest_${now}_${num_cameras}"

#Running ansible script
ansible-playbook -i serverinfo setup.yml --extra-vars "time_to_run=$time_to_run ip=$ip_address db_name='$database_name' modified_camera_names='$modified_indices_brackets' No_of_cameras=$num_cameras db_ip=$db_ip"

#Running Script to write to Excel sheet
./DBtoExcel "$database_name" "$ip_address" "$time_to_run" "$objects" "$db_ip"
