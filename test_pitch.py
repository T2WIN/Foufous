import crepe
from scipy.io import wavfile
from scipy.signal import resample
import os
import sys
from moviepy.editor import VideoFileClip
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import noisereduce as nr
from scipy.signal import lfilter


def convert_video_to_audio_moviepy(video_file, output_ext="wav"):
    """Converts video to audio using MoviePy library
    that uses `ffmpeg` under the hood"""
    filename, ext = os.path.splitext(video_file)
    clip = VideoFileClip(video_file)
    clip.audio.write_audiofile(f"{filename}.{output_ext}")


video_file = "Annotations OK/Mael.mp4"
convert_video_to_audio_moviepy(video_file)

sr, audio = wavfile.read(video_file[:-4] + ".wav")

time, frequency, confidence, activation = crepe.predict(
    audio, sr, viterbi=True, model_capacity="tiny")

a = np.column_stack((time, frequency, confidence))
chunks = np.array_split(audio, audio.size/(sr/50))

dbs = [np.linalg.norm(np.mean(chunk**2)) for chunk in chunks]
series_db = pd.Series(dbs, name="Volume")

data = pd.DataFrame(data=a, columns=["Time", "Frequency", "Confidence"])
data["Volume"] = series_db
data = data.set_index(data["Time"])
data["Frequency"] = data["Frequency"] - np.mean(data["Frequency"])
data["Volume"] = data["Volume"] - np.mean(data["Volume"])

data = data[data["Frequency"] > 0.75]
# data = data[data["Frequency"] < 2]

n = 15  # the larger n is, the smoother curve will be
b = [1.0 / n] * n
a = 1
data["Volume"] = lfilter(b, a, data["Volume"])
data["Frequency"] = lfilter(b, a, data["Frequency"])
print(np.var(data["Frequency"]))

var = np.var(data["Frequency"])
if var >= 0.22:
    print("Bien")
elif var > 0.20 and var < 0.22:
    print("Moyen")
else:
    print("Nul")

plt.plot(data["Frequency"])
plt.show()
