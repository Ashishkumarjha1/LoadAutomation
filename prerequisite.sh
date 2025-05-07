# Prompt the user to confirm if the cameras are already added and running
read -p "Are all cameras analytics stopped? (yes/no): " answer
# Check if the cameras are already running
if [ "$answer" = "no" ]; then
    echo "Stop analytics. Exiting the script."
    exit 0
fi

#remove all logs
rm -r /home/allgovision/AGV/data/AllGoVision/ProgramData/*LOAD*
rm /home/allgovision/DS/video_decoder_service/decode_service/n0/*
rm /home/allgovision/DS/video_decoder_service/decode_service/n1/*

# Set the path to the JSON file
json_file0="/home/allgovision/DS/video_decoder_service/decode_service/decode_service_init_n0.json"
json_file1="/home/allgovision/DS/video_decoder_service/decode_service/decode_service_init_n1.json"

# Set the new value for the "debug_mode" field
new_debug_value=3

# Use sed to update the "debug_mode" field in the JSON file
sed -i 's/"debug_mode": [0-9]*/"debug_mode": '$new_debug_value'/' "$json_file0"

# Use sed to update the "debug_mode" field in the JSON file
sed -i 's/"debug_mode": [0-9]*/"debug_mode": '$new_debug_value'/' "$json_file1"

docker restart decode_service

echo "!!!!!!!!!!!!IGNORE NO SUCH FILE OR DIRECTORY ERRORS!!!!!!!!!!!!"