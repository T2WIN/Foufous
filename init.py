import os

# Define the directory path
dir_path = "content/Video/"

# Get a list of all files in the directory
files = os.listdir(dir_path)

# Print the file names
for file in files:
    print(file)

# STEP 1: Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

def analyse_image(image, timestamp):
  # STEP 2: Create an PoseLandmarker object

  VisionRunningMode = mp.tasks.vision.RunningMode

  base_options = python.BaseOptions(model_asset_path='content/pose_landmarker.task')
  options = vision.PoseLandmarkerOptions(
      base_options=base_options,
      output_segmentation_masks=True,
      running_mode=VisionRunningMode.VIDEO,
      min_pose_presence_confidence=0.5)
  detector = vision.PoseLandmarker.create_from_options(options)
  # STEP 3: Load the input image.
  mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

  # STEP 4: Detect pose landmarks from the input image.
  detection_result = detector.detect_for_video(mp_image, timestamp)
  print(detection_result)
  # STEP 5: Process the detection result. In this case, visualize it.
  annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), detection_result)


from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np


def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)
  amount_of_landmarks_to_plot = min(len(pose_landmarks_list),5)
  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      None,
      solutions.drawing_styles.get_default_pose_landmarks_style())
  return annotated_image

import cv2

# Read video file and store into 4D numpy array
cap = cv2.VideoCapture(dir_path + files[1])
while cap.isOpened():
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
    analyse_image(frame, timestamp)
    cap.release()

cap.release()


# for x in video_4d_array:
#     cv2_imshow(x)