from whisper_timestamped import transcribe_timestamped, load_model
import string
import statistics

POTENTIAL_FILLERS = [
    "donc",
    "mais",
    "alors",
    "genre",
    "attend",
    "attends",
]

REAL_FILLERS = [
    ["du", "coup"],
    ["en", "fait"],
    ["bah"],
    ["ouais"],
]

def flatten(list_of_lists, key = None):
    for sublist in list_of_lists:
        for item in sublist.get(key, []) if key else sublist:
            yield item

def normalize_text(s):
    return s["text"].lower().translate(str.maketrans("", "", string.punctuation))

model = load_model("base")

def get_fillers_events(words, words_without_pauses):
    events = []
    for i, s in enumerate(words):
        if i > 0 and s["text"] == "[*]" and not words[i - 1]["text"].endswith((".", ",", "!", "?")):
            events.append({
                "timestamp": s["start"],
                "type": "(F)iller",
                "note": "bad",
            })

    i = 0
    while i < len(words_without_pauses):
        t = normalize_text(words_without_pauses[i])
        for f in REAL_FILLERS:
            if t == f[0]:
                j = 1
                while j < len(f) and f[j] == normalize_text(words_without_pauses[i + j]):
                    j += 1
                if j == len(f):
                    events.append({
                        "timestamp": words_without_pauses[i]["start"],
                        "type": "(F)iller",
                        "note": "bad",
                    })
                    i += j - 1
                    break

        if t in POTENTIAL_FILLERS and normalize_text(words_without_pauses[i + 1]) in POTENTIAL_FILLERS:
            events.append({
                "timestamp": words_without_pauses[i]["start"],
                "type": "(F)iller",
                "note": "bad",
            })
            i += 1

        i += 1

    return sorted(events, key=lambda e: e["timestamp"])

def get_speed(words):
    start_t = words[0]["start"]
    windows = []
    while True:
        count = 0
        for s in words:
            if s["start"] > start_t + 5:
                windows.append({
                    "start": start_t,
                    "count": count,
                    "mean": count / 5,
                })
                start_t += 1
                break
            if s["start"] > start_t:
                count += 1
        else:
            break

    return {
        "windows": windows,
        "count": len(words),
        "mean": len(words) / (words[-1]["end"] - words[0]["start"]),
        "var": statistics.variance([w["mean"] for w in windows]),
    }
    
def analyze_audio(video):
    result = transcribe_timestamped(
        model, video,
        language="fr",
        detect_disfluencies=True,
    )

    words = list(flatten(result["segments"], "words"))
    words_without_pauses = [s for s in words if s["text"] != "[*]"]

    filler_events = get_fillers_events(words, words_without_pauses)
    speed_stats = get_speed(words_without_pauses)

    frequency_grade = int(speed_stats["var"] < 0.5) + int(speed_stats["var"] < 0.75)

    return {
        "global": {
            "Texte - débit/fréquence": str(frequency_grade),
            "Voix - débit": str(frequency_grade),
        },
        "events": filler_events,
        "stats": {
            "Fréquence": speed_stats["mean"],
            "Variance": speed_stats["var"],
            "Mots": speed_stats["count"],
        },
    }

if __name__ == "__main__":
    print(analyze_audio("../content/Video/Louis1 - prezzup.com.mp4"))
