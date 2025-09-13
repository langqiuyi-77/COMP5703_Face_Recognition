# Face Recognition Project

This project provides scripts for building a face feature database from images and running face recognition on videos using DeepFace.

## Dataset

- Youtube Face : https://www.cs.tau.ac.il/~wolf/ytfaces/
- VFHD : https://liangbinxie.github.io/projects/vfhq/

## Environment Setup

1. Create and activate the environment using the provided file:
  ```bash
  conda env create -f environment.yml
  conda activate face
  ```


## Kafka & Docker Setup

1. **Important:** For external access, you must set the advertised listeners in your `docker-compose.yml`:
  ```yaml
  # TODO: Change to your actual IP, do NOT use localhost
  - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092,EXTERNAL://{your_ip}:29092
  # Example:
  - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092,EXTERNAL://100.102.164.179:29092
  ```
  - In `face_recognition.py`, use the same IP and port:
  ```python
  producer = KafkaProducer(bootstrap_servers='100.102.164.179:29092')
  ```
  - Do **not** use `localhost` for external connections.

2. Start Kafka and Kafka UI using Docker Compose:
  ```bash
  docker-compose up -d
  ```
  - This will start Kafka and expose port 9092 for messaging, and Kafka UI on port 8080 for monitoring.
  - You can access Kafka UI in your browser at [http://localhost:8080](http://localhost:8080) to view topics and messages.



## Usage

### 1. Build a Face Database
Generate a feature database (pkl file) from a folder of images:

```bash
python build_face_db.py --db_path ./YTFace --output ytface_db.pkl
python build_face_db.py --db_path ./VFHQ --output vfhq_db.pkl
```
- `--db_path`: Path to the folder containing images (jpg, jpeg, png)
- `--output`: Output pickle file name


### 2. Run Face Recognition on Videos (YAML Config)
Run face recognition using multiple videos and a database, configured via YAML:

```bash
python face_recognition.py --config Conf/config.yaml
```
- `--config`: Path to the YAML config file

Example `config.yaml`:
```yaml
videos:
  - path: "./YTFace/output.mp4"
    direction: "in"
  - path: "./VFHQ/output.mp4"
    direction: "out"
db_file: "ytface_db.pkl"
```


### Kafka Log Message Format

Recognition logs are sent to Kafka topic `Log` in JSON format:

```json
{
  "person": "03",                // Recognized person name
  "video": "./VFHQ/output.mp4",   // Video file name
  "frame": 0,                      // Frame number
  "timestamp": "2025-09-05 01:32:45", // Recognition timestamp
  "bbox": {
    "x": 195, "y": 54, "w": 251, "h": 264 // Face bounding box
  },
  "recognition_time": 11.17        // Time taken for recognition (seconds)
}
```

You can view these logs in Kafka UI at [http://localhost:8080](http://localhost:8080).

![tip](tip.gif)

### 3. Example Datasets
- Place your datasets (image folders) in the project directory, e.g., `people/`, `VFHQ/`, etc.
- Place your videos in the project directory or subfolders.

## Notes
- The `.pkl` files (face databases) are generated and can be large. You may choose **not** to upload them to git, as teammates can regenerate them from the datasets.
- Datasets (image folders) **should** be uploaded if you want teammates to reproduce results.


---

Feel free to modify the scripts for your own datasets and experiments.
