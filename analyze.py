import audio
import video

def analyze(p):
    v = video.analyse_video(p)
    a = audio.analyze_audio(p)

    events = {}
    i = 0
    for e in sorted(v["events"] + a["events"], key=lambda e: e["timestamp"]):
        events[str(i)] = e
        i += 1

    return {
        "global": {**v["global"], **a["global"]},
        "events": events,
        "stats": a["stats"],
    }
