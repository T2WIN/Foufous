import audio
import video

def analyze(video):
    v = video.analyze_video(video)
    a = audio.analyze_audio(video)

    events = {}
    i = 0
    for e in sorted(v["events"] + a["events"], key=lambda e: e["timestamp"]):
        events[str(i)] = e

    return {
        "global": {**v["global"], **a["global"]},
        "events": events,
        "stats": {**v["stats"], **a["stats"]},
    }
