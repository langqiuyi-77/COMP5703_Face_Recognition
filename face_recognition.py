import cv2
import pickle
import numpy as np
from deepface import DeepFace
import os
import tensorflow as tf
from datetime import datetime
import time
import argparse
import json
import yaml
from kafka import KafkaProducer
import threading

parser = argparse.ArgumentParser(description="Face recognition on video using a face database.")
parser.add_argument('--config', type=str, required=True, help='Path to YAML config file')
args = parser.parse_args()

# Load YAML config
with open(args.config, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

KAFKA_TOPIC = 'Log'
MODEL = "ArcFace"
DIST_METRIC = "euclidean_l2"
THRESHOLD = 1.24
SKIP = 10

# Check the number of available GPUs
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Load feature database (shared)
with open(config["db_file"], "rb") as f:
    face_db = pickle.load(f)

def l2_normalize(x):
    x = np.array(x)
    return x / np.linalg.norm(x)

def process_video(video_path, direction_label):
    # TODO: Change to your actual IP
    producer = KafkaProducer(bootstrap_servers='100.102.165.57:29092')
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    last_seen = {direction_label: None}  # last_seen is per video stream, records last recognized person for this direction
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % SKIP == 0:
            start_time = time.time()
            try:
                results = DeepFace.extract_faces(
                    img_path=frame,
                    detector_backend="retinaface",
                    enforce_detection=False,
                    align=False
                )
                for face in results:
                    region = face["region"] if "region" in face else face["facial_area"]
                    x, y, w, h = region["x"], region["y"], region["w"], region["h"]
                    face_img = frame[y:y+h, x:x+w]
                    try:
                        target_repr = DeepFace.represent(
                            img_path=face_img,
                            model_name=MODEL,
                            enforce_detection=False,
                            detector_backend="retinaface"
                        )[0]["embedding"]
                        target_repr = l2_normalize(target_repr)
                    except Exception:
                        continue
                    min_dist = float("inf")
                    name = "Unknown"
                    for item in face_db:
                        db_repr = l2_normalize(item["embedding"])
                        db_name = os.path.basename(os.path.dirname(item["img_path"]))
                        dist = np.linalg.norm(target_repr - db_repr)
                        if dist < min_dist:
                            min_dist = dist
                            name = db_name
                    # Only log and print when a new person is recognized (different from last_seen)
                    if name != last_seen.get(direction_label):
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[{now}] Detected: {name}, Frame: {frame_idx}, Position: ({x},{y},{w},{h}), Direction: {direction_label}")
                        log_msg = {
                            "person": name,
                            "video": video_path,
                            "frame": frame_idx,
                            "timestamp": now,
                            "bbox": {"x": x, "y": y, "w": w, "h": h},
                            "recognition_time": round(time.time() - start_time, 2),
                            "direction": direction_label
                        }
                        producer.send(KAFKA_TOPIC, json.dumps(log_msg).encode('utf-8'))
                        last_seen[direction_label] = name
                elapsed = time.time() - start_time
                print(f"Frame {frame_idx} recognition time: {elapsed:.2f} seconds [{direction_label}]")
            except Exception as e:
                print(f"Error: {e}")
        frame_idx += 1
    cap.release()
    producer.close()

threads = []
for video_cfg in config["videos"]:
    t = threading.Thread(target=process_video, args=(video_cfg["path"], video_cfg["direction"]))
    t.start()
    threads.append(t)
for t in threads:
    t.join()
