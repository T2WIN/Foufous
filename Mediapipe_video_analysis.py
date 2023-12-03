import cv2
from math import sqrt
import numpy as np
from mediapipe.framework.formats import landmark_pb2
from mediapipe import solutions
from mediapipe.tasks.python import vision
from mediapipe.tasks import python
import mediapipe as mp
import os
import json


all_points = []  # stores every posture related points throughout the video
frameRate = 30
everything_found = []
amplitudes = []
nb_ancrage = 0
nb_parasite = 0
checking_interval = 6
meter = 0
note_global = []
left_arm = []
right_hand_stop_moving = 0
left_hand_stop_moving = 0
potential_balance_issue = []

# Mediapipe doing its magic
def analyse_image(image, timestamp):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global

    VisionRunningMode = mp.tasks.vision.RunningMode

    base_options = python.BaseOptions(
        model_asset_path='pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True,
        running_mode=VisionRunningMode.VIDEO,
        min_pose_presence_confidence=0.5)
    detector = vision.PoseLandmarker.create_from_options(options)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

    detection_result = detector.detect_for_video(mp_image, timestamp)
    push_all_points(mp_image.numpy_view(), detection_result)

# Push all the points detected by mediapipe to all_points for later processing
def push_all_points(rgb_image, detection_result):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global
  
    pose_landmarks_list = detection_result.pose_landmarks
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        all_points_this_frame = [
            [landmark.x, landmark.y, landmark.z] for landmark in pose_landmarks]
        all_points.append(all_points_this_frame)

# Checks if the person is smiling at a certain frame
def check_for_smile(current_frame):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global
    mouth_size = dist(all_points[0][5][0], all_points[0][5][1], all_points[0][2][0], all_points[0][2][1]) * .91
    if (dist(all_points[current_frame][10][0], all_points[current_frame][10][1], all_points[current_frame][9][0], all_points[current_frame][9][1]) > mouth_size):
        everything_found.append(["(S)ourire", current_frame/frameRate, "good"])

# Checks if the person is swinging a t a certain frame
def check_balance(current_frame):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global, potential_balance_issue
  
    if ((all_points[current_frame][11][0] - all_points[current_frame-checking_interval][11][0]) / (checking_interval / frameRate) > .075 * meter):
        potential_balance_issue.append(current_frame/frameRate)

# Checks if the person is doing sudden movements  a certain frame
def check_for_sudden_movement(current_frame):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global
    
    left_arm = [13, 15, 17, 19, 21]
    right_arm = [14, 16, 18, 20, 22]
    left_shoulder = 11
    right_shoulder = 12
    global left_hand_stop_moving
    global right_hand_stop_moving

    derivative_threshold = .3 * meter / 1
    if (current_frame > left_hand_stop_moving):
      if (get_derivative(all_points, current_frame - checking_interval, current_frame, 15, left_shoulder) > derivative_threshold):
          movement = get_movement(current_frame, 15, left_shoulder)
          amplitude = dist(all_points[movement[0]][15][0], all_points[movement[0]][15][1], all_points[movement[1]][15][0], all_points[movement[1]][15][1])/meter
          amplitudes.append(amplitude)
          left_hand_stop_moving = movement[1]
          everything_found.append(["(G)estes", movement[0]/frameRate, type_geste(amplitude)])

    if (current_frame > right_hand_stop_moving):
      if (get_derivative(all_points, current_frame - checking_interval, current_frame, 16, right_shoulder) > derivative_threshold):
          movement = get_movement(current_frame, 16, right_shoulder)
          amplitude = dist(all_points[movement[0]][15][0], all_points[movement[0]][15][1], all_points[movement[1]][15][0], all_points[movement[1]][15][1])/meter
          amplitudes.append(amplitude)
          right_hand_stop_moving = movement[1]
          everything_found.append(["(G)estes", movement[0]/frameRate, type_geste(amplitude)])

# Classifies the movement based on its amplitude (small movements are parasites, so bad, big ones are good)
def type_geste(amplitude):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global
    if (amplitude < .04):
      nb_parasite += 1
      return "bad"
    if (amplitude > .14):
        return "good"
    return "ok"

# returns the distance between 2 points
def dist(x, y, i, j):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global
    return sqrt((x-i)**2 + (y-j)**2)

