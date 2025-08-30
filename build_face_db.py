
import os
import pickle
from deepface import DeepFace
import argparse

parser = argparse.ArgumentParser(description="Build face database from images.")
parser.add_argument('--db_path', type=str, default="./VFHQ", help='Path to the image database folder')
parser.add_argument('--output', type=str, default="face_db.pkl", help='Output pickle file name')
args = parser.parse_args()

DB_PATH = args.db_path
OUTPUT_FILE = args.output
MODEL = "ArcFace"
representations = []


for root, dirs, files in os.walk(DB_PATH):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(root, file)
            try:
                # Extract features from a single image
                embedding_objs = DeepFace.represent(
                    img_path=img_path,
                    model_name=MODEL,
                    enforce_detection=False,
                    detector_backend="retinaface"
                )
                # Compatible with both list and single object return
                if isinstance(embedding_objs, list):
                    for emb in embedding_objs:
                        emb["img_path"] = img_path
                        representations.append(emb)
                else:
                    embedding_objs["img_path"] = img_path
                    representations.append(embedding_objs)
                print(f"Processed: {img_path}")
            except Exception as e:
                print(f"Skipped {img_path}: {e}")

# Save features to local file
with open(OUTPUT_FILE, "wb") as f:
    pickle.dump(representations, f)

print(f"Feature database saved to {OUTPUT_FILE}, total {len(representations)} images.")