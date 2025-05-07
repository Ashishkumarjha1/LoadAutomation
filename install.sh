#!/bin/bash


# Check if the correct number of command-line arguments was provided
if [ $# -ne 6 ]; then
  echo "Usage: bash $0 <database_name> <ip_address> <camera_list> <No_of_cameras> <time_to_run> <db_ip>"
  exit 1
fi

# Extract command-line arguments
database_name="$1"
ip_address=$2
camera_list=$3
num_cameras=$4
time_to_run=$5
db_ip=$6

# Add the string "_cameras" to the num_cameras variable
num_cameras="cameras_${num_cameras}"




# Create backup file name with timestamp
now="$(date +'%d_%m_%Y_%H_%M_%S')"
#database_name="${1}_${now}_${num_cameras}"
# echo $database_name

# run all scripts parallelly 
cd /home/allgovision/LoadTest_Scripts
./main $database_name $camera_list $db_ip> main.log
#usr/bin/python3 /home/allgovision/LoadTest_Scripts/main.py $database_name $camera_list

./cpugpustats $database_name $camera_list $time_to_run $db_ip> cpugpustats.log &
./camerainfo $database_name $camera_list $time_to_run $db_ip> camerainfo.log &
./alerts $database_name $ip_address $camera_list $time_to_run $db_ip> alerts.log &
./decoderService $database_name $time_to_run $db_ip> decoder.log &

wait

# Define the path to the directory where the files should be copied
destination_dir="/home/allgovision/LoadTest_Scripts/$database_name"

# Define the list of elements to match in the filenames
elements=$camera_list

# Remove square brackets and quotes from elements string
elements=$(echo "$elements" | sed 's/\[//; s/\]//; s/"//g')

# Convert elements string to an array
IFS=',' read -ra elements_array <<< "$elements"

# Create the destination directory if it doesn't exist
mkdir -p "$destination_dir"

#Copying logs to directory with database name
# Loop through files in the specified path
for file in /home/allgovision/AGV/data/AllGoVision/ProgramData/*; do
    # Extract the filename from the full file path
    filename=$(basename "$file")
    # echo $filename
    # Loop through the elements to match
    for element in "${elements_array[@]}"; do
        # Extract the element from the filename
        extracted_element=$(echo "$filename" | awk -F "_" '{print $NF}')
        if [[ "$extracted_element" == "$element" ]]; then
            # Copy the file to the destination directory
            cp -r "$file" "$destination_dir"
            break
        fi
    done
done

#Copying Decoder Service logs

source_dir="/home/allgovision/DS/video_decoder_service/decode_service/n0/"

# Check if the source directory exists
if [ ! -d "$source_dir" ]; then
    echo "Decoder Service directory does not exist: $source_dir"
    exit 1
fi

# Copy the directory and handle errors
if ! cp -r "$source_dir" "$destination_dir"; then
    echo "Error occurred while copying Decoder Service logs."
    exit 1
fi
# cp -r /home/allgovision/DS/video_decoder_service/decode_service/n0/ "$destination_dir"
