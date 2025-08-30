#!/usr/bin/env python3
import os
import glob
import random

# Root directory path (change this to your dataset root)
root_dir = r"D:/Share/01 Comp5703 Web CapStone/VFHQ"

# Number of images to keep in each subfolder
keep_num = 5

# Whether to select randomly (True) or keep the first N images after sorting (False)
random_select = False

for subdir, dirs, files in os.walk(root_dir):
    # Skip the root folder itself, only process subfolders
    if subdir == root_dir:
        continue

    # Collect all image files in this subfolder
    images = []
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        images.extend(glob.glob(os.path.join(subdir, ext)))

    if len(images) <= keep_num:
        print(f"{subdir} has only {len(images)} images, nothing deleted.")
        continue

    # Select which images to keep
    if random_select:
        keep_files = set(random.sample(images, keep_num))
    else:
        keep_files = set(sorted(images)[:keep_num])

    # Delete all other images
    delete_count = 0
    for img in images:
        if img not in keep_files:
            os.remove(img)
            delete_count += 1

    print(f"{subdir}: kept {keep_num}, deleted {delete_count}.")

print("Done")
