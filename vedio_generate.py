#!/usr/bin/env python3
import os
import re
from pathlib import Path
import subprocess

# 1. Specify the image directory and output list file
search_dir = "G:/db1/VFHQ"  # Only search for images under the VFHQ directory
output_file = "G:/db1/VFHQ/filelist.txt"
ffmpeg_path = "ffmpeg"
filelist = "G:/db1/VFHQ/filelist.txt"
output_video = "G:/db1/VFHQ/output.mp4"

# 2. Define a function to extract numbers from file paths for sorting
# For example, extract ('folder_A', 0.001) from './folder_A/0.001.jpg'
def get_sort_key(filepath):
    path = Path(filepath)
    folder_name = path.parent.name
    file_name = path.name

    # Try to convert folder_name to int for numeric sorting
    try:
        folder_num = int(folder_name)
    except ValueError:
        folder_num = float('inf')  # Non-numeric folders go last

    match = re.search(r'(\\d+\\.\\d+)|\\d+', file_name)
    if match:
        number = float(match.group())
    else:
        number = 0
    return (folder_num, number)

# 3. Recursively find all png files
jpg_files = []
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            full_path = os.path.abspath(os.path.join(root, file))  # Use absolute path
            jpg_files.append(full_path)

# 4. Sort by custom key: first by folder name, then by number in file name
# If you want to customize folder order, you can define a mapping here
# folder_order = {'folder_A': 1, 'folder_B': 2, 'folder_C': 3}
# Then the sort key can be: key=lambda x: (folder_order.get(Path(x).parent.name, 99), get_sort_key(x)[1])
jpg_files_sorted = sorted(jpg_files, key=get_sort_key)

# 5. Write the sorted file list to a text file
with open(output_file, 'w') as f:
    for file_path in jpg_files_sorted:
        file_path = file_path.replace("\\", "/")  # Key: use forward slash
        f.write(f"file '{file_path}'\n")  # FFmpeg concat protocol requires absolute path for stability
        f.write("duration 0.04\n")  # each image show 0.04s = 25fps

print(f"File list generated: {output_file} with {len(jpg_files_sorted)} images.")

cmd = [
    ffmpeg_path,
    "-f", "concat",
    "-safe", "0",
    "-i", filelist,
    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
    "-pix_fmt", "yuv420p",
    "-r", "25",
    output_video
]

subprocess.run(cmd, check=True)
print("Video generation completed!")