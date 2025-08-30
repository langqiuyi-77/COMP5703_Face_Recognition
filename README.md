# Face Recognition Project

This project provides scripts for building a face feature database from images and running face recognition on videos using DeepFace.

## Requirements
- Python 3.10.18
- Install dependencies:
  ```bash
  pip install deepface opencv-python numpy tensorflow
  ```

## Usage

### 1. Build a Face Database
Generate a feature database (pkl file) from a folder of images:

```bash
python build_face_db.py --db_path ./YTFace --output ytface_db.pkl
python build_face_db.py --db_path ./VFHQ --output vfhq_db.pkl
```
- `--db_path`: Path to the folder containing images (jpg, jpeg, png)
- `--output`: Output pickle file name

### 2. Run Face Recognition on a Video
Run face recognition using a video and a database:

```bash
python face_recognition.py --video ./YTFace/output.mp4 --db_file ytface_db.pkl
python face_recognition.py --video ./VFHQ/output.mp4 --db_file vfhq_db.pkl
```
- `--video`: Path to the video file
- `--db_file`: Path to the face database pickle file

![tip](tip.gif)

### 3. Example Datasets
- Place your datasets (image folders) in the project directory, e.g., `people/`, `VFHQ/`, etc.
- Place your videos in the project directory or subfolders.

## Notes
- The `.pkl` files (face databases) are generated and can be large. You may choose **not** to upload them to git, as teammates can regenerate them from the datasets.
- Datasets (image folders) **should** be uploaded if you want teammates to reproduce results.


---

Feel free to modify the scripts for your own datasets and experiments.
