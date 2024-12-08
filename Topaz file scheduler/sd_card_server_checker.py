import os

# Path to the SD card directory and the server file list
sd_card_path = "/Volumes/EOS_DIGITAL/DCIM/100CANON"
server_file_list_path = "/Users/king/Documents/GitHub/Scripts/Topaz file scheduler/filelist.txt"

# Read server file list
with open(server_file_list_path, 'r') as f:
    server_files = f.read().splitlines()

# Get list of files from SD card
sd_card_files = []
for root, dirs, files in os.walk(sd_card_path):
    for file in files:
        if not file.endswith('.CR2'):  # Exclude .CR2 files
            # Create relative path similar to how server files are listed
            relative_path = os.path.relpath(os.path.join(root, file), sd_card_path)
            sd_card_files.append(f'./{relative_path}')

# Find files on the SD card that are not in the server file list
missing_from_server = [file for file in sd_card_files if file not in server_files]

# Print files missing from the server file list
if missing_from_server:
    print("Files on the SD card (except .CR2) not found on the server:")
    for file in missing_from_server:
        print(file)
else:
    print("All files from the SD card are present on the server (excluding .CR2 files).")