# Gets the speed of a movement in the referential of the "origin"
def get_derivative(function_points, t1, t2, i, origin):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global
    delta_x = (function_points[t2][i][0] - function_points[t2][origin]
               [0]) - (function_points[t1][i][0] - function_points[t1][origin][0])
    delta_y = (function_points[t2][i][1] - function_points[t2][origin]
               [1]) - (function_points[t1][i][1] - function_points[t1][origin][1])
    return sqrt(delta_x**2 + delta_y**2) / ((t2 - t1) / frameRate)

# Gets the beginning and the end frames of the detected movement
def get_movement(frame_catch, i, origin):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global
    derivative_threshold = .1 * meter / 1

    # find end of movement
    end_frame = frame_catch
    while (end_frame < len(all_points)-1 and get_derivative(all_points, end_frame - checking_interval, end_frame, i, origin) > derivative_threshold):
        end_frame += 1

    # find beggining of movement
    beginning_frame = frame_catch
    while (beginning_frame >= checking_interval+1 and get_derivative(all_points, beginning_frame - checking_interval, beginning_frame, i, origin) > derivative_threshold):
        beginning_frame -= 1
    return [beginning_frame, end_frame]

# Only store the relevant balance issues (longer than half a second)
def treat_balance_issues():
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global, potential_balance_issue

    balance_start = -1
    balance_end = -1
    for i in range(len(potential_balance_issue)):
        if (balance_start == -1):
            balance_start = potential_balance_issue[i]
            balance_end = balance_start
        if (potential_balance_issue[i] - balance_end < .11):
            balance_end = potential_balance_issue[i]
        else:
            if (balance_end - balance_start > .5):
              everything_found.append(["(M)ouvements du corps", balance_start, "bad"])
              nb_ancrage += 1
            balance_start = potential_balance_issue[i]
            balance_end = balance_start
    if (balance_end - balance_start > .5):
      everything_found.append(["(M)ouvements du corps", balance_start, "bad"])
      nb_ancrage += 1

# Calculates stats from the amplitudes of the movements throughout the video
def amplitude_stats():
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global
    
    min = amplitudes[0]
    max = amplitudes[0]
    mean = 0
    for i in amplitudes:
      mean += i
      if (i < min):
          min = i
      if (i > max):
          max = i
    return (min, max, mean/len(amplitudes))

# Split the video frame by frame for the mediapipe analysis, then checks for every movement and return a json file with them
def analyse_video(path):
    global all_points, frameRate, everything_found, amplitudes, nb_ancrage, nb_parasite, checking_interval, meter, note_global
  
    # Read video file and store into 4D numpy array
    cap = cv2.VideoCapture(path)
    current_frame = 0
    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            break
        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        analyse_image(frame, timestamp)
        # cap.release()
        current_frame += 1

        ## COMMENT TO PRODUCE FULL VIDEO
        if (current_frame > 300):
            cap.release()


    cap.release()
    meter = (all_points[0][2][0] - all_points[0][5][0]) / 50 * 1000

    current_frame = checking_interval
    left_hand_stop_moving = 0
    right_hand_stop_moving = 0
    while (current_frame < len(all_points)):
        check_for_sudden_movement(current_frame)
        check_for_smile(current_frame)
        check_balance(current_frame)
        current_frame+=1

    treat_balance_issues()
    note_global = [1 for i in range(3)]
    if (nb_ancrage < 3):
        note_global[0] = 2
    elif (nb_ancrage > 10):
        note_global[0] = 0

    if (amplitude_stats()[2] > .10):
        note_global[1] = 2
    elif (amplitude_stats()[2] < .04):
        note_global[1] = 0

    if (nb_parasite < 5):
        note_global[2] = 2
    elif (nb_parasite > 20):
        note_global[2] = 0

    return {
        "global": {"Ancrage du corps": note_global[0], "Gestes": note_global[1], "Calme (vs anxiete)": note_global[2]},
        "events": {str(i): {"timestamp": event[1], "type": event[0], "note": event[2]} for i, event in enumerate(everything_found)}
    }

if __name__ == "__main__":
    analyse_video("./content/Video/William3 - prezzup.com.mp4")