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

all_points = [] #stores every posture related points throughout the video
frameRate = 30

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
  #print(detection_result)
  # STEP 5: Process the detection result. In this case, visualize it.
  annotated_image = push_all_points(mp_image.numpy_view(), detection_result)


from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
from math import sqrt

def push_all_points(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  # annotated_image = np.copy(rgb_image)
  amount_of_landmarks_to_plot = min(len(pose_landmarks_list),5)
  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]
    #print(pose_landmarks[0].x)

    all_points_this_frame = [[landmark.x, landmark.y, landmark.z] for landmark in pose_landmarks]
    print(pose_landmarks[0])
    all_points.append(all_points_this_frame)
    # Draw the pose landmarks.
  #   pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
  #   pose_landmarks_proto.landmark.extend([
  #     landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
  #   ])
  #   solutions.drawing_utils.draw_landmarks(
  #     annotated_image,
  #     pose_landmarks_proto,
  #     None,
  #     solutions.drawing_styles.get_default_pose_landmarks_style())
  # return annotated_image

def check_for_sudden_movement(current_frame):
  left_arm = [13, 15, 17, 19, 21]
  right_arm = [14, 16, 18, 20, 22]
  left_shoulder = 11
  right_shoulder = 12

  derivative_threshold =  .5 * meter / 1
  #for i in left_arm:
  if (get_derivative(all_points, current_frame - checking_interval, current_frame, 15, left_shoulder) > derivative_threshold):
      movement = get_movement(current_frame, 15, left_shoulder)
      print(movement[0]/frameRate,",", movement[1]/frameRate, "left arm", get_derivative(all_points, current_frame - checking_interval, current_frame, 15, left_shoulder) / meter, "at", current_frame/frameRate)
      return movement[1]
  
  #for i in right_arm:
  if (get_derivative(all_points, current_frame - checking_interval, current_frame, 16, right_shoulder) > derivative_threshold):
      movement = get_movement(current_frame, 16, right_shoulder)
      print(movement[0]/frameRate,",", movement[1]/frameRate, "right arm", get_derivative(all_points, current_frame - checking_interval, current_frame, 16, right_shoulder) / meter, "at", current_frame/frameRate)
      return movement[1]
  return current_frame+1

def get_derivative(function_points, t1, t2, i, origin):
  delta_x = (function_points[t2][i][0] - function_points[t2][origin][0]) - (function_points[t1][i][0] - function_points[t1][origin][0])
  delta_y = (function_points[t2][i][1] - function_points[t2][origin][1]) - (function_points[t1][i][1] - function_points[t1][origin][1])
  delta_z = 0 #(function_points[t2][i][2] - function_points[t2][origin][2]) - (function_points[t1][i][2] - function_points[t1][origin][2])
  return sqrt(delta_x**2 + delta_y**2 + delta_z**2) / ((t2 - t1) / frameRate)

def get_movement(frame_catch, i, origin):
  derivative_threshold = .1 * meter / 1

  #find end of movement
  end_frame = frame_catch
  while (end_frame < len(all_points) and get_derivative(all_points, end_frame - checking_interval, end_frame, i, origin) > derivative_threshold):
    end_frame += 1

  #find beggining of movement
  beginning_frame = frame_catch
  while (beginning_frame >= checking_interval and get_derivative(all_points, beginning_frame - checking_interval, beginning_frame, i, origin) > derivative_threshold):
    beginning_frame -= 1
  return [beginning_frame, end_frame]


import cv2

# Read video file and store into 4D numpy array
cap = cv2.VideoCapture(dir_path + files[1])
current_frame = 0
checking_interval = 6
while cap.isOpened():
    print(current_frame)
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
    analyse_image(frame, timestamp)
    #cap.release()
    current_frame += 1
    if (current_frame > 150):
       cap.release()


cap.release()
meter = (all_points[0][2][0] - all_points[0][5][0]) / 50 * 1000

print("start checking for sudden movements")
current_frame = checking_interval
while (current_frame < len(all_points)):
   current_frame = check_for_sudden_movement(current_frame)