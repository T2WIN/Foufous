unzip 'Annotations OK'.zip -d content/

cd content

# Create Video and JSON directories if they don't exist
mkdir -p Video JSON

# Move all mp4 files to Video folder
mv 'Annotations OK'/*.mp4 Video/

# Move all JSON files to JSON folder
mv 'Annotations OK'/*.json JSON/


sudo pip install -q mediapipe==0.10.0
sudo pip install scikit-video
sudo apt update && sudo apt install ffmpeg
sudo pip install -U openai-whisper
wget -O pose_landmarker.task -q https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task
