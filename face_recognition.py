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
from kafka import KafkaProducer

parser = argparse.ArgumentParser(description="Face recognition on video using a face database.")
parser.add_argument('--video', type=str, default="./VFHQ/output.mp4", help='Path to the video file')
parser.add_argument('--db_file', type=str, default="face_db.pkl", help='Path to the face database pickle file')

args = parser.parse_args()

# Setup Kafka producer
# TODO: Change to your actual IP, do NOT use localhost
producer = KafkaProducer(bootstrap_servers='100.102.164.179:29092')
KAFKA_TOPIC = 'Log'

MODEL = "ArcFace"
DIST_METRIC = "euclidean_l2"
THRESHOLD = 1.24
SKIP = 10

# Check the number of available GPUs
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))


# Load feature database
with open(args.db_file, "rb") as f:
    face_db = pickle.load(f)

# cap = cv2.VideoCapture("rtsp://username:password@IP:554/stream")
cap = cv2.VideoCapture(args.video)
frame_idx = 0

def l2_normalize(x):
    x = np.array(x)
    return x / np.linalg.norm(x)

last_seen = {}  # Record the last frame number each person appeared
LOG_INTERVAL = SKIP * 2  # If not seen for more than this many frames, count as "newly appeared"


while True:
    ret, frame = cap.read()
    if not ret:
        break

    display_frame = frame.copy()

    if frame_idx % SKIP == 0:
        start_time = time.time()
        try:
            results = DeepFace.extract_faces(
                img_path=frame,
                detector_backend="retinaface",
                enforce_detection=False,
                align=False
            )
            display_texts = []
            for face in results:
                region = face["region"] if "region" in face else face["facial_area"]
                x, y, w, h = region["x"], region["y"], region["w"], region["h"]
                face_img = frame[y:y+h, x:x+w]

                # Extract current face features
                try:
                    target_repr = DeepFace.represent(
                        img_path=face_img,
                        model_name=MODEL,
                        enforce_detection=False,
                        detector_backend="retinaface"
                    )[0]["embedding"]
                    target_repr = l2_normalize(target_repr)  # <--- normalize
                except Exception:
                    display_texts.append("NoFace")
                    continue

                # Compare with all features in the database
                min_dist = float("inf")
                name = "Unknown"
                for item in face_db:
                    db_repr = l2_normalize(item["embedding"])  # <--- normalize
                    db_name = os.path.basename(os.path.dirname(item["img_path"]))
                    dist = np.linalg.norm(target_repr - db_repr)
                    if dist < min_dist:
                        min_dist = dist
                        name = db_name

                if min_dist <= THRESHOLD:
                    label = f"{name} ({min_dist:.2f})"
                else:
                    label = f"Unknown ({min_dist:.2f})"
                display_texts.append(label)

                # Draw rectangle and name
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

                # Logging logic
                if name != "Unknown":
                    last_time = last_seen.get(name, -LOG_INTERVAL)
                    if frame_idx - last_time >= LOG_INTERVAL:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[{now}] Detected: {name}, Frame: {frame_idx}, Position: ({x},{y},{w},{h})")
                        # Send log to Kafka
                        log_msg = {
                            "person": name,
                            "video": args.video,
                            "frame": frame_idx,
                            "timestamp": now,
                            "bbox": {"x": x, "y": y, "w": w, "h": h},
                            "recognition_time": round(time.time() - start_time, 2)
                        }
                        producer.send(KAFKA_TOPIC, json.dumps(log_msg).encode('utf-8'))
                    last_seen[name] = frame_idx

            elapsed = time.time() - start_time
            print(f"Frame {frame_idx} recognition time: {elapsed:.2f} seconds")
        except Exception as e:
            print(f"Error: {e}")

    cv2.imshow("Face Recognition", display_frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

    frame_idx += 1

cap.release()
cv2.destroyAllWindows()
